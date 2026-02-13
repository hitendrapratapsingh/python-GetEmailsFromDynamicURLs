from ddgs import DDGS
from urllib.parse import urlparse
import requests
import re
from datetime import datetime

# =============================
# USER INPUT
# =============================
keyword = input("Enter keyword: ")
target_count = int(input("How many URLs you want: "))

# =============================
# BLOCKED DOMAINS
# =============================
blocked_domains = [
    "linkedin.com",
    "clutch.co",
    "goodfirms.co",
    "themanifest.com",
    "justdial.com",
    "sulekha.com",
    "designrush.com",
    "topdevelopers.co",
    "techbehemoths.com"
]

# =============================
# STEP 1 — GET URLS
# =============================
print("\nSearching websites...")

results_set = set()

with DDGS() as ddgs:
    results = ddgs.text(
        keyword,
        region="in-en",
        safesearch="off",
        max_results=target_count * 3
    )

    for result in results:
        url = result.get("href")

        if not url:
            continue

        parsed = urlparse(url)
        domain = parsed.netloc
        clean_url = "https://" + domain

        if any(block in clean_url for block in blocked_domains):
            continue

        results_set.add(clean_url)

        if len(results_set) >= target_count:
            break

print(f"Collected {len(results_set)} unique websites")

# Save websites backup
with open("websites.txt", "w") as f:
    for site in results_set:
        f.write(site + "\n")

# =============================
# STEP 2 — SCRAPE EMAILS
# =============================
print("\nExtracting emails...")

email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

all_emails = set()

for site in results_set:
    print("Checking:", site)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(site, headers=headers, timeout=10)
        html = response.text

        raw_matches = re.finditer(email_pattern, html)

        for match in raw_matches:
            email = match.group()

            unwanted_extensions = [
                ".png", ".jpg", ".jpeg", ".webp", ".svg",
                ".gif", ".bmp", ".tiff", ".ico", ".avif",
                ".heic", ".mp4", ".mp3", ".pdf", ".zip"
            ]

            if any(email.lower().endswith(ext) for ext in unwanted_extensions):
                continue

            all_emails.add(email)

    except Exception as e:
        print("Error:", e)

# =============================
# STEP 3 — SAVE UNIQUE EMAILS
# =============================
cleaned_emails = sorted(all_emails)

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

file_name = f"emails_{current_time}.txt"

with open(file_name, "w") as output:
    for email in cleaned_emails:
        output.write(email + "\n")

print(f"\nFinished! {len(cleaned_emails)} unique emails saved in {file_name}")
