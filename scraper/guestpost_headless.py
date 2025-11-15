import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def log(msg):
    print(msg, flush=True)

def main():
    # Read JSON input
    raw = sys.stdin.read().strip()
    if not raw:
        log("❌ No JSON input received.")
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        log("❌ Invalid JSON format.")
        return

    # Form defaults
    URL = "http://metallbau-willeke.de/kunden.php?"
    name = data.get("name", "Guest Poster")
    email = data.get("email", "guestposter@example.com")
    website = data.get("website", "https://yourdomain.com")
    message = data.get("message", "Hallo! Ihre Website ist sehr interessant. Grüße!")

    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")  # Uncomment to run headless
    driver = webdriver.Chrome(options=chrome_options)

    try:
        log(f"🌐 Opening browser to {URL}")
        driver.get(URL)
        wait = WebDriverWait(driver, 20)

        # Wait for the X5 guestbook form
        wait.until(EC.presence_of_element_located((By.ID, "x5gb432-topic-form")))
        log("🧩 Form detected")

        # Wait a little for X5 JS initialization
        time.sleep(2)

        # Fetch fields again to avoid stale reference
        name_input = driver.find_element(By.ID, "x5gb432-topic-form-name")
        email_input = driver.find_element(By.ID, "x5gb432-topic-form-email")
        url_input = driver.find_element(By.ID, "x5gb432-topic-form-url")
        body_input = driver.find_element(By.ID, "x5gb432-topic-form-body")
        submit_btn = driver.find_element(By.ID, "x5gb432-topic-form_submit")

        # Fill the form
        name_input.send_keys(name)
        email_input.send_keys(email)
        url_input.send_keys(website)
        body_input.send_keys(message)
        log("✍️ Form fields filled")

        # Submit form via JS button
        submit_btn.click()
        log("📨 Form submitted via browser!")

        # Optional: wait to see the result page
        time.sleep(5)

    except Exception as e:
        log(f"⚠️ Error: {e}")

    finally:
        driver.quit()
        log("🟢 Browser closed")

if __name__ == "__main__":
    main()
