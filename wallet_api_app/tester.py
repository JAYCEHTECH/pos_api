import requests
import timeit



# Define the base URL without parameters
base_url = 'http://127.0.0.1:8000/initiate_flexi_transaction/'

# Define parameters
token = "ygduguegiewqgegwiqgie"
user_id = '9VA0qyq6lXYPZ6Ut867TVcBvF2t1'
txn_type = 'Flexi Payment'
txn_status = 'success'
paid_at = '2023-11-27'
ishare_balance = '50'
color_code = 'Green'  # URL encoded '#FFA500'
data_volume = '51'
reference = 'tftft'
data_break_down = 'details'
amount = '2'
receiver = '0272266444'
date = '2023-11-27'
image = 'image_url'
time = '14:30:00'
date_and_time = '2023-11-27T14:30:00'

# Construct the complete URL with parameters
url = f"{base_url}{token}/{user_id}/{txn_type}/{txn_status}/{paid_at}/{ishare_balance}/{color_code}/{data_volume}/{reference}/{data_break_down}/{amount}/{receiver}/{date}/{image}/{time}/{date_and_time}/"

# Send POST request
response = requests.post(url)

# Check response status
if response.status_code == 200:
    print("Request successful.")
    print(response.text)  # If expecting a response, print it
else:
    print("Request failed. Status code:", response.status_code)




# file_path = 'wallet_api_app/mail.txt'  # Replace with your file path
#
# with open(file_path, 'r') as file:
#     html_content = file.read()
#
# # print(html_content)
# print(type(html_content))