import sqlite3
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def init_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_users = [
            ('John Doe', 'john@example.com', 'password123'),
            ('Jane Smith', 'jane@example.com', 'secret456'),
            ('Bob Johnson', 'bob@example.com', 'qwerty789')
        ]
        
        for name, email, password in sample_users:
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
        
        print("Database initialized with sample data")
    else:
        print("Database already contains data")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()