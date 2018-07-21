import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def SetUp(Proxy, username, password):
    global driver
    print("using proxy: " + str(Proxy) + '\n')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=http://%s' % Proxy)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    #driver = webdriver.Chrome()

    #driver.set_page_load_timeout(15)

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
    global change_Account
    global delay
    global searchFieldID
    global incorrectCapthaXpath
    global incorrectUserXpath

    usernameFieldID = "username"
    passwordFieldName = "password"
    loginButtonXpath = '//*[@id="loginForm"]/div[3]/button'
    incorrectCapthaXpath = "//*[@id='loginForm']/div[contains(text(), 'Please complete the CAPTCHA correctly.')]"
    incorrectUserXpath = "//*[@id='loginForm']/div[contains(text(), 'Incorrect username or password.')]"
    searchFieldID = "query"
    channelXpath= "//*[@id='channel']/div/div[2]/p"  
    delay = 15

    # checks if login page is loaded
    try:
        usernameFieldElement = WebDriverWait(driver, delay + 5).until(EC.presence_of_element_located((By.ID, usernameFieldID)))
        passwordFieldElement = driver.find_element_by_name(passwordFieldName)
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
        WebDriverWait(driver, delay - 5).until(EC.presence_of_element_located((By.ID, searchFieldID)))
        Follow()
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

def Follow():
    driver.get("https://www.twitch.tv/" + str(channel))

    #checks if channel is found
    try:
        followButtonElement = WebDriverWait(driver, delay - 5).until(EC.presence_of_element_located((By.LINK_TEXT, "Follow")))
        followButtonElement.click()
        time.sleep(2)
        print ("Folowing, moving on the next user!!!" + '\n')
        print("------------------------------------------- " + '\n')
        driver.quit()
    except TimeoutException:
        #checks if channel is already following
        try:
            driver.find_element_by_class_name("svg-heart")
            print ("This user is already following thin channel, moving on the next user!!!" + '\n')
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
#global change_Account
change_Account = False
proxy_count = 0

f_proxies = open("proxies.txt", "r")
proxies = f_proxies.read().splitlines()
if (proxies[-1] != "end"):
    with open("proxies.txt", 'a') as f_proxies:
        f_proxies.write('\n' + "end")
f_proxies.close()

channel = input('what channel should i follow?: ')

with open('users.txt') as f_users:
  credentials = [x.strip().split(':') for x in f_users.readlines()]

for username, password in credentials:
        if (proxies[proxy_count] != "end"):
            if (change_Account == True): 
                change_Account = False  
                SetUp(oldProxy, oldUsername, oldPassword)
            else:
                SetUp(proxies[proxy_count], username, password)
                proxy_count += 1

print ("Bot Stopped!!!")
