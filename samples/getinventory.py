import requests
import json
import datetime
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

apicemHost = "https://10.71.154.113/api/v1"

def get_token(url): #トークン取得
    api_call ="/ticket"
    payload = {"username": "admin", "password": "Nms12345!" }
    headers = {"content-type" : "application/json"}
    url +=api_call

    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False).json()
    return response["response"]["serviceTicket"]


def get_device_info(token,url): #デバイス情報表示
    api_call = "/network-device"
    headers = {"X-AUTH-TOKEN" : token}
    url +=api_call

    response = requests.get(url, headers=headers, verify=False).json()
    
    print('-----', 'ホスト名', '|', '管理IPアドレス', '|', 'ソフトウェアバージョン', '|', 'アップタイム', '|', 'デバイスID', '-----')
    for item in response['response']:
        print(item['hostname'],'|',item['managementIpAddress'],'|',item['softwareVersion'],'|',item['upTime'],'|',item['id'])
    print('-----','APIC-EMで管理されている装置数は',len(response['response']),'台です！','-----')

    
def get_device_config(token,url): #コンフィグ取得して保存

    api_call = "/network-device"
    headers = {"X-AUTH-TOKEN" : token}
    url +=api_call

    response = requests.get(url, headers=headers, verify=False).json()
    
    now = datetime.datetime.now()
    file_name = "{0:%Y%m%d.%H%M}".format(now)

    file = open(file_name + '_' + str(len(response['response'])) + 'nodes' + '_config.txt', 'a')
    
    for item in response['response']:
        api_call_config = "/" + item['id'] +"/config"
        response = requests.get(url=url+api_call_config, headers=headers, verify=False).json()
        
        file.write(response['response'])
    file.close()

auth_token = get_token(apicemHost)
get_device_info(auth_token,apicemHost)
get_device_config(auth_token, apicemHost)
