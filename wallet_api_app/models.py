from django.db import models


# Create your models here.
class WalletUser(models.Model):
    user_id = models.CharField(max_length=200, null=False, blank=False)
    wallet_balance = models.FloatField(null=False, blank=False, default=0.0)
    choices = (
        ("Active", "Active"),
        ("Inactive", "Inactive")
    )
    status = models.CharField(max_length=200, null=False, blank=False, choices=choices, default="Active")
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_id


class MTNTransaction(models.Model):
    user_id = models.CharField(max_length=200, null=False, blank=False)
    amount = models.FloatField(null=False, blank=False, default=0)
    bundle_volume = models.FloatField(null=False, blank=False, default=0)
    status = models.CharField(max_length=200, default="Undelivered")
    batch_id = models.CharField(max_length=200, default="Unknown")
    number = models.CharField(max_length=200, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    firebase_date = models.CharField(max_length=200, null=True, blank=True)



