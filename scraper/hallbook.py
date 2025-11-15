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
LOGIN_URL = "https://hallbook.com.br/signin"
HOME_URL = "https://hallbook.com.br/"

def log(msg):
    print(msg, flush=True)

def safe_click(driver, element):
    """Safely click element using JS (handles overlays)."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.4)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(0.8)

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
    wait = WebDriverWait(driver, 40)

    try:
        log("🌐 Opening login page...")
        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(4)  # allow page scripts to initialize

        # Locate fields more robustly (React form uses dynamic rendering)
        email_field = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username_email'], input[type='email']"))
        )
        password_field = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password'], input[type='password']"))
        )

        # Use JS to fill fields (bypasses React interference)
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_field, USERNAME)
        time.sleep(0.5)
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field, PASSWORD)
        time.sleep(0.5)

        # Find Sign In button and click
        login_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sign In') or contains(., 'Login')]"))
        )
        safe_click(driver, login_btn)
        log("🚀 Login submitted...")

        time.sleep(8)

        driver.get(HOME_URL)
        log("🏠 Navigated to home page, waiting for feed to load...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)

        # ✅ Click on publisher div (not textarea yet)
        publisher_div = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.publisher-message.position-relative"))
        )
        safe_click(driver, publisher_div)
        log("✅ Publisher box clicked successfully.")

        # ✅ Wait for the textarea to become visible (it appears after div click)
        textarea = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea.js_publisher-scraper"))
        )

        # ✅ Type message properly using JS (React-friendly)
        driver.execute_script("""
            arguments[0].focus();
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """, textarea, message)
        time.sleep(1)
        log(f"🖋️ Typed message: {message}")

        # ✅ Find and click the Post button
        post_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.js_publisher-btn.js_publisher"))
        )
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
