# get_doc.py
from selenium import webdriver
#from selenium import selenium.common.exceptions.SessionNotCreatedException
import time
import re
import csv

browser = webdriver.Chrome()
url='http://www.saicsa.org.sg/english/contact/prac.htm'
browser.get(url)
time.sleep(4)
csvfile="secretaries.csv"
test=True
stop=2
with open(csvfile, "w+b") as output:
    writer = csv.writer(output, delimiter=',', lineterminator='\n')
    table=browser.find_element_by_xpath("//*[@class='MsoNormalTable']")
    rows = table.find_elements_by_tag_name('tr')  
    for i in range(len(rows)): 
        #print rows[i].find_elements_by_tag_name('td')
        #if i==0 or i==4:
        #    continue
        cols = rows[i].find_elements_by_tag_name('td') 
        datarow = []        
        for index in range(len(cols)):   
            data = cols[index].text.encode('utf-8')
            data = data.replace('\r', ' ').replace('\n', ' ')
            if not data:
                continue
            #datarow.append(data)
            #print i,data
            datarow.append(data)
        writer.writerow(datarow)
        if test==True and i==stop:
            break;
browser.quit()
