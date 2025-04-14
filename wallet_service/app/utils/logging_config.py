import random
from datetime import datetime

def generate_transaction_id(user_id: int) -> int:
    # Lấy thời gian hiện tại dạng YYMMDDHHMMSS (12 chữ số)
    timestamp = datetime.now().strftime("%y%m%d%H%M%S")
    
    # Chuyển user_id sang dạng 4 chữ số (padding nếu cần)
    user_part = str(user_id).zfill(4)[-4:]

    # Random thêm 3 chữ số (000 - 999)
    rand_part = str(random.randint(0, 999)).zfill(3)

    # Gộp tất cả lại
    transaction_id_str = f"{timestamp}{user_part}{rand_part}"
    
    return int(transaction_id_str)
