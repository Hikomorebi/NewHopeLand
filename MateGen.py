import os
from openai import OpenAI
import copy
import traceback
from ChatMessage import ChatMessages
from utils import (
    modify_prompt,
    add_task_decomposition_prompt,
    extract_json_fields,
    process_user_input,
    dws_connect,
    get_indicator_data_dictionary,
)
import json

system_prompt_indicator_template = """
{indicator_name}是一个需要计算的指标，它的字段名为{indicator_field_name}，计算规则为:
{indicator_rule}；
你是一名数据库专家，请根据计算规则生成正确的PostgreSQL语句。要求如下：
1. 请仔细阅读并理解用户的请求。参考数据库字典提供的表结构和各字段信息，根据计算规则生成正确的PostgreSQL语句。
2. 请完全按照提供的计算规则模板来设计SQL语句，不要修改计算规则的结构，同时如果计算规则中带有'$'符合作为占位符，需要从用户问题中提取相关的时间等信息来填充占位符。
3. 请确保所有字段和条件都使用具体的值。禁止随意假设不存在的信息。请务必确保生成的SQL语句能够直接运行。
4. 如果数据字典中存在 partitiondate 字段，请在生成SQL语句的筛选条件中加入 partitiondate = current_date 。如果计算规则中存在 partitiondate 字段，则将该字段值筛选条件设为 current_date 。
5. 若用户提问中涉及项目名称，请提取项目名称作为筛选条件。项目名称可能包含城市名，应视为一个完整的字符串，不要拆分。如"成都皇冠湖壹号","温州立体城"才是完整的项目名称。
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

    def chat(self, question=None):
        # status:0表示大模型调用失败，1表示无需生成SQL语句，2表示生成SQL错误，3表示成功生成SQL语句
        chat_dict = {}
        if question is not None:
            user_message = {"role": "user", "content": question}
            # todo:逻辑修改，需要先进行同义词解释，再进行问题干预和指标问数。
            # 该函数直接判断是否为问题干预（1）、指标问数（2）、同义词解释（3）
            process_user_input_dict = process_user_input(question)

            # 1 表示问题干预成功，直接得到SQL语句
            if process_user_input_dict["status"] == 1:
                sql_code = process_user_input_dict["preset_sql"]
                self.messages.messages_append(user_message)
                key_fields = None
                display_type = "response_bar_chart"
            else:
                indicator_message = copy.deepcopy(self.messages)
                if process_user_input_dict["status"] == 2:
                    indicator_data = process_user_input_dict["indicator_data"]
                    indicator_name = process_user_input_dict["indicator_name"]
                    print(f"匹配到指标：{indicator_name}")
                    system_prompt_indicator = system_prompt_indicator_template.format(
                        indicator_name=indicator_name,
                        indicator_field_name=indicator_data["指标字段名"],
                        indicator_rule=indicator_data["计算规则"],
                    )
                    indicator_tables = indicator_data["数据来源"]
                    indicator_data_dictionary = get_indicator_data_dictionary(
                        indicator_tables
                    )
                    if (
                        indicator_data_dictionary is None
                        or indicator_data_dictionary == ""
                    ):
                        indicator_message.delete_system_messages_temp()
                        indicator_message.add_system_message_temp(
                            {"role": "system", "content": system_prompt_indicator}
                        )
                    else:
                        indicator_system_messages = [
                            {"role": "system", "content": indicator_data_dictionary},
                            {"role": "system", "content": system_prompt_indicator},
                        ]
                        indicator_message.replace_system_message(
                            indicator_system_messages
                        )
                    indicator_message.messages_append(user_message)

                    self.messages.messages_append(user_message)

                elif process_user_input_dict["status"] == 3:
                    modified_question = process_user_input_dict["user_question"]
                    indicator_message.messages_append(
                        {"role": "user", "content": modified_question}
                    )
                    self.messages.messages_append(user_message)

                response_message = get_gpt_response(
                    client=self.client, model=self.model, messages=indicator_message
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
                        "针对当前问题无法为您生成可用的查询。"
                    )
                    self.messages.messages_append(
                        {
                            "role": "assistant",
                            "content": "针对当前问题无法为您生成可用的查询。",
                        }
                    )
                    return chat_dict

            # 执行SQL语句
            # status : 0表示sql执行报错,1表示正常返回结果，2表示查询结果为空
            sql_exec_dict = dws_connect(sql_code, key_fields, display_type)
            if sql_exec_dict["status"] == 0:
                chat_dict["status"] = 2
                chat_dict["sql_error_message"] = sql_exec_dict["error_message"]
                self.messages.messages_append(
                    {
                        "role": "assistant",
                        "content": "针对当前问题无法为您生成可用的查询。",
                    }
                )
                return chat_dict
            elif sql_exec_dict["status"] == 2:
                chat_dict["status"] = 1
                chat_dict["gpt_response"] = "针对该问题，查询结果为空。"
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
                    "content": "由于查询结果数据量较大，无法全部展示。但是用户已经得到所需的全部数据。根据问题请生成一段简要的描述性文字，用于配合用户得到的数据，描述查询结果的概况。例如问题：请列出2024年8月提交的所有订单。你的回答：这里展示了2024年8月提交的所有订单。尽量简洁，只需要简短一句话即可。",
                }
            else:
                second_message = {
                    "role": "user",
                    "content": f"为了回答这个问题，生成SQL代码： {sql_code} 查询数据库，SQL查询返回结果为 {sql_exec_dict['sql_results']} ，请根据返回结果回答问题，请生成总结式的概括，尽可能简洁，你可以假装用户已经获取需要的数据，而不要在回答中直接展示数据。",
                }
            copy_messages.delete_system_messages_temp()
            copy_messages.messages_append(second_message)

            chat_dict["status"] = 3
            chat_dict["sql_results_json"] = sql_exec_dict["sql_results_json"]
            chat_dict["sql_code"] = sql_code
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
