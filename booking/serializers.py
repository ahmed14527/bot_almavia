from rest_framework import serializers
from .models import BookingRequest

class BookingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = [
            'id',
            'email',
            'password',
            'passport_number',
            'phone_number',
            'birth_date',
            'nationality',       
            'passport_image',
            'status',
            'created_at'
        ]
        read_only_fields = ['status', 'created_at']
