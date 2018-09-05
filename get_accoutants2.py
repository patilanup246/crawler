# get_doc.py
from selenium import webdriver
#from selenium import selenium.common.exceptions.SessionNotCreatedException
import time, re, csv, string
from lxml import html
def cleanData(data):
	data = data.encode('utf-8')
	data = data.strip()
	#data = re.sub(r'[^\x00-\x7f]',r'',data) 
	#data = data.encode('ascii',errors='ignore').decode()
	data = data.replace('\r', ' ').replace('\n', ' ')
	return data

options = webdriver.ChromeOptions()
options.add_argument('headless')

browser = webdriver.Chrome(chrome_options=options)
url='https://eservices.isca.org.sg/apex/DirectoryList'
browser.get(url)
time.sleep(4)
test=True
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
			doc=html.fromstring(browser.page_source)
			address=doc.xpath('//*[@id="directoryDetails"]/div/div/div[3]/div[1]')[0].text_content().strip()
			print "address",cleanData(address)
			datarow.append(cleanData(address))
			#find all the information
			text2=doc.xpath('//*[@id="directoryDetails"]/div/div/div[3]/div[2]')[0].text_content()
			text1=text2.split("\n")	
			for tx in text1:
				tx = cleanData(tx)
				#tx = tx.decode('utf-8').encode('ascii', errors='ignore')
				#tx = re.sub(r'[^\x00-\x7f]',r'',tx) 
				if tx:
					print tx
					datarow.append(tx)
			#get the executive contact
			executive_contact=doc.xpath('//*[@id="directoryDetails"]/div/div/div[4]/div')[0].text_content().strip()
			print "contact", executive_contact
			datarow.append(cleanData(executive_contact))

			#get the classification
			#classification=browser.find_element_by_xpath('//*[@id="directoryDetails"]/div/div/div[5]').text
			classification=doc.xpath('//*[@id="directoryDetails"]/div/div/div[5]/div[1]/p')
			temp=""
			for row1 in classification:
				for row2 in row1.findall('span')[1:]:
					temp=temp+row2.text.strip()+"\015"
			print temp
			#datarow.append(cleanData(temp))
			datarow.append(temp)

			#get the company profile
			#company_profile=browser.find_element_by_xpath('//*[@class="sfdc_richtext"]').text
			company_profile=doc.xpath('//*[@class="sfdc_richtext"]')[0].text_content()
			datarow.append(cleanData(company_profile))

			#close the new tab
			time.sleep(4)
			browser.close()
			#go back to the original tab
			browser.switch_to.window(browser.window_handles[0])
			writer.writerow(datarow)
			output.flush()
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

