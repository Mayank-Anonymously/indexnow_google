import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

USERNAME = "laylawoods270@gmail.com"
PASSWORD = "Mannuk@12"
LOGIN_URL = "https://www.pinlap.com/signin"
HOME_URL = "https://www.pinlap.com/"

def log(msg):
    print(msg, flush=True)

def safe_click(driver, element):
    """Safely click element using JS (handles overlays)."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(0.5)

def main():
    raw = sys.stdin.read().strip() or '{"message": "Automation test 🚀"}'
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"message": "Automation test 🚀"}

    message = data.get("message", "Automation test 🚀")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 25)

    try:
        # --- LOGIN ---
        log("🌐 Opening login page...")
        driver.get(LOGIN_URL)

        # Wait for email and password fields
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "username_email")))
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))

        email_field.clear()
        password_field.clear()
        email_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)

        # Locate the Sign In button and click
        login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fr_welcome_btn")))
        safe_click(driver, login_btn)
        log("🚀 Login submitted...")
        time.sleep(6)

        # --- NAVIGATE TO HOME ---
        driver.get(HOME_URL)
        log("🏠 Navigated to home page, waiting for feed to load...")
        time.sleep(6)

        # --- CLICK PUBLISHER BOX ---
        publisher = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.publisher-message")))
        safe_click(driver, publisher)
        log("✅ Publisher box clicked.")

        # --- WAIT FOR TEXTAREA ---
        textarea = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea.js_publisher-scraper")))
        driver.execute_script("arguments[0].focus(); arguments[0].value = arguments[1];", textarea, message)
        textarea.send_keys(" ")  # trigger input
        time.sleep(2)
        log(f"🖋️ Typed message: {message}")

        # --- CLICK POST BUTTON ---
        post_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.js_publisher-btn.js_publisher")))
        safe_click(driver, post_btn)
        log("✅ Post created successfully!")

    except TimeoutException as e:
        log(f"⏱️ Timeout waiting for an element: {e}")
        driver.save_screenshot("timeout_debug.png")
        log("📸 Saved screenshot as timeout_debug.png for debugging.")
    except WebDriverException as e:
        log(f"⚠️ WebDriver error: {e}")
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
    finally:
        driver.quit()
        log("🟢 Browser closed.")

if __name__ == "__main__":
    main()
