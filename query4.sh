#!/bin/bash

# 设置为 UTF-8 编码
export LANG=en_US.UTF-8

# 硬编码的参数
SALEROPENID="oFUZO5y9WDfaH-JVkkchVCRuLfRo"
PROJECTID="8217"
PROJECTNAME="华东公司四季春晓"
START_DATE="2024-11-18 12:00:00"
END_DATE="2024-11-20 11:59:59"

# 发送带有硬编码参数的 POST 请求
curl -X POST http://127.0.0.1:45108/analysis \
     -H "Content-Type: application/json" \
     -d "{\"saleropenid\": \"$SALEROPENID\", \"projectId\": \"$PROJECTID\", \"projectName\": \"$PROJECTNAME\", \"start_date\": \"$START_DATE\", \"end_date\": \"$END_DATE\"}"