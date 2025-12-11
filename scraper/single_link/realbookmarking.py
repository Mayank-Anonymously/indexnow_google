import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


# ==========================================
# 🔹 CONFIG
# ==========================================
LOGIN_URL = "https://www.realbookmarking.com/login"
SUBMIT_URL = "https://www.realbookmarking.com/submit"

USERNAME = "nalybuxa@forexzig.com"
PASSWORD = "Mannuk@12"


# ==========================================
# 🔹 LOG FUNCTION
# ==========================================
def log(msg):
    print(msg, flush=True)


# ==========================================
# 🔹 READ INPUT FROM NODE BACKEND
# ==========================================
def get_input_data():
    log("📥 Reading input from backend...")

    raw = sys.stdin.read().strip()
    if not raw:
        log("⚠️ No data received — using fallback values.")
        return {"url": "https://example.com/default", "repeatCount": 1}

    try:
        data = json.loads(raw)

        # Ensure repeatCount exists
        if "repeatCount" not in data:
            data["repeatCount"] = 1

        log(f"✅ Input received: {data}")
        return data

    except json.JSONDecodeError:
        log("❌ JSON decode failed — using fallback values.")
        return {"url": "https://example.com/default", "repeatCount": 1}


# ==========================================
# 🔹 SAFE CLICK
# ==========================================
def click_safely(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(0.2)
        element.click()
    except:
        log("⚠️ Normal click failed — using JS click.")
        driver.execute_script("arguments[0].click();", element)


# ==========================================
# 🔹 LOGIN FUNCTION
# ==========================================
def login(driver):
    try:
        log("🔹 Opening login page...")
        driver.get(LOGIN_URL)
        time.sleep(2)

        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)

        login_btn = driver.find_element(
            By.CSS_SELECTOR, "input[type='submit'][value='Login']"
        )
        click_safely(driver, login_btn)

        time.sleep(2)

        if "submit" in driver.current_url:
            log("✅ Login successful.")
            return True

        log("❌ Login failed.")
        return False

    except Exception as e:
        log(f"⚠️ Login error: {e}")
        return False


# ==========================================
# 🔹 SUBMIT LINK
# ==========================================
def submit_link(driver, url):
    wait = WebDriverWait(driver, 20)

    try:
        log(f"🟢 Submitting: {url}")
        driver.get(SUBMIT_URL)

        # STEP 1 — Enter URL
        url_field = driver.find_element(By.ID, "checkUrl")
        url_field.clear()
        url_field.send_keys(url)

        check_button = driver.find_element(By.CSS_SELECTOR, "input.checkUrl")
        click_safely(driver, check_button)

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".submit2")))
        log("➡️ Step 1 completed")

        # STEP 2 — Fill article info
        driver.find_element(By.ID, "articleTitle").send_keys(url)

        # Category
        try:
            category = driver.find_element(By.ID, "category")
            for opt in category.find_elements(By.TAG_NAME, "option"):
                if "Travel" in opt.text:
                    opt.click()
                    log(f"📌 Category selected: {opt.text}")
                    break
        except:
            log("⚠️ Category dropdown not found")

        # Tags
        try:
            driver.find_element(By.ID, "tag").send_keys("travel, guide, adventure")
        except:
            log("⚠️ Tag field missing")

        # Description
        driver.find_element(By.ID, "description").send_keys(f"Read more at: {url}")

        save_btn = driver.find_element(By.CSS_SELECTOR, "input.saveChanges")
        click_safely(driver, save_btn)

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".submit3")))
        log("➡️ Step 2 completed")

        # STEP 3 — Final submit
        submit_btn = driver.find_element(By.ID, "submit")
        click_safely(driver, submit_btn)

        log("🎉 Successfully submitted!")
        return True

    except Exception as e:
        log(f"❌ Submission error: {e}")
        return False


# ==========================================
# 🔹 MAIN WORKFLOW WITH repeatCount
# ==========================================
def main():
    data = get_input_data()

    target_url = (data.get("url") or data.get("targetUrl", "")).strip()
    repeat_count = int(data.get("repeatCount", 1))

    if not target_url.startswith("http"):
        log("❌ Invalid URL input — stopping.")
        return

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,2000")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # LOGIN ONCE
        if not login(driver):
            log("❌ Cannot continue without login.")
            return

        # REPEAT SUBMISSION
        for i in range(repeat_count):
            log(f"\n🔁 Repeat {i + 1}/{repeat_count}")
            submit_link(driver, target_url)
            time.sleep(2)

    finally:
        log("🟢 Closing browser.")
        driver.quit()


# ==========================================
# 🔹 ENTRY POINT
# ==========================================
if __name__ == "__main__":
    main()
