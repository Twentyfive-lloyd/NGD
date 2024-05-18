import mysql.connector
import logging
import time


def connect_to_database():
    MAX_RETRIES = 3
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                database="ngdelivery",
                user="kmfktg",
                password="Defs@2012.com"
            )
            return conn  # Retourne la connexion si la connexion réussit
        except mysql.connector.Error as error:
            logging.error("Erreur de connexion à la base de données :", exc_info=True)
            retry_count += 1
            # Attendez un certain temps avant de réessayer la connexion
            time.sleep(5)
    
    logging.error("Impossible de se connecter à la base de données après plusieurs tentatives.")
    return None  # Retourne None si la connexion échoue après les tentatives
