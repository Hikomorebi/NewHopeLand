# client.py
from flask import Flask, Response, request, jsonify
import requests
import traceback
from utils import dws_connect

app = Flask(__name__)

# 服务端地址
SERVER_URL = "http://47.109.178.240:45108"  
  
# 转发 /configure 请求到服务端
@app.route("/configure", methods=["POST"])
def configure():
    data = request.json
    response = requests.post(f"{SERVER_URL}/configure", json=data)
    return jsonify(response.json()), response.status_code

@app.route("/execute_sql", methods=["POST"])
def execute_sql():
    data = request.json
    sql_query = data.get("sql_query")
    key_fields = data.get("key_fields", None)
    display_type = data.get("display_type", "response_bar_chart")

    try:
        # 调用dws_connect执行SQL查询
        sql_exec_dict = dws_connect(sql_query, key_fields, display_type)
        
        # 返回查询结果
        return jsonify(sql_exec_dict)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": 0, "error_message": str(e)})

# 转发 /chat 请求到服务端
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    response = requests.post(f"{SERVER_URL}/chat", json=data, stream=True)
    return Response(response.iter_content(chunk_size=1024), content_type=response.headers['Content-Type'])

# 转发 /close 请求到服务端
@app.route("/close", methods=["POST"])
def close():
    data = request.json
    response = requests.post(f"{SERVER_URL}/close", json=data)
    return jsonify(response.json()), response.status_code

def client():
    app.run(threaded=True, host="0.0.0.0", port=45109)
    
if __name__ == "__main__":
    client()