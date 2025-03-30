import datetime
import json
import requests

class Transaction:
    def __init__(self, description: str, amount: float, date: datetime.date):
        self.description = description.lower()
        self.amount = amount
        self.date = str(date)

    def __str__(self):
        return f"{self.description.capitalize()}: {self.amount} on {self.date}"

    def to_dict(self):
        return {"description": self.description, "amount": self.amount, "date": self.date}

class Account:
    FILE = 'database.json'

    def __init__(self, name: str, budget: int | float, currency: str = "USD"):
        self.name = name.lower()
        if currency.upper() in ExchangeRate.list_currency():
            self.currency = currency.upper()
        else:
            print("Available Currencies: ", ', '.join(ExchangeRate.list_currency()))
            raise ValueError("Enter a valid currency from the above list.")
        
        data = self.load_data()
        
        if self.name in data:
            self.transactions = [Transaction(t["description"], t["amount"], datetime.date.fromisoformat(t["date"])) for t in data[self.name]["transactions"]]
            self.budget = data[self.name]["budget"]
            self.currency = data[self.name]["currency"]
        else:
            self.budget = budget
            self.transactions = []
        
        self.save_to_file()

    def __str__(self):
        return f"Account: {self.name.capitalize()} | Budget: {self.budget} {self.currency}, Transactions: {len(self.transactions)}"

    def add_transaction(self, description: str, amount: int | float, date: datetime.date = datetime.date.today()):
        self.transactions.append(Transaction(description, amount, date))
        self.save_to_file()

    def balance(self) -> int | float:
        return self.budget - sum(t.amount for t in self.transactions)

    def save_to_file(self):
        data = self.load_data()
        data[self.name] = {
            "budget": self.budget,
            "currency": self.currency,
            "transactions": [t.to_dict() for t in self.transactions]
        }
        try:
            with open(self.FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise e

    @classmethod
    def load_data(cls):
        try:
            with open(cls.FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @classmethod
    def list_accounts(cls):
        return list(cls.load_data().keys())

class ExchangeRate:
    API = "https://api.exchangerate-api.com/v4/latest/USD"

    @classmethod
    def get_data(cls):
        try:
            response = requests.get(cls.API)
            response.raise_for_status()
            data = response.json()
            return data['rates']
        except requests.RequestException as e:
            print(f"Error fetching exchange rates {e}")
            return {"USD": 1.0, "INR": 74.0, "PKR": 160.0, "JPY": 110.0}  # Default rates if API fails

    @classmethod
    def list_currency(cls) -> list:
        return list(cls.get_data())
    
def main():
    print("Welcome to your Personal Finance Manager Dashboard!")
    while True:
        print("Below is a list of features:")
        print("1. Create a new account")
        print("2. View existing accounts")
        print("3. Add a transaction to an account")
        print("4. View account balance")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            name = input("Enter account name: ").strip()
            try:
                budget = float(input("Enter budget: ").strip())
            except ValueError:
                print("Invalid budget. Please enter a numeric value.")
                continue
            currency = input("Enter currency (default is USD): ").strip() or "USD"
            try:
                account = Account(name, budget, currency)
                print(f"Account '{name}' created successfully!")
            except ValueError as e:
                print(e)

        elif choice == "2":
            accounts = Account.list_accounts()
            if accounts:
                print("Existing accounts:")
                for acc in accounts:
                    print(f"- {acc.capitalize()}")
            else:
                print("No accounts found.")

        elif choice == "3":
            name = input("Enter account name: ").strip()
            data = Account.load_data()
            if name.lower() in data:
                try:
                    date_input = input("Enter transaction date (YYYY-MM-DD) or leave blank for today: ").strip()
                    date = datetime.date.fromisoformat(date_input) if date_input else datetime.date.today()
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
                    continue
                description = input("Enter transaction description: ").strip()
                try:
                    amount = float(input("Enter transaction amount: ").strip())
                except ValueError:
                    print("Invalid amount. Please enter a numeric value.")
                    continue
                account = Account(name, data[name.lower()]["budget"], data[name.lower()]["currency"])
                account.add_transaction(description, amount, date)
                print("Transaction added successfully!")
            else:
                print("Account not found.")

        elif choice == "4":
            name = input("Enter account name: ").strip()
            data = Account.load_data()
            if name.lower() in data:
                account = Account(name, data[name.lower()]["budget"], data[name.lower()]["currency"])
                print(f"Account Balance: {account.balance()} {account.currency}")
            else:
                print("Account not found.")

        elif choice == "5":
            print("Exiting the application. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()