#encoding:utf-8
import requests
import json

# Disable warnings
requests.packages.urllib3.disable_warnings()

apic_em_ip = "https://<apicem_ipaddress>/api/v1"

def get_token(url):
    api_call = "/ticket"
    payload = {"username": "<username>", "password": "<password>"}
    headers = {
        "content-type": "application/json"
    }
    url += api_call
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False).json()
    return response["response"]["serviceTicket"]

def postQoS(url, ticket):
    api_call = "/policy/flow"
    url += api_call
    headers = {
        "content-type": "application/json",
        "X-Auth-Token": ticket
    }
    payload = {
        "flowType": flowType_id,
        "protocol": protocol,
        "destIP": destIP,
        "sourceIP": sourceIP,
        "destPort": destPort
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    print('----------------------------------------')
    print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
    r_json = response.json()
    print('FlowID: ', r_json["response"]["flowId"])
    print('----------------------------------------')

if __name__ == "__main__":

    flowType_id = input('フロータイプを入力してください..例）VOICE: ')
    protocol = input('L4プロトコルを入力してください..例）tcp, udp: ')
    destIP = input('宛先IPアドレスを入力してください..例）10.71.154.100: ')
    sourceIP = input('送信元IPアドレスを入力してください..例）10.71.59.138: ')
    destPort = input('宛先ポート番号を入力してください..例）5061: ')
    
    auth_token = get_token(apic_em_ip)
    #print(auth_token)

    postQoS(apic_em_ip, auth_token)
