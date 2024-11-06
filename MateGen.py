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
    sql_exec,
    dws_connect,
    connect_to_db,
    get_synonyms,
)
import json

system_prompt_indicator_template = """
指标{indicator_name}的字段名为{indicator_field_name}，其计算规则为:{indicator_rule}。
你是一名数据库专家，请根据计算规则生成正确的PostgreSQL语句。
1. **理解用户意图**：请仔细阅读并理解用户的请求，根据用户提问对计算规则中带有‘$’符号的占位符进行填充。
2. **使用计算规则**：请完全按照提供的计算规则模板来设计SQL语句，不要无端自行增删或修改计算规则，同时需要从用户问题中提取相关的时间等信息来填充计算规则中带有'$'符号的占位符以生成完整正确的SQL语句。
3. **SQL规范性**：生成的SQL语句不能涵盖非法字符如"\n"，请确保生成的SQL语句能直接在数据库上执行。
请根据计算规则给出SQL代码，并按照以下JSON格式响应：  
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
                model=model, messages=enhanced_messages.messages
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


def get_first_response(
    client,
    model,
    messages,
    available_functions=None,
    is_developer_mode=False,
    is_enhanced_mode=False,
):
    """
    不对messages作出任何改变，且返回一个最正确的copy_messages
    """
    # 0 表示大语言模型调用失败，1 表示无需生成SQL代码，2 表示无法生成正确的SQL语句，3表示正确返回
    return_dict = {"status": 0}
    # 本轮对话第一次提问
    response_message = get_gpt_response(
        client=client,
        model=model,
        messages=messages,
        available_functions=available_functions,
        is_developer_mode=is_developer_mode,
        is_enhanced_mode=is_enhanced_mode,
    )

    if type(response_message) is dict:
        return_dict["gpt_error_message"] = response_message["content"]
        return return_dict

    print("============================================================")
    print("第一次提问返回结果")
    print(response_message.content)
    print("============================================================")

    # 解析出SQL代码和返回类型
    sql_code, thoughts = extract_json_fields(response_message.content)

    # 如果sql_code为空，说明无需生成sql代码
    if sql_code is None:
        return_dict["status"] = 1
        return_dict["gpt_response"] = response_message.content
        messages.messages_append(response_message)
        return return_dict
    if sql_code == "":
        return_dict["status"] = 2
        return_dict["sql_error_message"] = "针对当前问题无法为您生成可用的查询。"
        return return_dict

    # 执行SQL代码并返回结果
    return_dict_sql_exex = sql_exec(sql_code)
    if return_dict_sql_exex["status"] == 0:
        correct_messages = copy.deepcopy(messages)
        correct_messages.messages_append(response_message)
        correct_message = {
            "role": "user",
            "content": f"生成的SQL代码{sql_code}执行时发生错误，报错信息：{return_dict_sql_exex['error_message']}，请根据报错信息进行检查，重新按照要求以json的格式生成SQL语句。",
        }
        correct_messages.messages_append(correct_message)
        response_message = get_gpt_response(
            client=client,
            model=model,
            messages=correct_messages,
            available_functions=available_functions,
            is_developer_mode=is_developer_mode,
            is_enhanced_mode=is_enhanced_mode,
        )
        sql_code, display_type = extract_json_fields(response_message.content)
        return_dict_sql_exex = sql_exec(sql_code)

        # 如果仍然执行失败，则直接返回，不再重新提问
        if return_dict_sql_exex["status"] == 0:
            return_dict["status"] = 2
            return_dict["sql_error_message"] = return_dict_sql_exex["error_message"]
            return return_dict

    copy_messages = copy.deepcopy(messages)
    if return_dict_sql_exex["is_long"]:
        second_message = {
            "role": "system",
            "content": "由于查询结果数据量较大，无法全部展示。但是用户已经得到所需的全部数据。根据问题请生成一段简要的描述性文字，用于配合用户得到的数据，描述查询结果的概况。例如问题：请列出2024年8月提交的所有订单。你的回答：这里展示了2024年8月提交的所有订单。尽量简洁，只需要简短一句话即可。",
        }
    else:
        second_message = {
            "role": "system",
            "content": f"为了回答这个问题，生成SQL代码： {sql_code} 查询数据库，SQL查询返回结果为 {return_dict_sql_exex['sql_results']} ，请根据返回结果回答问题，请生成总结式的概括，尽可能简洁，你可以假装用户已经获取需要的数据，而不要在回答中直接展示数据。",
        }
    copy_messages.messages_append(second_message)
    copy_messages.delete_system_messages_temp()

    return_dict["status"] = 3
    return_dict["second_message"] = copy_messages
    return_dict["sql_results_json"] = return_dict_sql_exex["sql_results_json"]
    return_dict["sql_code"] = sql_code
    return_dict["thoughts"] = thoughts

    return return_dict


def get_gpt_response_stream(client, model, messages):
    stream = client.chat.completions.create(
        model=model, messages=messages.messages, stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield json.dumps({"content": chunk.choices[0].delta.content})


def get_second_response(
    client,
    model,
    messages,
    return_dict,
    available_functions=None,
    is_developer_mode=False,
    is_enhanced_mode=False,
):
    response_message = get_gpt_response(
        client=client,
        model=model,
        messages=return_dict["second_message"],
        available_functions=available_functions,
        is_developer_mode=is_developer_mode,
        is_enhanced_mode=is_enhanced_mode,
    )
    if type(response_message) is dict:
        del return_dict
        return_dict = {"status": 0, "gpt_error_message": response_message["content"]}
        return return_dict

    print("============================================================")
    print("第二次提问返回结果")
    print(response_message.content)
    print("============================================================")
    messages.messages_append(response_message)
    del return_dict["second_message"]
    return_dict["final_response"] = response_message.content

    return return_dict


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

            if process_user_input_dict["status"] == 1:
                sql_code = process_user_input_dict["preset_sql"]
                self.messages.messages_append(user_message)
            else:
                indicator_message = copy.deepcopy(self.messages)
                if process_user_input_dict["status"] == 2:
                    indicator_data = process_user_input_dict["indicator_data"]
                    indicator_name = process_user_input_dict["indicator_name"]
                    system_prompt_indicator = system_prompt_indicator_template.format(
                        indicator_name=indicator_name,
                        indicator_field_name=indicator_data["指标字段名"],
                        indicator_rule=indicator_data["计算规则"]
                    )
                    indicator_message.delete_system_messages_temp()
                    indicator_message.add_system_message_temp(
                        {"role": "system", "content": system_prompt_indicator}
                    )
                    indicator_message.messages_append(user_message)

                    self.messages.messages_append(user_message)

                elif process_user_input_dict["status"] == 3:
                    modified_question = process_user_input_dict["modified_question"]
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
                sql_code, thoughts = extract_json_fields(response_message.content)
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
            sql_exec_dict = dws_connect(sql_code)
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
