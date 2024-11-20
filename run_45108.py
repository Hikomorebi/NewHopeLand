# python3
# -*- coding: utf-8 -*-
from flask import Flask, Response, request, jsonify
import os
import time
import traceback
from MateGen import MateGen
import json
# from generate_report import generate_json_report, query_customer_info
from utils import (
    default_converter,
    query_tables_description,
    query_few_shots,
    get_session_messages,
    test_match,
    dict_intersection,
    #read_csv_data,
    #get_project_ids_for_sales_manager,
    #query_subordinates,
    process_user_input,
    select_table_based_on_indicator,
)
from auto_select_tables import select_table_based_on_query

app = Flask(__name__)

# 设置环境变量（仅在当前脚本运行期间有效）
os.environ["OPENAI_API_KEY"] = "sk-94987a750c924ae19693c9a9d7ea78f7"

system_prompt_common = """
你是一名数据库专家，请根据用户的输入回答问题。
1. 首先，请仔细阅读并理解用户的请求，使用地产销售数据字典提供的表结构和各字段信息创建正确的 PostgreSQL 语句。
2. 只能使用提供的数据字典信息生成正确的 PostgreSQL 语句。请生成完整的、可执行的SQL语句，确保所有字段和条件都使用具体的值，禁止包含任何形式的占位符或模板变量，禁止随意假设不存在的信息。
3. 在生成SQL时，请注意不要混淆表与列之间的关系。确保选择的表和列与用户的请求相匹配。
4. 请确保SQL的正确性，包括语法、表名、列名以及日期格式等。同时，确保查询在正确条件下的性能优化。
5. 如果数据字典中存在 partitiondate 字段，请在生成SQL语句的筛选条件中加入 partitiondate = current_date 。
6. 如果用户请求的是一段时间内的数据，请确保SQL语句能够正确提取这段时间内的数据。如询问当日的数据，可以使用 current_date 作为筛选条件。如果问题涉及到今年或者本月，请自动理解为当前时间为2024年11月。
7. 生成的SQL语句不能涵盖非法字符如"\n"。
8. 生成的SQL语句选择的字段分为核心字段和相关字段，核心字段是与用户需求连接最紧密的字段，相关字段是与用户需求相关的其他字段，用于确保信息的完整性。请将核心字段放入返回要求格式的 key_fields 参数值中。
9. 若用户提问中涉及项目名称，请提取项目名称作为模糊匹配的筛选条件。项目名称可能包含城市名，应视为一个完整的字符串，不要拆分。如"成都皇冠湖壹号","温州立体城"可以通过"%皇冠湖壹号%"和"%立体城%"进行模糊匹配。
10. 请从如下给出的展示方式种选择最优的一种用以进行数据渲染，将类型名称放入返回要求格式的 display_type 参数值中，可用数据展示方式如下:
{
    "response_line_chart": "用于显示对比趋势分析数据",
    "response_pie_chart": "适用于比例和分布统计场景",
    "response_bar_chart": "适用于对比多个类别的数据大小、展示分类数据的分布和差异等"
}
请逐步思考生成并SQL代码，并按照以下JSON格式响应，
{
    "thoughts": "thoughts summary",
    "sql": "SQL Query to run",
    "key_fields":"fields most relevant to the query",
    "display_type":"data display method"
}
确保回答是正确的JSON格式，并且可以被Python的json.loads解析。要求只返回一个json对象，不要包含其余内容。
如下给出示例：
<few_shots>
"""
system_prompt_indicator_template = """
{indicator_name}是一个需要计算的指标，它的字段名为{indicator_field_name}，计算规则为:
{indicator_rule};
你是一名数据库专家，请根据计算规则生成正确的PostgreSQL语句。要求如下：
1. 请仔细阅读并理解用户的请求。参考数据库字典提供的表结构和各字段信息，根据计算规则生成正确的PostgreSQL语句。
2. 请完全按照提供的计算规则模板来设计SQL语句，不要修改计算规则的结构，同时如果计算规则中带有'$'符号作为占位符，需要从用户问题中提取相关的时间等信息来填充占位符。请确保所有占位符都被具体的值填充。
3. 请确保所有字段和条件都使用具体的值。禁止随意假设不存在的信息。请务必确保生成的SQL语句能够直接运行。
4. 如果数据字典中存在 partitiondate 字段，请在生成SQL语句的筛选条件中加入 partitiondate = current_date 。如果计算规则中存在 partitiondate 字段，则将该字段值筛选条件设为 current_date 。
5. 如果用户请求的是一段时间内的数据，请确保SQL语句能够正确提取这段时间内的数据。如询问当日的数据，可以使用 current_date 作为筛选条件。
6. 如果问题涉及到相对时间，如今年、当月，请按照当前时间为 2024 年 11 月份进行计算。
7. 若用户提问中涉及项目名称，请提取项目名称作为模糊匹配的筛选条件。项目名称可能包含城市名，应视为一个完整的字符串，不要拆分。如"成都皇冠湖壹号","温州立体城"可以通过"%皇冠湖壹号%"和"%立体城%"进行模糊匹配。
请严格按照计算规则的逻辑给出SQL代码，并按照以下JSON格式响应：
{{
    "sql": "SQL Query to run",
}}
要求只返回最终的json对象，不要包含其余内容。
"""

with open('SystemPrompts/subsignrate.txt', 'r', encoding='utf-8') as file:
    system_prompt_subsignrate = file.read()
with open('SystemPrompts/signrate.txt', 'r', encoding='utf-8') as file:
    system_prompt_signrate = file.read()
with open('SystemPrompts/subgap.txt', 'r', encoding='utf-8') as file:
    system_prompt_subgap = file.read()
with open('SystemPrompts/visitgroup.txt', 'r', encoding='utf-8') as file:
    system_prompt_visitgroup = file.read()

mategen_dict = {}
all_tables = {
    "fdc_ads": [
        "ads_salesreport_subscranalyse_a_min",
        "ads_salesreport_visitweekanalyse_a_min",
    ],
    "fdc_dwd": [
        "dwd_cust_custvisitflow_a_min",
        "dwd_trade_roomreceivable_a_min",
        "dwd_trade_roomsign_a_min",
        "dwd_trade_roomsmsubscr_a_min",
        "dwd_trade_roomsubscr_a_min",
    ],
    "fdc_dws": ["dws_proj_projplansum_a_h", "dws_proj_room_totalsale_a_min"],
}

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
        start_time = time.time()
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

        # 问题干预：status=1,preset_sql为sql语句
        # 指标管理：status=2,indicator_name为指标名,indicator_data为指标描述
        # 基础问数：status=3,user_question为用户问题
        process_user_input_dict = process_user_input(query)

        # 获取当前会话id
        session_id = data.get("session_id")
        if session_id in mategen_dict:
            mategen = mategen_dict[session_id]
        else:
            is_new = True
            try:
                # 暂时使用从请求的dataSource字段中获取used_tables，后续实现根据session_id查华菁数据库获取used_tables信息
                chosen_tables = json.loads(data.get("dataSource"))
                if isinstance(chosen_tables, list):
                    chosen_tables = None
            except Exception as e:
                # 捕获其他可能的错误
                print(str(e))
                chosen_tables = None

            try:
                available_tables = json.loads(data.get("availableTables"))
            except Exception as e:
                print(str(e))
                available_tables = all_tables

            current_session_id = session_id
            # 根据session_id获取历史消息，查询华菁数据库nh_chat_history表中CONTENT字段，注意需要去除id的内容。若为空，则说明开启的是新会话，返回NULL
            session_messages = get_session_messages(current_session_id)
            # 根据session_id获取使用到的表，查询华菁数据库nh_chat_history表中DATA_SET_JSON字段获取
            is_1_indicator = False
            if process_user_input_dict['status'] == 1 and process_user_input_dict["is_indicator"]:
                is_1_indicator = True
            if process_user_input_dict["status"] == 2 or is_1_indicator:
                print(
                    f"识别到指标问数，匹配到指标：{process_user_input_dict['indicator_name']}"
                )
                if process_user_input_dict["indicator_name"] in ["认签达成进度","认签比","认购缺口"]:
                    chosen_tables = {"fdc_dwd":["dwd_trade_roomsubscr_a_min"],"fdc_dws":["dws_proj_projplansum_a_h"]}
                elif process_user_input_dict["indicator_name"] in ["签约达成率","签约完成率"]:
                    chosen_tables = {"fdc_dwd":["dwd_trade_roomsign_a_min"],"fdc_dws":["dws_proj_projplansum_a_h"]}
                elif process_user_input_dict["indicator_name"] == "来访组数":
                    chosen_tables = {"fdc_dwd":"dwd_cust_custvisitflow_a_min"}
                else:
                    chosen_tables = select_table_based_on_indicator(
                        process_user_input_dict["indicator_data"]["数据来源"]
                    )
                print(f"选择的表是：{chosen_tables}")
            if chosen_tables is None:
                chosen_tables = select_table_based_on_query(query)
                print(f"选择的表是：{chosen_tables}")
            used_tables = dict_intersection(chosen_tables, available_tables)

            # 根据used_tables拼接获得数据字典
            data_dictionary_md = query_tables_description(used_tables)

            if process_user_input_dict["status"] == 2 or is_1_indicator:
                indicator_data = process_user_input_dict["indicator_data"]
                indicator_name = process_user_input_dict["indicator_name"]

                if indicator_name == "认签比":
                    mategen = MateGen(
                        api_key=os.getenv("OPENAI_API_KEY"),
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                        model="qwen-plus",
                        system_content_list=[system_prompt_subsignrate],
                    )
                elif indicator_name == "签约完成率" or indicator_name == "签约达成率":
                    mategen = MateGen(
                        api_key=os.getenv("OPENAI_API_KEY"),
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                        model="qwen-plus",
                        system_content_list=[system_prompt_signrate],
                    )
                elif indicator_name == "认购缺口":
                    mategen = MateGen(
                        api_key=os.getenv("OPENAI_API_KEY"),
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                        model="qwen-plus",
                        system_content_list=[system_prompt_subgap],
                    )
                elif indicator_name == "来访组数":
                    mategen = MateGen(
                        api_key=os.getenv("OPENAI_API_KEY"),
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                        model="qwen-plus",
                        system_content_list=[system_prompt_visitgroup],
                    )
                else:
                    system_prompt_indicator = system_prompt_indicator_template.format(
                        indicator_name=indicator_name,
                        indicator_field_name=indicator_data["指标字段名"],
                        indicator_rule=indicator_data["计算规则"],
                    )
                    mategen = MateGen(
                        api_key=os.getenv("OPENAI_API_KEY"),
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                        model="qwen-plus",
                        system_content_list=[system_prompt_indicator],
                    )
            else:
                few_shots = query_few_shots(used_tables)

                mategen = MateGen(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    model="qwen-plus",
                    system_content_list=[
                        system_prompt_common.replace("<few_shots>", few_shots)
                    ],
                )
            mategen_dict[session_id] = mategen

            # 更换messages对象对应的数据字典部分
            mategen.replace_data_dictionary(data_dictionary_md)

            # 加载历史会话记录
            mategen.add_session_messages(session_messages)

        # 调用chat函数，返回chat_dict，记录函数执行过程的返回值
        before_chat_time = time.time()
        elapsed_time = before_chat_time - start_time

        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(f"第一阶段：对话准备（数据表选择）耗时: {elapsed_time:.4f} 秒")

        chat_dict = mategen.chat(query, process_user_input_dict)

        chat_dict["time"] = f"\n第一阶段：对话准备（数据表选择）耗时: {elapsed_time:.4f} 秒" + chat_dict["time"]
        if "chosen_tables" not in chat_dict:
            if is_new:
                chat_dict["chosen_tables"] = chosen_tables
            else:
                chat_dict["chosen_tables"] = {
                    "error": "多轮对话不展示chosen_tables信息"
                }

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
            # yield json.dumps(used_tables)

            for data in stream:
                json_data = json.loads(data)
                print(json_data)
                if "content" in json_data:
                    current_conversation.append(json_data["content"])
                    yield json.dumps(json_data) + "\n"
            final_response = "".join(current_conversation)
            mategen.messages.messages_append(
                {"role": "assistant", "content": final_response}
            )
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            print(final_response)
            finish_info = {
                "sql_code": chat_dict["sql_code"],
                "sql_response": chat_dict["sql_results_json"],
                "chosen_tables": chat_dict["chosen_tables"],
                "time": chat_dict["time"],
            }
            yield json.dumps(finish_info, default=default_converter)

        end_time = time.time()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(f"总共耗时: {end_time-start_time:.4f} 秒")
        if chat_dict["status"] != 3:
            return Response(generate_012(chat_dict), content_type="text/event-stream")
        else:
            return Response(generate_3(chat_dict), content_type="text/event-stream")

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "response": str(e)})


# @app.route("/analysis", methods=["POST"])
# def analysis():
#     try:
#         data = request.json
#         saleropenid = data.get("saler_id")
#         role_name = data.get("role_name")
#         if not all([saleropenid, role_name]):
#             return jsonify(
#                 {
#                     "status": "error",
#                     "response": "缺少必要的参数: saler_id 或 role_name",
#                 }
#             )

#         # 读取当天的销售人员信息
#         # 后续可能要改成数据库的读取形式
#         role_data = read_csv_data("role.csv")

#         # 如果是销售主管，查询所有下属的置业顾问的顾客信息
#         if role_name == "销售主管":
#             project_ids = get_project_ids_for_sales_manager(saleropenid, role_data)
#             subordinate_ids = query_subordinates(project_ids, role_data)
#             customer_data = []
#             for sub_id in subordinate_ids:
#                 customers = query_customer_info(sub_id)
#                 customer_data.extend(customers)
#         # 如果是置业顾问，只查询自己的顾客信息
#         else:
#             customer_data = query_customer_info(saleropenid)

#         if not customer_data:
#             return jsonify({"status": "error", "response": "未查询到相关客户信息。"})

#         json_report = generate_json_report(customer_data)

#         report_filename = f"高意向客户分析报告_{saleropenid}.json"
#         with open(report_filename, "w", encoding="utf-8") as file:
#             # 美化输出JSON
#             json.dump(json_report, file, ensure_ascii=False, indent=4)

#         print(f"报告已生成并保存在 {report_filename}")

#         return jsonify({"status": "success", "response": json_report})

#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"status": "error", "response": str(e)})


if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=45108)
