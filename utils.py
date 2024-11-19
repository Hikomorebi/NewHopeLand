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
import Levenshtein  # 使用 Levenshtein 库来计算字符串距离
import time
import csv

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
    formatted_value = value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    # 如果结果是整数，例如 1689.00，转换为整数形式
    if formatted_value == formatted_value.to_integral_value():
        return int(formatted_value)

    return float(formatted_value)


def get_sql_results_json(translated_column_names, type_codes, results, sql_query, results_length, positions, display_type):
    response_data = {col: [] for col in translated_column_names}
    for row in results:
        for col_name, value in zip(translated_column_names, row):
            response_data[col_name].append(format_decimal_value(value))

    response_columns = []
    for i in range(len(translated_column_names)):
        # 如果是数值型
        if type_codes[i] in [1700,701,23]:
            numbers = [x for x in response_data[translated_column_names[i]] if x is not None]
            if numbers == []:
                response_columns.append({"name":translated_column_names[i],"field_type":"指标","default_display":True if i in positions else False,"stats":{}})
            else:
                total_sum = sum(numbers)
                stats = {"sum":total_sum,"avg":total_sum / len(numbers) if numbers else 0,"max":max(numbers),"min":min(numbers)}
                response_columns.append({"name":translated_column_names[i],"field_type":"指标","default_display":True,"stats":stats})
        else:
            response_columns.append({"name":translated_column_names[i],"field_type":"维度","default_display":True if i in positions else False})
    response_metadata = {"sql": sql_query,"record_count":results_length,"display_type": display_type}
    sql_response_json = {"columns":response_columns,"data":response_data,"metadata":response_metadata}
    

    return sql_response_json


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
    translated_column_names = []
    for column in column_names:
        if column not in en2zh_json.keys() and not is_chinese(column):
            need_translate_list.append(column)
    if need_translate_list == []:
        for column in column_names:
            if column in en2zh_json.keys():
                translated_column_names.append(en2zh_json[column])
            else:
                translated_column_names.append(column)
        return translated_column_names

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
        model="qwen-plus",
        messages=[{"role": "user", "content": final_prompt}],
    )
    temp_dict = extract_json_from_response(response.choices[0].message.content)

    for column in column_names:
        if column not in en2zh_json.keys() and not is_chinese(column):
            translated_column_names.append(temp_dict[column])
        elif column in en2zh_json.keys():
            translated_column_names.append(en2zh_json[column])
        else:
            translated_column_names.append(column)
    return translated_column_names

# 从CSV文件中读取数据
def read_csv_data(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

# 查询销售主管涉及的项目ID列表
def get_project_ids_for_sales_manager(saler_id, role_data):
    project_ids = []
    for row in role_data:
        if row['saler_id'] == saler_id and row['role_name'] == '销售主管':
            project_ids.append(row['project_id'])
    return project_ids

# 查询下属置业顾问的saler_id
def query_subordinates(project_ids, role_data):
    subordinate_ids = []
    for row in role_data:
        if row['role_name'] == '置业顾问' and row['project_id'] in project_ids:
            subordinate_ids.append(row['saler_id'])
    return subordinate_ids

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

# 计算两个字符串的相似度
def get_similarity(query1, query2):
    return Levenshtein.ratio(query1, query2)

# 查询干预问题
# 更新查询干预问题的函数以包括相似度匹配
def get_intervention_sql(cursor, user_question, similarity_threshold=0.7):
    query = """  
    SELECT question_name, select_sql  
    FROM nh_problem_meddle  
    WHERE enabled = 'ENABLE' AND DELETE_FLAG = 'NOT_DELETE'  
    """
    cursor.execute(query)
    results = cursor.fetchall()

    for question_name, select_sql in results:
        similarity = get_similarity(user_question, question_name)
        if similarity >= similarity_threshold:
            return select_sql  # 如果相似度足够高，返回相应的 SQL 语句
    return None

def get_indicator_names(cursor):
    query = "SELECT `NAME` FROM NH_INDICATOR_MANAGEMENT"
    cursor.execute(query)
    result = cursor.fetchall()
    indicator_names = [row[0] for row in result if row[0] is not None]
    return indicator_names
def get_indicator_data(cursor,indicator_name):
    query = "SELECT NAME,FIELD_NAME,CALCULATION_RULES,DATA_SOURCE FROM NH_INDICATOR_MANAGEMENT WHERE `NAME` = %s"
    cursor.execute(query, (indicator_name,))
    result = cursor.fetchone()
    if result:
        columns = ["指标名","指标字段名","计算规则","数据来源"]
        result_dict = dict(zip(columns, result))
        #result_json = json.dumps(result_dict, ensure_ascii=False, indent=4, default=default_converter)
        return result_dict


def match_indicator(query, indicator_names):
    # 关键词列表，如“新增”表示新增相关的指标
    keywords = ["新增", "计划", "认购转", "认购未", "累计"]

    # 按照长度从大到小排序，优先匹配更长的指标
    indicator_names.sort(key=len, reverse=True)

    # 如果用户查询中包含关键词，检查匹配的指标是否包含该关键词
    for indicator in indicator_names:
        if indicator in query:
            # 如果查询中包含关键词，而匹配的指标不包含该关键词，跳过
            if any(keyword in query for keyword in keywords) and not any(keyword in indicator for keyword in keywords):
                continue
            return indicator  # 返回匹配到的指标名称

    # 如果没有精准匹配，调用大模型进行模糊匹配
    return fuzzy_match_indicator(query, indicator_names)
    
# 大模型模糊匹配
def fuzzy_match_indicator(query, indicator_names):
    # 创建 OpenAI 客户端并设定模型
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    model = "qwen-plus"

    # 构建模型提示
    indicator_names_str = "\n".join([f"- {indicator}" for indicator in indicator_names])
    prompt = (
        f"请从以下基础指标中提取出用户问题中提到的指标：\n"
        f"{indicator_names_str}\n"
        f"用户问题是：'{query}'\n"
        f"请仔细分析用户的问题，如果问题涉及基础指标，请返回匹配到的基础指标名称的列表，以逗号分隔。如果用户的问题不涉及基础指标，不要强行匹配指标，请返回'无关指标'。"
    )

    # 调用大模型API进行模糊匹配
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )

    # 解析响应并获取匹配的指标
    matched_indicators = response.choices[0].message.content.strip()
    if matched_indicators == "无关指标":
        return None

    if matched_indicators:
        matched_indicators_list = [
            indicator.strip() for indicator in matched_indicators.split(",")
        ]
    else:
        matched_indicators_list = []

    # 过滤基础指标中的有效匹配项
    final_matched_indicators = [
        indicator for indicator in indicator_names if indicator in matched_indicators_list
    ]

    return final_matched_indicators[0] if final_matched_indicators else None


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
    # status=1表示问题干预成功，2表示匹配到指标，3表示返回同义词解释后的语句
    process_user_input_dict = {}
    # 连接到Navicat(Mysql)数据库
    conn, cursor = connect_to_db()

    # 查询同义词
    synonyms = get_synonyms(cursor)  # 这里获取同义词字典
    if synonyms:
        user_question = replace_synonyms(
            user_question, synonyms
        )  # 传入同义词字典
        print(f"Modified question: {user_question}")

    # 查询干预问题对应的SQL语句
    preset_sql = get_intervention_sql(cursor, user_question)

    if preset_sql:
        # 如果找到干预问题，返回预设的SQL语句
        print(f"Intervention found: {preset_sql}")
        # 关闭数据库连接

        process_user_input_dict["status"] = 1
        process_user_input_dict["preset_sql"] = preset_sql
        process_user_input_dict["is_indicator"] = False

        indicator_names = get_indicator_names(cursor)

        indicator_name = match_indicator(user_question,indicator_names)

        if indicator_name:
            # 如果找到匹配的指标，返回匹配的指标
            # 关闭数据库连接
            indicator_data = get_indicator_data(cursor,indicator_name)
            process_user_input_dict["is_indicator"] = True
            process_user_input_dict["indicator_name"] = indicator_name
            process_user_input_dict["indicator_data"] = indicator_data
            
        cursor.close()
        conn.close()
        return process_user_input_dict
    else:
        # 如果没有找到干预问题，进行指标匹配
        # 查询华菁数据库获取所有指标名，以列表形式返回
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
            process_user_input_dict["status"] = 3
            process_user_input_dict["user_question"] = user_question
            return process_user_input_dict

def dws_connect(sql_query,key_fields=None,display_type="response_bar_chart"):
    # status : 0表示sql执行报错,1表示正常返回结果，2表示查询结果为空
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
            start_time = time.time()
            cursor.execute(sql_query)

            results = cursor.fetchall()
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"查询耗时{elapsed_time}秒")
            column_description = cursor.description
            column_names, type_codes = zip(*((des[0], des[1]) for des in column_description))
            if key_fields is None or key_fields=="":
                positions = set(range(len(column_names)))
            else:
                key_field_words = [word.strip() for word in key_fields.split(',')]
                positions = {i for i, word in enumerate(column_names) if word in key_field_words}

            results_length = len(results)
            if results_length > 100:
                results = results[:100]
                results_length = 100
            if results_length==0:
                dws_connect_dict["status"] = 2
                dws_connect_dict["is_long"] = False
                connection.close()
                return dws_connect_dict

            if results_length > 20:
                dws_connect_dict["is_long"] = True
                # sql_results = json.dumps(results[:50], ensure_ascii=False, default=default_converter)
            else:
                dws_connect_dict["is_long"] = False
                sql_results = json.dumps(
                    results, ensure_ascii=False, default=default_converter
                )
                dws_connect_dict["sql_results"] = sql_results
            translated_column_names = get_translate_column_names(column_names)
            dws_connect_dict["translated"] = translated_column_names
            sql_results_json = get_sql_results_json(translated_column_names, type_codes, results, sql_query, results_length, positions, display_type)
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

def dws_connect_test(sql_query):
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
            start_time = time.time()
            cursor.execute(sql_query)

            results = cursor.fetchall()
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"查询耗时{elapsed_time}秒")
            print(results)
    except Exception as e:
        print(str(e))
    finally:
        connection.close()

def extract_json_fields(input_string):
    # Use regex to find potential JSON parts in the input string
    # json_matches = re.findall(r"{.*?}", input_string, re.DOTALL)
    json_matches = re.findall(r"\{(?:[^{}]*|\{(?:[^{}]*|\{[^{}]*\})*\})*\}", input_string, re.DOTALL)
    json_matches.reverse()

    for json_str in json_matches:
        try:
            # Parse the JSON string
            
            # Check if the JSON contains the "sql" key
            if "sql" in json_str:
                json_data = json.loads(json_str)
                # Extract the required fields
                sql = json_data.get("sql", "")
                thoughts = json_data.get("thoughts", "")
                key_fields = json_data.get("key_fields","")
                display_type = json_data.get("display_type","")
                return sql, thoughts, key_fields, display_type
        except json.JSONDecodeError:
            print("json.JSONDecodeError")
            continue  # Skip to the next match if there's a decoding error

    return None, None, None, None

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

    return "这是地产销售数据字典：\n"+"".join(result)

def query_few_shots(database_dir_mapping):
    """
    根据传入的数据库和表名字典，拼接相应表的描述文件内容
    :param database_dir_mapping: 字典，键为数据库名，值为表名列表
    :return: 拼接的描述文件内容
    """
    result = []

    for db_name, tables in database_dir_mapping.items():
        db_dir = os.path.join("FewShots", db_name)  # 假设目录名就是数据库名
        for table in tables:
            table_file = os.path.join(db_dir, f"{table}.txt")  # 表名加上txt后缀构成文件名
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

    example_return_data = [] 
    
    return example_return_data


def test_match(user_question):
    # 连接到Navicat(Mysql)数据库
    conn, cursor = connect_to_db()

    indicator_names = get_indicator_names(cursor)
    indicator_name = match_indicator(user_question,indicator_names)
    cursor.close()
    conn.close()
    return indicator_name
def select_table_based_on_indicator(indicator_tables):
    try:
        table_str = indicator_tables.strip()
        parts = table_str.split(".")
        if len(parts) != 2:
            return None
        # 将数据库部分作为键，表名部分作为值
        return {parts[0]: [parts[1]]}
    except Exception as e:
        # 捕获任何异常，返回 None
        print(str(e))
        return None
def get_indicator_data_dictionary(indicator_tables):
    try:
        table_str = indicator_tables.strip()
        parts = table_str.split(".")
        if len(parts) != 2:
            return None
        # 将数据库部分作为键，表名部分作为值
        return query_tables_description({parts[0]: [parts[1]]})
    except Exception as e:
        # 捕获任何异常，返回 None
        return None

def dict_intersection(dict1, dict2):
    # 初始化结果字典
    result = {}
    
    # 遍历第一个字典的每个键
    for key in dict1:
        # 如果第二个字典中也有该键
        if key in dict2:
            # 计算两个列表的交集
            common_tables = list(set(dict1[key]) & set(dict2[key]))
            # 如果交集非空，将结果添加到结果字典
            if common_tables:
                result[key] = common_tables
    
    return result
if __name__ == "__main__":

    #dws_connect_test("select subtosign_period/newvisittosub_num as subtosignavgcycle,subtosign_num as subtosignunits from fdc_ads.ads_salesreport_subscranalyse_a_min where statdate = current_date")
    dws_connect("""with visitflow as (select projcode, projname, saleruserid, isvisit as isrevisit, visitdate, min(visitdate) over(partition by saleruserid, isvisit) min_visitdate from fdc_dwd.dwd_cust_custvisitflow_a_min where partitiondate = current_date) select count(distinct case when isrevisit = '否' then saleruserid else null end) + count(distinct case when isrevisit = '是' then saleruserid else null end) as 来访组数 from visitflow a where (isrevisit = '是' or visitdate = min_visitdate) and left(visitdate, 10) between '2024-10-01' and '2024-10-07' and projname LIKE '%锦粼湖院%'; """)
