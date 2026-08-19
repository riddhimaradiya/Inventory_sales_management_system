from django.conf import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
import json

class TwilioWhatsAppService:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

    @staticmethod
    def format_indian_number(mobile_number):
        mobile_number = mobile_number.strip()
        if(
            len(mobile_number) != 10
            or not mobile_number.isdigit()
            or mobile_number[0] not in "6789"
        ):
            raise ValueError("Invalid Indian mobile number.")
        return f"+91{mobile_number}"

    def send_template_message(self, mobile_number, content_sid, content_variables):
        phone_number = (self.format_indian_number(mobile_number))
        try:
            response = self.client.messages.create(
                from_ = (settings.TWILIO_WHATSAPP_NUMBER),
                to=f"whatsapp:{phone_number}",
                content_sid=content_sid,
                content_variables=json.dumps(
                    content_variables
                ),
            )
            return response.sid
        except TwilioRestException as exc:
            raise RuntimeError(f"twilio whatsapp failed: {exc}") from exc

    def send_whatsapp(self, mobile_number, message):
        phone_number = self.format_indian_number(mobile_number)
        try:
            response = self.client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=f"whatsapp:{phone_number}",
                body=message,
            )
            return response.sid
        except TwilioRestException as exc:
            raise RuntimeError(f"twilio whatsapp failed: {exc}") from exc