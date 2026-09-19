import os
from django.core.management.base import BaseCommand
from booking.models import BookingRequest
from booking.excel_service import validate_and_preview_excel
from booking.tasks import dispatch_booking_job

class Command(BaseCommand):
    help = "Import customers from Excel file and optionally start workflow"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file (.xlsx, .xls, .csv)')
        parser.add_argument('--start', action='store_true', help='Automatically start booking workflow for imported accounts')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        auto_start = kwargs.get('start', False)

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        with open(file_path, 'rb') as f:
            preview = validate_and_preview_excel(f)

        if not preview.get('success'):
            self.stdout.write(self.style.ERROR(f"Error parsing file: {preview.get('error')}"))
            return

        valid_rows = preview.get('valid_rows', [])
        invalid_rows = preview.get('invalid_rows', [])

        self.stdout.write(f"Total rows: {preview.get('total_rows')}")
        self.stdout.write(self.style.SUCCESS(f"Valid rows: {len(valid_rows)}"))
        if invalid_rows:
            self.stdout.write(self.style.WARNING(f"Invalid rows: {len(invalid_rows)}"))
            for inv in invalid_rows:
                self.stdout.write(self.style.WARNING(f"  Row {inv['row_number']}: {', '.join(inv['errors'])}"))

        count = 0
        for row in valid_rows:
            try:
                b = BookingRequest.objects.create(
                    full_name=row.get('full_name') or row.get('email', '').split('@')[0],
                    email=row['email'],
                    password=row['password'],
                    passport_number=row['passport_number'],
                    nationality=row['nationality'],
                    phone_number=row['phone_number'],
                    birth_date=row['birth_date'],
                    status=BookingRequest.Status.PENDING,
                    current_step="Imported from Excel - Pending"
                )
                count += 1
                if auto_start:
                    dispatch_booking_job(b.id)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error importing row: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} customer accounts."))
