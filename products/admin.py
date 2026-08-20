from django.contrib import admin
from .models import Product,StockMovement
# Register your models here.
admin.site.register(Product)
admin.site.register(StockMovement)