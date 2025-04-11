from datetime import datetime
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

from sqlalchemy.sql import text  # Import text từ SQLAlchemy

def get_transaction_history(wallet_id, limit=None):
    try:

        # Sử dụng text() để khai báo truy vấn SQL thuần
        sql = text("SELECT * FROM transactions WHERE wallet_id = :wallet_id ORDER BY created_at DESC")
        if limit:
            sql = text("SELECT * FROM transactions WHERE wallet_id = :wallet_id ORDER BY created_at DESC LIMIT :limit")
        
        params = {"wallet_id": wallet_id}
        if limit:
            params["limit"] = limit
        
        result = db.session.execute(sql, params)
        transactions = result.fetchall()
        
        if not transactions:
            return {"message": "No transaction history found"}, 404
        
        # Chuyển đổi kết quả thành danh sách
        result = [{
            "transaction_id": row.transaction_id,
            "transaction_type": row.transaction_type,
            "amount": float(row.amount),
            "status": row.status,
            "created_at": row.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for row in transactions]
        
        return {"wallet_id": wallet_id, "transactions": result}, 200
    except SQLAlchemyError as e:
        print("SQLAlchemy Error:", e)
        print(traceback.format_exc())
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


def test(wallet_id):
    try:
        # Tạo query để lấy danh sách giao dịch theo wallet_id, sắp xếp theo thời gian giảm dần
        transactions = db.session.query(Transaction).filter_by(wallet_id=wallet_id).order_by(Transaction.created_at.desc()).all()
        print(f"Query: {transactions}")  # Debug

        
        # Lấy danh sách giao dịch từ query
        # transactions = query.all()
        
        # # Nếu không có giao dịch nào, trả về thông báo lỗi
        # if not transactions:
        #     return {"message": "No transaction history found"}, 404
        
        # # Trả về danh sách giao dịch nguyên bản
        # result = [{
        #     "transaction_id": tx.transaction_id,
        #     "user_id": tx.user_id,  # Thêm user_id từ đối tượng Transaction
        #     "transaction_type": tx.transaction_type.value,
        #     "amount": float(tx.amount),
        #     "status": tx.status.value,
        #     "created_at": tx.created_at.strftime('%Y-%m-%d %H:%M:%S')
        # } for tx in transactions]
        
        return {
            "wallet_id": wallet_id,
            "transactions": 1  # Trả về danh sách giao dịch nguyên bản
        }, 200
    except SQLAlchemyError as e:
        print("SQLAlchemy Error:", e)
        print(traceback.format_exc())  # In ra stack trace để debug
        return {"error": str(e)}, 500