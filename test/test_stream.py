import requests

# 设置请求URL
url = "http://127.0.0.1:45108/chat"  # 假设Flask应用运行在本地的5000端口

# 要发送的POST数据
data = {"session_id":"11214","query": "列出每个公司的认签比","dataSource":''}

# 发起POST请求，stream=True表示以流的形式处理响应
response = requests.post(url, json=data, stream=True)

# 确保请求成功
if response.status_code == 200:
    # 逐行读取并处理返回的SSE数据
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            received_data = decoded_line.strip()
            print(f"Received: {received_data}")
else:
    print(f"Failed to get response. Status code: {response.status_code}")
