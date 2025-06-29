# booking/management/commands/import_excel.py

import pandas as pd
from django.core.management.base import BaseCommand
from booking.models import BookingRequest
from booking.tasks import run_booking_bot_task
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = "Import booking requests from Excel or CSV and trigger Celery"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel or CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        # قراءة الملف سواء CSV أو Excel
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        required_fields = ['email', 'password', 'passport_number', 'phone_number', 'birth_date', 'nationality']
        missing_fields = [f for f in required_fields if f not in df.columns]
        if missing_fields:
            self.stdout.write(self.style.ERROR(f"الملف ناقص الحقول التالية: {', '.join(missing_fields)}"))
            return

        created = 0
        for _, row in df.iterrows():
            try:
                birth_date = row['birth_date']
                # إذا كانت القيمة ليست تاريخ من نوع datetime أو str صريح، حاول تحويلها
                if not pd.isna(birth_date):
                    if isinstance(birth_date, str):
                        birth_date = parse_date(birth_date)
                    elif hasattr(birth_date, 'to_pydatetime'):
                        birth_date = birth_date.to_pydatetime().date()
                    else:
                        birth_date = None
                else:
                    birth_date = None

                booking = BookingRequest.objects.create(
                    email=row['email'],
                    password=row['password'],
                    passport_number=row['passport_number'],
                    phone_number=row['phone_number'],
                    birth_date=birth_date,
                    nationality=row['nationality']
                )
                run_booking_bot_task.delay(booking.id)  # ← Celery task
                created += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"فشل في استيراد الصف: {row.to_dict()} بسبب: {e}"))

        self.stdout.write(self.style.SUCCESS(f"✅ تم استيراد وتشغيل المهام لـ {created} مستخدمًا"))
