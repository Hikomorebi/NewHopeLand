#!/bin/bash

# 设置为 UTF-8 编码
export LANG=en_US.UTF-8

# 硬编码的参数
SALEROPENID="oFUZO5yshoBg2hon0orI7vpaHhe0"
ROLEID="2011"
PROJECTID="8194"
START_DATE="2024-12-02 00:00:00"
END_DATE="2024-12-03 23:59:59"

# 发送带有硬编码参数的 POST 请求
curl -X POST http://127.0.0.1:45108/analysis \
     -H "Content-Type: application/json" \
     -d "{\"saleropenid\": \"$SALEROPENID\",\"roleid\": \"$ROLEID\", \"projectId\": \"$PROJECTID\",  \"start_date\": \"$START_DATE\", \"end_date\": \"$END_DATE\"}"