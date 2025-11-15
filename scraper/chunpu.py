import sys
import json
import time
import cv2
import numpy as np
import pytesseract
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def log(msg):
    print(msg, flush=True)

def solve_captcha(img_url, driver):
    # Get full src (handle relative URLs)
    if not img_url.startswith("http"):
        base = driver.current_url.rsplit("/", 1)[0]
        img_url = f"{base}/{img_url}"

    # Download image
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content)).convert("L")  # grayscale

    # Convert to numpy for OpenCV
    img_np = np.array(img)
    # Apply thresholding to improve OCR
    _, img_thresh = cv2.threshold(img_np, 150, 255, cv2.THRESH_BINARY_INV)
    
    # OCR using pytesseract
    captcha_text = pytesseract.image_to_string(img_thresh, config='--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
    captcha_text = captcha_text.strip()
    log(f"🖼️ CAPTCHA detected: {captcha_text}")
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

    URL = "https://chunpu.tw/EN/share.php"  # Replace with actual page URL
    name = data.get("name", "Guest")
    message = data.get("message", "Hello! Nice website!")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        log(f"🌐 Opening {URL}")
        driver.get(URL)
        wait = WebDriverWait(driver, 20)

        # Wait for form to appear
        wait.until(EC.presence_of_element_located((By.ID, "form1")))
        log("🧩 Form detected")

        # Fill name and message
        driver.find_element(By.ID, "guest").send_keys(name)
        driver.find_element(By.NAME, "message").send_keys(message)
        log("✍️ Name and message filled")

        # Solve CAPTCHA
        captcha_img = driver.find_element(By.ID, "siimage").get_attribute("src")
        captcha_text = solve_captcha(captcha_img, driver)
        driver.find_element(By.NAME, "captcha_code").send_keys(captcha_text)

        # Submit form
        driver.find_element(By.ID, "button").click()
        log("📨 Form submitted!")

        # Wait to see result
        time.sleep(5)

    except Exception as e:
        log(f"⚠️ Error: {e}")

    finally:
        driver.quit()
        log("🟢 Browser closed")

if __name__ == "__main__":
    main()
