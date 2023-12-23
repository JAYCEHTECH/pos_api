import requests
import json

url = "https://posapi.bestpaygh.com/api/v1/initiate_mtn_transaction"

payload = json.dumps({
  "user_id": "9VA0qyq6lXYPZ6Ut867TVcBvF2t1",
  "receiver": "0242442147",
  "data_volume": 50,
  "reference": "look3",
  "amount": 5667789,
  "channel": "wallet"
})
headers = {
  'Authorization': 'HelloWorld',
  'Content-Type': 'application/json',
  'Cookie': '__cf_bm=7LzHGGJeBXVRXySsW5Ej4IR8rwiJ5xrPGmf9mgS4mSY-1703327140-1-Aew1VVW7QqtoLHb7+DR3pBlK7eW2PKtLDvvdKedQc9eI3nMNF3nAX/+gc0hQPnl71Kbyz0yoJRL3PNxKK57V17g='
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)