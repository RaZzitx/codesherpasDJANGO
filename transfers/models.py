from django.db import models

# Create your models here.
class Account(models.Model):
    iban = models.CharField(max_length=24, unique=True)
    balance = models.FloatField(default=0.0)

class Trasaction(models.Model):
    date = models.TextField()
    amount = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)
    type = models.IntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)