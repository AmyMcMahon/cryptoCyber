from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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
driver.save_screenshot('screenshot.png')

relative_path = './selinum_scripts/testing.txt'
absolute_path = os.path.abspath(relative_path)

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

upload_xpaths = {
    "file_upload" : '//*[@id="file"]',
    "selector" : '//*[@id="receiver"]',
    "selectUser": '//*[@id="receiver"]/option[3]',
    "upload_button" : '//*[@id="uploadForm"]/button'
}

def signup():
    driver.find_element(By.XPATH, signup_xpaths["signup_button"]).click()
    driver.save_screenshot('screenshot2.png')
    driver.find_element(By.XPATH, signup_xpaths["username"]).send_keys("testuser1")
    driver.find_element(By.XPATH, signup_xpaths["password"]).send_keys("password")
    driver.save_screenshot('screenshot3.png')
    driver.find_element(By.XPATH, signup_xpaths["signup_submit"]).click()
    print("signed up")
    os.system("echo signed up")
    time.sleep(10)
    driver.save_screenshot('screenshot4.png')

def login():
    #waits for singup 1 & 2
    time.sleep(10)
    driver.save_screenshot('screenshot5.png')
    driver.find_element(By.XPATH, login_xpaths["username"]).send_keys("testuser1")
    driver.save_screenshot('screenshot6.png')
    driver.find_element(By.XPATH, login_xpaths["password"]).send_keys("password")
    driver.save_screenshot('screenshot7.png')
    driver.find_element(By.XPATH, login_xpaths["login_button"]).click()
    driver.save_screenshot('screenshot8.png')
    print("logged in")
    os.system("echo logged in")
    time.sleep(5)

def upload():
    #waits for login 1
    time.sleep(10)
    driver.find_element(By.XPATH, upload_xpaths["file_upload"]).send_keys(absolute_path)
    driver.find_element(By.XPATH, upload_xpaths["selector"]).click()
    driver.find_element(By.XPATH, upload_xpaths["selectUser"]).click()
    driver.find_element(By.XPATH, upload_xpaths["upload_button"]).click()
    print("uploaded")
    os.system("echo uploaded")
    time.sleep(5)

signup()
login()
upload()

