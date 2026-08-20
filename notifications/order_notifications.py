from .services import TwilioWhatsAppService
from .models import NotificationLog


class OrderNotificationService:

    @staticmethod
    def build_item_block(order):
        items = order.items.select_related("product").all()
        blocks = []
        for item in items:
            blocks.append(
                f"Product: {item.product.name}\n"
                f"Price: ₹{item.unit_price}\n"
                f"Quantity: {item.quantity}\n"
                f"Amount: ₹{item.subtotal}\n"
                f"GST ({item.gst_percentage}%): ₹{item.gst_amount}"
            )
        return "\n- - - - - - - - - - - -\n".join(blocks)

    @staticmethod
    def build_payment_success_message(order):
        payment = order.payment
        item_block = OrderNotificationService.build_item_block(order)
        subtotal = sum(item.subtotal for item in order.items.all())
        gst_total = sum(item.gst_amount for item in order.items.all())

        return (
            f"🧾 *ORDER BILL*\n"
            f"―――――――――――――――――――――\n"
            f"Order No: *{order.order_number}*\n"
            f"Date: {order.created_at.strftime('%d %b %Y, %I:%M %p')}\n"
            f"Customer: {order.customer.name}\n"
            f"―――――――――――――――――――――\n\n"
            f"{item_block}\n\n"
            f"―――――――――――――――――――――\n"
            f"Subtotal: ₹{subtotal}\n"
            f"Total GST: ₹{gst_total}\n"
            f"*Total: ₹{payment.amount}*\n"
            f"―――――――――――――――――――――\n\n"
            f"✅ *Payment Successful*\n"
            f"Transaction ID: {payment.transaction_id or 'Not available'}\n\n"
            f"Thank you for your order, {order.customer.name}! 🙏\n"
            f"We'll notify you once it's shipped."
        )


    @staticmethod
    def send_order_confirmation(order):
        customer = order.customer
        notification_log = NotificationLog.objects.create(
            notification_type=NotificationLog.NotificationType.ORDER_CONFIRMATION,
            channel=NotificationLog.Channel.WHATSAPP,
            recipient=customer.mobile_number,
            reference_id=order.order_number,
            status=NotificationLog.Status.PENDING,
        )
        try:
            whatsapp_service = TwilioWhatsAppService()
            message_sid = whatsapp_service.send_whatsapp(
                mobile_number=customer.mobile_number,
                message=OrderNotificationService.build_payment_success_message(order),
            )
            notification_log.status = NotificationLog.Status.SENT
            notification_log.provider_message_id = message_sid
            notification_log.save(update_fields=[
                "status", "provider_message_id", "updated_at",
            ])
            return message_sid
    
        except Exception as exc:
            notification_log.status = NotificationLog.Status.FAILED
            notification_log.error_message = str(exc)
            notification_log.save(update_fields=[
                "status", "provider_message_id", "updated_at",
            ])
            return None

    @staticmethod
    def build_payment_failed_message(order, validated_items):
        item_lines = "\n- - - - - - - - - - - -\n".join(
            f" Product ID: {item['product'].id}\n Quantity: {item['quantity']}"
            for item in validated_items
        )
        return (
            f"❌ *Payment Failed*\n"
            f"―――――――――――――――――――――\n"
            f" Order: {order.order_number}\n"
            f" Mobile: +91{order.customer.mobile_number}\n"
            f"―――――――――――――――――――――\n"
            f"{item_lines}\n"
            f"―――――――――――――――――――――\n\n"
            f"⚠️ Your payment could not be processed.\n"
            f"Please try again or contact support."
        )

    @staticmethod
    def send_payment_failed(order, validated_items):
        customer = order.customer
        notification_log = NotificationLog.objects.create(
            notification_type=NotificationLog.NotificationType.ORDER_CONFIRMATION,
            channel=NotificationLog.Channel.WHATSAPP,
            recipient=customer.mobile_number,
            reference_id=order.order_number,
            status=NotificationLog.Status.PENDING,
        )
        try:
            whatsapp_service = TwilioWhatsAppService()
            message_sid = whatsapp_service.send_whatsapp(
                mobile_number=customer.mobile_number,
                message=OrderNotificationService.build_payment_failed_message(
                    order, validated_items
                ),
            )
            notification_log.status = NotificationLog.Status.SENT
            notification_log.provider_message_id = message_sid
            notification_log.save(update_fields=[
                "status", "provider_message_id", "updated_at",
            ])
            return message_sid
 
        except Exception as exc:
            notification_log.status = NotificationLog.Status.FAILED
            notification_log.error_message = str(exc)
            notification_log.save(update_fields=[
                "status", "provider_message_id", "updated_at",
            ])
            return None

   