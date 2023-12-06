import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, firestore
from django.conf import settings

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
#
# if not firebase_admin._apps:
#     cred = credentials.Certificate(settings.FIREBASE_ADMIN_CERT)
#     firebase_admin.initialize_app(cred, {
#         'databaseURL': 'https://bestpay-flutter-default-rtdb.firebaseio.com'
#     })
#
# database = firestore.client()
#
# bearer_token_collection = database.collection("_KeysAndBearer")

url = "https://console.bestpaygh.com/api/flexi/v1/new_transaction/"

# token = bearer_token_collection.document("Active_API_BoldAssure")
# token_doc = token.get()
# token_doc_dict = token_doc.to_dict()
key = "YZIDF9C3G1-MJS1ZLAMTSZT9DN3YYZ19"
secret = "M6FXA0$UBS-ACRA2FHFW$MC333$9TFU5UYK3$69UU77NOGC$NC8S53TL9O66ZR0Y"

headers = {
    "api-key": key,
    "api-secret": secret,
    'Content-Type': 'application/json'
}

payload = json.dumps({
  "first_name": "Mike",
  "last_name": "Gyamfi",
  "account_number": "0242442147",
  "receiver": "0272266444",
  "account_email": "codeage20@gmail.com",
  "reference": "lambda8",
  "bundle_amount": 50
})

session = requests.Session()
retry = Retry(connect=15, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)

response = session.post(url, headers=headers, data=payload)
status_code = response.status_code
print("after response")

print(response.json())
