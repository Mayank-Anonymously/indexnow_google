#!/usr/bin/env python3
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def log(msg):
    print(msg, flush=True)

def main():
    # Read input JSON
    raw = sys.stdin.read().strip()
    if not raw:
        log("❌ No JSON input received.")
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        log("❌ Invalid JSON format.")
        return

    # Page target
    URL = "https://www.klepalov.ru/blotter/apage-268.html"
    name = data.get("name", "Гость")  # Default: Guest
    email = data.get("email", "guest@example.com")
    website = data.get("website", "https://example.com")
    message = data.get("message", "Отличный сайт! Большое спасибо за контент.")

    # Configure Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless=new")  # Uncomment for headless mode

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        log(f"🌐 Opening {URL}")
        driver.get(URL)

        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.NAME, "form-blotter[17]")))
        log("🧩 Form detected")

        # Fill in the form
        driver.find_element(By.NAME, "form-blotter[17]").send_keys(name)
        driver.find_element(By.NAME, "form-blotter[12]").send_keys(email)
        website_field = driver.find_element(By.NAME, "form-blotter[18]")
        website_field.clear()
        website_field.send_keys(website)
        driver.find_element(By.NAME, "form-blotter[19]").send_keys(message)
        log("✍️ Fields filled successfully")

        # Submit
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Сохранить']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(1)
        submit_btn.click()
        log("📨 Form submitted!")

        # Wait a bit for confirmation
        time.sleep(5)
        log("✅ Done! Check the website for your message.")

    except Exception as e:
        log(f"⚠️ Error: {e}")
        try:
            with open("debug_klepalov.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            log("📄 Saved current page HTML for debugging.")
        except Exception as dump_err:
            log(f"💥 Could not save HTML: {dump_err}")
    finally:
        driver.quit()
        log("🟢 Browser closed.")

if __name__ == "__main__":
    main()
