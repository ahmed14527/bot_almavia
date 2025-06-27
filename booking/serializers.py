# booking/serializers.py

from rest_framework import serializers
from .models import BookingRequest

class BookingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = ['id', 'email', 'password', 'status']
        read_only_fields = ['status']
