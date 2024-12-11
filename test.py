import psycopg2
from psycopg2.extras import RealDictCursor

# 连接数据库查询客户信息
def query_customer_info(start_date, end_date):
    connection = psycopg2.connect(dbname="fdc_dc",
                                  user="dws_user_hwai",
                                  password="NewHope#1982@",
                                  host="124.70.57.67",
                                  client_encoding='UTF8',
                                  port="8000")
    print("连接DWS数据库成功！")

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            sql = """
            WITH ranked_customers AS (
                SELECT 
                    u.id, u.createtime, u.username, u.age, u.familystructure, u.mobile, 
                    u.qualified, u.visitcounts, u.budget, u.customerresource, u.mymttj, u.work, u.live, u.industry, u.jobs,
                    u.house, u.purpose, u.floor, u.interest, u.userrank, u.memo , u.saleropenid,
                    u.buyuse, u.dealway, u.channel, u.unitprice, u.customerchannel,  u.customer_id, u.income,
                    u.area, u.visitamount, u.memo1, u.abandon_reason, u.notbuyreason, u.layouttype, u.buyfactor, u.interestlayout,
                    ROW_NUMBER() OVER (PARTITION BY u.username, u.mobile ORDER BY u.createtime DESC) as row_num
                FROM 
                    fdc_ods.ods_qw_market_dh_crm_saleruser u
                WHERE 
                    u.projectid ='8194' AND u.createtime >= %s  AND u.createtime < %s
                    AND u.partitiondate >= CURRENT_DATE - INTERVAL '1 day' AND u.partitiondate < CURRENT_DATE + INTERVAL '1 day'
            )
            SELECT 
                id, createtime, username, age, familystructure, mobile, 
                qualified, visitcounts, budget, customerresource, mymttj, work, live, industry, jobs,
                house, purpose, floor, interest,  userrank, memo , saleropenid,
                buyuse, dealway, channel, unitprice, customerchannel,  customer_id, income,
                area, visitamount, memo1 , abandon_reason, notbuyreason, layouttype, buyfactor, interestlayout,
                row_num
            FROM 
                ranked_customers
            WHERE 
                row_num = 1
                ;
            """
            cursor.execute(sql, (start_date, end_date))
            result = cursor.fetchall()
            print("查询客户信息成功！")
            return result
    except Exception as e:
        print(f"查询客户信息时出错: {e}")
        return []
    finally:
        connection.close()

# 示例调用
start_date = '2023-05-11 00:00:00'
end_date = '2023-05-11 23:59:59'
customer_info = query_customer_info(start_date, end_date)

# 统计不同saleropenid名下的数据条数
saleropenid_counts = {}
for customer in customer_info:
    saleropenid = customer['saleropenid']
    if saleropenid in saleropenid_counts:
        saleropenid_counts[saleropenid] += 1
    else:
        saleropenid_counts[saleropenid] = 1

# 打印统计结果
for saleropenid, count in saleropenid_counts.items():
    print(f"saleropenid {saleropenid} 查询结果中共有 {count} 条数据")

# 计算并打印总数据条目数
total_data_count = sum(saleropenid_counts.values())
print(f"总共有 {total_data_count} 条数据条目")