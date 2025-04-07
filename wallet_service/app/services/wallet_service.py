from app.models import db, User, Wallet, Transaction, TransactionTypeEnum, TransactionStatusEnum, BalanceHistory
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
import traceback

# def create_wallet(user_id):
#     try:
#         if Wallet.query.filter_by(user_id=user_id).first():
#             return {"error": "Wallet already exists"}, 400
        
#         new_wallet = Wallet(user_id=user_id, balance=0.00)
#         db.session.add(new_wallet)
#         db.session.commit()
#         return {"message": "Wallet created successfully", "wallet_id": new_wallet.wallet_id}, 201
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         print(traceback.format_exc())
#         print(f"Received user_id type: {type(user_id)}, value: {user_id}")
#         return {"error": str(e)}, 500



def create_wallet(user_id):
    try:
        print(f"Checking existing wallet for user_id: {user_id}")
        
        existing_wallet = Wallet.query.filter_by(user_id=user_id).first()
        print(f"Existing wallet: {existing_wallet}")  # Debug

        if existing_wallet:
            return {"error": "Wallet already exists"}, 400

        print("Creating new wallet...")
        new_wallet = Wallet(user_id=user_id, balance=0.00)
        db.session.add(new_wallet)
        db.session.commit()
        
        return {"message": "Wallet created successfully", "wallet_id": new_wallet.wallet_id}, 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        print(traceback.format_exc())
        print(f"Received user_id type: {type(user_id)}, value: {user_id}")
        return {"error": str(e)}, 500






def get_wallet_balance(wallet_id):
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        return {"error": "Wallet not found"}, 404
    return {"wallet_id": wallet.wallet_id, "balance": float(wallet.balance)}, 200

def get_transaction_history(wallet_id, limit=10):
    try:
        transactions = Transaction.query.filter_by(wallet_id=wallet_id).order_by(Transaction.created_at.desc()).limit(limit).all()
        if not transactions:
            return {"message": "No transaction history found"}, 404
        
        history = [{
            "transaction_id": tx.transaction_id,
            "transaction_type": tx.transaction_type.value,
            "amount": float(tx.amount),
            "status": tx.status.value,
            "created_at": tx.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for tx in transactions]
        
        return {"wallet_id": wallet_id, "transactions": history}, 200
    except SQLAlchemyError as e:
        return {"error": str(e)}, 500

def search_transaction(wallet_id, transaction_id=None, transaction_type=None, amount=None, status=None, start_date=None, end_date=None):
    try:
        filters = [Transaction.wallet_id == wallet_id]
        if transaction_id:
            filters.append(Transaction.transaction_id == transaction_id)
        if transaction_type:
            filters.append(Transaction.transaction_type == transaction_type)
        if amount:
            filters.append(Transaction.amount == amount)
        if status:
            filters.append(Transaction.status == status)
        if start_date and end_date:
            filters.append(Transaction.created_at.between(start_date, end_date))
        
        transactions = Transaction.query.filter(and_(*filters)).order_by(Transaction.created_at.desc()).all()
        if not transactions:
            return {"message": "No transactions found"}, 404
        
        result = [{
            "transaction_id": tx.transaction_id,
            "transaction_type": tx.transaction_type.value,
            "amount": float(tx.amount),
            "status": tx.status.value,
            "created_at": tx.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for tx in transactions]
        
        return {"wallet_id": wallet_id, "transactions": result}, 200
    except SQLAlchemyError as e:
        return {"error": str(e)}, 500


