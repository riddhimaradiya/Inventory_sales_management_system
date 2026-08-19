from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import TwilioNotificationService

class TestWhatsappView(APIView):
    def post(self, request):
        mobile_number = request.data.get("mobile_number")
        message = request.data.get("message")
        if not mobile_number or not message:
            return Response(
                {
                    "detail" : ("mobile_number and" 
                                "message are required.")
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            service = (TwilioNotificationService())
            message_sid = (
                service.send_whatsapp(mobile_number, message)
            )
            return Response(
                {
                    "message": (
                        "WhatsApp message "
                        "sent successfully."
                    ),
                    "message_sid": message_sid,
                },
                status=status.HTTP_200_OK
            )
        except(ValueError,RuntimeError) as exc:
            return Response({"detail":str(exc)},
                            status=status.HTTP_400_BAD_REQUEST)