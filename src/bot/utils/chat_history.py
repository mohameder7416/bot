from datetime import datetime


def save_conversation(db, lead_id, prompt, result):
    conn = db.connexion()
    if conn:
        try:
            query = """
            INSERT INTO conversations (lead_id, prompt, result, timestamp)
            VALUES (%s, %s, %s, %s)
            """
            data = (lead_id, prompt, result, datetime.now())
            affected_rows = db.write_query(conn, query, data)
            conn.close()
            return affected_rows > 0
        except Exception as e:
            print(f"Error saving conversation: {str(e)}")
            conn.close()
            return False
    return False


def load_chat_history(db, lead_id):
    conn = db.connexion()
    if conn:
        try:
            query = """
            SELECT prompt, result, timestamp
            FROM conversations
            WHERE lead_id = %s
            ORDER BY timestamp ASC
            """
            data = (lead_id,)
            rows = db.readQuery(conn, query, data)
            conn.close()
            return rows
        except Exception as e:
            print(f"Error loading chat history: {str(e)}")
            conn.close()
            return []
    return []