import sqlite3

# initalizes the SQLite database by creating the necessary tables
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #SQL command to create the 'users' table with columns for user information.
    # 'email' column is unique to prevent duplicate entries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
    ''')

    conn.close()

# establishes a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    init_db()
    print("Database has been initialized.")