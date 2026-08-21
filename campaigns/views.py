from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Campaign
from .serializers import CampaignSerializer
from .services import CampaignService
from .tasks import send_campaign_broadcask_task

class CampaignListCreateView(generics.ListCreateAPIView):
    queryset = Campaign.objects.all().prefetch_related("products")
    serializer_class = CampaignSerializer
    ordering = ["-created_at"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        campaign = CampaignService.create_campaign(serializer.validated_data)
        response_serializer = self.get_serializer(campaign)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CampaignDetailView(generics.RetrieveUpdateAPIView):
    queryset = Campaign.objects.all().prefetch_related("products")
    serializer_class = CampaignSerializer
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        campaign = CampaignService.update_campaign(instance, serializer.validated_data)
        response_serializer = self.get_serializer(campaign)
        return Response(response_serializer.data)

class CampaignBroadcastView(APIView):
    def post(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
        except Campaign.DoesNotExist:
            return Response(
                {"detail":"Campaign not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not campaign.is_live():
            return Response(
                {"detail":"Caqmpaign is not currently active/live."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        send_campaign_broadcask_task.delay(campaign.id)

        return Response(
            {"detail":"Campaign broadcast has been queued."},
            status=status.HTTP_202_ACCEPTED,
        )