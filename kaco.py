from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
from datetime import datetime

login_url = "https://www.solar-monitoring.net/vcom/login?language=en"

scrape_url = "https://www.solar-monitoring.net/vcom/performance-overview/get"

username = "sadiku-admin"
password = "sunvolta12"

def generate_date():
    current_date = datetime.now()
    return current_date.strftime("%Y-%-m-%-d")

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
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        submit_button = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "submit"))
        )

        # Input your username and password
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Click the submit button to attempt login
        submit_button.click()

        # Wait for some time to see the result (you might want to adjust this)
        WebDriverWait(driver, 200).until(EC.title_contains("VCOM"))

        # Retrieve and store cookies after successful login
        cookies = driver.get_cookies()

        # Perform API requests using the same browser instance
        data = format_json(make_api_request(driver, scrape_url, cookies, "POST"), driver, cookies)
        return data

    finally:
        # Close the browser window
        driver.quit()
        
def format_json(json, driver, cookies):
    ret = []
    list = json["data"]
    for item in list:
        extra_data = fetch_data_monthly(item["DT_RowId"], cookies)["data"][0]
        PAM = extra_data["E_Z_EVU"]
        PSM = extra_data["E_N"]
        ret.append({
            "Klienti": item['bezeichnung'],
            "Sistemi Monitorues": "Kaco",
            "Prodhimi Aktual Ditore [kWh]": str(round(float(item['E_Z_EVU'].replace(',', '')), 3)) + " [kWh]",
            "Prodhimi Specifik Ditore [kWh/kWp]": str(round(float(item['E_N'].replace(',', '')), 3)) + " [kWh/kWp]",
            "Prodhimi Aktual Mujor [kWh]": str(round(float(PAM.replace(',', '')), 3)) + " [kWh]",
            "Prodhimi Specifik Mujor [kWh/kWp]": str(round(float(PSM.replace(',', '')), 3)) + " [kWh/kWp]",
        })
    return ret

def make_api_request(driver, api_data, cookies, method = "POST"):
    payload = {
        "systemId": None,
        "date": "yesterday",
        "columns": [
            {"data": "STATUS", "name": "STATUS", "orderable": True, "search": {"value": ""}},
            {"data": "bezeichnung", "name": "bezeichnung", "orderable": True, "search": {"value": ""}},
            {"data": "LEISTUNG", "name": "LEISTUNG", "orderable": True, "search": {"value": ""}},
            {"data": "E_Z_EVU", "name": "E_Z_EVU", "orderable": True, "search": {"value": ""}},
            {"data": "G_M", "name": "G_M", "orderable": True, "search": {"value": ""}},
            {"data": "E_N", "name": "E_N", "orderable": True, "search": {"value": ""}},
            {"data": "PR", "name": "PR", "orderable": True, "search": {"value": ""}},
            {"data": "VFG", "name": "VFG", "orderable": True, "search": {"value": ""}},
            {"data": "EPI", "name": "EPI", "orderable": True, "search": {"value": ""}},
            {"data": "DATAINPUT", "name": "DATAINPUT", "orderable": True, "search": {"value": ""}},
            {"data": "E_SIM", "name": "E_SIM", "orderable": True, "search": {"value": ""}},
            {"data": "E_SIM_DIFF_PERC", "name": "E_SIM_DIFF_PERC", "orderable": True, "search": {"value": ""}},
            {"data": "LAST_DATAINPUT_LOCALTIME", "name": "LAST_DATAINPUT_LOCALTIME", "orderable": True, "search": {"value": ""}},
            {"data": "LOCAL_TIMEZONE_OFFSET", "name": "LOCAL_TIMEZONE_OFFSET", "orderable": True, "search": {"value": ""}},
            {"data": "SPECIFIC_YIELD_SIMULATED", "name": "SPECIFIC_YIELD_SIMULATED", "orderable": True, "search": {"value": ""}},
            {"data": "alarmsToday", "name": "alarmsToday", "orderable": True, "search": {"value": ""}},
            {"data": "alarmsYesterday", "name": "alarmsYesterday", "orderable": True, "search": {"value": ""}},
            {"data": "alarmsLastWeek", "name": "alarmsLastWeek", "orderable": True, "search": {"value": ""}},
            {"data": "INVERTER_EVALUATION", "name": "INVERTER_EVALUATION", "orderable": True, "search": {"value": ""}}
        ],
        "order": [{"column": "bezeichnung", "dir": "asc"}],
        "start": 0,
        "length": 25
    }
    api_url = api_data

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # Convert cookies list to a dictionary
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

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

import requests

def fetch_data_monthly(id, cookies):
    url = "https://www.solar-monitoring.net/vcom/performance-overview/get"

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    body = {
        "systemId": id,
        "date": "customMonth",
        "columns": [
            {"data": "STATUS", "name": "STATUS", "orderable": True, "search": {"value": ""}},
            {"data": "bezeichnung", "name": "bezeichnung", "orderable": True, "search": {"value": ""}},
            {"data": "LEISTUNG", "name": "LEISTUNG", "orderable": True, "search": {"value": ""}},
            {"data": "E_Z_EVU", "name": "E_Z_EVU", "orderable": True, "search": {"value": ""}},
            {"data": "G_M", "name": "G_M", "orderable": True, "search": {"value": ""}},
            {"data": "E_N", "name": "E_N", "orderable": True, "search": {"value": ""}},
            {"data": "PR", "name": "PR", "orderable": True, "search": {"value": ""}},
            {"data": "VFG", "name": "VFG", "orderable": True, "search": {"value": ""}},
            {"data": "EPI", "name": "EPI", "orderable": True, "search": {"value": ""}},
            {"data": "DATAINPUT", "name": "DATAINPUT", "orderable": True, "search": {"value": ""}},
            {"data": "E_SIM", "name": "E_SIM", "orderable": True, "search": {"value": ""}},
            {"data": "E_SIM_DIFF_PERC", "name": "E_SIM_DIFF_PERC", "orderable": True, "search": {"value": ""}},
            {"data": "LAST_DATAINPUT_LOCALTIME", "name": "LAST_DATAINPUT_LOCALTIME", "orderable": True, "search": {"value": ""}},
            {"data": "LOCAL_TIMEZONE_OFFSET", "name": "LOCAL_TIMEZONE_OFFSET", "orderable": True, "search": {"value": ""}},
            {"data": "SPECIFIC_YIELD_SIMULATED", "name": "SPECIFIC_YIELD_SIMULATED", "orderable": True, "search": {"value": ""}},
            {"data": "alarmsToday", "name": "alarmsToday", "orderable": True, "search": {"value": ""}},
            {"data": "alarmsYesterday", "name": "alarmsYesterday", "orderable": True, "search": {"value": ""}},
            {"data": "alarmsLastWeek", "name": "alarmsLastWeek", "orderable": True, "search": {"value": ""}},
            {"data": "INVERTER_EVALUATION", "name": "INVERTER_EVALUATION", "orderable": True, "search": {"value": ""}}
        ],
        "order": [{"column": "bezeichnung", "dir": "asc"}],
        "start": 0,
        "selectedDate": generate_date(),
        "customEndDate": generate_date(),
        "length": 25
    }
    
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

    response = requests.post(url, headers=headers, cookies=cookies_dict, json=body)
    response.raise_for_status()
    return response.json()

def main_kaco():
    return login_to_website(login_url, username, password)

if __name__ == "__main__":
    main_kaco()
