#!/usr/bin/env python3
import sys
import json
import time
import cv2
import numpy as np
import pytesseract
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def log(msg):
    """Print messages immediately for debugging."""
    print(msg, flush=True)

# 🧩 OCR logic adapted from your alexlang script
def ocr_captcha_character_by_character(driver):
    """Find CAPTCHA image(s), download and recognize each."""
    try:
        log("🔍 Locating CAPTCHA image...")
        captcha_imgs = driver.find_elements(By.CSS_SELECTOR, ".x5captcha-wrap img, .imCptImage")

        if not captcha_imgs:
            log("⚠️ No CAPTCHA images found.")
            return ""

        captcha_text = ""
        for img_elem in captcha_imgs:
            src = img_elem.get_attribute("src")
            if not src:
                continue
            resp = requests.get(src, timeout=10)
            img_arr = np.frombuffer(resp.content, dtype=np.uint8)
            img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

            char = pytesseract.image_to_string(
                thresh,
                config="--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            ).strip().upper()

            captcha_text += char

        return captcha_text[:5]
    except Exception as e:
        log(f"⚠️ OCR failed: {e}")
        return ""

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

    URL = "https://barricella.it/commenti.php?"
    name = data.get("name", "Guest Poster")
    email = data.get("email", "guestposter@example.com")
    website = data.get("website", "")
    message = data.get("message", "Fantastico sito, complimenti!")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless=new" )  # run headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        log(f"🌐 Opening {URL}")
        driver.get(URL)
        wait = WebDriverWait(driver, 20)

        wait.until(EC.presence_of_element_located((By.ID, "x5gb171-topic-form")))
        form = driver.find_element(By.ID, "x5gb171-topic-form")
        log("🧩 Guestbook form detected")

        time.sleep(2)

        # Fill form fields
        name_input = form.find_element(By.ID, "x5gb171-topic-form-name")
        email_input = form.find_element(By.ID, "x5gb171-topic-form-email")
        url_input = form.find_element(By.ID, "x5gb171-topic-form-url")
        body_input = form.find_element(By.ID, "x5gb171-topic-form-body")

        name_input.send_keys(name)
        email_input.send_keys(email)
        url_input.send_keys(website)
        body_input.send_keys(message)
        log("✍️ Form fields filled")

        # --- OCR CAPTCHA handling ---
        captcha_attempts = 0
        captcha_text = ""

        while captcha_attempts < 3 and len(captcha_text) != 5:
            captcha_attempts += 1
            log(f"🧠 OCR attempt {captcha_attempts}...")
            time.sleep(2)

            captcha_text = ocr_captcha_character_by_character(driver)
            log(f"🧩 OCR result: {captcha_text}")

            if len(captcha_text) != 5:
                log("⚠️ CAPTCHA OCR incomplete, refreshing page...")
                driver.refresh()
                wait.until(EC.presence_of_element_located((By.ID, "x5gb171-topic-form")))
                form = driver.find_element(By.ID, "x5gb171-topic-form")

                # Refill the form
                form.find_element(By.ID, "x5gb171-topic-form-name").send_keys(name)
                form.find_element(By.ID, "x5gb171-topic-form-email").send_keys(email)
                form.find_element(By.ID, "x5gb171-topic-form-url").send_keys(website)
                form.find_element(By.ID, "x5gb171-topic-form-body").send_keys(message)
                time.sleep(1)

        if len(captcha_text) != 5:
            log("❌ Failed to read CAPTCHA after 3 attempts.")
            return

        # Fill CAPTCHA input (if present)
        try:
            captcha_input = form.find_element(By.NAME, "imCpt")
            captcha_input.send_keys(captcha_text)
            log("🔑 CAPTCHA filled")
        except:
            log("⚠️ CAPTCHA input not found — skipping")

        # --- Submit form ---
        try:
            submit_btn = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='submit'][value='Invia']"))
            )
        except:
            log("⚠️ Primary CSS lookup failed, using XPath fallback...")
            submit_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='submit' or @value='Invia']"))
            )

        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(1)
        submit_btn.click()
        log("📨 Form submitted successfully!")

        time.sleep(5)

    except Exception as e:
        log(f"⚠️ Error occurred: {e}")
        try:
            html = driver.page_source
            with open("debug_form.html", "w", encoding="utf-8") as f:
                f.write(html)
            log("📄 Saved debug_form.html for inspection.")
        except Exception as dump_err:
            log(f"💥 Could not save HTML: {dump_err}")
    finally:
        driver.quit()
        log("🟢 Browser closed.")

if __name__ == "__main__":
    main()
