import psycopg2
import pymysql
import os
import pandas as pd
import json
from datetime import date
import re
import traceback
from decimal import Decimal, ROUND_HALF_UP
from openai import OpenAI

# 设置环境变量（仅在当前脚本运行期间有效）
os.environ["OPENAI_API_KEY"] = "sk-94987a750c924ae19693c9a9d7ea78f7"

with open("en2ch.json", "r", encoding="utf-8") as file:
    en2zh_json = json.load(file)


def default_converter(o):
    if isinstance(o, date):
        return o.strftime("%Y-%m-%d")
    if isinstance(o, Decimal):
        return str(o)


def format_decimal_value(value):
    if not isinstance(value, Decimal):
        return value
    if value.is_zero():
        return 0

    # 对于其他数值，保留两位小数并四舍五入
    # 使用 ROUND_HALF_UP 来确保正确的舍入
    formatted_value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # 如果结果是整数，例如 1689.00，转换为整数形式
    if formatted_value == formatted_value.to_integral_value():
        return int(formatted_value)

    # 返回字符串形式的保留两位小数的数值
    return float(formatted_value)


def get_sql_results_json(column_names, results):
    if results == []:
        return []
    sql_results_json = []
    data = []
    data_dict = {}

    columns_data = {col: [] for col in column_names}
    for row in results:
        for col_name, value in zip(column_names, row):
            columns_data[col_name].append(format_decimal_value(value))

    main_dict = {}
    titles = []
    main_name = None
    main_en_name = None
    count_other = 0
    # 遍历返回的所有字段
    for en_name in column_names:
        # 如果该字段为数据库中字段且其为非数值型，设置其为主字段
        if en_name in en2zh_json.keys() and en2zh_json[en_name][1] == 0:
            count_other += 1
            main_en_name = en_name
            if count_other >= 2:
                break

    if count_other == 1:
        main_name = en2zh_json[main_en_name][0]
        main_dict[main_name] = columns_data[main_en_name]
        column_names.remove(main_en_name)
    # 0代表没有非数值字段 1代表有唯一非数值字段 2代表有多个非数值字段
    for en_name in column_names:
        if en_name not in en2zh_json.keys():
            main_dict[en_name] = columns_data[en_name]
            titles.append(en_name)
        elif en2zh_json[en_name][1] == 0:
            main_dict[en2zh_json[en_name][0]] = columns_data[en_name]
            titles.append(en2zh_json[en_name][0])
        elif en2zh_json[en_name][1] == 1:
            main_dict[en2zh_json[en_name][0]] = columns_data[en_name]
            titles.append(en2zh_json[en_name][0])

    data_dict["title"] = titles

    data_dict["x"] = main_dict[main_name] if count_other == 1 else []
    data_dict["y"] = []
    for key in titles:
        data_dict["y"].append({"name": key, "data": main_dict[key]})
    data.append(data_dict)

    sql_results_json.append({"name": main_name, "data": data})

    return sql_results_json


def add_task_decomposition_prompt(messages):
    # 任务拆解Few-shot
    # 第一个提示示例
    user_question1 = "请问谷歌云邮箱是什么？"
    user_message1_content = (
        "现有用户问题如下：“%s”。为了回答这个问题，总共需要分几步来执行呢？\
    若无需拆分执行步骤，请直接回答原始问题。"
        % user_question1
    )
    assistant_message1_content = (
        "谷歌云邮箱是指Google Workspace（原G Suite）中的Gmail服务，\
    它是一个安全、智能、易用的电子邮箱，有15GB的免费存储空间，可以直接在电子邮件中接收和存储邮件。\
    Gmail 邮箱会自动过滤垃圾邮件和病毒邮件，并且可以通过电脑或手机等移动设备在任何地方查阅邮件。\
    您可以使用搜索和标签功能来组织邮件，使邮件处理更为高效。"
    )

    # 第二个提示示例
    user_question2 = "请帮我介绍下OpenAI。"
    user_message2_content = (
        "现有用户问题如下：“%s”。为了回答这个问题，总共需要分几步来执行呢？\
    若无需拆分执行步骤，请直接回答原始问题。"
        % user_question2
    )
    assistant_message2_content = "OpenAI是一家开发和应用友好人工智能的公司，\
    它的目标是确保人工通用智能（AGI）对所有人都有益，以及随着AGI部署，尽可能多的人都能受益。\
    OpenAI致力在商业利益和人类福祉之间做出正确的平衡，本质上是一家人道主义公司。\
    OpenAI开发了诸如GPT-3这样的先进模型，在自然语言处理等诸多领域表现出色。"

    # 第三个提示示例
    user_question3 = "围绕数据库中的user_payments表，我想要检查该表是否存在缺失值"
    user_message3_content = (
        "现有用户问题如下：“%s”。为了回答这个问题，总共需要分几步来执行呢？\
    若无需拆分执行步骤，请直接回答原始问题。"
        % user_question3
    )
    assistant_message3_content = (
        "为了检查user_payments数据集是否存在缺失值，我们将执行如下步骤：\
    \n\n步骤1：使用`extract_data`函数将user_payments数据表读取到当前的Python环境中。\
    \n\n步骤2：使用`python_inter`函数执行Python代码检查数据集的缺失值。"
    )

    # 第四个提示示例
    user_question4 = (
        "我想寻找合适的缺失值填补方法，来填补user_payments数据集中的缺失值。"
    )
    user_message4_content = (
        "现有用户问题如下：“%s”。为了回答这个问题，总共需要分几步来执行呢？\
    若无需拆分执行步骤，请直接回答原始问题。"
        % user_question4
    )
    assistant_message4_content = "为了找到合适的缺失值填充方法，我们需要执行以下三步：\
    \n\n步骤1：分析user_payments数据集中的缺失值情况。通过查看各字段的缺失率和观察缺失值分布，了解其缺失幅度和模式。\
    \n\n步骤2：确定值填补策略。基于观察结果和特定字段的性质确定恰当的填补策略，例如使用众数、中位数、均值或建立模型进行填补等。\
    \n\n步骤3：进行缺失值填补。根据确定的填补策略，执行填补操作，然后验证填补效果。"

    # 在保留原始问题的情况下加入Few-shot
    task_decomp_few_shot = messages.copy()
    task_decomp_few_shot.messages_pop(manual=True, index=-1)
    task_decomp_few_shot.messages_append(
        {"role": "user", "content": user_message1_content}
    )
    task_decomp_few_shot.messages_append(
        {"role": "assistant", "content": assistant_message1_content}
    )
    task_decomp_few_shot.messages_append(
        {"role": "user", "content": user_message2_content}
    )
    task_decomp_few_shot.messages_append(
        {"role": "assistant", "content": assistant_message2_content}
    )
    task_decomp_few_shot.messages_append(
        {"role": "user", "content": user_message3_content}
    )
    task_decomp_few_shot.messages_append(
        {"role": "assistant", "content": assistant_message3_content}
    )
    task_decomp_few_shot.messages_append(
        {"role": "user", "content": user_message4_content}
    )
    task_decomp_few_shot.messages_append(
        {"role": "assistant", "content": assistant_message4_content}
    )

    user_question = messages.history_messages[-1]["content"]

    new_question = (
        "现有用户问题如下：“%s”。为了回答这个问题，总共需要分几步来执行呢？\
    若无需拆分执行步骤，请直接回答原始问题。"
        % user_question
    )
    question_message = messages.history_messages[-1].copy()
    question_message["content"] = new_question
    task_decomp_few_shot.messages_append(question_message)

    return task_decomp_few_shot


def modify_prompt(messages, action="add", enable_md_output=True, enable_COT=True):
    # 思考链提示词模板
    cot_prompt = "请一步步思考并得出结论。"

    # 输出markdown提示词模板
    md_prompt = "任何回答都请以markdown格式进行输出。"

    # 如果是添加提示词
    if action == "add":
        if enable_COT:
            messages.messages[-1]["content"] += cot_prompt
            messages.history_messages[-1]["content"] += cot_prompt

        if enable_md_output:
            messages.messages[-1]["content"] += md_prompt
            messages.history_messages[-1]["content"] += md_prompt

    # 如果是将指定提示词删除
    elif action == "remove":
        if enable_md_output:
            messages.messages[-1]["content"] = messages.messages[-1]["content"].replace(
                md_prompt, ""
            )
            messages.history_messages[-1]["content"] = messages.history_messages[-1][
                "content"
            ].replace(md_prompt, "")

        if enable_COT:
            messages.messages[-1]["content"] = messages.messages[-1]["content"].replace(
                cot_prompt, ""
            )
            messages.history_messages[-1]["content"] = messages.history_messages[-1][
                "content"
            ].replace(cot_prompt, "")

    return messages


def is_chinese(string):
    # 匹配中文字符的正则表达式
    chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
    # 检查字符串中是否有中文字符
    return bool(chinese_pattern.search(string))


def extract_json_from_response(response_text):
    """
    从模型的回答文本中提取JSON对象。

    参数:
        response_text (str): 模型的回答文本

    返回:
        dict: 提取出的JSON对象，如果未找到有效的JSON则返回None
    """
    # 使用正则表达式找到JSON块
    json_pattern = re.search(r"\{.*?\}", response_text, re.DOTALL)

    if json_pattern:
        try:
            # 提取并解析JSON字符串
            json_str = json_pattern.group(0)

            # 清理换行和多余空格
            json_str = json_str.replace("\n", "").replace(" ", "")

            # 解析JSON字符串
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("无法解析JSON")
            return None
    else:
        print("未找到JSON对象")
        return None


def get_translate_column_names(column_names):
    need_translate_list = []
    for column in column_names:
        if column not in en2zh_json.keys() and not is_chinese(column):
            need_translate_list.append(column)
    if need_translate_list == []:
        return column_names

    prompt_template = """
    请帮我将以下变量名从英文翻译为简洁的中文变量名。变量名会以Python列表的形式提供，如：['avg_daily_outbound', 'days_to_deplete']。请注意，翻译时应尽可能保持变量名原有的语义，并以简洁准确的中文形式表示。结果应以JSON格式返回，其中英文变量名作为键，中文翻译作为值。例如：
    输入：['avg_daily_outbound', 'days_to_deplete']
    输出：{
    "avg_daily_outbound": "日均出库量",
    "days_to_deplete": "耗尽天数"
    }

    以下是需要翻译的变量列表：
    <input>
    """
    final_prompt = prompt_template.replace("<input>", str(need_translate_list))
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    response = client.chat.completions.create(
        model="qwen2.5-72b-instruct",
        messages=[{"role": "user", "content": final_prompt}],
    )
    temp_dict = extract_json_from_response(response.choices[0].message.content)

    translate_column_names = []
    for column in column_names:
        if column not in en2zh_json.keys() and not is_chinese(column):
            translate_column_names.append(temp_dict[column])
        else:
            translate_column_names.append(column)
    return translate_column_names


# 连接到Navicat(Mysql)数据库
def connect_to_db():
    conn = pymysql.connect(
        host="8.137.93.112",
        port=3306,
        user="new_hope",
        password="nA48AAse3kCpChnh",
        db="new_hope_estate_db",
    )
    cur = conn.cursor()
    return conn, cur


# 查询干预问题
def get_intervention_sql(cursor, user_question):
    query = """  
    SELECT select_sql  
    FROM nh_problem_meddle  
    WHERE question_name = %s AND enabled = 'ENABLE' AND DELETE_FLAG = 'NOT_DELETE'  
    LIMIT 1  
    """
    cursor.execute(query, (user_question,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_indicator_names(cursor):
    query = "SELECT `NAME` FROM NH_INDICATOR_MANAGEMENT"
    cursor.execute(query)
    result = cursor.fetchall()
    indicator_names = [row[0] for row in result if row[0] is not None]
    return indicator_names
def get_indicator_data(cursor,indicator_name):
    query = "SELECT NAME,FIELD_NAME,CALCULATION_RULES,DATA_TABLE_NAME FROM NH_INDICATOR_MANAGEMENT WHERE `NAME` = %s"
    cursor.execute(query, (indicator_name,))
    result = cursor.fetchone()
    if result:
        columns = ["指标名","指标字段名","计算规则","数据来源"]
        result_dict = dict(zip(columns, result))
        #result_json = json.dumps(result_dict, ensure_ascii=False, indent=4, default=default_converter)
        return result_dict


def match_indicator(query, indicator_names):
    # 按照长度从大到小排序
    indicator_names.sort(key=len, reverse=True)
    
    # 遍历指标列表，找到第一个匹配的指标
    for indicator in indicator_names:
        if indicator in query:
            return indicator  # 返回匹配到的指标名称
    
    return None  # 如果没有匹配到，则返回None
# 匹配基础指标并使用大模型进行逻辑判断
# def match_indicators(user_question):
#     # 从文件中读取基础指标信息
#     with open("indicators.json", "r", encoding="utf-8") as file:
#         data = json.load(file)
#         basis_indicators = data["basis_indicators"]

#     # 设计提示
#     basis_indicators_str = "\n".join(
#         [f"- {indicator['indicator_name']}" for indicator in basis_indicators]
#     )
#     prompt = (
#         f"请从以下基础指标中提取出用户问题中提到的指标：\n"
#         f"{basis_indicators_str}\n"
#         f"用户问题是：'{user_question}'\n"
#         f"请返回匹配到的基础指标名称的列表，以逗号分隔。"
#     )

#     # 创建 OpenAI 客户端
#     client = OpenAI(
#         api_key=os.getenv("OPENAI_API_KEY"),
#         base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
#     )
#     model = "qwen2.5-72b-instruct"

#     # 调用大模型
#     response = client.chat.completions.create(
#         model=model, messages=[{"role": "user", "content": prompt}]
#     )

#     # 解析响应并处理可能的格式问题
#     matched_indicators = response.choices[0].message.content.strip()
#     if matched_indicators:
#         matched_indicators_list = [
#             indicator.strip() for indicator in matched_indicators.split(",")
#         ]
#     else:
#         matched_indicators_list = []

#     # 从基础指标中找到与模型输出匹配的指标
#     final_matched_indicators = [
#         indicator
#         for indicator in basis_indicators
#         if indicator["indicator_name"] in matched_indicators_list
#     ]

#     return final_matched_indicators


# 查询同义词
def get_synonyms(cursor):
    query = """  
    SELECT TERM, EXPLANATION  
    FROM nh_synonym_explanation 
    WHERE ENABLED = 'ENABLE' AND DELETE_FLAG = 'NOT_DELETE'
    """
    cursor.execute(query)
    return {row[0]: row[1] for row in cursor.fetchall()}


# 替换同义词
def replace_synonyms(text, synonyms):
    pattern = re.compile(r"(" + "|".join(map(re.escape, synonyms.keys())) + r")")
    return pattern.sub(lambda match: synonyms[match.group(0)], text)


def process_user_input(user_question):
    # status=1表示问题干预成功
    process_user_input_dict = {}
    # 连接到Navicat(Mysql)数据库
    conn, cursor = connect_to_db()

    # 查询同义词
    synonyms = get_synonyms(cursor)  # 这里获取同义词字典

    # 查询干预问题对应的SQL语句
    preset_sql = get_intervention_sql(cursor, user_question)

    if preset_sql:
        # 如果找到干预问题，返回预设的SQL语句
        print(f"Intervention found: {preset_sql}")

        # 关闭数据库连接
        cursor.close()
        conn.close()
        process_user_input_dict["status"] = 1
        process_user_input_dict["preset_sql"] = preset_sql
        return process_user_input_dict
    else:
        # 如果没有找到干预问题，进行指标匹配
        indicator_names = get_indicator_names(cursor)
        indicator_name = match_indicator(user_question,indicator_names)
        

        if indicator_name:
            # 如果找到匹配的指标，返回匹配的指标
            # 关闭数据库连接
            indicator_data = get_indicator_data(cursor,indicator_name)
            cursor.close()
            conn.close()
            process_user_input_dict["status"] = 2
            process_user_input_dict["indicator_name"] = indicator_name
            process_user_input_dict["indicator_data"] = indicator_data
            return process_user_input_dict
        else:
            # 如果没有找到匹配的指标，进行同义词替换
            modified_question = replace_synonyms(
                user_question, synonyms
            )  # 传入同义词字典
            print(f"Modified question for model: {modified_question}")
            # 关闭数据库连接
            cursor.close()
            conn.close()
            process_user_input_dict["status"] = 3
            process_user_input_dict["modified_question"] = modified_question
            return process_user_input_dict


def sql_exec(sql_query):
    # 结果返回字典，status=0表示成功返回
    return_dict = {"status": 0}

    postgres_pw = os.getenv("SQL_PW")

    connection = psycopg2.connect(
        host="localhost",  # 数据库地址
        user="postgres",  # 数据库用户名
        password=postgres_pw,  # 数据库密码
        dbname="nuogaomei",  # 数据库名
        options="-c client_encoding=utf8",  # 设置字符集编码为utf8
    )

    try:
        with connection.cursor() as cursor:
            # SQL查询语句
            sql = sql_query
            cursor.execute(sql)

            # 获取查询结果
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            my_df = pd.read_sql(sql_query, connection)
            my_df.to_csv("data.csv", index=False)

            if len(results) > 100:
                return_dict["is_long"] = True
                # sql_results = json.dumps(results[:50], ensure_ascii=False, default=default_converter)
            else:
                return_dict["is_long"] = False
                sql_results = json.dumps(
                    results, ensure_ascii=False, default=default_converter
                )
                return_dict["sql_results"] = sql_results
            translate_column_names = get_translate_column_names(column_names)
            sql_results_json = get_sql_results_json(translate_column_names, results)
            return_dict["status"] = 1
            return_dict["sql_results_json"] = sql_results_json

    except Exception as e:
        traceback.print_exc()
        return_dict["status"] = 0

        error_message = str(e)
        return_dict["error_message"] = error_message
        # 获取报错信息

        print(f"SQL 执行报错: {error_message}")
    finally:
        connection.close()

    return return_dict


def dws_connect(sql_query):
    dws_connect_dict = {}
    connection = psycopg2.connect(
        dbname="fdc_dc",
        user="dws_user_hwai",
        password="NewHope#1982@",
        host="124.70.57.67",
        port="8000",
    )
    connection.set_client_encoding('UTF8')
    print("连接成功")

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)

            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            # my_df = pd.read_sql(sql_query, connection)
            # my_df.to_csv("data.csv", index=False)

            if len(results) > 100:
                dws_connect_dict["is_long"] = True
                # sql_results = json.dumps(results[:50], ensure_ascii=False, default=default_converter)
            else:
                dws_connect_dict["is_long"] = False
                sql_results = json.dumps(
                    results, ensure_ascii=False, default=default_converter
                )
                dws_connect_dict["sql_results"] = sql_results
            translate_column_names = get_translate_column_names(column_names)
            sql_results_json = get_sql_results_json(translate_column_names, results)
            dws_connect_dict["status"] = 1
            dws_connect_dict["sql_results_json"] = sql_results_json
    except Exception as e:
        traceback.print_exc()
        dws_connect_dict["status"] = 0

        error_message = str(e)
        dws_connect_dict["error_message"] = error_message
        # 获取报错信息

        print(f"SQL 执行报错: {error_message}")
    finally:
        connection.close()

    return dws_connect_dict


def extract_json_fields(input_string):
    # Use regex to find JSON part in the input string
    json_match = re.search(r"{.*?}", input_string, re.DOTALL)

    if json_match:
        json_str = json_match.group()
        try:
            # Parse the JSON string
            json_data = json.loads(json_str)
            # Extract the required fields
            sql = json_data.get("sql", "")
            thoughts = json_data.get("thoughts", "")
            return sql, thoughts
        except json.JSONDecodeError:
            return None, None
    return None, None


def query_tables_description(database_dir_mapping):
    """
    根据传入的数据库和表名字典，拼接相应表的描述文件内容
    :param database_dir_mapping: 字典，键为数据库名，值为表名列表
    :return: 拼接的描述文件内容
    """
    result = []

    for db_name, tables in database_dir_mapping.items():
        db_dir = os.path.join("Description", db_name)  # 假设目录名就是数据库名
        for table in tables:
            table_file = os.path.join(db_dir, f"{table}.md")  # 表名加上md后缀构成文件名
            try:
                with open(table_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    result.append(f"--- {db_name}.{table} ---\n{content}\n")
            except FileNotFoundError:
                print(f"表 {table} 在数据库 {db_name} 中找不到描述文件 {table_file}")
            except Exception as e:
                print(f"读取文件 {table_file} 时发生错误: {e}")

    return "".join(result)


def get_used_tables(current_session_id):
    # TODO
    # 连接数据库通过sql语句获取涉及到的表，返回dict

    example_return_data = {
        "fdc_dwd": ["dwd_trade_roomsign_a_min"],
        "fdc_dws": ["dws_proj_room_totalsale_a_min", "dws_proj_projplansum_a_h"],
    }
    return example_return_data


def get_session_messages(current_session_id):
    # TODO
    # 连接数据库通过sql语句获取该会话历史信息，返回list

    example_return_data = [{"role":"user","content":"你好"},{"role":"assistant","content":"你好，我是人工智能助手。"}] 
    
    return example_return_data


if __name__ == "__main__":
    # sql_exec("SELECT SUM(main_quantity + secondary_quantity) AS total_outbound_quantity FROM sales_outbound WHERE product_code = '040203003037';")
    sql_exec(
        "WITH sales_rate AS (SELECT product_code, AVG(main_quantity) AS average_sales FROM sales_order GROUP BY product_code), inventory_data AS (SELECT material_code, material_name, stock_quantity FROM inventory) SELECT i.material_name, i.stock_quantity, s.average_sales, i.stock_quantity / s.average_sales AS 库存消耗天数 FROM inventory_data i JOIN sales_rate s ON i.material_code = s.product_code WHERE s.average_sales > 0 ORDER BY 库存消耗天数 ASC LIMIT 5;"
    )
    # sql_exec("SELECT * FROM sales_outbound WHERE salesperson_name = '胡丹';")
