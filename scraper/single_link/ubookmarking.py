import sys
import json
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


# ========================
# 🔹 Configuration
# ========================
LOGIN_URL = "https://www.ubookmarking.com/login/re-submit"
SUBMIT_URL = "https://www.ubookmarking.com/submit"
USERNAME = "nalybuxa@forexzig.com"
PASSWORD = "Mannuk@12"


# ========================
# 🔹 Logging Helper
# ========================
def log(msg):
    print(msg, flush=True)


# ========================
# 🔹 Input Reader
# ========================
def get_input_data():
    """Read JSON input from Node backend"""
    raw = sys.stdin.read().strip()
    if not raw:
        log("⚠️ No input received — using fallback URL.")
        return {"url": "https://example.com/fallback"}

    try:
        data = json.loads(raw)
        log(f"✅ Received input: {data}")
        return data
    except json.JSONDecodeError:
        log("❌ Invalid JSON input. Using fallback URL.")
        return {"url": "https://example.com/fallback"}


# ========================
# 🔹 Login Function
# ========================
def login(driver):
    log("🔹 Opening login page...")
    try:
        driver.get(LOGIN_URL)
        time.sleep(2)

        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']").click()

        time.sleep(3)
        if "submit" in driver.current_url:
            log("✅ Login successful.")
            return True
        log(f"❌ Login failed. Current URL: {driver.current_url}")
        return False
    except Exception as e:
        log(f"⚠️ Login error: {e}")
        return False


# ========================
# 🔹 Submission Function
# ========================
def submit_link(driver, url):
    log(f"🟢 Starting submission for: {url}")
    try:
        driver.get(SUBMIT_URL)
        time.sleep(2)

        url_field = driver.find_element(By.ID, "checkUrl")
        url_field.clear()
        url_field.send_keys(url)
        driver.find_element(By.CSS_SELECTOR, "input.checkUrl").click()
        time.sleep(3)

        driver.find_element(By.ID, "articleTitle").send_keys(url)

        # Try selecting 'Travel'
        try:
            category_select = driver.find_element(By.ID, "category")
            for option in category_select.find_elements(By.TAG_NAME, "option"):
                if "Travel" in option.text:
                    option.click()
                    log(f"✅ Selected category: {option.text}")
                    break
        except NoSuchElementException:
            log("⚠️ Category dropdown not found.")

        # Tags
        try:
            driver.find_element(By.ID, "tag").send_keys("travel, adventure, guide")
        except NoSuchElementException:
            log("⚠️ Tag input not found.")

        # Description
        driver.find_element(By.ID, "description").send_keys(f"Check out this link: {url}")

        driver.find_element(By.CSS_SELECTOR, "input.saveChanges").click()
        time.sleep(2)
        driver.find_element(By.ID, "submit").click()
        time.sleep(3)

        log(f"✅ Successfully submitted: {url}")
        return True
    except Exception as e:
        log(f"❌ Submission error: {e}")
        return False


# ========================
# 🔹 Main Runner
# ========================
def main():
    log("🚀 Starting ubookmarking automation...")

    data = get_input_data()
    target_url = data.get("url", "").strip()

    if not target_url or not target_url.startswith("http"):
        log("❌ Invalid or missing URL. Exiting.")
        return

    log(f"📎 Target URL: {target_url}")

    # --- Setup isolated Chrome session ---
    random_port = random.randint(9200, 9400)
    user_data_dir = f"/tmp/chrome_profile_{os.getpid()}_{random_port}"

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument(f"--remote-debugging-port={random_port}")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        if login(driver):
            if not submit_link(driver, target_url):
                log("🔁 Retrying submission...")
                time.sleep(2)
                submit_link(driver, target_url)
        else:
            log("❌ Login failed. Stopping script.")
    finally:
        driver.quit()
        log("🟢 Browser closed.")
        log("🏁 Script finished.")


# ========================
# 🔹 Entry
# ========================
if __name__ == "__main__":
    main()
