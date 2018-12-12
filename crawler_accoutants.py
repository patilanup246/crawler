#!python
from selenium import webdriver
import requests
import time, sys, os
import codecs
from io import open

url='https://eservices.isca.org.sg/apex/DirectoryList'

test=False
stop=1
csvfile="page"
time_out=10
######################################################
folder="./accountants/"
delim=","
quotes="\""
newline="\n"
csvfile="page"
######################################################

options = webdriver.ChromeOptions()
options.add_argument('headless')

browser = webdriver.Chrome(chrome_options=options)
browser.get(url)
time.sleep(time_out)

count=1
try:
    for i in range(1,100000):
        records = browser.find_elements_by_xpath('//div[@class="row"]/div[@class="col-sm-8"]/h5/a')
        #reach each line
        print "number of record on this page: ", len(records) if test else None
        for record in records:
            #name=record.text
            new_url = record.get_attribute('href')
            print new_url if test else None
            if new_url:
                r = requests.get(new_url, verify=False)
                datafile=folder+csvfile+str(count)+".html"
                count+=1
                with open(datafile, "a", encoding='utf-8') as output:
                    output.write(r.text)
                    output.flush
            # record.click()#click throug the link
            # time.sleep(time_out)
            # #switch to the new tab
            # browser.switch_to.window(browser.window_handles[1])
            # datafile=folder+csvfile+str(count)+".html"
            # count+=1
            # with open(datafile, "a", encoding='utf-8') as output:
                # data = browser.page_source
                # output.write(data)
                # output.flush
            # #close the new tab
            # time.sleep(time_out)
            # browser.close()
            # #go back to the original tab
            # browser.switch_to.window(browser.window_handles[0])
            # #for testing purpose
        buttons = browser.find_elements_by_xpath('//button[@id="next"]')
        if len(buttons)==0:
            break 
        button=buttons[0]
        if button.is_enabled():
            button.click()    
        else:
            break
        time.sleep(time_out)
        if test and i==stop:
            break
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
finally:
    browser.quit()
browser.quit()

