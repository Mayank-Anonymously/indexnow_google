import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
from io import BytesIO
import random
import string

# --- Configuration ---
form_url = "http://example.com/index.php?site=profile&action=guestbook&id=11"
user_message = "Hello! This is an automated guestbook message."

# --- Helper functions ---
def generate_random_name():
    return "Guest" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

def generate_random_email():
    return "".join(random.choices(string.ascii_lowercase, k=6)) + "@example.com"

def generate_random_website():
    return "https://example.com/" + "".join(random.choices(string.ascii_lowercase, k=5))

def solve_captcha(captcha_url, session):
    """Download captcha image and extract text using OCR"""
    response = session.get(captcha_url)
    img = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(img, config="--psm 8").strip()
    return text

# --- Start session ---
session = requests.Session()
response = session.get(form_url, timeout=15)
soup = BeautifulSoup(response.text, "html.parser")

# --- Extract form ---
form = soup.find("form", id="post")
if not form:
    raise Exception("Form with id='post' not found")

form_action = form.get("action")
if not form_action.startswith("http"):
    form_action = requests.compat.urljoin(form_url, form_action)

# --- Extract hidden inputs ---
payload = {}
for hidden_input in form.find_all("input", type="hidden"):
    name = hidden_input.get("name")
    value = hidden_input.get("value", "")
    if name:
        payload[name] = value

# --- Fill random user data and message ---
payload.update({
    "gbname": generate_random_name(),
    "gbemail": generate_random_email(),
    "gburl": generate_random_website(),
    "message": user_message
})

# --- Handle captcha ---
captcha_img_tag = form.find("img", alt="Sicherheitscode")
if captcha_img_tag:
    captcha_src = captcha_img_tag.get("src")
    captcha_text = solve_captcha(requests.compat.urljoin(form_url, captcha_src), session)
    payload["captcha"] = captcha_text
    # Get captcha_hash hidden input
    captcha_hash_input = form.find("input", {"name": "captcha_hash"})
    if captcha_hash_input:
        payload["captcha_hash"] = captcha_hash_input.get("value", "")

# --- Submit form ---
submit_response = session.post(form_action, data=payload)

if submit_response.status_code == 200:
    print("✅ Form submitted successfully!")
else:
    print(f"❌ Submission failed: {submit_response.status_code}")

# --- Debug output ---
print("Payload sent:", payload)
