import sqlite3

# initalizes the SQLite database by creating the necessary tables

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Drop tables if they already exist to start with a clean state
    cursor.executescript('''
        DROP TABLE IF EXISTS bookings;
        DROP TABLE IF EXISTS flights;
        DROP TABLE IF EXISTS users;
    ''')

    # Unified `users` table creation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
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

    # Unified `flights` table creation with `airline` column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            departure TEXT NOT NULL,
            airline TEXT
        )
    ''')

    # Unified `bookings` table creation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            flight_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (flight_id) REFERENCES flights (flight_id)
        )
    ''')

    conn.commit()
    conn.close()

    
def insert_sample_data():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    # Insert sample users
    #cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", ('testuser', 'test@example.com'))
    

    # Insert sample flights with airline names
    cursor.execute("INSERT INTO flights (destination, departure, airline) VALUES (?, ?, ?)", ('Toronto to Calgary', '2024-12-01 10:00:00', 'Air Canada'))
    cursor.execute("INSERT INTO flights (destination, departure, airline) VALUES (?, ?, ?)", ('Calgary to Toronto', '2024-12-06 03:00:00', 'WestJet'))
    
    # Insert sample booking
    cursor.execute("INSERT INTO bookings (user_id, flight_id, status) VALUES (?, ?, ?)", (1, 1, 'active'))
    cursor.execute("INSERT INTO bookings (user_id, flight_id, status) VALUES (?, ?, ?)", (1, 2, 'active'))
    
    connection.commit()
    connection.close()

# establishes a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    init_db()
    insert_sample_data()
    print("Database has been initialized.")