from django.db import models
from django.utils.translation import gettext_lazy as _


class BookingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        RUNNING = 'RUNNING', _('Running')
        WAITING_FOR_USER = 'WAITING_FOR_USER', _('Waiting for User')
        SUCCESS = 'SUCCESS', _('Success')
        FAILED = 'FAILED', _('Failed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        RETRYING = 'RETRYING', _('Retrying')

    # Customer Identification & Credentials
    full_name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField()
    password = models.CharField(max_length=255)
    passport_number = models.CharField(max_length=50, db_index=True)
    phone_number = models.CharField(max_length=30)
    birth_date = models.DateField()
    nationality = models.CharField(max_length=100)
    passport_image = models.ImageField(upload_to='passport_images/', null=True, blank=True)

    # Workflow & Automation State Tracking
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    current_step = models.CharField(max_length=255, blank=True, default='Pending')
    step_progress = models.IntegerField(default=0)
    total_steps = models.IntegerField(default=8)
    action_required = models.TextField(blank=True, default='')

    # Booking Confirmation Details
    reference_number = models.CharField(max_length=100, blank=True, default='')
    appointment_date = models.CharField(max_length=100, blank=True, default='')

    # Diagnostics & Audit
    error_message = models.TextField(blank=True, default='')
    last_screenshot = models.CharField(max_length=500, blank=True, default='')
    celery_task_id = models.CharField(max_length=255, blank=True, default='')
    retry_count = models.IntegerField(default=0)
    notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        name = self.full_name or self.email
        return f"{name} ({self.passport_number}) - {self.status}"

