import sys
import json
import time
import cv2
import numpy as np
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
def log(msg):
    """Print messages immediately."""
    print(msg, flush=True)

def download_and_combine_captcha(driver):
    """Download all CAPTCHA GIFs from iframe and combine horizontally."""
    # Switch to CAPTCHA iframe
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe.captcha-container")
    driver.switch_to.frame(iframe)

    captcha_imgs = driver.find_elements(By.TAG_NAME, "img")
    images = []

    for img_elem in captcha_imgs:
        src = img_elem.get_attribute("src")
        # Download using requests
        resp = requests.get(src)
        img_arr = np.frombuffer(resp.content, dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        images.append(img)

    # Combine horizontally
    captcha_full = np.hstack(images)
    cv2.imwrite("captcha_combined.png", captcha_full)

    # Switch back to main content
    driver.switch_to.default_content()
    return captcha_full
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

    URL = "https://www.zingerle-skulpturen.at/gaestebuch.php"
    name = data.get("name", "Guest Poster")
    email = data.get("email", "guestposter@example.com")
    website = data.get("website", "https://example.com")
    message = data.get("message", "Hallo! Tolle Webseite – sehr interessant!")

    # Setup Chrome
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Uncomment to run headless
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

        # Fill form
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
            time.sleep(2)  # Let CAPTCHA load

            # Download and combine CAPTCHA
            captcha_image = download_and_combine_captcha(driver)

            # OCR
            captcha_text = pytesseract.image_to_string(captcha_image, config="--psm 7")
            captcha_text = "".join(ch for ch in captcha_text.strip() if ch.isalnum()).upper()
            log(f"🧠 OCR result: {captcha_text}")

            if len(captcha_text) != 5:
                log("⚠️ OCR failed, retrying...")
                driver.refresh()
                wait.until(EC.presence_of_element_located((By.ID, "x5gb91-topic-form-name")))
                # Refill form
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
