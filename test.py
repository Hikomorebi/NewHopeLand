from transformers import AutoTokenizer, AutoModel

# 模型名称
model_name = 'sentence-transformers/paraphrase-MiniLM-L6-v2'

# 下载模型和分词器到本地路径
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 保存模型到本地路径
local_path = './models/sentence-transformers/paraphrase-MiniLM-L6-v2'
tokenizer.save_pretrained(local_path)
model.save_pretrained(local_path)

print("模型和分词器下载并保存成功！")
