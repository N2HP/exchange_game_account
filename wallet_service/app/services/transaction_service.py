import traceback
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






# ...existing code...

def escrow_hold_money(buyer_wallet_id, seller_wallet_id, amount):
    """
    Hold money from buyer's wallet in escrow for a transaction.
    
    Args:
        buyer_wallet_id: ID of the buyer's wallet
        seller_wallet_id: ID of the seller's wallet (to reference in transaction)
        amount: Amount to hold in escrow
        
    Returns:
        Tuple of (response_object, status_code)
    """
    try:
        buyer_wallet = Wallet.query.get(buyer_wallet_id)
        seller_wallet = Wallet.query.get(seller_wallet_id)

        if not buyer_wallet or not seller_wallet:
            return {"error": "Wallet not found"}, 404

        if buyer_wallet.balance < amount:
            return {"error": "Insufficient balance"}, 400

        # Record previous balance
        previous_buyer_balance = buyer_wallet.balance
        
        # Reduce buyer's available balance
        new_buyer_balance = buyer_wallet.balance - amount
        buyer_wallet.balance = new_buyer_balance
        
        # Create escrow transaction
        escrow_transaction_id = generate_transaction_id(buyer_wallet.user_id)
        escrow_transaction = Transaction(
            transaction_id=escrow_transaction_id,
            user_id=buyer_wallet.user_id,
            wallet_id=buyer_wallet_id,
            transaction_type=TransactionTypeEnum.escrow.value,  # You might need to add this enum value
            amount=amount,
            status=TransactionStatusEnum.pending.value,  # Mark as pending until released
            destination="escrow_" + str(seller_wallet_id)
        )
        
        db.session.add(escrow_transaction)
        
        # Record balance history
        balance_history = BalanceHistory(
            wallet_id=buyer_wallet_id,
            transaction_id=escrow_transaction_id,
            previous_balance=previous_buyer_balance,
            new_balance=new_buyer_balance
        )
        
        db.session.add(balance_history)
        db.session.commit()
        
        return {
            "message": "Money held in escrow successfully", 
            "escrow_transaction_id": escrow_transaction_id,
            "new_buyer_balance": float(new_buyer_balance)
        }, 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": str(e)}, 500


def release_escrow_to_seller(escrow_transaction_id):
    """
    Release money held in escrow to the seller's wallet.
    
    Args:
        escrow_transaction_id: The transaction ID of the escrow hold
        
    Returns:
        Tuple of (response_object, status_code)
    """
    try:
        # Find the escrow transaction
        escrow_transaction = Transaction.query.filter_by(
            transaction_id=escrow_transaction_id,
            transaction_type=TransactionTypeEnum.escrow.value
        ).first()
        
        if not escrow_transaction:
            return {"error": "Escrow transaction not found"}, 404
            
        # if escrow_transaction.status != TransactionStatusEnum.pending.value:
        #     return {"error": "Escrow already processed"}, 400
        
        # Extract seller wallet ID from destination
        seller_wallet_id = int(escrow_transaction.destination.split('_')[1])
        seller_wallet = Wallet.query.get(seller_wallet_id)
        
        if not seller_wallet:
            return {"error": "Seller wallet not found"}, 404
            
        # Get amount from escrow transaction
        amount = escrow_transaction.amount
        
        # Record previous balance
        previous_seller_balance = seller_wallet.balance
        
        # Update seller balance
        new_seller_balance = seller_wallet.balance + amount
        seller_wallet.balance = new_seller_balance
        
        # Update escrow transaction status
        escrow_transaction.status = TransactionStatusEnum.successful.value
        
        # Create new transaction for seller
        seller_transaction_id = generate_transaction_id(seller_wallet.user_id)
        seller_transaction = Transaction(
            transaction_id=seller_transaction_id,
            user_id=seller_wallet.user_id,
            wallet_id=seller_wallet_id,
            transaction_type=TransactionTypeEnum.escrow.value,  # You might need to add this enum value
            amount=amount,
            status=TransactionStatusEnum.successful.value,
            destination="from_escrow_" + str(escrow_transaction_id)
        )
        
        db.session.add(seller_transaction)
        
        # Record balance history
        balance_history = BalanceHistory(
            wallet_id=seller_wallet_id,
            transaction_id=seller_transaction_id,
            previous_balance=previous_seller_balance,
            new_balance=new_seller_balance
        )
        
        db.session.add(balance_history)
        db.session.commit()
        
        return {
            "message": "Escrow funds released to seller successfully", 
            "seller_transaction_id": seller_transaction_id,
            "new_seller_balance": float(new_seller_balance)
        }, 200
    except SQLAlchemyError as e:
        error_message = str(e)
        stack = traceback.format_exc()
        print(f"SQLAlchemyError: {error_message}\n{stack}")  # Ghi log chi tiết ra console/log file
        return {"error": error_message, "details": stack}, 500  # Trả về chi tiết (chỉ nên dùng khi debug)




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
