from django.contrib import admin
from .models import BookingRequest


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'email',
        'passport_number',
        'nationality',
        'status',
        'current_step',
        'reference_number',
        'created_at',
    )
    list_filter = ('status', 'nationality', 'created_at')
    search_fields = ('email', 'full_name', 'passport_number', 'phone_number', 'reference_number')
    readonly_fields = ('created_at', 'updated_at', 'celery_task_id')

    fieldsets = (
        ('Customer Information', {
            'fields': (
                'full_name',
                'email',
                'password',
                'passport_number',
                'phone_number',
                'birth_date',
                'nationality',
                'passport_image',
            )
        }),
        ('Automation State & Progress', {
            'fields': (
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
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

