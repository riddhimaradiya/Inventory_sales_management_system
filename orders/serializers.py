from rest_framework import serializers
from customers.models import Customer
from products.models import Product
from .models import Order,OrderItem

class OrderItemCreateSerialzer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)

class OrderCreateSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(min_value=1)
    items = OrderItemCreateSerialzer(many=True)

    def validate_customer_id(self, value):
        if not Customer.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Active customer not found.")
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("order must contain at least one time.")
        product_ids = [
            item["product_id"]
            for item in value
        ]

        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("The same product cannot be added twice.")

        products = Product.objects.filter(id__in=product_ids, is_active=True)
        existing_ids = set(products.values_list("id", flat=True))
        missing_ids = (set(product_ids) - existing_ids)

        if missing_ids:
            raise serializers.ValidationError(
                {
                    "product_id": (
                        f"Product not found or "
                        f"inactive: "
                        f"{sorted(missing_ids)}"
                    )
                }
            )
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source = "product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "unit_price", "gst_percentage", "gst_amount", "subtotal",]
        read_only_fields = fields

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name",read_only=True)
    customer_mobile = serializers.CharField(source="customer.mobile_number",read_only=True)
    items = OrderItemSerializer(many=True,read_only=True)

    class Meta:
        model = Order
        fields = ["id", "order_number", "customer", "customer_name", "customer_mobile", "status", "payment_status", "total_amount", "items", "created_at", "updated_at",]
        read_only_fields = fields