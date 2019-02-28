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
import html
import json
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
    if PROXY_ENABLED:
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
        if response and len(response.content) < 1000:  # capcha check
            continue
        else:
            break
    return response

########################################


def clean_data(str1):
    result = ""
    str1 = str1.replace("\r\n", "").replace("\n", "").replace("  "," ")
    for e in str1:
        if (re.sub('[ -~]', '', e)) == "":
            result += e
    result = html.unescape(result)
    return result

########################################


def parse(url, img_url):
    logger.info(url)
    sys.stdout.flush()
    response = request_data(url)
    sys.stdout.flush()
    # parsing the text
    date = ""
    caption = ""
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.select('script')
    if scripts and len(scripts) > 0:
        json_data = ""
        for script in scripts:
            if "@context" in script.get_text():
                json_data = script.get_text()
                break
        print("AAA")
        if json_data == "":
            for script in scripts:
                if "edge_media_to_caption" in script.get_text():
                    json_data2 = script.get_text()
                    print(json_data2)
                    break 
        
        if json_data != "":
            #json_data = clean_data(json_data)
            try:
                json_list = json.loads(json_data)
                date = json_list["uploadDate"][0:10]
                caption = clean_data(json_list["caption"])
            except Exception as e:
                logger.info("Cannot find any json")
                logger.info(e)
                #print(response.text)
                sys.stdout.flush()
                pass
    try:
        if date == "":
            datetime = soup.find('time')
            if datetime:
                date = datetime.attrs["datetime"][0:10]
    except:
        logger.info("Cannot find date in the <time>")
        pass
    try:
        if caption == "":
            comments = soup.select('.gElp9')
            if comments and len(comments) > 0:
                caption = clean_data(comments[0].get_text())
    except:
        logger.info("Cannot find caption in the comments")
        pass
    datarow = []
    datarow.append(date)
    datarow.append(caption)
    datarow.append(url)
    datarow.append(img_url)
    append_to_file(datarow)
    time.sleep(random.randint(1, 2))


###########################################
""" main function """
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('--url_file', nargs='?',
                           help='get list of instagram post urls, usage: --url_file <filename>')
    argparser.add_argument('--output_file', nargs='?',
                           help='write output to a local file, by default it is output.csv, usage: --output_file <filename>')
    argparser.add_argument('--proxy_file', nargs='?',
                           help='the list of proxies: --proxy_file <filename>')
    args = argparser.parse_args()
    url_file = args.url_file
    output_file = args.output_file
    proxy_file = args.proxy_file
    logger.info("url_file: " + str(url_file))
    logger.info("output_file: " + str(output_file))
    logger.info("proxy_file: " + str(proxy_file))
    sys.stdout.flush()
    if not output_file is None:
        RESULT_FILE = output_file
    elif not url_file is None:
        RESULT_FILE =  url_file + "_parsed.csv"
    if not proxy_file is None:
        PROXY_ENABLED = True
        PROXY_FILE = proxy_file
    if not url_file is None:
        with open(url_file, 'r') as input_file:
            next(input_file)
            for line in input_file:
                post_url = line.rstrip().split(",")[0]
                img_url = line.rstrip().split(",")[1]
                parse(post_url, img_url)
