#!/usr/bin/env python
import requests, csv, sys, re, argparse, random,time
import time, glob, urllib3
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
src_url = "https://www.thumbstack.com/k/{}/near-me"
result_file = "./results/thumbtack.csv"

options = webdriver.ChromeOptions()
options.add_argument("--window-size=%s" % WINDOW_SIZE)
options.add_argument("--start-maximized")
#options.add_argument('--headless')

categories_list = defaultdict(list) 
def getAllCategories():
	url = first_url
	print(url)
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
	print(response.status_code)
	soup = BeautifulSoup(response.text, 'html.parser')
	categories = soup.select('div[id*="category"]')
	for category in categories:
		#print(category)
		cat = category.select('h3[class*="title"]')[0].get_text().replace('\n','').strip()
		#print(header)
		links = category.select('a[class*="category"]')
		for link in links:
			temp = link.attrs["href"]
			#print(temp)
			categories_list[temp].append(cat)
	#print(categories_list)

def appendToFile(datarow):
    with open(result_file, 'a', encoding = 'utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(datarow)

def crawler(category,zipcode):
	url = src_url.format(category)
	driver = webdriver.Chrome(chrome_options=options)
	driver.get(first_url)
	driver.implicitly_wait(IMPLICIT_WAIT)
	time.sleep(10)
	driver.get(url)
	driver.implicitly_wait(IMPLICIT_WAIT)
	time.sleep(10)
	driver.close()
if __name__=="__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('action',help= 'test, parse, crawl')
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
    if "parse" == action:
        parse()
    if "crawl" == action:
        if not zipcode is None:
                crawler("cabinet-installation",zipcode)

