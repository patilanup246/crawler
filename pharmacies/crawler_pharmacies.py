#!python
from selenium import webdriver
import requests
import time, sys, os
import codecs
from io import open

url='https://biopharmguy.com/links/'

test=False
stop=10
csvfile="page"
time_out=10
######################################################
folder="./raw/biopharm/"
delim=","
quotes="\""
newline="\n"
csvfile="page"
######################################################

options = webdriver.ChromeOptions()
options.add_argument('headless')

browser = webdriver.Chrome(chrome_options=options)
browser.get(url)
time.sleep(time_out)

count=1
try:
    records = browser.find_elements_by_tag_name('a')
    #reach each line
    print("number of record on this page: ", len(records)) if test else None
    for record in records:
        # name=record.text
        new_url = record.get_attribute('href')
        if "php" in new_url:
            print(new_url)if test else None
            csvfile = new_url.split('/')[4].split('.')[0]
            r = requests.get(new_url, verify=False)
            datafile=folder+csvfile+".html"
            count+=1
            with open(datafile, "a", encoding='utf-8') as output:
                output.write(r.text)
            if count == stop and test == True:
                break
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
finally:
    browser.quit()
browser.quit()

