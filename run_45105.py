# python3
# -*- coding: utf-8 -*-
from flask import Flask, Response, request, jsonify
import time
import traceback
from MateGen import MateGen
import json
from utils import (
    default_converter,
    query_tables_description,
    query_few_shots,
    dict_intersection,
    process_user_input,
    select_table_based_on_indicator,
)
from auto_select_tables import select_table_based_on_query

app = Flask(__name__)

OPENAI_API_KEY = "sk-46632b8571664330b45695ba5256c30e"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"

with open("indicator_prompt.json", "r", encoding="utf-8") as file:
    indicator_prompt_dict = json.load(file)

system_prompt_common = """
你是一名数据库专家，请根据用户的输入回答问题。
1. 请仔细阅读并理解用户的请求，使用地产销售数据字典提供的信息创建正确的 PostgreSQL 语句。
2. 只能使用提供的数据字典信息生成正确的 PostgreSQL 语句。请生成完整的、可执行的SQL语句，确保所有字段和条件都使用具体的值，禁止包含任何形式的占位符或模板变量，禁止随意假设不存在的信息。
3. 在生成SQL时，请注意不要混淆表与列之间的关系。确保选择的表和列与用户的请求相匹配。
4. 请确保SQL的正确性，包括语法、表名、列名以及日期格式等。同时，确保查询在正确条件下的性能优化。
5. 如果用户请求的是一段时间内的数据，请确保SQL语句能够正确提取这段时间内的数据。若询问相对时间如当日、本周、本月、昨日、上周、上月的数据，可以使用 current_date 结合 date_trunc 作为筛选条件。如果问题涉及具体月份，请自动理解为当前时间为2024年12月。
6. 生成的SQL语句不能涵盖非法字符如"\n"。
7. 生成的SQL语句选择的字段分为核心字段和相关字段，核心字段是与用户需求连接最紧密的字段，相关字段是与用户需求相关的其他字段，用于确保信息的完整性。请将核心字段放入返回要求格式的 key_fields 参数值中。
8. 请从如下给出的展示方式种选择最优的一种用以进行数据渲染，将类型名称放入返回要求格式的 display_type 参数值中，可用数据展示方式如下:
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
2. 请完全按照提供的计算规则模板来设计SQL语句，可以根据问题增加具体的筛选条件，但不要修改计算规则的逻辑。如果计算规则中带有'$'符号作为占位符，需要从用户问题中提取相关的时间等信息来填充占位符。请确保所有占位符都被具体的值填充。
3. 请确保所有字段和条件都使用具体的值。禁止随意假设不存在的信息。请务必确保生成的SQL语句能够直接运行。
4. 如果计算规则中存在 partitiondate 字段，则将该字段值筛选条件设为 current_date 。
5. 如果用户请求的是一段时间内的数据，请确保SQL语句能够正确提取这段时间内的数据。若询问相对时间如当日、本周、本月、昨日、上周、上月的数据，可以使用 current_date 结合 date_trunc 作为筛选条件。如果问题涉及具体月份，请自动理解为当前时间为2024年12月。
请严格按照计算规则的逻辑给出SQL代码，并按照以下JSON格式响应：
{{
    "sql": "SQL Query to run",
}}
要求只返回最终的json对象，不要包含其余内容。
"""


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


@app.route("/close", methods=["POST"])
def close():
    data = request.json
    session_id = data.get("session_id")
    print("******************************")
    if session_id in mategen_dict:
        del mategen_dict[session_id]
        print(f"已删除session_id:{session_id}")
        print("******************************")
        return jsonify({"response": "已删除该会话"})
    else:
        print(f"没有该会话session_id:{session_id}")
        print("******************************")
        return jsonify({"response": "不存在该会话"})


@app.route("/chat", methods=["POST"])
def chat():
    try:
        start_time = time.time()
        global mategen_dict
        data = request.json

        print("显示当前所有会话id：")
        for m in mategen_dict.keys():
            print(m)

        print("打印data内容：")
        print(data)

        # 获取用户输入的query字段
        query = data.get("query")
        print("\n\n++++++++++++++++++++++++++++++")
        print(f"用户文本提问：{query}")

        # 问题干预：status=1,preset_sql为sql语句，is_indicator指示是否为指标问数
        # 指标管理：status=2,indicator_name为指标名,indicator_data为指标描述
        # 基础问数：status=3,user_question为用户问题，indicator_name为base
        # "indicator_name = 'base'"表示基础问数
        process_user_input_dict = process_user_input(query)

        # 获取当前会话id
        session_id = data.get("session_id")
        is_new = True
        # 同时满足如下条件下不单开对话，1、session_id已存在 2、【基础问数,新指标，旧指标】中不是新指标 3、count小于等于5
        if session_id in mategen_dict:
            mategen = mategen_dict[session_id]
            if (
                process_user_input_dict.get("indicator_name", None)
                in [mategen.current_indicator, "base"]
                and mategen.current_count <= 10
            ):
                is_new = False
                mategen.current_count += 1
            else:
                del mategen_dict[session_id]
                is_new = True

        if is_new:
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

            # 根据session_id获取历史消息，查询华菁数据库nh_chat_history表中CONTENT字段，注意需要去除id的内容。若为空，则说明开启的是新会话，返回NULL
            # session_messages = get_session_messages(current_session_id)
            session_messages = []
            # 根据session_id获取使用到的表，查询华菁数据库nh_chat_history表中DATA_SET_JSON字段获取

            if process_user_input_dict["indicator_name"] != "base":
                print(
                    f"识别到指标问数，匹配到指标：{process_user_input_dict['indicator_name']}"
                )
                indicator_name = process_user_input_dict["indicator_name"]
                if indicator_name in indicator_prompt_dict:
                    print("特殊指标！")
                    chosen_tables = indicator_prompt_dict[indicator_name][
                        "chosen_tables"
                    ]
                else:
                    chosen_tables = select_table_based_on_indicator(
                        process_user_input_dict["indicator_data"]["数据来源"],
                        process_user_input_dict["indicator_data"]["数据来源表"],
                    )
                print(f"选择的表是：{chosen_tables}")
            if chosen_tables is None:
                chosen_tables = select_table_based_on_query(query)
                print(f"选择的表是：{chosen_tables}")
            used_tables = dict_intersection(chosen_tables, available_tables)

            # 根据used_tables拼接获得数据字典
            data_dictionary_md = query_tables_description(used_tables)

            if process_user_input_dict["indicator_name"] != "base":
                indicator_data = process_user_input_dict["indicator_data"]
                indicator_name = process_user_input_dict["indicator_name"]

                if indicator_name in indicator_prompt_dict:
                    with open(
                        indicator_prompt_dict[indicator_name]["prompt"],
                        "r",
                        encoding="utf-8",
                    ) as file:
                        special_indicator_prompt = file.read()
                    mategen = MateGen(
                        api_key=OPENAI_API_KEY,
                        base_url=BASE_URL,
                        model=MODEL_NAME,
                        system_content_list=[special_indicator_prompt],
                        current_indicator=indicator_name,
                    )
                else:
                    system_prompt_indicator = system_prompt_indicator_template.format(
                        indicator_name=indicator_name,
                        indicator_field_name=indicator_data["指标字段名"],
                        indicator_rule=indicator_data["计算规则"],
                    )
                    mategen = MateGen(
                        api_key=OPENAI_API_KEY,
                        base_url=BASE_URL,
                        model=MODEL_NAME,
                        system_content_list=[system_prompt_indicator],
                        current_indicator=indicator_name,
                    )
            else:
                few_shots = query_few_shots(used_tables)

                mategen = MateGen(
                    api_key=OPENAI_API_KEY,
                    base_url=BASE_URL,
                    model=MODEL_NAME,
                    system_content_list=[
                        system_prompt_common.replace("<few_shots>", few_shots)
                    ],
                    current_indicator="base",
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

        # chat函数
        chat_dict = mategen.chat(process_user_input_dict)

        chat_dict["time"] = (
            f"\n第一阶段：对话准备（数据表选择）耗时: {elapsed_time:.4f} 秒"
            + chat_dict["time"]
        )
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
                "column_names": chat_dict["column_names"],
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

if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=45105)
