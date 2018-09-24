import sys
import os
from pathlib import Path
from time import sleep

from selenium import webdriver
import pandas
import json

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import TimeoutException

driver = None
current_proxy = None
proxy_timeout = False
delay = 10
page_elements = None


def follow_channel(username, follow_channel_name):
    global delay

    print("[{}] Trying to follow: [{}]".format(username, follow_channel_name))

    try:
        driver.get("https://www.twitch.tv/{}".format(follow_channel_name))

        follow_button = driver.find_element_by_xpath(
            get_page_element("follow_button"))

        follow_button.click()

        # wait for request
        sleep(5)

        print("[{}] Successfully followed: [{}]".format(
            username, follow_channel_name))

        return True
    except:
        # checks if channel is already following
        try:
            driver.find_element_by_xpath(get_page_element("unfollow_button"))

            print("[{}] Is already following: [{}], moving on the next user!!!".format(
                username, follow_channel_name))

            return True
        except:
            try:
                driver.find_element_by_xpath(
                    get_page_element("nonexistent_channel"))

                print("No channel: [{}] found, exiting!!!".format(
                    follow_channel_name))

                exit()
            except:
                pass

            return False


def sign_in(username, password):
    global proxy_timeout
    global delay

    print("[{}] Singing in...".format(username))

    try:
        driver.get("https://www.twitch.tv/login")

        username_input = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, get_page_element("username_input"))))

        password_input = driver.find_element_by_xpath(
            get_page_element("password_input"))
        login_button = driver.find_element_by_xpath(
            get_page_element("login_button"))

        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)

        login_button.click()

        WebDriverWait(driver, delay).until(EC.presence_of_element_located(
            (By.XPATH, get_page_element("my_account"))))

        print("[{}] Successfully signed in.\n".format(username))
        return True
    except TimeoutException:
        try:
            driver.find_element_by_xpath(get_page_element("auth_failed"))
            print("[{}] Incorrect credentials, changing account!!!".format(username))
            return False
        except:
            try:
                driver.find_element_by_xpath(get_page_element("recaptcha"))
                print("[{}] Recaptcha, changing proxy!!!".format(username))
            except:
                pass

            proxy_timeout = True
            return False


def main():
    global proxy_timeout
    global page_elements

    follow_channel_name = input("What channel should I follow? : ")

    # load page_elements json file
    with open(get_full_path("/page_elements.json")) as page_elements_file:
        page_elements = json.load(page_elements_file)

    accounts_csv_path = get_full_path("/data/accounts.csv")
    accounts_csv = pandas.read_csv(accounts_csv_path, sep=',', dtype="str")

    # define accounts.csv columns
    username_rows = accounts_csv.username
    password_rows = accounts_csv.password

    # go through every account in .csv
    for i, (username, password) in enumerate(zip(username_rows, password_rows)):
        if pandas.isnull(username) is False or pandas.isnull(password) is False:
            print("--------------------------------")

            run_driver(True)

            sign_in_status = sign_in(username, password)

            while sign_in_status is False and proxy_timeout:
                print("--------------------------------")
                print("Time expired, changing proxy...")
                print("Using previous account: [{}]\n".format(username))

                run_driver(True)

                sign_in_status = sign_in(username, password)

            if sign_in_status:
                if follow_channel(username, follow_channel_name):
                    accounts_csv.at[i,
                                    'following_channel'] = follow_channel_name
                    accounts_csv.at[i, 'used_proxy'] = current_proxy
                    accounts_csv.to_csv(accounts_csv_path, sep=',',
                                        index=False, index_label=False)
                else:
                    accounts_csv.at[i, 'following_channel'] = "ERROR"
                    accounts_csv.to_csv(accounts_csv_path, sep=',',
                                        index=False, index_label=False)

                    print("[{}] An error ocurred while trying to follow: [{}]!!!".format(
                        username, follow_channel_name))
    print("--------------------------------")
    print("No more accounts!!!")
    print("--------------------------------")


def get_page_element(input):
    global page_elements

    return page_elements[input]["value"]


def get_full_path(file_path):
    return str(Path("{}{}".format(os.getcwd(), file_path)))


def find_available_proxy():
    proxies_csv_path = get_full_path("/data/proxies.csv")
    proxies_csv = pandas.read_csv(proxies_csv_path, sep=',', dtype="str")

    # define proxies.csv columns
    proxy_rows = proxies_csv.proxy
    status_rows = proxies_csv.status

    # go through every proxy in .csv and check if it is available to use
    for i, (proxy, status) in enumerate(zip(proxy_rows, status_rows)):
        if i == len(proxy_rows) - 1 and status == "USED":
            print("--------------------------------")
            print("No more proxies!!!")
            print("--------------------------------")
            exit()
        elif pandas.isnull(status):
            proxies_csv.at[i, 'status'] = "USED"
            proxies_csv.to_csv(proxies_csv_path, sep=',',
                               index=False, index_label=False)
            return proxy


def run_driver(run_with_proxy):
    global driver
    global current_proxy

    # stop driver before changing it
    stop_driver()

    chrome_options = Options()
    chrome_options.add_argument("--lang=en-US,en")
    chrome_options.add_argument("--disable-notifications")

    if run_with_proxy:
        current_proxy = find_available_proxy()

        if current_proxy:
            chrome_options.add_argument(
                "--proxy-server={}".format(current_proxy))
            print("Using proxy: [{}]".format(current_proxy))

    current_os = sys.platform

    chrome_driver_file_name = ""
    if current_os in "darwin":
        chrome_driver_file_name = "chromedriver_mac64"
    elif current_os in "linux":
        chrome_driver_file_name = "chromedriver_linux64"
    elif current_os in "win32":
        chrome_driver_file_name = "chromedriver_win32.exe"

    chrome_driver_path = get_full_path(
        "/drivers/{}".format(chrome_driver_file_name))

    driver = webdriver.Chrome(options=chrome_options,
                              executable_path=chrome_driver_path)
    driver.set_window_size(880, 720)
    driver.set_window_position(0, 0)
    driver.set_page_load_timeout(20)


def stop_driver():
    global driver

    if driver is None:
        pass
    else:
        driver.quit()
        driver = None


def exit():
    stop_driver()
    input("Pres 'Enter' to Exit")
    sys.exit()


if __name__ == '__main__':
    main()
    exit()
