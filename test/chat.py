import requests
import json
import re
import time


def post_chat(query):
    # 接口地址
    url = "http://me.ilisa.team:45108/chat"
    headers = {"Content-Type": "application/json"}
    #data = {"session_id":"2","query": query,"dataSource":'{"fdc_dws":["dws_proj_room_totalsale_a_min"]}'}
    data = {"session_id":"5","query": query,"dataSource":''}
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"发出请求到获取回答总用时: {elapsed_time:.4f} 秒")
            response.encoding = "utf-8"  # 设置编码以正确显示中文字符
            try:
                response_json = response.json()
                # 使用 ensure_ascii=False 以正确显示中文字符
                print("Response:", json.dumps(response_json, ensure_ascii=False))
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"操作耗时: {elapsed_time:.4f} 秒")
            except json.JSONDecodeError:
                # 使用encode().decode()以确保显示中文
                answer = response.text.encode("utf-8").decode("unicode_escape")
                content = re.findall(r'"content": "(.*?)"', answer)
                content = "".join(content)
                sql_code = re.findall(r'"sql_code": "(.*?)"', answer)
                sql_code = "".join(sql_code)
                sql_response = re.findall(r'"sql_response": \{.*, "chosen_tables"', answer)
                sql_response = "".join(sql_response)

                print(data)
                print(answer)
                print("==========================================================================")
                match = re.search(r'"chosen_tables":\s*({.*?}),\s*"time":\s*"([^"]+)"', answer, re.DOTALL)

                # 提取并输出结果
                if match:
                    chosen_tables = match.group(1)
                    time_ = match.group(2)
                    print(f"chosen_tables: {chosen_tables}")
                    print(f"time: {time_}")
                else:
                    print("没有找到 'chosen_tables' 和 'time' 的相关内容")
                print("content:", content)
                print("sql_code:", sql_code)
                print("sql_response",json.dumps(json.loads(sql_response[15:-17]), indent=4,ensure_ascii=False))

                
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print("Exception occurred:", str(e))



# 1
#post_chat("本月新增认购")
#post_chat("其中西部公司是多少")
#post_chat("西部公司中新增认购套数最高的三个项目")

# 2
#post_chat("返回当月的认购缺口")

# 3
#post_chat("列出每个公司的认签比")
#post_chat("列出全国每个项目的认签比")
#post_chat("认签比完成最差的三个项目")
#post_chat("云境项目的认签达成进度")

# 4
#post_chat("本月签约达成率")

# 5
#post_chat("国庆期间的来访人数有多少？")
#post_chat("与去年国庆相差多少？")
#post_chat("列出其中锦粼湖院的数据")
#post_chat("锦粼湖院的数据与去年国庆相差多少")

# 6
#post_chat("今年双十一期间的新增认购")
#post_chat("与去年同期相差多少")
post_chat("今年中秋期间的新增认购")