from celery import shared_task
from concurrent.futures import ThreadPoolExecutor
from booking.bot_runner import run_bot
from booking.models import BookingRequest

@shared_task
def run_booking_bot_task(booking_id):
    try:
        booking = BookingRequest.objects.get(id=booking_id)
        print(f"⏳ Running bot for: {booking.email}")

        # تمرير كل البيانات المطلوبة إلى run_bot
        success = run_bot(
            email=booking.email,
            password=booking.password,
            passport_number=booking.passport_number,
            nationality=booking.nationality,
            birth_date=booking.birth_date,
            phone_number=booking.phone_number,
            passport_image_path=booking.passport_image.path if booking.passport_image else None
        )
        
        booking.status = "success" if success else "failed"
        booking.save()
        print(f"✅ Finished for: {booking.email}")
    except Exception as e:
        print(f"❌ Error in task for ID {booking_id}: {e}")

@shared_task
def run_booking_bot_parallel(accounts):
    """
    accounts = [
        {
            "email": "email1@example.com",
            "password": "pass1",
            "passport_number": "A12345678",
            "nationality": "Egypt",
            "birth_date": "1990-05-15",
            "phone_number": "01234567890",
            "passport_image_path": "/path/to/image.jpg"
        },
        ...
    ]
    """
    def run_single(account):
        print(f"🔐 Starting for: {account['email']}")
        result = run_bot(
            email=account["email"],
            password=account["password"],
            passport_number=account["passport_number"],
            nationality=account["nationality"],
            birth_date=account["birth_date"],
            phone_number=account["phone_number"],
            passport_image_path=account.get("passport_image_path")
        )
        print(f"✅ {account['email']} → Success: {result}")
        return result

    with ThreadPoolExecutor(max_workers=len(accounts)) as executor:
        executor.map(run_single, accounts)
