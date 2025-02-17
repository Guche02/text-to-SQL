import mysql.connector

# Establish connection
conn = mysql.connector.connect(
    host="localhost",     
    user="root",  
    password="12345",  
    database="company" 
)

cursor = conn.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

print("Tables in the database:")
for table in tables:
    print(table[0])

cursor.close()
conn.close()
