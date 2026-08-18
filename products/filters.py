from django.db import models
from django_filters import rest_framework as filters
from .models import Product, StockMovement


class ProductFilter(filters.FilterSet):
    low_stock = filters.BooleanFilter(method="filter_low_stock")

    class Meta:
        model = Product
        fields = ["is_active", "low_stock"]

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(quantity__lte=models.F("threshold_quantity"))
        return queryset

class StockMovementFilter(filters.FilterSet):
    movement_type = filters.CharFilter(field_name="Movement_Type")
    reference = filters.CharFilter(field_name="reference", lookup_expr="icontains")
    created_after = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = StockMovement
        fields = ["movement_type", "reference", "created_after", "created_before"]
