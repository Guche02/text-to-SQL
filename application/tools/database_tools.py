import os
import mysql.connector
from dotenv import load_dotenv
import datetime
import decimal
import base64
import uuid

env_path = os.path.join(os.path.dirname(__file__), "../configs/.env")
load_dotenv(env_path)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def extract_corrected_sql(ai_message):
    """
    Extracts the corrected SQL query from the AI model's response.
    If no corrected query is found, return the error message.
    
    Args:
        ai_message (object): The AI-generated response containing the corrected SQL query.

    Returns:
        str: Extracted SQL query or error message
    """
    if hasattr(ai_message, 'content'):
        content = ai_message.content.strip()

        if "**Corrected SQL Query:**" in content:
            query = content.split("**Corrected SQL Query:**")[-1].strip()
            return query
        else: 
            return ai_message.content  # If no corrected query, return the full response as an error

def establish_mysql_connection():
    """
    Attempts to establish a connection to the MySQL database.
    Returns 'Connection established' if successful, otherwise returns an error message.

    Returns:
        str: Success message or error message
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.close()
        return "Connection established"
    except mysql.connector.Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def execute_select_query(query: str):
    """Executes a SELECT query and returns the results."""
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description] if cursor.description else []

        return {"success": True, "columns": column_names, "result": results}

    except mysql.connector.Error as e:
        return {"failed_query": query, "success": False, "error": f"MySQL Error: {e}"}
    except Exception as e:
        return {"failed_query": query, "success": False, "error": f"Unexpected Error: {e}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def execute_modify_query(query: str):
    """Executes an INSERT, UPDATE, DELETE, or other modification query."""
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        affected_rows = cursor.rowcount

        return {"success": True, "columns": [], "result": f"Query executed successfully."}

    except mysql.connector.Error as e:
        return {"failed_query": query, "success": False, "result": f"MySQL Error: {e}"}
    except Exception as e:
        return {"failed_query": query, "success": False, "result": f"Unexpected Error: {e}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def execute_query(query: str):
    """Identifies the query type and calls the appropriate execution function."""
    query_type = query.strip().lower().split()[0]  # Get the first word (SELECT, INSERT, etc.)

    if query_type == "select":
        return execute_select_query(query)
    else:
        return execute_modify_query(query)

def serialize(obj):
    """Convert non-serializable objects into JSON-serializable format."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode("utf-8")
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# # Example Usage:
# test_query = "SELECT * FROM staff"
# print(execute_query(test_query))

# modify_query = "INSERT INTO staff (first_name, last_name, address_id, store_id, username) VALUES ('looza', 'subedy', 1, 1, 'looza');"
# print(execute_query(modify_query))
