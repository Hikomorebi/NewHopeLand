#!/bin/bash

# 设置为 UTF-8 编码
export LANG=en_US.UTF-8

# 提示用户输入 saler_id, role_name
read -p "请输入置业顾问ID（saler_id）: " SALER_ID
read -p "请输入角色身份（role_name）: " ROLE_NAME

# 发送带有输入参数的 POST 请求
curl -X POST http://127.0.0.1:45108/analysis \
     -H "Content-Type: application/json" \
     -d "{\"saler_id\": \"$SALER_ID\", \"role_name\": \"$ROLE_NAME\"}"
