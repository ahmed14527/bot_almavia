# booking/management/commands/import_excel.py

import pandas as pd
from django.core.management.base import BaseCommand
from booking.tasks import run_booking_bot_task
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = "استيراد الحسابات من ملف Excel وتشغيل البوت لكل حساب"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='مسار ملف الإكسل')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        # تحميل الملف
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        required_columns = ['email', 'password', 'passport_number', 'nationality', 'birth_date', 'phone_number']
        for col in required_columns:
            if col not in df.columns:
                self.stdout.write(self.style.ERROR(f"❌ العمود مفقود: {col}"))
                return

        count = 0
        for _, row in df.iterrows():
            try:
                birth_date = row['birth_date']
                if isinstance(birth_date, str):
                    birth_date = parse_date(birth_date)
                elif hasattr(birth_date, 'to_pydatetime'):
                    birth_date = birth_date.to_pydatetime().date()

                account = {
                    "email": row['email'],
                    "password": row['password'],
                    "passport_number": row['passport_number'],
                    "nationality": row['nationality'],
                    "birth_date": birth_date,
                    "phone_number": row['phone_number'],
                    "passport_image_path": None  # ضيفها لو عندك مسار في الملف
                }

                run_booking_bot_task.delay(account)
                count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ فشل في {row.get('email')} بسبب: {e}"))

        self.stdout.write(self.style.SUCCESS(f"✅ تم تشغيل البوت لـ {count} حساب"))
