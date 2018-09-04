# get_doc.py
from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
import re
import csv
import selenium.webdriver.support.ui as UI
import contextlib

delim=","
quotes="\""
newline="\n"
csvfile="lawyer_names.csv"
url='https://www.mlaw.gov.sg/eservices/lsra/lsra-home/'
time_wait=10

open(csvfile, 'w').close()

with contextlib.closing(webdriver.Chrome()) as browser:
    #browser = webdriver.Chrome()
    #url='https://www.mlaw.gov.sg/eservices/lsra/search-lawyer-or-law-firm'    
    #print "----------------------------------------------"
    browser.get(url)
    #time.sleep(time_wait)
    wait = UI.WebDriverWait(browser, 30) # timeout after 10 seconds

    #click on the first button
    #button1 = browser.find_element_by_xpath('//*[@id="content"]/div[2]/div[3]/div/div/div/div[1]/div[4]/div[2]/form/a')
    #button1.click()
    #time.sleep(time_wait)
     
    # #print "----------------------------------------------"
    # #open search menu
    # button_advanced_search = browser.find_element_by_id('lsra_flip')
    # button_search = browser.find_element_by_xpath('//*[@id="btnSearch"]')
    # #add all the selection 
    # #unselect_list2 = browser.find_element_by_xpath('//*[@id="UnselectedAreasList"]')
    # unselect_list = UI.Select(browser.find_element_by_xpath('//*[@id="UnselectedAreasList"]'))
    # dropdown_type_of_law_practice=UI.Select(browser.find_element_by_xpath('//*[@id="TypeofLawPractice"]'))
    # print "----------------------------------------------"
    # button_advanced_search.click()
    # print "----------------------------------------------"
    # #for option in unselect_list.find_elements_by_tag_name('option'):
    # for option in unselect_list.options:
        # if not option.text:
            # continue
        # print(option.text, option.get_attribute('value'))
        # option.click()
    # button_add = browser.find_element_by_xpath('//*[@id="search_pc"]/div[2]/input[1]');
    # button_add.click()
    # time.sleep(time_wait)

    # #print "----------------------------------------------"
    # #search all
    # button_search.click()
    # time.sleep(time_wait)

    #print "----------------------------------------------"
    #loop through each tables
    #tables=browser.find_elements_by_class_name('table lsra-search')
    results = wait.until(lambda driver: browser.find_elements_by_xpath("//*[@class='table lsra-search']"))
    tables=browser.find_elements_by_xpath("//*[@class='table lsra-search']")
    for table in tables:
        rows = table.find_elements_by_tag_name('tr')
        for i in range(len(rows)): 
            #print rows[i].find_elements_by_tag_name('td')
            #if i==1 or i==4:
            #    continue
            row = rows[i].find_elements_by_tag_name('td')
            datarow = []
            for index in range(len(row)):   
                #print quotes, row[index].text.encode('utf-8').strip(),quotes,delim,
                data = row[index].text.encode('utf-8')
                #data = data.replace('\r', '').replace('\n', '')
                #data = data.rstrip('\n\r ')
                #data = data.strip('\n\r')
                #newdata = ''.join(data.splitlines())
                datarow.append(data)
            with open(csvfile, "a") as output:
                writer = csv.writer(output, lineterminator="\n")
                writer.writerow(datarow)
            #print rows[i].find_elements_by_tag_name('td')[2]
            #print rows[i].find_elements_by_tag_name('td')[5]
    time.sleep(time_wait)
    #browser.quit()