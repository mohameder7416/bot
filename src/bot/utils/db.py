import psycopg2
from psycopg2 import Error
from datetime import datetime
import os
from  dotenv import load_dotenv
load_dotenv()

DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_NAME=os.getenv("DB_NAME")




class DataBase:
    # Connection to any PostgreSQL database using HOST, USER, PASSWORD, NAME
    def connexion(self, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME,port=DB_PORT):
        try:
            conn = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                dbname=database,
                port=port
            )
            return conn
        except Error as e:
            error_mes = f"Connexion function => {str(e)}"
            return None  # Return None if connection fails

    # Get any value from database using a SELECT query
    def readQuery(self, conn, query, data=None,raw=False):
        try:
            with conn.cursor() as cur:
                
                if raw:
                    cur.execute(query)
                else :
                    cur.execute(query, data if data else None)
                rows = cur.fetchall()
                
  
            return rows
        except Error as e:
            error_mes = f"readQuery function => {str(e)}"
            return []

    # Insert any value in database using an INSERT query
    def writeQuery(self, conn, query, data):
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, data)
                conn.commit()
                return cursor.rowcount  # Return number of affected rows
        except Error as e:
            error_mes = f"writeQuery function => {str(e)}"
            now = datetime.now()
        
            
            return 0

    # Update any table in the database with an UPDATE query
    def updateQuery(self, conn, query, data):
        return self.writeQuery(conn, query, data)  # Reuse writeQuery method

    # Delete rows from a table
    def deleteQuery(self, conn, query, data):
        return self.writeQuery(conn, query, data)  # Reuse writeQuery method

    # Write to tracking conversation
    