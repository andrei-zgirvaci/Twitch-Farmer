import sys
import os
from pathlib import Path

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


def follow_channel(follow_channel_name):
    pass


def sign_in(username, passowrd):
    print("Singing In - " + username)

    pass


def main():
    global proxy_timeout

    follow_channel_name = input("What channel should I follow? : ")

    accounts_csv_path = get_full_path("/data/accounts.csv")
    accounts_csv = pandas.read_csv(accounts_csv_path, sep=',', dtype="str")

    # define accounts.csv columns
    username_rows = accounts_csv.username
    password_rows = accounts_csv.password

    # go through every account in .csv
    for i, (username, password) in enumerate(zip(username_rows, password_rows)):
        print("--------------------------------")

        # change proxy
        run_driver(True)

        while sign_in(username, password) is False and proxy_timeout:
            print("\nTime expired, changing proxy...")
            print("Using previous account: [{}]\n".format(username))

            run_driver(True)

        print("[{}] Successfully signed in.".format(username))

        print("[{}] Trying to follow: [{}]".format(
            username, follow_channel_name))

        if follow_channel(follow_channel_name):
            accounts_csv.at[i, 'following_channel'] = follow_channel
            accounts_csv.at[i, 'used_proxy'] = current_proxy
            accounts_csv.to_csv(accounts_csv_path, sep=',',
                                index=False, index_label=False)

            print("[{}] Successfully followed: [{}]".format(
                username, follow_channel_name))
        else:
            accounts_csv.at[i, 'following_channel'] = "ERROR"
            accounts_csv.to_csv(accounts_csv_path, sep=',',
                                index=False, index_label=False)

            print("[{}] An error ocured while trying to follow: [{}]!!!".format(
                username, follow_channel_name))


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
                '--proxy-server=socks5://' + current_proxy)

            print("New Proxy: " + current_proxy)
        else:
            print("No more proxies!!!")
            exit()

    chrome_driver_path = get_full_path("/drivers/chromedriver")

    driver = webdriver.Chrome(options=chrome_options,
                              executable_path=chrome_driver_path)
    driver.set_window_size(880, 720)
    driver.set_window_position(0, 0)
    driver.set_page_load_timeout(20)


def find_available_proxy():
    proxies_csv_path = get_full_path("/data/proxies.csv")
    proxies_csv = pandas.read_csv(proxies_csv_path, sep=',', dtype="str")

    # define proxies.csv columns
    proxy_rows = proxies_csv.proxy
    status_rows = proxies_csv.status

    # go through every proxy in .csv and check if it is available to use
    for i, (proxy, status) in enumerate(zip(proxy_rows, status_rows)):
        if i == len(proxy_rows) - 1 and status == "USED":
            return False
        elif pandas.isnull(status):
            proxies_csv.at[i, 'status'] = "USED"
            proxies_csv.to_csv(proxies_csv_path, sep=',',
                               index=False, index_label=False)
            return proxy


def exit():
    stop_driver()
    input("Pres 'Enter' to Exit")
    sys.exit()


def stop_driver():
    global driver

    if driver is None:
        pass
    else:
        driver.quit()
        driver = None


def get_full_path(file_path):
    return Path("{}{}".format(os.getcwd(), file_path))


if __name__ == '__main__':
    main()
    print("--------------------------------")
    print("No more accounts!!!")
    exit()
