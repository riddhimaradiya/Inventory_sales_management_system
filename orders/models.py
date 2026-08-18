from django.db import models
from customers.models import Customer
import uuid

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    order_number = models.CharField(max_length=30,unique=True,editable=False)
    Customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=OrderStatus.choices,default=OrderStatus.PENDING)
    payment_Status = models.CharField(max_length=20,choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    total_amount = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = (f"ORD-{uuid.uuid4().hex[:12].upper()}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product",on_delete=models.PROTECT,related_name="order_items")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12,decimal_places=2)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=12,decimal_places=2)
    subtotal = models.DecimalField(max_digits=12,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.order.order_number} - "
            f"{self.product.name}"
        )