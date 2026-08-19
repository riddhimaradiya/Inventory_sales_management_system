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
                channel=(NotificationLog.channel.EMAIL),
                recipient=settings.ADMIN_EMAIL,
                reference_id=(order.order_number),
                status = (NotificationLog.Status.PENDING),
            )
        )
        try:
            csv_content = (OrderCSVReportService.generate_order_csv(order))
            subject = (                
                f"Low Stock Alert - "
                f"{product.name}"
            )
            body = (
                f"Low stock alert.\n\n"
                f"Product: {product.name}\n"
                f"Current Stock: "
                f"{product.quantity}\n"
                f"Threshold: "
                f"{product.threshold}\n"
                f"Order: "
                f"{order.order_number}\n"
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