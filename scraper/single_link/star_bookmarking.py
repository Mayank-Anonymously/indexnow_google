import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


LOGIN_URL = "https://www.starbookmarking.com/login/re-submit"
SUBMIT_URL = "https://www.starbookmarking.com/submit"
USERNAME = "nalybuxa@forexzig.com"
PASSWORD = "Mannuk@12"


def log(msg):
    print(msg, flush=True)


# =========================================================
# Read Input (with repeatCount)
# =========================================================
def get_input_data():
    log("📥 Waiting for data from frontend...")

    raw = sys.stdin.read().strip()
    if not raw:
        log("⚠️ No input received — using fallback values.")
        return {"url": "https://example.com", "repeatCount": 1}

    try:
        data = json.loads(raw)

        # Ensure repeatCount exists
        if "repeatCount" not in data:
            data["repeatCount"] = 1

        log(f"✅ Received input: {data}")
        return data

    except json.JSONDecodeError:
        log("❌ Invalid JSON — using fallback values.")
        return {"url": "https://example.com", "repeatCount": 1}


# =========================================================
# Safe Click
# =========================================================
def click_safely(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.25)
        element.click()
    except:
        log("⚠️ Normal click failed — using JS click.")
        driver.execute_script("arguments[0].click();", element)


# =========================================================
# Login
# =========================================================
def login(driver):
    try:
        log("🔹 Opening login page...")
        driver.get(LOGIN_URL)
        time.sleep(2)

        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)

        btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']")
        click_safely(driver, btn)

        time.sleep(2)

        if "submit" in driver.current_url:
            log("✅ Login successful.")
            return True

        log("❌ Login failed.")
        return False

    except Exception as e:
        log(f"⚠️ Login error: {e}")
        return False


# =========================================================
# Submit Link
# =========================================================
def submit_link(driver, url):
    wait = WebDriverWait(driver, 20)

    try:
        log(f"\n🟢 Starting submission for: {url}")
        driver.get(SUBMIT_URL)
        time.sleep(1.5)

        # === Step 1: Enter URL ===
        url_field = driver.find_element(By.ID, "checkUrl")
        url_field.clear()
        url_field.send_keys(url)

        check_btn = driver.find_element(By.CSS_SELECTOR, "input.checkUrl")
        click_safely(driver, check_btn)

        # Wait for submit2
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".submit2")))
        log("➡️ Submit2 loaded.")

        # === Step 2: Fill Article Info ===
        driver.find_element(By.ID, "articleTitle").send_keys(url)

        # Category
        try:
            category = driver.find_element(By.ID, "category")
            found = False
            for opt in category.find_elements(By.TAG_NAME, "option"):
                if "Travel" in opt.text:
                    opt.click()
                    log(f"📌 Selected category: {opt.text}")
                    found = True
                    break
            if not found:
                log("⚠️ Travel category not found — using default category.")
        except:
            log("⚠️ Category element missing!")

        # Tags
        try:
            driver.find_element(By.ID, "tag").send_keys("travel, adventure, guide")
        except:
            log("⚠️ Tag field missing — skipped.")

        # Description
        driver.find_element(By.ID, "description").send_keys(f"Read more: {url}")

        save = driver.find_element(By.CSS_SELECTOR, "input.saveChanges")
        click_safely(driver, save)

        # Wait for submit3
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".submit3")))
        log("➡️ Submit3 loaded.")

        # === Step 3: Final Submit ===
        final_btn = driver.find_element(By.ID, "submit")
        click_safely(driver, final_btn)

        time.sleep(2)
        log("🎉 SUCCESS — Link submitted!")
        return True

    except Exception as e:
        log(f"❌ Submission error: {e}")
        return False


# =========================================================
# Main
# =========================================================
def main():
    log("🚀 Starting StarBookmarking automation...")

    data = get_input_data()

    url = data.get("url", "").strip()
    repeatCount = int(data.get("repeatCount", 1))

    if not url.startswith("http"):
        log("❌ Invalid URL input — stopping.")
        return

    log(f"📎 Target URL: {url}")
    log(f"🔁 Repeat count: {repeatCount}")

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--window-size=1400,2000")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        if not login(driver):
            log("❌ Login failed — exiting.")
            return

        # Loop repeatCount
        for i in range(repeatCount):
            log(f"\n🔁 Submission {i + 1}/{repeatCount}")
            submit_link(driver, url)
            time.sleep(2)

    finally:
        driver.quit()
        log("🟢 Browser closed.")
        log("🏁 Script finished.")


if __name__ == "__main__":
    main()
