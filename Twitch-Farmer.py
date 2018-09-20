import time
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def SetUp(Proxy, username, password):
    global driver
    print("using proxy: " + str(Proxy) + '\n')

    chrome_driver_path = Path("{}/drivers/chromedriver".format(os.getcwd()))

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=http://%s' % Proxy)
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)

    # driver = webdriver.Chrome(executable_path=chrome_driver_path)

    driver.set_page_load_timeout(20)

    Login(username, password)


def change_proxy(twitchUsername, twitchPassword):
    global proxy_count
    global oldUsername
    global oldPassword
    oldUsername = twitchUsername
    oldPassword = twitchPassword
    if (proxies[proxy_count + 1] != "end"):
        proxy_count += 1 
        driver.quit()
        SetUp(proxies[proxy_count], oldUsername, oldPassword)
    else:
        print ("Done!!! No more proxies to test" + '\n')
        print("------------------------------------------- " + '\n')
        driver.quit()


def Login(twitchUsername, twitchPassword):
    print("using username: " + str(twitchUsername) + '\n')
    print("using password: " + str(twitchPassword) + '\n')
    print("------------------------------------------- " + '\n')

    try:
        driver.get("https://www.twitch.tv/login")
        #driver.get("http://whatismyipaddress.com")
    except TimeoutException:
        print ("")     

    global channelXpath
    global delay
    global myAccountXpath
    global incorrectCapthaXpath
    global incorrectUserXpath

    usernameFieldXpath = "//div[contains(@data-a-target,'login-username-input')]/input"
    passwordFieldXpath = "//div[contains(@data-a-target,'login-password-input')]/input"
    loginButtonXpath = "//button[contains(@data-a-target,'passport-login-button')]"
    incorrectUserXpath = "//div[contains(@class, 'server-message-alert')]"
    myAccountXpath = "//div[contains(@data-a-target, 'user-display-name')]"
    incorrectCapthaXpath = "//div[contains(@id, 'recaptcha-element-container')]"
    channelXpath= "//div[contains(@data-target, 'channel-header-right')]//button[contains(@data-a-target, 'follow-button')]"
    
    delay = 15

    # checks if login page is loaded
    try:
        usernameFieldElement = WebDriverWait(driver, delay + 5).until(EC.presence_of_element_located((By.XPATH, usernameFieldXpath)))
        passwordFieldElement = driver.find_element_by_xpath(passwordFieldXpath)
        loginButtonElement = driver.find_element_by_xpath(loginButtonXpath)
        usernameFieldElement.clear()
        usernameFieldElement.send_keys(twitchUsername)
        passwordFieldElement.clear()
        passwordFieldElement.send_keys(twitchPassword)
        loginButtonElement.click()
        Logged(twitchUsername, twitchPassword)
    except TimeoutException:
        print("Time expired, changing proxy!!!(1)" + '\n')
        print("------------------------------------------- " + '\n')
        change_proxy(twitchUsername, twitchPassword)


def Logged(twitchUsername, twitchPassword):
    global oldProxy

    #checks if logged
    try:
        WebDriverWait(driver, delay - 5).until(EC.presence_of_element_located((By.XPATH, myAccountXpath)))
        Follow(twitchUsername, twitchPassword)
    except TimeoutException:
        try:
            driver.find_element_by_xpath(incorrectCapthaXpath)
            print ("Incorrect CAPTCHA, changing proxy!!!" + '\n')
            print("------------------------------------------- " + '\n')
            change_proxy(twitchUsername, twitchPassword)          
        except:
            try:
                driver.find_element_by_xpath(incorrectUserXpath)
                print ("Incorrect username or password, changing account!!!" + '\n')
                print("------------------------------------------- " + '\n')
                oldProxy = proxies[proxy_count]              
                change_Account = True
                driver.quit()
            except:
                    print ("Time expired, changing proxy!!!(2)" + '\n')
                    print("------------------------------------------- " + '\n')
                    change_proxy(twitchUsername, twitchPassword)

def Follow(twitchUsername, twitchPassword):
    driver.get("https://www.twitch.tv/" + str(channel))

    #checks if channel is found
    try:
        followButtonElement = WebDriverWait(driver, delay - 5).until(EC.presence_of_element_located((By.XPATH, channelXpath)))
        followButtonElement.click()
        time.sleep(2)
        print ("Folowing, moving on the next user!!!" + '\n')
        print("------------------------------------------- " + '\n')
        driver.quit()
    except TimeoutException:
        #checks if channel is already following
        try:
            driver.find_element_by_xpath("//button[contains(@data-a-target, 'unfollow-button')]")
            print ("This user is already following this channel, moving on the next user!!!" + '\n')
            print("------------------------------------------- " + '\n')
            driver.quit()
        except:
            try:
                driver.find_element_by_xpath(channelXpath)
                print ("Bad channel, reset bot!!!" + '\n')
                print("------------------------------------------- " + '\n')
                return
            except:
                print ("Time expired, changing proxy!!!(3)" + '\n')
                print("------------------------------------------- " + '\n')
                change_proxy(twitchUsername, twitchPassword)             
#__main__#
#global proxy_count
global change_Account
change_Account = False
proxy_count = 0

f_proxies = open("proxies.txt", "r")
proxies = f_proxies.read().splitlines()[1:]
if (proxies[-1] != "end"):
    with open("proxies.txt", 'a') as f_proxies:
        f_proxies.write('\n' + "end")
f_proxies.close()

channel = input('what channel should i follow?: ')

with open('users.txt') as f_users:
  credentials = [x.strip().split(':') for x in f_users.readlines()[1:]]

for username, password in credentials:
        if (proxies[proxy_count] != "end"):
            if (change_Account == True):
                change_Account = False  
                SetUp(oldProxy, oldUsername, oldPassword)
            else:
                SetUp(proxies[proxy_count], username, password)
                proxy_count += 1

print ("Bot Stopped!!!")
