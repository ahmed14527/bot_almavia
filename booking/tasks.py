from celery import shared_task
from concurrent.futures import ThreadPoolExecutor
from booking.bot_runner import run_bot
from booking.models import BookingRequest

@shared_task
def run_booking_bot_task(booking_id):
    try:
        booking = BookingRequest.objects.get(id=booking_id)
        print(f"⏳ Running bot for: {booking.email}")
        success = run_bot(booking.email, booking.password)
        booking.status = "success" if success else "failed"
        booking.save()
        print(f"✅ Finished for: {booking.email}")
    except Exception as e:
        print(f"❌ Error in task for ID {booking_id}: {e}")






@shared_task
def run_booking_bot_parallel(accounts):
    """
    accounts = [
        ["email1@example.com", "pass1"],
        ["email2@example.com", "pass2"],
        ...
    ]
    """
    def run_single(account):
        email, password = account
        print(f"🔐 Starting for: {email}")
        result = run_bot(email, password)
        print(f"✅ {email} → Success: {result}")
        return result

    with ThreadPoolExecutor(max_workers=len(accounts)) as executor:
        executor.map(run_single, accounts)


