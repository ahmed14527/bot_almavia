import os
import time
import logging
from datetime import datetime
from pathlib import Path
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

def get_media_screenshot_path(booking_id: int, prefix: str = "shot") -> tuple[str, str]:
    media_dir = Path(settings.MEDIA_ROOT) / 'screenshots'
    media_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{prefix}_{booking_id}_{int(time.time())}.png"
    abs_path = str(media_dir / filename)
    rel_url = f"{settings.MEDIA_URL}screenshots/{filename}"
    return abs_path, rel_url

def safe_send_keys(driver, element, text):
    try:
        if element.get_attribute('disabled') or not element.is_enabled():
            driver.execute_script("arguments[0].removeAttribute('disabled')", element)
            time.sleep(0.5)
        element.clear()
        element.send_keys(text)
    except Exception as e:
        logger.warning(f"safe_send_keys warning: {e}")
        try:
            element.send_keys(text)
        except Exception:
            pass

def update_booking_step(booking, step_num: int, total_steps: int, step_desc: str, status=None):
    from booking.models import BookingRequest
    if not booking:
        return
    try:
        booking.refresh_from_db()
        booking.step_progress = step_num
        booking.total_steps = total_steps
        booking.current_step = step_desc
        if status:
            booking.status = status
        booking.save(update_fields=['step_progress', 'total_steps', 'current_step', 'status', 'updated_at'])
    except Exception as e:
        logger.error(f"Failed to update booking progress: {e}")

def check_for_human_challenge(driver) -> bool:
    try:
        page_source = driver.page_source.lower()
        if 'cf-challenge-running' in page_source or 'challenge-platform' in page_source:
            return True
        if 'recaptcha' in page_source or 'hcaptcha' in page_source:
            return True
        if 'verify you are human' in page_source or 'checking your browser' in page_source:
            return True
        if 'enter the code' in page_source or 'one-time password' in page_source or 'otp' in page_source:
            return True
        challenge_elements = driver.find_elements(
            'css selector',
            'iframe[src*="captcha"], iframe[src*="challenge"], #challenge-stage, .cf-turnstile-wrapper, input[name="otp"]'
        )
        return len(challenge_elements) > 0
    except Exception:
        return False

def wait_for_user_resume(booking, driver, max_wait_seconds: int = 180) -> str:
    from booking.models import BookingRequest
    abs_path, rel_url = get_media_screenshot_path(booking.id, "verification")
    try:
        driver.save_screenshot(abs_path)
    except Exception:
        pass

    booking.refresh_from_db()
    booking.status = BookingRequest.Status.WAITING_FOR_USER
    booking.current_step = "Human Verification Required (CAPTCHA / OTP)"
    booking.action_required = "Please solve the security challenge / enter OTP in the browser session, then click 'Resume Workflow' in the dashboard."
    booking.last_screenshot = rel_url
    booking.save(update_fields=['status', 'current_step', 'action_required', 'last_screenshot', 'updated_at'])
    logger.info(f"Booking {booking.id} is WAITING_FOR_USER. Waiting up to {max_wait_seconds}s...")

    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        time.sleep(2.5)
        booking.refresh_from_db()

        if booking.status == BookingRequest.Status.CANCELLED:
            logger.info(f"Booking {booking.id} was cancelled by user.")
            return "CANCELLED"

        if booking.status == BookingRequest.Status.RUNNING:
            logger.info(f"Booking {booking.id} resumed by user.")
            booking.action_required = ""
            booking.save(update_fields=['action_required', 'updated_at'])
            return "RESUMED"

    return "TIMEOUT"

def run_simulation(booking):
    from booking.models import BookingRequest
    logger.info(f"Running simulation for booking {booking.id} ({booking.email})")

    steps = [
        (1, "Initializing simulated browser session"),
        (2, "Navigating to Italian Visa portal (egy.almaviva-visa.it)"),
        (3, "Submitting authentication credentials"),
        (4, "Checking for security challenge / human verification"),
        (5, "Navigating to appointment scheduling section"),
        (6, "Loading applicant profile details form"),
        (7, "Filling passport data and uploading required documents"),
        (8, "Confirming appointment booking and verifying reference number"),
    ]

    booking.status = BookingRequest.Status.RUNNING
    booking.save(update_fields=['status', 'updated_at'])

    for step_num, step_desc in steps:
        booking.refresh_from_db()
        if booking.status == BookingRequest.Status.CANCELLED:
            logger.info(f"Simulation cancelled for booking {booking.id}")
            return False

        update_booking_step(booking, step_num, 8, step_desc)
        time.sleep(1.0)

        # Trigger human verification simulation if requested
        if step_num == 4 and ('captcha' in booking.email.lower() or 'otp' in booking.email.lower()):
            booking.status = BookingRequest.Status.WAITING_FOR_USER
            booking.current_step = "Human Verification Required"
            booking.action_required = "Simulation: Security challenge detected. Click 'Resume' in the dashboard to continue."
            booking.save(update_fields=['status', 'current_step', 'action_required', 'updated_at'])

            start_wait = time.time()
            resumed = False
            while time.time() - start_wait < 60:
                time.sleep(1.0)
                booking.refresh_from_db()
                if booking.status == BookingRequest.Status.CANCELLED:
                    return False
                if booking.status == BookingRequest.Status.RUNNING:
                    resumed = True
                    booking.action_required = ""
                    booking.save(update_fields=['action_required', 'updated_at'])
                    break

            if not resumed:
                booking.status = BookingRequest.Status.FAILED
                booking.error_message = "Simulation: Timed out waiting for human verification resume."
                booking.save(update_fields=['status', 'error_message', 'updated_at'])
                return False

    if 'fail' in booking.email.lower():
        booking.status = BookingRequest.Status.FAILED
        booking.error_message = "Simulation: No appointment slots currently available on embassy portal."
        booking.save(update_fields=['status', 'error_message', 'updated_at'])
        return False

    booking.status = BookingRequest.Status.SUCCESS
    booking.current_step = "Appointment confirmed successfully"
    booking.reference_number = f"IT-ALM-{booking.id:04d}-{int(time.time()) % 100000}"
    booking.appointment_date = (timezone.now() + timezone.timedelta(days=14)).strftime('%Y-%m-%d 10:30')
    booking.save(update_fields=['status', 'current_step', 'reference_number', 'appointment_date', 'updated_at'])
    return True

def run_bot(booking_id: int = None, email: str = None, password: str = None, passport_number: str = None,
            nationality: str = None, birth_date = None, phone_number: str = None,
            passport_image_path: str = None, simulate: bool = False) -> bool:
    from booking.models import BookingRequest
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException

    booking = None
    if booking_id:
        try:
            booking = BookingRequest.objects.get(id=booking_id)
            email = booking.email
            password = booking.password
            passport_number = booking.passport_number
            nationality = booking.nationality
            birth_date = booking.birth_date
            phone_number = booking.phone_number
            if not passport_image_path and booking.passport_image:
                try:
                    passport_image_path = booking.passport_image.path
                except Exception:
                    passport_image_path = None
        except BookingRequest.DoesNotExist:
            logger.error(f"BookingRequest {booking_id} does not exist.")
            return False

    # Check for simulation mode
    is_simulation = simulate or getattr(settings, 'BOT_SIMULATION_MODE', False)
    if is_simulation and booking:
        return run_simulation(booking)

    if booking:
        booking.refresh_from_db()
        if booking.status == BookingRequest.Status.CANCELLED:
            return False
        booking.status = BookingRequest.Status.RUNNING
        booking.retry_count += 1
        booking.error_message = ""
        booking.save(update_fields=['status', 'retry_count', 'error_message', 'updated_at'])

    chrome_options = Options()
    is_headless = getattr(settings, 'SELENIUM_HEADLESS', True)
    if is_headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")

    # Detect Linux container Chromium binary
    chrome_bin = os.environ.get("CHROME_BIN")
    if not chrome_bin:
        for candidate in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
            if os.path.exists(candidate):
                chrome_bin = candidate
                break
    if chrome_bin:
        chrome_options.binary_location = chrome_bin

    # Detect Linux container Chromedriver path
    driver_path = os.environ.get("CHROMEDRIVER_PATH")
    if not driver_path:
        for candidate in ("/usr/bin/chromedriver", "/usr/lib/chromium/chromedriver"):
            if os.path.exists(candidate):
                driver_path = candidate
                break

    driver = None
    try:
        update_booking_step(booking, 1, 8, "Initializing secure browser session")
        if driver_path:
            from selenium.webdriver.chrome.service import Service
            driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(45)

        update_booking_step(booking, 2, 8, "Navigating to Italian Visa portal")
        driver.get("https://egy.almaviva-visa.it/")
        time.sleep(2)

        # Check for initial Cloudflare / human challenge
        if check_for_human_challenge(driver) and booking:
            result = wait_for_user_resume(booking, driver)
            if result != "RESUMED":
                return False
            update_booking_step(booking, 2, 8, "Navigating to Italian Visa portal", status=BookingRequest.Status.RUNNING)

        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.bg-visa-primary-500"))
        )
        login_button.click()

        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )

        update_booking_step(booking, 3, 8, "Entering user authentication credentials")
        username_input = driver.find_element(By.ID, "username")
        safe_send_keys(driver, username_input, email)

        password_input = driver.find_element(By.ID, "password")
        safe_send_keys(driver, password_input, password)

        login_button_form = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "kc-login"))
        )
        login_button_form.click()

        update_booking_step(booking, 4, 8, "Checking for security challenge / human verification")
        time.sleep(3)

        # Check if 2FA / OTP or CAPTCHA appeared on login
        if check_for_human_challenge(driver) and booking:
            result = wait_for_user_resume(booking, driver)
            if result != "RESUMED":
                return False
            update_booking_step(booking, 4, 8, "Security verification completed", status=BookingRequest.Status.RUNNING)

        # Wait for portal redirect after login
        WebDriverWait(driver, 25).until(
            EC.url_contains("https://egy.almaviva-visa.it/")
        )
        time.sleep(2)

        update_booking_step(booking, 5, 8, "Navigating to appointment booking section")
        book_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/appointment"][title="Go to Take an appointment"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", book_link)
        driver.execute_script("arguments[0].click();", book_link)

        update_booking_step(booking, 6, 8, "Loading applicant profile details form")
        WebDriverWait(driver, 20).until(
            EC.url_contains("/profile/user-required-data")
        )

        update_booking_step(booking, 7, 8, "Entering applicant details and uploading documents")
        passport_input = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="passportNumber"]'))
        )
        safe_send_keys(driver, passport_input, passport_number)

        if passport_image_path and os.path.exists(passport_image_path):
            try:
                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        'input[type="file"][accept*=".pdf"], input[type="file"][accept*=".png"], input[type="file"][accept*=".jpg"], input[type="file"][accept*=".jpeg"]'
                    ))
                )
                file_input.send_keys(passport_image_path)
                time.sleep(1.5)
            except Exception as e:
                logger.warning(f"File upload element warning: {e}")

        nationality_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'mat-select[formcontrolname="nationality"]'))
        )
        nationality_select.click()
        time.sleep(1)

        options = driver.find_elements(By.CSS_SELECTOR, 'mat-option')
        for option in options:
            if option.text.strip().lower() == nationality.strip().lower():
                option.click()
                break

        dob_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="dateOfBirth"]'))
        )
        if isinstance(birth_date, str):
            dob_str = birth_date
        elif hasattr(birth_date, 'strftime'):
            dob_str = birth_date.strftime('%d/%m/%Y')
        else:
            dob_str = str(birth_date)
        safe_send_keys(driver, dob_input, dob_str)

        try:
            phone_input = driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="phoneNumber"]')
            if not phone_input.get_attribute('disabled') and phone_input.is_enabled():
                safe_send_keys(driver, phone_input, phone_number)
        except Exception:
            pass

        update_booking_step(booking, 8, 8, "Submitting appointment and verifying confirmation")
        proceed_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.visasys-button'))
        )

        if proceed_button.get_attribute('disabled') or not proceed_button.is_enabled():
            if booking:
                abs_path, rel_url = get_media_screenshot_path(booking.id, "slot_unavailable")
                driver.save_screenshot(abs_path)
                booking.status = BookingRequest.Status.FAILED
                booking.current_step = "No appointment slots available"
                booking.error_message = "Proceed button disabled: No available appointment slots found."
                booking.last_screenshot = rel_url
                booking.save(update_fields=['status', 'current_step', 'error_message', 'last_screenshot', 'updated_at'])
            return False

        proceed_button.click()

        # Strict confirmation check
        confirmed = False
        ref_num = ""
        try:
            confirmation_elem = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//*[contains(text(), 'تم الحجز بنجاح') or contains(text(), 'Booking confirmed') or contains(text(), 'Appuntamento confermato')]"
                ))
            )
            confirmed = True
            ref_num = confirmation_elem.text.strip()[:60]
        except TimeoutException:
            current_url = driver.current_url.lower()
            if "confirmation" in current_url or "appointment-success" in current_url:
                confirmed = True

        if confirmed:
            if booking:
                abs_path, rel_url = get_media_screenshot_path(booking.id, "success")
                driver.save_screenshot(abs_path)
                booking.status = BookingRequest.Status.SUCCESS
                booking.current_step = "Appointment confirmed successfully"
                booking.reference_number = ref_num or f"IT-ALM-{booking.id}-{int(time.time()) % 10000}"
                booking.last_screenshot = rel_url
                booking.save(update_fields=['status', 'current_step', 'reference_number', 'last_screenshot', 'updated_at'])
            return True
        else:
            if booking:
                abs_path, rel_url = get_media_screenshot_path(booking.id, "unconfirmed")
                driver.save_screenshot(abs_path)
                booking.status = BookingRequest.Status.FAILED
                booking.current_step = "Confirmation not verified"
                booking.error_message = "Official booking confirmation was not detected after submitting."
                booking.last_screenshot = rel_url
                booking.save(update_fields=['status', 'current_step', 'error_message', 'last_screenshot', 'updated_at'])
            return False

    except Exception as e:
        logger.error(f"Error during bot execution for booking {booking_id or email}: {e}")
        if booking:
            try:
                abs_path, rel_url = get_media_screenshot_path(booking.id, "error")
                if driver:
                    driver.save_screenshot(abs_path)
                booking.status = BookingRequest.Status.FAILED
                booking.current_step = "Encountered system error"
                booking.error_message = str(e)[:300]
                booking.last_screenshot = rel_url if driver else ""
                booking.save(update_fields=['status', 'current_step', 'error_message', 'last_screenshot', 'updated_at'])
            except Exception:
                pass
        return False

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
