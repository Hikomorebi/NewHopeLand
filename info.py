import psycopg2
from psycopg2.extras import RealDictCursor
from transformers import AutoTokenizer, AutoModel
import torch
import pickle
from utils import get_resource_path

# 定义均值池化函数
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# 获取 models 文件夹的路径
models_path = get_resource_path('models')

# 加载分词器和模型
tokenizer = AutoTokenizer.from_pretrained(models_path + '/paraphrase-MiniLM-L6-v2')
model = AutoModel.from_pretrained(models_path + '/paraphrase-MiniLM-L6-v2')

# 连接数据库查询历史相似客户信息
def query_history_customer_info():
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
                WHERE partitiondate >= CURRENT_DATE 
                AND partitiondate < CURRENT_DATE + INTERVAL '1 day'
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
            print(f"查询历史相似客户信息成功！")
            return result
    except Exception as e:
        print(f"查询历史相似客户信息时出错: {e}")
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

# 将自然语言描述转换为向量（支持长文本分段处理）
def convert_to_embeddings(descriptions):
    embeddings_list = []
    for description in descriptions:
        if not description:  # 检查描述是否为空
            continue
        # 分割文本为多个段落，每个段落不超过512个token
        encoded_segments = tokenizer(
            description,
            max_length=512,
            truncation=True,
            padding=True,
            return_tensors='pt',
            return_overflowing_tokens=True,  # 返回溢出的token（如果有的话）
            is_split_into_words=False  # 根据字符而不是单词分割（对于中文很重要）
        )
        
        # 处理所有段落
        for segment in encoded_segments.input_ids:
            attention_mask = (segment != tokenizer.pad_token_id).float().unsqueeze(0)  # 创建attention mask
            with torch.no_grad():
                model_output = model(segment.unsqueeze(0), attention_mask=attention_mask)  # 添加batch维度
            segment_embedding = mean_pooling(model_output, attention_mask)
            embeddings_list.append(segment_embedding)
        
        # 如果文本被分割成了多个段落，我们需要合并这些段落的嵌入
        # 这里我们简单地使用平均池化来合并
        if len(encoded_segments.input_ids) > 1:
            final_embedding = torch.mean(torch.stack(embeddings_list[-len(encoded_segments.input_ids):]), dim=0)
            embeddings_list[-len(encoded_segments.input_ids):] = [final_embedding]  # 用合并后的嵌入替换段落嵌入
            embeddings_list = embeddings_list[:-len(encoded_segments.input_ids) + 1]  # 移除旧的段落嵌入
    
    # 确保 embeddings_list 不是空的
    if not embeddings_list:
        raise ValueError("embeddings_list is empty, please check the input data.")
    
    # 返回所有描述的嵌入列表（或根据需要进一步处理）
    return torch.stack(embeddings_list)
 
# 对新数据进行向量化并匹配
def find_similar_customers(new_description, embeddings, historical_data):
    # 分割并处理新描述（与convert_to_embeddings中的处理相同）
    encoded_segments = tokenizer(
        new_description,
        max_length=512,
        truncation=True,
        padding=True,
        return_tensors='pt',
        return_overflowing_tokens=True,
        is_split_into_words=False
    )
    new_embedding_list = []
    for segment in encoded_segments.input_ids:
        attention_mask = (segment != tokenizer.pad_token_id).float().unsqueeze(0)
        with torch.no_grad():
            model_output = model(segment.unsqueeze(0), attention_mask=attention_mask)
        segment_embedding = mean_pooling(model_output, attention_mask)
        new_embedding_list.append(segment_embedding)
    
    # 合并新描述的段落嵌入（同样使用平均池化）
    if len(new_embedding_list) > 1:
        new_embedding = torch.mean(torch.stack(new_embedding_list), dim=0)
    else:
        new_embedding = new_embedding_list[0]
    
    # 计算相似度并找到最相似的历史客户
    similarities = torch.cosine_similarity(new_embedding, embeddings)
    most_similar_index = torch.argmax(similarities).item()
    return historical_data[most_similar_index]


