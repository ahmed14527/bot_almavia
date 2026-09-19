from rest_framework import serializers
from .models import BookingRequest


class BookingRequestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = BookingRequest
        fields = [
            'id',
            'full_name',
            'email',
            'password',
            'passport_number',
            'phone_number',
            'birth_date',
            'nationality',
            'passport_image',
            'status',
            'current_step',
            'step_progress',
            'total_steps',
            'action_required',
            'reference_number',
            'appointment_date',
            'error_message',
            'last_screenshot',
            'celery_task_id',
            'retry_count',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'current_step',
            'step_progress',
            'total_steps',
            'action_required',
            'reference_number',
            'appointment_date',
            'error_message',
            'last_screenshot',
            'celery_task_id',
            'retry_count',
            'notes',
            'created_at',
            'updated_at',
        ]


class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = [
            'id',
            'status',
            'current_step',
            'step_progress',
            'total_steps',
            'action_required',
            'reference_number',
            'appointment_date',
            'error_message',
            'last_screenshot',
            'updated_at',
        ]
        read_only_fields = fields


class BulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

