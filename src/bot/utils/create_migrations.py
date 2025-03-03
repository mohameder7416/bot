from bot.utils.db import DataBase

DB=DataBase()
import os
import time

def get_executed_versions(connection):
    try:
        """Fetch the list of already executed versions from the migrations table."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT version FROM migrations")
            return {row[0] for row in cursor.fetchall()}
    except:
        return {}

def execute_sql_file(file_path, connection):
    """Execute the SQL script from the given file path."""
    with open(file_path, 'r') as file:
        sql_script = file.read()
    
    # Split the script into individual statements
    sql_statements = sql_script.split(';')
    
    with connection.cursor() as cursor:
        for statement in sql_statements:
            if statement.strip():  # Ignore empty statements
                cursor.execute(statement)
        connection.commit()

def main():
    # Database connection details
    connection = DB.connexion(
    DB_HOST_ASSISTANCE_WRITE ,
    DB_USERNAME_ASSISTANCE_WRITE , 
    DB_PASSWORD_ASSISTANCE_WRITE ,
    DB_DATABASE_ASSISTANCE_WRITE 
        )

    # Path to the migrations folder
    migrations_folder = 'migrations'

    try:
        # Fetch existing versions
        executed_versions = get_executed_versions(connection)

        # Iterate over files in the migrations folder
        for file_name in os.listdir(migrations_folder):
            if file_name.endswith('.sql'):
                version = file_name.replace('.sql', '')  # Extract version from file name
                version=version.replace("_",".")
                if version not in executed_versions:
                    # Execute the SQL file and insert the version into the migrations table
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

