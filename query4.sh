#!/bin/bash

# 设置为 UTF-8 编码
export LANG=en_US.UTF-8

# 硬编码的参数
ROLEID="2015"
PROJECTID="8194"
START_DATE="2023-05-11 00:00:00"
END_DATE="2023-05-11 23:59:59"

# 发送带有硬编码参数的 POST 请求
curl -X POST http://127.0.0.1:45108/analysis \
     -H "Content-Type: application/json" \
     -d "{\"roleId\": \"$ROLEID\", \"projectId\": \"$PROJECTID\", \"start_date\": \"$START_DATE\", \"end_date\": \"$END_DATE\"}"