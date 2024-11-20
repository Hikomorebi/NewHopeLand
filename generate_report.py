# -*- coding: utf-8 -*-
import os
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import re
import csv
from info import(
    historical_data,
    knowledge_base,
    find_similar_customers
)
# 设置环境变量（仅在当前脚本运行期间有效）
os.environ["OPENAI_API_KEY"] = "sk-94987a750c924ae19693c9a9d7ea78f7"

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
model = 'qwen2.5-72b-instruct'

# Few-shot 示例
few_shot_examples = '''
[   
    {
        "客户基本信息总结": {
            "接待销售": "张兴基",
            "来访渠道": "自然",
            "客户姓名": "卢女士",
            "首复访": "首访",
            "年龄": "未知",
            "诚意度": "E",
            "家庭人数": "未知",
            "置业次数": "未知",
            "意向面积": "洋房",
            "预期价格": "未知",
            "预期折扣": "未知",
            "首付预算": "未知",
            "关注点1": "暂无购房需求",
            "关注点2": "暂无购房需求",
            "对比竞品": "无",
            "未成交原因": "暂无购房需求",
            "客户情况补充": "路过逛逛，暂无购房需求",
            "最新跟进反馈": "回访电话打不通，加了女儿微信，女儿不回信息"
        },
        "成交卡点分析": {
            "1. 无购房需求": "卢女士表示暂无购房需求，且没有明确的购房预算或购房计划。",
            "2. 联系难度大": "虽然有加女儿微信，但联系较困难，影响了后续跟进的可能性。",
            "3. 路过考察": "她只是路过并没有明确的购房意图，可能对项目不感兴趣。"
        },
        "后续跟进计划": [
            {
                "时间": "一周内",
                "内容": "尝试再次与卢女士通过电话或微信沟通，确认是否有进一步购房计划。",
                "方式": "通过电话或微信联系卢女士，询问是否对购房有新的考虑。"
            },
            {
                "时间": "两周内",
                "内容": "通过电话与卢女士再次确认她的购房意向，并提醒她项目的特色。",
                "方式": "电话联系，提供当前楼盘的一些优惠信息。"
            },
            {
                "时间": "每月一次",
                "内容": "定期保持联系，了解卢女士的购房需求是否有所变化。",
                "方式": "电话或微信联系，提供市场动态和优惠活动。"
            },
            {
                "时间": "长期",
                "内容": "持续关注卢女士的购房意图变化，适时更新楼盘信息。",
                "方式": "通过电话或微信定期发送楼盘信息和优惠政策。"
            }
        ],
        "意向等级": "E - 无意向"
    },
    {
        "客户基本信息总结": {
            "接待销售": "李国良",
            "来访渠道": "自渠",
            "客户姓名": "张女士",
            "首复访": "首访",
            "年龄": "30",
            "诚意度": "C",
            "家庭人数": "2",
            "置业次数": "首次",
            "意向面积": "90-100m²",
            "预期价格": "80-90万",
            "预期折扣": "未知",
            "首付预算": "未知",
            "关注点1": "价格",
            "关注点2": "交通",
            "对比竞品": "无",
            "未成交原因": "预算不足",
            "客户情况补充": "张女士对价格非常敏感，预算有限，之前看了很多类似的楼盘都觉得价格太高。",
            "最新跟进反馈": "目前没有进一步购房的强烈意向，暂时没有选择的计划"
        },
        "成交卡点分析": {
            "1. 价格敏感": "张女士对价格的敏感性较强，预算限制了她的选择范围。",
            "2. 交通需求": "张女士对交通的要求较高，但目前的房源不完全满足她的需求。",
            "3. 资金承受力": "张女士目前面临资金承受力问题，购房预算不足，可能需要调整预算或等待其他房源。"
        },
        "后续跟进计划": [
            {
                "时间": "一周内",
                "内容": "通过电话联系张女士，确认她的预算范围，并推荐符合预算的房源。",
                "方式": "电话联系，发送相关房源信息"
            },
            {
                "时间": "两周内",
                "内容": "了解张女士对其他房源的反馈，提供一些特价或优惠的房源。",
                "方式": "电话联系，发送特价房源信息"
            },
            {
                "时间": "每月一次",
                "内容": "定期与张女士保持联系，了解她对市场房价的看法，定期推荐符合预算的房源。",
                "方式": "电话或微信联系"
            },
            {
                "时间": "长期",
                "内容": "密切关注市场上价格适中的房源，及时向张女士推送符合她需求的房源。",
                "方式": "建立客户档案，定期更新市场信息"
            }
        ],
        "意向等级": "C - 一般意向"
    },
    {
        "客户基本信息总结": {
            "接待销售": "王涛",
            "来访渠道": "自然",
            "客户姓名": "李先生",
            "首复访": "首访",
            "年龄": "40",
            "诚意度": "D",
            "家庭人数": "4",
            "置业次数": "首次",
            "意向面积": "120m²",
            "预期价格": "160-180万",
            "预期折扣": "未知",
            "首付预算": "未知",
            "关注点1": "学区",
            "关注点2": "生活配套",
            "对比竞品": "无",
            "未成交原因": "资金问题",
            "客户情况补充": "李先生目前没有购房资金，计划等资金到位后再考虑购房。",
            "最新跟进反馈": "暂时没有购房意向，资金不足，且还在考虑学区和配套问题"
        },
        "成交卡点分析": {
            "1. 资金问题": "李先生目前缺乏购房所需资金，暂时没有明确的购房计划。",
            "2. 学区要求": "李先生希望选一个学区较好的房源，但目前没有找到合适的房源。",
            "3. 生活配套需求": "李先生对生活配套设施有较高要求，但当前的房源可能不完全满足需求。"
        },
        "后续跟进计划": [
            {
                "时间": "一月内",
                "内容": "了解李先生的资金情况，提供适合资金情况的房源，并帮助其解决购房资金问题。",
                "方式": "电话联系，发送房源信息并进行资金咨询"
            },
            {
                "时间": "两个月内",
                "内容": "继续关注李先生的资金情况，推荐符合学区要求的房源。",
                "方式": "电话或微信联系"
            },
            {
                "时间": "每季一次",
                "内容": "每季与李先生联系，了解资金变化和学区需求的变化，及时调整推荐房源。",
                "方式": "电话或微信联系"
            },
            {
                "时间": "长期",
                "内容": "持续关注市场上符合李先生需求的房源，及时推荐。",
                "方式": "定期更新市场信息，电话或微信联系"
            }
        ],
        "意向等级": "D - 低意向"
    }，
    {
        "客户基本信息总结": {
            "接待销售": "张兴基",
            "来访渠道": "自然",
            "客户姓名": "关吕静",
            "首复访": "首访",
            "年龄": "未知",
            "诚意度": "A",
            "家庭人数": "未知",
            "置业次数": "未知",
            "意向面积": "洋房",
            "预期价格": "未知",
            "预期折扣": "未知",
            "首付预算": "未知",
            "关注点1": "暂无",
            "关注点2": "暂无",
            "对比竞品": "无",
            "未成交原因": "无",
            "客户情况补充": "当天认购新增录入",
            "最新跟进反馈": "已认购"
        },
        "成交卡点分析": {
            "1. 高意向度": "关吕静为当天认购客户，表现出较强的购房意向，可能是目标客户。",
            "2. 即时认购": "客户在首访当天即表现出认购意向，显示出高转化潜力。"
        },
        "后续跟进计划": [
            {
                "时间": "一周内",
                "内容": "确认客户的认购进度，确保顺利完成相关购房流程。",
                "方式": "通过电话或微信联系客户，确保认购手续顺利进行。"
            },
            {
                "时间": "两周内",
                "内容": "跟进客户对选定房源的后续反馈，并提供必要的支持。",
                "方式": "电话联系客户，询问购房后期可能需要的服务。"
            },
            {
                "时间": "每月一次",
                "内容": "维持联系，了解客户在购房过程中的任何需求或疑问。",
                "方式": "定期通过电话或微信沟通，确保客户的购房需求得到满足。"
            },
            {
                "时间": "长期",
                "内容": "为客户提供后续入住及装修建议，维持长期关系。",
                "方式": "与客户保持联系，提供后期房产服务。"
            }
        ],
        "意向等级": "A - 高意向"
    },
    {
        "客户基本信息总结": {
            "接待销售": "张利飞",
            "来访渠道": "自渠",
            "客户姓名": "崔先生",
            "首复访": "首访",
            "年龄": "未知",
            "诚意度": "B",
            "家庭人数": "未知",
            "置业次数": "未知",
            "意向面积": "120",
            "预期价格": "104万",
            "预期折扣": "未知",
            "首付预算": "未知",
            "关注点1": "温岭华府",
            "关注点2": "价格敏感",
            "对比竞品": "温岭华府",
            "未成交原因": "风水问题",
            "客户情况补充": "着急入住，考虑风水问题。",
            "最新跟进反馈": "希望风水师过来看房"
        },
        "成交卡点分析": {
            "1. 价格敏感": "崔先生对价格相对敏感，可能影响决策。",
            "2. 风水问题": "客户提到需要风水师查看，可能影响他对房源的最终选择。",
            "3. 着急入住": "崔先生需要尽快找到合适的房源，时间较为紧迫。"
        },
        "后续跟进计划": [
            {
                "时间": "一周内",
                "内容": "联系风水师陪同崔先生实地看房，解答风水疑虑。",
                "方式": "安排风水师与客户一同考察房源，消除疑虑。"
            },
            {
                "时间": "两周内",
                "内容": "跟进崔先生对房源的意见，并在价格上进行适当让步。",
                "方式": "电话联系，讨论价格及相关优惠政策。"
            },
            {
                "时间": "每月一次",
                "内容": "定期向崔先生提供市场上符合他需求的房源信息。",
                "方式": "通过电话或微信更新楼盘信息，提供最新价格与房源情况。"
            },
            {
                "时间": "长期",
                "内容": "维持长期联系，关注崔先生的购房需求变化。",
                "方式": "定期通过电话或微信联系，提供购房相关信息。"
            }
        ],
        "意向等级": "B - 高意向"
    }，
    {   请根据以下客户的基本信息，生成有针对性的成交卡点、后续跟进计划以及意向等级：

        "客户基本信息总结": {
            "接待销售": "张丽",
            "来访渠道": "自然来访",
            "客户姓名": "戴先生",
            "首复访": "首访",
            "年龄": "未知",
            "诚意度": "D",
            "家庭人数": "未知",
            "置业次数": "首次",
            "意向面积": "110-120m²",
            "预期价格": "260-280万",
            "预期折扣": "未知",
            "首付预算": "未知",
            "关注点1": "地段",
            "关注点2": "升值潜力",
            "对比竞品": "未知",
            "未成交原因": "户型",
            "客户情况补充": "戴先生看商铺投资，面积太大了！位置也不喜欢，想买100左右的商铺，投资",
            "最新跟进反馈": "便宜，肯定接受"
        },
        "成交卡点分析": {
            "1. 面积过大": "戴先生认为现有的商铺面积（130m²）过大，不符合他的投资需求。",
            "2. 位置不满意": "戴先生对当前商铺的位置不满意，希望找到更符合他需求的位置。",
            "3. 户型问题": "戴先生对现有商铺的户型不满意，可能影响他的投资决策。",
            "4. 价格敏感": "戴先生对价格非常敏感，希望价格能够更加合理。"
        },
        "后续跟进计划": [
            {
                "时间": "一周内",
                "内容": "整理并提供符合戴先生需求的100平方米左右的商铺房源信息，包括位置、价格、户型等详细资料。",
                "方式": "通过电话或微信联系戴先生，发送相关资料。"
            },
            {
                "时间": "两周内",
                "内容": "邀请戴先生实地考察推荐的商铺，现场了解商铺的具体情况。",
                "方式": "提前预约，确保戴先生的时间安排。"
            },
            {
                "时间": "每月一次",
                "内容": "定期与戴先生沟通，了解他对推荐商铺的意见和建议，及时调整推荐方案。",
                "方式": "电话或微信联系。"
            },
            {
                "时间": "长期",
                "内容": "持续关注市场上的优质商铺资源，一旦发现符合戴先生需求的新房源，立即通知他。",
                "方式": "建立客户档案，定期更新市场信息。"
            }
        ],
        "意向等级": "D - 低意向"
    }   
]
'''

# 调用通义千问 API 生成建议、计划和意向等级
def generate_model_suggestions_and_rank(customer_data):
    customer_info = "客户基本信息:\n"
    for key, value in customer_data.items():
        customer_info += f"{key}: {value}\n"

    prompt = f"""
    {few_shot_examples}
    根据以下客户的基本信息，生成有针对性的意向分析、成交卡点、后续跟进计划以及意向等级并以json格式返回：
    {customer_info}
    返回结果应包含以下字段：
    - "成交卡点分析": 列表，每个元素包含卡点和详细说明
    - "后续跟进计划": 列表，每个元素包含时间、内容、方式
    - "意向分析": 字符串，分析客户的意向情况
    - "意向等级": 字符串，表示客户的意向等级
    以严格的可直接处理的JSON字符串格式输出。
     意向等级包括：
        A - 认购
        B - 高意向
        C - 一般意向
        D - 低意向
        E - 无意向
    - 后续跟进计划最好能直接对应一个或多个成交卡点，同时要针对客户的具体情况，要提出切实可行的行动方案。
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        # print("API响应内容:", response.choices[0].message.content)  # 打印API响应内容
        api_response = response.choices[0].message.content
        # 移除响应内容中的多余字符
        api_response = api_response.strip().replace('```json', '').replace('```', '')
        try:
            # 尝试将API响应解析为JSON
            response_json = json.loads(api_response)
            return json.dumps(response_json, ensure_ascii=False)
        except json.JSONDecodeError as e:
            print(f"调用通义千问 API 生成建议、计划和意向等级时解析API响应为JSON时出错: {e}")
            return "{}"
    except Exception as e:
        print(f"调用通义千问 API 生成建议、计划和意向等级时出错: {e}")
        return "{}"

# 调用通义千问 API 提取 对比项目 和 未成交抗性
def extract_model(customer_data, field):
    customer_info = "客户白描:\n"
    memo_value = customer_data.get('memo', '')  # 使用get方法安全地获取memo的值，如果不存在则返回空字符串
    if memo_value:
        customer_info += f"{memo_value}\n"
    else:
        # 如果memo字段为空，直接返回未知
        return json.dumps({field: "未知"}, ensure_ascii=False)

    prompt = f"""
    根据以下客户的白描信息，提取出 {field} 并以json格式返回：
    {customer_info}
    返回结果应包含以下字段：
    - "{field}": 字符串，表示房地产领域的相应字段信息
    以严格的可直接处理的JSON字符串格式输出。
    - 若确实无法从客户白描中提取到相应字段，将该字段赋值为 '未知' 后返回。
    请直接返回JSON格式的数据，不需要其他提示信息。
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        api_response = response.choices[0].message.content
        # 打印API响应以进行调试
        print(f"API响应: {api_response}")
        
        # 移除响应内容中的多余字符
        api_response = api_response.strip().replace('```json', '').replace('```', '')
        
        if not api_response:
            print("API响应为空")
            return json.dumps({field: "未知"}, ensure_ascii=False)

        try:
            # 尝试将API响应解析为JSON
            response_json = json.loads(api_response)
            return json.dumps(response_json, ensure_ascii=False)
        except json.JSONDecodeError as e:
            print(f"调用通义千问 API 提取对比项目和未成交抗性 解析API响应为JSON时出错: {e}")
            return json.dumps({field: "未知"}, ensure_ascii=False)
    except Exception as e:
        print(f"调用通义千问 API 提取对比项目和未成交抗性时出错: {e}")
        return json.dumps({field: "未知"}, ensure_ascii=False)

# 获取 对比项目 字段
def get_comparison_projects(customer):
    comparison_projects = customer.get('memo1', '')
    if not comparison_projects:
        # 调用extract_model前检查memo1是否为空
        comparison_projects_response = extract_model(customer, '对比项目')
        if comparison_projects_response:
            comparison_projects_data = json.loads(comparison_projects_response)
            comparison_projects = comparison_projects_data.get('对比项目', '未知')
    return comparison_projects

# 获取 未成交抗性 字段
def get_non_deal_resistance(customer):
    abandon_reason = customer.get('abandon_reason', '')
    notbuyreason = customer.get('notbuyreason', '')
    if abandon_reason and notbuyreason:
        non_deal_resistance = abandon_reason + " " + notbuyreason
    elif abandon_reason or notbuyreason:
        non_deal_resistance = abandon_reason or notbuyreason
    else:
        non_deal_resistance_response = extract_model(customer, '未成交抗性')
        if non_deal_resistance_response:
            non_deal_resistance_data = json.loads(non_deal_resistance_response)
            non_deal_resistance = non_deal_resistance_data.get('未成交抗性', '未知')
    return non_deal_resistance

# 连接数据库查询客户信息
def query_customer_info(saleropenid):
    connection = psycopg2.connect(dbname="fdc_dc",
                                  user="dws_user_hwai",
                                  password="NewHope#1982@",
                                  host="124.70.57.67",
                                  client_encoding='UTF8',
                                  port="8000")
    print("连接DWS数据库成功！")

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            sql = """
            WITH ranked_customers AS (
                SELECT 
                    u.id, u.createtime, u.username, u.age, u.familystructure, u.mobile, 
                    u.qualified, u.visitcounts, u.budget, u.customerresource, u.mymttj, u.work, u.live, u.industry, u.jobs,
                    u.house, u.purpose, u.floor, u.interest, u.userrank, u.memo , u.saleropenid,
                    u.buyuse, u.dealway, u.channel, u.unitprice, u.customerchannel,  u.customer_id, u.income,
                    u.area, u.visitamount, u.memo1, u.abandon_reason, u.notbuyreason, u.layouttype, u.buyfactor, u.interestlayout,
                    ROW_NUMBER() OVER (PARTITION BY u.username, u.mobile ORDER BY u.createtime DESC) as row_num
                FROM 
                    fdc_ods.ods_qw_market_dh_crm_saleruser u
                WHERE 
                    u.saleropenid = %s AND u.createtime >= CURRENT_DATE - INTERVAL '3 month' AND u.createtime < CURRENT_DATE + INTERVAL '1 day'
                    AND u.partitiondate >= CURRENT_DATE - INTERVAL '1 day' AND u.partitiondate < CURRENT_DATE + INTERVAL '1 day'
            )
            SELECT 
                id, createtime, username, age, familystructure, mobile, 
                qualified, visitcounts, budget, customerresource, mymttj, work, live, industry, jobs,
                house, purpose, floor, interest,  userrank, memo , saleropenid,
                buyuse, dealway, channel, unitprice, customerchannel,  customer_id, income,
                area, visitamount, memo1 , abandon_reason, notbuyreason, layouttype, buyfactor, interestlayout,
                row_num
            FROM 
                ranked_customers
            WHERE 
                row_num = 1
                ;
            """
            cursor.execute(sql, (saleropenid,))
            result = cursor.fetchall()
            print(f"查询客户信息成功！")
            return result
    except Exception as e:
        print(f"查询客户信息时出错: {e}")
        return []
    finally:
        connection.close()

# 连接数据库查询来访人数信息[暂时不使用查询的方式；改用计数的方式]
def query_visitornum_info():
    connection = psycopg2.connect(dbname="fdc_dc",
                                  user="dws_user_hwai",
                                  password="NewHope#1982@",
                                  host="124.70.57.67",
                                  client_encoding='UTF8',
                                  port="8000")
    print("连接DWS数据库成功！")

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # TODO  在大量数据条目中区分特定的来访信息的逻辑待给出
            sql = """
                SELECT 
                visitornum,
                newvisitornum,
                revisitornum
            FROM 
                fdc_ads.ads_salesreport_visitweekanalyse_a_min
            WHERE 
                statdate = current_date
                AND orgcode = 'FCSYGS001' --先写死 项目代号，目前缺乏实现流程的逻辑
            ORDER BY 
                statdate DESC -- 通常statdate是日期类型,所以按降序排列最新的会在最前面
            LIMIT 1; -- 限制结果集只返回一条记录
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            print(f"查询来访人数信息成功！")
            return result
    except Exception as e:
        print(f"查询来访人数信息时出错: {e}")
        return []
    finally:
        connection.close()

# 从CSV文件中读取数据并建立销售人员ID和姓名、项目名的映射关系
def build_saler_map_from_csv(file_path):
    saler_map1 = {}
    saler_map2 = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            saler_id = row['saler_id']
            saler_name = row['saler_name']
            project_name = row['project_name']
            saler_map1[saler_id] = saler_name
            saler_map2[saler_id] = project_name
    return saler_map1 , saler_map2

# 生成 json 形式的报告
def generate_json_report(customers):

    # 设置存储销售人员信息的csv文件的系统路径并构建映射关系
    role_csv_file_path = 'role.csv'
    saler_map1,saler_map2 = build_saler_map_from_csv(role_csv_file_path)

    visitornum = 0  # 来访客户总数
    newvisitornum = 0  # 新增来访客户数
    revisitornum = 0  # 复访客户数

    report = {
        "来访客户": visitornum,
        "新增来访": newvisitornum,
        "复访客户": revisitornum,
        "新访": [],
        "复访":[],
        "高意向客户":[]
    }

    for customer in customers:
        visitornum += 1  # 来访客户数加1
        # 从映射关系中获取销售人员姓名+项目名字
        saler_name = saler_map1.get(customer.get('saleropenid', '未知'), '未知')
        project_name = saler_map2.get(customer.get('saleropenid','未知'),'未知')
        # 从来访次数字段判断是新访、复访
        # 确保 visitamount 是整数类型
        visitamount = int(customer.get('visitamount', 0))
        # 通过RAG模型判断向量化的历史相似客户案例
        new_customer_description = f"购房用途：{customer['buyuse']}，意向面积：{customer['area']}，家庭构成：{customer['familystructure']}，预算：{customer['budget']}，购房关注点：{customer['interest']}，客户简介：{customer['memo']}，用户评级：{customer['userrank']}。"
        similar_customer = find_similar_customers(new_customer_description, knowledge_base, historical_data)
        # 获取 对比项目 字段和 未成交抗性
        comparison_projects =get_comparison_projects(customer)
        non_deal_resistance = get_non_deal_resistance(customer)
        # 调用大模型API获取意向分析、成交卡点、后续跟进计划以及意向等级
        suggestions_and_rank = generate_model_suggestions_and_rank(customer)
        print("API返回了一条顾客的JSON数据")  # 打印API调用信息{可以用 suggestions_and_rank}

        try:
            # 尝试将API返回的JSON字符串解析为Python字典
            suggestions_and_rank_data = json.loads(suggestions_and_rank)
        except json.JSONDecodeError as e:
            print(f"解析API返回的JSON数据时出错: {e}")
            continue

        # 确保suggestions_and_rank_data包含所需的字段：意向等级
        if  "意向等级" in suggestions_and_rank_data:

            intent_level = suggestions_and_rank_data["意向等级"]
            # 使用正则表达式从意向等级中提取字母部分
            intent_level_code = re.sub(r'[^A-Z]', '', intent_level)
            # 符合高意向客户的标准，则添加进高意向客户JSON键
            if intent_level_code in ["A", "B"]:
                customer_report = {
                    "序号": customer.get('id','未知'),
                    "日期":customer.get('createtime','未知'),
                    "项目名称":project_name,
                    "置业顾问ID": customer.get('saleropenid', '未知'),
                    "置业顾问姓名":saler_name,
                    "客户姓名": customer.get('username', '未知'),  
                    "意向度": customer.get('userrank', '未知'),
                    "高意向分析":suggestions_and_rank_data.get("意向分析", "未知"),
                    "年龄": customer.get('age', '未知'),  
                    "家庭结构": customer.get('familystructure', '未知'),
                    "电话": customer.get('mobile', '未知'),                      
                    "客户来源(前台咨客录入的来源)": customer.get('customerresource', '未知'),
                    "需求户型": customer.get('purpose', '未知'),
                    "意向楼栋": customer.get('floor', '未知'),
                    "意向房源一": customer.get('layouttype', '未知'),
                    "意向房源二": customer.get('buyfactor', '未知'),
                    "客户关注点": customer.get('interest', '未知'),
                    "客户对项目满意点": customer.get('interestlayout', '未知'),
                    "对比项目": comparison_projects,                   
                    "未成交抗性": non_deal_resistance,
                    "未成交原因分类": customer.get('abandon_reason', '未知'),                   
                    "意向等级": intent_level,
                    "客户白描": customer.get('memo', '未知'),
                    "历史相似客户": similar_customer,
                    "成交卡点": suggestions_and_rank_data.get("成交卡点分析", []),  
                    "跟进建议": suggestions_and_rank_data.get("后续跟进计划", [])
                }

                report["高意向客户"].append(customer_report)

            if  visitamount == 0:
                newvisitornum += 1  # 新增来访客户数加1
                customer_report = {
                    "序号": customer.get('id','未知'),
                    "日期":customer.get('createtime','未知'),
                    "项目名称":project_name,
                    "置业顾问ID": customer.get('saleropenid', '未知'),
                    "置业顾问姓名":saler_name,
                    "客户姓名": customer.get('username', '未知'),  
                    "年龄": customer.get('age', '未知'),  
                    "家庭结构": customer.get('familystructure', '未知'),
                    "电话": customer.get('mobile', '未知'),  
                    "是否具有购房资格": customer.get('qualified', '未知'),
                    "置业次数": customer.get('visitcounts', '未知'),
                    # 假设正确的首付预算键名为 'downpayment_budget'
                    "首付预算": customer.get('downpayment_budget', '待定'),
                    "总价预算": customer.get('budget', '未知'),  
                    "客户来源": customer.get('customerresource', '未知'),
                    "认知途径": customer.get('mymttj', '未知'),
                    "工作区域": customer.get('work', '未知'),
                    "居住区域": customer.get('live', '未知'),
                    "行业": customer.get('industry', '未知'),
                    "职务": customer.get('jobs', '未知'),
                    "目前居住的面积": customer.get('house', '未知'),
                    "需求户型": customer.get('purpose', '未知'),
                    "意向楼栋": customer.get('floor', '未知'),
                    # 假设正确的意向房源一键名
                    "意向房源一": customer.get('layouttype', '待定'),
                    # 假设正确的意向房源二键名
                    "意向房源二": customer.get('buyfactor', '待定'),
                    "客户关注点": customer.get('interest', '未知'),
                    # 假设正确的客户对项目满意点键名
                    "客户对项目满意点": customer.get('interestlayout', '待定'),
                    "对比项目": comparison_projects,
                    "未成交抗性": non_deal_resistance,
                    # 假设正确的未成交原因分类键名
                    "未成交原因分类": customer.get('abandon_reason', '待定'),
                    "意向等级": intent_level,
                    "客户白描": customer.get('memo', '未知'),  
                    "跟进建议": suggestions_and_rank_data.get("后续跟进计划", [])
                }

                report["新访"].append(customer_report)

            elif visitamount >= 1:
                revisitornum += 1  # 复访客户数加1
                customer_report = {
                    "序号": customer.get('id','未知'),
                    "日期":customer.get('createtime','未知'),
                    "项目名称":project_name,
                    "置业顾问ID": customer.get('saleropenid', '未知'),
                    "置业顾问姓名":saler_name,
                    "客户姓名": customer.get('username', '未知'),  
                    "年龄": customer.get('age', '未知'),  
                    "家庭结构": customer.get('familystructure', '未知'),
                    "电话": customer.get('mobile', '未知'),  
                    "是否具有购房资格": customer.get('qualified', '未知'),
                    "置业次数": customer.get('visitcounts', '未知'),
                    # 假设正确的首付预算键名为 'downpayment_budget'
                    "首付预算": customer.get('downpayment_budget', '待定'),
                    "总价预算": customer.get('budget', '未知'),  
                    "客户来源": customer.get('customerresource', '未知'),
                    "认知途径": customer.get('mymttj', '未知'),
                    "工作区域": customer.get('work', '未知'),
                    "居住区域": customer.get('live', '未知'),
                    "行业": customer.get('industry', '未知'),
                    "职务": customer.get('jobs', '未知'),
                    "目前居住的面积": customer.get('house', '未知'),
                    "需求户型": customer.get('purpose', '未知'),
                    "意向楼栋": customer.get('floor', '未知'),
                    # 假设正确的意向房源一键名
                    "意向房源一": customer.get('layouttype', '待定'),
                    # 假设正确的意向房源二键名
                    "意向房源二": customer.get('buyfactor', '待定'),
                    "客户关注点": customer.get('interest', '未知'),
                    # 假设正确的客户对项目满意点键名
                    "客户对项目满意点": customer.get('interestlayout', '待定'),
                    "对比项目": comparison_projects,
                    "未成交抗性": non_deal_resistance,
                    # 假设正确的未成交原因分类键名
                    "未成交原因分类": customer.get('abandon_reason', '待定'),
                    "意向等级": intent_level,
                    "客户白描": customer.get('memo', '未知'),  
                    "跟进建议": suggestions_and_rank_data.get("后续跟进计划", [])
                }

                report["复访"].append(customer_report)
    
    report["来访客户"] = visitornum
    report["新增来访"] = newvisitornum
    report["复访客户"] = revisitornum

    return report
