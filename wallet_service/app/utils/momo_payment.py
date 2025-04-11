import hmac
import hashlib
import json
import requests
import uuid
from datetime import datetime

# MoMo Sandbox credentials (thay bằng thông tin thật nếu bạn có)
PARTNER_CODE = "MOMO..."
ACCESS_KEY = "..."
SECRET_KEY = "..."
REDIRECT_URL = "https://yourdomain.com/momo/redirect"
IPN_URL = "https://yourdomain.com/momo/ipn"

def create_momo_payment(amount, order_id=None):
    order_id = order_id or str(uuid.uuid4())
    request_id = str(uuid.uuid4())

    raw_data = f"accessKey={ACCESS_KEY}&amount={amount}&extraData=&ipnUrl={IPN_URL}&orderId={order_id}&orderInfo=Nạp ví&partnerCode={PARTNER_CODE}&redirectUrl={REDIRECT_URL}&requestId={request_id}&requestType=captureWallet"

    signature = hmac.new(SECRET_KEY.encode(), raw_data.encode(), hashlib.sha256).hexdigest()

    payload = {
        "partnerCode": PARTNER_CODE,
        "accessKey": ACCESS_KEY,
        "requestId": request_id,
        "amount": str(amount),
        "orderId": order_id,
        "orderInfo": "Nạp ví",
        "redirectUrl": REDIRECT_URL,
        "ipnUrl": IPN_URL,
        "extraData": "",
        "requestType": "captureWallet",
        "signature": signature,
        "lang": "vi"
    }

    response = requests.post("https://test-payment.momo.vn/v2/gateway/api/create", json=payload)
    return response.json()
