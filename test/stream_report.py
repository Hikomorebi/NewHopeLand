import requests
import json
import re


def post_analysis(saleropenid,start_date,end_date):
    # 接口地址
    url = "http://me.ilisa.team:45102/analysis"
    headers = {"Content-Type": "application/json"}
    data = {"saleropenid": saleropenid,"start_date":start_date,"end_date":end_date}

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
                # print("thoughts:", thoughts)
    except Exception as e:
        print("Exception occurred:", str(e))


post_analysis("oFUZO5xjO671mxo3fSQ3Fkldlaj8","2024-01-01","2024-10-31")