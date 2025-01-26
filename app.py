from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime
from config import FROLING_USERNAME, FROLING_PASSWORD

# Path to your chromedriver
CHROME_DRIVER_PATH = "/Froling"  # Update the path if needed

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

        # Scrape data
        keys = driver.find_elements(By.CLASS_NAME, "key")
        values = driver.find_elements(By.CLASS_NAME, "value")
        return {key.text: value.text for key, value in zip(keys, values)}

    # Initialize data dictionary
    scraped_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pages": {}
    }

    # Iterate over all pages and scrape data
    for page_name, url in PAGES.items():
        print(f"Scraping data from {page_name}...")
        scraped_data["pages"][page_name] = scrape_page(url, page_name)

    try:
        # Load existing data from JSON file
        with open('data.json', 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    # Append new data to existing data
    existing_data.append(scraped_data)

    # Save updated data back to JSON file
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)

    print(f"All data saved to data.json")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
