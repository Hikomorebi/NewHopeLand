#!/bin/bash

# 设置为 UTF-8 编码
export LANG=en_US.UTF-8

# 提示用户输入必要的参数
read -p "请输入查询人员的id（saleropenid）: " SALEROPENID
read -p "请输入查询人员所属的id（格式为字符串：ID1,ID2,ID3....）: " SUBORDINATEID
read -p "请输入项目ID（projectId）: " PROJECTID
read -p "请输入项目名称（projectName）: " PROJECTNAME
read -p "请输入开始时间（start_date）: " START_DATE
read -p "请输入结束时间（end_date）: " END_DATE

# 发送带有输入参数的 POST 请求
curl -X POST http://127.0.0.1:45108/analysis \
     -H "Content-Type: application/json" \
     -d "{\"saleropenid\": \"$SALEROPENID\", \"subordinateId\": \"$SUBORDINATEID\", \"projectId\": \"$PROJECTID\", \"projectName\": \"$PROJECTNAME\", \"start_date\": \"$START_DATE\", \"end_date\": \"$END_DATE\"}"