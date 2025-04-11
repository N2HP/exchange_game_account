from flask import Blueprint, request, jsonify
from app.services.wallet_service import create_wallet, get_wallet_balance, get_transaction_history, search_transaction, test

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/wallet/create', methods=['POST'])
def create_wallet_route():
    data = request.get_json()
    user_id =int(data .get('user_id'))
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    return jsonify(create_wallet(user_id))

@wallet_bp.route('/wallet/balance', methods=['GET'])
def get_balance_route():
    wallet_id = request.args.get('wallet_id', type=int)
    if not wallet_id:
        return jsonify({"error": "wallet_id is required"}), 400
    return jsonify(get_wallet_balance(wallet_id))


@wallet_bp.route('/wallet/transactions/search', methods=['GET'])
def search_transactions():
    wallet_id = request.args.get('wallet_id', type=int)
    transaction_id = request.args.get('transaction_id', type=int)
    transaction_type = request.args.get('transaction_type')
    amount = request.args.get('amount', type=float)
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not wallet_id:
        return jsonify({"error": "wallet_id is required"}), 400
    
    return jsonify(search_transaction(wallet_id, transaction_id, transaction_type, amount, status, start_date, end_date))

@wallet_bp.route('/wallet/transactions/history', methods=['GET'])
def get_transaction_history_route():
    wallet_id = request.args.get('wallet_id', type=int)
    if not wallet_id:
        return jsonify({"error": "wallet_id is required"}), 400
    return jsonify(get_transaction_history(wallet_id))

@wallet_bp.route('/wallet/test', methods=['GET'])
def get_test_route():
    wallet_id = request.args.get('wallet_id', type=int)
    if not wallet_id:
        return jsonify({"error": "wallet_id is required"}), 400
    return jsonify(test(wallet_id))