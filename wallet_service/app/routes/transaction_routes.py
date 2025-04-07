# from flask import Blueprint, request, jsonify
# from app.services.transaction_service import deposit, withdraw

# wallet_bp_t = Blueprint('wallet', __name__)

# @wallet_bp_t.route('/wallet/deposit', methods=['POST'])
# def deposit_money():
#     data = request.get_json()
#     wallet_id = data.get('wallet_id')
#     amount = data.get('amount')
#     if not wallet_id or not amount:
#         return jsonify({"error": "wallet_id and amount are required"}), 400
#     return jsonify(deposit(wallet_id, amount))

# @wallet_bp_t.route('/wallet/withdraw', methods=['POST'])
# def withdraw_money():
#     data = request.get_json()
#     wallet_id = data.get('wallet_id')
#     amount = data.get('amount')
#     if not wallet_id or not amount:
#         return jsonify({"error": "wallet_id and amount are required"}), 400
#     return jsonify(withdraw(wallet_id, amount))



from flask import Blueprint, request, jsonify
from app.services.transaction_service import deposit, withdraw

# Use a unique name for the Blueprint
wallet_bp_t = Blueprint('wallet_transactions', __name__)

@wallet_bp_t.route('/wallet/deposit', methods=['POST'])
def deposit_money():
    data = request.get_json()
    wallet_id = data.get('wallet_id')
    amount = data.get('amount')
    if not wallet_id or not amount:
        return jsonify({"error": "wallet_id and amount are required"}), 400
    return jsonify(deposit(wallet_id, amount))

@wallet_bp_t.route('/wallet/withdraw', methods=['POST'])
def withdraw_money():
    data = request.get_json()
    wallet_id = data.get('wallet_id')
    amount = data.get('amount')
    if not wallet_id or not amount:
        return jsonify({"error": "wallet_id and amount are required"}), 400
    return jsonify(withdraw(wallet_id, amount))