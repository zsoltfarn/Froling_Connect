# Web Scraper for Fröling Connect

## Overview
This project is a web scraper that logs into the Fröling Connect web portal, navigates to various system component pages, extracts relevant data, and saves it into a JSON file. The script uses Selenium WebDriver to automate the browser interactions.

## Features
- Logs into Fröling Connect using provided credentials.
- Navigates to predefined pages for different system components.
- Scrapes key-value pairs of displayed data.
- Saves the extracted data to a `data.json` file with a timestamp.
- Runs in headless mode for efficiency.

## Prerequisites
- Python 3.x installed on your system.
- Google Chrome browser installed.
- ChromeDriver installed and accessible at `/usr/local/chromedriver/` (update path if necessary and install the version that works with your Google Chrome browser).
- Selenium package installed (`pip install selenium`).
- A `config.py` (change the filename from 'confg.py.example' to 'config.py' and change the "your_username" and "your_password" with your own credentials) file containing:
  ```python
  FROLING_USERNAME = "your_username"
  FROLING_PASSWORD = "your_password"
  ```

## Installation
1. Clone this repository or download the script.
2. Install required dependencies:
   ```bash
   pip install selenium
   ```
3. Ensure ChromeDriver is installed and update the path in the script if necessary.
4. Create a `config.py` file and enter your login credentials.

## Usage
Run the script with.:
```bash
python app.py
```

The script will:
1. Open Chrome in headless mode.
2. Log into the Fröling Connect portal.
3. Scrape data from the specified system component pages.
4. Save the data to `data.json`.

## JSON Output Format
The extracted data is stored in `data.json` in the following structure:
```json
[
    {
        "timestamp": "YYYY-MM-DD HH:MM:SS",
        "pages": {
            "Boiler": { "key1": "value1", "key2": "value2" },
            "Hot Water Tank": { "key1": "value1", "key2": "value2" }
        }
    }
]
```

## Troubleshooting
- **Chromedriver not found:** Ensure you have installed ChromeDriver and set the correct path. Also ensure that it's compatible with your version of Google Chrome.
- **Login issues:** Double-check your credentials in `config.py`.
- **Data not scraped:** Check if the class names `key` and `value` match the website’s HTML structure.

## License
This project is open-source and free to use under the MIT License.

