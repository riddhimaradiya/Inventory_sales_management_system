from django.utils import timezone
from .models import Campaign

class CampaignService:

    @staticmethod
    def create_campaign(validated_data):
        products = validated_data.pop("products")
        campaign = Campaign.objects.create(**validated_data)
        campaign.products.set(products)
        return campaign

    @staticmethod
    def update_campaign(campaign, validated_data):
        products = validated_data.pop("products", None)
        for field, value in validated_data.items():
            setattr(campaign, field, value)
        campaign.save()
        if products is not None:
            campaign.products.set(products)
        return campaign

    @staticmethod
    def get_best_discounted_price(product):
        now = timezone.now()
        live_campaigns = product.campaigns.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now,
        )
        best_price = product.price
        best_campaign = None

        for campaign in live_campaigns:
            candidate_price = campaign.calculate_discounted_price(product.price)
            if candidate_price < best_price:
                best_price = candidate_price
                best_campaign = campaign

        return best_price, best_campaign