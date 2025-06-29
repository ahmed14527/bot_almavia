from django.contrib import admin
from .models import BookingRequest


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'passport_number',
        'phone_number',
        'birth_date',
        'nationality',
        'status',
        'created_at',
    )
    list_filter = ('status', 'nationality', 'created_at')
    search_fields = ('email', 'passport_number', 'phone_number')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'email',
                'password',
                'passport_number',
                'phone_number',
                'birth_date',
                'nationality',
                'passport_image',
                'status',
                'created_at',
            )
        }),
    )
