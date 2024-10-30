import psycopg2
import pymysql


def connect_to_db():
    conn = pymysql.connect(
        host="8.137.93.112",
        port=3306,
        user="new_hope",
        password="nA48AAse3kCpChnh",
        db="new_hope_estate_db",
    )
    cur = conn.cursor()
    return conn, cur
conn, cursor = connect_to_db()
query = """  
SELECT DATA_SET_JSON, CONTENT 
FROM nh_chat_history
WHERE SESSION_ID=123
"""
cursor.execute(query)
a = {row[0]: row[1] for row in cursor.fetchall()}
print(a)
