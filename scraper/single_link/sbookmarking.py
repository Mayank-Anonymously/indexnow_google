import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
    TimeoutException,
)
from webdriver_manager.chrome import ChromeDriverManager


LOGIN_URL = "https://www.ubookmarking.com/login/re-submit"
SUBMIT_URL = "https://www.ubookmarking.com/submit"
USERNAME = "nalybuxa@forexzig.com"
PASSWORD = "Mannuk@12"


def log(msg):
    print(msg, flush=True)


def get_input_data():
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
        log("❌ Invalid JSON. Using fallback.")
        return {"url": "https://example.com/default"}


# -------------------------------
# SAFE CLICK (scroll + JS fallback)
# -------------------------------
def click_safely(driver, el):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.2)
        el.click()
    except:
        log("⚠️ Normal click failed → using JS click.")
        driver.execute_script("arguments[0].click();", el)


# -------------------------------
# LOGIN
# -------------------------------
def login(driver):
    log("🔹 Opening login page...")
    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 20)

        wait.until(EC.visibility_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)

        login_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']")
        click_safely(driver, login_btn)

        # Wait for page redirect
        try:
            WebDriverWait(driver, 10).until(EC.url_contains("submit"))
        except TimeoutException:
            pass

        if "submit" in driver.current_url.lower():
            log("✅ Login successful.")
            return True

        log(f"❌ Login failed. URL: {driver.current_url}")
        return False

    except Exception as e:
        log(f"⚠️ Login error: {e}")
        return False


# -------------------------------
# SUBMISSION
# -------------------------------
def submit_link(driver, url):
    log(f"\n🟢 Submitting: {url}")
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(SUBMIT_URL)

        # STEP 1 — URL FIELD
        wait.until(EC.visibility_of_element_located((By.ID, "checkUrl")))
        url_field = driver.find_element(By.ID, "checkUrl")
        url_field.clear()
        url_field.send_keys(url)

        check_btn = driver.find_element(By.CSS_SELECTOR, "input.checkUrl")
        click_safely(driver, check_btn)

        # Wait until step 2 loads
        wait.until(EC.visibility_of_element_located((By.ID, "articleTitle")))
        log("➡️ Step 2 loaded.")

        # STEP 2 — ARTICLE
        driver.find_element(By.ID, "articleTitle").send_keys(url)

        # Category
        try:
            cat = driver.find_element(By.ID, "category")
            for opt in cat.find_elements(By.TAG_NAME, "option"):
                if "Travel" in opt.text:
                    opt.click()
                    break
        except:
            log("⚠️ Category not found")

        # Tags
        try:
            driver.find_element(By.ID, "tag").send_keys("travel, adventure, guide")
        except:
            log("⚠️ Tag field missing")

        # Description
        try:
            driver.find_element(By.ID, "description").send_keys(f"More info: {url}")
        except:
            log("⚠️ Description missing")

        # Save
        save_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.saveChanges")))
        click_safely(driver, save_btn)

        # STEP 3 — FINAL SUBMIT  
        wait.until(EC.visibility_of_element_located((By.ID, "submit")))
        final_btn = driver.find_element(By.ID, "submit")
        click_safely(driver, final_btn)

        log("🎉 Successfully submitted!")
        return True

    except Exception as e:
        log(f"❌ Submission error: {e}")
        return False


# -------------------------------
# MAIN
# -------------------------------
def main():
    data = get_input_data()
    url = data.get("url", "")

    if not url.startswith("http"):
        log("❌ Invalid URL.")
        return

    log(f"📎 URL: {url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,2200")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # REMOVE webdriver FLAG (anti-detection)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    })

    try:
        if login(driver):
            if not submit_link(driver, url):
                log("🔁 Retrying in 2s...")
                time.sleep(2)
                submit_link(driver, url)
    finally:
        driver.quit()
        log("🟢 Browser closed.")
        log("🏁 Done")


if __name__ == "__main__":
    main()
