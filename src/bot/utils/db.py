import pymysql
from pymysql import Error
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))  # Default MySQL port is 3306
DB_NAME = os.getenv("DB_NAME")

class DataBase:
    # Connection to any MySQL database using HOST, USER, PASSWORD, NAME
    def connexion(self, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT):
        try:
            conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            return conn
        except Error as e:
            error_mes = f"Connection function => {str(e)}"
            print(error_mes)
            return None  # Return None if connection fails

    # Get any value from database using a SELECT query
    def readQuery(self, conn, query, data=None, raw=False):
        try:
            with conn.cursor() as cur:
                if raw:
                    cur.execute(query)
                else:
                    cur.execute(query, data if data else None)
                rows = cur.fetchall()
            return rows
        except Error as e:
            error_mes = f"read_query function => {str(e)}"
            print(error_mes)
            return []

    # Insert any value in database using an INSERT query
    def write_query(self, conn, query, data):
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, data)
                conn.commit()
                return cursor.rowcount  # Return number of affected rows
        except Error as e:
            error_mes = f"write_query function => {str(e)}"
            print(error_mes)
            conn.rollback()
            return 0

    # Update any table in the database with an UPDATE query
    def update_query(self, conn, query, data):
        return self.write_query(conn, query, data)  # Reuse write_query method

    # Delete rows from a table
    def delete_query(self, conn, query, data):
        return self.write_query(conn, query, data)  # Reuse write_query method

