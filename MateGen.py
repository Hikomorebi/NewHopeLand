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
    connect_to_db,
    get_synonyms,
)
import json


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
    sql_code,thoughts = extract_json_fields(response_message.content)

    # 如果sql_code为空，说明无需生成sql代码
    if sql_code is None:
        return_dict["status"] = 1
        return_dict["gpt_response"] = response_message.content
        messages.messages_append(response_message)
        return return_dict
    if sql_code == '':
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
        project=None,
        messages=None,
        tokens_thr=150000,
        available_functions=None,
        is_enhanced_mode=False,
        is_developer_mode=False,
    ):
        self.client = OpenAI(
            api_key=api_key if api_key else os.getenv("OPENAI_API_KEY"),
            base_url=base_url if base_url else "https://api.openai.com/v1",
        )
        self.model = model
        self.system_content_list = system_content_list
        self.project = project
        self.tokens_thr = tokens_thr

        # 创建self.messages属性
        self.messages = ChatMessages(
            system_content_list=self.system_content_list, tokens_thr=self.tokens_thr
        )

        # 若初始参数messages不为None，则将其加入self.messages中
        if messages is not None:
            self.messages.messages_append(messages)

        self.available_functions = available_functions
        self.is_enhanced_mode = is_enhanced_mode
        self.is_developer_mode = is_developer_mode

    def chat(self, question=None):
        return_dict = {"status": 0}  # 提前声明 return_dict 变量
        if question is not None:
            user_message = {"role": "user", "content": question}
            self.messages.messages_append(user_message)

            # 首先检查是否有干预 SQL 语句或指标匹配
            result = process_user_input(question)
            if isinstance(result, str):
                # 返回的是修改后的问题
                modified_question = result
                user_message_modified = {"role": "user", "content": modified_question}
                self.messages.messages_append(user_message_modified)
            elif isinstance(result, list):
                # 返回的是匹配的基础指标
                # 将完整的指标信息提供给大模型
                for indicator in result:
                    self.messages.messages_append({"role": "system", "content": json.dumps(indicator)})
            else:
                # 返回的是干预问题的SQL
                return_dict_sql_exec = sql_exec(result)
                if return_dict_sql_exec["status"] == 0: # sql_exec(result)结果返回字典，status=0表示成功返回
                    return_dict["status"] = 3
                    return_dict["final_response"] = "根据预定义的 SQL 语句返回的结果"
                    return_dict["sql_results_json"] = return_dict_sql_exec["sql_results_json"]
                    return_dict["sql_code"] = result
                else:
                    return_dict["status"] = 2
                    return_dict["sql_error_message"] = return_dict_sql_exec["error_message"]
                return return_dict

            # 第一次提问，负责得到 second_message
            return_dict = get_first_response(
                client=self.client,
                model=self.model,
                messages=self.messages,
                available_functions=None,
                is_developer_mode=self.is_developer_mode,
                is_enhanced_mode=self.is_enhanced_mode,
            )

            # 0表示大模型调用失败，2表示生成错误的SQL语句
            if return_dict["status"] == 0 or return_dict["status"] == 2:
                self.messages.messages_append(
                    {"role": "assistant", "content": "该问题无法回答。"}
                )

            if return_dict["status"] != 3:
                return return_dict

            response_message_stream = get_gpt_response_stream(
                self.client, self.model, return_dict["second_message"]
            )
            return_dict["response_message_stream"] = response_message_stream
            return return_dict

    def reset(self):
        """
        重置当前MateGen对象的messages
        """
        self.messages = ChatMessages(
            system_content_list=self.system_content_list, tokens_thr=self.tokens_thr
        )
