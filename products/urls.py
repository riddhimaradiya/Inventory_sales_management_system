from django.urls import path
from .views import ProductListCreateView, ProductDetailView, ProductStockUpdateView, ProductStockMovementListView

urlpatterns = [
    path("", ProductListCreateView.as_view(), name = "product-list-create"),
    path("<int:pk>/",ProductDetailView.as_view(),name="product-detail"),
    path("<int:pk>/stock/",ProductStockUpdateView.as_view(),name="product-stock-update"),
    path("<int:pk>/stock-movements/", ProductStockMovementListView.as_view(),name="product-stock-movements"),
]
