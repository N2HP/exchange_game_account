from flask import Blueprint, request, jsonify
import urllib
from app.services.transaction_service import escrow_hold_money, release_escrow_to_seller, withdraw, transfer_money
from app.utils.vnpay_payment import __hmacsha512, create_vnpay_payment_url, update_deposit
from app.database import db
from flask import request, jsonify
import hmac, hashlib
from urllib.parse import urlencode
from app.models import Transaction, TransactionStatusEnum, Wallet
from app.config import Config
from sqlalchemy.exc import SQLAlchemyError

from app.kafka.producer import send_notification




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


@wallet_bp_t.route('/wallet/hold_money', methods=['POST'])
def hold_money():
    data = request.get_json()
    buyer_wallet_id = data.get('buyer_wallet_id')
    seller_wallet_id = data.get('seller_wallet_id')
    amount = data.get('amount')
    if not buyer_wallet_id or not seller_wallet_id or not amount:
        return jsonify({"error": "buyer_wallet_id, seller_wallet_id and amount are required"}), 400
    return jsonify(escrow_hold_money(buyer_wallet_id, seller_wallet_id, amount))


@wallet_bp_t.route('/wallet/escrow_release', methods=['POST'])
def release_money():
    data = request.get_json()
    transaction_id = data.get('transaction_id')
    if not transaction_id:
        return jsonify({"error": "transaction_id is required"}), 400
    return jsonify(release_escrow_to_seller(transaction_id))



@wallet_bp_t.route('/wallet/withdraw', methods=['POST'])
def withdraw_money():
    data = request.get_json()
    wallet_id = data.get('wallet_id')
    amount = data.get('amount')
    if not wallet_id or not amount:
        return jsonify({"error": "wallet_id and amount are required"}), 400
    try:
        pla=withdraw(wallet_id, amount)
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500
    
    transaction = db.session.query(Transaction).filter_by(transaction_id=pla).first()
    send_notification(transaction.user_id, amount, transaction.transaction_type.value, transaction.status.value)

    return jsonify({
        "message": "Rút tiền thành công!",
        "transaction_id": pla,
    })

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

    transaction = db.session.query(Transaction).filter_by(transaction_id=order_id).first()

    print(transaction)

    if not transaction:
        return jsonify({"message": "Không tìm thấy giao dịch!"}), 404

    if transaction.status == TransactionStatusEnum.successful.value:
        return jsonify({"message": "Giao dịch đã được xử lý trước đó!"})


    # # Bước 3: Cập nhật trạng thái và cộng tiền
    result = update_deposit(transaction, amount)

    send_notification(transaction.user_id, amount, transaction.transaction_type.value, transaction.status.value)

    return jsonify({
        "message": "Thanh toán thành công!",
        "order_id": order_id,
        "amount": amount,
        "new_balance": result # Lấy giá trị new_balance từ result
    }), 200


@wallet_bp_t.route('/wallet/test', methods=['POST'])
def test():
    data = request.get_json()
    print(data)
    return jsonify({"message": "ok"}), 200