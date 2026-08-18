from django.db import transaction
from .models import Product, StockMovement

class ProductService:
    @staticmethod
    @transaction.atomic
    def create_product(validated_data):
        quantity = validated_data.get("quantity", 0)
        product = Product.objects.create(**validated_data)
        if quantity > 0:
            StockMovement.objects.create(
                product=product,
                Movement_Type=StockMovement.MovementType.PURCHASE,
                quantity=quantity,
                reference="INITIAL_STOCK",
                note="Initial stock added during product creation.",
            )

        return product