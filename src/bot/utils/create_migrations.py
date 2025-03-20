import os
import pymysql
from db import DataBase
from dotenv import load_dotenv
load_dotenv()
db = DataBase(
    host=os.getenv("DB_HOST_WRITE"),
    user=os.getenv("DB_USER_WRITE"),
    password=os.getenv("DB_PASSWORD_WRITE"),
    database=os.getenv("DB_NAME_WRITE"),
    port=int(os.getenv("DB_PORT_WRITE", 3306)),
)

def get_executed_versions(connection):
    """Fetch the list of already executed versions from the migrations table."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version FROM migrations")
            return {row[0] for row in cursor.fetchall()}
    except pymysql.MySQLError:
        return set()

def execute_sql_file(file_path, connection):
    """Execute the SQL script from the given file path."""
    with open(file_path, 'r') as file:
        sql_script = file.read()
    
    sql_statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
    
    with connection.cursor() as cursor:
        for statement in sql_statements:
            cursor.execute(statement)
        connection.commit()

def main():
    connection = db.connexion()
    if not connection:
        print("Failed to connect to the database.")
        return

    migrations_folder = 'migrations'
    os.makedirs(migrations_folder, exist_ok=True)

    try:
        executed_versions = get_executed_versions(connection)

        for file_name in sorted(os.listdir(migrations_folder)):
            if file_name.endswith('.sql'):
                version = file_name.replace('.sql', '').replace("_", ".")
                if version not in executed_versions:
                    file_path = os.path.join(migrations_folder, file_name)
                    execute_sql_file(file_path, connection)
                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO migrations (version, created_at) VALUES (%s, NOW())", (version,))
                        connection.commit()
                    print(f"Executed and logged migration: {file_name}")
                else:
                    print(f"Skipping already executed migration: {file_name}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
