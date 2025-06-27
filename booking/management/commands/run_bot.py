# booking/management/commands/run_bot.py
from django.core.management.base import BaseCommand
from booking.models import BookingRequest
from booking.bot_runner import run_bot

class Command(BaseCommand):
    help = "Run booking bot for all pending requests"

    def handle(self, *args, **options):
        pending = BookingRequest.objects.filter(status="pending")

        for req in pending:
            self.stdout.write(f"🔄 Processing: {req.email}")
            success = run_bot(req.email, req.password)

            req.status = "success" if success else "failed"
            req.save()
            self.stdout.write(f"{'✅' if success else '❌'} Finished for: {req.email}")
