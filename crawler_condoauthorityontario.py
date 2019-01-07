#!/usr/bin/env python
import requests, csv, sys, re, argparse, random

import time, glob, urllib3, urllib
from bs4 import BeautifulSoup
from selenium import webdriver
#from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

src_url = "https://www.condoauthorityontario.ca/en-US/public-registry/results/?searchby=legalname&searchregion=Ottawa-Carleton&lgnumber="
#src_url = "https://www.condoauthorityontario.ca/en-US/public-registry/details/?id=2bcda817-1988-e711-8122-480fcff42871&searchby=legalname&searchregion=Ottawa-Carleton&total=1&lgnumber="
result_file = "./results/condoauthorityontario.csv"

WINDOW_SIZE = "1920,1080"
IMPLICIT_WAIT = 30
EXPLICIT_WAIT = 30

options = webdriver.ChromeOptions()
options.add_argument("--window-size=%s" % WINDOW_SIZE)
options.add_argument("--start-maximized")
options.add_argument('--headless')

def parse(code):
    url = src_url + code
    print(url)
    sys.stdout.flush()
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    #driver.implicitly_wait(IMPLICIT_WAIT)
    time.sleep(random.randint(10,14))
    driver.find_elements_by_xpath("//div[@id='boardOfDirectorSubgrid']")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    title = ""
    address = ""
    voting = ""
    cao_name = ""
    director_list = [] 
    #title
    if len(soup.select('input[title*="Name Assigned to the Corporation"]'))>0:
        title = soup.select('input[title*="Name Assigned to the Corporation"]')[0].attrs["value"]
    #address
    if len(soup.select('input[name*="streetname"]'))>0:
        add1 = soup.select('input[name*="streetname"]')[0].attrs["value"]
        address +=  " " + add1
    if len(soup.select('input[name*="unitname"]'))>0:
        add1 = soup.select('input[name*="unitname"]')[0].attrs["value"]
        address +=  " " + add1
    if len(soup.select('input[name*="city"]'))>0:
        add1 = soup.select('input[name*="city"]')[0].attrs["value"]
        address +=  " " + add1
    if len(soup.select('input[name*="province"]'))>0:
        add1 = soup.select('input[name*="province"]')[0].attrs["value"]
        address +=  " " + add1
    if len(soup.select('input[name*="postalcode"]'))>0:
        add1 = soup.select('input[name*="postalcode"]')[0].attrs["value"]
        address +=  " " + add1
    if len(soup.select('input[name*="country"]'))>0:
        add1 = soup.select('input[name*="country"]')[0].attrs["value"]
        address +=  " " + add1
    #voting
    if len(soup.select('input[name*="voting"]'))>0:
        voting= soup.select('input[name*="voting"]')[0].attrs["value"]

    #board_of_director
    if len(soup.select('div[id="boardOfDirectorSubgrid"]'))>0:
        board = soup.select('div[id="boardOfDirectorSubgrid"]')[0]
        paginations = board.select('ul[class="pagination"]')
        if len(paginations) > 0:
            pages = paginations[0].find_all('li')
            
            no_of_pages = 0
            if len(pages) > 0:
                no_of_pages = len(pages) - 2
                for i in range(0,no_of_pages):
                    rows= board.select('tr[data-entity*="contactcorporation"]')
                    for row in rows:
                        cols = row.find_all('td')
                        director = []
                        director.append(cols[0].get_text())
                        director.append(cols[1].get_text())
                        director_name = ""
                        director_name = " ".join(director)
                        if director_name != "":
                            director_list.append(director_name) 
                    driver.find_elements_by_xpath("//div[@id='boardOfDirectorSubgrid']//a")[-1].click()
                    time.sleep(5)
        else:
            rows= board.select('tr[data-entity*="contactcorporation"]')
            for row in rows:
                cols = row.find_all('td')
                director = []
                director.append(cols[0].get_text())
                director.append(cols[1].get_text())
                director_name = ""
                director_name = " ".join(director)
                if director_name != "":
                    director_list.append(director_name) 

    #condo management individuals
    condo_managers = []
    if len(soup.select('div[id="condoManagersSubgrid"]'))>0:
        board = soup.select('div[id="condoManagersSubgrid"]')[0]
        rows = board.select('tr[data-entity*="contactcorporation"]')
        for row in rows:
            cols = row.find_all('td')
            manager = []
            manager.append(cols[0].get_text())
            manager.append(cols[1].get_text())
            manager_name= ""
            manager_name = " ".join(manager)
            if manager_name!= "":
                condo_managers.append(manager_name) 
    #cao_name
    if len(soup.select('td[data-attribute="cao_name"]'))>0:
        cao_name= soup.select('td[data-attribute="cao_name"]')[0].get_text()
    
    datarow=[]
    datarow.append(code)
    datarow.append(title)
    datarow.append(address)
    datarow.append(voting)
    datarow.append(cao_name)
    datarow.append(";".join(director_list).replace("  "," "))
    datarow.append(";".join(condo_managers).replace("  "," "))
    print(datarow)
    sys.stdout.flush()
    appendToFile(datarow)
    driver.quit()
def appendToFile(datarow):
    with open(result_file, 'a', encoding = 'utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(datarow)
def crawler():
    i = 150
    while True:
        url = src_url + str(i)
        i +=  30
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
        print(len(response.content))
        with open("condo.html","w") as output:
            output.write(str(response.text))
        if len(response.content) < 400000:
            break
        sys.stdout.flush()
        #parsing the text
        soup = BeautifulSoup(response.text, 'html.parser')
        blocks = soup.select('div[class*="businessName"]')
        for block in blocks:
            title=block.get_text()
            if  title[0].isdigit() == False:
                continue 
            link=""
            href=""
            if len(block.select('a[class*="lemon--a"]')) > 0:
                href = block.select('a[class*="lemon--a"]')[0]
                link = href.attrs["href"]
            parse("https://www.yelp.com" + link)
            #print(href)
            #print(datarow)
            #appendToFile(datarow)
            time.sleep(random.randint(1,3))
        time.sleep(random.randint(5,10))
if __name__=="__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('action',help= ' parse, crawl')
    argparser.add_argument('--output',nargs= '?', help = 'crawl --output <filename>')
    args = argparser.parse_args()
    action = args.action
    output= args.output
    print ("action: %s"%(action))
    print ("output:",output)
    sys.stdout.flush()
    if not output is None:
        result_file = output
    if "parse" == action:
        parse(str(82))
    if "crawl" == action:
        for i in range(80,100):
            parse(str(i))
