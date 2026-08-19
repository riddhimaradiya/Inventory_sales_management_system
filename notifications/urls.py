from django.urls import path
from .views import TestWhatsappView

urlpatterns = [
    path("test-whatsapp/", TestWhatsappView.as_view(), name="test-whatsapp"),
]
