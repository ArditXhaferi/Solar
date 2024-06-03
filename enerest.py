from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import requests

login_url = "https://sunvolta.enerest.world/"

scrape_urls = [
    "https://sunvolta.enerest.world/api/widget/widget/plant-yield/plant/1ed69ab4-8527-6190-9d82-1d93ad0b4832",
    "https://sunvolta.enerest.world/api/widget/widget/plant-yield/plant/1ed7c8d9-0347-6112-93b0-291c25fbc949",
    "https://sunvolta.enerest.world/api/widget/widget/plant-yield/plant/1ed53711-bc86-67ec-af75-ed69e12703c5",
    "https://sunvolta.enerest.world/api/widget/widget/plant-yield/plant/1ed7613d-a885-6bfa-ab0e-b5d4e32695e9",
    "https://sunvolta.enerest.world/api/widget/widget/plant-yield/plant/1ed850d6-a424-646a-9baa-5d4384c198db",
    "https://sunvolta.enerest.world/api/widget/widget/plant-yield/plant/1ed57661-1a55-66e6-8de9-334bc61611fd",
    ]

username = "sunvolta.ks@gmail.com"
password = "Kosova1234!"

def login_to_website(url, username, password):
    # Initialize the web driver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome(ChromeDriverManager().install())

    # Open the website
    driver.get(url)

    # Locate the username and password fields and submit button using their HTML attributes
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    submit_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "kc-login"))
    )

    # Input your username and password
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Click the submit button to attempt login
    submit_button.click()

    # Wait for some time to see the result (you might want to adjust this)
    WebDriverWait(driver, 200).until(EC.title_contains("Monitoring"))
    
    # for url in urls:
    #     fetch_and_print_content(driver, url)
    bearer_token = get_access_token_from_local_storage(driver)
    data = []
    for url in scrape_urls:
        data.append(make_api_request(url, bearer_token))
    driver.quit()

    return data

def get_access_token_from_local_storage(driver):
    # Execute JavaScript to get the access token from local storage
    access_token = driver.execute_script("return localStorage.getItem('access_token');")
    
    return access_token


def make_api_request(api_url, bearer_token):
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(api_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            ret = format_json(response.json())
            return ret
        else:
            print(f"API request failed with status code {response.status_code}:\n{response.text}")

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        
def format_json(json):
    if(json['yieldToday'] != 0):
        nint = json['yieldToday'] / 1000
    else:
        nint = 0
        
    if(json['yieldMonth'] != 0):
        ym = json['yieldMonth'] / 1000
    else:
        ym = 0
    
    ret = {
        "Klienti": json['plantLabel'],
        "Sistemi Monitorues": "Enerest",
        "Prodhimi Aktual Ditore [kWh]": str(round(nint, 3)) + " [kWh]",
        "Prodhimi Specifik Ditore [kWh/kWp]": str(round(json['normalizedYieldToday'], 3)) + " [kWh/kWp]",
        "Prodhimi Aktual Mujor [kWh]": str(round(ym, 3)) + " [kWh]",
        "Prodhimi Specifik Mujor [kWh/kWp]": str(round(json['normalizedYieldMonth'], 3)) + " [kWh/kWp]"
    }
    return ret

def main_enerest():
    return login_to_website(login_url, username, password)