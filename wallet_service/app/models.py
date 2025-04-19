
from datetime import datetime
from enum import Enum
from app.database import db



# Định nghĩa Enum cho loại giao dịch và trạng thái giao dịch
class TransactionTypeEnum(Enum):
    deposit = 'deposit'
    withdrawal = 'withdrawal'
    transfer = 'transfer'
    escrow = 'escrow'

class TransactionStatusEnum(Enum):
    pending = 'pending'
    successful = 'successful'
    failed = 'failed'

class GatewayStatusEnum(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    FAILED = 'failed'

# Bảng Users
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Quan hệ với Wallet
    wallets = db.relationship('Wallet', backref='user', lazy=True, cascade="all, delete-orphan")

# Bảng Wallets
class Wallet(db.Model):
    __tablename__ = 'wallets'

    wallet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    balance = db.Column(db.Numeric(20, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Quan hệ với Transactions & BalanceHistory
    transactions = db.relationship('Transaction', back_populates='wallet', cascade="all, delete-orphan")
    balance_history = db.relationship('BalanceHistory', back_populates='wallet', cascade="all, delete-orphan")

# Bảng Transactions
class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id', ondelete='CASCADE'), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionTypeEnum, name="transaction_type_enum"), nullable=False)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    status = db.Column(db.Enum(TransactionStatusEnum, name="transaction_status_enum"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.Column(db.Text, nullable=True)  # Cột mới đã thêm



    # Quan hệ hai chiều với Wallet
    wallet = db.relationship("Wallet", back_populates="transactions")

    # Quan hệ với PaymentGatewayLog và BalanceHistory
    payment_gateway_logs = db.relationship('PaymentGatewayLog', back_populates='transaction', cascade="all, delete-orphan")
    balance_history = db.relationship('BalanceHistory', back_populates='transaction', cascade="all, delete-orphan")

# Bảng PaymentGatewayLogs
class PaymentGatewayLog(db.Model):
    __tablename__ = 'payment_gateway_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.transaction_id', ondelete='CASCADE'), nullable=False)
    gateway_name = db.Column(db.String(50), default='MoMo')
    gateway_status = db.Column(db.Enum(GatewayStatusEnum, name="gateway_status_enum"), nullable=False)
    response_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Quan hệ với Transaction
    transaction = db.relationship('Transaction', back_populates='payment_gateway_logs')

# Bảng BalanceHistory
class BalanceHistory(db.Model):
    __tablename__ = 'balancehistory'
    
    history_id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id', ondelete='CASCADE'), nullable=False)
    transaction_id = db.Column(db.BigInteger, db.ForeignKey('transactions.transaction_id', ondelete='CASCADE'), nullable=False)
    previous_balance = db.Column(db.Numeric(20, 2), nullable=False)
    new_balance = db.Column(db.Numeric(20, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Quan hệ hai chiều với Wallet và Transaction
    wallet = db.relationship('Wallet', back_populates='balance_history')
    transaction = db.relationship('Transaction', back_populates='balance_history')



