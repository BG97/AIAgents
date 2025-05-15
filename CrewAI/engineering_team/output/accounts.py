class Account:
    def __init__(self, account_id: str, initial_deposit: float) -> None:
        self.account_id = account_id
        self.balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.holdings = {}
        self.transactions = []

    def deposit_funds(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError('Deposit amount must be positive.')
        self.balance += amount
        self._add_transaction('deposit', '', 0, amount)

    def withdraw_funds(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError('Withdrawal amount must be positive.')
        if self.balance >= amount:
            self.balance -= amount
            self._add_transaction('withdraw', '', 0, -amount)
            return True
        return False

    def buy_shares(self, symbol: str, quantity: int) -> bool:
        if quantity <= 0:
            raise ValueError('Quantity must be positive.')
        share_price = get_share_price(symbol)
        total_price = share_price * quantity
        if self.balance >= total_price:
            self.balance -= total_price
            self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
            self._add_transaction('buy', symbol, quantity, -total_price)
            return True
        return False

    def sell_shares(self, symbol: str, quantity: int) -> bool:
        if quantity <= 0:
            raise ValueError('Quantity must be positive.')
        if self.holdings.get(symbol, 0) >= quantity:
            share_price = get_share_price(symbol)
            total_price = share_price * quantity
            self.balance += total_price
            self.holdings[symbol] -= quantity
            if self.holdings[symbol] == 0:
                del self.holdings[symbol]
            self._add_transaction('sell', symbol, quantity, total_price)
            return True
        return False

    def get_portfolio_value(self) -> float:
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            total_value += get_share_price(symbol) * quantity
        return total_value

    def get_profit_or_loss(self) -> float:
        return self.get_portfolio_value() - self.initial_deposit

    def get_holdings(self) -> dict:
        return self.holdings.copy()

    def list_transactions(self) -> list:
        return self.transactions.copy()

    def _add_transaction(self, transaction_type: str, symbol: str, quantity: int, price: float) -> None:
        transaction = {
            'type': transaction_type,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'balance': self.balance
        }
        self.transactions.append(transaction)

def get_share_price(symbol: str) -> float:
    prices = {
        'AAPL': 150.0,
        'TSLA': 700.0,
        'GOOGL': 2800.0
    }
    return prices.get(symbol, 0.0)