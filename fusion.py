from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import datetime

login_url = "https://eu5.fusionsolar.huawei.com/unisso/login.action?service=%2Funisess%2Fv1%2Fauth%3Fservice%3D%252Fnetecowebext%252Fhome%252Findex.html#/LOGIN"

scrape_url = "https://uni005eu5.fusionsolar.huawei.com/rest/pvms/web/station/v1/station/station-list"

username = "SolarKos"
password = "Solarenergy2023"

def current_month_index():
    # Get the current date
    current_date = datetime.datetime.now()
    
    # Extract the month from the current date
    current_month = current_date.month
    
    return current_month

def login_to_website(url, username, password):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    # Initialize the web driver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    try:
        # Open the website
        driver.get(url)

        # Locate the username and password fields and submit button using their HTML attributes
        username_field = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/div[3]/div[1]/div[2]/div[2]/div[3]/input[1]"))
        )
        password_field = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/div[3]/div[1]/div[3]/div[3]/input"))
        )
        submit_button = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/div[3]/div[4]/div/div/span"))
        )

        # Input your username and password
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Click the submit button to attempt login
        submit_button.click()

        # Wait for some time to see the result (you might want to adjust this)
        WebDriverWait(driver, 200).until(EC.title_contains("List View"))

        # Retrieve and store cookies after successful login
        cookies = driver.get_cookies()

        # Perform API requests using the same browser instance
        data = format_json(make_api_request(driver, scrape_url, cookies), driver, cookies)
        return data

    finally:
        # Close the browser window
        driver.quit()
        
def format_json(json, driver, cookies):
    ret = []
    list = json["data"]["list"]
    for item in list:
        specific_url = "https://uni005eu5.fusionsolar.huawei.com/rest/pvms/web/station/v1/overview/energy-balance?timeDim=5&queryTime=1704063600000&timeZone=1&timeZoneStr=Europe%2FBelgrade&stationDn=" + item["dn"]
        extra_data = make_api_request(driver, specific_url, cookies, "GET")["data"]["productPower"][current_month_index() - 1]
        
        ret.append({
            "Klienti": item['name'],
            "Sistemi Monitorues": "FusionSolar",
            "Prodhimi Aktual Ditore [kWh]": str(round(float(item['dailyEnergy']), 3)) + " [kWh]",
            "Prodhimi Specifik Ditore [kWh/kWp]": str(round(float(item['eqPowerHours']), 3)) + " [kWh/kWp]",
            "Prodhimi Aktual Mujor [kWh]": str(extra_data) + " [kWh]",
            "Prodhimi Specifik Mujor [kWh/kWp]": "No Data",
        })
    return ret

def make_api_request(driver, api_data, cookies, method = "POST"):
    api_url = api_data

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # Convert cookies list to a dictionary
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

    payload = {
        "curPage": 1,
        "pageSize": 100,
        "gridConnectedTime": "",
        "queryTime": 1705705200000,
        "timeZone": 1,
        "sortId": "createTime",
        "sortDir": "DESC",
        "locale": "en_US"
    }

    try:
        # Use the existing browser instance for API request
        if method == "GET":
            driver.get(api_url)
            data = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
            # Execute JavaScript to get the content
            json_data = json.loads(data.text)
            return json_data
        elif method == "POST":
            response = requests.post(api_url, headers=headers, cookies=cookies_dict, json=payload)

            # Check if the request was successful (status code 200)
            response.raise_for_status()

            # If successful, print the JSON content
            return response.json()
        # Add other methods (PUT, DELETE, etc.) as needed

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")

def main_fusion():
    return login_to_website(login_url, username, password)

if __name__ == "__main__":
    main_fusion()
