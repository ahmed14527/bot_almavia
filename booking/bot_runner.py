from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def safe_send_keys(driver, element, text):
    if element.get_attribute('disabled') or not element.is_enabled():
        driver.execute_script("arguments[0].removeAttribute('disabled')", element)
        time.sleep(0.5) 
    element.clear()
    element.send_keys(text)

def run_bot(email, password, passport_number, nationality, birth_date, phone_number, passport_image_path):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://egy.almaviva-visa.it/")
        print("✅ Website opened:", driver.current_url)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.bg-visa-primary-500"))
        )
        login_button.click()
        print("✅ Clicked login button")

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        print("✅ Login page loaded")

        username_input = driver.find_element(By.ID, "username")
        safe_send_keys(driver, username_input, email)

        password_input = driver.find_element(By.ID, "password")
        safe_send_keys(driver, password_input, password)

        login_button_form = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "kc-login"))
        )
        login_button_form.click()
        print("✅ Login submitted")

        WebDriverWait(driver, 20).until(
            EC.url_contains("https://egy.almaviva-visa.it/")
        )
        print("✅ Logged in and homepage loaded:", driver.current_url)
        time.sleep(3)  

        book_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/appointment"][title="Go to Take an appointment"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", book_link)
        driver.execute_script("arguments[0].click();", book_link)
        print("✅ Clicked on Book appointment link")

        WebDriverWait(driver, 15).until(
            EC.url_contains("/profile/user-required-data")
        )
        print("✅ Navigated to user-required-data page:", driver.current_url)

        passport_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="passportNumber"]'))
        )
        safe_send_keys(driver, passport_input, passport_number)
        print("✅ Passport number entered")

        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                'input[type="file"][accept*=".pdf"], input[type="file"][accept*=".png"], input[type="file"][accept*=".jpg"], input[type="file"][accept*=".jpeg"]'
            ))
        )
        file_input.send_keys(passport_image_path)
        print(f"✅ Passport image uploaded from: {passport_image_path}")

        time.sleep(2)

        nationality_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'mat-select[formcontrolname="nationality"]'))
        )
        nationality_select.click()
        time.sleep(1)  

        options = driver.find_elements(By.CSS_SELECTOR, 'mat-option')
        selected = False
        for option in options:
            if option.text.strip().lower() == nationality.strip().lower():
                option.click()
                selected = True
                print(f"✅ Nationality selected: {nationality}")
                break
        if not selected:
            print(f"⚠️ Nationality '{nationality}' not found in list.")

        dob_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="dateOfBirth"]'))
        )
        if dob_input.get_attribute('disabled') or not dob_input.is_enabled():
            driver.execute_script("arguments[0].removeAttribute('disabled')", dob_input)
            time.sleep(0.5)
        dob_input.clear()
        if isinstance(birth_date, str):
            dob_str = birth_date
        else:
            dob_str = birth_date.strftime('%d/%m/%Y')
        dob_input.send_keys(dob_str)
        print(f"✅ Date of birth entered: {dob_str}")

        phone_input = driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="phoneNumber"]')
        if phone_input.get_attribute('disabled') or not phone_input.is_enabled():
            print("⚠️ Phone number input is disabled; skipping.")
        else:
            safe_send_keys(driver, phone_input, phone_number)
            print("✅ Phone number entered")

        proceed_button = driver.find_element(By.CSS_SELECTOR, 'button.visasys-button')

        if proceed_button.get_attribute('disabled') or not proceed_button.is_enabled():
            print("⚠️ PROCEED button is disabled; booking not completed.")
            return False

        proceed_button.click()
        print("✅ PROCEED button clicked, waiting for confirmation...")

        try:
            confirmation_msg = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//*[contains(text(), 'تم الحجز بنجاح') or contains(text(), 'Booking confirmed')]"
                ))
            )
            print("✅ Booking confirmed:", confirmation_msg.text)
            return True
        except TimeoutException:
            current_url = driver.current_url
            if "confirmation" in current_url or "success" in current_url:
                print("✅ Booking confirmed by URL change:", current_url)
                return True
            else:
                print("❌ Booking confirmation not detected after clicking PROCEED.")
                return False

    except Exception as e:
        print("❌ Error during process:", e)
        driver.save_screenshot("error.png")
        return False

    finally:
        driver.quit()
