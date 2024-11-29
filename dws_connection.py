
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
SELECT rt_c.cityname, SUM(rt_c.sub_amt - rt_b.sub_amt) AS subamount FROM fdc_dws.dws_proj_room_totalsale_a_min rt_c LEFT JOIN fdc_dws.dws_proj_room_totalsale_a_min rt_b ON rt_c.datadate = '2024-11-01' AND rt_c.roomcode = rt_b.roomcode WHERE rt_b.datadate = current_date AND rt_c.partitiondate = current_date GROUP BY rt_c.cityname;
"""

dws_connect_test(query)