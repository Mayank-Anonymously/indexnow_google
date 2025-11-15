import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

USERNAME = "laylawoods270@gmail.com"
PASSWORD = "Mannuk@12"
LOGIN_URL = "https://thesn.eu/signin"
HOME_URL = "https://thesn.eu/"

def log(msg):
    print(msg, flush=True)

def remove_overlays(driver):
    driver.execute_script("""
        document.querySelectorAll("[style*='z-index: 2147483647']").forEach(el => el.remove());
    """)

def safe_click(driver, element):
    """Try JS-based click with retries."""
    for attempt in range(3):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", element)
            return True
        except (ElementClickInterceptedException, WebDriverException):
            log(f"⚠️ Click failed (attempt {attempt+1}), retrying...")
            remove_overlays(driver)
            time.sleep(1)
    return False

def wait_for_publisher(driver, wait, max_scrolls=10):
    """Scroll and retry until publisher-message is visible."""
    for i in range(max_scrolls):
        try:
            elem = driver.find_element(By.CSS_SELECTOR, "div.publisher-message")
            if elem.is_displayed():
                return elem
        except NoSuchElementException:
            pass
        driver.execute_script("window.scrollBy(0, 400);")
        log(f"🔎 Scrolling attempt {i+1} to locate publisher box...")
        time.sleep(1)
    raise TimeoutException("Publisher div not found after scrolling.")

def wait_for_link_preview(driver, timeout=20):
    """
    Wait until link preview (metadata box) appears after pasting a link.
    Returns True if preview detected, False if timeout.
    """
    log("⏳ Waiting for link preview to load (if any)...")
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            preview = driver.find_element(By.CSS_SELECTOR, "div.publisher-meta, div.publisher-link")
            if preview.is_displayed():
                log("🔗 Link preview detected — waiting for final load...")
                time.sleep(2)
                return True
        except NoSuchElementException:
            pass
        time.sleep(1)
    log("⚠️ No link preview detected (continuing without it).")
    return False

def main():
    raw = sys.stdin.read().strip()
    if not raw:
        raw = '{"message": "https://example.com — check this out 🚀"}'

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
    wait = WebDriverWait(driver, 30)

    try:
        # --- LOGIN ---
        log("🌐 Opening login page...")
        driver.get(LOGIN_URL)
        username_input = wait.until(
            EC.presence_of_element_located((By.NAME, "username_email"))
        )
        password_input = wait.until(
            EC.presence_of_element_located((By.NAME, "password"))
        )

        username_input.clear()
        username_input.send_keys(USERNAME)
        password_input.clear()
        password_input.send_keys(PASSWORD)

        log("🔑 Credentials entered. Locating login button...")

        login_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "button.btn.btn-block.btn-primary.bg-gradient-blue.border-0.rounded-pill"
            ))
        )
        safe_click(driver, login_button)
        log("🚀 Login button clicked successfully.")
        time.sleep(5)

        # --- HOME PAGE ---
        driver.get(HOME_URL)
        log("🏠 Navigated to home page, waiting for feed...")
        time.sleep(6)
        remove_overlays(driver)

        # --- WAIT FOR PUBLISHER BOX ---
        publisher_div = wait_for_publisher(driver, wait)
        log("✅ Publisher message box found!")

        safe_click(driver, publisher_div)
        log("🖱️ Clicked inside publisher box.")
        time.sleep(2)

        # --- TYPE MESSAGE / LINK ---
        textarea = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "textarea.js_publisher-scraper")
            )
        )
        driver.execute_script("arguments[0].focus();", textarea)
        driver.execute_script("arguments[0].value = arguments[1];", textarea, message)
        textarea.send_keys(" ")  # trigger input event
        log(f"✍️ Typed message: {message}")

        # --- WAIT FOR LINK PREVIEW BEFORE POSTING ---
        wait_for_link_preview(driver)

        # --- CLICK POST BUTTON ---
        post_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.ml5.js_publisher-btn.js_publisher"))
        )
        safe_click(driver, post_btn)
        log("🚀 Clicked 'Post' button successfully.")
        
        time.sleep(4)
        log("✅ Post created successfully!")

    except TimeoutException as e:
        log(f"⏱️ Timeout error: {e}")
        driver.save_screenshot("timeout_debug.png")
        log("📸 Saved screenshot as timeout_debug.png for inspection.")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
    finally:
        driver.quit()
        log("🟢 Browser closed.")

if __name__ == "__main__":
    main()
