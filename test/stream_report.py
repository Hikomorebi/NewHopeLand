import requests
import json
import re


def post_analysis():
    # 接口地址
    url = "http://me.ilisa.team:45108/analysis"
    headers = {"Content-Type": "application/json"}
    data = {"saleropenid":"oFUZO5y9WDfaH-JVkkchVCRuLfRo","projectId":"8217","projectName":"华东公司四季春晓","start_date":"2024-11-20 00:00:00","end_date":"2024-11-20 23:59:59"}

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


post_analysis()