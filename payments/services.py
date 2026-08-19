import random
import uuid
from .models import Payment

class PaymentService:
    @staticmethod
    def make_payment(order, amount):
        payment_success = random.choice([True, False])
        if payment_success:
            transaction_id = (f"TXN-{uuid.uuid4().hex[:16].upper()}")
            payment = Payment.objects.create(
                order=order,
                amount=amount,
                status=Payment.PaymentStatus.SUCCESS,
                transaction_id=transaction_id,
            )
            return payment

        payment = Payment.objects.create(
            order=order,
            amount=amount,
            status=Payment.PaymentStatus.FAILED,
        )
        return payment