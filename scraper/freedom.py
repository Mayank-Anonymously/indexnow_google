#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#   echo '{"name":"Alice","email":"alice@example.com","website":"https://example.com","message":"Great photos!"}' \
#     | python3 submit_guestbook.py
#
# Keeps your original logging style, targets the live guestbook form and sets the rating to full (100%).

import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

def log(msg):
    print(msg, flush=True)

def set_full_rating(driver):
    """
    Tries multiple strategies to set the visual star rating to full:
    1) Set width of the 'topic-star-fixer-big' element to 100%
    2) If there's a hidden input named 'rating' (or similar), set it to '5'
    3) As a fallback, click near the end of the star container to simulate a 5-star click
    """
    try:
        # Strategy A: set the fixer width to 100%
        fixer = driver.find_element(By.CLASS_NAME, "topic-star-fixer-big")
        driver.execute_script("arguments[0].style.width='100%';", fixer)
        log("⭐ Rating: set visual width to 100% (strategy A)")
    except Exception as e:
        log(f"⚠️ Rating strategy A failed: {e}")

    # Strategy B: set hidden input if present
    possible_names = ["rating", "vote", "score"]
    for name in possible_names:
        try:
            rating_input = driver.find_element(By.NAME, name)
            driver.execute_script("arguments[0].value='5';", rating_input)
            # Fire change event if necessary
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", rating_input)
            log(f"⭐ Rating: set hidden input '{name}' = 5 (strategy B)")
            return
        except NoSuchElementException:
            continue
        except Exception as e:
            log(f"⚠️ Rating strategy B for '{name}' error: {e}")

    # Strategy C: click near the right edge of the star container
    try:
        container = driver.find_element(By.CLASS_NAME, "variable-star-rating")
        driver.execute_script("""
            var el = arguments[0];
            var rect = el.getBoundingClientRect();
            var x = rect.left + rect.width * 0.98;
            var y = rect.top + rect.height / 2;
            var ev = document.createEvent('MouseEvents');
            ev.initMouseEvent('click', true, true, window, 1,
                x, y, x, y, false, false, false, false, 0, null);
            el.dispatchEvent(ev);
        """, container)
        log("⭐ Rating: clicked near right edge of star container (strategy C)")
    except Exception as e:
        log(f"⚠️ Rating strategy C failed: {e}")

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

    # ---------- Configuration ----------
    URL = "http://www.freedom-photography.ch/blog/index.php?id=la49v4g1&"
    name = data.get("name", "Guest Poster")
    email = data.get("email", "guestposter@example.com")
    website = data.get("website", "https://yourdomain.com")
    message = data.get("message", "Hallo! Geweldig werk! Je website is erg interessant. Groeten!")
    headless = False   # set False to see the browser in action
    timeout_seconds = 20
    # -----------------------------------

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    if headless:
        chrome_options.add_argument("--headless=new")  # use new headless if available

    # Optionally disable GPU, sandbox if needed (uncomment if required)
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")

    try:
        driver = webdriver.Chrome(options=chrome_options)
    except WebDriverException as e:
        log(f"❌ Could not start Chrome WebDriver: {e}")
        return

    try:
        log(f"🌐 Opening browser to {URL}")
        driver.get(URL)
        wait = WebDriverWait(driver, timeout_seconds)

        # Wait for the form element (by ID)
        try:
            wait.until(EC.presence_of_element_located((By.ID, "x5_pcla49v4g1-topic-form")))
            log("🧩 Form detected")
        except TimeoutException:
            # fallback: wait for any input that appears to belong to the form
            log("⚠️ Timeout waiting for form ID; trying to detect by form inputs...")
            wait.until(EC.presence_of_element_located((By.ID, "x5_pcla49v4g1-topic-form-name")))
            log("🧩 Form inputs detected (fallback)")

        # small delay to allow JS widgets to fully initialize
        time.sleep(1.5)

        # locate inputs (updated IDs from your HTML)
        name_input = driver.find_element(By.ID, "x5_pcla49v4g1-topic-form-name")
        email_input = driver.find_element(By.ID, "x5_pcla49v4g1-topic-form-email")
        url_input = driver.find_element(By.ID, "x5_pcla49v4g1-topic-form-url")
        body_input = driver.find_element(By.ID, "x5_pcla49v4g1-topic-form-body")
        submit_btn = driver.find_element(By.ID, "x5_pcla49v4g1-topic-form_submit")

        # Fill the form fields
        name_input.clear(); name_input.send_keys(name)
        email_input.clear(); email_input.send_keys(email)
        url_input.clear(); url_input.send_keys(website)
        body_input.clear(); body_input.send_keys(message)
        log("✍️ Form fields filled")

        # Set rating to full using helper
        set_full_rating(driver)

        # Submit the form
        try:
            # The submit button in HTML is input type="button" so click triggers the JS handler
            submit_btn.click()
            log("📨 Submit button clicked")
        except Exception as e:
            log(f"⚠️ Could not click submit button directly: {e}")
            # Try JS submit of the form as a last resort (may bypass JS validators)
            try:
                form_el = driver.find_element(By.ID, "x5_pcla49v4g1-topic-form")
                driver.execute_script("arguments[0].submit();", form_el)
                log("📨 Form submitted via form.submit() (fallback)")
            except Exception as e2:
                log(f"❌ Fallback submit also failed: {e2}")
                raise

        # Wait briefly for any success message or page change
        time.sleep(2)
        log("✅ Done - form submission attempted.")

    except Exception as e:
        log(f"⚠️ Error: {e}")

    # finally:
    #     try:
    #         driver.quit()
    #     except Exception:
    #         pass
    #     log("🟢 Browser closed")

if __name__ == "__main__":
    main()
