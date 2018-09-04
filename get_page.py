import scrapy
from selenium import webdriver

class northshoreSpider(scrapy.Spider):
    name = 'scrapy'
    allowed_domains = ['www.example.org']
    start_urls = ['https://www.example.org']

    def __init__(self):
        self.driver = webdriver.Chrome()

    def parse2(self,response):
            self.driver.get('https://www.example.org/abc')
	    print "AAA"

            while True:
                try:
                    next = self.driver.find_element_by_xpath('//*[@id="BTN_NEXT"]')
                    url = 'http://www.example.org/abcd'
		    print url	
                    yield Request(url,callback=self.parse2)
                    next.click()
                except:
                    break

            self.driver.close()

    def parse(self,response):
        print 'you are here!'

