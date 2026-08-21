from django.urls import path
from .views import CampaignListCreateView, CampaignDetailView, CampaignBroadcastView

urlpatterns = [
    path("", CampaignListCreateView.as_view(), name="campaign-list-create"),
    path("<int:pk>/", CampaignDetailView.as_view(), name="campaign-detail"),
    path("<int:pk>/broadcast/",CampaignBroadcastView.as_view(), name="campaign-broadcast"),
]
