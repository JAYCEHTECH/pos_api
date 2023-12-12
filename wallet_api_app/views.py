import datetime
import json
import random
from time import sleep

import requests
from decouple import config
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from requests.adapters import HTTPAdapter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from urllib3 import Retry
from django.conf import settings

from . import models, serializers
from .other_tests import tranx_id_generator
# Create your views here.

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, firestore
from secrets import compare_digest

if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_ADMIN_CERT)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://bestpay-flutter-default-rtdb.firebaseio.com'
    })

database = firestore.client()
user_collection = database.collection(u'Users')
history_collection = database.collection(u'History Web')
mail_collection = database.collection('mail')
mtn_history = database.collection('MTN_Admin_History')
mtn_tranx = mtn_history.document('mtnTransactions')
mtn_other = mtn_tranx.collection('mtnOther')
bearer_token_collection = database.collection("_KeysAndBearer")
history_web = database.collection(u'History Web').document('all_users')



# all_users = [{**user.to_dict(), "id": user.id} for user in user_collection]
# print(all_users)
# user1 = user_collection.document('B2Ruk9G9b0ZX8mvluBUL3jKOCuA3')


# print(user1.get())
# print({**user1.to_dict(), "id": user1.id})


def all_users():
    """Get all todo from firestore database"""
    docs = user_collection.stream()
    for doc in docs:
        print(doc.to_dict())


def get_user_details(user_id):
    user = user_collection.document(user_id)
    doc = user.get()
    if doc.exists:
        doc_dict = doc.to_dict()
        first_name = doc_dict['first name']
        last_name = doc_dict['last name']
        email = doc_dict['email']
        phone = doc_dict['phone']
        print(doc_dict['wallet'])
        print(first_name), print(last_name), print(email), print(phone)
        return doc.to_dict()
    else:
        return None


def update_user_wallet(user_id, amount):
    print("did updating")
    print(f"amount:{amount}")
    user = get_user_details(user_id)
    if user is None:
        return None
    user_wallet = user['wallet']
    new_balance = float(user_wallet) - float(amount)
    print(f"new_balance:{new_balance}")
    print(user_wallet)
    doc_ref = user_collection.document(user_id)
    doc_ref.update({'wallet': new_balance})
    user = get_user_details(user_id)
    user_wallet = user['wallet']
    print(f"new_user_wallet: {user_wallet}")
    if user_wallet is not None:
        return user_wallet
    else:
        return None


def tranx_id_gen():
    tranx_id = tranx_id_generator()
    history = history_collection.document(str(tranx_id))
    doc = history.get()
    if doc.exists:
        return tranx_id_gen()
    else:
        return str(tranx_id)


def check_user_balance_against_price(user_id, price):
    details = get_user_details(user_id)
    wallet_balance = details['wallet']
    if wallet_balance is not None:
        return wallet_balance >= float(price)
    else:
        return None


# History
def get_all_history():
    docs = history_collection.stream()
    counter = 0
    for doc in docs:
        if counter < 10:
            print(doc.to_dict())
            counter = counter + 1
            print(f"counter {counter}")
        break


def send_ishare_bundle(first_name: str, last_name: str, buyer, receiver: str, email: str, bundle: float, reference: str):
    # print("in send bundle")
    # url = "https://backend.boldassure.net:445/live/api/context/business/transaction/new-transaction"
    #
    # payload = json.dumps({
    #     "accountNo": buyer,
    #     "accountFirstName": first_name,
    #     "accountLastName": last_name,
    #     "accountMsisdn": receiver,
    #     "accountEmail": email,
    #     "accountVoiceBalance": 0,
    #     "accountDataBalance": bundle,
    #     "accountCashBalance": 0,
    #     "active": True
    # })
    #
    # token = bearer_token_collection.document("Active_API_BoldAssure")
    # token_doc = token.get()
    # token_doc_dict = token_doc.to_dict()
    # tokennn = token_doc_dict['ishare_bearer']
    #
    # headers = {
    #     'Authorization': tokennn,
    #     'Content-Type': 'application/json'
    # }
    # print("here")
    # session = requests.Session()
    # retry = Retry(connect=15, backoff_factor=0.5)
    # adapter = HTTPAdapter(max_retries=retry)
    # session.mount('https://', adapter)
    #
    # response = session.post(url, headers=headers, data=payload)
    # status_code = response.status_code
    # print("after response")
    #
    # return response, status_code

    url = "https://console.bestpaygh.com/api/flexi/v1/new_transaction/"

    token = bearer_token_collection.document("Active_API_BoldAssure")
    token_doc = token.get()
    token_doc_dict = token_doc.to_dict()
    key = token_doc_dict['key']
    secret = token_doc_dict['secret']

    headers = {
        "api-key": key,
        "api-secret": secret,
        'Content-Type': 'application/json'
    }

    payload = json.dumps({
        "first_name": first_name,
        "last_name": last_name,
        "account_number": buyer,
        "receiver": receiver,
        "account_email": email,
        "reference": reference,
        "bundle_amount": bundle
    })

    session = requests.Session()
    retry = Retry(connect=15, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)

    response = session.post(url, headers=headers, data=payload)
    status_code = response.status_code
    print("after response")

    return response, status_code


def send_and_save_to_history(user_id, txn_type: str, txn_status: str, paid_at: str, ishare_balance: float,
                             color_code: str,
                             data_volume: float, reference: str, data_break_down: str, amount: float, receiver: str,
                             date: str, image, time: str, date_and_time: str):
    user_details = get_user_details(user_id)
    first_name = user_details['first name']
    last_name = user_details['last name']
    email = user_details['email']
    phone = user_details['phone']

    data = {
        'batch_id': "unknown",
        'buyer': phone,
        'color_code': color_code,
        'amount': amount,
        'data_break_down': data_break_down,
        'data_volume': data_volume,
        'date': date,
        'date_and_time': date_and_time,
        'done': "unknown",
        'email': email,
        'image': user_id,
        'ishareBalance': ishare_balance,
        'name': f"{first_name} {last_name}",
        'number': receiver,
        'paid_at': paid_at,
        'reference': reference,
        'responseCode': "0",
        'status': txn_status,
        'time': time,
        'tranxId': str(tranx_id_gen()),
        'type': txn_type,
        'uid': user_id
    }
    history_collection.document(date_and_time).set(data)
    history_web.collection(email).document(date_and_time).set(data)

    print("first save")

    ishare_response, status_code = send_ishare_bundle(first_name=first_name, last_name=last_name, receiver=receiver,
                                                      buyer=phone,
                                                      bundle=data_volume,
                                                      email=email, reference=reference)
    json_response = ishare_response.json()
    print(f"hello:{json_response}")
    status_code = status_code
    print(status_code)
    batch_id = json_response["batch_id"]
    print(batch_id)

    doc_ref = history_collection.document(date_and_time)
    doc_ref.update({'batch_id': batch_id, 'responseCode': status_code})
    history_web.collection(email).document(date_and_time).update({'batch_id': batch_id, 'responseCode': status_code})
    # data = {
    #     'batch_id': batch_id,
    #     'buyer': phone,
    #     'color_code': color_code,
    #     'amount': amount,
    #     'data_break_down': data_break_down,
    #     'data_volume': data_volume,
    #     'date': date,
    #     'date_and_time': date_and_time,
    #     'done': "unknown",
    #     'email': email,
    #     'image': image,
    #     'ishareBalance': ishare_balance,
    #     'name': f"{first_name} {last_name}",
    #     'number': receiver,
    #     'paid_at': paid_at,
    #     'reference': reference,
    #     'responseCode': status_code,
    #     'status': txn_status,
    #     'time': time,
    #     'tranxId': str(tranx_id_gen()),
    #     'type': txn_type,
    #     'uid': user_id
    # }
    # history_collection.document(date_and_time).set(data)
    # history_web.collection(email).document(date_and_time).set(data)

    print("firebase saved")
    return status_code, batch_id if batch_id else "No batchId", email, first_name


def ishare_verification(batch_id):
    if batch_id == "No batchId":
        return False

    url = f"https://backend.boldassure.net:445/live/api/context/business/airteltigo-gh/ishare/tranx-status/{batch_id}"

    payload = {}
    token = bearer_token_collection.document("Active_API_BoldAssure")
    token_doc = token.get()
    token_doc_dict = token_doc.to_dict()
    tokennn = token_doc_dict['ishare_bearer']
    headers = {
        'Authorization': tokennn
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        json_data = response.json()
        print(json_data)
        return json_data
    else:
        return False


# all_users()

# print(get_user_wallet('9VA0qyq6lXYPZ6Ut867TVcBvF2t1'))
# print(get_user_details('9VA0qyq6lXYPZ6Ut867TVcBvF2t1'))
# print(check_user_balance_against_price('9VA0qyq6lXYPZ6Ut867TVcBvF2t1', 857585758))


# get_all_history()


class WalletUserListApiView(APIView):

    def get(self, *args, **kwargs):
        # wallet_users = users_ref.get()
        # serializer = serializers.WalletUserSerializer(wallet_users, many=True)
        # return Response(wallet_users, status=status.HTTP_200_OK)
        ...

    def post(self, request, *args, **kwargs):
        data = {
            'user_id': request.data.get('user_id'),
            'wallet_balance': request.data.get('wallet_balance'),
            'status': request.data.get('status')
        }
        print(data)
        serializer = serializers.WalletUserSerializer(data=data)
        try:
            converted = float(data['wallet_balance'])
        except ValueError:
            return Response({'message': "Invalid wallet balance provided"}, status=status.HTTP_400_BAD_REQUEST)
        user_status = data['status']
        if user_status not in ["Active", "Inactive"]:
            return Response({'message': "Invalid status provided. Valid options are 'Active' or 'Inactive'."},
                            status=status.HTTP_400_BAD_REQUEST)
        # if users_ref.child(data['user_id']):
        #     return Response({"code": "0001", "message": "User wallet already exists"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # if serializer.is_valid():
        #     users_ref.child(data['user_id']).set(
        #         {
        #             'user_id': data['user_id'],
        #             'wallet_balance': data['wallet_balance'],
        #             'status': data['status']
        #         }
        #     )
        #     return Response({"code": "0000", "message": "User wallet created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletUserDetail(APIView):

    def get_object(self, user_id):
        try:
            # user = users_ref.child(user_id)
            user = "hi"
            return user
        except:
            return None

    def get(self, request, user_id, *args, **kwargs):
        user_instance = self.get_object(user_id)
        if not user_instance:
            return Response({
                "message": "User does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        # serializer = user_instance.get()
        # user_dict = dict(serializer)
        # wallet = user_dict["wallet_balance"]
        # print(wallet)
        # print(user_dict)
        # print(serializer)
        # return Response({'user_details': serializer}, status=status.HTTP_200_OK)
        ...

    def post(self, request, user_id, *args, **kwargs):
        user_instance = self.get_object(user_id)
        if not user_instance:
            return Response({
                "message": "User does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        data = {
            'user_id': request.data.get('user_id'),
            'wallet_balance': request.data.get('wallet_balance'),
            'status': request.data.get('status')
        }
        print(data)
        user_data = user_instance.get()
        serializer = serializers.WalletUserSerializer(data=data)
        try:
            converted = float(data['wallet_balance'])
        except ValueError:
            return Response({'message': "Invalid wallet balance provided"}, status=status.HTTP_400_BAD_REQUEST)
        user_status = data['status']
        if user_status not in ["Active", "Inactive"]:
            return Response({'message': "Invalid status provided. Valid options are 'Active' or 'Inactive'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # if serializer.is_valid():
        #     users_ref.child(user_id).update(
        #         {
        #             'wallet_balance': data['wallet_balance'],
        #             'user_id': data['user_id'],
        #             'status': data['status'],
        #         }
        #     )
        #     new_user_details = users_ref.child(user_id).get()
        #     return Response({"code": "0000", "message": "User details updated successfully", "data": new_user_details},
        #                     status=status.HTTP_200_OK)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletUserBalance(APIView):
    def get_object(self, user_id):
        try:
            # user = users_ref.child(user_id)
            user = "hi"
            return user
        except TypeError:
            return None

    # def get(self, request, user_id, *args, **kwargs):
    #     user_instance = self.get_object(user_id)
    #     if not user_instance:
    #         return Response({
    #             "message": "User does not exist"
    #         }, status=status.HTTP_404_NOT_FOUND)
    # serializer = user_instance.get()
    # try:
    #     user_dict = dict(serializer)
    # except TypeError:
    #     return Response({'code': '0001', 'message': "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    # wallet = user_dict["wallet_balance"]
    # return Response({'code': '0000', 'wallet_balance': wallet}, status=status.HTTP_200_OK)

    def get(self, request, token, user_id, amount: str, txn_type: str, txn_status: str, paid_at: str,
            channel: str, ishare_balance: str,
            color_code: str,
            data_volume: str, reference: str, data_break_down: str, receiver: str,
            date: str, image, time: str, date_and_time: str, callback_url, *args, **kwargs):
        if token != config('TOKEN'):
            return Response(data={'message': 'Invalid Authorization Token Provided'},
                            status=status.HTTP_401_UNAUTHORIZED)
        print("hit it")
        user_details = get_user_details(user_id)
        email = user_details['email']
        user_instance = self.get_object(user_id)
        # hist = history_web.collection(email).document(date_and_time)
        # doc = hist.get()
        # if doc.exists:
        #     print(doc)
        #     return redirect(f"https://{callback_url}")
        # else:
        #     print("no record found")
        if not user_instance:
            return Response({
                "message": "User does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        data = {
            'user_id': user_id,
            'top_up_amount': amount,
        }
        user_details = get_user_details(user_id)
        first_name = user_details['first name']
        last_name = user_details['last name']
        phone = user_details['phone']
        to_be_added = float(amount)
        all_data = {
            'batch_id': "unknown",
            'buyer': phone,
            'color_code': color_code,
            'amount': amount,
            'data_break_down': data_break_down,
            'data_volume': data_volume,
            'date': date,
            'date_and_time': date_and_time,
            'done': "Success",
            'email': email,
            'image': user_id,
            'ishareBalance': ishare_balance,
            'name': f"{first_name} {last_name}",
            'number': receiver,
            'paid_at': paid_at,
            'reference': reference,
            'responseCode': 200,
            'status': txn_status,
            'time': time,
            'tranxId': str(tranx_id_gen()),
            'type': txn_type,
            'uid': user_id
        }
        history_web.collection(email).document(date_and_time).set(all_data)
        print("saved")
        print(f"yo{history_web.collection(email).document(date_and_time).get().to_dict()}")
        print(data)
        user_details = get_user_details(user_id)
        try:
            previous_wallet_balance = user_details['wallet']
        except ValueError:
            return Response({'code': '0001', 'message': "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.WalletUserSerializer(data=data)
        if serializer.is_valid():

            user_details = get_user_details(user_id)
            first_name = user_details['first name']
            last_name = user_details['last name']
            email = user_details['email']
            phone = user_details['phone']
            to_be_added = float(amount)
            print(to_be_added)
            print("heyyyyyyyy")
            new_balance = previous_wallet_balance + to_be_added
            print(new_balance)
            doc_ref = user_collection.document(user_id)
            doc_ref.update({'wallet': new_balance, 'wallet_last_update': date_and_time, 'recent_wallet_reference': reference})
            print(doc_ref.get().to_dict())
            # data = {
            #     'batch_id': "unknown",
            #     'buyer': phone,
            #     'color_code': color_code,
            #     'amount': amount,
            #     'data_break_down': data_break_down,
            #     'data_volume': data_volume,
            #     'date': date,
            #     'date_and_time': date_and_time,
            #     'done': "Success",
            #     'email': email,
            #     'image': image,
            #     'ishareBalance': ishare_balance,
            #     'name': f"{first_name} {last_name}",
            #     'number': receiver,
            #     'paid_at': paid_at,
            #     'reference': reference,
            #     'responseCode': 200,
            #     'status': txn_status,
            #     'time': time,
            #     'tranxId': str(tranx_id_gen()),
            #     'type': txn_type,
            #     'uid': user_id
            # }
            # history_web.collection(email).document(date_and_time).set(data)
            name = f"{first_name} {last_name}"
            amount = to_be_added
            file_path = 'wallet_api_app/wallet_mail.txt'
            mail_doc_ref = mail_collection.document()

            with open(file_path, 'r') as file:
                html_content = file.read()

            placeholders = {
                '{name}': name,
                '{amount}': amount
            }

            for placeholder, value in placeholders.items():
                html_content = html_content.replace(placeholder, str(value))

            mail_doc_ref.set({
                'to': email,
                'message': {
                    'subject': 'Wallet Topup',
                    'html': html_content,
                    'messageId': 'Bestpay'
                }
            })

            sms_message = f"GHS {to_be_added} was deposited in your wallet. Available balance is now GHS {new_balance}"
            sms_url = f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=UmpEc1JzeFV4cERKTWxUWktqZEs&to=0{user_details['phone']}&from=InternetHub&sms={sms_message}"
            response = requests.request("GET", url=sms_url)
            print(response.status_code)
            return redirect(f"https://{callback_url}")
        return redirect(f"https://{callback_url}")


class InitiateTransaction(APIView):
    def get(self, request, token, user_id: str, txn_type: str, txn_status: str, paid_at: str,
            channel: str, ishare_balance: str,
            color_code: str,
            data_volume: str, reference: str, data_break_down: str, amount: str, receiver: str,
            date: str, image, time: str, date_and_time: str, callback_url: str):
        if token != config('TOKEN'):
            return Response(data={'message': 'Invalid Authorization Token Provided'},
                            status=status.HTTP_401_UNAUTHORIZED)
        if channel.lower() == "wallet":
            enough_balance = check_user_balance_against_price(user_id, amount)
        else:
            enough_balance = True
        print(enough_balance)
        if enough_balance:
            user_details = get_user_details(user_id)
            email = user_details['email']
            print(enough_balance)
            # hist = history_web.collection(email).document(date_and_time)
            # doc = hist.get()
            # if doc.exists:
            #     return redirect(f"https://{callback_url}")
            # else:
            #     print("no record found")
            if channel.lower() == "wallet":
                update_user_wallet(user_id, amount)
            status_code, batch_id, email, first_name = send_and_save_to_history(user_id, txn_type, txn_status, paid_at,
                                                                                float(ishare_balance),
                                                                                color_code, float(data_volume),
                                                                                reference,
                                                                                data_break_down,
                                                                                float(amount), receiver,
                                                                                date, image, time, date_and_time)
            print(status_code)
            print(batch_id)
            sleep(10)
            ishare_verification_response = ishare_verification(batch_id)
            if ishare_verification_response is not False:
                code = \
                    ishare_verification_response["flexiIshareTranxStatus"]["flexiIshareTranxStatusResult"][
                        "apiResponse"][
                        "responseCode"]
                ishare_response = \
                    ishare_verification_response["flexiIshareTranxStatus"]["flexiIshareTranxStatusResult"][
                        "ishareApiResponseData"][
                        "apiResponseData"][
                        0][
                        "responseMsg"]
                print(code)
                print(ishare_response)
                if code == '200' or ishare_response == 'Crediting Successful.':
                    sms = f"Hey there\nYour account has been credited with {data_volume}MB.\nTransaction Reference: {reference}"
                    r_sms_url = f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=UmpEc1JzeFV4cERKTWxUWktqZEs&to={receiver}&from=InternetHub&sms={sms}"
                    response = requests.request("GET", url=r_sms_url)
                    print(response.text)
                    doc_ref = history_collection.document(date_and_time)
                    doc_ref.update({'done': 'Successful'})
                    mail_doc_ref = mail_collection.document(f"{batch_id}-Mail")
                    file_path = 'wallet_api_app/mail.txt'  # Replace with your file path

                    name = first_name
                    volume = data_volume
                    date = date_and_time
                    reference_t = reference
                    receiver_t = receiver

                    with open(file_path, 'r') as file:
                        html_content = file.read()

                    placeholders = {
                        '{name}': name,
                        '{volume}': volume,
                        '{date}': date,
                        '{reference}': reference_t,
                        '{receiver}': receiver_t
                    }

                    for placeholder, value in placeholders.items():
                        html_content = html_content.replace(placeholder, str(value))

                    mail_doc_ref.set({
                        'to': email,
                        'message': {
                            'subject': 'AT Flexi Bundle',
                            'html': html_content,
                            'messageId': 'Bestpay'
                        }
                    })
                else:
                    doc_ref = history_collection.document(date_and_time)
                    doc_ref.update({'done': 'Failed'})
                user = history_collection.document(date_and_time)
                doc = user.get()
                print(doc.to_dict())
                # return Response(data={'status_code': status_code, 'batch_id': batch_id}, status=status.HTTP_200_OK)
                return redirect(f"https://{callback_url}")
            else:
                return redirect(f"https://{callback_url}")
        else:
            return redirect(f"https://{callback_url}")
            # return Response({"code": '0001', 'message': 'Not enough balance to perform transaction'},
            #                 status=status.HTTP_200_OK)


# class InitiateMTNTransaction(APIView):
#     ...


class InitiateBigTimeTransaction(APIView):
    def get(self, request, token, user_id: str, txn_type: str, txn_status: str, paid_at: str,
            channel: str, ishare_balance: str,
            color_code: str,
            data_volume: str, reference: str, data_break_down: str, amount: str, receiver: str,
            date: str, image, time: str, date_and_time: str, callback_url: str):
        if token != config('TOKEN'):
            return Response(data={'message': 'Invalid Authorization Token Provided'},
                            status=status.HTTP_401_UNAUTHORIZED)
        if channel.lower() == "wallet":
            print("used this")
            enough_balance = check_user_balance_against_price(user_id, amount)
        else:
            enough_balance = True
        print(enough_balance)
        if enough_balance:
            user_details = get_user_details(user_id)
            first_name = user_details['first name']
            last_name = user_details['last name']
            email = user_details['email']
            phone = user_details['phone']
            # hist = history_web.collection(email).document(date_and_time)
            # doc = hist.get()
            # if doc.exists:
            #     print(doc)
            #     return redirect(f"https://{callback_url}")
            # else:
            #     print("no record found")
            if channel.lower() == "wallet":
                print("updated")
                update_user_wallet(user_id, amount)
            data = {
                'batch_id': "unknown",
                'buyer': phone,
                'color_code': color_code,
                'amount': amount,
                'data_break_down': data_break_down,
                'data_volume': data_volume,
                'date': date,
                'date_and_time': date_and_time,
                'done': "unknown",
                'email': email,
                'image': user_id,
                'ishareBalance': ishare_balance,
                'name': f"{first_name} {last_name}",
                'number': receiver,
                'paid_at': paid_at,
                'reference': reference,
                'responseCode': 200,
                'status': txn_status,
                'time': time,
                'tranxId': str(tranx_id_gen()),
                'type': txn_type,
                'uid': user_id
            }
            history_collection.document(date_and_time).set(data)
            history_web.collection(email).document(date_and_time).set(data)
            mtn_other.document(date_and_time).set(data)
            user = history_collection.document(date_and_time)
            doc = user.get()
            print(doc.to_dict())
            tranx_id = doc.to_dict()['tranxId']
            mail_doc_ref = mail_collection.document()
            file_path = 'wallet_api_app/mtn_mail.txt'  # Replace with your file path

            name = first_name
            volume = data_volume
            date = date_and_time
            reference_t = reference
            receiver_t = receiver

            with open(file_path, 'r') as file:
                html_content = file.read()

            placeholders = {
                '{name}': name,
                '{volume}': volume,
                '{date}': date,
                '{reference}': reference_t,
                '{receiver}': receiver_t
            }

            for placeholder, value in placeholders.items():
                html_content = html_content.replace(placeholder, str(value))

            mail_doc_ref.set({
                'to': email,
                'message': {
                    'subject': 'Big Time Data',
                    'html': html_content,
                    'messageId': 'Bestpay'
                }
            })
            return redirect(f"https://{callback_url}")
        else:
            return Response({"code": '0001', 'message': 'Not enough balance to perform transaction'},
                            status=status.HTTP_200_OK)


class InitiateMTNTransaction(APIView):
    def get(self, request, token, user_id: str, txn_type: str, txn_status: str, paid_at: str,
            channel: str, ishare_balance: str,
            color_code: str,
            data_volume: str, reference: str, data_break_down: str, amount: str, receiver: str,
            date: str, image, time: str, date_and_time: str, callback_url: str):
        if token != config('TOKEN'):
            return Response(data={'message': 'Invalid Authorization Token Provided'},
                            status=status.HTTP_401_UNAUTHORIZED)
        if channel.lower() == "wallet":
            print("used this")
            enough_balance = check_user_balance_against_price(user_id, amount)
        else:
            enough_balance = True
        print(enough_balance)
        if enough_balance:
            user_details = get_user_details(user_id)
            first_name = user_details['first name']
            last_name = user_details['last name']
            email = user_details['email']
            phone = user_details['phone']
            # hist = history_web.collection(email).document(date_and_time)
            # doc = hist.get()
            # if doc.exists:
            #     print(doc)
            #     return redirect(f"https://{callback_url}")
            # else:
            #     print("no record found")
            if channel.lower() == "wallet":
                print("updated")
                update_user_wallet(user_id, amount)

            data = {
                'batch_id': "unknown",
                'buyer': phone,
                'color_code': color_code,
                'amount': amount,
                'data_break_down': data_break_down,
                'data_volume': data_volume,
                'date': date,
                'date_and_time': date_and_time,
                'done': "unknown",
                'email': email,
                'image': user_id,
                'ishareBalance': ishare_balance,
                'name': f"{first_name} {last_name}",
                'number': receiver,
                'paid_at': paid_at,
                'reference': reference,
                'responseCode': 200,
                'status': txn_status,
                'time': time,
                'tranxId': str(tranx_id_gen()),
                'type': txn_type,
                'uid': user_id
            }


            history_collection.document(date_and_time).set(data)
            history_web.collection(email).document(date_and_time).set(data)
            user = history_collection.document(date_and_time)
            doc = user.get()
            print(doc.to_dict())
            tranx_id = doc.to_dict()['tranxId']
            second_data = {
                'amount': amount,
                'batch_id': "unknown",
                'channel': channel,
                'color_code': color_code,
                'created_at': date_and_time,
                'data_volume': data_volume,
                'date': date,
                'email': email,
                'date_and_time': date_and_time,
                'image': user_id,
                'ip_address': "",
                'ishareBalance': 0,
                'name': f"{first_name} {last_name}",
                'number': receiver,
                'buyer': phone,
                'paid_at': date_and_time,
                'payment_status': "success",
                'reference': reference,
                'status': "Completed",
                'time': time,
                'tranxId': tranx_id,
                'type': "MTN Other Data"
            }
            mtn_other.document(date_and_time).set(second_data)
            user22 = mtn_other.document(date_and_time)
            pu = user22.get()
            print(pu.to_dict())
            print("pu")
            mail_doc_ref = mail_collection.document()
            file_path = 'wallet_api_app/mtn_maill.txt'  # Replace with your file path

            name = first_name
            volume = data_volume
            date = date_and_time
            reference_t = reference
            receiver_t = receiver

            with open(file_path, 'r') as file:
                html_content = file.read()

            placeholders = {
                '{name}': name,
                '{volume}': volume,
                '{date}': date,
                '{reference}': reference_t,
                '{receiver}': receiver_t
            }

            for placeholder, value in placeholders.items():
                html_content = html_content.replace(placeholder, str(value))

            mail_doc_ref.set({
                'to': email,
                'message': {
                    'subject': 'MTN Data',
                    'html': html_content,
                    'messageId': 'Bestpay'
                }
            })
            print("got to redirect")
            return redirect(f"https://{callback_url}")
        else:
            return Response({"code": '0001', 'message': 'Not enough balance to perform transaction'},
                            status=status.HTTP_200_OK)
