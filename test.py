import mysql.connector

# 配置数据库连接参数
config = {
    'user': 'fr_zypt_hw',
    'password': 'WqZp4G7h$2Tr!9',
    'host': 'bj-cdb-4s207vhc.sql.tencentcdb.com',
    'port': 59639,
    'database': 'fr_zypt_hw'
}

# 建立连接
try:
    conn = mysql.connector.connect(**config)
    print("数据库连接成功！")
    
    # 创建游标
    cursor = conn.cursor()
    
    # 查询所有表
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("数据库中的表：")
    for table in tables:
        table_name = table[0]
        print(f"表名: {table_name}")
        
        # 查询表结构
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        print("列信息：")
        for column in columns:
            print(column)
        
        # 查询表数据
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        print("表数据：")
        for row in rows:
            print(row)
        
        print("\n")
    
except mysql.connector.Error as e:
    print(f"连接失败: {e}")
finally:
    if conn.is_connected():
        conn.close()
        print("数据库连接已关闭")