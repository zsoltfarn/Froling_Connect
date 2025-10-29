from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import shutil
import time
import json
from datetime import datetime
from config import FROLING_USERNAME, FROLING_PASSWORD

# Chromedriver path is managed automatically by webdriver-manager.

# URLs
URL = "https://connect-web.froeling.com/login"  # Login URL
PAGES = {
    "Boiler": "https://connect-web.froeling.com/facility/67918/components/1_100",
    "Hot Water Tank": "https://connect-web.froeling.com/facility/67918/components/200_2100",
    "Heating Tank": "https://connect-web.froeling.com/facility/67918/components/400_4100",
    "Solar": "https://connect-web.froeling.com/facility/67918/components/1_500",
    "Feed System": "https://connect-web.froeling.com/facility/67918/components/1_906",
}

# Create a new instance of Chrome WebDriver with headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')  # Required for some systems
# Extra flags helpful on servers/containers
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--remote-debugging-port=9222')
chrome_options.add_argument('--user-data-dir=/tmp/froeling-chrome')

# If using snap-installed Chromium or a custom Chrome path, allow override via env var
chrome_binary_env = os.getenv('CHROME_BINARY')
if chrome_binary_env:
    chrome_options.binary_location = chrome_binary_env
else:
    # Try to auto-detect a common Chrome/Chromium binary
    for exe in ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']:
        detected = shutil.which(exe)
        if detected:
            chrome_options.binary_location = detected
            break

# Decide Chrome type based on available binary
# Use Selenium Manager (Selenium 4.6+) to automatically manage the driver.
# This works for both Google Chrome and Chromium when the binary is detected or provided via CHROME_BINARY.
driver = webdriver.Chrome(options=chrome_options)

# Open the login page
driver.get(URL)

# Wait for the page to load
time.sleep(2)

try:
    # Login process
    username_field = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='username']")
    password_field = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='current-password']")
    username_field.send_keys(FROLING_USERNAME)
    password_field.send_keys(FROLING_PASSWORD)
    login_button = driver.find_element(By.CLASS_NAME, "mdc-button")
    login_button.click()

    # Wait for login to complete
    time.sleep(3)

    print("Login successful!")

    # Function to scrape a single page
    def scrape_page(url, page_name):
        driver.get(url)
        time.sleep(5)  # Wait for the page to load

        data = {}
        # Special metrics we want to track for Boiler
        boiler_metrics = {
            "Boiler Status": None,
            "Operation hours": None,
            "Hours since last maintenance": None
        }

        # Get all key-value pairs
        key_elements = driver.find_elements(By.CLASS_NAME, "key")
        value_elements = driver.find_elements(By.CLASS_NAME, "value")

        for key_elem, value_elem in zip(key_elements, value_elements):
            key = key_elem.text.strip()
            value = value_elem.text.strip()
            if key and value:  # Only add if both key and value are non-empty
                # Handle translation for Kesselzustand to Boiler Status
                if key == "Kesselzustand":
                    key = "Boiler Status"
                data[key] = value
                # Check if this is one of our special boiler metrics
                if page_name == "Boiler" and key in boiler_metrics:
                    boiler_metrics[key] = value

        # Get data from infoboxes
        infoboxes = driver.find_elements(By.CLASS_NAME, "froeling-infobox")
        for box in infoboxes:
            box_text = box.text
            for line in box_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    # Handle translation for Kesselzustand to Boiler Status
                    if key == "Kesselzustand":
                        key = "Boiler Status"
                    data[key] = value.strip()
                    # Check if this is one of our special boiler metrics
                    if page_name == "Boiler" and key in boiler_metrics:
                        boiler_metrics[key] = value.strip()  

        return data

    # Initialize data dictionary
    scraped_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pages": {}
    }

    # Iterate over all pages and scrape data
    for page_name, url in PAGES.items():
        print(f"Scraping data from {page_name}...")
        scraped_data["pages"][page_name] = scrape_page(url, page_name)

    # Save only the latest data to JSON file
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump([scraped_data], file, indent=4, ensure_ascii=False)

    print(f"Latest data saved to data.json")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
