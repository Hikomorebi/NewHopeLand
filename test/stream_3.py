import requests
import json


def post_chat(query):
    # 接口地址
    url = "http://me.ilisa.team:45108/match"
    headers = {"Content-Type": "application/json"}
    data = {"query": query}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            response.encoding = "utf-8"  # 设置编码以正确显示中文字符
            try:
                response_json = response.json()
                # 使用 ensure_ascii=False 以正确显示中文字符
                print("Response:", json.dumps(response_json, ensure_ascii=False))
            except json.JSONDecodeError:
                pass
                # 使用encode().decode()以确保显示中文
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print("Exception occurred:", str(e))
post_chat("查询语句")