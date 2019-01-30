#!/usr/bin/env python
import csv
import json
import re
import urllib3
import lepl.apps.rfc3696
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

# @options = webdriver.ChromeOptions()
# 'options.add_argument("--window-size=%s" % WINDOW_SIZE)
# 'options.add_argument("--start-maximized")
# 'options.add_argument('--headless')

######################################

EMAIL_VALIDATOR = lepl.apps.rfc3696.Email()
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

######################################

def get_email_from_text(str1):
    #print(str1)
    email_result = ""
    list2 = []
    tempStr = ""
    count = 0
    for e in str1:
        count = count + 1
        if (re.sub('[ -~]', '', e)) == "":
            #do something here
            tempStr += e
        elif tempStr != "":
            list2.append(tempStr)
            tempStr = ""
        if count == len(str1) and tempStr != "":
            list2.append(tempStr)
            tempStr = ""
    for i in list2:
        if EMAIL_REGEX.match(i):
            email_result = i
            break
    return email_result

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
            if 'email' in data:
                email = get_email_from_text(data['email']) 
            if email == "":
                if 'description' in data:
                    desc = data['description'].replace("\n", "")
                    list2 = desc.split(' ')
                    for item in list2:
                        if '@' in item: 
                            email = get_email_from_text(item) 
    if email != "":
        if EMAIL_REGEX.match(email):
            datarow = []
            datarow.append(account)
            datarow.append(email.replace("\n", ""))
            datarow.append(url)
            append_to_file(datarow)
######################################


def append_to_file(datarow):
    try:
        with open(RESULT_FILE, 'a', encoding='utf-8') as output:
            writer = csv.writer(output, delimiter=",", lineterminator="\n")
            writer.writerow(datarow)
    except:
        pass


######################################
if __name__ == "__main__":
    with open(USERS_LIST, 'r') as input_file:
        for line in input_file:
            user_name = line.replace("\n", "")
            parse(
                "https://www.instagram.com/{0}/".format(user_name), user_name)
