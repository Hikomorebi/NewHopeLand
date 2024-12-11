
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
SELECT phone, name, project_name, report_type, customer_name, customer_phone, intention_level FROM fdc_ods.ods_hwy_ai_nh_high_intent_report_a_d WHERE partitiondate = current_date - 1 AND report_date BETWEEN date_trunc('month', current_date) AND current_date AND (intention_level LIKE '%A%' OR intention_level LIKE '%B%')
"""

dws_connect_test(query)