
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
select rt_c.projname, sum(nvl(rt_c.sign_amt, 0) - nvl(rt_b.sign_amt, 0)) as signamount from fdc_dws.dws_proj_room_totalsale_a_min rt_c left join fdc_dws.dws_proj_room_totalsale_a_min rt_b on rt_c.datadate = '2024-10-07' and rt_c.roomcode = rt_b.roomcode where rt_b.datadate = '2024-10-01' group by rt_c.projname order by signamount desc limit 3
"""

dws_connect_test(query)