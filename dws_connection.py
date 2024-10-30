#!/usr/bin/env python3
# _*_ encoding=utf-8 _*_

import psycopg2
from psycopg2.extras import RealDictCursor

def dws_connect():
    # 创建连接
    conn = psycopg2.connect(dbname="fdc_dc",
                            user="dws_user_hwai",
                            password="NewHope#1982@",
                            host="124.70.57.67",
                            port="8000")
    print("连接成功")

    # 使用默认游标执行SQL，查询结果是元祖
    query = "SELECT datadate FROM fdc_dws.dws_proj_projplansum_a_h LIMIT 10;"
    
    print("Start to execute: \"%s\"" % query)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    print("Output:")
    print(', '.join([field.name for field in cursor.description]))
    for row in rows:
        print(', '.join([str(e) for e in row]))
    cursor.close()

    # 使用RealDictCursor游标执行SQL，查询结果是字典
    '''query = "select * from student"

    print("Start to execute: \"%s\"" % query)
    cursor = conn.cursor(cursor_factory = RealDictCursor)
    cursor.execute(query)
    records = cursor.fetchall()
    field_names = [field.name for field in cursor.description]
    cursor.close()

    print("Output:")
    row = 0
    for record in records:
        row += 1
        print("-[ RECORD %d ]-" % row)
        for name in field_names:
            print("%-5s | %-5s" % (name, record[name]))
    print("(%d %s)" % (row, "rows" if row > 1 else "row"))

    conn.close()'''
