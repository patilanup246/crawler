from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
import sys, csv, time, unidecode, contextlib
from selenium.webdriver.support.ui import WebDriverWait

delim=","
quotes="\""
newline="\n"
csvfile="lawyer_names.csv"
pidfile="chrome.pid"
url='https://www.mlaw.gov.sg/eservices/lsra/lsra-home/'
time_wait=10

# executor_url = driver.command_executor._url
# session_id = driver.session_id

def attach_to_session():
    with open(pidfile, "rb") as ins:
        array = []
        for line in ins:
            array.append(line)
        executor_url = array[0]
        session_id = array[1]
    print executor_url,"AAA"
    print session_id,"BBB"
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

def find(driver, data):
    element = driver.find_elements_by_id(data)
    if element:
        return element
    else:
        return False
        
def getCurrentPage(driver):
    element = driver.find_elements_by_xpath('//a[@class="active"]')
    if element:
        return element.get_attribute("id")
    else:
        return 1

@contextlib.contextmanager
def wait_for_page_load(driver, timeout=120):
    old_page = driver.find_element_by_tag_name('html')
    yield
    WebDriverWait(driver, timeout).until(staleness_of(old_page))
#############################################################
browser = attach_to_session()

#bro.get('http://ya.ru/')
#open(csvfile, 'w').close()
stop = 100000
currentPageNumber=-1
pageLoaded=True
with open(csvfile, "w") as output:
    writer = csv.writer(output, delimiter=',', lineterminator='\n', quotechar = "\"")
    for i in range(1,100000):
        tables=browser.find_elements_by_xpath("//*[@class='table lsra-search']")
        for table in tables:
            rows = table.find_elements_by_tag_name('tr')
            datarow = []
            for i in range(len(rows)): 
                #print rows[i].find_elements_by_tag_name('td')
                if i==0 or i==4:
                    continue
                cols = rows[i].find_elements_by_tag_name('td')     
                for index in range(len(cols)):   
                    data = cols[index].text.encode('utf-8')
                    #if not data:
                    #    continue
                    datarow.append(data)
                    #print i,data
                    #datarow.append(data)
                writer.writerow(datarow)
        button = browser.find_elements_by_xpath('//a[@id="next"]')
        if (len(button)==0):
            break
        doc = button[0]
        doc.click()
        # if doc.is_enabled():
            # doc.click()
        # else:
            # break #end of the page
        #for testing purpose
        if i==stop:
            break
        time.sleep(time_wait)
        wait_for_page_load(browser)
