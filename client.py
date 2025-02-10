# client.py
from flask import Flask, Response, request, jsonify
import requests
import json

app = Flask(__name__)

# 服务端地址
# SERVER_URL = "http://47.109.178.240:45108"  
SERVER_URL = "http://localhost:45108"  
# 转发 /configure 请求到服务端
@app.route("/configure", methods=["POST"])
def configure():
    data = request.json
    response = requests.post(f"{SERVER_URL}/configure", json=data)
    return jsonify(response.json()), response.status_code

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