#!/usr/bin/env python
import csv
import sys
import random
import time
import json
import os
import logging
from collections import defaultdict
import urllib
import urllib.parse
import urllib.request
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
from fake_useragent import UserAgent
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WINDOW_SIZE = "1920,1080"
IMPLICIT_WAIT = 300
EXPLICIT_WAIT = 300

first_url = "https://www.thumbtack.com/more-services"
search_url = "https://www.thumbtack.com{0}?category_pk={1}&force_browse=1&is_zip_code_changed=true&zip_code="
searchPK_url = "https://hercule.thumbtack.com/search?query={}&prefix=1&limit=1&v=0&includeTest=true"
result_file = "./results/thumbtack.csv"
image_folder = "./results/images/"
url_file = "./resources/thumbtack_urls.txt"
categories_file = "./resources/thumbtack_categories.csv"

test = 5000000

chrome_path = r''
if os.name == 'nt':
    chrome_path = r'./resources/win/chromedriver.exe'
else:
    chrome_path = r'./resources/linux/chromedriver'
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

categories_list = defaultdict(list)
categories_url_list = {}
##################################
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("logfile.log", "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    

sys.stdout = Logger()
sys.stderr = Logger() 

##################################


def get_filename(title, category_pk):
    filename = ""
    filename = category_pk + "_" + "".join(x for x in title if x.isalnum())
    filename = filename + ".jpg"
    return filename
##################################


def download_image(imgUrl, filename):
    urllib.request.urlretrieve(imgUrl, image_folder + filename)
##################################


def get_categories_from_pk(category_pk):
    result = []
    with open(categories_file, 'r') as input_file:
        reader = csv.reader(input_file, quotechar='"', delimiter=",",
                            quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for line in reader:
            cat, subcat, pk = line
            if category_pk == pk:
                list1 = []
                list1.append(cat)
                list1.append(subcat)
                result.append(list1)
    return result
##################################


def get_all_categories():
    url = first_url
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
    categories = soup.select('div[id*="category"]')
    for category in categories:
        # print(category)
        cat = category.select(
            'h3[class*="title"]')[0].get_text().replace('\n', '').strip()
        # print(header)
        links = category.select('a[class*="category"]')
        for link in links:
            href = link.attrs["href"]
            subcat = link.get_text().strip()
            # print(temp)
            categories_list[subcat].append(cat)
            categories_url_list[subcat] = href
            #categories_list[subcat]["href"] = href
    # print(categories_list)
#######################


def get_pk(category):
    url = searchPK_url.format(urllib.parse.quote_plus(category))
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
    json_data = json.loads(response.text)
    return json_data[0]["PK"]

#######################


def append_to_file(datarow):
    with open(result_file, 'a', encoding='utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(datarow)
#######################


def parse(url):
    print(url)
    category_pk = url.split("category_pk=")[1].split("&lp")[0]
    driver = webdriver.Chrome(chrome_path, chrome_options=options)
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        main = soup.find("main")
        mt1 = soup.select('div[class="mt1"]')
        title = ""
        rating = ""
        votes = ""
        if mt1:
            title = mt1[0].previous_sibling('div')[0].get_text()
            rating1 = mt1[0].select('span[class*="numericRating"]')
            if rating1:
                rating = rating1[0].get_text()
            votes1 = mt1[0].select('span[class*="numberOfReviews"]')
            if votes1:
                votes = votes1[0].get_text()
            if votes:
                votes = votes.split("(")[1].split(")")[0]
        intro = ""
        intro1 = main.select('span[class="b"]')
        if intro1:
            intro = intro1[0].parent.get_text()
        image_url = ""
        image_url1 = main.select('div[style*="background-image"]')
        if image_url1:
            image_url = image_url1[0].attrs["style"].split("(")[1].split(")")[
                0]
        aside = soup.find("aside")
        cost = ""
        cost1 = aside.select('div[class*="tp-title-5"]')
        if cost1:
            cost = cost1[0].get_text()
        social_media = []
        social_media_node = soup.find('p', string='Social media')
        if social_media_node:
            next_nodes = social_media_node.find_next('p').findAll('a')
            for nodes in next_nodes:
                social_media.append(nodes.attrs["href"])

        datarow = []
        # datarow.append(category_pk)
        datarow.append(title)
        filename = get_filename(title, category_pk)
        datarow.append("=HYPERLINK(" +"\"" + image_folder + filename + "\"" + ")")
        datarow.append(rating.replace("\n", ""))
        datarow.append(votes.replace("\n", ""))
        datarow.append(intro.replace("\n", "").replace("  ", " "))
        datarow.append(",".join(social_media).replace("\n", ""))
        datarow.append(cost.replace("\n", ""))
        download_image(image_url, filename)
        list1 = get_categories_from_pk(category_pk)
        for list2 in list1:
            temp_row = list2 + datarow
            append_to_file(temp_row)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
    finally:
        driver.quit()
#######################


def crawl(url):
    driver = webdriver.Chrome(chrome_path, chrome_options=options)
    try:
        driver.get(url)
        time.sleep(3)
        driver.implicitly_wait(0)
        try:
            see_more = driver.find_elements_by_xpath(
                '//button[text()="See More"]')
            while see_more:
                see_more[0].click()
        except StaleElementReferenceException as e:
            see_more = driver.find_elements_by_xpath(
                '//button[text()="See More"]')
            while see_more:
                see_more[0].click()
        time.sleep(random.randint(1, 2))
        links = driver.find_elements_by_xpath(
            '//button/span[text()="View Profile"]')
        driver.implicitly_wait(IMPLICIT_WAIT)
        # print(len(links))
        # time.sleep(10)
        action = ActionChains(driver)
        for link in links:
            action.move_to_element(link).perform()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links = soup.select('a[href*="category_pk"]')
        for link in links:
            url1 = "https://www.thumbtack.com" + link.attrs["href"]
            parse(url1)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
    finally:
        driver.quit()


#######################
if __name__ == "__main__":
    with open(url_file, 'r') as input_file:
        for line in input_file:
            url = line.rstrip()
            crawl(url)
