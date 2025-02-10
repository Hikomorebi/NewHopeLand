import requests
import json

# 配置信息
api_key = "sk-9a9538a6e032437ebfb73a5ac17debc4"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
model_name = "qwen-plus"

# 服务端地址
server_url = "http://127.0.0.1:45108/configure"

# 发送 POST 请求到 /configure 接口
def test_configure(api_key, base_url, model_name, server_url):
    data = {
        "api_key": api_key,
        "base_url": base_url,
        "model_name": model_name
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(server_url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        print("配置成功！")
        print("响应内容：", response.json())
    else:
        print("配置失败！")
        print("状态码：", response.status_code)
        print("响应内容：", response.json())

if __name__ == "__main__":
    test_configure(api_key, base_url, model_name, server_url)