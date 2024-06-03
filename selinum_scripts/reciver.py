from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
from pyvirtualdisplay import Display
import time
import os
display = Display(visible=0, size=(800, 800))  
display.start()

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

chrome_options = webdriver.ChromeOptions()    
# Add your options as needed    
options = [
  # Define window size here
   "--window-size=1200,1200",
    "--ignore-certificate-errors"
 
    #"--headless",
    #"--disable-gpu",
    #"--window-size=1920,1200",
    #"--ignore-certificate-errors",
    #"--disable-extensions",
    #"--no-sandbox",
    #"--disable-dev-shm-usage",
    #'--remote-debugging-port=9222'
]

for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome(options = chrome_options)

driver.get("http://127.0.0.1:8000")

signup_xpaths = {
    "signup_button" : '/html/body/main/a/button',
    "username" : '//*[@id="createAccountForm"]/fieldset/label[1]/input',
    "password" : '//*[@id="createAccountForm"]/fieldset/label[2]/input',
    "signup_submit" : '//*[@id="createAccountForm"]/fieldset/button',
}

login_xpaths = {
    "username" : '//*[@id="loginForm"]/fieldset/label[1]/input',
    "password" : '//*[@id="loginForm"]/fieldset/label[2]/input',
    "login_button" : '//*[@id="loginForm"]/button',
}

download_xpaths = {
    "download_button" : '/html/body/main/table/tbody/tr[1]/td[3]/button',
}

def signup():
    #waits for signup 1
    time.sleep(10)
    driver.find_element(By.XPATH, signup_xpaths["signup_button"]).click()
    driver.find_element(By.XPATH, signup_xpaths["username"]).send_keys("testuser2")
    driver.find_element(By.XPATH, signup_xpaths["password"]).send_keys("password")
    driver.find_element(By.XPATH, signup_xpaths["signup_submit"]).click()


def login():
    #waits for login & upload 1
    time.sleep(40)
    driver.find_element(By.XPATH, login_xpaths["username"]).send_keys("testuser2")
    driver.find_element(By.XPATH, login_xpaths["password"]).send_keys("password")
    driver.find_element(By.XPATH, login_xpaths["login_button"]).click()


def download():
    #waits for login 2
    time.sleep(10)
    driver.find_element(By.XPATH, download_xpaths["download_button"]).click()
    time.sleep(10)

signup()
login()
download()

