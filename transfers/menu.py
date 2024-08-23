import os
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codesherpas.settings")

import django
django.setup()

import requests
def iban_check(iban):
    # Remove spaces and to upper case
    iban = iban.replace(' ', '').upper()

    # Check the length of the Spanish IBAN
    if len(iban) != 24:
        return False

    # Check the country code
    elif not iban.startswith('ES'):
        return False
    else:
        return True

def create_account(iban):
    url = 'http://localhost:8000/createaccount/'
    iban_data = {'iban': iban}

    response = requests.post(url, json=iban_data)

    if response.status_code == 201:
        print("Account created:", response.json())
        return response.json()
    elif response.status_code == 400:
        print("Error:", response.json().get('error'))
        return response.json()
    else:
        print("An unexpected error occurred:", response.json().get('error'))
def check_account(iban):
    # Define the URL where the Django view is located
    url = 'http://localhost:8000/account/'

    # Prepare the data to be sent in the POST request
    iban_data = {
        'iban': iban
    }

    try:
        # Make the POST request with the IBAN data
        response = requests.post(url, json=iban_data)

        # Check the status code and handle the response accordingly
        if response.status_code == 200:
            # Return the account details
            return response.json()
        elif response.status_code == 404:
            # Return the created account
            print("Couldn't find the account. Creating it...")
            # CREATES THE ACCOUNT
            createResp = create_account(iban)
            return createResp
        else:
            # Handle any other unexpected error
            return {"Error:" f"An unexpected error occurred: {response.json().get('error')}"}

    except requests.exceptions.RequestException as e:
        # Handle any requests exceptions (e.g., network issues)
        return {"Error:" f"Request failed: {str(e)}"}





def deposit(iban, date, amount, transactionType):
    url = 'http://localhost:8000/deposit/'
    deposit_data = {
        'iban': iban,
        'date': date,
        'amount': amount,
        'type': transactionType
    }

    response = requests.post(url, json=deposit_data)

    if response.status_code == 201:
        transaction = response.json().get('transaction', {})
        # Extract and print the relevant fields from the response
        print(f"Deposit successful:\nDate: {transaction.get('date')}\nAmount: + {transaction.get('amount')}\nBalance: {transaction.get('balance')}")
    elif response.status_code == 400:
        print("Invalid input:", response.json().get('error'))
    else:
        print("An unexpected error occurred:", response.json().get('error'))


def withdraw(iban, date, amount, transactionType):
    url = 'http://localhost:8000/withdraw/'
    withdraw_data = {
        'iban': iban,
        'date': date,
        'amount': amount,
        'type': transactionType
    }

    response = requests.post(url, json=withdraw_data)

    if response.status_code == 201:
        transaction = response.json().get('transaction', {})
        # Extract and print the relevant fields from the response
        print(f"Withdraw successful:\nDate: {transaction.get('date')}\nAmount: - {transaction.get('amount')}\nBalance: {transaction.get('balance')}")
    elif response.status_code == 400:
        print("Invalid input:", response.json().get('error'))
    else:
        print("An unexpected error occurred:", response.json().get('error'))

def transfer_money(or_iban, dest_iban, date, amount):
    url = 'http://localhost:8000/transfer/'  # Adjust the URL to match your Django app's URL configuration
    transfer_data = {
        'originIBAN': or_iban,
        'destIBAN': dest_iban,
        'date': date,
        'amount': amount
    }

    try:
        response = requests.post(url, json=transfer_data)
        if response.status_code == 201:
            transaction = response.json().get('transaction', {})
            print(f"Transfer successful:\nDate: {transaction.get('date')}\nAmount: - {transaction.get('amount')}\nNew Balance: {transaction.get('balance')}")
        elif response.status_code == 400:
            print("Invalid input. Ensure all required fields are provided.")
        elif response.status_code == 404:
            print("Error: Account not found or insufficient funds.")
        else:
            print(f"Unexpected error occurred. Status code: {response.status_code}")
            print("Error details:", response.json().get('error'))
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")


def printTransactions(data, ascending):
    print("------- LIST OF TRANSACTIONS ---------")
    data = data.get('transactions', [])

    # Print header
    print(f"{'Date':<12} {'Amount':<7} {'Balance':<7} {'Type':<7}")

    # Sort data by date in ascending or descending order based on the 'ascending' flag
    data.sort(key=lambda x: x['date'], reverse=not ascending)

    # Convert date strings to datetime objects after sorting
    for entry in data:
        entry['date'] = datetime.strptime(entry['date'], "%Y-%m-%d")

    # Print each record
    for entry in data:
        formatted_date = entry['date'].strftime("%d.%m.%Y")

        if entry['type'] == 0:
            entry['type'] = "Deposit"
            # Format amount with a sign
            amount = f"+{entry['amount']:.0f}"
        else:
            entry['type'] = "Withdrawal"
            # Format amount with a sign
            amount = f"-{entry['amount']:.0f}"

        print(f"{formatted_date:<12} {amount:<7} {entry['balance']:<7.0f} {entry['type']}")

def fetch_transactions(iban):
    # Define the URL where the POST request should be sent
    url = 'http://localhost:8000/get_transactions/'  # Update this with your actual URL if different

    # Prepare the request payload
    payload = {
        'iban': iban
    }

    # Send the POST request
    try:
        response = requests.post(url, json=payload)
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # Uncomment to Print or process the transaction details
            '''for transaction in transactions:
                print(f"Transaction ID: {transaction['id']}")
                print(f"Date: {transaction['date']}")
                print(f"Amount: {transaction['amount']}")
                print(f"Balance: {transaction['balance']}")
                print(f"Type: {transaction['type']}")
                print('---')'''
            return data
        else:
            # Handle unsuccessful requests
            print(f"Error {response.status_code}: {response.json().get('error')}")
            return response.json().get('error')

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")



def is_valid_date(date_str):
    """Check if date its in format YYYY-MM-DD."""
    try:
        if date_str:
            datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
def get_user_input():
    # Ask the user if he wants to deposit or withdraw
    transaction_type = input("Do you want to see Deposits or Withdraws? (type 'd' or 'w'): ").strip().lower()
    if transaction_type != 'd' and transaction_type != 'w':
        print("Wrong type of transaction! Will show all transactions.")
        transaction_type = None
    elif transaction_type == 'd':
        transaction_type = 0
    elif transaction_type == 'w':
        transaction_type = 1
    # Ask for start date
    start_date = input("Introduce the start date (YYYY-MM-DD) or press enter in case you don't want: ").strip()
    if start_date == "" or not is_valid_date(start_date):
        start_date = None
        print("Invalid date format. No start date added")

    # Ask for end  date
    end_date = input("Introduce the end date (YYYY-MM-DD) or press enter in case you don't want: ").strip()
    if end_date == "" or not is_valid_date(end_date):
        end_date = None
        print("Invalid date format. No end date added")

    print("TRANSACTION TYPE: ", transaction_type)
    return transaction_type, start_date, end_date


def fetch_filtered_transactions(iban, start_date=None, end_date=None, transaction_type=None):
    url = 'http://localhost:8000/get_transactions/'  # Update with your actual URL

    # Prepare the request payload
    payload = {
        'iban': iban,
    }
    if start_date:
        payload['start_date'] = start_date
    if end_date:
        payload['end_date'] = end_date
    if transaction_type is not None:
        payload['type'] = transaction_type

    # Send the POST request
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        # Check if the request was successful
        if response.status_code == 200:

            # Uncomment to Print or process the transaction details

            '''transactions = data.get('transactions', [])
            for transaction in transactions:
                print(f"Transaction ID: {transaction['id']}")
                print(f"Date: {transaction['date']}")
                print(f"Amount: {transaction['amount']}")
                print(f"Balance: {transaction['balance']}")
                print(f"Type: {transaction['type']}")
                print('---')'''
            return data
        else:
            print(f"Error {response.status_code}: {response.json().get('error')}")
            return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")



def show_menu():
    try:
        while True:
            iban = input("What is your IBAN? ")
            checkIban = iban_check(iban)

            if checkIban:
                # Remove spaces and to upper case
                iban = iban.replace(' ', '').upper()

                # RETURNS A JSON WITH THE RESPONSE
                resp = check_account(iban)

                if resp.get('status') == 201:

                    print("\nMenu:")
                    print("1. Deposit money")
                    print("2. Withdraw money")
                    print("3. Transfer money")
                    print("4. Show transactions list")
                    print("5. Search movements")
                    print("6. Exit")

                    choice = input("Select an option (1/2/3/4/5/6): ")

                    if choice == "1":
                        # Create a transaction
                        try:

                            amount = input("How much do you want to deposit? ")
                            date = input("Input the desired date in format 'YYYY-mm-dd': ")
                            valid_date = is_valid_date(date)
                            if valid_date:
                                deposit(iban, date, float(amount), 0)
                            else:
                                print("Invalid date format, try again")

                        except ValueError:
                            print(f"Invalid input: Please enter a valid number.")

                    elif choice == "2":
                        try:

                            amount = input("How much do you want to withdraw? ")
                            date = input("Input the desired date in format 'YYYY-mm-dd': ")
                            valid_date = is_valid_date(date)
                            if valid_date:
                                withdraw(iban, date, float(amount), 1)
                            else:
                                print("Invalid date format, try again")

                        except ValueError:
                            print(f"Invalid input: Please enter a valid number.")

                    elif choice == "3":
                        try:

                            IBANToTransfer = input("Introduce the IBAN of the transfer: ")
                            checkTransferIban = iban_check(IBANToTransfer)

                            if checkTransferIban:
                                # Remove spaces and to upper case
                                IBANToTransfer = IBANToTransfer.replace(' ', '').upper()
                                resp = check_account(IBANToTransfer)


                                if resp.get('status') == 201:
                                    if IBANToTransfer != iban:
                                        amount = input("How much do you want to transfer? ")
                                        date = input("Input the desired date in format 'YYYY-mm-dd': ")
                                        valid_date = is_valid_date(date)
                                        if valid_date:
                                            transfer_money(iban, IBANToTransfer, date, amount)
                                        else:
                                            print("Invalid date format, try again")

                                    else:
                                        print("You can't transfer money to yourself!")

                                else:
                                    print("Error with transfer IBAN try again")

                            else:
                                print("Invalid IBAN try again")
                        except ValueError:
                            print(f"Invalid input: Please enter a valid number.")

                    elif choice == "4":

                        sort_order = input("Do you want to show transactions in ascending or descending order? (a/d) (Enter for default): ").lower()
                        data = fetch_transactions(iban)
                        if sort_order == 'a':
                            printTransactions(data, ascending=True)
                        elif sort_order == 'd':
                            printTransactions(data, ascending=False)
                        else:
                            print("Invalid choice. Showing transactions in descending order by default.")
                            printTransactions(data, ascending=False)

                    elif choice == "5":
                        searchSortOrder = input("Do you want to show transactions in ascending or descending order? (a/d) (Enter for default): ").lower()

                        transactionType, start_date, end_date = get_user_input()
                        data = fetch_filtered_transactions(iban, start_date, end_date, transactionType)
                        if data.get('status') != 404 and data.get('status') != 500:

                            if searchSortOrder == 'a':
                                printTransactions(data, ascending=True)
                            elif searchSortOrder == 'd':
                                printTransactions(data, ascending=False)
                            else:
                                print("Invalid choice. Showing transactions in descending order by default.")
                                printTransactions(data, ascending=False)
                        else:
                            print("Transactions not found!")

                    elif choice == "6":
                        print("Exiting the program...")
                        break
                    else:
                        print("Invalid option! Try again!")
                else:
                    print("ERROR WITH IBAN TRY AGAIN")
            else:
                print("Invalid IBAN try again")

    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Exiting...")


if __name__ == "__main__":
    # Show the menu
    show_menu()
