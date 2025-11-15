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
    # Read input JSON from stdin
    raw = sys.stdin.read().strip()
    if not raw:
        log("❌ No JSON input received.")
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        log("❌ Invalid JSON format.")
        return

    URL = "https://www.creazionidiwina.com/index.php?"  # Target guestbook page
    name = data.get("name", "Guest Poster")
    email = data.get("email", "guestposter@example.com")
    website = data.get("website", "")
    message = data.get("message", "Fantastico lavoro! Saluti!")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")  # Run headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        log(f"🌐 Opening {URL}")
        driver.get(URL)
        wait = WebDriverWait(driver, 20)

        # Wait for form container
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "topic-form")))
        log("🧩 Form container detected")

        # Small delay to allow X5 JS initialization
        time.sleep(2)

        # Locate form fields (update IDs according to the HTML you provided)
        name_input = driver.find_element(By.ID, "x5gb010-topic-form-name")
        email_input = driver.find_element(By.ID, "x5gb010-topic-form-email")
        url_input = driver.find_element(By.ID, "x5gb010-topic-form-url")
        body_input = driver.find_element(By.ID, "x5gb010-topic-form-body")
        submit_btn = driver.find_element(By.ID, "x5gb010-topic-form_submit")

        # Fill the form
        name_input.send_keys(name)
        email_input.send_keys(email)
        url_input.send_keys(website)
        body_input.send_keys(message)
        log("✍️ Form fields filled")

        # Submit the form
        submit_btn.click()
        log("📨 Form submitted successfully!")

        # Wait to ensure submission goes through
        time.sleep(5)

    except Exception as e:
        log(f"⚠️ Error: {e}")

    finally:
        driver.quit()
        log("🟢 Browser closed")

if __name__ == "__main__":
    main()
