from django.contrib import admin

from wallet_api_app import models


class MTNTransactionAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'amount', 'number', 'bundle_volume', 'batch_id', 'status', 'date']


# Register your models here.
admin.site.register(models.MTNTransaction, MTNTransactionAdmin)
