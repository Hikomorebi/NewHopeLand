
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
SELECT COUNT(1) AS 新增认购套数, SUM(a.archArea) AS 新增认购面积, SUM(a.subscramount * b.equityratio) AS 权益后新增认购金额 FROM fdc_dwd.dwd_trade_roomsubscr_a_min a LEFT JOIN fdc_ads.view_proj_equity_his b ON a.projcode = b.projcode AND a.subscrexecdate BETWEEN b.validdate AND b.invaliddate WHERE a.partitiondate = CURRENT_DATE AND a.subscrexecdate BETWEEN date_trunc('year', current_date) AND current_date AND (a.subscrstatus = '激活' OR a.closereason = '转签约') AND a.cityname LIKE '%西部区域%'

"""

dws_connect_test(query)