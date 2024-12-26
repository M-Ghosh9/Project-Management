import sqlite3
import bcrypt

DB_FILE = "project_manager.db"

def init_auth_db():
    """Initialize the user authentication database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'member'
            )
        """)
        # Check if admin user exists
        cursor.execute("SELECT * FROM users WHERE email=?", ("admin@ic.ac.uk",))
        if not cursor.fetchone():
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                           ("admin@ic.ac.uk", hashed_password.decode('utf-8'), "admin"))

def register_user(email, password, role="member"):
    """Register a new user."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", 
                           (email, hashed_password, role))
            return True, "User registered successfully!"
        except sqlite3.IntegrityError:
            return False, "User with this email already exists."

def authenticate_user(email, password):
    """Authenticate a user by verifying their credentials."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email=?", (email,))
        result = cursor.fetchone()
        if result:
            stored_password = result[0]
            # Ensure stored password is hashed
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    return True
            except ValueError:
                raise ValueError("Stored password is not properly hashed.")
    return False

def get_user_role(email):
    """Retrieve the role of the user with the given email."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE email=?", (email,))
        role = cursor.fetchone()
        return role[0] if role else None

def change_password(email, new_password):
    """Change the password of a user."""
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed_password, email))
