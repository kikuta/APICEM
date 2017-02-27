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

def delQoS(url, ticket, flow_id):
    api_call = "/policy/flow"
    url += api_call + "/" + flow_id
    headers = {
        "content-type": "application/json",
        "X-Auth-Token": ticket
    }
    response = requests.delete(url, headers=headers, verify=False)
    print('----------------------------------------')
    print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
    #r_json = response.json()
    #print(r_json)
    print('----------------------------------------')

if __name__ == "__main__":
    flow_id = input('消去したいフローIDを入力してください: ')

    auth_token = get_token(apic_em_ip)
    delQoS(apic_em_ip, auth_token, flow_id)





