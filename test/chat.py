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

post_chat("今年国庆的新增认购？")
#post_chat("认签比完成最差的项目有哪些")
#post_chat("查询当月签约达成率")
#post_chat("当月的新增认购套数和金额是多少？")
#post_chat("其中西部公司是多少")
#post_chat("其中认购套数最高的三个项目")
#post_chat("返回当月的认购缺口")

#post_chat("2022年6月份的认签比是多少")
#post_chat("其中认签比最差的项目有那些")
#post_chat("6月成都锦官天宸项目的认签达成进度是多少")

#post_chat("2024年9月份的签约完成率是多少？")
#post_chat("其中温州立体城的是多少？")
#post_chat("该月温州立体城的预估签约完成率是多少？")

#post_chat("2024年国庆期间的新增认购套数、面积和金额有多少？")
#post_chat("查询与去年国庆期间新增认购套数相差多少？")
#post_chat("成都锦粼湖院2024年国庆与去年国庆相比，新增认购套数相差多少")