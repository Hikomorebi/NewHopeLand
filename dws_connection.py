
import time
import psycopg2
def dws_connect_test(sql_query):
    connection = psycopg2.connect(
        dbname="fdc_dc",
        user="dws_user_hwai",
        password="NewHope#1982@",
        host="124.70.57.67",
        port="8000",
    )
    connection.set_client_encoding('UTF8')
    print("连接成功")

    try:
        with connection.cursor() as cursor:
            start_time = time.time()
            cursor.execute(sql_query)

            results = cursor.fetchall()
            end_time = time.time()
            elapsed_time = end_time - start_time
            column_description = cursor.description
            print(f"查询耗时{elapsed_time}秒")
            print(results)
            print(column_description)
    except Exception as e:
        print(str(e))
    finally:
        connection.close()


query = """
SELECT EXTRACT(MONTH FROM visitdate::timestamp) AS month, projname, SUM(visitorcount) AS total_visits, tradechannel FROM fdc_dwd.dwd_cust_custvisitflow_a_min WHERE projname LIKE '%武汉锦粼九里%' AND partitiondate = current_date AND visitdate::timestamp BETWEEN '2023-01-01' AND '2023-06-30' GROUP BY month, projname, tradechannel ORDER BY month;
"""

dws_connect_test(query)