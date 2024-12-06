
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
select a.cityname as 公司, a.subscramount/nullif(b.plansignamount, 0) as 认签比, a.subscramount as 月度新增认购金额, b.plansignamount as 月度签约任务, nvl(a.subscramount/nullif(b.plansignamount, 0), 0) - EXTRACT(DAY FROM CURRENT_DATE)::FLOAT / EXTRACT(DAY FROM last_day(current_date)) 认签比达成进度 from ( select citycode, cityname, sum(subscramount) as subscramount from fdc_dwd.dwd_trade_roomsubscr_a_min where partitiondate = current_date and subscrexecdate between date_trunc('month', current_date) and current_date and (subscrstatus = '激活' or closereason = '转签约') group by 1,2 ) a left join ( select cityCode, sum(m12PlanSignAmount) plansignamount from fdc_dws.dws_proj_projplansum_a_h where partitiondate = current_date and years = left(current_date, 4) group by citycode ) b on a.citycode = b.citycode
"""

dws_connect_test(query)