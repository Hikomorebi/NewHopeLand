#!/bin/bash

# 设置为 UTF-8 编码
export LANG=en_US.UTF-8

# 硬编码的参数
SALEROPENID="oFUZO5wGVxMiyR6vAo3E-ycTZM8s"
SUBORDINATEID="oFUZO52c2dZ0j5y9U8ijsPN8pQzQ,oFUZO54NVrk8uFDYwwMS6SJvCwek,oFUZO56QZhwcA4_xZo4-5ygYuDfo,oFUZO59OLy-cp8VUjwqWiJEvD77k,oFUZO5_yyAXOdRPURK8Xs7jFHDqI"
PROJECTID="8138"
PROJECTNAME="杭州区域公司锦麟天樾"
START_DATE="2024-11-18 12:00:00"
END_DATE="2024-11-20 11:59:59"

# 发送带有硬编码参数的 POST 请求
curl -X POST http://127.0.0.1:45108/analysis \
     -H "Content-Type: application/json" \
     -d "{\"saleropenid\": \"$SALEROPENID\", \"subordinateId\": \"$SUBORDINATEID\", \"projectId\": \"$PROJECTID\", \"projectName\": \"$PROJECTNAME\", \"start_date\": \"$START_DATE\", \"end_date\": \"$END_DATE\"}"