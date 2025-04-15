from flask import Blueprint, request, jsonify
import urllib
from app.services.transaction_service import withdraw, transfer_money
from app.utils.vnpay_payment import __hmacsha512, create_vnpay_payment_url, update_deposit
from app.database import db
from flask import request, jsonify
import hmac, hashlib
from urllib.parse import urlencode
from app.models import Transaction, TransactionStatusEnum, Wallet
from app.config import Config
from sqlalchemy.exc import SQLAlchemyError




# Use a unique name for the Blueprint
wallet_bp_t = Blueprint('wallet_transactions', __name__)

@wallet_bp_t.route('/wallet/deposit', methods=['POST'])
def deposit_money():
    data = request.get_json()
    wallet_id = data.get('wallet_id')
    amount = data.get('amount')
    payment_url = create_vnpay_payment_url(amount, wallet_id)
    if not wallet_id or not amount:
        return jsonify({"error": "wallet_id and amount are required"}), 400
    # return jsonify(deposit(wallet_id, amount))
    return jsonify({"payment_url": payment_url})

@wallet_bp_t.route('/wallet/transfer', methods=['POST'])
def transfer_money_to_someone():
    data = request.get_json()
    sender_wallet_id = data.get('sender_wallet_id')
    receiver_wallet_id = data.get('receiver_wallet_id')
    amount = data.get('amount')

    if not sender_wallet_id or not receiver_wallet_id or not amount:
        return jsonify({"error": "sender_wallet_id, receiver_wallet_id and amount are required"}), 400

    # Call the transfer function from the service layer
    result = transfer_money(sender_wallet_id, receiver_wallet_id, amount)
    
    return jsonify(result)

@wallet_bp_t.route('/wallet/withdraw', methods=['POST'])
def withdraw_money():
    data = request.get_json()
    wallet_id = data.get('wallet_id')
    amount = data.get('amount')
    if not wallet_id or not amount:
        return jsonify({"error": "wallet_id and amount are required"}), 400
    return jsonify(withdraw(wallet_id, amount))

@wallet_bp_t.route('/wallet/vnpay_return', methods=['GET'])
def vnpay_return():
    vnp_params = request.args.to_dict()
    vnp_secure_hash = vnp_params.pop('vnp_SecureHash', None)

    # Bước 1: Xác minh chữ ký
    sorted_params = sorted(vnp_params.items())
    seq = 0
    for key, val in sorted_params:
        if seq == 1:
            queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
        else:
            seq = 1
            queryString = key + '=' + urllib.parse.quote_plus(str(val))

    generated_hash = __hmacsha512(Config.VNP_HASH_SECRET, queryString)

    if generated_hash != vnp_secure_hash:
        return jsonify({"message": "Chữ ký không hợp lệ!"}), 400



    # Bước 2: Kiểm tra mã giao dịch
    order_id = vnp_params.get("vnp_TxnRef")
    amount = int(vnp_params.get("vnp_Amount", 0)) // 100  # đổi về đơn vị VND

    # transaction=db.session.query(Transaction).filter_by(transaction_id=order_id).first()
    transaction = db.session.query(Transaction).filter_by(transaction_id=order_id).first()

    print(transaction)

    if not transaction:
        return jsonify({"message": "Không tìm thấy giao dịch!"}), 404

    if transaction.status == TransactionStatusEnum.successful.value:
        return jsonify({"message": "Giao dịch đã được xử lý trước đó!"})


    # # Bước 3: Cập nhật trạng thái và cộng tiền
    result = update_deposit(transaction, amount)
    
    return jsonify({
        "message": "Thanh toán thành công!",
        "order_id": order_id,
        "amount": amount,
        "new_balance": result # Lấy giá trị new_balance từ result
    }), 200
