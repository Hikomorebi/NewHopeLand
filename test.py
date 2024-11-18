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

                    SELECT 
                        *                       
                    FROM 
                        fdc_ods.ods_qw_market_dh_crm_saleruser
                    WHERE 
                         createtime >= CURRENT_DATE - INTERVAL '3 month' AND createtime < CURRENT_DATE + INTERVAL '1 day'
                        AND partitiondate >= CURRENT_DATE - INTERVAL '3 month' AND partitiondate < CURRENT_DATE + INTERVAL '1 day'
                    LIMIT 3;
        
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            print(f"查询信息成功！")
            
            # 将结果写入CSV文件
            write_to_csv(result, 'visitor_info.csv')
            
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