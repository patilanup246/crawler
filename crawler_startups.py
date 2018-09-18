#!python
from selenium import webdriver
#from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time, sys, os, datetime
import codecs
from io import open

url='https://www.startupsg.net/directory/startups'

test=True
stop=10
time_out=1
folder="./raw/startups/"
######################################################
delim=","
quotes="\""
newline="\n"
csvfile="page"
pidfile="chrome.pid"
WINDOW_SIZE = "1920,1080"
IMPLICIT_WAIT=30
usr="nguyendd+startupsg@gmail.com"
pwd="o9Y1JcrE0E"
########
start_time=time.time()
print(datetime.datetime.now())
#######k
options = webdriver.ChromeOptions()
options.add_argument("--window-size=%s" % WINDOW_SIZE)
options.add_argument('headless')
#######k
driver = webdriver.Chrome(chrome_options=options)
driver.get(url)
driver.implicitly_wait(IMPLICIT_WAIT)
time.sleep(time_out)
try:
	#login into the app
	#driver.save_screenshot("output.png")
	#raise Exception("Testing")
	e = driver.find_element_by_css_selector('#app > div.application--wrap > div > div.header > nav > div > a')
	#raise Exception("Testing")
	e.click()
	time.sleep(time_out)
	#
	elem = driver.find_element_by_css_selector('#app > div.dialog__content.dialog__content__active > div > div.login-form.entity-form > div > form > div:nth-child(1) > div.input-group__input > input[type="text"]')
	elem.send_keys(usr)
	#
	elem = driver.find_element_by_css_selector('#app > div.dialog__content.dialog__content__active > div > div.login-form.entity-form > div > form > div:nth-child(2) > div.input-group__input > input[type="password"]')
	#print elem
	elem.send_keys(pwd)
	elem.send_keys(Keys.RETURN)
	time.sleep(time_out)
	#time.sleep(time_out)
	#get link one by one
	page=1
	count=1
	while True:
		records = driver.find_elements_by_xpath('//div[@class="flex xs12"]/a')
		#print(len(records))
		for record in records:
			#print(record.get_attribute('href'))
			sys.stdout.flush()
			record.click()
			time.sleep(time_out)
			driver.switch_to.window(driver.window_handles[-1])
			r = driver.page_source
			datafile=folder+csvfile+str(count)+".html"
			count+=1
			with open(datafile, "w", encoding="utf-8") as output:
				output.write(r)
				output.close()
			#time.sleep(time_out)
			driver.close()
			driver.switch_to.window(driver.window_handles[0])
		if test and page==stop:
			break	
		page+=1
		driver.find_elements_by_xpath('//button[@class="pagination__navigation"]')[0].click()
except Exception as e:
	print(str(e))
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	print(exc_type, fname, exc_tb.tb_lineno)
	driver.save_screenshot("screenshot.png")
finally:
	print(datetime.datetime.now())
	end_time=time.time()
	print("Total processing time: ",(end_time-start_time))
	print("Total number of pages: ", page)
	print("Total number of companies: ", count)
	driver.quit()

