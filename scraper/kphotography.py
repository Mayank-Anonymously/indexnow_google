import sys
import json
import time
import signal
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

def log(msg):
    print(msg, flush=True)

def safe_quit(driver):
    """Ensures ChromeDriver and Chrome processes are killed cleanly."""
    try:
        driver.quit()
        log("✅ driver.quit() executed.")
    except Exception as e:
        log(f"⚠️ driver.quit() failed: {e}")
    finally:
        # Kill any stray Chrome or chromedriver processes
        for proc in psutil.process_iter(["name"]):
            if "chromedriver" in proc.info["name"] or "chrome" in proc.info["name"]:
                try:
                    proc.send_signal(signal.SIGKILL)
                except Exception:
                    pass
        log("🧹 Cleaned up leftover Chrome/Driver processes.")

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

    # Input data from frontend
    url = data.get("url", "").strip() or "https://keithisaacphotography.zenfolio.com/guestbook.html"
    name = data.get("name", "Guest User")
    email = data.get("email", "guest@example.com")
    website = data.get("website", "https://yourwebsite.com")
    message = data.get("message", "Hello! Great website!")

    # Browser setup
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-popup-blocking")
    # chrome_options.add_argument("--headless=new")  # uncomment for silent run

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 25)

        log(f"🌐 Opening {url}")
        driver.get(url)

        # Try clicking "Add entry" if it exists
        try:
            add_entry_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.ml-addlink")))
            add_entry_button.click()
            log("➕ Clicked 'Add entry' button.")
        except Exception:
            log("ℹ️ 'Add entry' button not found or already open.")

        # Wait for the form
        wait.until(EC.presence_of_element_located((By.ID, "_aaba-form")))
        log("🧩 Form is visible.")

        # Public entry radio
        try:
            public_radio = driver.find_element(By.CSS_SELECTOR, "#_aaba-access-public input[type='radio']")
            driver.execute_script("arguments[0].click();", public_radio)
            log("🔘 Selected 'Public entry' radio.")
        except Exception:
            log("⚠️ Public entry already selected or missing.")

        # Fill the fields
        driver.find_element(By.ID, "_aaba-name").send_keys(name)
        driver.find_element(By.ID, "_aaba-body").send_keys(message)

        try:
            driver.find_element(By.ID, "_aaba-email").send_keys(email)
        except:
            log("⚠️ Email field not found (optional).")

        try:
            driver.find_element(By.ID, "_aaba-url").send_keys(website)
        except:
            log("⚠️ Website field not found (optional).")

        log("✍️ Filled all visible fields.")

        # Submit
        try:
            submit_button = driver.find_element(By.ID, "_aaba-add")
            driver.execute_script("arguments[0].click();", submit_button)
            log("📨 Clicked 'Add entry'.")
        except Exception as e:
            log(f"⚠️ Submit failed: {e}")

        time.sleep(3)
        log("✅ Form submitted successfully (check guestbook).")

    except WebDriverException as e:
        log(f"❌ WebDriver error: {e}")
    except Exception as e:
        log(f"❌ Error: {e}")
    finally:
        if driver:
            safe_quit(driver)

if __name__ == "__main__":
    main()
