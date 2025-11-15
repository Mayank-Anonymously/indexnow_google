import sys
import json
import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


LOGIN_URL = "https://www.starbookmarking.com/login/re-submit"
SUBMIT_URL = "https://www.starbookmarking.com/submit"
USERNAME = "nalybuxa@forexzig.com"
PASSWORD = "Mannuk@12"


def log(msg):
    print(msg, flush=True)


def get_input_data():
    log("📥 Waiting for data from frontend...")
    raw = sys.stdin.read().strip()
    if not raw:
        log("⚠️ No input received, using fallback URL.")
        return {"url": "https://example.com/default"}

    try:
        data = json.loads(raw)
        log(f"✅ Received input: {data}")
        return data
    except json.JSONDecodeError:
        log("❌ Invalid JSON input. Using fallback URL.")
        return {"url": "https://example.com/default"}


def login(driver: webdriver.Chrome) -> bool:
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
        else:
            log(f"❌ Login failed, current URL: {driver.current_url}")
            return False

    except Exception as e:
        log(f"⚠️ Login error: {e}")
        return False


def submit_link(driver: webdriver.Chrome, url: str) -> bool:
    log(f"\n🟢 Starting submission for: {url}")
    try:
        driver.get(SUBMIT_URL)
        time.sleep(2)

        url_field = driver.find_element(By.ID, "checkUrl")
        url_field.clear()
        url_field.send_keys(url)
        driver.find_element(By.CSS_SELECTOR, "input.checkUrl").click()
        time.sleep(3)

        driver.find_element(By.ID, "articleTitle").send_keys(url)

        # Select category "Travel"
        category_select = driver.find_element(By.ID, "category")
        found = False
        for option in category_select.find_elements(By.TAG_NAME, "option"):
            if "Travel" in option.text:
                option.click()
                log(f"✅ Selected category: {option.text}")
                found = True
                break
        if not found:
            log("⚠️ 'Travel' category not found — using default.")

        # Tags
        try:
            driver.find_element(By.ID, "tag").send_keys("travel, adventure, guide")
        except NoSuchElementException:
            log("⚠️ Tag field not found — skipped.")

        driver.find_element(By.ID, "description").send_keys(f"Read more at {url}")
        driver.find_element(By.CSS_SELECTOR, "input.saveChanges").click()
        time.sleep(2)
        driver.find_element(By.ID, "submit").click()
        time.sleep(3)

        log(f"✅ Successfully submitted: {url}")
        return True

    except NoSuchElementException as e:
        log(f"❌ Missing element: {e}")
        return False
    except WebDriverException as e:
        log(f"⚠️ WebDriver issue: {e}")
        return False
    except Exception as e:
        log(f"⚠️ Unknown error: {e}")
        return False


def main():
    log("🚀 Starting StarBookmarking automation (frontend integrated)...")

    data = get_input_data()
    target_url = data.get("url", "").strip()

    if not target_url.startswith("http"):
        log("❌ Invalid or missing 'url'. Exiting.")
        return

    log(f"📎 Target URL to submit: {target_url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        if not login(driver):
            log("❌ Login failed. Exiting.")
            return

        if not submit_link(driver, target_url):
            log("🔁 Retrying once...")
            time.sleep(2)
            submit_link(driver, target_url)

        log("✅ All done.")
    finally:
        driver.quit()
        log("🟢 Browser closed.")
        log("🏁 Script finished.")


if __name__ == "__main__":
    main()
