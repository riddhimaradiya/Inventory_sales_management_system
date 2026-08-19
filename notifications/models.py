from django.db import models

class NotificationLog(models.Model):
    class NotificationType(models.TextChoices):
        ORDER_CONFIRMATION = ("ORDER_CONFIRMATION", "Order Confirmation")
        LOW_STOCK_ALERT = ("LOW_STOCK_ALERT","Low Stock Alert")

    class Channel(models.TextChoices):
        WHATSAPP = "WHATSAPP", "WhatsApp"
        EMAIL = "EMAIL", "Email"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    notification_type = models.CharField(max_length=50,choices=NotificationType.choices)
    channel = models.CharField(max_length=20,choices=Channel.choices)
    recipient = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=100,blank=True,null=True)
    provider_message_id = models.CharField(max_length=255,blank=True,null=True)
    status = models.CharField(max_length=20,choices=Status.choices)
    error_message = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.notification_type} - "
            f"{self.status}"
        )