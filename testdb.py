import mysql.connector
from mysql.connector import Error

def test_database_connection(host, user, password, database):
    try:
        # Establish a connection to the database
        connection = mysql.connector.connect(
            host='45.41.235.162',
            user='safeplac_ngadmin',
            password='Defs@2012.com',
            database='safeplac_ngdelivery'
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
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

# Use the database configuration values
host='45.41.235.162'
user='safeplac_ngadmin'
password='Defs@2012.com'
database='safeplac_ngdelivery'

test_database_connection(host, user, password, database)
