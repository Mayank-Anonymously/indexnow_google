import sys
import json
import requests
from bs4 import BeautifulSoup

def log(message):
    print(message, flush=True)

def main():
    # Read input (same format as your existing handler)
    raw = sys.stdin.read().strip()
    if not raw:
        log("No input received")
        return
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        log("Invalid JSON")
        return

    name = data.get("name", "Guest")
    url = data.get("url", "https://")
    message = data.get("message", "Hello from scraper!")

    # Step 1️⃣ - Load the chat page to grab fresh hidden fields
    page_url = "https://90plink.live/truc-tiep-tran-dau-heidenheimer-vs-borussia-monchengladbach-2413062/"
    session = requests.Session()
    resp = session.get(page_url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        log(f"Failed to load page: {resp.status_code}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    form = soup.find("form", id="sac-form")
    if not form:
        log("Form not found")
        return

    hidden_inputs = {inp.get("name"): inp.get("value", "") for inp in form.find_all("input", type="hidden")}

    # Step 2️⃣ - Prepare data for POST request
    post_data = {
        "sac_name": name,
        "sac_url": url,
        "sac_chat": message,
        **hidden_inputs
    }

    post_url = form.get("action")
    if not post_url.startswith("http"):
        post_url = "https://90plink.live" + post_url

    # Step 3️⃣ - Send the POST request
    res = session.post(post_url, data=post_data, headers={"User-Agent": "Mozilla/5.0"})
    if res.status_code == 200:
        log("✅ Message posted successfully!")
    else:
        log(f"❌ Failed to post message: {res.status_code}")

if __name__ == "__main__":
    main()
