# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime
from pathlib import Path
from config import FROLING_USERNAME, FROLING_PASSWORD

# URLs
URL = "https://connect-web.froeling.com/login"
PAGES = {
    "Boiler": "https://connect-web.froeling.com/facility/67918/components/1_100",
    "Hot Water Tank": "https://connect-web.froeling.com/facility/67918/components/200_2100",
    "Heating Tank": "https://connect-web.froeling.com/facility/67918/components/400_4100",
    "Solar": "https://connect-web.froeling.com/facility/67918/components/1_500",
    "Feed System": "https://connect-web.froeling.com/facility/67918/components/1_906",
}

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--hide-scrollbars")

APP_DIR = Path(__file__).resolve().parent
(APP_DIR / ".chrome-profile").mkdir(exist_ok=True)
chrome_options.add_argument(f"--user-data-dir={APP_DIR / '.chrome-profile'}")

driver = webdriver.Chrome(options=chrome_options)

# --- URLs and scraping logic ---
driver.get(URL)
time.sleep(2)

try:
    # Login
    username_field = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='username']")
    password_field = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='current-password']")
    username_field.send_keys(FROLING_USERNAME)
    password_field.send_keys(FROLING_PASSWORD)
    login_button = driver.find_element(By.CLASS_NAME, "mdc-button")
    login_button.click()
    time.sleep(3)
    print("Login successful!")

    # Scrape helper
    def scrape_page(url, page_name):
        driver.get(url)
        time.sleep(5)
        keys = driver.find_elements(By.CLASS_NAME, "key")
        values = driver.find_elements(By.CLASS_NAME, "value")
        data = {}
        for key, value in zip(keys, values):
            k = key.text.strip()
            v = value.text.strip()
            if k:
                if k == "Kesselzustand":
                    k = "Boiler Status"
                data[k] = v
        return data

    # Collect new dataset
    scraped_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pages": {}
    }

    for page_name, url in PAGES.items():
        print(f"Scraping data from {page_name}...")
        scraped_data["pages"][page_name] = scrape_page(url, page_name)

    # Load existing JSON (if any)
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            if not isinstance(existing_data, list):
                existing_data = [existing_data]
    except FileNotFoundError:
        existing_data = []

    # Append and save
    existing_data.append(scraped_data)
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

    print("? All data saved to data.json")

except Exception as e:
    print(f"? Error: {e}")

finally:
    driver.quit()
