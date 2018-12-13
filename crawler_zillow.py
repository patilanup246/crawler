#!/usr/bin/env python
from lxml import html
import requests, csv
#import unicodecsv as csv
import argparse, re
import time, glob
from bs4 import BeautifulSoup

src_url = "https://www.zillow.com/{0}/real-estate-agent-reviews/?page="
output_folder = "./raw/zillow/"
result_file = "./results/agents.csv"

def download(zipcode, run=1):
	if run is None:
		run = 1 
	start = int(zipcode)
	end = int(zipcode) + int(run)
	for zip1 in range(start, end):
			  for i in range(1,26):
				  url = src_url.format(zip1)+ str(i)
				  print(url)
				  headers= {
							  'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
							  'accept-encoding':'gzip, deflate, sdch, br',
							  'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
							  'cache-control':'max-age=0',
							  'upgrade-insecure-requests':'1',
							  'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
				  }
				  response = requests.get(url,headers=headers)
				  print(response.status_code)
				  csv_file = str(zip1) + str("_") + str(i)+".html" 
				  data_file = output_folder + csv_file
				  with open(data_file, "a", encoding="utf-8") as output:
					  output.write(response.text)
				  time.sleep(1)

def parse():
	file_list= glob.glob(output_folder+"*.html")
	file_list.sort()
	print(file_list)
	header=["zipcode" , "name", "phone" ]
	with open(result_file, 'w', encoding = 'utf-8') as output:
		  writer = csv.writer(output, delimiter=",", lineterminator="\n")
		  writer.writerow(header)
		  for file1 in file_list:
					 filename1 = file1.split("/")[-1]
					 print(filename1)
					 zipcode = filename1.split("_")[0]
					 with open(file1, 'r', encoding = 'utf-8') as html_file:
						 soup = BeautifulSoup(html_file, 'html.parser')
						 blocks = soup.select('div[data-test-id="ldb-boards-results"]')
						 rows = blocks[0].select('div[data-test-id*="ldb-board"]') 
						 for row in rows:
							 #agent = row.select('div[class="ldb-board-inner"]')[0]
							 try:
								 agent = row.select('div[class="ldb-col-a"]')[0].select('div[class="ldb-board-inner"]')[0]
								 name = agent.select('p[class*="ldb-contact-name"]')[0].get_text()
								 phone = agent.select('p[class*="ldb-phone-number"]')[0].get_text()
								 rating = agent.select('span[class*="zsg-rating"]')[0]['title']
								 reviews= agent.select('a[class*="zsg-link zsg-fineprint"]')[0].get_text()
								 office = row.select('div[class="ldb-col-b"]')[0].select('div[class="ldb-board-inner"]')[0].select('p[class="ldb-business-name"]')[0].get_text()
								 office =re.sub(r'[\ \n]{2,}', '', office)
							 except:
						     	next		
							 datarow = []
							 datarow.append(zipcode)
							 datarow.append(name)
							 datarow.append(phone)
							 datarow.append(rating)
							 datarow.append(reviews)
							 datarow.append(office)
							 print(datarow)
							 writer.writerow(datarow)
def crawler(zipcode, run=1):
	if run is None:
		run = 1 
	start = int(zipcode)
	end = int(zipcode) + int(run)
	for zip1 in range(start, end):
			  for i in range(1,26):
				  url = src_url.format(zip1)+ str(i)
				  print(url)
				  headers= {
							  'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
							  'accept-encoding':'gzip, deflate, sdch, br',
							  'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
							  'cache-control':'max-age=0',
							  'upgrade-insecure-requests':'1',
							  'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
				  }
				  response = requests.get(url,headers=headers)
				  print(response.status_code)
				  csv_file = str(zip1) + str("_") + str(i)+".html" 
				  data_file = output_folder + csv_file
				  with open(data_file, "a", encoding="utf-8") as output:
					  output.write(response.text)
				  time.sleep(5)
	for i in range(26):
		# try:
		headers= {
					'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					'accept-encoding':'gzip, deflate, sdch, br',
					'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
					'cache-control':'max-age=0',
					'upgrade-insecure-requests':'1',
					'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
		}
		response = requests.get(url,headers=headers)
		print(response.status_code)
		parser = html.fromstring(response.text)
		search_results = parser.xpath("//div[@id='search-results']//article")
		properties_list = []
		
		for properties in search_results:
			raw_address = properties.xpath(".//span[@itemprop='address']//span[@itemprop='streetAddress']//text()")
			raw_city = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressLocality']//text()")
			raw_state= properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressRegion']//text()")
			raw_postal_code= properties.xpath(".//span[@itemprop='address']//span[@itemprop='postalCode']//text()")
			raw_price = properties.xpath(".//span[@class='zsg-photo-card-price']//text()")
			raw_info = properties.xpath(".//span[@class='zsg-photo-card-info']//text()")
			raw_broker_name = properties.xpath(".//span[@class='zsg-photo-card-broker-name']//text()")
			url = properties.xpath(".//a[contains(@class,'overlay-link')]/@href")
			raw_title = properties.xpath(".//h4//text()")
			
			address = ' '.join(' '.join(raw_address).split()) if raw_address else None
			city = ''.join(raw_city).strip() if raw_city else None
			state = ''.join(raw_state).strip() if raw_state else None
			postal_code = ''.join(raw_postal_code).strip() if raw_postal_code else None
			price = ''.join(raw_price).strip() if raw_price else None
			info = ' '.join(' '.join(raw_info).split()).replace(u"\xb7",',')
			broker = ''.join(raw_broker_name).strip() if raw_broker_name else None
			title = ''.join(raw_title) if raw_title else None
			property_url = "https://www.zillow.com"+url[0] if url else None 
			is_forsale = properties.xpath('.//span[@class="zsg-icon-for-sale"]')
			properties = {
							'address':address,
							'city':city,
							'state':state,
							'postal_code':postal_code,
							'price':price,
							'facts and features':info,
							'real estate provider':broker,
							'url':property_url,
							'title':title
			}
			if is_forsale:
				properties_list.append(properties)
		return properties_list
		#except:
			#print ("Failed to process the page",url)

if __name__=="__main__":
	argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
	argparser.add_argument('action',help= 'download or parse')
	argparser.add_argument('--zipcode',nargs= '+', help = '90001, 90002, etc. ')
	argparser.add_argument('--run',nargs= '?', help = '1, 2, 3, etc. ')
	args = argparser.parse_args()
	action = args.action
	zipcode= args.zipcode
	run= args.run
	print ("action: %s"%(action))
	print ("zipcode:",zipcode)
	print ("run:",run)
	if "download" == action:
		for zip1 in zipcode:
			download(zip1, run)
	if "parse" == action:
		parse()
	#scraped_data = parse(zipcode,sort)
	#print ("Writing data to output file")
	#with open("properties-%s.csv"%(zipcode),'wb')as csvfile:
		#fieldnames = ['title','address','city','state','postal_code','price','facts and features','real estate provider','url']
		#writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		#writer.writeheader()
		#for row in  scraped_data:
		#	writer.writerow(row)

