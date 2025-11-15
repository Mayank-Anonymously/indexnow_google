 #!/usr/bin/env python3
"""
Florida2005 Guestbook Auto-Filler

Usage:
    echo '{"name":"John Doe","email":"john@example.com","website":"https://example.com","message":"Hello from Selenium!"}' | python3 florida_guestbook.py

Dependencies:
    pip install selenium webdriver-manager
"""

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


# --------------------------------------------------
# Utility Logging
# --------------------------------------------------
def log(msg):
    print(msg, flush=True)


# --------------------------------------------------
# Main Automation
# --------------------------------------------------
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

    URL = "https://www.florida2005.de/main/newentry.php"
    name = data.get("name", "Guest User")
    email = data.get("email", "guest@example.com")
    website = data.get("website", "")
    message = data.get("message", "Hallo, schöne Webseite!")

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # Uncomment to run headless:
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        log(f"🌐 Opening {URL}")
        driver.get(URL)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.NAME, "creator")))

        log("🧩 Filling out guestbook form...")

        # Fill fields
        driver.find_element(By.NAME, "creator").send_keys(name)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "homepage").send_keys(website)
        driver.find_element(By.NAME, "entry").send_keys(message)

        log("✍️ Message entered successfully.")

        # Submit form
        driver.find_element(By.NAME, "enter").click()
        log("📨 Form submitted!")

        # Wait a bit for response page
        time.sleep(4)
        log("✅ Done! Check the guestbook for your entry.")

    except Exception as e:
        log(f"⚠️ Error: {e}")
    finally:
        driver.quit()
        log("🟢 Browser closed.")


# --------------------------------------------------
if __name__ == "__main__":
    main()
