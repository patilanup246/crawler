#!/usr/bin/env python
import csv
import json
import urllib3
import requests
from bs4 import BeautifulSoup
#from selenium import webdriver
#from selenium.webdriver.remote.webdriver import WebDriver

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WINDOW_SIZE = "1920,1080"
IMPLICIT_WAIT = 300
EXPLICIT_WAIT = 300
RESULT_FILE = "./results/instagram.csv"
USERS_LIST = "./resources/followers.lst"

#@options = webdriver.ChromeOptions()
#'options.add_argument("--window-size=%s" % WINDOW_SIZE)
#'options.add_argument("--start-maximized")
#'options.add_argument('--headless')

######################################


def parse(url, account):
    # print(url)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    response = requests.get(url, headers=headers, verify=False)
    # print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup)
    script = soup.find('script', type='application/ld+json')
    #data = json.loads(soup.find('script', type='application/ld+json').text)
    email = ""
    if script:
        data = json.loads(script.text)
        if data:
            if 'description' in data:
                desc = data['description'].replace("\n", "")
                list2 = desc.split(' ')
                for item in list2:
                    if '@' in item:
                        email = item
            if 'email' in data:
                email = data['email']
    datarow = []
    datarow.append(account)
    datarow.append(email.replace("\n", ""))
    datarow.append(url)
    append_to_file(datarow)
######################################


def append_to_file(datarow):
    with open(RESULT_FILE, 'a', encoding='utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(datarow)


######################################
if __name__ == "__main__":
    with open(USERS_LIST, 'r') as input_file:
        for line in input_file:
            user_name = line.replace("\n", "")
            parse(
                "https://www.instagram.com/{0}/".format(user_name), user_name)
