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
history_collection = database.collection(u'History')
mail_collection = database.collection('mail')
# mtn_history = database.collection()


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


def send_ishare_bundle(first_name: str, last_name: str, buyer, receiver: str, email: str, bundle: float):
    print("in send bundle")
    url = "https://backend.boldassure.net:445/live/api/context/business/transaction/new-transaction"

    payload = json.dumps({
        "accountNo": buyer,
        "accountFirstName": first_name,
        "accountLastName": last_name,
        "accountMsisdn": receiver,
        "accountEmail": email,
        "accountVoiceBalance": 0,
        "accountDataBalance": bundle,
        "accountCashBalance": 0,
        "active": True
    })

    headers = {
        'Authorization': config("BEARER_TOKEN"),
        'Content-Type': 'application/json'
    }
    print("here")
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

    ishare_response, status_code = send_ishare_bundle(first_name=first_name, last_name=last_name, receiver=receiver,
                                                      buyer=phone,
                                                      bundle=data_volume,
                                                      email=email)
    json_response = ishare_response.json()
    print(f"hello:{json_response}")
    status_code = status_code
    print(status_code)
    batch_id = json_response["batchId"]
    print(batch_id)

    data = {
        'batch_id': batch_id,
        'buyer': phone,
        'color_code': color_code,
        'amount': amount,
        'data_break_down': data_break_down,
        'data_volume': data_volume,
        'date': date,
        'date_and_time': date_and_time,
        'done': "unknown",
        'email': email,
        'image': image,
        'ishareBalance': ishare_balance,
        'name': f"{first_name} {last_name}",
        'number': receiver,
        'paid_at': paid_at,
        'reference': reference,
        'responseCode': status_code,
        'status': txn_status,
        'time': time,
        'tranxId': str(tranx_id_gen()),
        'type': txn_type,
        'uid': user_id
    }
    history_collection.document(date_and_time).set(data)
    print("firebase saved")
    return status_code, batch_id if batch_id else "No batchId", email, first_name


def ishare_verification(batch_id):
    if batch_id == "No batchId":
        return False

    url = f"https://backend.boldassure.net:445/live/api/context/business/airteltigo-gh/ishare/tranx-status/{batch_id}"

    payload = {}
    headers = {
        'Authorization': config("BEARER_TOKEN")
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

    def get(self, request, user_id, *args, **kwargs):
        user_instance = self.get_object(user_id)
        if not user_instance:
            return Response({
                "message": "User does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        # serializer = user_instance.get()
        # try:
        #     user_dict = dict(serializer)
        # except TypeError:
        #     return Response({'code': '0001', 'message': "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        # wallet = user_dict["wallet_balance"]
        # return Response({'code': '0000', 'wallet_balance': wallet}, status=status.HTTP_200_OK)

    def post(self, request, token, user_id, amount, *args, **kwargs):
        if compare_digest(token, config('TOKEN')):
            return Response(data={'message': 'Invalid Authorization Token Provided'},
                            status=status.HTTP_401_UNAUTHORIZED)
        user_instance = self.get_object(user_id)
        if not user_instance:
            return Response({
                "message": "User does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        data = {
            'user_id': user_id,
            'top_up_amount': amount,
        }
        print(data)
        user_details = get_user_details(user_id)
        try:
            previous_wallet_balance = user_details['wallet']
        except ValueError:
            return Response({'code': '0001', 'message': "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.WalletUserSerializer(data=data)
        try:
            converted = float(amount)
        except ValueError:
            return Response({'message': "Invalid wallet balance provided"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            to_be_added = float(amount)
            new_balance = previous_wallet_balance + to_be_added
            doc_ref = user_collection.document(user_id)
            doc_ref.update({'wallet': new_balance})
            return Response({"code": "0000", "message": "Wallet Crediting Successful",
                             "data": {'previousBalance': previous_wallet_balance, 'currentBalance': new_balance}},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            print(enough_balance)
            status_code, batch_id, email, first_name = send_and_save_to_history(user_id, txn_type, txn_status, paid_at,
                                                                                float(ishare_balance),
                                                                                color_code, float(data_volume),
                                                                                reference,
                                                                                data_break_down,
                                                                                float(amount), receiver,
                                                                                date, image, time, date_and_time)
            print(status_code)
            print(batch_id)
            if channel.lower() == "wallet":
                update_user_wallet(user_id, amount)
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
                return redirect(callback_url)
            else:
                return redirect(callback_url)
                # return Response(data={'status_code': '0001', 'batch_id': 'None'}, status=status.HTTP_200_OK)
        else:
            return redirect(callback_url)
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
                'image': image,
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
            return redirect(callback_url)
        else:
            return Response({"code": '0001', 'message': 'Not enough balance to perform transaction'},
                            status=status.HTTP_200_OK)


class InitiateMTNTransaction(APIView):
    def get(self, request, token, user_id: str, txn_type: str, txn_status: str, paid_at: str,
            channel: str, ishare_balance: str,
            color_code: str,
            data_volume: str, reference: str, data_break_down: str, amount: str, receiver: str,
            date: str, image, time: str, date_and_time: str,  callback_url: str):
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
                'image': image,
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
            user = history_collection.document(date_and_time)
            doc = user.get()
            print(doc.to_dict())
            tranx_id = doc.to_dict()['tranxId']
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
            return redirect(callback_url)
        else:
            return Response({"code": '0001', 'message': 'Not enough balance to perform transaction'},
                            status=status.HTTP_200_OK)
