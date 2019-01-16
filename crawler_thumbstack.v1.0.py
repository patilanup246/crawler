#!/usr/bin/env python
import requests, csv, sys, re, argparse, random,time
import time, glob, urllib3, json, os
import urllib.parse
from bs4 import BeautifulSoup
from collections import defaultdict
from selenium import webdriver
#from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WINDOW_SIZE = "1920,1080"
IMPLICIT_WAIT = 300
EXPLICIT_WAIT = 300

first_url = "https://www.thumbtack.com/more-services"
search_url = "https://www.thumbtack.com{0}?category_pk={1}&force_browse=1&is_zip_code_changed=true&zip_code="
searchPK_url = "https://hercule.thumbtack.com/search?query={}&prefix=1&limit=1&v=0&includeTest=true"
result_file = "./results/thumbtack.csv"
url_file = "./thumbtack_urls.txt"

test = 5000000

options = webdriver.ChromeOptions()
options.add_argument("--window-size=%s" % WINDOW_SIZE)
options.add_argument("--start-maximized")
options.add_argument('--headless')

categories_list = defaultdict(list) 
categories_url_list = {}
def getAllCategories():
	url = first_url
	#print(url)
	sys.stdout.flush()
	headers= {
		  'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		  'accept-encoding':'gzip, deflate, sdch, br',
		  'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
		  'cache-control':'max-age=0',
		  'upgrade-insecure-requests':'1',
		  'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	}
	response = requests.get(url,headers=headers, verify=False)
	#print(response.status_code)
	soup = BeautifulSoup(response.text, 'html.parser')
	categories = soup.select('div[id*="category"]')
	for category in categories:
		#print(category)
		cat = category.select('h3[class*="title"]')[0].get_text().replace('\n','').strip()
		#print(header)
		links = category.select('a[class*="category"]')
		for link in links:
			href = link.attrs["href"]
			subcat= link.get_text().strip()
			#print(temp)
			categories_list[subcat].append(cat) 
			categories_url_list[subcat] =href 
			#categories_list[subcat]["href"] = href 
	#print(categories_list)
#######################
def getPK(category):
	url = searchPK_url.format(urllib.parse.quote_plus(category))
	#print(url)
	sys.stdout.flush()
	headers= {
		  'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		  'accept-encoding':'gzip, deflate, sdch, br',
		  'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
		  'cache-control':'max-age=0',
		  'upgrade-insecure-requests':'1',
		  'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	}
	response = requests.get(url,headers=headers, verify=False)
	#print(response.status_code)
	json_data = json.loads(response.text)
	return json_data[0]["PK"]

#######################
def appendToFile(datarow):
    with open(result_file, 'a', encoding = 'utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(datarow)
#######################
def parse(url, zipcode):
    url = url + zipcode
    driver = webdriver.Chrome(chrome_options=options)
    try:
        driver.get(url)
        time.sleep(2)
        driver.implicitly_wait(0)
        while (driver.find_elements_by_xpath('//button[text()="See More"]')):
            driver.find_elements_by_xpath('//button[text()="See More"]')[0].click()
        driver.implicitly_wait(IMPLICIT_WAIT)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #print(soup)
        experts = soup.select('div[class="ph3 s_ph0"]')
        for expert in experts:
            datarow=[]
            datarow.append("")
            datarow.append(url)
            name = expert.select('div[class*="black hover-blue"]')[0].get_text()
            datarow.append(name)
            rating = ""
            if (len(expert.select('span[class*="StarRating-numericRating"]'))>0): 
                rating= expert.select('span[class*="StarRating-numericRating"]')[0].get_text()
            datarow.append(rating)
            review= ""
            if (len(expert.select('span[class*="StarRating-numberOfReviews"]'))>0): 
                review= expert.select('span[class*="StarRating-numberOfReviews"]')[0].get_text()
            datarow.append(review)
            cost = ""
            if (len(expert.select('div[data-test="pro-cost-estimate"]'))>0): 
                temp = expert.select('div[data-test="pro-cost-estimate"]')[0].findAll('div')
                cost = temp[0].get_text()
            datarow.append(cost)
            appendToFile(datarow)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    finally:
        driver.quit()
#######################
if __name__=="__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('action',help= 'generateURL, parse, crawl, test')
    argparser.add_argument('--zipcode',nargs= '?', help = 'crawl --zipcode <zipcode>')
    argparser.add_argument('--file',nargs= '?', help = 'crawl --file <filename>')
    argparser.add_argument('--output',nargs= '?', help = 'crawl --output <filename>')
    argparser.add_argument('--category',nargs= '?', help = 'crawl --category <category>')
    args = argparser.parse_args()
    action = args.action
    zipcode= args.zipcode
    category= args.category
    file= args.file
    output= args.output
    print ("action: %s"%(action))
    print ("zipcode:",zipcode)
    print ("file:",file)
    print ("output:",output)
    sys.stdout.flush()
    if not output is None:
        result_file = output
    if "test" == action:
        getAllCategories()
        for keys, values in categories_list.items():
            print(keys,end=";")
            for e in values:
                print(e,end="/")
            print("\n")
    if "generateURL" == action:
        getAllCategories()
        for keys, values in categories_list.items():
            cat = keys
            cat_url = categories_url_list[keys]
            cat_pk = getPK(cat)
            url = search_url.format(cat_url,cat_pk)
            list1=[]
            list1.append(cat)
            list1.append("/".join(values))
            list1.append(url)
            print(";".join(list1))
    if "parse" == action:
        parse("https://www.thumbtack.com/k/bathroom-remodeling/near-me/?category_pk=219264413294461288&force_browse=1&is_zip_code_changed=true&zip_code=","10002")
 #       getAllCategories()
 #       with open(url_file, 'r') as input_file:
 #           count = 1
 #           for line in input_file:
 #               count += 1
 #               url = line.rstrip()
 #               parse(url, "10001")
 #               if(count==test):
 #                   break
    if "crawl" == action:
        if not zipcode is None:
                crawler(zipcode)

