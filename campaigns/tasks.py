from celery import shared_task
from customers.models import Customer
from notifications.services import TwilioWhatsAppService
from notifications.models import NotificationLog
from .models import Campaign

def build_campaign_message(campaign):
    product_lines = "\n".join(
        f"• {p.name} — was ₹{p.price}"
        for p in campaign.products.all()[:10]
    )
    discount_label = (
        f"{campaign.discount_value}% OFF"
        if campaign.discount_type == Campaign.DiscountType.PERCENTAGE
        else f"₹{campaign.discount_value} OFF"
    )
    return{
        f"🎉 *{campaign.name}*\n"
        f"―――――――――――――――――――――\n"
        f"*{discount_label}* on selected items!\n\n"
        f"{product_lines}\n\n"
        f"―――――――――――――――――――――\n"
        f"Valid till {campaign.end_date.strftime('%d %b %Y')}. "
        f"Shop now before it ends!"
    }

@shared_task(name="campaigns.tasks.send_campaign_broadcast_task")
def send_campaign_broadcask_task(campaign_id):
    campaign = Campaign.objects.prefetch_related("products").get(id=campaign_id)
    message = build_campaign_message(campaign)
    whatsapp_service = TwilioWhatsAppService()
    sent_count = 0
    failed_count = 0

    for customer in Customer.objects.filter(is_active=True):
        notification_log = NotificationLog.objects.create(
            notification_type=NotificationLog.NotificationType.SALE_CAMPAIGN,
            channel=NotificationLog.Channel.WHATSAPP,
            recipient=customer.mobile_number,
            reference_id=str(campaign.id),
            status=NotificationLog.Status.PENDING,
        )

        message_sid = None
        try:
            message_sid = whatsapp_service.send_whatsapp(
                mobile_number=customer.mobile_number,
                message=message,
            )
            notification_log.status = NotificationLog.Status.SENT
            notification_log.provider_message_id = message_sid
            notification_log.save(update_fields=[
                "status", "provider_message_id", "updated_at",
            ])
            sent_count += 1
        except Exception as exc:
            notification_log.status = NotificationLog.Status.FAILED
            notification_log.error_message = str(exc)
            notification_log.provider_message_id = message_sid
            notification_log.save(update_fields=[
                "status", "provider_message_id", "error_message", "updated_at",
            ])
            failed_count += 1

    campaign.broadcast_sent = True
    campaign.save(update_fields=["broadcast_sent", "updated_at"])
    return {"sent": sent_count, "failed": failed_count}