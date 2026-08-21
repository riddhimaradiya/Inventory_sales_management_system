from rest_framework import serializers
from products.models import Product
from .models import Campaign

class CampaignSerializer(serializers.ModelSerializer):
    product_ids = serializers.PrimaryKeyRelatedField(
        source="products",
        queryset=Product.objects.filter(is_active=True),
        many=True,
        write_only=True,
    )
    products = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Campaign
        fields = [
            "id",
            "name",
            "description",
            "discount_type",
            "discount_value",
            "product_ids",
            "products",
            "start_date",
            "end_date",
            "is_active",
            "broadcast_sent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "broadcast_sent", "created_at", "updated_at"]

    def get_products(self, obj):
        return [
            {"id": p.id, "sku": p.sku, "name": p.name, "price": p.price}
            for p in obj.products.all()
        ]

    def validate_discount_value(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Discount value must be greater than zero."
            )
        return value

    def validate(self, attrs):
        discount_type = attrs.get(
            "discount_type",
            getattr(self.instance, "discount_type", Campaign.DiscountType.PERCENTAGE),
        )
        discount_value = attrs.get(
            "discount_value",
            getattr(self.instance, "discount_value", None),
        )
        if discount_type == Campaign.DiscountType.PERCENTAGE and discount_value is not None:
            if discount_value > 100:
                raise serializers.ValidationError({
                    "discount_value": "Percentage discount cannot exceed 100."
                })
 
        start_date = attrs.get(
            "start_date", getattr(self.instance, "start_date", None)
        )
        end_date = attrs.get(
            "end_date", getattr(self.instance, "end_date", None)
        )
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                "end_date": "End date must be after start date."
            })
 
        product_ids = attrs.get("products")
        if product_ids is not None and len(product_ids) == 0:
            raise serializers.ValidationError({
                "product_ids": "At least one product must be selected."
            })
 
        return attrs