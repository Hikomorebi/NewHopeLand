
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
SELECT 
    SUM(首访客户数) AS 首访客户数总和
FROM (
    SELECT 
        COUNT(DISTINCT CASE WHEN isvisit = '否' THEN saleruserId ELSE NULL END) AS 首访客户数
    FROM fdc_dwd.dwd_cust_custvisitflow_a_min
    WHERE partitiondate = CURRENT_DATE
    AND left(visitDate, 10) = current_date
    GROUP BY projname
) AS proj_summary;
"""

dws_connect_test(query)