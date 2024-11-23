
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
SELECT SUM(subscramount) AS 新增认购金额, COUNT(1) AS 新增认购套数 FROM fdc_dwd.dwd_trade_roomsubscr_a_min WHERE partitiondate = current_date AND subscrexecdate BETWEEN '2024-11-01' AND '2024-11-30' AND (subscrstatus = '激活' OR closereason = '转签约');
"""

dws_connect_test(query)