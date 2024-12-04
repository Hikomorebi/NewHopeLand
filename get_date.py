# -*- coding: utf-8 -*-
import os
from openai import OpenAI
import json

# 设置环境变量（仅在当前脚本运行期间有效）
os.environ["OPENAI_API_KEY"] = "sk-94987a750c924ae19693c9a9d7ea78f7"

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
model = 'qwen2.5-72b-instruct'

# 调用通义千问 API
def generate_model_date(prompt):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        api_response = response.choices[0].message.content
        # print("API 响应内容:", api_response)  # 打印响应内容
        api_response = api_response.strip().replace('```json', '').replace('```', '')
        try:
            # 尝试将API响应解析为JSON
            response_json = json.loads(api_response)
            return json.dumps(response_json, ensure_ascii=False)
        except json.JSONDecodeError as e:
            print(f"解析API响应为JSON时出错: {e}")
            return "{}"
    except Exception as e:
        print(f"调用API时出错: {e}")
        return "{}"

# 从文件中读取文本内容
def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_holiday_period(query, file_path):
    try:
        # 读取文件内容
        file_content = read_file_content(file_path)

        # 将网页内容作为 prompt 传递给大模型
        prompt = f'''请从下列提问中提取对应假日的开始日期和结束日期： {query} ；
            参考下面的日期数据:\n\n{file_content}，
            当涉及到上面的数据不包含的节假日时，用系统日历进行判断输出，
            返回结果应包含且只能包含以下字段：
            - "开始日期"
            - "结束日期"
            以严格的可直接处理的JSON字符串格式输出，不要包含其他内容。
            '''
        result = generate_model_date(prompt)
        return result

    except Exception as e:
        print(f"处理文件时出错: {e}")
        return "{}"

if __name__ == "__main__":
    # 示例查询
    query = "2024年清明节的净利润是多少"
    file_path = "Database/Date.txt"  # 文件的正确路径
    holiday_period = get_holiday_period(query,file_path)
    print(holiday_period)