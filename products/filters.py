from django.db import models
from django_filters import rest_framework as filters
from .models import Product


class ProductFilter(filters.FilterSet):
    low_stock = filters.BooleanFilter(method="filter_low_stock")

    class Meta:
        model = Product
        fields = ["is_active", "low_stock"]

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(quantity__lte=models.F("threshold_quantity"))
        return queryset
