import logging
import threading
from celery import shared_task
from booking.bot_runner import run_bot

logger = logging.getLogger(__name__)

@shared_task(bind=True, acks_late=True, max_retries=1, default_retry_delay=30)
def run_booking_bot_task(self, booking_id: int):
    """
    Celery task that executes the automated booking workflow for a BookingRequest.
    """
    from booking.models import BookingRequest
    try:
        booking = BookingRequest.objects.get(id=booking_id)
        booking.celery_task_id = getattr(self.request, 'id', '') or ''
        booking.save(update_fields=['celery_task_id', 'updated_at'])
    except BookingRequest.DoesNotExist:
        logger.error(f"BookingRequest {booking_id} does not exist.")
        return {"booking_id": booking_id, "status": "not_found"}

    logger.info(f"Starting booking automation task for booking ID: {booking_id}")
    try:
        success = run_bot(booking_id=booking_id)
        return {"booking_id": booking_id, "status": "success" if success else "failed"}
    except Exception as e:
        logger.error(f"Error in task for booking {booking_id}: {e}")
        raise self.retry(exc=e)

def execute_in_background_thread(booking_id: int):
    """
    Direct asynchronous execution in a background thread when Celery is not active.
    """
    def worker():
        try:
            run_bot(booking_id=booking_id)
        except Exception as e:
            logger.error(f"Background thread error for booking {booking_id}: {e}")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return thread

def dispatch_booking_job(booking_id: int, prefer_celery: bool = True):
    """
    Smart dispatcher that attempts Celery first, falling back to background thread
    if Redis / Celery broker is unavailable.
    """
    if prefer_celery:
        try:
            result = run_booking_bot_task.delay(booking_id)
            logger.info(f"Dispatched booking {booking_id} to Celery: {result.id}")
            return {"type": "celery", "task_id": result.id}
        except Exception as e:
            logger.warning(f"Celery dispatch failed for {booking_id} ({e}), falling back to background thread.")

    execute_in_background_thread(booking_id)
    return {"type": "thread", "task_id": f"thread-{booking_id}"}
