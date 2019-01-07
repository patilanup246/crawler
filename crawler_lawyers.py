from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
import sys, csv, time, unidecode, contextlib
from selenium.webdriver.support.ui import WebDriverWait
import lxml.html
import lxml.html.clean
import codecs
from io import open
#############################################################
url='https://www.mlaw.gov.sg/eservices/lsra/lsra-home/'
time_wait=30
test=False
stop = 10
#############################################################
options = webdriver.ChromeOptions()
folder="./output/"
delim=","
quotes="\""
newline="\n"
csvfile="page"
pidfile="chrome.pid"
#############################################################
def attach_to_session():
	with open(pidfile, "rb") as ins:
		array = []
		for line in ins:
			array.append(line)
		executor_url = array[0]
		session_id = array[1]
	print executor_url if test else None
	print session_id if test else None
	original_execute = WebDriver.execute
	def new_command_execute(self, command, params=None):
		if command == "newSession":
			# Mock the response
			return {'success': 0, 'value': None, 'sessionId': session_id}
		else:
			return original_execute(self, command, params)
	# Patch the function before creating the driver object
	WebDriver.execute = new_command_execute
	driver = webdriver.Remote(command_executor=executor_url, desired_capabilities=options.to_capabilities())
	driver.session_id = session_id
	# Replace the patched function with original function
	WebDriver.execute = original_execute
	return driver
#############################################################
try:
    browser = attach_to_session()

    for i in range(1,100000):
        datafile=folder+csvfile+str(i)+".html"
        with open(datafile, "a", encoding='utf-8') as output:
            data = browser.page_source
            output.write(data)
            output.flush
        button = browser.find_elements_by_xpath('//a[@id="next"]')
        if (len(button)==0):
            break
        doc = button[0]
        if doc.is_enabled():
            doc.click()
        else:
            break #end of the page
        #for testing purpose
        if test==True and i==stop:
            break
        time.sleep(time_wait)
except Exception as e:
    print e