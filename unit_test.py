#!python
from selenium import webdriver
#from selenium.webdriver.remote.webdriver import WebDriver
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
time_out=2
######################################################
folder="./raw/startups/"
delim=","
quotes="\""
newline="\n"
csvfile="page"
pidfile="chrome.pid"
options = webdriver.ChromeOptions()


#options.add_argument('headless')
usr="nguyendd+startupsg@gmail.com"
pwd="o9Y1JcrE0E"
browser = webdriver.Chrome(chrome_options=options)
browser.get(url)
time.sleep(time_out)
#list1=browser.find_elements_by_xpath('//button[contains(@class,"btn-primary--small")]')
#print list1
e = browser.find_element_by_css_selector('#app > div.application--wrap > div > div.header > nav > div > a')
print e
# list1=browser.find_elements_by_xpath('//div[@class="toolbar__items"]/a')
# print list1
# elem = browser.find_elements_by_xpath('//input[@aria-label="Email"]')[0]
# print elem
# # elem.send_keys(usr)
# elem = browser.find_elements_by_xpath('//input[@aria-label="Password"]')[0]
# print elem
# elem.send_keys(pwd)
# elem.send_keys(Keys.RETURN)
# time.sleep(time_out)
browser.quit()

