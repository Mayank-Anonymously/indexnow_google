#!/usr/bin/env python3
"""
PeopleFirst Hamburg Guestbook Auto-Filler + Local OCR (no external API)

Usage:
    echo '{"name":"John Doe","email":"john@example.com","website":"https://example.com","message":"Hello world!"}' | python3 peoplefirst_localocr.py

Dependencies:
    pip install selenium webdriver-manager pytesseract pillow numpy opencv-python
    # Make sure Tesseract OCR is installed on your system:
    # Ubuntu/Debian: sudo apt install tesseract-ocr
    # macOS (brew):  brew install tesseract
"""

import sys
import json
import os
import time
import tempfile
import requests
import numpy as np
import cv2
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def log(msg):
    print(msg, flush=True)


# --------------------------------------------------
# Download CAPTCHA directly from <img id="captcha">
# --------------------------------------------------
def download_captcha(driver):
    img_elem = driver.find_element(By.ID, "captcha")
    src = img_elem.get_attribute("src")

    resp = requests.get(src, timeout=15)
    resp.raise_for_status()
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".png")
    os.close(tmp_fd)
    with open(tmp_path, "wb") as f:
        f.write(resp.content)
    log(f"📸 CAPTCHA saved to: {tmp_path}")
    return tmp_path


# --------------------------------------------------
# Local OCR via OpenCV + Tesseract
# --------------------------------------------------
def extract_text_from_image(image_path):
    """Enhanced preprocessing for curved or cursive CAPTCHA"""
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Increase contrast a little
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)

    # Remove background noise (denoise but keep edges)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # Binarize (adaptive threshold handles gradients/curves)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 31, 15
    )

    # Morphological opening to clean specks
    kernel = np.ones((2, 2), np.uint8)
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Invert back to black text on white
    clean = cv2.bitwise_not(clean)

    # Optional resize for OCR clarity
    scale_factor = 3
    clean = cv2.resize(clean, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

    # OCR configuration — single word, whitelist
    config = "--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    text = pytesseract.image_to_string(clean, config=config)

    cleaned = "".join(ch for ch in text.strip() if ch.isalnum())
    return cleaned


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

    URL = "http://www.peoplefirst-hamburg.de/index.php/guestbook/index/newentry"
    name = data.get("name", "Guest User")
    email = data.get("email", "guest@example.com")
    website = data.get("website", "")
    message = data.get("message", "Hallo, tolle Webseite!")

    # Chrome setup
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--headless=new")  # uncomment for headless mode

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        log(f"🌐 Opening {URL}")
        driver.get(URL)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.NAME, "name")))

        # Fill basic fields
        driver.find_element(By.NAME, "name").send_keys(name)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "homepage").send_keys(website)

        # Enter message in CKEditor iframe
        log("🧠 Typing message inside CKEditor iframe...")
        iframe = driver.find_element(By.CSS_SELECTOR, "iframe.cke_wysiwyg_frame")
        driver.switch_to.frame(iframe)
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()
        body.send_keys(message)
        driver.switch_to.default_content()
        log("✍️ Message entered successfully.")

        # Solve CAPTCHA locally
        attempts, captcha_text = 0, ""
        while attempts < 3 and len(captcha_text) < 3:
            attempts += 1
            log(f"🔍 Solving CAPTCHA (attempt {attempts})")
            captcha_path = download_captcha(driver)
            captcha_text = extract_text_from_image(captcha_path)
            log(f"🧠 OCR result: '{captcha_text}'")

            if len(captcha_text) < 3:
                log("⚠️ OCR unclear, refreshing CAPTCHA...")
                try:
                    driver.find_element(By.ID, "change-image").click()
                    time.sleep(2)
                except Exception:
                    pass

        if len(captcha_text) < 3:
            log("❌ Failed to read CAPTCHA after 3 tries.")
            return

        # Fill CAPTCHA and submit
        driver.find_element(By.NAME, "captcha").send_keys(captcha_text)
        driver.find_element(By.NAME, "saveGuestbook").click()
        log("📨 Form submitted!")

        time.sleep(5)
        log("✅ Done! Check the site for your entry.")

    except Exception as e:
        log(f"⚠️ Error: {e}")
    finally:
        driver.quit()
        log("🟢 Browser closed.")


if __name__ == "__main__":
    main()
