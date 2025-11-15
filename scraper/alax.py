import sys
import json
import time
import cv2
import numpy as np
import pytesseract
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def log(msg):
    """Print messages immediately."""
    print(msg, flush=True)

def ocr_captcha_character_by_character(driver):
    """Download each CAPTCHA GIF from iframe and OCR individually."""
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe.captcha-container")
    driver.switch_to.frame(iframe)

    captcha_imgs = driver.find_elements(By.TAG_NAME, "img")
    captcha_text = ""

    for img_elem in captcha_imgs:
        src = img_elem.get_attribute("src")
        resp = requests.get(src)
        img_arr = np.frombuffer(resp.content, dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

        # Threshold per character (keep colors for better OCR if needed)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        char = pytesseract.image_to_string(
            thresh, config="--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        ).strip().upper()

        if char:
            captcha_text += char

    driver.switch_to.default_content()
    return captcha_text

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

    URL = "https://www.alexlang.ch/gaestebuch.php"  # Updated URL
    name = data.get("name", "Guest Poster")
    email = data.get("email", "guestposter@example.com")
    website = data.get("website", "https://example.com")
    message = data.get("message", "Hallo! Tolle Webseite – sehr interessant!")

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Uncomment to run headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        log(f"🌐 Opening {URL}")
        driver.get(URL)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "x5gb91-topic-form-name")))
        log("🧩 Form detected")

        # Fill form fields
        driver.find_element(By.ID, "x5gb91-topic-form-name").send_keys(name)
        driver.find_element(By.ID, "x5gb91-topic-form-email").send_keys(email)
        driver.find_element(By.ID, "x5gb91-topic-form-url").send_keys(website)
        driver.find_element(By.ID, "x5gb91-topic-form-body").send_keys(message)
        log("✍️ Form fields filled")

        # CAPTCHA handling loop
        captcha_attempts = 0
        captcha_text = ""

        while captcha_attempts < 3 and len(captcha_text) != 5:
            captcha_attempts += 1
            log(f"🔍 CAPTCHA attempt {captcha_attempts}")
            time.sleep(2)

            captcha_text = ocr_captcha_character_by_character(driver)
            log(f"🧠 OCR result: {captcha_text}")

            if len(captcha_text) != 5:
                log("⚠️ OCR failed, retrying...")
                driver.refresh()
                wait.until(EC.presence_of_element_located((By.ID, "x5gb91-topic-form-name")))
                driver.find_element(By.ID, "x5gb91-topic-form-name").send_keys(name)
                driver.find_element(By.ID, "x5gb91-topic-form-email").send_keys(email)
                driver.find_element(By.ID, "x5gb91-topic-form-url").send_keys(website)
                driver.find_element(By.ID, "x5gb91-topic-form-body").send_keys(message)
                time.sleep(2)

        if len(captcha_text) != 5:
            log("❌ Failed to read CAPTCHA after 3 attempts.")
            return

        # Submit form
        driver.find_element(By.NAME, "imCpt").send_keys(captcha_text)
        driver.find_element(By.ID, "x5gb91-topic-form_submit").click()
        log("📨 Form submitted!")
        time.sleep(5)
        log("✅ Done! Check website for confirmation.")

    except Exception as e:
        log(f"⚠️ Error: {e}")
    finally:
        driver.quit()
        log("🟢 Browser closed.")

if __name__ == "__main__":
    main()
