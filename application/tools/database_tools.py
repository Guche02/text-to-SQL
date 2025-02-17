import os
import mysql.connector
from langchain.tools import tool
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), "../configs/.env")
load_dotenv(env_path)

# Retrieve database credentials from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

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
    except Exception as e:
        return f"Failed to establish connection: {e}"

@tool(parse_docstring=True)
def execute_query(query: str):
    """
    Attempts to execute the generated SQL query.
    Returns results if successful, otherwise returns an error message.

    Args:
        query (str): The SQL query to be executed.

    Returns:
        list or dict: Query results or error message
    """
    conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    try:
     return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "failed_query": query, "error": str(e)}