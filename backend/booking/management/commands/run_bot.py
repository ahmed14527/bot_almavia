from django.core.management.base import BaseCommand
from booking.models import BookingRequest
from booking.bot_runner import run_bot

class Command(BaseCommand):
    help = "Run booking bot for pending requests"

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help='Max requests to process')
        parser.add_argument('--simulate', action='store_true', help='Run in simulation mode')

    def handle(self, *args, **options):
        limit = options.get('limit', 10)
        simulate = options.get('simulate', False)
        pending = BookingRequest.objects.filter(status=BookingRequest.Status.PENDING)[:limit]

        if not pending:
            self.stdout.write(self.style.WARNING("No pending booking requests found."))
            return

        for req in pending:
            self.stdout.write(f"Processing booking #{req.id}: {req.email}")
            try:
                success = run_bot(booking_id=req.id, simulate=simulate)
                self.stdout.write(f"{'Success' if success else 'Failed'} for booking #{req.id}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {req.email}: {e}"))
