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
few_shot_examples = """
根据以下客户的基本信息，生成有针对性地成交卡点、建议应对措施、后续跟进计划以及意向等级：
客户基本信息:
接待销售: 徐聪
来访渠道: 58爱房
客户姓名: 邹小姐
首复访: 首次复访
年龄: 53
诚意度: C
家庭人数: 6
置业次数: 首次
意向面积: 117
预期价格: 240万
预期折扣: 71
首付预算: 100万
关注点1: 价格
关注点2: 教育配套
对比竞品: 岛内其他二手
未成交原因: 价格
客户情况补充: 客户带儿子回来复访，意向5-1103，心理预期比较低，想着230万买，后面拉到240万，价格合适会买。
最新跟进反馈: 已买5-1103

意向等级: A

根据以下客户的基本信息，生成有针对性地成交卡点、建议应对措施、后续跟进计划以及意向等级：
客户基本信息:
接待销售: 黄泽锋
来访渠道: 贝壳
客户姓名: 吴小姐
首复访: 首访
年龄: 37
诚意度: C
家庭人数: 3
置业次数: 二次
意向面积: 85
预期价格: 175万
预期折扣: 72
首付预算: 100万
关注点1: 价格
关注点2: 户型
对比竞品: 周边二手
未成交原因: 版块未定
客户情况补充: 客户主要国外生活，偶然回来居住下，没有迫切的购房需求，需求三房一卫，意向85方，有钱，想多看。
最新跟进反馈: 8.8 客户觉得小区一般，有朋友告知附近有墓园，不考虑，和中介多次沟通邀约无复访。8.23不考虑

意向等级: C

根据以下客户的基本信息，生成有针对性地成交卡点、建议应对措施、后续跟进计划以及意向等级：
客户基本信息:
接待销售: 黄泽锋
来访渠道: 贝壳
客户姓名: 侯先生
首复访: 首访
年龄: 40
诚意度: D
家庭人数: 4
置业次数: 首套
意向面积: 117
预期价格: 235万
预期折扣: 67
首付预算: 20万
关注点1: 地段
关注点2: 教育
对比竞品: 广佛都看
未成交原因: 佛山地段，价格，小区素质
客户情况补充: 客户心理预期在2万，槎头个体户，想低首付买117方，对比广洲和佛山，目前觉得价格不值得，户型不满意。
最新跟进反馈: 8.8 暂时不看楼盘，未来预期低，预算不足 8.23不考虑

意向等级: D

根据以下客户的基本信息，生成有针对性地成交卡点、建议应对措施、后续跟进计划以及意向等级：
客户基本信息:
接待销售: 李伟
来访渠道: 安居客
客户姓名: 王先生
首复访: 首访
年龄: 45
诚意度: A
家庭人数: 3
置业次数: 二次
意向面积: 95
预期价格: 200万
预期折扣: 75
首付预算: 150万
关注点1: 交通
关注点2: 周边配套
对比竞品: 同区域其他楼盘
未成交原因: 无
客户情况补充: 客户之前有过购房经验，明确表示对该楼盘非常感兴趣，首付预算充足，计划尽快购买。
最新跟进反馈: 客户已签约，预计下周完成支付。

意向等级: A

根据以下客户的基本信息，生成有针对性地成交卡点、建议应对措施、后续跟进计划以及意向等级：
客户基本信息:
接待销售: 张丽
来访渠道: 自然来访
客户姓名: 李女士
首复访: 首访
年龄: 29
诚意度: B
家庭人数: 4
置业次数: 首次
意向面积: 120
预期价格: 250万
预期折扣: 70
首付预算: 80万
关注点1: 学区
关注点2: 小区环境
对比竞品: 附近新楼盘
未成交原因: 价格有待商议
客户情况补充: 客户对学区要求高，有两个小孩需要上学，对小区的环境非常满意，但希望价格可以再优惠一些。
最新跟进反馈: 客户已表示有较强购房意向，等待价格商议结果。

意向等级: B
"""


# 调用通义千问 API 生成建议、计划和意向等级
def generate_model_suggestions_and_rank(customer_data):
    customer_info = "客户基本信息:\n"
    for key, value in customer_data.items():
        customer_info += f"{key}: {value}\n"

    prompt = f"""
    {few_shot_examples}
    根据以下客户的基本信息，生成有针对性地成交卡点、建议应对措施、后续跟进计划以及意向等级：
    {customer_info}
    意向等级包括：
    A - 认购
    B - 高意向
    C - 一般意向
    D - 低意向
    E - 无意向
    - 在建议应对措施中，请确保每一条建议都直接对应一个或多个成交卡点，并且针对客户的具体情况，避免使用泛泛而谈的建议。
    - 后续跟进计划也应针对客户的特定需求，提出切实可行的行动方案。
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
                    LIMIT 3;                      
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
