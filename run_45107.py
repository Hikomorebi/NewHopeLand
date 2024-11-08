# python3
# -*- coding: utf-8 -*-
from flask import Flask, Response, request, jsonify
import os
import traceback
from MateGen import MateGen
import json
from audio2text import audio_to_text
from generate_report import generate_markdown_report, query_customer_info
from utils import (
    default_converter,
    query_tables_description,
    get_session_messages,
    get_used_tables,
)

app = Flask(__name__)

# 设置环境变量（仅在当前脚本运行期间有效）
os.environ["OPENAI_API_KEY"] = "sk-94987a750c924ae19693c9a9d7ea78f7"

# 先不读取这个字典了，存在问题
# with open('xinxiwang_dictionary.md', 'r', encoding='utf-8') as f:
#     md_content = f.read()

system_prompt_common = """
你是一名数据库专家，请根据用户的输入回答问题。
1. **理解用户意图**：首先，请仔细阅读并理解用户的请求，使用数据库字典提供的表结构和各字段信息创建正确的PostgreSQL语句。
2. **使用数据字典**：只能使用提供的数据信息生成正确的PostgreSQL语句。如果无法根据提供的信息生成SQL，请说：“提供的表结构信息不足以生成SQL查询。” 禁止随意编造信息。  
3. **表与列关系**：在生成SQL时，请注意不要混淆表与列之间的关系。确保选择的表和列与用户的请求相匹配。  
4. **SQL正确性**：请检查SQL的正确性，包括语法、表名、列名以及日期格式等。同时，确保查询在正确条件下的性能优化。  
5. **SQL规范性**：生成的SQL语句不能涵盖非法字符如"\n"，请确保生成的SQL语句能直接在数据库上执行。
6. **时间范围**：请确保SQL语句能够涵盖用户请求的时间范围。如果用户请求的是一段时间内的数据，请确保SQL语句能够正确提取这段时间内的数据。
7. **完整代码**：已知现在的时间是2024年11月。请生成完整的、可执行的SQL语句，不要包含任何形式的占位符或模板变量。确保所有字段和条件都使用具体的值。
8. **数据呈现**：生成的SQL查询结果应以合适的形式进行数据呈现，确保信息清晰易读。
请逐步思考生成并SQL代码，并按照以下JSON格式响应：
{
    "thoughts": "thoughts summary",
    "sql": "SQL Query to run",
}
确保回答是正确的JSON格式，并且可以被Python的json.loads解析。
"""
system_prompt_indicator_template = """
以json格式给出指标{indicator}的描述，
{indicator_json}
你是一名数据库专家，请根据指标描述生成正确的PostgreSQL语句。
1. **理解用户意图**：请仔细阅读并理解用户的请求，使用数据库字典提供的表结构和各字段信息，以及指标描述中的计算规则生成SQL语句。
2. **使用计算规则**：请完全按照提供的计算规则模板来设计SQL语句，不要无端自行增删或修改计算规则，同时需要从用户问题中提取相关的时间等信息来填充计算规则中带有'$'符号的部分以生成完整正确的SQL语句。
3. **SQL规范性**：生成的SQL语句不能涵盖非法字符如"\n"，请确保生成的SQL语句能直接在数据库上执行。
请逐步思考生成并SQL代码，并按照以下JSON格式响应：  
{{
    "thoughts": "thoughts summary",
    "sql": "SQL Query to run",
}}
"""
mategen = MateGen(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen2.5-72b-instruct",
    system_content_list=[system_prompt_common],
)
current_session_id = -1

print("Flask 启动！")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        global mategen
        global current_session_id

        data = request.json

        print(data)

        try:
            # 暂时使用从请求的dataSource字段中获取used_tables，后续实现根据session_id查华菁数据库获取used_tables信息
            used_tables_ = json.loads(data.get("dataSource"))
        except Exception as e:
            # 捕获其他可能的错误
            print(str(e))
            used_tables_ = None
        print(used_tables_)

        # 获取当前会话id
        session_id = data.get("session_id")

        # 如果请求中会话id发生变化，则说明切换会话或开启新会话，需要重新加载历史会话
        if session_id != current_session_id:
            current_session_id = session_id

            # 根据session_id获取历史消息，查询华菁数据库nh_chat_history表中CONTENT字段，注意需要去除id的内容。若为空，则说明开启的是新会话，返回NULL
            session_messages = get_session_messages(current_session_id)
            # 根据session_id获取使用到的表，查询华菁数据库nh_chat_history表中DATA_SET_JSON字段获取
            used_tables = used_tables_ if used_tables_ else get_used_tables(current_session_id)

            # 根据used_tables拼接获得数据字典
            data_dictionary_md = query_tables_description(used_tables)

            # 更换messages对象对应的数据字典部分
            mategen.replace_data_dictionary(data_dictionary_md)

            # 加载历史会话记录
            mategen.add_session_messages(session_messages)

        # 获取用户输入的query字段
        query = data.get("query")
        print("\n\n++++++++++++++++++++++++++++++")
        print(f"用户文本提问：{query}")

        # 开启一次新的对话
        if query == "reset":
            mategen.reset()
            return jsonify({"response": "已删除历史对话信息"})

        # 调用chat函数，返回message消息
        chat_dict = mategen.chat(query)

        def generate_012(chat_dict):
            if chat_dict["status"] == 0:
                yield json.dumps(
                    {
                        "status": "API call failed",
                        "response": chat_dict["gpt_error_message"],
                    }
                )
            elif chat_dict["status"] == 1:
                yield json.dumps({"response": chat_dict["gpt_response"]})
            elif chat_dict["status"] == 2:
                yield json.dumps(
                    {
                        "status": "SQL query execution failed",
                        "response": chat_dict["sql_error_message"],
                    }
                )

        def generate_3(chat_dict):
            current_conversation = []
            stream = chat_dict["response_message_stream"]

            for data in stream:
                json_data = json.loads(data)
                print(json_data)
                if "content" in json_data:
                    current_conversation.append(json_data["content"])
                    yield json.dumps(json_data)
            final_response = "".join(current_conversation)
            mategen.messages.messages_append(
                {"role": "assistant", "content": final_response}
            )
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            print(final_response)
            finish_info = {
                "sql_code": chat_dict["sql_code"],
                "sql_response": chat_dict["sql_results_json"],
            }
            yield json.dumps(finish_info, default=default_converter)

        if chat_dict["status"] != 3:
            return Response(generate_012(chat_dict), content_type="text/event-stream")
        else:
            return Response(generate_3(chat_dict), content_type="text/event-stream")

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "response": str(e)})


@app.route("/audio", methods=["POST"])
def audio():
    appid = "28851d54"
    secret_key = "f8b62faf11b2f3c4bcd7eb4b930e0437"
    if "file" in request.files:
        audio_path = "./audio/received_audio.wav"
        if os.path.isfile(audio_path):
            os.remove(audio_path)
        audio_file = request.files["file"]
        audio_file.save(audio_path)
        query = audio_to_text(audio_path, appid, secret_key)
        print(f"用户语音提问：{query}")
        return jsonify({"response": query})
    else:
        return jsonify({"status": "error", "response": "没有语音文件!"})


@app.route("/analysis", methods=["POST"])
def analysis():
    try:
        data = request.json
        saleropenid = data.get("saleropenid")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if not all([saleropenid, start_date, end_date]):
            return jsonify({"status": "error", "response": "缺少必要的参数：saleropenid, start_date 或 end_date"})

        customers = query_customer_info(saleropenid, start_date, end_date)
        if not customers:
            return jsonify({"status": "error", "response": "未查询到相关客户信息。"})

        report = generate_markdown_report(customers, saleropenid)

        report_filename = f"高意向客户分析报告_{saleropenid}.md"
        with open(report_filename, "w", encoding="utf-8") as file:
            file.write(report)

        return jsonify({"status": "success", "response": report})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "response": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=45107)