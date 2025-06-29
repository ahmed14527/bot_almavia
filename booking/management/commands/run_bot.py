from django.core.management.base import BaseCommand
from booking.models import BookingRequest
from booking.bot_runner import run_bot

class Command(BaseCommand):
    help = "Run booking bot for all pending requests"

    def handle(self, *args, **options):
        pending = BookingRequest.objects.filter(status="pending")

        for req in pending:
            self.stdout.write(f"🔄 Processing: {req.email}")
            try:
                success = run_bot(
                    email=req.email,
                    password=req.password,
                    passport_number=req.passport_number,
                    phone_number=req.phone_number,
                    birth_date=req.birth_date,
                    nationality=req.nationality,
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error processing {req.email}: {e}"))
                req.status = "failed"
                req.save()
                continue

            req.status = "success" if success else "failed"
            req.save()
            self.stdout.write(f"{'✅' if success else '❌'} Finished for: {req.email}")
