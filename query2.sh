#!/bin/bash

# 设置为 UTF-8 编码
export LANG=en_US.UTF-8

# 提示用户输入 saleropenid, start_date 和 end_date
read -p "请输入置业顾问ID（saleropenid）: " SALEROPENID
read -p "请输入开始日期（YYYY-MM-DD）: " START_DATE
read -p "请输入结束日期（YYYY-MM-DD）: " END_DATE

# 发送带有输入参数的 POST 请求
curl -X POST http://127.0.0.1:45102/analysis \
     -H "Content-Type: application/json" \
     -d "{\"saleropenid\": \"$SALEROPENID\", \"start_date\": \"$START_DATE\", \"end_date\": \"$END_DATE\"}"
