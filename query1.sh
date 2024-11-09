#!/bin/bash

# 获取所有传递给脚本的参数
QUERY="$@"

# 使用curl发送POST请求
curl -X POST http://127.0.0.1:45104/chat -H "Content-Type: application/json" -d "{\"query\": \"$QUERY\"}"