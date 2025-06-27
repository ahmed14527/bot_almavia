# booking/management/commands/import_excel.py

import pandas as pd
from django.core.management.base import BaseCommand
from booking.models import BookingRequest
from booking.tasks import run_booking_bot_task

class Command(BaseCommand):
    help = "Import booking requests from Excel or CSV and trigger Celery"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel or CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)

        created = 0
        for _, row in df.iterrows():
            email = row['email']
            password = row['password']

            booking = BookingRequest.objects.create(email=email, password=password)
            run_booking_bot_task.delay(booking.id)  # ← Celery task
            created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ تم استيراد وتشغيل المهام لـ {created} مستخدمًا"))
