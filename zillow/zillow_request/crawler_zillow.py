#!/usr/bin/env python
import csv
import sys
import re
import argparse
import time
import random
import urllib3
import requests
import logging
from bs4 import BeautifulSoup
from itertools import cycle

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FILE_SEPARATOR = ""
if sys.platform == 'linux':
    FILE_SEPARATOR = "/"
elif sys.platform == 'darwin':
    FILE_SEPARATOR = "/"
else:
    FILE_SEPARATOR = "\\"

SRC_URL = "https://www.zillow.com/{0}/real-estate-agent-reviews/?page="
OUTPUT_FOLDER = "raw"
RESULT_FILE = "results" + FILE_SEPARATOR + "output.csv"
LOG_FILE = "logs" + FILE_SEPARATOR + "out.log"
PROXY_FILE = "resources" + FILE_SEPARATOR + "proxy.txt"
PROXY_ENABLED = False
BREAK_TIME = 0
########################################


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(LOG_FILE, mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger


logger = setup_custom_logger('zillow')
########################################
""" get proxy from file """


def get_proxies():
    proxies = set()
    with open(PROXY_FILE, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            temp = line.rstrip().split(':')
            if temp and len(temp) > 0:
                # if it is normal proxy, no username and password
                if len(temp) == 2:
                    proxies.add(line.rstrip())
                # if it is proxy with password, in format ip:port:username:password
                elif len(temp) == 4:
                    ip = temp[0]
                    port = temp[1]
                    username = temp[2]
                    password = temp[3]
                    proxy = username + ":" + password + "@" + ip + ":" + port
                    proxies.add(proxy)
    return proxies


########################################
""" append data to file"""


def append_to_file(datarow):
    with open(RESULT_FILE, 'a', encoding='utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(datarow)


########################################
""" loop through the proxy and get the data --between 3046 bytes and 1000000 bytes """


def request_data(url):
    response = ""
    proxies1 = get_proxies()
    proxy_pool = cycle(proxies1)
    time_out = BREAK_TIME
    while True:
        try:

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, sdch, br',
                'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
                'cache-control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
            }
            if PROXY_ENABLED:
                proxy = next(proxy_pool)
                logger.info("Using proxy: " + proxy)
                response = requests.get(url, headers=headers, proxies={
                    "http": proxy, "https": proxy}, verify=False)
            else:
                response = requests.get(url, headers=headers, verify=False)
            logger.info("Response code: " + str(response.status_code))
            logger.info("Response content size: " + str(len(response.content)))
        except:
            logger.info("Skipipng proxy. Connection error")
            continue
        if response and len(response.content) < 10000:  # capcha check
            continue
        else:
            break
    return response


########################################
""" crawl the zillow website to get data"""


def crawler(zipcode):
    i = 0
    while True:
        i += 1
        url = SRC_URL.format(zipcode) + str(i)
        logger.info(url)
        sys.stdout.flush()
        response = request_data(url)
        # if it is the wrong url
        if len(response.content) < 180000 and len(response.content) > 10000:
            break
        sys.stdout.flush()
        # parsing the text
        soup = BeautifulSoup(response.text, 'html.parser')
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
            name = agent.select('p[class*="ldb-contact-name"]')[0].get_text()
            phone = agent.select('p[class*="ldb-phone-number"]')[0].get_text()
            try:
                rating = agent.select('span[class*="zsg-rating"]')[0]['title']
            except:
                pass
            try:
                reviews = agent.select(
                    'a[class*="zsg-link zsg-finelogger.info"]')[0].get_text()
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
            datarow.append(str(i))
            datarow.append(name)
            datarow.append(phone)
            datarow.append(rating)
            datarow.append(reviews)
            datarow.append(office)
            append_to_file(datarow)
            time.sleep(random.randint(1, 2))


###########################################
""" main function """
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('--zipcode', nargs='?',
                           help='get only 1 single zip code, usage: --zipcode <zipcode>')
    argparser.add_argument('--zipcode_file', nargs='?',
                           help='get list of zip codes from a local file, usage: --zipcode_file <filename>')
    argparser.add_argument('--output_file', nargs='?',
                           help='write output to a local file, by default it is output.csv, usage: --output_file <filename>')
    argparser.add_argument('--proxy_file', nargs='?',
                           help='the list of proxies: --proxy_file <filename>')
    args = argparser.parse_args()
    zipcode = args.zipcode
    zipcode_file = args.zipcode_file
    output_file = args.output_file
    proxy_file = args.proxy_file
    logger.info("zipcode:" + str(zipcode))
    logger.info("zipcode_file: " + str(zipcode_file))
    logger.info("output_file: " + str(output_file))
    logger.info("proxy_file: " + str(proxy_file))
    sys.stdout.flush()
    if not output_file is None:
        RESULT_FILE = output_file
    if not proxy_file is None:
        PROXY_ENABLED = True
        PROXY_FILE = proxy_file
    if not zipcode is None:
        crawler(zipcode)
    if not zipcode_file is None:
        with open(zipcode_file, 'r') as input_file:
            for line in input_file:
                zipcode = line.rstrip()
                if zipcode.isdigit():
                    crawler(zipcode)
