
import sqlite3
import hashlib
import secrets
import hmac

from database import get_connection


# Default administrator credentials
DEFAULT_ADMIN_NAME = "System Administrator"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin@12345"


def hash_password(password):
    """Convert password into a secure hash."""

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        600000
    )

    return salt + "$" + password_hash.hex()


def verify_password(password, stored_password):
    """Verify entered password against stored hash."""

    try:
        salt, saved_hash = stored_password.split("$")

        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            600000
        )

        return hmac.compare_digest(
            new_hash.hex(),
            saved_hash
        )

    except (ValueError, AttributeError):
        return False


def create_default_admin():
    """Create the default admin if one does not exist."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE username = ?",
        (DEFAULT_ADMIN_USERNAME,)
    )

    existing_admin = cursor.fetchone()

    if existing_admin is None:

        password_hash = hash_password(
            DEFAULT_ADMIN_PASSWORD
        )

        cursor.execute("""
            INSERT INTO users (
                full_name,
                username,
                password_hash,
                role
            )
            VALUES (?, ?, ?, 'admin')
        """, (
            DEFAULT_ADMIN_NAME,
            DEFAULT_ADMIN_USERNAME,
            password_hash
        ))

        conn.commit()

        print("Default Admin account created successfully!")

    else:
        print("Admin account already exists.")

    conn.close()


def register_patient(full_name, username, email, phone, password):
    """Register a new patient."""

    if not all([
        full_name.strip(),
        username.strip(),
        password
    ]):
        return False, "Please fill in all required fields."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    password_hash = hash_password(password)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (
                full_name,
                username,
                email,
                phone,
                password_hash,
                role
            )
            VALUES (?, ?, ?, ?, ?, 'patient')
        """, (
            full_name.strip(),
            username.strip(),
            email.strip() or None,
            phone.strip() or None,
            password_hash
        ))

        conn.commit()
        return True, "Patient registration successful!"

    except sqlite3.IntegrityError:
        return False, "Username or email already exists."

    finally:
        conn.close()


def authenticate_user(username, password):
    """Check login credentials."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, full_name, username,
               password_hash, role
        FROM users
        WHERE username = ?
    """, (username.strip(),))

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return None

    user_id, full_name, username, saved_hash, role = user

    if verify_password(password, saved_hash):

        return {
            "user_id": user_id,
            "full_name": full_name,
            "username": username,
            "role": role
        }

    return None


if __name__ == "__main__":

    create_default_admin()

    print("\nDefault Admin Login Details")
    print("---------------------------")
    print("Username:", DEFAULT_ADMIN_USERNAME)
    print("Password:", DEFAULT_ADMIN_PASSWORD)
