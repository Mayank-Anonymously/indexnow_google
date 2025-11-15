import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def log(msg):
    print(msg, flush=True)

def main():
    # Read JSON input from stdin
    raw = sys.stdin.read().strip()
    if not raw:
        log("❌ No JSON input received.")
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        log("❌ Invalid JSON format.")
        return

    # Form data
    URL = "https://jmc-hypnotherapie.ch/blog/index.php?id=8j5jje3j&"
    name = data.get("name", "Guest Poster")
    email = data.get("email", "guestposter@example.com")
    website = data.get("website", "")
    message = data.get("message", "Bonjour! Super contenu sur votre site!")

    # Chrome options
    chrome_options = Options()
    # Run non-headless for stability with X5 JS
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome_temp")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        log(f"🌐 Opening {URL}")
        driver.get(URL)
        wait = WebDriverWait(driver, 20)

        # Wait for the form container to appear
        wait.until(EC.presence_of_element_located((By.ID, "x5_pc8j5jje3j-topic-form")))
        log("🧩 Form container detected")

        # Allow X5 JS to initialize
        time.sleep(2)

        # Fill form fields individually
        name_input = wait.until(EC.presence_of_element_located((By.ID, "x5_pc8j5jje3j-topic-form-name")))
        email_input = wait.until(EC.presence_of_element_located((By.ID, "x5_pc8j5jje3j-topic-form-email")))
        url_input = wait.until(EC.presence_of_element_located((By.ID, "x5_pc8j5jje3j-topic-form-url")))
        body_input = wait.until(EC.presence_of_element_located((By.ID, "x5_pc8j5jje3j-topic-form-body")))

        name_input.send_keys(name)
        email_input.send_keys(email)
        url_input.send_keys(website)
        body_input.send_keys(message)
        log("✍️ Form fields filled")

        # Locate submit button and click via JS
        submit_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#x5_pc8j5jje3j-topic-form input[type='submit']"))
        )
        driver.execute_script("arguments[0].click();", submit_btn)
        log("📨 Form submitted successfully!")

        # Wait to observe result
        time.sleep(5)

    except Exception as e:
        log(f"⚠️ Error: {e}")

    finally:
        driver.quit()
        log("🟢 Browser closed")

if __name__ == "__main__":
    main()
