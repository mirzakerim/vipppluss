import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def execute_query(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        return True
    except Error as e:
        print(f"Error: {e}")
        return False

def fetch_query(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Error: {e}")
        return None

def get_user_level(telegram_id):
    connection = create_connection()
    query = "SELECT user_level FROM users WHERE telegram_id = %s"
    data = (telegram_id,)
    result = fetch_query(connection, query, data)
    connection.close()  # افزودن این خط برای بستن اتصال به دیتابیس
    if result:
        return result[0][0]
    return None
