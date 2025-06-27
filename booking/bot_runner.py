from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_bot(email, password):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # افتح الموقع
        driver.get("https://egy.almaviva-visa.it/")
        print("✅ Website opened:", driver.current_url)

        # اضغط على زر تسجيل الدخول (زر فيه ايقونة الشخص)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.bg-visa-primary-500"))
        )
        login_button.click()
        print("✅ Clicked login button")

        # انتظر تحميل صفحة تسجيل الدخول (ننتظر ظهور input البريد الإلكتروني)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        print("✅ Login page loaded")

        # املأ البريد الإلكتروني
        driver.find_element(By.ID, "username").send_keys(email)

        # املأ كلمة المرور
        driver.find_element(By.ID, "password").send_keys(password)

        # اضغط زر تسجيل الدخول
        driver.find_element(By.ID, "kc-login").click()

        # انتظر تحميل الصفحة التالية (مثلاً عنوان URL يحتوي "dashboard" أو "appointment" أو أي علامة نجاح)
        WebDriverWait(driver, 10).until(
            lambda d: "dashboard" in d.current_url or "appointment" in d.current_url
        )

        print("✅ Logged in successfully, current URL:", driver.current_url)
        driver.save_screenshot("after_login.png")

        return True

    except Exception as e:
        print("❌ Error during login:", e)
        driver.save_screenshot("login_error.png")
        return False

    finally:
        driver.quit()
