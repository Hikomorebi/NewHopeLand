
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
SELECT rt_c.projname, sum(nvl(rt_c.sub_amt, 0) - nvl(rt_b.sub_amt, 0)) AS subamount FROM fdc_dws.dws_proj_room_totalsale_a_min rt_c LEFT JOIN fdc_dws.dws_proj_room_totalsale_a_min rt_b ON rt_c.datadate = date_trunc('month', current_date) - interval '1 day' AND rt_c.roomcode = rt_b.roomcode WHERE rt_b.datadate = date_trunc('month', current_date) - interval '1 month' - interval '1 day' AND rt_c.partitiondate = date_trunc('month', current_date) - interval '1 day' AND rt_c.cityname LIKE '%西部区域%' AND rt_c.projname LIKE '%锦粼湖院%' GROUP BY rt_c.projname

"""

dws_connect_test(query)