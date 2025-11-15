import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
)
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
# 🔹 Get Data from Frontend
# ========================
def get_input_data():
    """
    Reads JSON from stdin (sent by Node backend).
    Example:
      { "url": "https://example.com/my-article" }
    """
    log("📥 Waiting for data from backend...")
    raw = sys.stdin.read().strip()

    if not raw:
        log("⚠️ No input received. Using fallback URL.")
        return {"url": "https://example.com/default"}

    try:
        data = json.loads(raw)
        log(f"✅ Received input: {data}")
        return data
    except json.JSONDecodeError:
        log("❌ Invalid JSON input. Using fallback URL.")
        return {"url": "https://example.com/default"}


# ========================
# 🔹 Login Function
# ========================
def login(driver: webdriver.Chrome) -> bool:
    log("🔹 Opening login page...")
    try:
        driver.get(LOGIN_URL)
        time.sleep(2)

        log("🔹 Filling credentials...")
        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)

        log("🔹 Submitting login form...")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']").click()
        time.sleep(3)

        if "submit" in driver.current_url.lower():
            log("✅ Login successful.")
            return True
        else:
            log(f"❌ Login failed. Current URL: {driver.current_url}")
            return False

    except Exception as e:
        log(f"⚠️ Login error: {e}")
        return False


# ========================
# 🔹 Submission Function
# ========================
def submit_link(driver: webdriver.Chrome, url: str) -> bool:
    log(f"\n🟢 Starting submission for: {url}")
    try:
        driver.get(SUBMIT_URL)
        time.sleep(2)

        # URL input
        try:
            url_field = driver.find_element(By.ID, "checkUrl")
            url_field.clear()
            url_field.send_keys(url)
            driver.find_element(By.CSS_SELECTOR, "input.checkUrl").click()
            log("✅ URL checked.")
        except NoSuchElementException:
            log("❌ URL field not found.")
            return False

        time.sleep(3)

        # Article title
        try:
            driver.find_element(By.ID, "articleTitle").send_keys(url)
            log("✅ Article title filled.")
        except NoSuchElementException:
            log("⚠️ Title field missing.")

        # Category
        try:
            category_select = driver.find_element(By.ID, "category")
            options = category_select.find_elements(By.TAG_NAME, "option")
            for option in options:
                if "Travel" in option.text:
                    option.click()
                    log(f"✅ Selected category: {option.text}")
                    break
            else:
                log("⚠️ 'Travel' category not found, using default.")
        except NoSuchElementException:
            log("⚠️ Category dropdown not found.")

        # Tags (optional)
        try:
            tag_field = driver.find_element(By.ID, "tag")
            tag_field.send_keys("travel, adventure, guide")
            log("✅ Tags added.")
        except NoSuchElementException:
            log("⚠️ Tag field not found — skipped.")

        # Description
        try:
            desc = driver.find_element(By.ID, "description")
            desc.send_keys(f"Read more about this: {url}")
            log("✅ Description filled.")
        except NoSuchElementException:
            log("⚠️ Description field missing.")

        # Save & Submit
        try:
            driver.find_element(By.CSS_SELECTOR, "input.saveChanges").click()
            time.sleep(2)
            log("💾 Saved changes.")
        except NoSuchElementException:
            log("⚠️ Save button missing.")

        try:
            driver.find_element(By.ID, "submit").click()
            time.sleep(3)
            log("📨 Submitted successfully.")
        except NoSuchElementException:
            log("❌ Submit button not found.")
            return False

        log(f"✅ Successfully submitted: {url}")
        return True

    except WebDriverException as e:
        log(f"⚠️ WebDriver error: {e}")
        return False
    except Exception as e:
        log(f"⚠️ Unknown error: {e}")
        return False


# ========================
# 🔹 Main Runner
# ========================
def main():
    log("🚀 Starting ubookmarking automation (frontend-integrated)...")

    # 1️⃣ Receive JSON data
    data = get_input_data()
    target_url = data.get("url", "").strip()

    if not target_url or not target_url.startswith("http"):
        log("❌ Invalid or missing URL. Exiting.")
        return

    log(f"📎 Target URL: {target_url}")

    # 2️⃣ Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    try:
        # 3️⃣ Login
        if not login(driver):
            log("❌ Login failed. Stopping process.")
            return

        # 4️⃣ Submit
        success = submit_link(driver, target_url)
        if not success:
            log("🔁 Retrying submission...")
            time.sleep(3)
            submit_link(driver, target_url)

        log("✅ Process complete.")
    finally:
        driver.quit()
        log("🟢 Browser closed.")
        log("🏁 Script finished.")


# ========================
# 🔹 Entry Point
# ========================
if __name__ == "__main__":
    main()
