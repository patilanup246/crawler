# get_doc.py
from selenium import webdriver
#from selenium import selenium.common.exceptions.SessionNotCreatedException
import time
import re
import csv

browser = webdriver.Chrome()
url='https://eservices.isca.org.sg/apex/DirectoryList'
browser.get(url)
time.sleep(4)
test=True
stop=1
csvfile="accoutants.csv"
with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator="\n")
    for i in range(1,100):
        records = browser.find_elements_by_xpath('//div[@class="row"]/div[@class="col-sm-8"]/h5/a')
        j = 0
        for record in records:
            name=record.text
            #print record.get_attribute('href')
            record.click()
            time.sleep(4)
            browser.switch_to.window(browser.window_handles[1])
            address=browser.find_element_by_xpath('//*[@id="directoryDetails"]/div/div/div[3]/div[1]').text
            text1=browser.find_element_by_xpath('//*[@id="directoryDetails"]/div/div/div[3]/div[2]').text.split("/n")
            # phone=text1[0]
            # fax=text1[1]
            # email=text1[2]
            # website=text1[3]
            print text1
            executive_contact=browser.find_element_by_xpath('//*[@id="directoryDetails"]/div/div/div[4]/div').text
            classification=browser.find_element_by_xpath('//*[@id="directoryDetails"]/div/div/div[5]').text
            //company_profile=browser.find_element_by_xpath('//*[@id="pg:j_id31:j_id112pg:j_id31:j_id112_00N2800000IMCn0_div"]
            print executive_contact
            print classification
            time.sleep(4)
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
            j=j+1
            if j==3:
                break
        # for record in records:
            # names= record.find_elements_by_tag_name("a")
            # if len(names)==0 or len(names) > 10:
                # continue 
            # text1 = record.text.split("\n")
            # print text1
            # writer.writerow(text1)
        # button = browser.find_elements_by_xpath('//button[@id="next"]')
        # if (len(button)==0):
            # break
        # doc = button[0]
        # doc.click()
        # if doc.is_enabled():
            # doc.click()
        # else:
            # break #end of the page
        #for testing purpose
        if test==True and i==stop:
            break
        time.sleep(5)
browser.quit()
