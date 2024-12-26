import sqlite3
from contextlib import contextmanager

DB_FILE = "project_manager.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                deadline DATE,
                progress INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Pending'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'member'
            )
        """)

def get_projects():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, deadline, progress, status FROM projects")
        rows = cursor.fetchall()
        return [{"id": row[0], "name": row[1], "description": row[2], "deadline": row[3], "progress": row[4], "status": row[5]} for row in rows]

def add_project(name, description, deadline):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO projects (name, description, deadline) VALUES (?, ?, ?)", (name, description, deadline))
        return cursor.lastrowid

def update_project(project_id, name, description, deadline, progress, status):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects SET name=?, description=?, deadline=?, progress=?, status=? WHERE id=?
        """, (name, description, deadline, progress, status, project_id))

def add_team_member(name, email, role="member"):
    """Add a new team member."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO team (name, email, role) VALUES (?, ?, ?)", (name, email, role))
        return cursor.lastrowid

def get_team_members():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, role FROM team")
        return [{"id": row[0], "name": row[1], "email": row[2], "role": row[3]} for row in cursor.fetchall()]
