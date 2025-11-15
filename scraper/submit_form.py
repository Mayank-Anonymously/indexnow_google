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
    raw = sys.stdin.read().strip()
    if not raw:
        log("❌ No JSON input received.")
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        log("❌ Invalid JSON format.")
        return

    URL = "https://elektropracticum.nl/index.php?"  # Replace with real guestbook
    name = data.get("name", "Guest Poster")
    email = data.get("email", "guestposter@example.com")
    website = data.get("website", "https://yourdomain.com")
    message = data.get("message", "Hallo! Geweldig werk! Je website is erg interessant. Groeten!")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")  # Uncomment for headless mode
  
    driver = webdriver.Chrome(options=chrome_options)

    try:
        log(f"🌐 Opening browser to {URL}")
        driver.get(URL)
        wait = WebDriverWait(driver, 20)

        # Wait for the form container to appear
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "topic-form")))
        log("🧩 Form container detected")

        # Wait a bit for X5 JS to render fully
        time.sleep(2)  # small delay to let JS initialize

        # REFRESH references after JS has initialized
        name_input = driver.find_element(By.ID, "x5gb02-topic-form-name")
        email_input = driver.find_element(By.ID, "x5gb02-topic-form-email")
        url_input = driver.find_element(By.ID, "x5gb02-topic-form-url")
        body_input = driver.find_element(By.ID, "x5gb02-topic-form-body")
        submit_btn = driver.find_element(By.ID, "x5gb02-topic-form_submit")

        # Fill the form
        name_input.send_keys(name)
        email_input.send_keys(email)
        url_input.send_keys(website)
        body_input.send_keys(message)
        log("✍️ Form fields filled")

        # Submit
        submit_btn.click()
        log("📨 Form submitted successfully!")


    except Exception as e:
        log(f"⚠️ Error: {e}")

    # finally:
    #     driver.quit()
    #     log("🟢 Browser closed")

if __name__ == "__main__":
    main()
