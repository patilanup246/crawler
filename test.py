#!python
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import requests
import time, sys, os
import codecs
from io import open

url='https://www.startupsg.net/directory/startups'

test=True
stop=1
csvfile="page"
time_out=20
######################################################
folder="./raw/startups/"
delim=","
quotes="\""
newline="\n"
csvfile="page"
pidfile="chrome.pid"

######################################################
def attach_to_session():
	with open(pidfile, "rb") as ins:
		array = []
		for line in ins:
			array.append(line)
		executor_url = array[0]
		session_id = array[1]
	print(executor_url) if test else None
	print(session_id) if test else None
	sys.stdout.flush()
	original_execute = WebDriver.execute
	def new_command_execute(self, command, params=None):
		if command == "newSession":
			# Mock the response
			return {'success': 0, 'value': None, 'sessionId': session_id}
		else:
			return original_execute(self, command, params)
	# Patch the function before creating the driver object
	WebDriver.execute = new_command_execute
	driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
	driver.session_id = session_id
	# Replace the patched function with original function
	WebDriver.execute = original_execute
	return driver
########################################################


options = webdriver.ChromeOptions()
#options.add_argument('headless')

browser2 = webdriver.Chrome(chrome_options=options)
#browser.get(url)
browser = attach_to_session()

try:
	#time.sleep(time_out)
	cookies = browser.get_cookies()
	print(cookies)
	for item in cookies:
		browser2.add_cookie(item)
	browser2.get(url)
	time.sleep(time_out)
except Exception as e:
	print("Exception: " + str(e))
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	print(exc_type, fname, exc_tb.tb_lineno)
finally:
	#browser.quit()
	browser2.quit()

