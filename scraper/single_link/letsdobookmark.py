import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL = "https://www.letsdobookmark.com/login/re-submit"
SUBMIT_URL = "https://www.letsdobookmark.com/submit"
USERNAME = "nalybuxa@forexzig.com"
PASSWORD = "Mannuk@12"

def log(msg): print(msg, flush=True)

def get_input_data():
    log("📥 Waiting for data from backend...")
    raw = sys.stdin.read().strip()
    if not raw:
        log("⚠️ No input received, using fallback URL.")
        return {"targetUrl": "https://example.com/default"}
    try:
        data = json.loads(raw)
        log(f"✅ Received input: {data}")
        return data
    except json.JSONDecodeError:
        log("❌ Failed to decode JSON input. Using fallback URL.")
        return {"targetUrl": "https://example.com/default"}

def login(driver):
    try:
        log("🔹 Opening login page...")
        driver.get(LOGIN_URL)
        time.sleep(2)
        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']").click()
        time.sleep(3)
        if "submit" in driver.current_url:
            log("✅ Login successful.")
            return True
        log(f"❌ Login failed: {driver.current_url}")
        return False
    except Exception as e:
        log(f"⚠️ Login error: {e}")
        return False

def submit_link(driver, url):
    try:
        log(f"🟢 Starting submission for: {url}")
        driver.get(SUBMIT_URL)
        time.sleep(2)
        url_field = driver.find_element(By.ID, "checkUrl")
        url_field.clear()
        url_field.send_keys(url)
        driver.find_element(By.CSS_SELECTOR, "input.checkUrl").click()
        time.sleep(3)

        driver.find_element(By.ID, "articleTitle").send_keys(url)

        category = driver.find_element(By.ID, "category")
        for opt in category.find_elements(By.TAG_NAME, "option"):
            if "Travel" in opt.text:
                opt.click()
                log(f"✅ Selected category: {opt.text}")
                break

        try:
            driver.find_element(By.ID, "tag").send_keys("travel, adventure, guide")
        except NoSuchElementException:
            log("⚠️ Tag field not found — skipped.")

        driver.find_element(By.ID, "description").send_keys(url * 3)
        driver.find_element(By.CSS_SELECTOR, "input.saveChanges").click()
        time.sleep(1)
        driver.find_element(By.ID, "submit").click()
        time.sleep(2)
        log("✅ Successfully submitted link.")
        return True
    except Exception as e:
        log(f"❌ Error submitting link: {e}")
        return False

def main():
    data = get_input_data()
    target_url = (data.get("url") or data.get("targetUrl", "")).strip()
    if not target_url or not target_url.startswith("http"):
        log("❌ Invalid URL from frontend.")
        return

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        if not login(driver):
            return
        submit_link(driver, target_url)
    finally:
        driver.quit()
        log("🟢 Browser closed.")

if __name__ == "__main__":
    main()
