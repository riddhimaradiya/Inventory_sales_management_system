from django.conf import settings
from django.core.mail import EmailMessage
from notifications.models import NotificationLog
from orders.report_service import OrderCSVReportService

class ThresholdAlertService:

    @staticmethod
    def send_threshold_alert(order, product):
        notification_log = (
            NotificationLog.objects.create(
                notification_type=(NotificationLog.NotificationType.LOW_STOCK_ALERT),
                channel=(NotificationLog.Channel.EMAIL),
                recipient=settings.ADMIN_EMAIL,
                reference_id=(order.order_number),
                status = (NotificationLog.Status.PENDING),
            )
        )
        try:
            csv_content = (OrderCSVReportService.generate_order_csv(order))
            subject = (                
                f"⚠️ Low Stock Alert - "
                f"{product.name} ({product.sku})"
            )
            body = (
                f"Hi Admin,\n\n"
                f"The stock for the following product has fallen at or below "
                f"its restock threshold after order {order.order_number}.\n\n"
                f"Product: {product.name} ({product.sku})\n"
                f"Current Stock: {product.quantity}\n"
                f"Threshold: {product.threshold_quantity}\n\n"
                f"Please restock this product as soon as possible.\n\n"
                f"A CSV report of the triggering order is attached for reference."
            )
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=(settings.DEFAULT_FROM_EMAIL),
                to = [settings.ADMIN_EMAIL],
            )
            filename = (f"{order.order_number}_report.csv")
            email.attach(filename,csv_content,"text/csv")
            email.send(fail_silently=False)
            notification_log.status = (NotificationLog.Status.SENT)
            notification_log.save(update_fields=["status","updated_at",])

        except Exception as exc:
            notification_log.status = (NotificationLog.Status.FAILED)
            notification_log.error_message = str(exc)
            notification_log.save(
                update_fields=["status", "error_message", "updated_at",]
            )