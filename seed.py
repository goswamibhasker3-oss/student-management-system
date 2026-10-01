import getpass
import re

import MySQLdb
from werkzeug.security import generate_password_hash

from config import Config


def _connect_to_server():
    return MySQLdb.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        passwd=Config.MYSQL_PASSWORD,
        port=Config.MYSQL_PORT,
        charset="utf8mb4",
    )


def _create_tables(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            role VARCHAR(20) DEFAULT 'admin',
            is_active TINYINT(1) DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(150) NOT NULL,
            credits INT DEFAULT 3,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            roll_no VARCHAR(30) UNIQUE NOT NULL,
            first_name VARCHAR(60) NOT NULL,
            last_name VARCHAR(60) NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            phone VARCHAR(20),
            gender ENUM('Male', 'Female', 'Other') DEFAULT 'Other',
            dob DATE,
            address VARCHAR(255),
            course_id INT,
            status ENUM('active', 'inactive', 'graduated') DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL
        )
        """
    )


def _create_admin(cursor):
    username = input("Admin username [admin]: ").strip() or "admin"
    if len(username) > 50:
        raise ValueError("Admin username must be 50 characters or fewer.")

    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        print(f"User '{username}' already exists; leaving it unchanged.")
        return

    while True:
        password = getpass.getpass("Choose an admin password (12+ characters): ")
        confirmation = getpass.getpass("Confirm admin password: ")
        if password != confirmation:
            print("Passwords did not match. Try again.")
        elif len(password) < 12:
            print("Password must be at least 12 characters. Try again.")
        else:
            break

    cursor.execute(
        """
        INSERT INTO users (username, password_hash, full_name, role, is_active)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (username, generate_password_hash(password), "Administrator", "admin", 1),
    )
    print(f"Admin user '{username}' created.")


def initialize_database():
    database_name = Config.MYSQL_DB
    if not re.fullmatch(r"[A-Za-z0-9_]+", database_name):
        raise ValueError("MYSQL_DB may contain only letters, numbers, and underscores.")

    connection = _connect_to_server()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            connection.select_db(database_name)
            _create_tables(cursor)
            _create_admin(cursor)
            connection.commit()
        finally:
            cursor.close()
    finally:
        connection.close()


if __name__ == "__main__":
    try:
        initialize_database()
    except MySQLdb.Error as error:
        raise SystemExit(
            "Could not connect to MySQL. Start the MySQL server and check the "
            "MYSQL_* values in your .env file."
        ) from error