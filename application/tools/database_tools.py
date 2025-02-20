import os
import mysql.connector
from langchain.tools import tool
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
    Returns results along with column names as the first row if successful, otherwise returns an error message.

    Args:
        query (str): The SQL query to be executed.

    Returns:
        dict: Query results as a list with column names as the first row (if successful), or error message.
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
            column_names = [desc[0] for desc in cursor.description]  # Extract column names
            
            # Append column names as the first row in results
            structured_result = [tuple(column_names)] + result  

            return {"success": True, "columns": column_names, "result": structured_result}

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

def serialize(obj):
    """Convert non-serializable objects into JSON-serializable format."""
    if isinstance(obj, datetime.datetime):  # Access datetime class through the module
        return obj.isoformat()  # Convert datetime to ISO format string
    elif isinstance(obj, datetime.date):  # Handle both date and datetime objects
        return obj.isoformat()  # Convert date to ISO format string
    elif isinstance(obj, decimal.Decimal):
        return float(obj)  # Convert Decimal to float
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode("utf-8")  # Encode bytes to a base64 string
    elif isinstance(obj, uuid.UUID):
        return str(obj)  # Convert UUID to string
    # You can add more custom types here as needed
    raise TypeError(f"Type {type(obj)} not serializable")


# test = """
# SELECT s.`store_id`, s.`manager_staff_id`, a.`address`, a.`city_id`, c.`city`, c.`country_id`, co.`country`
# FROM `store` s
# JOIN `address` a ON s.`address_id` = a.`address_id`
# JOIN `city` c ON a.`city_id` = c.`city_id`
# JOIN `country` co ON c.`country_id` = co.`country_id`
# JOIN `staff` st ON s.`manager_staff_id` = st.`staff_id`
# LIMIT 10;
# """

# response = execute_query(test)
# print(response)