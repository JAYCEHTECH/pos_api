from django.urls import path
from . import views

urlpatterns = [
    path('api', views.WalletUserListApiView.as_view()),
    path('api/<str:user_id>/', views.WalletUserDetail.as_view()),
    path('api/wallet/<str:user_id>/', views.WalletUserBalance.as_view()),

    path(
        'initiate_flexi_transaction/<str:token>/<str:user_id>/<str:txn_type>/<str:txn_status>/<str:paid_at>/<str:channel>/<str:ishare_balance>/<str:color_code>/<str:data_volume>/<str:reference>/<str:data_break_down>/<str:amount>/<str:receiver>/<str:date>/<str:image>/<str:time>/<str:date_and_time>/',
        views.InitiateTransaction.as_view()),
    path(
        'initiate_bigtime_transaction/<str:token>/<str:user_id>/<str:txn_type>/<str:txn_status>/<str:paid_at>/<str:channel>/<str:ishare_balance>/<str:color_code>/<str:data_volume>/<str:reference>/<str:data_break_down>/<str:amount>/<str:receiver>/<str:date>/<str:image>/<str:time>/<str:date_and_time>/',
        views.InitiateBigTimeTransaction.as_view()),
]
