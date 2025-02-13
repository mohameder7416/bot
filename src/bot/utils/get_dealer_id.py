import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_dealer_id():
    # Load environment variables
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_NAME = os.getenv("DB_NAME", "bot")

    # Initialize the connection and query
    connection = None
    latest_dealer_id = None

    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )

        # Create a cursor to execute the query
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Fetch the latest dealer_id based on the latest row in selected_item table
            query = """
                SELECT dealers_id 
                FROM selected_item 
                ORDER BY id DESC 
                LIMIT 1;
            """
            cursor.execute(query)
            result = cursor.fetchone()

            # Extract the dealer_id from the result if it exists
            if result:
                latest_dealer_id = result['dealers_id']

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Close the connection
        if connection:
            connection.close()

    return latest_dealer_id
if __name__ == "__main__":
    latest_id = get_latest_dealer_id()
    if latest_id is not None:
        print(f"The latest dealer_id is: {latest_id}")
    else:
        print("No dealer_id found in the table.")