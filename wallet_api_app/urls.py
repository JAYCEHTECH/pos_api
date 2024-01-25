from django.urls import path
from . import views

urlpatterns = [
    path('api', views.WalletUserListApiView.as_view()),
    path('api/<str:user_id>/', views.WalletUserDetail.as_view()),
    path('api/wallet/<str:token>/<str:user_id>/<str:amount>/<str:txn_type>/<str:txn_status>/<str:paid_at>/<str:channel>/<str:ishare_balance>/<str:color_code>/<str:data_volume>/<str:reference>/<str:data_break_down>/<str:receiver>/<str:date>/<str:image>/<str:time>/<str:date_and_time>/<str:callback_url>/', views.WalletUserBalance.as_view()),

    path(
        'initiate_flexi_transaction/<str:token>/<str:user_id>/<str:txn_type>/<str:txn_status>/<str:paid_at>/<str:channel>/<str:ishare_balance>/<str:color_code>/<str:data_volume>/<str:reference>/<str:data_break_down>/<str:amount>/<str:receiver>/<str:date>/<str:image>/<str:time>/<str:date_and_time>/<str:callback_url>/',
        views.InitiateTransaction.as_view()),
    path(
        'initiate_bigtime_transaction/<str:token>/<str:user_id>/<str:txn_type>/<str:txn_status>/<str:paid_at>/<str:channel>/<str:ishare_balance>/<str:color_code>/<str:data_volume>/<str:reference>/<str:data_break_down>/<str:amount>/<str:receiver>/<str:date>/<str:image>/<str:time>/<str:date_and_time>/<str:callback_url>/',
        views.InitiateBigTimeTransaction.as_view()),
    path(
        'initiate_mtn_transaction/<str:token>/<str:user_id>/<str:txn_type>/<str:txn_status>/<str:paid_at>/<str:channel>/<str:ishare_balance>/<str:color_code>/<str:data_volume>/<str:reference>/<str:data_break_down>/<str:amount>/<str:receiver>/<str:date>/<str:image>/<str:time>/<str:date_and_time>/<str:callback_url>/',
        views.InitiateMTNTransaction.as_view()),


    path('api/v1/initiate_mtn_transaction', views.MTNFlexiInitiate.as_view()),
    path('paystack_webhook', views.paystack_webhook, name='paystack_webhook'),
    path('hubtel_webhook', views.hubtel_webhook, name='hubtel_Webhook'),
    path('export_unknown_transactions/', views.export_unknown_transactions, name='export_unknown_transactions'),
]
