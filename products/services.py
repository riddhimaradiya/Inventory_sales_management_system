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

class StockService:

    INCREASE_MOVEMENTS = {
        StockMovement.MovementType.PURCHASE,
        StockMovement.MovementType.RESTOCK,
        StockMovement.MovementType.RETURN,
    }

    DECREASE_MOVEMENT = {StockMovement.MovementType.SALE}

    @staticmethod
    @transaction.atomic
    def update_stock(product_id, movement_type, quantity, reference ="", note="",):
        product = (Product.objects.select_for_update().get(id=product_id))

        if movement_type in StockService.INCREASE_MOVEMENTS:
            product.quantity += quantity
        elif movement_type in StockService.DECREASE_MOVEMENT:
            if product.quantity < quantity:
                raise ValueError("Insufficient stock.")
            product.quantity -= quantity
        else:
            raise ValueError("unsuppoted stock movement type.")

        product.save(update_fields=["quantity", "updated_at",])
        movement = StockMovement.objects.create(
            product=product,
            Movement_Type=movement_type,
            quantity=quantity,
            reference=reference,
            note=note,
        )
        return product, movement