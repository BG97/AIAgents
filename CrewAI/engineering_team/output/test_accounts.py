```python
import unittest
from accounts import Account, get_share_price

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account('123ABC', 1000)

    def test_deposit_funds(self):
        self.account.deposit_funds(500)
        self.assertEqual(self.account.balance, 1500)
        with self.assertRaises(ValueError):
            self.account.deposit_funds(-200)

    def test_withdraw_funds(self):
        result = self.account.withdraw_funds(300)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 700)
        result = self.account.withdraw_funds(800)
        self.assertFalse(result)
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(-100)

    def test_buy_shares(self):
        self.account.deposit_funds(5000)
        result = self.account.buy_shares('AAPL', 10)
        self.assertTrue(result)
        self.assertEqual(self.account.holdings['AAPL'], 10)
        with self.assertRaises(ValueError):
            self.account.buy_shares('TSLA', -5)

    def test_sell_shares(self):
        self.account.buy_shares('GOOGL', 1)
        result = self.account.sell_shares('GOOGL', 1)
        self.assertTrue(result)
        self.assertNotIn('GOOGL', self.account.holdings)
        with self.assertRaises(ValueError):
            self.account.sell_shares('TSLA', -2)

    def test_get_portfolio_value(self):
        self.account.deposit_funds(5000)
        self.account.buy_shares('TSLA', 2)
        self.assertAlmostEqual(self.account.get_portfolio_value(), 9400, places=2)

    def test_get_profit_or_loss(self):
        self.account.deposit_funds(4000)
        self.account.buy_shares('TSLA', 1)
        self.assertAlmostEqual(self.account.get_profit_or_loss(), 300, places=2)

    def test_get_holdings(self):
        self.account.buy_shares('AAPL', 3)
        holdings = self.account.get_holdings()
        self.assertIn('AAPL', holdings)
        self.assertEqual(holdings['AAPL'], 3)

    def test_list_transactions(self):
        self.account.deposit_funds(500)
        transactions = self.account.list_transactions()
        self.assertTrue(len(transactions) > 0)
        self.assertEqual(transactions[0]['type'], 'deposit')

if __name__ == '__main__':
    unittest.main()
```