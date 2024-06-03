from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
driver.get("http://127.0.0.1:8000")

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
    driver.find_element(By.XPATH, signup_xpaths["username"]).send_keys("testuser1")
    driver.find_element(By.XPATH, signup_xpaths["password"]).send_keys("password")
    driver.find_element(By.XPATH, signup_xpaths["signup_submit"]).click()
    time.sleep(10)

def login():
    #waits for singup 1 & 2
    time.sleep(20)
    driver.find_element(By.XPATH, login_xpaths["username"]).send_keys("testuser1")
    driver.find_element(By.XPATH, login_xpaths["password"]).send_keys("password")
    driver.find_element(By.XPATH, login_xpaths["login_button"]).click()
    time.sleep(10)

def upload():
    #waits for login 1
    time.sleep(10)
    driver.find_element(By.XPATH, upload_xpaths["file_upload"]).send_keys(absolute_path)
    driver.find_element(By.XPATH, upload_xpaths["selector"]).click()
    driver.find_element(By.XPATH, upload_xpaths["selectUser"]).click()
    driver.find_element(By.XPATH, upload_xpaths["upload_button"]).click()
    time.sleep(5)

signup()
login()
upload()

