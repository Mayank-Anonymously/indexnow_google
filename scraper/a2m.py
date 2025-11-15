from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random

# =========================
# CONFIG
# =========================
URL = "https://www.a2mphotography.com/guestbook.html"

# Example entry data
NAME = f"Guest_{random.randint(1000,9999)}"
EMAIL = f"guest{random.randint(1000,9999)}@example.com"
WEBSITE = f"https://example{random.randint(1000,9999)}.com"
MESSAGE = "Hello! This is a test entry from Selenium."

# =========================
# SETUP CHROME DRIVER
# =========================
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--headless")  # optional headless mode

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get(URL)
    wait = WebDriverWait(driver, 15)

    # -------------------------
    # 1️⃣ Click the "Add entry" button
    # -------------------------
    add_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".ml-addlink"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", add_btn)
    time.sleep(0.5)
    add_btn.click()

    # -------------------------
    # 2️⃣ Wait for the modal form to appear
    # -------------------------
    form = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "form.me-form, form.ml-form"))
    )

    # -------------------------
    # 3️⃣ Fill in the form
    # -------------------------
    form.find_element(By.NAME, "name").send_keys(NAME)
    form.find_element(By.NAME, "comment").send_keys(MESSAGE)
    form.find_element(By.NAME, "email").send_keys(EMAIL)
    form.find_element(By.NAME, "website").send_keys(WEBSITE)

    # -------------------------
    # 4️⃣ Click "Save entry" or "Submit"
    # -------------------------
    save_btn = form.find_element(By.CSS_SELECTOR, ".me-save, .ml-save")
    driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
    time.sleep(0.5)
    save_btn.click()

    # -------------------------
    # 5️⃣ Wait for confirmation
    # -------------------------
    confirmation = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".me-message, .ml-message"))
    )
    print("✅ Entry submitted. Confirmation:", confirmation.text)

finally:
    time.sleep(3)  # wait a little to see results
    driver.quit()
