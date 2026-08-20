import csv
from io import StringIO
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from notifications.models import NotificationLog
from .models import Product

def generate_daily_stock_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "date", "sku", "product_name", "price",
        "gst_percentage", "current_quantity",
        "threshold_quantity", "stock_status",
    ])
    products = Product.objects.filter(is_active=True).order_by("name")
    today = timezone.localdate().strftime("%Y-%m-%d")

    for product in products:
        stock_status = (
            "LOW STOCK"
            if product.quantity <= product.threshold_quantity
            else "OK"
        )
        writer.writerow([
            today,
            product.sku,
            product.name,
            product.price,
            product.gst_percentage,
            product.quantity,
            product.threshold_quantity,
            stock_status,
        ])
    return output.getvalue()

@shared_task(name="products.tasks.send_daily_stock_report_task")
def send_daily_stock_report_task():
    today = timezone.localdate().strftime("%Y-%m-%d")
    notification_log = NotificationLog.objects.create(
        notification_type=NotificationLog.NotificationType.DAILY_STOCK_REPORT,
        channel=NotificationLog.Channel.EMAIL,
        recipient=settings.ADMIN_EMAIL,
        reference_id=today,
        status=NotificationLog.Status.PENDING,
    )

    try:
        csv_content = generate_daily_stock_csv()
        subject = f"📦 Daily Stock Report - {today}"
        body = (
            f"Hi Admin,\n\n"
            f"Please find attached today's stock report "
            f"({today}) for all active products.\n\n"
            f"This is an automated daily summary."
        )
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
        )
        filename = f"stock_report_{today}.csv"
        email.attach(filename, csv_content, "text/csv")
        email.send(fail_silently=False)
        notification_log.status=NotificationLog.Status.SENT
        notification_log.save(update_fields=["status", "updated_at"])
        return "sent"

    except Exception as exc:
        notification_log.status =NotificationLog.Status.FAILED
        notification_log.error_message = str(exc)
        notification_log.save(update_fields=["status", "error_message", "updated_at",])
        return "failed"