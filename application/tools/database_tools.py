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
    except mysql.connector.Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
    
def extract_corrected_sql(ai_message):
    """
    Extracts the corrected SQL query from the AI model's response.
    If no corrected query is found, return the error message.
    """
    if hasattr(ai_message, 'content'):
        content = ai_message.content  
        if "**Corrected SQL Query:**" in content:
            query = content.split("**Corrected SQL Query:**")[-1].strip()
        # elif "***SQL Query:***" in content:
        #     query = content.split("**SQL Query:**")[-1].strip()
        
        #     print("\nExtracted SQL Query:\n", query)
        #     return query
        else: 
           return ai_message.content  # If no corrected query, return the full response as error

def execute_query(query: str):
    """
    Attempts to execute the generated SQL query.
    Returns results if successful, otherwise returns an error message.

    Args:
        query (str): The SQL query to be executed.

    Returns:
        dict: Query results or error message
    """
    try:
        # Attempt to connect to the database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return {"success": True, "result": result}

        except mysql.connector.ProgrammingError as e:
            return {"success": False, "error": f"SQL Syntax Error: {e}", "failed_query": query}
        except mysql.connector.IntegrityError as e:
            return {"success": False, "error": f"Integrity Constraint Violation: {e}", "failed_query": query}
        except mysql.connector.DatabaseError as e:
            return {"success": False, "error": f"Database Error: {e}", "failed_query": query}
        except Exception as e:
            return {"success": False, "error": f"Unexpected Error in Query Execution: {e}", "failed_query": query}
        
        finally:
            cursor.close()

    except mysql.connector.InterfaceError as e:
        return {"success": False, "error": f"Connection Error: {e}"}
    except mysql.connector.OperationalError as e:
        return {"success": False, "error": f"Operational Error: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected Error: {e}"}

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
