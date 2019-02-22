#!/usr/bin/env python
import csv
import sys
import re
import os
import argparse
import time
import glob
import random
import urllib3
import requests
import logging
from fake_useragent import UserAgent
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

######################################
""" constans"""
WINDOW_SIZE = "1920,1080"
IMPLICIT_WAIT = 300
EXPLICIT_WAIT = 300

FILE_SEPARATOR = ""
if sys.platform == 'linux':
    FILE_SEPARATOR = "/"
elif sys.platform == 'darwin':
    FILE_SEPARATOR = "/"
else:
    FILE_SEPARATOR = "\\"

SRC_URL = "https://www.zillow.com/{0}/real-estate-agent-reviews/?page="
OUTPUT_FOLDER = "raw"
RESULT_FILE = "results" + FILE_SEPARATOR + "result.csv"
LOG_FILE = "logs" + FILE_SEPARATOR + "out.log"

######################################
""" configure stream logger """


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
    # level=logging.DEBUG,
    level=logging.INFO,
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
"""setting up chromedriver"""

chrome_path = r''
if sys.platform == 'linux':
    chrome_path = r'./resources/chromedriver/linux/chromedriver'
elif sys.platform == 'darwin':
    chrome_path = r'./resources/chromedriver/mac/chromedriver'
else:
    chrome_path = r'./resources/chromedriver/win/chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument("--window-size=%s" % WINDOW_SIZE)
options.add_argument("--start-maximized")
options.add_argument('--headless')
options.add_argument("--disable-extensions")
options.add_argument("test-type")

# add random user agent
ua = UserAgent()
user_agent = ua.random
options.add_argument(f'user-agent={user_agent}')

########################################
""" download data into local file """


def download(zipcode):
    i = 0
    while True:
        i += 1
        url = SRC_URL.format(zipcode) + str(i)
        print(url)
        sys.stdout.flush()
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
            'user-agent': str(ua.random)
        }
        response = requests.get(url, headers=headers, verify=False)
        print(response.status_code)
        print(len(response.content))
        if len(response.content) < 180000:
            break
        sys.stdout.flush()
        csv_file = str(zipcode) + str("_") + str(i)+".html"
        data_file = OUTPUT_FOLDER + FILE_SEPARATOR + csv_file
        with open(data_file, "a", encoding="utf-8") as output:
            output.write(response.text)
        time.sleep(10)


########################################
""" parse the data from html file in OUTPUT_FOLDER"""


def parse():
    file_list = glob.glob(OUTPUT_FOLDER + FILE_SEPARATOR + "*.html")
    file_list.sort()
    # print(file_list)
    header = ["Zip Code", "Page", "Name",
              "Phone", "Rating", "Reviews", "Office"]
    with open(RESULT_FILE, 'w', encoding='utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(header)
        for file1 in file_list:
            filename1 = file1.split(FILE_SEPARATOR)[-1]
            print(filename1)
            sys.stdout.flush()
            zipcode = filename1.split("_")[0]
            page = filename1.split("_")[1].split(".")[0]
            with open(file1, 'r', encoding='utf-8') as html_file:
                soup = BeautifulSoup(html_file, 'html.parser')
                blocks = soup.select('div[data-test-id="ldb-boards-results"]')
                rows = blocks[0].select('div[data-test-id*="ldb-board"]')
                for row in rows:
                    name = ""
                    phone = ""
                    rating = ""
                    reviews = ""
                    office = ""
                    # agent = row.select('div[class="ldb-board-inner"]')[0]
                    agent = row.select(
                        'div[class="ldb-col-a"]')[0].select('div[class="ldb-board-inner"]')[0]
                    name = agent.select(
                        'p[class*="ldb-contact-name"]')[0].get_text()
                    phone = agent.select(
                        'p[class*="ldb-phone-number"]')[0].get_text()
                    try:
                        rating = agent.select(
                            'span[class*="zsg-rating"]')[0]['title']
                    except:
                        pass
                    try:
                        reviews = agent.select(
                            'a[class*="zsg-link zsg-fineprint"]')[0].get_text()
                    except:
                        pass

                    try:
                        office = row.select('div[class="ldb-col-b"]')[0].select('div[class="ldb-board-inner"]')[
                            0].select('p[class="ldb-business-name"]')[0].get_text()
                        office = re.sub(r'[\ \n]{2,}', '', office)
                        office = re.sub(r'\n', '', office)
                    except:
                        pass
                    datarow = []
                    datarow.append(zipcode)
                    datarow.append(page)
                    datarow.append(name)
                    datarow.append(phone)
                    datarow.append(rating)
                    datarow.append(reviews)
                    datarow.append(office)
                    # print(datarow)
                    writer.writerow(datarow)


########################################
""" append data to file"""


def append_to_file(datarow):
    with open(RESULT_FILE, 'a', encoding='utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(datarow)


########################################

def request_data(url):
    url = "https://www.zillow.com/homes/for_sale/1-_beds/2-_baths/0-900000_price/40-796_mp/12m_days/globalrelevanceex_sort/40.506782,-79.958861,40.489438,-79.985709_rect/14_zm/"
    driver = webdriver.Chrome(chrome_path, options=options)
    try:
        driver.get(url)
        time.sleep(10)
        #wait = WebDriverWait(driver, 10)
        elems = driver.find_elements_by_xpath("//*[@id='map-result-count-message']/h2")
        print(driver.page_source)
        if elems and len(elems)>0:
            print(elems[0])
    except Exception as e:
        print(e)


###########################################
if __name__ == "__main__":
    request_data(" ")
