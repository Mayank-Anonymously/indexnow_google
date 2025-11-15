import sys
import json
import requests
from bs4 import BeautifulSoup

def log(msg):
    """Stream log output for Next.js handler."""
    print(msg, flush=True)

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

    # Default input values
    base_url = "http://www.rose.ne.jp/~art/cgi-bin/yybbs/yybbs.cgi?"
    form_url = data.get("form_url", base_url)
    your_name = data.get("name", "Guest Poster")
    your_email = data.get("email", "guestposter@example.com")
    your_website = data.get("website", "http://guestposter.example.com")
    your_title = data.get("title", "Guest Message")
    your_message = data.get("message", "こんにちは！素晴らしいサイトです！")
    your_pwd = data.get("pwd", "Mayankk2")
    your_color = str(data.get("color", "0"))

    try:
        # Step 1️⃣ Fetch page
        log(f"🌐 Fetching form page: {form_url}")
        session = requests.Session()
        r = session.get(form_url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Step 2️⃣ Locate the <form> element
        form = soup.find("form", {"method": "POST"})
        if not form:
            log("❌ Could not find POST form.")
            return

        # Extract form action and hidden inputs
        form_action = form.get("action", "")
        if not form_action.startswith("http"):
            form_action = requests.compat.urljoin(form_url, form_action)

        hidden_inputs = {i.get("name"): i.get("value", "") for i in form.find_all("input", {"type": "hidden"})}

        # Debug info
        log(f"🧩 Found hidden fields: {hidden_inputs}")
        log(f"📨 Target action URL: {form_action}")

        # Step 3️⃣ Prepare full payload
        payload = {
            "mode": hidden_inputs.get("mode", "regist"),
            "page": hidden_inputs.get("page", ""),
            "tpwd": hidden_inputs.get("tpwd", ""),
            "name": your_name,
            "email": your_email,
            "sub": your_title,
            "comment": your_message,
            "url": your_website,
            "pwd": your_pwd,
            "color": your_color,
        }

        log(f"📦 Prepared Payload: {payload}")

        # Step 4️⃣ Submit POST
        res = session.post(form_action, data=payload, timeout=20)
        log(f"🌍 Response Code: {res.status_code}")

        # Step 5️⃣ Handle Response
        if res.status_code == 200:
            if "エラー" in res.text or "error" in res.text.lower():
                log("⚠️ Submission may have failed — check server validation.")
            else:
                log("✅ Form submitted successfully to rose.ne.jp!")
        else:
            log(f"❌ Submission failed with HTTP {res.status_code}")

    except Exception as e:
        log(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    main()
