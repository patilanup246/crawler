# get_doc.py
from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
import re
import csv

browser = webdriver.Chrome()
url='https://www.mlaw.gov.sg/eservices/lsra/search-lawyer-or-law-firm'
browser.get(url)
time.sleep(4)
stop=100
csvfile="laywer_names.csv"
search = browser.find_element_by_id('lsra_flip')
search.click()
unselect_list = browser.find_element_by_id('UnselectedAreasList')
#unselect_list = browser.find_element_by_xpath('//select[@class="lsra-listbox valid" and @name="UnselectedAreasList"]')
#print unselect_list.text
#for option in unselect_list.find_elements_by_tag_name('option'):
for option in unselect_list.find_elements_by_xpath('//option'):
	if not option.text:
		continue
	print(option.text, option.get_attribute('value'))
	option.click()
time.sleep(10)
browser.quit()
