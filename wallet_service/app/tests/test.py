import pytest
from app.models import db, Wallet, Transaction, BalanceHistory
from app.services.transaction_service import deposit
from app.models import TransactionTypeEnum, TransactionStatusEnum

@pytest.fixture
def setup_wallet(app):
    """Fixture để thiết lập một ví thử nghiệm."""
    with app.app_context():
        # Tạo một ví thử nghiệm
        wallet = Wallet(user_id=1, balance=1000.00)
        db.session.add(wallet)
        db.session.commit()
        yield wallet
        # Cleanup sau khi test
        db.session.delete(wallet)
        db.session.commit()

def test_deposit_success(app, setup_wallet):
    """Kiểm tra trường hợp nạp tiền thành công."""
    wallet = setup_wallet
    deposit_amount = 500.00

    # Gọi hàm deposit
    response, status_code = deposit(wallet_id=wallet.wallet_id, amount=deposit_amount)

    # Kiểm tra phản hồi
    assert status_code == 200
    assert response["message"] == "Deposit successful"
    assert response["new_balance"] == float(wallet.balance + deposit_amount)

    # Kiểm tra cơ sở dữ liệu
    with app.app_context():
        updated_wallet = Wallet.query.get(wallet.wallet_id)
        assert updated_wallet.balance == wallet.balance + deposit_amount

        # Kiểm tra giao dịch được tạo
        transaction = Transaction.query.filter_by(wallet_id=wallet.wallet_id).first()
        assert transaction is not None
        assert transaction.amount == deposit_amount
        assert transaction.transaction_type == TransactionTypeEnum.DEPOSIT.value
        assert transaction.status == TransactionStatusEnum.SUCCESSFUL.value

        # Kiểm tra lịch sử số dư
        balance_history = BalanceHistory.query.filter_by(wallet_id=wallet.wallet_id).first()
        assert balance_history is not None
        assert balance_history.previous_balance == wallet.balance
        assert balance_history.new_balance == wallet.balance + deposit_amount