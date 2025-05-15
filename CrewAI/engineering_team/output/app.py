
# app.py

import gradio as gr
from accounts import Account, get_share_price

# Initialize the account with a test user and a deposit
account = Account(account_id="user123", initial_deposit=10000.0)

def create_account(user_id, initial_deposit):
    global account
    account = Account(account_id=user_id, initial_deposit=float(initial_deposit))
    return f"Account created for {user_id} with initial deposit of {initial_deposit}"

def deposit_funds(amount):
    try:
        account.deposit_funds(float(amount))
        return f"Deposited {amount}. Current balance: {account.balance}"
    except ValueError as e:
        return str(e)

def withdraw_funds(amount):
    try:
        if account.withdraw_funds(float(amount)):
            return f"Withdrew {amount}. Current balance: {account.balance}"
        else:
            return f"Insufficient funds to withdraw {amount}."
    except ValueError as e:
        return str(e)

def buy_shares(symbol, quantity):
    try:
        if account.buy_shares(symbol, int(quantity)):
            return f"Bought {quantity} shares of {symbol}. Current balance: {account.balance}"
        else:
            return f"Insufficient funds to buy {quantity} shares of {symbol}."
    except ValueError as e:
        return str(e)

def sell_shares(symbol, quantity):
    try:
        if account.sell_shares(symbol, int(quantity)):
            return f"Sold {quantity} shares of {symbol}. Current balance: {account.balance}"
        else:
            return f"Cannot sell {quantity} shares of {symbol}. Not enough holdings."
    except ValueError as e:
        return str(e)

def get_portfolio_value():
    return f"Total portfolio value: {account.get_portfolio_value()}"

def get_profit_or_loss():
    return f"Profit or Loss: {account.get_profit_or_loss()}"

def list_holdings():
    holdings = account.get_holdings()
    return f"Holdings: {holdings}"

def list_transactions():
    transactions = account.list_transactions()
    return f"Transactions: {transactions}"

with gr.Blocks() as demo:
    gr.Markdown("# Trading Simulation Platform")

    with gr.Tab("Account Management"):
        user_id = gr.Textbox(label="User ID")
        initial_deposit = gr.Number(label="Initial Deposit")
        create_btn = gr.Button("Create Account")
        create_out = gr.Textbox(label="Output", interactive=False)
        create_btn.click(create_account, [user_id, initial_deposit], create_out)

        deposit_amt = gr.Number(label="Deposit Amount")
        deposit_btn = gr.Button("Deposit")
        deposit_out = gr.Textbox(label="Output", interactive=False)
        deposit_btn.click(deposit_funds, [deposit_amt], deposit_out)

        withdraw_amt = gr.Number(label="Withdraw Amount")
        withdraw_btn = gr.Button("Withdraw")
        withdraw_out = gr.Textbox(label="Output", interactive=False)
        withdraw_btn.click(withdraw_funds, [withdraw_amt], withdraw_out)

    with gr.Tab("Trading"):
        symbol = gr.Dropdown(['AAPL', 'TSLA', 'GOOGL'], label="Share Symbol")
        quantity = gr.Number(label="Quantity")

        buy_btn = gr.Button("Buy Shares")
        buy_out = gr.Textbox(label="Output", interactive=False)
        buy_btn.click(buy_shares, [symbol, quantity], buy_out)

        sell_btn = gr.Button("Sell Shares")
        sell_out = gr.Textbox(label="Output", interactive=False)
        sell_btn.click(sell_shares, [symbol, quantity], sell_out)

    with gr.Tab("Reports"):
        portfolio_btn = gr.Button("Get Portfolio Value")
        portfolio_out = gr.Textbox(label="Output", interactive=False)
        portfolio_btn.click(get_portfolio_value, [], portfolio_out)

        profit_loss_btn = gr.Button("Get Profit or Loss")
        profit_loss_out = gr.Textbox(label="Output", interactive=False)
        profit_loss_btn.click(get_profit_or_loss, [], profit_loss_out)

        holdings_btn = gr.Button("List Holdings")
        holdings_out = gr.Textbox(label="Output", interactive=False)
        holdings_btn.click(list_holdings, [], holdings_out)

        transactions_btn = gr.Button("List Transactions")
        transactions_out = gr.Textbox(label="Output", interactive=False)
        transactions_btn.click(list_transactions, [], transactions_out)

demo.launch()
