import uuid
from yoomoney import Quickpay, Client
from config.config import settings

yoomoney_client = Client(settings.YOOMONEY_ACCESS_TOKEN)

def create_yoomoney_payment(user_id: int, amount: float, description: str):
    label = f"user_{user_id}_{uuid.uuid4().hex[:8]}"
    quickpay = Quickpay(
        reciever = settings.YOOMONEY_RECEIVER,
        quickpay_form="shop",
        targets=description,
        paymentType="SB",
        sum=amount,
        label=label,
    )
    return {"status": "success", "payment_url": quickpay.redirected_url, "label": label}

def check_yoomoney_payment(label: str):
    try:
        history = yoomoney_client.operation_history(label=label)
        for op in history.operations:
            if op.label == label and op.status == "success":
                return True
        return False
    except Exception as e:
        print(f"Error checking payment: {e}")
        return False