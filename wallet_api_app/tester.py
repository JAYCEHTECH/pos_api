import requests

url = f"https://console.bestpaygh.com/api/flexi/v1/transaction_detail/T682709328318817/"

payload = ""
headers = {
    'api-key': "YZIDF9C3G1-MJS1ZLAMTSZT9DN3YYZ19",
    'api-secret': "M6FXA0$UBS-ACRA2FHFW$MC333$9TFU5UYK3$69UU77NOGC$NC8S53TL9O66ZR0Y",
}

response = requests.request("POST", url, headers=headers, data=payload)

response = response.json()
print(response["code"])


