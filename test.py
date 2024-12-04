import psycopg2
from psycopg2.extras import RealDictCursor
import csv

# 连接数据库查询来访人数信息
def query_visitornum_info():
    connection = psycopg2.connect(dbname="fdc_dc",
                                  user="dws_user_hwai",
                                  password="NewHope#1982@",
                                  host="124.70.57.67",
                                  client_encoding='UTF8',
                                  port="8000")
    print("连接成功！")

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            sql = """
            select t3.openid from fdc_ext.ext_qw_market_qywx_address_user_info t1 inner join fdc_ext.ext_qw_market_g_user_bind_account t2 on t1.user_id = t2.userId inner join fdc_ext.ext_qw_market_g_user t3 on t3.openid = t2.openid where t1.mobile = '15680695658';
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            print(f"查询信息成功！")
            # 检查是否有查询结果
            if result:
                openid = result[0]['openid']  # 假设查询结果只有一个openid、即 mobile和 id一一对应
                openid= 'oFUZO593EQQzgv3ZoDXG7IZoCcDs'
                print(openid)
                # 第二个SQL查询，使用查询出的openid
                sql2 = """
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
                        u.saleropenid = %s AND u.createtime >= %s  AND u.createtime < %s
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
                """
                # 定义查询参数
                start_date = '1990-01-01'  # 根据需要设置开始日期
                end_date = '2024-12-03'    # 根据需要设置结束日期
                cursor.execute(sql2, (openid, start_date, end_date))
                ranked_result = cursor.fetchall()
                print(f"查询客户信息成功！")

                # 将结果写入CSV文件
                write_to_csv(ranked_result, 'visitor_info.csv')
            else:
                print("没有查询到openid信息。")
            return result
    except Exception as e:
        print(f"查询信息时出错: {e}")
        return []
    finally:
        connection.close()

# 将查询结果写入CSV文件
def write_to_csv(data, filename):
    # 获取字段名（即列名）
    fieldnames = data[0].keys() if data else []
    
    # 打开文件并写入CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # 写入表头
        writer.writeheader()
        
        # 写入数据行
        writer.writerows(data)
        
        print(f"数据已成功写入 {filename}")

# 调用函数执行查询并保存数据
if __name__ == "__main__":
    query_visitornum_info()