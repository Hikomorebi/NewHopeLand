def match_metric(sentence, metrics):
    # 按照长度从大到小排序
    metrics.sort(key=len, reverse=True)
    
    # 遍历指标列表，找到第一个匹配的指标
    for metric in metrics:
        if metric in sentence:
            return metric  # 返回匹配到的指标名称
    
    return None  # 如果没有匹配到，则返回None
metrics = ["首访客户数", "新增签约面积", "签约面积"]
sentence = "本月的新增签约面积增长显著。"
matched_metric = match_metric(sentence, metrics)
print(matched_metric)  # 输出：新增签约面积
