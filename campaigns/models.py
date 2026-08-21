from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from products.models import Product

class Campaign(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "PERCENTAGE", "Percentage"
        FLAT = "FLAT", "FLAT Amount"

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE,)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],)
    products = models.ManyToManyField(Product, related_name="campaigns",)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    broadcast_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(discount_value__gte=0),
                name="campaign_discount_value_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.discount_value} {self.discount_type})"

    def is_live(self):
        now = timezone.now()
        return(
            self.is_active
            and self.start_date <= now <= self.end_date
        )

    def calculate_discounted_price(self, price):
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount_amount = (price * self.discount_value) / 100
        else:
            discount_amount = self.discount_value

        discount_price = price - discount_amount
        return discount_price if discount_price > 0 else price * 0