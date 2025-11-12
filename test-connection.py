import mysql.connector

def initialize_database():
    """Initialize the database with required tables"""
    endpoint = 'localhost'
    port = 8889
    user = 'root'
    password = 'root'

    try:
        print("Connecting to MySQL server...")
        connection = mysql.connector.connect(
            host=endpoint,
            port=port,
            user=user,
            password=password
        )

        cursor = connection.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS groovnapp")
        cursor.execute("USE groovnapp")

        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """)

        # Create reviews table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            album VARCHAR(255) NOT NULL,
            artist VARCHAR(255) NOT NULL,
            genre VARCHAR(100),
            rating INT,
            review TEXT,
            url TEXT,
            date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        connection.commit()
        print("Database and tables initialized successfully!")

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    initialize_database()
