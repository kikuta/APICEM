# -*- coding: utf-8 -*-
# 2017.2.28 kikuta@cisco.com
#
import requests
import json
import datetime
import os
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

apicem = "https://10.71.154.113"
apicemApi = apicem + "/api/v1"


def get_token(url): #トークン取得
    api_call ="/ticket"
    payload = {"username": "admin", "password": "Nms12345!" }
    headers = {"content-type" : "application/json"}
    url +=api_call

    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False).json()
    
    print("認証トークン：", response["response"]["serviceTicket"])
    return response["response"]["serviceTicket"]


def get_legit_reads(token,url): #/cli/legit-reads
    api_call = "/network-device-poller/cli/legit-reads"
    headers = {"X-AUTH-TOKEN" : token}
    url +=api_call
    
    displayCmd = input("サポートCLIリストを表示しますか？（y/n）:")
    if displayCmd == 'y':
        response = requests.get(url, headers=headers, verify=False).json()
        print('---------------')
        print('サポートされているCLIは以下です。: /network-device-poller/cli/legit-reads')
        for item in response['response']:
            print(item)


def get_device_info(token,url): #デバイス情報表示
    api_call = "/network-device"
    headers = {"X-AUTH-TOKEN" : token}
    url +=api_call

    response = requests.get(url, headers=headers, verify=False).json()
    
    n = 1
    deviceIdList = []
    print('---------------------------------')
    print('      APIC-EM 管理対象機器一覧      ')
    print('---------------------------------')
    print('番号', '|', 'ホスト名', '|', '管理IPアドレス', '|', 'ソフトウェアバージョン', '|', 'アップタイム')
    for item in response['response']:
        print(n, item['hostname'],'|',item['managementIpAddress'],'|',item['softwareVersion'],'|',item['upTime'])
        n += 1
    print('---------------------------------')
    print('      APIC-EM管理装置数：',len(response['response']),'台')
    print('---------------------------------')
    

def set_cliDeviceNums(): #コマンド実行したい機器番号リスト
    cliDeviceNums = []
    while True:
        cliDevice = input("対象装置番号は？（qで終了）:")
        if cliDevice == 'q':
            break
        else:
            cliDeviceNums.append(cliDevice)
            continue
    return cliDeviceNums


def get_cliDeviceIds(token,url,cliDeviceNums): #★★CLIデバイスIDをReturn
    api_call = "/network-device"
    headers = {"X-AUTH-TOKEN" : token}
    url +=api_call

    response = requests.get(url, headers=headers, verify=False).json()
    
    deviceIdList = []
    deviceHostList = []
    for item in response['response']:
        deviceIdList.append(item['id'])
        deviceHostList.append(item['hostname'])
    
    cliDeviceIds = []
    cliDeviceHosts = []
    for Num in cliDeviceNums:
        cliDeviceIds.append(deviceIdList[int(Num) - 1])
        cliDeviceHosts.append(deviceHostList[int(Num) - 1])
    
    print('------------')
    print('対象デバイスIDリスト：', cliDeviceIds)
    print('対象デバイス名リスト：', cliDeviceHosts)
    print('------------')
    return cliDeviceIds
    

def set_runCmds(): #実行コマンドのリスト作成しReturn
    runCmds = []
    while True:
        runCmd = input("実行したいCLI？（qで終了）:")
        if runCmd == 'q':
            break
        else:
            runCmds.append(runCmd)
            continue
    print('実行するコマンドリスト：', runCmds)
    print('------------')
    return runCmds


def post_cli_request_task(token,url,cliDeviceIds,runCmds): #POST /network-device-poller/cli/read-request
    api_call = "/network-device-poller/cli/read-request"
    headers = {
        "X-AUTH-TOKEN" : token,
        "content-type" : "application/json"
    } 
    url +=api_call
    
    payload = {
        "timeout": 0,
        "description": "",
        "commands": 
            #リスト
            runCmds
            #"show version",
            #"show arp"
        ,
        "deviceUuids": 
            #リスト
            cliDeviceIds
        ,
        "name": ""
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False).json()
    #print(response)
    return response["response"]["url"] #taskIdをリターン


def request_file(token,url,taskIdPath): #FileIdをGET
    headers = {"X-AUTH-TOKEN" : token}
    url +=taskIdPath
    print('タスク：', url)
    
    response = requests.get(url, headers=headers, verify=False)
    #print(response.json())
    fileIdStr = response.json()["response"]["progress"]
    return json.loads(fileIdStr)["fileId"] #fileIdをリターン


def get_fileOutput(token,url,fileId): #ファイルIDの中身からCLI結果を表示
    headers = {"X-AUTH-TOKEN" : token}
    url += "/file/"
    url += fileId
    print('ファイル：', url)
    print('------------')

    response = requests.get(url, headers=headers, verify=False)
    #print(response.json()) #テスト用全表示
    for content in response.json():
        #print(response.json())
        print('デバイスID：', content["deviceUuid"])
        print(content["commandResponses"]["SUCCESS"])
        print('-----------')
    
    
if __name__ == '__main__':
    auth_token = get_token(apicemApi) #トークン取得
    get_legit_reads(auth_token,apicemApi)
    time.sleep(1)
    get_device_info(auth_token,apicemApi) #デバイス一覧表示
    cliDeviceNums = set_cliDeviceNums() #デバイス番号リスト作成
    cliDeviceIds = get_cliDeviceIds(auth_token,apicemApi,cliDeviceNums) #デバイスIDリスト作成
    runCmds = set_runCmds() #コマンドリスト作成
    taskIdPath = post_cli_request_task(auth_token,apicemApi,cliDeviceIds,runCmds) #TASK作成
    time.sleep(5)
    fileId = request_file(auth_token,apicem,taskIdPath) #FileID取得
    get_fileOutput(auth_token,apicemApi,fileId) #Fileを取得、出力
