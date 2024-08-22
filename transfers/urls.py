from django.urls import path
from transfers.views import createAccount, getAccount, deposit, withdraw, transfer, get_transactions

urlpatterns = [
    path('createaccount/', createAccount),
    path('account/', getAccount),
    path('deposit/', deposit),
    path('withdraw/', withdraw),
    path('transfer/', transfer),
    path('get_transactions/', get_transactions)
]