from rest_framework import serializers
from .models import Customer
import re

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "mobile_number", "email", "is_active", "created_at","updated_at",]
        read_only_fields = ["id", "created_at", "updated_at",]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("name cannot be empty.")
        return value

    def validate_mobile_number(self, value):
        value = value.strip()
        if not re.fullmatch(r"[6-9]\d{9}",value):
            raise serializers.ValidationError("Enter a valid 10-digit Indian mobile number.")
        return value