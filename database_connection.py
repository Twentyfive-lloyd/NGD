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
                user="root",
                password=""
            )
            return conn  # Retourne la connexion si la connexion réussit
        except mysql.connector.Error as error:
            logging.error("Erreur de connexion à la base de données :", exc_info=True)
            retry_count += 1
            # Attendez un certain temps avant de réessayer la connexion
            time.sleep(5)
    
    logging.error("Impossible de se connecter à la base de données après plusieurs tentatives.")
    return None  # Retourne None si la connexion échoue après les tentatives

# Classe Singleton pour gérer la connexion à la base de données
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conn = cls._instance.connect_to_database()
        return cls._instance

    def connect_to_database(self):
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                database="ngdelivery",
                user="root",
                password=""
            )
            logging.info("Connexion à la base de données établie avec succès")
            return conn
        except mysql.connector.Error as e:
            logging.error("Erreur lors de la connexion à la base de données: %s", e)
            return None

    @property
    def conn(self):
        if self._conn is None or not self._conn.is_connected():
            self._conn = self.connect_to_database()
        return self._conn
