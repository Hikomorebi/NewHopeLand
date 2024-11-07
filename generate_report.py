import os
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor

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
    根据以下客户的基本信息，生成有针对性的成交卡点、后续跟进计划以及意向等级：
    {customer_info}
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
        print(f"调用 API 成功！")
        return response.choices[0].message.content
    except Exception as e:
        print(f"调用 API 时出错: {e}")
        return "未能生成建议。"

# 连接数据库查询客户信息
def query_customer_info(saleropenid, start_date, end_date):
    connection = psycopg2.connect(dbname="fdc_dc",
                                  user="dws_user_hwai",
                                  password="NewHope#1982@",
                                  host="124.70.57.67",
                                  client_encoding='UTF8',
                                  port="8000")
    print("连接成功！")

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # 数据库中存在相同客户的多条数据，只返回同一客户的最新记录
            sql = """
                    WITH ranked_customers AS (
                        SELECT 
                            username, mobile, channel, live, work, income, house, purpose,
                            position, floor, area, buyuse, familystructure, dealway,
                            interestlayout, propcondition, intentprice, liveaddress,
                            workaddress, interest, memo, usersrc, budget, visitcounts,
                            userrank, mymttj, unitprice, notbuyreason, customerchannel,
                            jobs, qq, wechat, memo1, customer_id, customerresource,
                            ROW_NUMBER() OVER (PARTITION BY username, mobile ORDER BY createtime DESC) as row_num
                        FROM 
                            fdc_ods.ods_qw_market_dh_crm_saleruser
                        WHERE 
                            saleropenid = %s AND createtime BETWEEN %s AND %s
                    )
                    SELECT 
                        username, mobile, channel, live, work, income, house, purpose,
                        position, floor, area, buyuse, familystructure, dealway,
                        interestlayout, propcondition, intentprice, liveaddress,
                        workaddress, interest, memo, usersrc, budget, visitcounts,
                        userrank, mymttj, unitprice, notbuyreason, customerchannel,
                        jobs, qq, wechat, memo1, customer_id, customerresource
                    FROM 
                        ranked_customers
                    WHERE 
                        row_num = 1
                    LIMIT 1;                      
            """
            cursor.execute(sql, (saleropenid, start_date, end_date))
            result = cursor.fetchall()
            print(f"查询客户信息成功！")
            return result
    except Exception as e:
        print(f"查询客户信息时出错: {e}")
        return []
    finally:
        connection.close()

# 生成 markdown 形式报告
def generate_markdown_report(customers, saleropenid):
    report = "# 高意向客户分析报告\n"
    report += f"## 置业顾问ID: {saleropenid}\n\n"

    for customer in customers:
        report += f"## Customer ID: {customer['customer_id']}\n"
        report += f"- **Username**: {customer['username']}\n"
        report += f"- **Mobile**: {customer['mobile']}\n"
        report += f"- **Channel**: {customer['channel']}\n"
        report += f"- **Live**: {customer['live']}\n"
        report += f"- **Work**: {customer['work']}\n"
        report += f"- **Income**: {customer['income']}\n"
        report += f"- **House**: {customer['house']}\n"
        report += f"- **Purpose**: {customer['purpose']}\n"
        report += f"- **Position**: {customer['position']}\n"
        report += f"- **Floor**: {customer['floor']}\n"
        report += f"- **Area**: {customer['area']}\n"
        report += f"- **Buy Use**: {customer['buyuse']}\n"
        report += f"- **Family Structure**: {customer['familystructure']}\n"
        report += f"- **Deal Way**: {customer['dealway']}\n"
        report += f"- **Interest Layout**: {customer['interestlayout']}\n"
        report += f"- **Property Condition**: {customer['propcondition']}\n"
        report += f"- **Intent Price**: {customer['intentprice']}\n"
        report += f"- **Live Address**: {customer['liveaddress']}\n"
        report += f"- **Work Address**: {customer['workaddress']}\n"
        report += f"- **Interest**: {customer['interest']}\n"
        report += f"- **Memo**: {customer['memo']}\n"
        report += f"- **User Source**: {customer['usersrc']}\n"
        report += f"- **Budget**: {customer['budget']}\n"
        report += f"- **Visit Counts**: {customer['visitcounts']}\n"
        report += f"- **User Rank**: {customer['userrank']}\n"
        report += f"- **Recommended**: {customer['mymttj']}\n"
        report += f"- **Unit Price**: {customer['unitprice']}\n"
        report += f"- **Not Buy Reason**: {customer['notbuyreason']}\n"
        report += f"- **Customer Channel**: {customer['customerchannel']}\n"
        report += f"- **Jobs**: {customer['jobs']}\n"
        report += f"- **QQ**: {customer['qq']}\n"
        report += f"- **WeChat**: {customer['wechat']}\n"
        report += f"- **Memo1**: {customer['memo1']}\n"
        report += f"- **Customer Resource**: {customer['customerresource']}\n"

        # 调用大模型生成建议和意向等级
        suggestions_and_rank = generate_model_suggestions_and_rank(customer)
        report += suggestions_and_rank + "\n\n"

    return report


def main():
    saleropenid = input("请输入置业顾问ID: ")
    start_date = input("请输入起始日期 (格式: YYYY-MM-DD): ")
    end_date = input("请输入结束日期 (格式: YYYY-MM-DD): ")

    customers = query_customer_info(saleropenid, start_date, end_date)
    if not customers:
        print("未查询到相关客户信息。")
        return

    report = generate_markdown_report(customers, saleropenid)

    report_filename = f"高意向客户分析报告_{saleropenid}.md"
    with open(report_filename, "w", encoding="utf-8") as file:
        file.write(report)

    print(f"报告已生成并保存到 {report_filename}")


if __name__ == "__main__":
    main()
