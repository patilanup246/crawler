#!/usr/bin/env python
import requests, csv, sys, re, argparse, random
import time, glob, urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

src_url = "https://www.zillow.com/{0}/real-estate-agent-reviews/?page="
output_folder = "./raw/zillow/"
result_file = "./results/agents.csv"

def download(zipcode):
    i = 0
    while True:
        i += 1
        url = src_url.format(zipcode)+ str(i)
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
        if len(response.content) < 180000:
            break
        sys.stdout.flush()
        csv_file = str(zipcode) + str("_") + str(i)+".html" 
        data_file = output_folder + csv_file
        with open(data_file, "a", encoding="utf-8") as output:
            output.write(response.text)
        time.sleep(10)

def parse():
    file_list= glob.glob(output_folder+"*.html")
    file_list.sort()
    #print(file_list)
    header=["Zip Code" , "Page", "Name", "Phone" , "Rating", "Reviews", "Office"]
    with open(result_file, 'w', encoding = 'utf-8') as output:
          writer = csv.writer(output, delimiter=",", lineterminator="\n")
          writer.writerow(header)
          for file1 in file_list:
                     filename1 = file1.split("\\")[-1]
                     print(filename1)
                     sys.stdout.flush()
                     zipcode = filename1.split("_")[0]
                     page = filename1.split("_")[1].split(".")[0]
                     with open(file1, 'r', encoding = 'utf-8') as html_file:
                         soup = BeautifulSoup(html_file, 'html.parser')
                         blocks = soup.select('div[data-test-id="ldb-boards-results"]')
                         rows = blocks[0].select('div[data-test-id*="ldb-board"]') 
                         for row in rows:
                             name = ""
                             phone = ""
                             rating = ""
                             reviews = ""
                             office = ""
                             #agent = row.select('div[class="ldb-board-inner"]')[0]
                             agent = row.select('div[class="ldb-col-a"]')[0].select('div[class="ldb-board-inner"]')[0]
                             name = agent.select('p[class*="ldb-contact-name"]')[0].get_text()
                             phone = agent.select('p[class*="ldb-phone-number"]')[0].get_text()
                             try:
                                 rating = agent.select('span[class*="zsg-rating"]')[0]['title']
                             except:
                                 pass
                             try:
                                 reviews= agent.select('a[class*="zsg-link zsg-fineprint"]')[0].get_text()
                             except:
                                 pass
                             
                             try:
                                 office = row.select('div[class="ldb-col-b"]')[0].select('div[class="ldb-board-inner"]')[0].select('p[class="ldb-business-name"]')[0].get_text()
                                 office =re.sub(r'[\ \n]{2,}', '', office)
                                 office =re.sub(r'\n', '', office)
                             except:
                                 pass
                             datarow = []
                             datarow.append(zipcode)
                             datarow.append(page)
                             datarow.append(name)
                             datarow.append(phone)
                             datarow.append(rating)
                             datarow.append(reviews)
                             datarow.append(office)
                             #print(datarow)
                             writer.writerow(datarow)
def appendToFile(datarow):
    with open(result_file, 'a', encoding = 'utf-8') as output:
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow(datarow)
def crawler(zipcode):
    i = 0
    while True:
        i += 1
        url = src_url.format(zipcode)+ str(i)
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
        if len(response.content) < 180000:
            break
        sys.stdout.flush()
        #parsing the text
        soup = BeautifulSoup(response.text, 'html.parser')
        blocks = soup.select('div[data-test-id="ldb-boards-results"]')
        rows = blocks[0].select('div[data-test-id*="ldb-board"]') 
        for row in rows:
            name = ""
            phone = ""
            rating = ""
            reviews = ""
            office = ""
            #agent = row.select('div[class="ldb-board-inner"]')[0]
            agent = row.select('div[class="ldb-col-a"]')[0].select('div[class="ldb-board-inner"]')[0]
            name = agent.select('p[class*="ldb-contact-name"]')[0].get_text()
            phone = agent.select('p[class*="ldb-phone-number"]')[0].get_text()
            try:
                rating = agent.select('span[class*="zsg-rating"]')[0]['title']
            except:
                pass
            try:
                reviews= agent.select('a[class*="zsg-link zsg-fineprint"]')[0].get_text()
            except:
                pass
            try:
                office = row.select('div[class="ldb-col-b"]')[0].select('div[class="ldb-board-inner"]')[0].select('p[class="ldb-business-name"]')[0].get_text()
                office =re.sub(r'[\ \n]{2,}', '', office)
                office =re.sub(r'\n', '', office)
            except:
                pass
            datarow = []
            datarow.append(zipcode)
            datarow.append(str(i))
            datarow.append(name)
            datarow.append(phone)
            datarow.append(rating)
            datarow.append(reviews)
            datarow.append(office)
            appendToFile(datarow)
        time.sleep(random.randint(5,10))

if __name__=="__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('action',help= 'download or parse')
    argparser.add_argument('--zipcode',nargs= '?', help = 'zip code')
    argparser.add_argument('--file',nargs= '?', help = 'a file contains list of zip codes')
    args = argparser.parse_args()
    action = args.action
    zipcode= args.zipcode
    file= args.file
    print ("action: %s"%(action))
    print ("zipcode:",zipcode)
    print ("file:",file)
    sys.stdout.flush()
    if "download" == action:
        if not zipcode is None:
            for zip1 in zipcode:
                download(zip1)
        if not file is None:
            with open(file, 'r') as input:
                for line in input:
                    if line.isdigit():
                        download(line)
    if "parse" == action:
        parse()
    if "crawl" == action:
        if not zipcode is None:
            for zip1 in zipcode:
                crawler(zip1)
        if not file is None:
            with open(file, 'r') as input:
                for line in input:
                    zipcode = line.rstrip()
                    if zipcode.isdigit():
                        crawler(zipcode)
    #scraped_data = parse(zipcode,sort)
    #print ("Writing data to output file")
    #with open("properties-%s.csv"%(zipcode),'wb')as csvfile:
        #fieldnames = ['title','address','city','state','postal_code','price','facts and features','real estate provider','url']
        #writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #writer.writeheader()
        #for row in  scraped_data:
        #   writer.writerow(row)

