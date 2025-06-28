from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def run_bot(email, password):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # افتح الموقع
        driver.get("https://egy.almaviva-visa.it/")
        print("✅ Website opened:", driver.current_url)

        # اضغط زر تسجيل الدخول
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.bg-visa-primary-500"))
        )
        login_button.click()
        print("✅ Clicked login button")

        # انتظر تحميل صفحة تسجيل الدخول
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        print("✅ Login page loaded")

        # اكتب البريد وكلمة المرور
        username_input = driver.find_element(By.ID, "username")
        username_input.clear()
        username_input.send_keys(email)

        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(password)

        # اضغط زر تسجيل الدخول في الفورم
        login_button_form = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "kc-login"))
        )
        login_button_form.click()
        print("✅ Login submitted")

        # انتظر حتى يعيد تحميل الصفحة الرئيسية بعد تسجيل الدخول (URL قد يحتوي بارامترات)
        WebDriverWait(driver, 20).until(
            EC.url_contains("https://egy.almaviva-visa.it/")
        )
        print("✅ Logged in and homepage loaded:", driver.current_url)

        # انتظر شوية لضمان تحميل كامل الصفحة
        time.sleep(3)

        # ابحث عن زرار Book أو رابط الحجز واضغط عليه
        # تأكد CSS Selector مضبوط مع صفحة الموقع
        book_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/appointment"][title="Go to Take an appointment"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", book_link)
        driver.execute_script("arguments[0].click();", book_link)
        print("✅ Clicked on Book appointment link")

        # انتظر تحميل الصفحة الخاصة بالبيانات المطلوبة أو الحجز
        WebDriverWait(driver, 15).until(
            EC.url_contains("/profile/user-required-data")
        )
        print("✅ Navigated to user-required-data page:", driver.current_url)

        driver.save_screenshot("after_click_book.png")

        return True

    except Exception as e:
        print("❌ Error during process:", e)
        driver.save_screenshot("error.png")
        return False

    finally:
        driver.quit()

# مثال للاستخدام:
# run_bot("your_email@example.com", "your_password")
