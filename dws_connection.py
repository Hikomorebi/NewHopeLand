
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
WITH current_period AS (SELECT COUNT(DISTINCT CASE WHEN isvisit = '否' THEN saleruserId ELSE NULL END) AS 当期数据 FROM fdc_dwd.dwd_cust_custvisitflow_a_min WHERE partitiondate = CURRENT_DATE AND LEFT(visitDate, 10) BETWEEN '2024-12-01' AND '2024-12-31'), previous_period AS (SELECT COUNT(DISTINCT CASE WHEN isvisit = '否' THEN saleruserId ELSE NULL END) AS 基期数据 FROM fdc_dwd.dwd_cust_custvisitflow_a_min WHERE partitiondate = CURRENT_DATE AND LEFT(visitDate, 10) BETWEEN '2024-11-01' AND '2024-11-30') SELECT CAST((current_period.当期数据 - previous_period.基期数据) * 1.0 / NULLIF(previous_period.基期数据, 0) AS DECIMAL(10, 4)) AS 首访客户数环比增长率 FROM current_period, previous_period
"""

dws_connect_test(query)