#!/bin/bash

# 设置为 UTF-8 编码
export LANG=en_US.UTF-8

# 硬编码的参数
SALEROPENID="oFUZO57eMpMCI2O4h5ZTiGE1RTVM"
SUBORDINATEID="oFUZO51esaK4QDcAePI3IAN9mSs0,oFUZO53aAk3s2FGGFVUC2oPe7ZC0,oFUZO53GCr93Bqk3-OhHaaCGFvvs,oFUZO53LLUvrTll_gzns-2bSVjtY,oFUZO53PyR2CCkfsZfylBEc9xVvI,oFUZO56YalREOqCWlSFf8HC9Dj_s,oFUZO58W913Dj9AB4Lr8e5DshkhA,oFUZO59YJb0iiay8ddeU_kQLzDVo,oFUZO5xjncHG7vHXMk83lC2fxiCs"
PROJECTID="8159"
PROJECTNAME="华南区域公司南宁锦麟玖玺"
START_DATE="2024-10-05 00:00:00"
END_DATE="2024-10-05 23:59:59"

# 发送带有硬编码参数的 POST 请求
curl -X POST http://127.0.0.1:45108/analysis \
     -H "Content-Type: application/json" \
     -d "{\"saleropenid\": \"$SALEROPENID\", \"subordinateId\": \"$SUBORDINATEID\", \"projectId\": \"$PROJECTID\", \"projectName\": \"$PROJECTNAME\", \"start_date\": \"$START_DATE\", \"end_date\": \"$END_DATE\"}"