# get_doc.py
from selenium import webdriver
#from selenium import selenium.common.exceptions.SessionNotCreatedException
import time
import re
import csv

def cleanData(data):
	data = data.encode('utf-8')
	data = data.replace('\r', ' ').replace('\n', ' ')
	return data

browser = webdriver.Chrome()
url='https://eservices.isca.org.sg/apex/DirectoryList'
browser.get(url)
time.sleep(4)
test=False
stop=1
csvfile="accoutants.csv"
with open(csvfile, "w+b") as output:
	writer = csv.writer(output, delimiter=',', lineterminator="\n")
	for i in range(1,1000):
		records = browser.find_elements_by_xpath('//div[@class="row"]/div[@class="col-sm-8"]/h5/a')
		j = 0
		#reach each line
		for record in records:
			datarow=[]
			name=record.text
			print name
			datarow.append(cleanData(record.text)) #add name
			#print record.get_attribute('href')
			record.click()#click throug the link
			time.sleep(4)
			#switch to the new tab
			browser.switch_to.window(browser.window_handles[1])
			#find the address
			address=browser.find_element_by_xpath('//*[@id="directoryDetails"]/div/div/div[3]/div[1]').text
			datarow.append(cleanData(address))
			#find all the information
			text2=browser.find_element_by_xpath('//*[@id="directoryDetails"]/div/div/div[3]/div[2]').text
			text1=text2.split("\n")	
			for tx in text1:
				#print cleanData(tx)
				datarow.append(cleanData(tx))
			#get the executive contact
			executive_contact=browser.find_element_by_xpath('//*[@id="directoryDetails"]/div/div/div[4]/div').text
			datarow.append(cleanData(executive_contact))

			#get the classification
			classification=browser.find_element_by_xpath('//*[@id="directoryDetails"]/div/div/div[5]').text
			datarow.append(cleanData(classification))

			#get the company profile
			company_profile=browser.find_element_by_xpath('//*[@class="sfdc_richtext"]').text
			datarow.append(cleanData(company_profile))

			#close the new tab
			time.sleep(4)
			browser.close()
			#go back to the original tab
			browser.switch_to.window(browser.window_handles[0])
			writer.writerow(datarow)
			j=j+1
			if test==True and j==stop:
				break
		#for testing purpose
		buttons = browser.find_elements_by_xpath('//button[@id="next"]')
		if len(buttons)==0:
			break 
		button=buttons[0]
		button.click()	
		#if button.is_enabled():
		#	button.click()	
		#else:
		#	break
		time.sleep(10)
		if test==True and i==stop:
			break
	time.sleep(5)
browser.quit()

