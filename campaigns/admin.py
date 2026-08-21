from django.contrib import admin
from .models import Campaign

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = [
        "name", "discount_type", "discount_value",
        "start_date", "end_date", "is_active", "broadcast_sent",
    ]
    list_filter = ["is_active", "discount_type"]
    filter_horizontal = ["products"]