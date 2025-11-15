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
)

USERNAME = "laylawoods270@gmail.com"
PASSWORD = "Mannuk@12"
LOGIN_URL = "https://followingbook.com/welcome"
HOME_URL = "https://followingbook.com/"

def log(msg):
    print(msg, flush=True)

def remove_overlays(driver):
    """Remove any high z-index overlays that block actions"""
    driver.execute_script("""
        document.querySelectorAll("div[style*='z-index: 2147483647']").forEach(el => el.remove());
    """)

def safe_click(driver, element):
    """Perform a JS-based click with overlay handling"""
    for attempt in range(3):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", element)
            return
        except ElementClickInterceptedException:
            log(f"⚠️ Click blocked (attempt {attempt+1}) — cleaning overlays...")
            remove_overlays(driver)
            time.sleep(1)
    raise Exception("❌ Failed to click element after retries")

def main():
    raw = sys.stdin.read().strip()
    if not raw:
        log("❌ No JSON input received.")
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        log("❌ Invalid JSON format.")
        return

    message = data.get("message", "Check out this great content! 🚀")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-infobars")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        # --- LOGIN ---
        log("🌐 Opening login page...")
        driver.get(LOGIN_URL)

        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        log("🔑 Credentials entered.")

        login_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-main.btn-mat.add_wow_loader"))
        )
        safe_click(driver, login_btn)
        log("🚀 Login submitted...")

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".wow_content.user-status-home")))
        log("✅ Logged in successfully!")

        # --- NAVIGATE TO HOME ---
        driver.get(HOME_URL)
        log("🏠 Navigated to home page.")
        remove_overlays(driver)
        time.sleep(1)

        # --- STEP 1: Click 'Create Post' ---
        create_post_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.wo_pub_txtara_combo button.btn.btn-main"))
        )
        safe_click(driver, create_post_btn)
        log("📝 Clicked 'Create post' button.")

        # --- STEP 2: Wait for textarea and enter message ---
        textarea = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[name='postText']"))
        )
        driver.execute_script("arguments[0].focus();", textarea)
        driver.execute_script("arguments[0].value = arguments[1];", textarea, message)
        log(f"✍️ Typed message: {message * 5}")

        time.sleep(1)

        # --- STEP 3: Click 'Share' button ---
        share_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='publisher-button']/span"))
        )
        safe_click(driver, share_btn)
        log("🚀 Clicked 'Share' button.")       

        # --- Wait for post completion ---
        time.sleep(3)
        log("✅ Post created successfully!")

    except TimeoutException as e:
        log(f"⏱️ Timeout error: {e}")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
    finally:
        driver.quit()
        log("🟢 Browser closed.")

if __name__ == "__main__":
    main()
