from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .models import Account,Trasaction
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_POST
def createAccount(request):
    try:
        # Parse the request body to get the IBAN
        data = json.loads(request.body)
        iban = data.get('iban')

        # Check if IBAN was provided
        if not iban:
            return JsonResponse({
                'error': 'IBAN is required',
                'status': 400
            }, status=400)

        # Create a new Account
        account = Account.objects.create(iban=iban, balance=0.0)

        # Return a success message with the created account's details
        return JsonResponse({
            'iban': account.iban,
            'balance': account.balance,
            'status': 201
        }, status=201)

    except Exception as e:
        # Handle any unexpected errors
        return JsonResponse({
            'error': f'An unexpected error occurred: {str(e)}',
            'status': 500
        }, status=500)

@csrf_exempt
@require_POST
def getAccount(request):
    try:
        # Parse the request body to get the IBAN
        data = json.loads(request.body)
        iban = data.get('iban')

        # Try to get the account by IBAN
        account = Account.objects.get(iban=iban)

        # If found, return the account details as JSON
        return JsonResponse({
            'iban': account.iban,
            'balance': account.balance,
            'status': 201
        })

    except Account.DoesNotExist:
        # If the account doesn't exist, return a 404 error
        return JsonResponse({
            'error': 'Account not found',
            'status': 404
        }, status=404)

    except Exception as e:
        # Handle any other unexpected errors
        return JsonResponse({
            'error': f'An unexpected error occurred: {str(e)}'
        }, status=500)


@csrf_exempt
@require_POST
def deposit(request):
    try:

        # Parse the request body to get the IBAN
        data = json.loads(request.body)
        iban = data.get('iban')
        date = data.get('date')
        amount = data.get('amount')
        type = data.get('type')

        # Check if IBAN was provided
        if not iban:
            return JsonResponse({
                'error': 'IBAN is required',
                'status': 400
            }, status=400)


        # Try to get the account by IBAN
        account = Account.objects.get(iban=iban)

        new_balance = float(account.balance) + float(amount)


        # Update the balance
        account.balance = new_balance
        account.save()


        # CREATE A TRANSACTION
        transaction = account.trasaction_set.create(date=date, amount=amount, type=type, balance=new_balance)

        # Return the transaction details in the response
        return JsonResponse({
            'transaction': {
                'id': transaction.id,
                'date': transaction.date,
                'amount': transaction.amount,
                'balance': transaction.balance,
                'type': transaction.type,
                'account_id': transaction.account.id
            },
            'status': 201
        }, status=201)

    except Account.DoesNotExist:

        return JsonResponse({
            'error': 'Account not found',
            'status': 404
        }, status=404)

    except Exception as e:

        return JsonResponse({
            'error': f'An unexpected error occurred: {str(e)}',
            'status': 500
        }, status=500)



@csrf_exempt
@require_POST
def withdraw(request):
    try:

        # Parse the request body to get the IBAN
        data = json.loads(request.body)
        iban = data.get('iban')
        date = data.get('date')
        amount = data.get('amount')
        type = data.get('type')

        # Check if IBAN was provided
        if not iban:
            return JsonResponse({
                'error': 'IBAN is required',
                'status': 400
            }, status=400)

        # Try to get the account by IBAN
        account = Account.objects.get(iban=iban)
        if float(account.balance) >= float(amount):
            new_balance = float(account.balance) - float(amount)
            # Update the balance
            account.balance = new_balance
            account.save()

            # CREATE A TRANSACTION
            transaction = account.trasaction_set.create(date=date, amount=amount, type=type, balance=new_balance)

            # Return the transaction details in the response
            return JsonResponse({
                'transaction': {
                    'id': transaction.id,
                    'date': transaction.date,
                    'amount': transaction.amount,
                    'balance': transaction.balance,
                    'type': transaction.type,
                    'account_id': transaction.account.id
                },
                'status': 201
            }, status=201)
        else:
            return JsonResponse({
                'error': 'You dont have enough money!',
                'status': 404
            }, status=404)

    except Account.DoesNotExist:

        return JsonResponse({
            'error': 'Account not found',
            'status': 404
        }, status=404)

    except Exception as e:

        return JsonResponse({
            'error': f'An unexpected error occurred: {str(e)}',
            'status': 500
        }, status=500)


@csrf_exempt
@require_POST
def transfer(request):
    try:

        # Parse the request body to get the IBAN
        data = json.loads(request.body)
        or_iban = data.get('originIBAN')
        dest_iban = data.get('destIBAN')
        date = data.get('date')
        amount = data.get('amount')

        # Check if IBAN was provided
        if not dest_iban or not or_iban:
            return JsonResponse({
                'error': 'IBAN is required',
                'status': 400
            }, status=400)

        # Try to get the account by IBAN
        or_account = Account.objects.get(iban=or_iban)
        dest_account = Account.objects.get(iban=dest_iban)
        if float(or_account.balance) >= float(amount):
            new_balance = float(or_account.balance) - float(amount)

            # Update the balance in origin acc
            or_account.balance = new_balance
            or_account.save()

            # Update the balance in dest acc
            new_balance = float(dest_account.balance) + float(amount)
            dest_account.balance = new_balance
            dest_account.save()

            # CREATE A WITHDRAW TRANSACTION FOR THE ORIGIN ACCOUNT
            transaction = or_account.trasaction_set.create(date=date, amount=amount, type=1, balance=or_account.balance)

            # CREATE A DEPOSIT TRANSACTION FOR THE DESTINATION ACCOUNT
            dest_account.trasaction_set.create(date=date, amount=amount, type=0, balance=dest_account.balance)


            # Return the transaction details in the response
            return JsonResponse({
                'transaction': {
                    'id': transaction.id,
                    'date': transaction.date,
                    'amount': transaction.amount,
                    'balance': transaction.balance,
                    'type': transaction.type,
                    'account_id': transaction.account.id
                },
                'status': 201
            }, status=201)
        else:
            return JsonResponse({
                'error': 'You dont have enough money!',
                'status': 404
            }, status=404)

    except Account.DoesNotExist:

        return JsonResponse({
            'error': 'Account not found',
            'status': 404
        }, status=404)

    except Exception as e:

        return JsonResponse({
            'error': f'An unexpected error occurred: {str(e)}',
            'status': 500
        }, status=500)

@csrf_exempt
@require_POST
def get_transactions(request):
    try:
        # Parse the request body to get the IBAN and optional filters
        data = json.loads(request.body)
        iban = data.get('iban')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        transaction_type = data.get('type')

        # Try to get the account by IBAN
        account = Account.objects.get(iban=iban)

        # Get all transactions for the account
        transactions = account.trasaction_set.all()

        # Apply optional filters
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        if transaction_type is not None:
            transactions = transactions.filter(type=transaction_type)

        # Prepare the transactions data to be returned in the response
        transactions_data = [
            {
                'id': transaction.id,
                'date': transaction.date,
                'amount': transaction.amount,
                'balance': transaction.balance,
                'type': transaction.type,
            }
            for transaction in transactions
        ]

        # Return the transactions data in the response
        return JsonResponse({
            'transactions': transactions_data,
            'status': 200
        }, status=200)

    except Account.DoesNotExist:
        # If the account doesn't exist, return a 404 error
        return JsonResponse({
            'error': 'Account not found',
            'status': 404
        }, status=404)

    except Exception as e:
        # Handle any other unexpected errors
        return JsonResponse({
            'error': f'An unexpected error occurred: {str(e)}',
            'status': 500
        }, status=500)
