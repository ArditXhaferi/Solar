from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import requests
import json

login_url = "https://www.solarweb.com/PvSystems/PvSystem?pvSystemId=5f3250da-b7a1-4ccc-87a4-a07fcc583d30"

scrape_url = "https://www.solarweb.com/PvSystems/GetPvSystemsForListView?_=1705327186792"
scrape_specific = "https://www.solarweb.com/Chart/GetChartNew?pvSystemId=*item-id*&year=2024&month=1&day=1&interval=year&view=production"

username = "info@sunvolta-ks.com"
password = "Valoni123!"

def login_to_website(url, username, password):
    # Initialize the web driver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome(ChromeDriverManager().install())

    try:
        # Open the website
        driver.get(url)

        # Locate the username and password fields and submit button using their HTML attributes
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "usernameUserInput"))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        submit_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-button"))
        )

        # Input your username and password
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Click the submit button to attempt login
        submit_button.click()

        # Wait for some time to see the result (you might want to adjust this)
        WebDriverWait(driver, 200).until(EC.title_contains("Hajdar Dushi"))
        
        data = format_json(get_json_content_with_selenium(driver, scrape_url), driver)
        return data
    finally:
        # Close the browser window
        driver.quit()

def get_access_token_from_local_storage(driver):
    # Execute JavaScript to get the access token from local storage
    access_token = driver.execute_script("return localStorage.getItem('access_token');")
    
    return access_token

def get_json_content_with_selenium(driver, url):
    # Open the URL
    driver.get(url)

    # Wait for some time to let the page load
    data = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
    # Execute JavaScript to get the content
    json_data = json.loads(data.text)
    return json_data
    
def format_json(json, driver):
    ret = []
    list = json["data"]

    for item in list:
        local_item = scrape_specific.replace("*item-id*", item['PvSystemId'])
        new_item = get_json_content_with_selenium(driver, local_item)
        try:
            PAM = str(round(new_item["settings"]["series"][0]["data"][-1][1], 3)) + " [kWh]"
        except (KeyError, IndexError):
            PAM = "No Data"

        ret.append({
        "Klienti": item['PvSystemName'],
        "Sistemi Monitorues": "Fronius",
        "Prodhimi Aktual Ditore [kWh]": str(round(item['EnergyTodayInkWh'], 3)) + " [kWh]",
        "Prodhimi Specifik Ditore [kWh/kWp]": str(round(item['KwhPerKwp'], 3)) + " [kWh/kWp]",
        "Prodhimi Aktual Mujor [kWh]": PAM, 
        "Prodhimi Specifik Mujor [kWh/kWp]": "No Data"
    })
    return ret

def main_fronius():
    return login_to_website(login_url, username, password)