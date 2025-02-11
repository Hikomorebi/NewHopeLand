# -*- coding: utf-8 -*-
import os
from openai import OpenAI
import json
from utils import (get_resource_path,
                   load_configuration)

OPENAI_API_KEY, BASE_URL, MODEL_NAME = load_configuration()
# 创建 OpenAI 客户端
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url= BASE_URL
)
model = MODEL_NAME

# 获取 Database 文件夹的路径
database_path = get_resource_path('Database')
# 加载 date.txt
date_path = os.path.join(database_path, 'Date.txt')

with open(date_path, "r", encoding="utf-8") as file:
    file_content =  file.read()

get_data_prompt = f"""
你是一个识别特殊日期的助手，提供如下的特殊日期供你参考：{file_content}；
请将今年理解为2025年，若无特别指明，默认询问今年的特殊日期。请你根据用户的提问判断出用户的问题中是否涉及到特殊日期，如果用户的问题中并不涉及到特殊时间相关或者用户的提问你不知道属于什么特殊日期，请直接回答“无效输入”，无需回答其他任何内容。如果涉及到某一个特殊日期，请你按照以下JSON格式响应，无需生成其他内容：
{{
    "name":"特殊日期的名称",
    "start":"开始日期",
    "end":"结束日期"
}}
示例：
user:今年中秋的新增认购是多少？
assistant:
{{
    "name":"今年中秋节",
    "start":"2025年10月6日",
    "end":"2025年10月8日"
}}
user:去年端午期间的新增认购是多少？
assistant:
{{
    "name":"去年端午节",
    "start":"2024年6月10日",
    "end":"2024年6月10日"
}}
user:本月的新增认购是多少？
assistant:无效输入

现在用户进行提问：
user:<question>
assistant:
"""


# 调用通义千问 API
def generate_special_date(prompt):
    try:
        response = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": get_data_prompt.replace("<question>",prompt)}]
        )
        api_response = response.choices[0].message.content
        # print("API 响应内容:", api_response)  # 打印响应内容
        api_response = api_response.strip()
        print(api_response)
        try:
            response_json = json.loads(api_response)
            description = f"{response_json['name']}的时间范围为{response_json['start']}至{response_json['end']}。"
            return description
        except Exception:
            return ""
    except Exception as e:
        print(f"日期工具调用出错: {e}")
        return ""

def get_enhanced_query(query):
    special_date = generate_special_date(query)
    if special_date:
        enhanced_query = special_date + query 
    else:
        enhanced_query = query
    return enhanced_query

if __name__ == "__main__":
    # 示例查询
    query = "去年中秋新增认购是多少？"
    holiday_period = get_enhanced_query(query)
    print(holiday_period)
