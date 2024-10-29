import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
api_upload = '/upload'
api_get_result = '/getResult'

class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()

    def get_signa(self):
        appid = self.appid
        secret_key = self.secret_key
        m2 = hashlib.md5()
        m2.update((appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return signa

    def upload(self):
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {
            'appId': self.appid,
            'signa': self.signa,
            'ts': self.ts,
            'fileSize': file_len,
            'fileName': file_name,
            'duration': "200"
        }
        data = open(upload_file_path, 'rb').read(file_len)

        response = requests.post(url=lfasr_host + api_upload + "?" + urllib.parse.urlencode(param_dict),
                                 headers={"Content-type": "application/json"}, data=data)
        result = json.loads(response.text)
        return result

    def get_result(self):
        uploadresp = self.upload()
        orderId = uploadresp['content']['orderId']
        param_dict = {
            'appId': self.appid,
            'signa': self.signa,
            'ts': self.ts,
            'orderId': orderId,
            'resultType': "transfer,predict"
        }

        status = 3
        while status == 3:
            response = requests.post(url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                                     headers={"Content-type": "application/json"})
            result = json.loads(response.text)
            status = result['content']['orderInfo']['status']
            if status == 4:
                break
            time.sleep(5)
            
        try:

            order_result_dict = json.loads(result['content']['orderResult'])
            
        except Exception as e:
            print("未检测到语音输入")
            return "未检测到语音输入"
        concatenated_text = ''
        for lattice_entry in order_result_dict['lattice']:
            json_1best_value = json.loads(lattice_entry['json_1best'])
            ws_list = json_1best_value['st']['rt'][0]['ws']
            for word in ws_list:
                concatenated_text += word['cw'][0]['w']
        return concatenated_text

def audio_to_text(blob, appid, secret_key): 

    # 调用科大讯飞API进行音频转文字
    api = RequestApi(appid=appid, secret_key=secret_key, upload_file_path=blob)
    text = api.get_result()
    return text

# 主函数仅用于本地测试，嵌入项目时可删
if __name__ == '__main__':
    # 模拟从本地读取一个音频文件作为测试输入
    test_audio_path = r"D:/audio/phi.blob"  
    with open(test_audio_path, 'rb') as audio_file:
        audio_blob = audio_file.read()
    
    # 讯飞开放平台的appid和secret_key
    appid = "28851d54"
    secret_key = "f8b62faf11b2f3c4bcd7eb4b930e0437"
    
    # 调用audio_to_text函数进行测试
    result_text = audio_to_text(audio_blob, appid, secret_key)
    print("转写结果：", result_text)