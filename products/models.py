from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Product(models.Model):
    sku = models.CharField(max_length=50,unique=True, db_index=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    quantity = models.PositiveIntegerField(default=0)
    threshold_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="product_price_non_negative"
            ),
            models.CheckConstraint(
                condition=models.Q(gst_percentage__gte=0),
                name="product_gst_non_negative"
            ),
            models.CheckConstraint(
                condition=models.Q(gst_percentage__lte=100),
                name="product_gst_max_100"
            ),
        ]


    def __str__(self):
        return f"{self.name} ({self.sku})"


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        PURCHASE = "PURCHASE", "Purchase"
        SALE = "SALE", "Sale"
        RESTOCK = "RESTOCK", "Restock"
        RETURN = "RETURN", "Return"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_movements")
    Movement_Type = models.CharField(max_length=20,choices=MovementType.choices)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["product", "created_at"]
            ),
        ]

        constraints = [
        models.CheckConstraint(
            condition=models.Q(quantity__gt=0),
            name="stock_movement_quantity_positive"
        ),
    ]

    def __str__(self):
        return (
            f"{self.product.sku} - "
            f"{self.Movement_Type} - " 
            f"{self.quantity}"
        )