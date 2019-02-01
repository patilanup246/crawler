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

test=False
stop=50
time_out=1
folder="./raw/startups/"
######################################################
delim=","
quotes="\""
newline="\n"
csvfile="record"
pidfile="chrome.pid"
WINDOW_SIZE = "1920,1080"
IMPLICIT_WAIT=300
EXPLICIT_WAIT=300
usr="nguyendd+startupsg@gmail.com"
pwd="o9Y1JcrE0E"
########
start_time=time.time()
print(datetime.datetime.now())
#######k
options = webdriver.ChromeOptions()
options.add_argument("--window-size=%s" % WINDOW_SIZE)
#options.add_argument("--start-maximized")
options.add_argument('--headless')
#######k
driver = webdriver.Chrome(chrome_options=options)
driver.get(url)
#driver.implicitly_wait(IMPLICIT_WAIT)
time.sleep(time_out)
page=1
start_page=230
stop_time=1000
count=0
count=(start_page-1)*10
records_in_current_page=0
try:
	#login into the app
	#driver.save_screenshot("output.png")
	#driver.execute_script("document.body.style.zoom='70%'")
	#raise Exception("Testing")
	#time.sleep(time_out)
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

	elem = driver.find_element_by_css_selector('#app > div.application--wrap > div > main > div > div > div > div > div > div.directory__filters > div > div > div.filter.directory__filter.directory__filter--sort > div > div > div.directory__sort__value')
	elem.click()
	time.sleep(time_out)
	elem = driver.find_element_by_css_selector('#app > div.application--wrap > div > main > div > div > div > div > div > div.directory__filters > div > div > div.filter.directory__filter.directory__filter--sort.active > div.filter-panel.filter-panel--right > div > div > div:nth-child(15) > a > div > div')	
	elem.click()	
	time.sleep(time_out)
	#raise Exception("testing")
	while True:
		count=(page-1)*10
		print("current page is ", page, " and current time_out is ",time_out)
		wait = WebDriverWait(driver, EXPLICIT_WAIT)
		wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="flex xs12"]/a')))
		records = driver.find_elements_by_xpath('//div[@class="flex xs12"]/a')
		#print(len(records))
		records_in_current_page=len(records)
		if page >= start_page:
				  for record in records:
					  #print(record.get_attribute('href'))
					  wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="flex xs12"]/a')))
					  sys.stdout.flush()
					  record.click()
					  time.sleep(time_out)
					  driver.switch_to.window(driver.window_handles[-1])
					  wait.until(EC.presence_of_element_located((By.XPATH,'//section')))
					  r = driver.page_source
					  count+=1
					  datafile=folder+csvfile+str(count)+".html"
					  #print(datafile)
					  with open(datafile, "w", encoding="utf-8") as output:
						  output.write(r)
						  output.flush()
						  output.close()
					  #time.sleep(time_out)
					  driver.close()
					  driver.switch_to.window(driver.window_handles[0])
				  if test and page==stop:
					  break	
				  if records_in_current_page==0:
					  driver.save_screenshot("screenshot_page_"+str(page)+".png")
					  print("cannot find any record in page ", page)
					  time_out += 10
					  continue
		#print("Done with page ", page, " with no of records ", records_in_current_page)
		page+=1
		wait.until(EC.presence_of_element_located((By.CLASS_NAME,"pagination__navigation")))
		buttons = driver.find_elements_by_xpath('//button[@class="pagination__navigation"][i/@class="icon mdi mdi-arrow-right"]')
		if len(buttons)==0:
			break
		else:
			buttons[0].click()
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
	print("Total number of records: ", count)
	driver.quit()

