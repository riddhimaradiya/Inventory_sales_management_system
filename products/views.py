from rest_framework import status, generics
from rest_framework.response import Response
from .filters import ProductFilter
from .serializers import ProductSerializer
from .services import ProductService
from .models import Product
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

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