import hashlib
import hmac
import random
from urllib.parse import urlencode
from datetime import datetime
import urllib
from app.config import Config
from app.models import TransactionStatusEnum, TransactionTypeEnum, Wallet, db, Transaction, BalanceHistory
from sqlalchemy.exc import SQLAlchemyError




def __hmacsha512(key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def generate_transaction_id(user_id: int) -> int:
    timestamp = datetime.now().strftime("%y%m%d%H%M%S")
    user_part = str(user_id).zfill(4)[-4:]
    rand_part = str(random.randint(0, 999)).zfill(3)
    transaction_id_str = f"{timestamp}{user_part}{rand_part}"
    return int(transaction_id_str)


def create_vnpay_payment_url(amount, wallet_id):
    try:
        wallet = db.session.query(Wallet).filter_by(wallet_id=wallet_id).first()
        if not wallet:
            return {"error": "Wallet not found"}, 404
        
        pla=wallet.user_id
        order_id = generate_transaction_id(pla)
        
        transaction = Transaction(
            transaction_id=order_id,
            user_id=pla,
            wallet_id=wallet_id,
            transaction_type=TransactionTypeEnum.deposit.value,
            amount=amount,
            status=TransactionStatusEnum.pending.value,
            destination="vnpay"  # Cột mới đã thêm
        )
        db.session.add(transaction)
        db.session.commit()

        vnp_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': Config.VNP_TMNCODE,
            'vnp_Amount': str(int(amount) * 100),
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
            'vnp_CurrCode': 'VND',
            'vnp_IpAddr': '127.0.0.1',
            'vnp_Locale': 'vn',
            'vnp_OrderInfo': f'Thanh toan don hang {order_id}',
            'vnp_OrderType': 'other',
            'vnp_ReturnUrl': Config.VNP_RETURN_URL,
            'vnp_TxnRef': str(order_id),
        }

        sorted_params = sorted(vnp_params.items())


        seq = 0
        for key, val in sorted_params:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        hashValue = __hmacsha512(Config.VNP_HASH_SECRET, queryString)
        return Config.VNP_URL + "?" + queryString + '&vnp_SecureHashType=SHA512&vnp_SecureHash=' + hashValue
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def update_deposit(transaction, amount):
    try:
        transaction.status = TransactionStatusEnum.successful.value
        wallet=db.session.query(Wallet).filter_by(wallet_id=transaction.wallet_id).first()
        
        previous_balance = wallet.balance
        new_balance = wallet.balance + amount
        transaction_id = transaction.transaction_id
        wallet.balance = new_balance

        balance_history = BalanceHistory(
            wallet_id=transaction.wallet_id,
            transaction_id=transaction_id,
            previous_balance=previous_balance,
            new_balance=new_balance
        )
        
        db.session.add(balance_history)
        db.session.commit()
        
        return  float(new_balance)
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": str(e)}, 500








    




