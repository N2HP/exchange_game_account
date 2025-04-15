from app.models import db, Wallet, Transaction, TransactionTypeEnum, TransactionStatusEnum, BalanceHistory
from sqlalchemy.exc import SQLAlchemyError

from app.utils.vnpay_payment import generate_transaction_id



def transfer_money(sender_wallet_id, receiver_wallet_id, amount):
    try:
        sender_wallet = Wallet.query.get(sender_wallet_id)
        receiver_wallet = Wallet.query.get(receiver_wallet_id)

        if not sender_wallet or not receiver_wallet:
            return {"error": "Wallet not found"}, 404

        if sender_wallet.balance < amount:
            return {"error": "Insufficient balance"}, 400

        previous_sender_balance = sender_wallet.balance
        previous_receiver_balance = receiver_wallet.balance
        
        new_sender_balance = sender_wallet.balance - amount
        new_receiver_balance = receiver_wallet.balance + amount
        
        pla1=generate_transaction_id(sender_wallet.user_id)
        sender_transaction = Transaction(
            transaction_id=pla1,
            user_id=sender_wallet_id,
            wallet_id=sender_wallet_id,
            transaction_type=TransactionTypeEnum.transfer.value,
            amount=amount,
            status=TransactionStatusEnum.successful.value,
            destination="seller_" + str(receiver_wallet_id)  
        )

        db.session.add(sender_transaction)
        db.session.flush()
        
        pla2=generate_transaction_id(sender_wallet.user_id)
        receiver_transaction = Transaction(
            transaction_id=pla2,
            user_id=receiver_wallet_id,
            wallet_id=receiver_wallet_id,
            transaction_type=TransactionTypeEnum.transfer.value,
            amount=amount,
            status=TransactionStatusEnum.successful.value,
            destination="buyer_"+ str(sender_wallet_id )
        )

        db.session.add(receiver_transaction)
        db.session.flush()   
        
        sender_wallet.balance = new_sender_balance
        receiver_wallet.balance = new_receiver_balance
        
        balance_history_sender = BalanceHistory(
            wallet_id=sender_wallet_id,
            transaction_id=pla1,
            previous_balance=previous_sender_balance,
            new_balance=new_sender_balance
        )
        
        balance_history_receiver = BalanceHistory(
            wallet_id=receiver_wallet_id,
            transaction_id=pla2,
            previous_balance=previous_receiver_balance,
            new_balance=new_receiver_balance
        )
        
        db.session.add(balance_history_sender)
        db.session.add(balance_history_receiver)
        
        db.session.commit()
        
        return {"message": "Transfer successful", "new_sender_balance": float(new_sender_balance), "new_receiver_balance": float(new_receiver_balance)}, 200
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
            transaction_type=TransactionTypeEnum.withdrawal.value,
            amount=amount,
            status=TransactionStatusEnum.successful.value
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
