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

########################################
""" crawl the zillow website to get data"""


def crawler(zipcode):
    # start with page 0
    driver = webdriver.Chrome(chrome_path, options=options)
    url = SRC_URL.format(zipcode) + "1"
    print(url)
    sys.stdout.flush()
    try:
        driver.get(url)
        time.sleep(10)
        #wait = WebDriverWait(driver, 10)
        driver.implicitly_wait(IMPLICIT_WAIT)
        # parsing the text
        page_count = 0  # page counting
        while True:
            url = driver.current_url
            print(url)
            sys.stdout.flush()
            elem = driver.find_element_by_xpath("//*")
            source_code = elem.get_attribute("outerHTML")
            print(len(source_code))
            while len(source_code) < 180000:
                driver.quit()
                time.sleep(200)
                driver.get(url)
                time.sleep(10)
                elem = driver.find_element_by_xpath("//*")
                source_code = elem.get_attribute("outerHTML")
                print(len(source_code))
            page_count = page_count + 1
            soup = BeautifulSoup(driver.page_source, 'html.parser')
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
                datarow.append(str(page_count))
                datarow.append(name)
                datarow.append(phone)
                datarow.append(rating)
                datarow.append(reviews)
                datarow.append(office)
                append_to_file(datarow)
                time.sleep(random.randint(1, 2))
            # click on Next button if it exist:
            action = ActionChains(driver)
            next_buttons = driver.find_elements_by_xpath('//a[text()="' + str(page_count +1) + '"]')
            if next_buttons and len(next_buttons) > 0:
                next_button = next_buttons[0]
                action.move_to_element(next_button).perform()
                #next_button.send_keys("\n")
                next_button.click()
                time.sleep(10)
            else:  # there is no more page, quit
                break
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
    finally:
        driver.quit()


###########################################
""" main function """
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('action', help='download, parse, crawl')
    argparser.add_argument('--zipcode', nargs='?',
                           help='get only 1 single zip code, usage: --zipcode <zipcode>')
    argparser.add_argument('--zipcode_file', nargs='?',
                           help='get list of zip codes from a local file, usage: --zipcode_file <filename>')
    argparser.add_argument('--output', nargs='?',
                           help='write output to a local file, by default it is output.csv, usage: --output <filename>')
    args = argparser.parse_args()
    action = args.action
    zipcode = args.zipcode
    zipcode_file = args.zipcode_file
    output = args.output
    print("action: %s" % (action))
    print("zipcode:", zipcode)
    print("zipcode_file:", zipcode_file)
    print("output:", output)
    sys.stdout.flush()
    if not output is None:
        RESULT_FILE = output
    if action == "download":
        if not zipcode is None:
            download(zipcode)
        if not zipcode_file is None:
            with open(zipcode_file, 'r') as input_file:
                for line in input_file:
                    if line.isdigit():
                        download(line)
    if action == "parse":
        parse()
    if action == "crawl":
        if not zipcode is None:
            crawler(zipcode)
        if not zipcode_file is None:
            with open(zipcode_file, 'r') as input_file:
                for line in input_file:
                    zipcode = line.rstrip()
                    if zipcode.isdigit():
                        crawler(zipcode)
