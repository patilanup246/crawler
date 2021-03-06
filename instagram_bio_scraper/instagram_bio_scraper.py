#!/usr/bin/env python
import csv
import sys
import logging
import json
import re
import urllib3
import lepl.apps.rfc3696
import requests
import time
import random
import argparse
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
#from selenium import webdriver
#from selenium.webdriver.remote.webdriver import WebDriver

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WINDOW_SIZE = "1920,1080"
IMPLICIT_WAIT = 300
EXPLICIT_WAIT = 300
RESULT_FILE = "./results/instagram.csv"
USERS_LIST = "./resources/followers.lst"
LOG_FILE = "./logs/out.log"

# @options = webdriver.ChromeOptions()
# 'options.add_argument("--window-size=%s" % WINDOW_SIZE)
# 'options.add_argument("--start-maximized")
# 'options.add_argument('--headless')

######################################

EMAIL_VALIDATOR = lepl.apps.rfc3696.Email()
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
######################################


class StreamToLogger():
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    filename=LOG_FILE,
    filemode='a'
)

stdout_logger = logging.getLogger('STDOUT')
sl = StreamToLogger(stdout_logger, logging.INFO)
sys.stdout = sl

stderr_logger = logging.getLogger('STDERR')
sl = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = sl
######################################


def get_email_from_text(str1):
    # print(str1)
    email_result = ""
    list2 = []
    tempStr = ""
    count = 0
    for e in str1:
        count = count + 1
        if (re.sub('[ -~]', '', e)) == "":
            # do something here
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
    ua = UserAgent()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        #'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        'user-agent':str(ua.random)
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
    print(account, email, url)
    sys.stdout.flush()
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
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('--input_file', nargs='?', help='--input_file <filename>')
    argparser.add_argument('--output_file', nargs='?',
                           help='--output_file <filename>')
    args = argparser.parse_args()
    input_file = args.input_file
    output_file = args.output_file
    if output_file is not None:
        RESULT_FILE = output_file
    if input_file is not None:
        USERS_LIST = input_file 
 
    error_count = 0
    record_count = 0
    with open(USERS_LIST, 'r') as input_file:
        for line in input_file:
            user_name = line.replace("\n", "")
            try:
                parse(
                    "https://www.instagram.com/{0}/".format(user_name), user_name)
                record_count = record_count + 1
                print("Reading record counting: " + str(record_count) + "th record")
                time.sleep(random.randint(1, 2))
            except:
                error_count = error_count + 1
                print("Time to sleep " + str(error_count*300) + " seconds")
                sys.stdout.flush()
                time.sleep(error_count * 300)
                continue
