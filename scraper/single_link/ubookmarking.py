import sys
import json
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager


LOGIN_URL = "https://www.ubookmarking.com/login/re-submit"
SUBMIT_URL = "https://www.ubookmarking.com/submit"

USERNAME = "nalybuxa@forexzig.com"
PASSWORD = "Mannuk@12"


# ====================================================
def log(msg):
    print(msg, flush=True)
# ====================================================


def get_input_data():
    raw = sys.stdin.read().strip()
    if not raw:
        return {"url": "https://example.com/fallback"}
    try:
        return json.loads(raw)
    except:
        return {"url": "https://example.com/fallback"}


# ====================================================
# SAFE CLICK (scroll + JS fallback)
# ====================================================
def click_safely(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(0.3)
        element.click()
    except:
        log("⚠️ Normal click failed → using JS click")
        driver.execute_script("arguments[0].click();", element)


# ====================================================
# LOGIN
# ====================================================
def login(driver):
    try:
        log("🔹 Opening login page...")
        driver.get(LOGIN_URL)

        wait = WebDriverWait(driver, 20)

        wait.until(EC.visibility_of_element_located((By.ID, "username")))

        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)

        login_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']")
        click_safely(driver, login_btn)

        # Wait for redirect to dashboard / submit
        try:
            wait.until(EC.url_contains("submit"))
        except TimeoutException:
            pass

        if "submit" in driver.current_url:
            log("✅ Login successful.")
            return True

        log("❌ Login failed – still on login page.")
        return False

    except Exception as e:
        log(f"⚠️ Login error: {e}")
        return False


# ====================================================
# SUBMISSION
# ====================================================
def submit_link(driver, url):
    wait = WebDriverWait(driver, 25)

    try:
        log(f"🟢 Starting submission for: {url}")
        driver.get(SUBMIT_URL)

        # ------------- STEP 1 ----------------
        wait.until(EC.visibility_of_element_located((By.ID, "checkUrl")))

        url_field = driver.find_element(By.ID, "checkUrl")
        url_field.clear()
        url_field.send_keys(url)

        check_button = driver.find_element(By.CSS_SELECTOR, "input.checkUrl")
        click_safely(driver, check_button)

        # Wait until story form loads
        wait.until(EC.visibility_of_element_located((By.ID, "articleTitle")))
        log("➡️ Step 2 loaded.")

        # ------------- STEP 2 ----------------
        driver.find_element(By.ID, "articleTitle").send_keys(url)

        # Category dropdown
        try:
            category = driver.find_element(By.ID, "category")
            for opt in category.find_elements(By.TAG_NAME, "option"):
                if "Travel" in opt.text:
                    opt.click()
                    log(f"📌 Category chosen: {opt.text}")
                    break
        except:
            log("⚠️ Could not select category")

        # Tags
        try:
            driver.find_element(By.ID, "tag").send_keys("travel, adventure, guide")
        except:
            log("⚠️ Tag field missing")

        # Description
        driver.find_element(By.ID, "description").send_keys(f"Read more: {url}")

        save_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.saveChanges")))
        click_safely(driver, save_btn)

        # Wait for final submit page
        wait.until(EC.visibility_of_element_located((By.ID, "submit")))
        log("➡️ Final step loaded.")

        # ------------- STEP 3 ----------------
        final_submit = driver.find_element(By.ID, "submit")
        click_safely(driver, final_submit)

        time.sleep(2)

        log(f"🎉 SUCCESSFULLY SUBMITTED: {url}")
        return True

    except Exception as e:
        log(f"❌ Submission error: {e}")
        return False


# ====================================================
# MAIN
# ====================================================
def main():
    data = get_input_data()
    url = data.get("url", "")

    if not url.startswith("http"):
        log("❌ Invalid URL")
        return

    log(f"📎 Target URL: {url}")

    random_port = random.randint(9200, 9500)
    profile_path = f"/tmp/chrome_profile_{os.getpid()}_{random_port}"

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # safer
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,2400")
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    # Remove Selenium fingerprint
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""
    })

    try:
        if login(driver):
            if not submit_link(driver, url):
                log("🔁 Retrying...")
                time.sleep(2)
                submit_link(driver, url)
        else:
            log("❌ Login failed, stopping.")
    finally:
        driver.quit()
        log("🟢 Browser closed.")
        log("🏁 Script completed.")


if __name__ == "__main__":
    main()
