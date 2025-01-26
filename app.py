from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Path to your chromedriver
CHROME_DRIVER_PATH = "/Froling_Connect"  # Update the path if needed

# URLs
URL = "https://connect-web.froeling.com/login"  # Login URL
PAGES = {
    "Boiler": "https://connect-web.froeling.com/facility/67918/components/1_100",
    "Hot Water Tank": "https://connect-web.froeling.com/facility/67918/components/200_2100",
    "Heating Tank": "https://connect-web.froeling.com/facility/67918/components/400_4100",
    "Solar": "https://connect-web.froeling.com/facility/67918/components/1_500",
    "Feed System": "https://connect-web.froeling.com/facility/67918/components/1_906",
}

# Create a new instance of Chrome WebDriver and specify the path to chromedriver
driver = webdriver.Chrome()

# Open the login page
driver.get(URL)

# Wait for the page to load
time.sleep(2)

try:
    # Login process
    username_field = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='username']")
    password_field = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='current-password']")
    username_field.send_keys("zsolt.farnas@gmail.com")
    password_field.send_keys("Zsoolti20!")
    login_button = driver.find_element(By.CLASS_NAME, "mdc-button")
    login_button.click()

    # Wait for login to complete
    time.sleep(3)

    print("Login successful!")

    # Consolidated HTML content
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scraped Data</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 30px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f4f4f4;
                font-weight: bold;
            }
            h1, h2 {
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>Scraped Data from All Pages</h1>
    """

    # Function to scrape a single page
    def scrape_page(url, page_name):
        driver.get(url)
        time.sleep(5)  # Wait for the page to load

        # Scrape data
        keys = driver.find_elements(By.CLASS_NAME, "key")
        values = driver.find_elements(By.CLASS_NAME, "value")
        scraped_data = [(key.text, value.text) for key, value in zip(keys, values)]

        # Add a section for this page to the HTML content
        global html_content
        html_content += f"<h2>{page_name}</h2>\n"
        html_content += """
        <table>
            <thead>
                <tr>
                    <th>Key</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
        """
        for key, value in scraped_data:
            html_content += f"                <tr>\n"
            html_content += f"                    <td>{key}</td>\n"
            html_content += f"                    <td>{value}</td>\n"
            html_content += f"                </tr>\n"
        html_content += """
            </tbody>
        </table>
        """

    # Iterate over all pages and scrape data
    for page_name, url in PAGES.items():
        print(f"Scraping data from {page_name}...")
        scrape_page(url, page_name)

    # Finalize the HTML content
    html_content += """
    </body>
    </html>
    """

    # Save the consolidated HTML to a file
    output_file = "scraped_data_all_pages.html"
    with open(output_file, "w") as file:
        file.write(html_content)

    print(f"All data saved to {output_file}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
