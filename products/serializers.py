from rest_framework import serializers
from .models import Product, StockMovement

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "description",
            "price",
            "gst_percentage",
            "quantity",
            "threshold_quantity",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_field = [
            "id", "create_at", "updated_at",
        ]

    def validate_sku(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "SKU cannot be empty."
            )
        return value

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                "Product name must contain at least 2 characters"
            )
        return value

    def validate_gst_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "GST percentage must be between 0 and 100."
            )
        return value

    def validate(self, attrs):
        price = attrs.get("price")
        threshold = attrs.get("threshold_quantity")
        quantity = attrs.get("quantity")

        if price is not None and price < 0:
            raise serializers.ValidationError({
                "price":"price cannot be negative."
            })
        if quantity is not None and quantity < 0:
            raise serializers.ValidationError({
                "quantity" : "Quantity cannot be Negative."
            })
        if threshold is not None and threshold < 0:
            raise serializers.ValidationError({
                "threshold_quantity" : "Threshold cannot be Negative."
            }) 
        return attrs

class StockUpdateSerializer(serializers.Serializer):
    movement_type = serializers.ChoiceField(
        choices=[
            StockMovement.MovementType.PURCHASE,
            StockMovement.MovementType.RESTOCK,
            StockMovement.MovementType.RETURN,
            StockMovement.MovementType.SALE,
        ]
    )
    quantity = serializers.IntegerField(min_value=1)
    reference = serializers.CharField(max_length=100,required=False,allow_blank=True)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        Movement_Type = attrs["Movement_Type"]
        quantity = attrs["quantity"]
        if(Movement_Type == StockMovement.MovementType.SALE and quantity <= 0):
            raise serializers.ValidationError({
                "quantity" : "Sale quantity must be greater than zero,"
            })
        return attrs

class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ["id", "product", "Movement_Type", "quantity", "reference", "note","created_at",]
        read_only_fields = fields
