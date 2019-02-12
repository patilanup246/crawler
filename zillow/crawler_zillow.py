#!/usr/bin/env python
import csv
import sys
import re
import argparse
import time
import glob
import random
import urllib3
import requests
import logging
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SRC_URL = "https://www.zillow.com/{0}/real-estate-agent-reviews/?page="
OUTPUT_FOLDER = "raw"
RESULT_FILE = "output.csv"

file_seperator = ""
if sys.platform == 'linux':
    file_seperator = "/"
elif sys.platform == 'darwin':
    file_seperator = "/"
else:
    file_seperator = "\\"

########################################
def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='w')
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
""" download data into local file """
def download(zipcode):
    i = 0
    while True:
        i += 1
        url = SRC_URL.format(zipcode) + str(i)
        logger.info(url)
        sys.stdout.flush()
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        response = requests.get(url, headers=headers, verify=False)
        logger.info(response.status_code)
        logger.info(len(response.content))
        if len(response.content) < 180000:
            break
        sys.stdout.flush()
        csv_file = str(zipcode) + str("_") + str(i)+".html"
        data_file = OUTPUT_FOLDER + file_seperator + csv_file
        with open(data_file, "a", encoding="utf-8") as output:
            output.write(response.text)
        time.sleep(10)

########################################
""" parse the data from html file in OUTPUT_FOLDER"""
def parse():
    file_list = glob.glob(OUTPUT_FOLDER+ file_seperator + "*.html")
    file_list.sort()
    # logger.info(file_list)
    header = ["Zip Code", "Page", "Name",
              "Phone", "Rating", "Reviews", "Office"]
    with open(RESULT_FILE, 'w', encoding='utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(header)
        for file1 in file_list:
            filename1 = file1.split(file_seperator)[-1]
            logger.info(filename1)
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
                    datarow.append(page)
                    datarow.append(name)
                    datarow.append(phone)
                    datarow.append(rating)
                    datarow.append(reviews)
                    datarow.append(office)
                    # logger.info(datarow)
                    writer.writerow(datarow)


########################################
""" append data to file"""
def append_to_file(datarow):
    with open(RESULT_FILE, 'a', encoding='utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(datarow)


########################################
""" crawl the zillow website to get data"""
def crawler(zipcode):
    i = 0
    break_time = 300
    while True:
        i += 1
        url = SRC_URL.format(zipcode) + str(i)
        logger.info(url)
        sys.stdout.flush()
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        response = requests.get(url, headers=headers, verify=False)
        logger.info("Response code: " + str(response.status_code))
        logger.info("Response content size: " + str(len(response.content)))
        #if it is a wrong url
        if len(response.content) < 180000 and len(response.content) > 10000:
            break
        #if it is the captcha check, we take a break
        while len(response.content) < 10000: 
            break_time = break_time + int(break_time*0.1)
            logger.info("We take a break "+ str(break_time) + " seconds")
            time.sleep(break_time)
            response = requests.get(url, headers=headers, verify=False)
            logger.info("Response code: " + str(response.status_code))
            logger.info("Response content size: " + str(len(response.content)))
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
    logger.info("action: " +str(action))
    logger.info("zipcode:" + str(zipcode))
    logger.info("zipcode_file: " + str(zipcode_file))
    logger.info("output: " +str(output))
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
