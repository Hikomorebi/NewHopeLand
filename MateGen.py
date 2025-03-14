import os
from openai import OpenAI
import copy
import time
import traceback
import requests
from ChatMessage import ChatMessages
from utils import (
    modify_prompt,
    add_task_decomposition_prompt,
    extract_json_fields,
    process_user_input,
    dws_connect,
    get_indicator_data_dictionary,
    force_matching
)
from get_date import get_enhanced_query
import json

CLIENT_URL = "http://113.54.153.102:45109" #实验室

system_prompt_indicator_template = """
{indicator_name}是一个需要计算的指标，它的字段名为{indicator_field_name}，计算规则为:
{indicator_rule};
你是一名数据库专家，请根据计算规则生成正确的PostgreSQL语句。要求如下：
1. 请仔细阅读并理解用户的请求。参考数据库字典提供的表结构和各字段信息，根据计算规则生成正确的PostgreSQL语句。
2. 请完全按照提供的计算规则模板来设计SQL语句，不要修改计算规则的结构，同时如果计算规则中带有'$'符合作为占位符，需要从用户问题中提取相关的时间等信息来填充占位符。请确保所有占位符都被具体的值填充。
3. 请确保所有字段和条件都使用具体的值。禁止随意假设不存在的信息。请务必确保生成的SQL语句能够直接运行。
4. 如果数据字典中存在 partitiondate 字段，请在生成SQL语句的筛选条件中加入 partitiondate = current_date 。如果计算规则中存在 partitiondate 字段，则将该字段值筛选条件设为 current_date 。
5. 如果用户请求的是一段时间内的数据，请确保SQL语句能够正确提取这段时间内的数据。如询问当日的数据，可以使用 current_date 作为筛选条件。
6. 若用户提问中涉及项目名称，请提取项目名称作为筛选条件。项目名称可能包含城市名，应视为一个完整的字符串，不要拆分。如"成都皇冠湖壹号","温州立体城"才是完整的项目名称。
请严格按照计算规则的逻辑给出SQL代码，并按照以下JSON格式响应，要求只返回一个json对象，不要包含其余内容：
{{
    "sql": "SQL Query to run",
}}
"""


def get_gpt_response(
    client,
    model,
    messages,
    available_functions=None,
    is_developer_mode=False,
    is_enhanced_mode=False,
):
    # 如果开启开发者模式，则进行提示词修改，首次运行是增加提示词
    if is_developer_mode:
        messages = modify_prompt(messages, action="add")

    # 如果是增强模式，则增加复杂任务拆解流程
    if is_enhanced_mode:
        enhanced_messages = add_task_decomposition_prompt(messages)
    else:
        enhanced_messages = messages

    # 考虑到可能存在通信报错问题，因此循环调用Chat模型进行执行

    try:
        # 若不存在外部函数
        if available_functions is None or available_functions.functions_list is None:
            response = client.chat.completions.create(
                model=model, messages=enhanced_messages.messages, temperature=0.01
            )
        # 若存在外部函数，此时functions和function_call参数信息都从AvailableFunctions对象中获取
        else:
            response = client.chat.completions.create(
                model=model,
                messages=enhanced_messages.messages,
                tools=available_functions.functions,
                tool_choice=available_functions.function_call,
            )
    except Exception as e:
        traceback.print_exc()
        return {"role": "get_gpt_response", "content": str(e)}

    # 还原原始的msge对象
    if is_developer_mode:
        messages = modify_prompt(messages, action="remove")

    return response.choices[0].message


def get_gpt_response_stream(client, model, messages):
    stream = client.chat.completions.create(
        model=model, messages=messages.messages, stream=True, temperature=0.01
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield json.dumps({"content": chunk.choices[0].delta.content})


class MateGen:
    def __init__(
        self,
        api_key=None,
        base_url=None,
        model="gpt-3.5-turbo",
        system_content_list=[],
        tokens_thr=150000,
        current_indicator=None,
        current_count=0
    ):
        self.client = OpenAI(
            api_key=api_key if api_key else os.getenv("OPENAI_API_KEY"),
            base_url=base_url if base_url else "https://api.openai.com/v1",
        )
        self.model = model
        self.system_content_list = system_content_list
        self.tokens_thr = tokens_thr

        # 创建self.messages属性
        self.messages = ChatMessages(
            system_content_list=self.system_content_list, tokens_thr=self.tokens_thr
        )
        self.current_indicator = current_indicator
        self.current_count = current_count

    def chat(self, process_user_input_dict=None):
        # status:0表示大模型调用失败，1表示无需生成SQL语句，2表示生成SQL错误，3表示成功生成SQL语句
        chat_dict = {"time":"\n"}
        if process_user_input_dict is not None:
            question = process_user_input_dict['user_question']

            question = get_enhanced_query(question)
            print(f"修改问题为{question}")

            user_message = {"role": "user", "content": question}
            self.messages.messages_append(user_message)
            before_get_sql = time.time()
            if process_user_input_dict["status"] == 1:
                sql_code = process_user_input_dict["preset_sql"]
                self.messages.messages_append(user_message)
                key_fields = None
                display_type = "response_bar_chart"
            else:
                response_message = get_gpt_response(
                    client=self.client, model=self.model, messages=self.messages
                )
                if type(response_message) is dict:
                    chat_dict["status"] = 0
                    chat_dict["gpt_error_message"] = response_message["content"]
                    return chat_dict

                print("============================================================")
                print("第一次提问返回结果")
                print(response_message.content)
                print("============================================================")
                # 解析出SQL代码和返回类型
                sql_code, thoughts, key_fields, display_type = extract_json_fields(
                    response_message.content
                )
                if sql_code is None:
                    chat_dict["status"] = 1
                    chat_dict["gpt_response"] = response_message.content
                    self.messages.messages_append(response_message)
                    return chat_dict
                if sql_code == "":
                    chat_dict["status"] = 2
                    chat_dict["sql_error_message"] = (
                        "我现在还回答不了这样的问题，敬请期待。"
                    )
                    self.messages.messages_append(
                        {
                            "role": "assistant",
                            "content": "针对该问题无法为您生成可用的查询。",
                        }
                    )
                    return chat_dict
            start_time_dws = time.time()
            elapsed_time_get_sql = start_time_dws - before_get_sql
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print(f"第二阶段：获取SQL语句耗时: {elapsed_time_get_sql:.4f} 秒")
            chat_dict["time"]+=f"第二阶段：获取SQL语句耗时: {elapsed_time_get_sql:.4f} 秒\n"
            # 执行SQL语句
            # status : 0表示sql执行报错,1表示正常返回结果，2表示查询结果为空
            # sql_exec_dict = dws_connect(sql_code, key_fields, display_type)
            # 调用客户端API执行SQL查询
            response = requests.post(
                f"{CLIENT_URL}/execute_sql", 
                json={"sql_query": sql_code, "key_fields": key_fields, "display_type": display_type}
            )
            sql_exec_dict = response.json()    

            end_time_dws = time.time()
            elapsed_time_dws = end_time_dws - start_time_dws
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print(f"第三阶段：查询dws数据库并制作sql_response耗时: {elapsed_time_dws:.4f} 秒")
            chat_dict["time"]+=f"第三阶段：查询dws数据库并制作sql_response耗时: {elapsed_time_dws:.4f} 秒\n"
            
            if sql_exec_dict["status"] == 0:
                if process_user_input_dict['indicator_name'] == 'base':
                    # 当sql执行报错且为基础问数时，强行匹配一个指标
                    dict_force = force_matching(process_user_input_dict['user_question'])
                    # 3 表示仍然没有匹配上指标
                    if dict_force['status'] == 3:
                        chat_dict["status"] = 2
                        chat_dict["sql_error_message"] = "我现在还回答不了这样的问题，敬请期待。"
                        print(sql_exec_dict["error_message"])
                        self.messages.messages_append(
                            {
                                "role": "assistant",
                                "content": "针对当前问题无法为您生成可用的查询。",
                            }
                        )
                        return chat_dict
                    elif dict_force['status'] == 2:
                        chat_dict["status"] = 1
                        chat_dict["gpt_response"] = f"你是想问以下指标中的某一个吗：{'，'.join(dict_force['indicator_names'])}，请选择你想要提问的指标重新提问。"
                        self.messages.messages_append(
                            {
                                "role": "assistant",
                                "content": "针对当前问题无法为您生成可用的查询。",
                            }
                        )

                else:
                    chat_dict["status"] = 2
                    chat_dict["sql_error_message"] = "我现在还回答不了这样的问题，敬请期待。"
                    print(sql_exec_dict["error_message"])
                    self.messages.messages_append(
                        {
                            "role": "assistant",
                            "content": "针对当前问题无法为您生成可用的查询。",
                        }
                    )
                    return chat_dict
            elif sql_exec_dict["status"] == 2:
                chat_dict["status"] = 1
                chat_dict["gpt_response"] = "没有输出，换个问法试试..."
                self.messages.messages_append(
                    {
                        "role": "assistant",
                        "content": "针对该问题，查询结果为空。",
                    }
                )
                return chat_dict
            copy_messages = copy.deepcopy(self.messages)
            if sql_exec_dict["is_long"]:
                second_message = {
                    "role": "user",
                    "content": """你是一个助手，需要为用户生成描述性文字，用于辅助理解SQL查询到的结果内容。请注意：
                    1. 不要包含具体的数值、数量、或内容，例如数字、列表中的项目、统计值等。
                    2. 仅需生成一段简短的描述，概括SQL查询结果的意义或范围，不要假设查询结果的具体细节。
                    3. 回答内容应完全基于用户问题的内容。
                    如下展示两个问答示例：
                    user：请列出2024年8月提交的所有订单。
                    assiatant：这里展示了2024年8月提交的所有订单。
                    user：查询南京天悦锦麟项目的所有客户名称和合同金额。
                    assistant：以下内容展示了南京天悦锦麟项目中所有客户的名称和合同金额。
                    """,
                }
            else:
                
                second_message = {
                    "role": "user",
                    "content": f"""
                    为了回答这个问题，使用SQL语句查询数据库返回结果，列名为：{sql_exec_dict['translated']}，每行内容为 {sql_exec_dict['sql_results']} ，请根据返回结果回答问题，请生成总结式的概括，尽可能简洁，当用户
                    未指定输出格式时，按下面的默认规范显示：
                    金额：单位为万元，按千分位展示，比如 19,341 万元。
                    套数：单位为套，按千分位展示，比如 12,247 套。
                    面积：单位为平方米，按千分位展示，比如 1325 平方米。
                    百分比：单位为%，按千分位展示，比如 41%。
                    仅需进行简短的概括式的描述，而无需对数据进行分析。尽可能简洁。
                    """,
                }
            copy_messages.delete_system_messages_temp()
            copy_messages.messages_append(second_message)

            chat_dict["status"] = 3
            chat_dict["sql_results_json"] = sql_exec_dict["sql_results_json"]
            chat_dict["sql_code"] = sql_code
            chat_dict["column_names"] = sql_exec_dict["column_names"]
            response_message_stream = get_gpt_response_stream(
                self.client, self.model, copy_messages
            )
            chat_dict["response_message_stream"] = response_message_stream
            return chat_dict

    def reset(self):
        """
        重置当前MateGen对象的messages
        """
        self.messages = ChatMessages(
            system_content_list=self.system_content_list, tokens_thr=self.tokens_thr
        )

    def replace_data_dictionary(self, data_dicrionary_md):
        new_list = [data_dicrionary_md] + self.system_content_list
        self.messages = ChatMessages(
            system_content_list=new_list, tokens_thr=self.tokens_thr
        )

    def add_session_messages(self, session_messages):
        for session_message in session_messages:
            self.messages.messages_append(session_message)
