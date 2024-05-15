import mysql.connector
from mysql.connector import Error

def test_database_connection(host, user, password, database):
    connection = None  # Initialisation de la variable connection

    try:
        # Establish a connection to the database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("Connected to the database.")
            
            # Execute a simple query to test connectivity
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result:
                print("Query executed successfully.")
            else:
                print("Query failed to execute.")

    except Error as e:
        print("Error while connecting to the database:", e)

    finally:
        # Close the database connection
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

# Use the database configuration values
host='localhost'
user='root'
password=''
database='ngdelivery'

test_database_connection(host, user, password, database)
