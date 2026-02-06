import hmac
import hashlib

def get_sign(secret_key: str, payload: str) -> str:
    try:
        signature = hmac.new(
            secret_key.encode("utf-8"),
            payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return signature
    except Exception as e:
        raise ValueError(f"Ошибка при создании подписиси: {str(e)}")