import psycopg2
from psycopg2.extras import RealDictCursor
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

# 定义均值池化函数
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# 加载模型和分词器
tokenizer = AutoTokenizer.from_pretrained('./models/paraphrase-MiniLM-L6-v2')
model = AutoModel.from_pretrained('./models/paraphrase-MiniLM-L6-v2')

# 连接数据库查询历史相似客户信息
def query_customer_info():
    connection = psycopg2.connect(dbname="fdc_dc",
                                  user="dws_user_hwai",
                                  password="NewHope#1982@",
                                  host="124.70.57.67",
                                  client_encoding='UTF8',
                                  port="8000")
    print("连接成功！")

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            sql = """
                WITH ranked_customers AS (
                 SELECT 
                    username, 
                    createtime, 
                    saleropenid, 
                    mobile, 
                    channel, 
                    live, 
                    work, 
                    income, 
                    house, 
                    purpose,
                    position, 
                    floor, 
                    area, 
                    buyuse, 
                    familystructure, 
                    dealway,
                    interestlayout, 
                    propcondition, 
                    intentprice, 
                    liveaddress,
                    workaddress, 
                    interest, 
                    memo, 
                    usersrc, 
                    budget, 
                    visitcounts,
                    userrank, 
                    mymttj, 
                    unitprice, 
                    notbuyreason, 
                    customerchannel,
                    jobs, 
                    qq, 
                    wechat, 
                    memo1, 
                    customer_id, 
                    customerresource,
                    ROW_NUMBER() OVER (PARTITION BY username, mobile ORDER BY createtime DESC) as row_num,
                    -- 计算非空列的数量
                    (
                        (CASE WHEN username IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN createtime IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN saleropenid IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN mobile IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN channel IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN live IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN work IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN income IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN house IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN purpose IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN position IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN floor IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN area IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN buyuse IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN familystructure IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN dealway IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN interestlayout IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN propcondition IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN intentprice IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN liveaddress IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN workaddress IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN interest IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN memo IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN usersrc IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN budget IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN visitcounts IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN userrank IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN mymttj IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN unitprice IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN notbuyreason IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN customerchannel IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN jobs IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN qq IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN wechat IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN memo1 IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN customer_id IS NOT NULL THEN 1 ELSE 0 END) +
                        (CASE WHEN customerresource IS NOT NULL THEN 1 ELSE 0 END)
                    ) AS non_null_column_count
                FROM 
                    fdc_ods.ods_qw_market_dh_crm_saleruser
            ),
            filtered_customers AS (
                SELECT *
                FROM ranked_customers
                WHERE row_num = 1
                AND non_null_column_count >= 25
            )
            SELECT 
                username, 
                createtime, 
                saleropenid, 
                mobile, 
                channel, 
                live, 
                work, 
                income, 
                house, 
                purpose,
                position, 
                floor, 
                area, 
                buyuse, 
                familystructure, 
                dealway,
                interestlayout, 
                propcondition, 
                intentprice, 
                liveaddress,
                workaddress, 
                interest, 
                memo, 
                usersrc, 
                budget, 
                visitcounts,
                userrank, 
                mymttj, 
                unitprice, 
                notbuyreason, 
                customerchannel,
                jobs, 
                qq, 
                wechat, 
                memo1, 
                customer_id, 
                customerresource
            FROM 
                filtered_customers
            LIMIT 1000;
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            print(f"查询客户信息成功！")
            return result
    except Exception as e:
        print(f"查询客户信息时出错: {e}")
        return []
    finally:
        connection.close()

# 转换成自然语言
def data_to_natural_language(data):
    descriptions = []
    for item in data:
        description = f"购房用途：{item['buyuse']}，意向面积：{item['area']}，家庭构成：{item['familystructure']}，预算：{item['budget']}，购房关注点：{item['interest']}，客户简介：{item['memo']}，用户评级：{item['userrank']}。"
        descriptions.append(description)
    return descriptions

# 将自然语言描述转换为向量
def convert_to_embeddings(descriptions):
    encoded_inputs = tokenizer(descriptions, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_outputs = model(**encoded_inputs)
    sentence_embeddings = mean_pooling(model_outputs, encoded_inputs['attention_mask'])
    return sentence_embeddings

# 对新数据进行向量化并匹配
def find_similar_customers(new_description, embeddings, historical_data):
    encoded_input = tokenizer(new_description, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)
    new_embedding = mean_pooling(model_output, encoded_input['attention_mask'])
    similarities = torch.cosine_similarity(new_embedding, embeddings)
    most_similar_index = torch.argmax(similarities).item()
    return historical_data[most_similar_index]

# 查询历史客户信息
historical_data = query_customer_info()

# 转换历史数据为自然语言描述
historical_descriptions = data_to_natural_language(historical_data)

# 将自然语言描述转换为向量
knowledge_base = convert_to_embeddings(historical_descriptions)

# 新的客户信息转为自然语言描述
new_customer_description = "购房用途：投资，意向面积：120平米，家庭构成：三口之家，预算：200万，购房关注点：学区房，客户简介：无，用户评级：A。"

# 查找与新客户信息最相似的历史客户
similar_customer = find_similar_customers(new_customer_description, knowledge_base, historical_data)

# 输出匹配结果
print("最相似的历史客户信息：", similar_customer)