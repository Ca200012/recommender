import mysql.connector
from data_retrieval import (
    get_data
)

from data_transformation import (
    transform_data
)

items = get_data()

transformed_data = transform_data(items)

print (len(transformed_data))
# Crearea conexiunii la baza de date
def create_conn():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='licenta-back'
    )
    if conn.is_connected():
        print("Successfully connected to the database.")
    else:
        print("Failed to connect to the database.")
    return conn

# Vom folosi acest obiect pentru a interactiona cu baza de date
conn = create_conn()

# Inchidem conexiunea cu baza de date
conn.close()