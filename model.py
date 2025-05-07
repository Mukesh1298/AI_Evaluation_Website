import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Expert@123",
        database="Evaluation_data"
    )
