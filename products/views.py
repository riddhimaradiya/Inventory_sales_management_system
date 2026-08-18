from rest_framework import status, generics
from rest_framework.response import Response
from .filters import ProductFilter, StockMovementFilter
from .serializers import ProductSerializer, StockUpdateSerializer, StockMovementSerializer
from .services import ProductService, StockService
from .models import Product, StockMovement
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.shortcuts import get_list_or_404
from rest_framework.exceptions import ValidationError

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ["name", "sku", "description",]
    ordering_fields = ["name", "price", "quantity", "created_at",]
    ordering = ["-created_at"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        product = ProductService.create_product(serializer.validated_data)
        response_serializer = self.get_serializer(product)
        return Response(response_serializer.data,status=status.HTTP_201_CREATED)
    
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"

class ProductStockUpdateView(generics.GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = StockUpdateSerializer
    def patch(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_product, movement = (
                StockService.update_stock(product_id=pk, **serializer.validated_data)
            )

        except Product.DoesNotExist:
            return Response(
                {
                    "detail" : "Product not found."
                },status=status.HTTP_404_NOT_FOUND
            )
        
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)})
        response_serializer = ProductSerializer(updated_product)

        return Response(
            {
                "message": "Stock updated successfully.",
                "product": response_serializer.data,
                "movement": {
                    "id": movement.id,
                    "movement_type": (
                        movement.Movement_Type
                    ),
                    "quantity": movement.quantity,
                    "reference": movement.reference,
                    "note": movement.note,
                    "created_at": movement.created_at,
                }
            },
            status=status.HTTP_200_OK
        )

class ProductStockMovementListView(generics.ListAPIView):
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter,]
    filterset_class = StockMovementFilter
    ordering_fields = ["created_at", "quantity", "Movement_Type",]
    ordering = ["-created_at"]

    def get_queryset(self):
        product_id = self.kwargs["pk"]
        return(StockMovement.objects.filter(product_id=product_id).select_related("product"))
    