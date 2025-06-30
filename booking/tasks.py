from celery import shared_task, group
from booking.bot_runner import run_bot

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_booking_bot_task(self, account_data):
    """
    account_data: dict يحتوي على مفاتيح مثل:
        email, password, passport_number, nationality, birth_date, phone_number, passport_image_path
    """
    try:
        print(f"⏳ Running bot for: {account_data.get('email')}")

        success = run_bot(
            email=account_data.get('email'),
            password=account_data.get('password'),
            passport_number=account_data.get('passport_number'),
            nationality=account_data.get('nationality'),
            birth_date=account_data.get('birth_date'),
            phone_number=account_data.get('phone_number'),
            passport_image_path=account_data.get('passport_image_path')
        )

        print(f"✅ Finished for: {account_data.get('email')} with status: {'success' if success else 'failed'}")
        return success

    except Exception as e:
        print(f"❌ Error in task for email {account_data.get('email')}: {e}")
        raise self.retry(exc=e)

@shared_task
def run_booking_bot_parallel(accounts):
    """
    accounts: قائمة dict لكل حساب.
    مثال:
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
    tasks = [run_booking_bot_task.s(account) for account in accounts]
    job = group(tasks)()
    return job.id
