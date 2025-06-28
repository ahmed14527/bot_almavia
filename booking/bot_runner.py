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
        driver.get("https://egy.almaviva-visa.it/")
        print("✅ Website opened:", driver.current_url)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.bg-visa-primary-500"))
        )
        login_button.click()
        print("✅ Clicked login button")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        print("✅ Login page loaded")

        username_input = driver.find_element(By.ID, "username")
        username_input.clear()
        username_input.send_keys(email)

        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(password)

        # انتظر حتى يصبح زر تسجيل الدخول قابل للنقر ثم اضغط عليه
        login_button_form = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "kc-login"))
        )
        login_button_form.click()
        print("✅ Login submitted")

        WebDriverWait(driver, 15).until(
            lambda d: d.current_url != "https://egy.almaviva-visa.it/"
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
