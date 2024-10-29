# python3
# -*- coding: utf-8 -*-
from flask import Flask,Response,request,jsonify,render_template
import os
import traceback
from MateGen import MateGen
import json
from audio2text import audio_to_text
from utils import default_converter
app = Flask(__name__)

# 设置环境变量（仅在当前脚本运行期间有效）
os.environ["OPENAI_API_KEY"] = "sk-94987a750c924ae19693c9a9d7ea78f7"

with open('xinxiwang_dictionary.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# 5. **列别名**：如果需要为列创建别名或生成新的列，请使用中文别名。不要在别名周围添加单引号或双引号。如果列代表时长，请在别名中使用括号注明单位，例如：首访转认购平均周期（天）。如果列代表套数、面积、金额、比率等，则在别名中使用括号注明单位，例如：签约套数（套）、签约面积（平方米）、签约金额（元）、签约完成率（%）。

system_prompt = """你是一名数据库专家，请根据用户的输入回答问题。  

1. **理解用户意图**：首先，请仔细阅读用户的请求，并确定他们想要查询的时间范围、主要指标类型（如签约面积、签约金额等）以及是否涉及衍生指标（如日、周、月、季、年、累计、权益前、权益后）。  

2. **使用数据字典**：只能使用提供的数据字典信息生成正确的PostgreSQL语句。如果无法根据提供的信息生成SQL，请说：“提供的表结构信息不足以生成SQL查询。” 禁止随意编造信息。  

3. **表与列关系**：在生成SQL时，请注意不要混淆表与列之间的关系。确保选择的表和列与用户的请求相匹配。  

4. **SQL正确性**：请检查SQL的正确性，包括语法、表名、列名以及日期格式等。同时，确保查询在正确条件下的性能优化。  

5. **SQL准确性**：请按照提供的指标字典中提供的计算规则模板来设计SQL语句，不要无端增删或修改SQL语句，同时需要提取衍生指标来填充计算规则以生成完整正确的SQL语句。

6. **SQL规范性**：生成的SQL语句不能涵盖非法字符如"\n"，请确保生成的SQL语句能直接在数据库上执行。

7. **衍生指标**：如果用户问题涉及衍生指标（如日、周、月、季、年、累计等），请确保在生成的SQL查询语句中考虑这些指标。查询结果中需要将衍生指标与基本指标结合。  

8. **时间范围**：请确保SQL语句能够涵盖用户请求的时间范围。如果用户请求的是一段时间内的数据（如从2023年10月1日至2024年11月3日），请确保SQL语句能够正确提取这段时间内的数据。  

9. **数据呈现**：生成的SQL查询结果应以合适的形式进行数据呈现，确保信息清晰易读。  

10. **冷静判断**：用户进行多轮提问时，冷静判断上下文的相关性，当本轮提问没有指出需要上一轮的数据时，只需要给出这一轮的SQL语句。

请逐步思考生成SQL代码，并按照以下JSON格式响应：  

{  
    "thoughts": "thoughts summary",  
    "sql": "SQL Query to run",  
}  

确保回答是正确的JSON格式，并且可以被Python的json.loads解析。  

"""

mategen = MateGen(api_key=os.getenv("OPENAI_API_KEY"),
                  base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                  model='qwen2.5-72b-instruct',
                  system_content_list=[md_content,system_prompt],
                  available_functions=None)

print("Flask 启动！")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        global mategen

        # 从请求中提取用户输入
        data = request.json

        # 获取用户输入的query字段
        query = data.get('query', '')
        print(f"用户文本提问：{query}")

        # 开启一次新的对话
        if query == 'reset':
            mategen.reset()
            return jsonify({'response': "已删除历史对话信息"})

        # 调用chat函数，返回message消息
        chat_dict = mategen.chat(query)

        def generate_012(chat_dict):
            if chat_dict["status"] == 0:
                yield json.dumps({'status': 'API call failed', 'response': chat_dict["gpt_error_message"]})
            elif chat_dict["status"] == 1:
                yield json.dumps({'response': chat_dict["gpt_response"]})
            elif chat_dict["status"] == 2:
                yield json.dumps({'status': 'SQL query execution failed', 'response': chat_dict["sql_error_message"]})

        def generate_3(chat_dict):
            current_conversation = []
            stream = chat_dict['response_message_stream']

            for data in stream:
                json_data = json.loads(data)
                print(json_data)
                if "content" in json_data:
                    current_conversation.append(json_data["content"])
                    yield json.dumps(json_data)
            final_response = ''.join(current_conversation)
            mategen.messages.messages_append({"role": "assistant", "content": final_response})
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            print(final_response)
            finish_info = {
                "sql_code": chat_dict["sql_code"],
                "sql_response": chat_dict["sql_results_json"],
                "thoughts": chat_dict["thoughts"]
            }
            yield json.dumps(finish_info, default=default_converter)

        if chat_dict["status"] != 3:
            return Response(generate_012(chat_dict), content_type='text/event-stream')
        else:
            return Response(generate_3(chat_dict), content_type='text/event-stream')

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'response': str(e)})


@app.route('/audio', methods=['POST'])
def audio():
    appid = "28851d54"
    secret_key = "f8b62faf11b2f3c4bcd7eb4b930e0437"
    if 'file' in request.files:
        audio_path = './audio/received_audio.wav'
        if os.path.isfile(audio_path):
            os.remove(audio_path)
        audio_file = request.files['file']
        audio_file.save(audio_path)
        query = audio_to_text(audio_path,appid,secret_key)
        print(f"用户语音提问：{query}")
        return jsonify({'response': query})
    else:
        return jsonify({'status': 'error','response': "没有语音文件!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=45104)