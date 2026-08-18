from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import ValidationError
from .serializers import OrderCreateSerializer, OrderSerializer

class OrderCreateView(generics.GenericAPIView):
    serializer_class = OrderCreateSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = OrderService.create_order(**serializer.validated_data)
        except ValueError as exc:
            raise ValidationError({"detail" : str(exc)})
        response_serializer = OrderSerializer(order)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )