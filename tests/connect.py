import mysql.connector

# Establish connection
conn = mysql.connector.connect(
    host=" ",     
    user=" ",  
    password=" ",  
    database=" " 
)

cursor = conn.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

print("Tables in the database:")
for table in tables:
    print(table[0])

cursor.close()
conn.close()
