import sys
from booking.models import BookingRequest
from booking.tasks import dispatch_booking_job

def run_batch_pending(limit=5):
    pending = BookingRequest.objects.filter(status=BookingRequest.Status.PENDING)[:limit]
    print(f'Starting batch for {pending.count()} pending bookings...')
    for b in pending:
        dispatch_booking_job(b.id)
        print(f'Dispatched booking #{b.id} ({b.email})')

if __name__ == '__main__':
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    run_batch_pending(limit)
