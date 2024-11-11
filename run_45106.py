# python3
# -*- coding: utf-8 -*-
from flask import Flask, Response, request, jsonify
import os
import traceback
from MateGen import MateGen
import json
from generate_report import generate_markdown_report, query_customer_info
from utils import (
    default_converter,
    query_tables_description,
    query_few_shots,
    get_session_messages,
    test_match,
    dict_intersection
)
from auto_select_tables import select_table_based_on_query
app = Flask(__name__)

# 设置环境变量（仅在当前脚本运行期间有效）
os.environ["OPENAI_API_KEY"] = "sk-94987a750c924ae19693c9a9d7ea78f7"

system_prompt_common = """
你是一名数据库专家，请根据用户的输入回答问题。
1. 首先，请仔细阅读并理解用户的请求，使用数据库字典提供的表结构和各字段信息创建正确的PostgreSQL语句。
2. 只能使用提供的数据字典信息生成正确的PostgreSQL语句。已知现在的时间是2024年11月。请生成完整的、可执行的SQL语句，不要包含任何形式的占位符或模板变量。确保所有字段和条件都使用具体的值。禁止随意假设不存在的信息。
3. 在生成SQL时，请注意不要混淆表与列之间的关系。确保选择的表和列与用户的请求相匹配。
4. 请确保SQL的正确性，包括语法、表名、列名以及日期格式等。同时，确保查询在正确条件下的性能优化。如果数据字典中存在partitiondate字段表，请务必在筛选条件中加入partitiondate=current_date。
5. 生成的SQL语句不能涵盖非法字符如"\n"，请确保生成的SQL语句能直接在数据库上执行。
6. 如果用户请求的是一段时间内的数据，请确保SQL语句能够正确提取这段时间内的数据。
7. 生成的SQL语句选择的字段分为核心字段和相关字段，核心字段是与用户需求连接最紧密的字段，相关字段是与用户需求相关的其他字段，确保信息的完整性。
8. 请从如下给出的展示方式种选择最优的一种用以进行数据渲染，将类型名称放入返回要求格式的display_type参数值中，可用数据展示方式如下:
{
    "response_line_chart": "用于显示对比趋势分析数据",
    "response_pie_chart": "适用于比例和分布统计场景",
    "response_bar_chart": "适用于对比多个类别的数据大小、展示分类数据的分布和差异等"
}
请逐步思考生成并SQL代码，并按照以下JSON格式响应：
{
    "thoughts": "thoughts summary",
    "sql": "SQL Query to run",
    "key_fields":"fields most relevant to the query",
    "display_type":"data display method"
}
确保回答是正确的JSON格式，并且可以被Python的json.loads解析。
如下给出示例：
<few_shots>
"""

mategen_dict = {}
all_tables = {"fdc_ads":["ads_salesreport_subscranalyse_a_min","ads_salesreport_visitweekanalyse_a_min"],"fdc_dwd":["dwd_cust_custvisitflow_a_min","dwd_trade_roomreceivable_a_min","dwd_trade_roomsign_a_min","dwd_trade_roomsmsubscr_a_min","dwd_trade_roomsubscr_a_min"],"fdc_dws":["dws_proj_projplansum_a_h","dws_proj_room_totalsale_a_min"]}

print("Flask 启动！")


@app.route("/match", methods=["POST"])
def match():
        data = request.json
        query = data.get("query")
        indicator_name = test_match(query)
        if indicator_name:
            return jsonify({"response": indicator_name})
        else:
            return jsonify({"response": "未匹配上指标"})

@app.route("/close", methods=["POST"])
def close():
        data = request.json
        session_id = data.get("session_id")
        print("******************************")
        if session_id in mategen_dict:
            del mategen_dict[session_id]
            print(f"删除session_id:{session_id}")
            return jsonify({"response": "已删除该会话"})
        else:
            print(f"没有该会话session_id:{session_id}")
            return jsonify({"response": "不存在该会话"})
        
@app.route("/chat", methods=["POST"])
def chat():
    try:
        global mategen_dict
        data = request.json
        is_new = False
        print("打印data内容：")
        print(data)
        print("显示当前所有会话id：")
        for m in mategen_dict.keys():
            print(m)

        # 获取用户输入的query字段
        query = data.get("query")
        print("\n\n++++++++++++++++++++++++++++++")
        print(f"用户文本提问：{query}")
        # 获取当前会话id
        session_id = data.get("session_id")
        if session_id in mategen_dict:
            mategen = mategen_dict[session_id]
        else:
            is_new = True

        try:
            # 暂时使用从请求的dataSource字段中获取used_tables，后续实现根据session_id查华菁数据库获取used_tables信息
            chosen_tables = json.loads(data.get("dataSource"))
        except Exception as e:
            # 捕获其他可能的错误
            print(str(e))
            chosen_tables = None

        try:
            available_tables = json.loads(data.get("availableTables"))
        except Exception as e:
            print(str(e))
            available_tables = all_tables
 

        # 如果请求中会话id发生变化，则说明切换会话或开启新会话，需要重新加载历史会话
        if is_new:
            current_session_id = session_id
            # 根据session_id获取历史消息，查询华菁数据库nh_chat_history表中CONTENT字段，注意需要去除id的内容。若为空，则说明开启的是新会话，返回NULL
            session_messages = get_session_messages(current_session_id)
            # 根据session_id获取使用到的表，查询华菁数据库nh_chat_history表中DATA_SET_JSON字段获取
            if chosen_tables is None:
                chosen_tables = select_table_based_on_query(query)
            used_tables = dict_intersection(chosen_tables,available_tables)

            # 根据used_tables拼接获得数据字典
            data_dictionary_md = query_tables_description(used_tables)
            few_shots = query_few_shots(used_tables)

            mategen = MateGen(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                model="qwen2.5-72b-instruct",
                system_content_list=[system_prompt_common.replace("<few_shots>",few_shots)],
            )
            mategen_dict[session_id] = mategen

            # 更换messages对象对应的数据字典部分
            mategen.replace_data_dictionary(data_dictionary_md)

            # 加载历史会话记录
            mategen.add_session_messages(session_messages)

        # 调用chat函数，返回chat_dict，记录函数执行过程的返回值
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
            yield json.dumps(used_tables)

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


@app.route("/analysis", methods=["POST"])
def analysis():
    try:
        data = request.json
        saleropenid = data.get("saleropenid")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if not all([saleropenid, start_date, end_date]):
            return jsonify(
                {
                    "status": "error",
                    "response": "缺少必要的参数：saleropenid, start_date 或 end_date",
                }
            )

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
    app.run(threaded=True,host="0.0.0.0", port=45106)