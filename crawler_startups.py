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
time_out=2
######################################################
folder="./raw/startups/"
delim=","
quotes="\""
newline="\n"
csvfile="page"
pidfile="chrome.pid"
options = webdriver.ChromeOptions()
######################################################
def attach_to_session():
    with open(pidfile, "rb") as ins:
        array = []
        for line in ins:
            array.append(line)
        executor_url = array[0]
        session_id = array[1]
    print executor_url if test else None
    print session_id if test else None
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


options.add_argument('headless')

#browser = webdriver.Chrome(chrome_options=options)
#browser.get(url)
browser = attach_to_session()
# Save the window opener (current window, do not mistaken with tab... not the same).
main_window = browser.current_window_handle
print("Main window: ",  main_window)
sys.stdout.flush()
count=1
try:
    time.sleep(time_out)
    for i in range(1,100000):
        records = browser.find_elements_by_xpath('//div[@class="flex xs12"]/a')
        #reach each line
        print "number of record on this page: ", len(records) if test else None
        sys.stdout.flush()
        for record in records:
            #name=record.text
            new_url = record.get_attribute('href')
            print new_url if test else None
            sys.stdout.flush()
            #click on the link
            record.click()
            time.sleep(time_out)
            print("-1 " + browser.window_handles[-1])
            print("0 " + browser.window_handles[0])
            print("1 " + browser.window_handles[1])
            print("Switing to " + browser.window_handles[1])
            sys.stdout.flush()
            #switch to the new window
            browser.switch_to_window(browser.window_handles[1])
            #browser.switch_to.window(browser.window_handles[1])
            print("Sub window: ",  browser.title)
            sys.stdout.flush()
            #r = requests.get(new_url, verify=False)
            time.sleep(time_out)
            r = browser.page_source
            datafile=folder+csvfile+str(count)+".html"
            count+=1
            # with open(datafile, "a", encoding='utf-8') as output:
                # output.write(r)
                # output.flush
            #switch to the new window'
            time.sleep(time_out)
            #browser.close()
            #browser.switch_to.window(browser.window_handles[0])
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
        buttons = browser.find_elements_by_xpath('//button[@class="pagination__navigation"]')
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
    print("Exception: " + str(e))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
#finally:
    #browser.close()

