from rest_framework import serializers
from . import models


class WalletUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WalletUser
        fields = ["user_id", "wallet_balance", "status"]


