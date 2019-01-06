#!/usr/bin/env python
import requests, csv, sys, re, argparse, random
import time, glob, urllib3, urllib
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

src_url = "https://www.yelp.com/search?find_desc=tea&find_loc=New%20York%2C%20NY&start="
output_folder = "./raw/yelp/"
result_file = "./results/yelp.csv"

def parse(url):
    print(url)
    datarow=[]
    headers= {
              'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'accept-encoding':'gzip, deflate, sdch, br',
              'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
              'cache-control':'max-age=0',
              'upgrade-insecure-requests':'1',
              'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    response = requests.get(url,headers=headers, verify=False)
    #print(response.status_code)
    #print(len(response.content))
    sys.stdout.flush()
    soup = BeautifulSoup(response.text, 'html.parser')
    title = ""
    address = ""
    phone = ""
    website = ""
    if len(soup.select('h1[class*="biz-page-title"]'))>0:
        title = soup.select('h1[class*="biz-page-title"]')[0].get_text().replace("\n","").replace("  ","")
    if len(soup.select('strong[class="street-address"]'))>0:
        add1 = soup.select('strong[class="street-address"]')[0]
        for br in add1.find_all("br"):
            br.replace_with(" ")
        address= add1.get_text().replace("\n","").replace("  ","")
    if len(soup.select('span[class="biz-phone"]'))>0:
        phone = soup.select('span[class="biz-phone"]')[0].get_text().replace("\n","").replace(" ","")
    if len(soup.select('span[class*="biz-website"]'))>0:
        site = soup.select('span[class*="biz-website"]')[0]
        if len(site.select('a'))>0:
            website = site.select('a')[0].attrs["href"].split("=")[1].split("&")[0]
    #print(title)
    #print(address)
    #print(phone)
    #print(urllib.parse.unquote(website))
    if title != "":
        datarow.append(title)
        datarow.append(address)
        datarow.append(phone)
        datarow.append(urllib.parse.unquote(website))
        appendToFile(datarow)
def appendToFile(datarow):
    with open(result_file, 'a', encoding = 'utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(datarow)
def crawler():
    i = 630 
    while True:
        url = src_url + str(i)
        i +=  30
        print(url)
        sys.stdout.flush()
        headers= {
                  'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'accept-encoding':'gzip, deflate, sdch, br',
                  'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
                  'cache-control':'max-age=0',
                  'upgrade-insecure-requests':'1',
                  'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        response = requests.get(url,headers=headers, verify=False)
        print(response.status_code)
        print(len(response.content))
        if len(response.content) < 400000:
            with open("screenshot.html", "w") as file:
                file.write(str(response.text))
            i -= 30
            time.sleep(random.randint(50,110))
            continue
        sys.stdout.flush()
        #parsing the text
        soup = BeautifulSoup(response.text, 'html.parser')
        blocks = soup.select('div[class*="businessName"]')
        for block in blocks:
            title=block.get_text()
            if  title[0].isdigit() == False:
                continue 
            link=""
            href=""
            if len(block.select('a[class*="lemon--a"]')) > 0:
                href = block.select('a[class*="lemon--a"]')[0]
                link = href.attrs["href"]
            parse("https://www.yelp.com" + link)
            #print(href)
            #print(datarow)
            #appendToFile(datarow)
            time.sleep(random.randint(1,3))
        time.sleep(random.randint(5,10))
if __name__=="__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('action',help= ' parse, crawl')
    argparser.add_argument('--output',nargs= '?', help = 'crawl --output <filename>')
    args = argparser.parse_args()
    action = args.action
    output= args.output
    print ("action: %s"%(action))
    print ("output:",output)
    sys.stdout.flush()
    if not output is None:
        result_file = output
    if "parse" == action:
        parse("https://www.yelp.com/biz/alices-tea-cup-new-york?osq=tea")
    if "crawl" == action:
        crawler()
