import sqlite3
import bcrypt

# Create database and users table
def initialize_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    """)

    # Videos table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            uploader_id INTEGER,
            FOREIGN KEY (uploader_id) REFERENCES users (id)
        )
    """)

    # Create admin user
    admin_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                       ("admin", admin_password, 1))
    except sqlite3.IntegrityError:
        pass  # Admin already exists

    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    initialize_db()
