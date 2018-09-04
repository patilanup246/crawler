# get_doc.py
from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
import re
import csv

browser = webdriver.Chrome()
url='https://eservices.isca.org.sg/apex/DirectoryList'
browser.get(url)
time.sleep(4)
stop=100
csvfile="output.csv"
with open(csvfile, "w") as output:
	writer = csv.writer(output, lineterminator="\n")
	for i in range(1,100):
		records = browser.find_elements_by_xpath('//div[@class="row"]/div[@class="col-sm-8"]')
		for record in records:
			names= record.find_elements_by_tag_name("a")
			if len(names)==0 or len(names) > 10:
				continue	
			text1 = record.text.split("\n");
			writer.writerow(text1)
		button = browser.find_elements_by_xpath('//button[@id="next"]')
		if len(button)==0:
			break
		doc = button[0]
		#doc = browser.find_elements_by_xpath('//button[@id="next"]')[0]
		doc.click()
		if i==stop:
			break
		time.sleep(5)
browser.quit()
