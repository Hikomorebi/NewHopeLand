import requests
import json
import re
import time


def post_chat(query):
    # 接口地址
    url = "http://me.ilisa.team:45108/chat"
    headers = {"Content-Type": "application/json"}
    data = {"session_id":"322","query": query,"dataSource":'{"fdc_dws":[dws_proj_room_totalsale_a_min]}'}

    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
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
                anwser = response.text.encode("utf-8").decode("unicode_escape")
                content = re.findall(r'"content": "(.*?)"', anwser)
                content = "".join(content)
                sql_code = re.findall(r'"sql_code": "(.*?)"', anwser)
                sql_code = "".join(sql_code)
                sql_response = re.findall(r'"sql_response": \{.*\}', anwser)
                sql_response = "".join(sql_response)
                # thoughts = re.findall(r'"thoughts": "(.*?)"', anwser)
                # thoughts = "".join(thoughts)
                print(data)
                print("==========================================================================")
                print("content:", content)
                print("sql_code:", sql_code)
                print("sql_response",json.dumps(json.loads(sql_response[15:-1]), indent=4,ensure_ascii=False))
                # print("thoughts:", thoughts)
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"操作耗时: {elapsed_time:.4f} 秒")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print("Exception occurred:", str(e))


post_chat("查询广佛悦珑湾在2022年的计划签约金额是多少，给出具体值")