from app.models import db, Wallet, Transaction, TransactionTypeEnum, TransactionStatusEnum, BalanceHistory
from sqlalchemy.exc import SQLAlchemyError


def deposit(wallet_id, amount):
    try:
        wallet = Wallet.query.get(wallet_id)
        if not wallet:
            return {"error": "Wallet not found"}, 404
        
        previous_balance = wallet.balance
        new_balance = wallet.balance + amount
        
        transaction = Transaction(
            user_id=wallet.user_id,
            wallet_id=wallet_id,
            transaction_type=TransactionTypeEnum.DEPOSIT.value,
            amount=amount,
            status=TransactionStatusEnum.SUCCESSFUL.value
        )
        db.session.add(transaction)
        db.session.flush()  # Đẩy dữ liệu vào database nhưng chưa commit, giúp lấy transaction_id

        transaction_id = transaction.transaction_id
        wallet.balance = new_balance
        balance_history = BalanceHistory(
            wallet_id=wallet_id,
            transaction_id=transaction_id,
            previous_balance=previous_balance,
            new_balance=new_balance
        )
        
        db.session.add(balance_history)
        db.session.commit()
        
        return {"message": "Deposit successful", "new_balance": float(new_balance)}, 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def withdraw(wallet_id, amount):
    try:
        wallet = Wallet.query.get(wallet_id)
        if not wallet:
            return {"error": "Wallet not found"}, 404
        if wallet.balance < amount:
            return {"error": "Insufficient balance"}, 400
        
        previous_balance = wallet.balance
        new_balance = wallet.balance - amount
        
        transaction = Transaction(
            user_id=wallet.user_id,
            wallet_id=wallet_id,
            transaction_type=TransactionTypeEnum.WITHDRAWAL.value,
            amount=amount,
            status=TransactionStatusEnum.SUCCESSFUL.value
        )

        db.session.add(transaction)
        db.session.flush() 
        wallet.balance = new_balance
        balance_history = BalanceHistory(
            wallet_id=wallet_id,
            transaction_id=transaction.transaction_id,
            previous_balance=previous_balance,
            new_balance=new_balance
        )
        db.session.add(balance_history)
        db.session.commit()
        
        return {"message": "Withdrawal successful", "new_balance": float(new_balance)}, 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": str(e)}, 500
