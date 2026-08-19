from django.conf import settings
from .services import TwilioWhatsAppService
from .models import NotificationLog

class OrderNotificationService:

    @staticmethod
    def build_product_summary(order):
        items = (order.items.select_related("product").all())
        product_lines = []
        for item in items:
            product_lines.append(
                f"{item.product.name} x {item.quantity}"
            )
        return "\n".join(product_lines)

    @staticmethod
    def send_order_confirmation(order):
        customer = order.customer
        notification_log = (NotificationLog.objects.create(
            notification_type=(NotificationLog.NotificationType.ORDER_CONFIRMATION),
            channel=(NotificationLog.Channel.WHATSAPP),
            recipient=(customer.mobile_number),
            reference_id=(order.order_number),
            status=(NotificationLog.Status.PENDING),
        ))
        try:
            product_summary = (OrderNotificationService.build_product_summary(order))
            content_variables = {
                "1": customer.name,
                "2": order.order_number,
                "3": product_summary,
                "4": str(order.total_amount),
            }
            whatsapp_service = (TwilioWhatsAppService())
            message_sid = (whatsapp_service.send_template_message(
                mobile_number=(customer.mobile_number),
                content_sid=(settings.TWILIO_WHATSAPP_CONTENT_SID),
                content_variables=(content_variables),
            ))
            notification_log.status = (NotificationLog.Status.SENT)
            notification_log.provider_message_id = (message_sid)
            notification_log.save(update_fields=[
                "status", "provider_message_id", "updated_at",
            ])
            return message_sid

        except Exception as exc:
            notification_log.status = (NotificationLog.Status.FAILED)
            notification_log.error_message = str(exc)
            notification_log.save(update_fields=[
                "status", "provider_message_id", "updated_at",
            ])
            return None