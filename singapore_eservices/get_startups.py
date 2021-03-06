#!python
# -*- coding: utf-8 -*-
import os, glob, csv
from bs4 import BeautifulSoup
import re,  codecs, sys

##########################
def cleanData(data):
	result=""
	list1 = data.split('\n')
	list2=[]
	for text1 in list1:
		list2.append(text1.strip())
	result = ";".join(filter(None,list2))
	return result

def cleanHtmlTags(data):
	result = ""
	sep= ','
	#remove all tags
	list1=[]
	for a in data:
		b = re.sub(r'<.+?>',r' ',str(a).strip())
		b = re.sub(r'\n',sep,b)
		b = re.sub(r' +',' ',b)
		list1.append(b)
	#list1 = [re.sub(r',+',r',',str(a)) for a in list1]
	#list1 = [re.sub(r' +',r' ',str(a)) for a in list1]
	list1 = list(filter(None,list1))
	result = "".join(list1)	
	result = result.strip()
	return result

###########################
FOLDER="./raw/startups/"
IN_FILENAME="record"
TEMP_FILENAME="temp.csv"
OUT_FILENAME="results/startups.csv"
FILE_EXTENSION=".html"
TEST=False
DELIM=","
NEWLINE="\n"
EXCELNEWLINE=";"
stop=2740
start_no=1
max_no=len(glob.glob(FOLDER+"*"+FILE_EXTENSION))

##print max_no if TEST else None
print(max_no,flush=True)
filename=""
header=["No","Name","UEN","Short Intro","Date incorporated","Sector","Funding Stage","Employee range","Tags","Description","Address","Website","Emails","Phone","Team","Funding Stage","Total Funding","Funding Rounds","Rounding Raised"]
with open(OUT_FILENAME,'w',encoding="utf-8" ) as out_file:
	writer = csv.writer(out_file, delimiter=DELIM, lineterminator="\n") 
	writer.writerow(header)
	for i in range(start_no,max_no+1):
		filename=FOLDER+IN_FILENAME+str(i)+FILE_EXTENSION
		print(filename,flush=True)
		datarow=[]
		datarow.append(str(i))
		try:
			with open(filename, 'r', encoding="utf-8") as html_file:
				soup=BeautifulSoup(html_file,'html.parser')
				sections=soup.find_all('section')
				#if len(sections)<3: 
				#	break
				#heading
				##print("=============header information")
				general=sections[0].find_all("section", {"id":"general"})
				general=sections[0].find_all("section", {"id":"general"})[0]
				heading=general.find_all("div",{"class":"flex md9 column"})[0]
				list1=[]
				list1.append(heading.select("h1")[0].text)
				list1.append(" ".join(heading.select("div")[0].text.strip().split(" ")[:2]))
				list1.append(heading.select("div")[1].text.strip())
				datarow = datarow + list1
				#body details
				#print("=============body details information")
				body=general.find_all("div",{"class":"flex entity__details xs12"})[0]
				#for text1 in body.select('div[class*="xs12 md9"]'):
				#print(text1.get_text().strip().encode("utf-8"))
				for text1 in body.select('div[class*="layout wrap"]')[:4]:
					datarow.append(text1.find_all('div')[1].text.encode("utf-8").strip())
				list1=[]
				for text1 in body.select('span[class*="entity__tag"]'):
					list1.append(text1.text)
				datarow.append(EXCELNEWLINE.join(list1))
					#print(text1.find_all('div')[1].text.encode("utf-8").strip())
				#datarow = datarow + body.select('div[class*="layout wrap"]')[:-1]
				#print(body.select('div[class*="read-more__content"]')[0].get_text().encode("utf-8"))
				try:
					datarow.append(body.select('div[class*="read-more__content"]')[0].get_text().encode("utf-8"))
					#print(body.select('div[class*="read-more__content"]')[0].get_text().encode("utf-8"))
				except:
					datarow.append(" ")
				#contact information
				#print("=============contact details information")
				contact=general.find_all("div",{"class":"contact card"})[0]
				try:
					text1 = cleanHtmlTags((contact.select('li[class*="address"]')[0]))
					datarow.append(text1)
					#datarow.append(contact.select('li[class*="address"]')[0].get_text().replace('\n',' ').replace('\r\n',' '))
				except:
					datarow.append(" ")
				try:
					datarow.append(contact.select('li[class*="website"]')[0].select('a')[0].get('href'))
					#datarow.append(contact.select('li[class*="website"]')[0].get_attribute('href').strip())
				except Exception as e:
					#print(str(e),flush=True)
					datarow.append(" ")
				try:
					#datarow.append(contact.select('li[class*="email"]')[0].get_text().strip())
					#print(contact.select('li[class*="email"]')[0].get_text().strip())
					text1 = contact.select('li[class*="email"]')[0].get_text()
					datarow.append(cleanData(text1))	
				except Exception as e:
					#print(str(e))
					datarow.append(" ")
				try:
					datarow.append(contact.select('li[class*="phone"]')[0].get_text().strip())
				except:
					datarow.append(" ")
				#team information
				#print("=============team information")
				try:
					team=sections[0].find_all("section", {"id":"team"})[0].select('h4[class*="team"]')
					list1=[]
					team_text=""
					for text1 in team:
						list2=[]
						list2.append(text1.text.strip())
						list2.append(text1.next_sibling.text.strip())
						list1.append(",".join(filter(None,list2)))
						#list1.append(text1.text.strip() + ", " + text1.next_sibling.text.strip())
					datarow.append(EXCELNEWLINE.join(list1))
				except Exception as e:
					#print(str(e))
					datarow.append(" ")	
				##print(general.encode("utf-8"))
				#funding information
				#print("=============funding information")
				try:
					funding=sections[0].find_all("section", {"id":"funding"})[0].find_all("div",{"class":"section__sub-legend"})
					for text1 in funding:
						datarow.append(text1.next_sibling.text.strip())
				except:
					datarow.append(" ")
				#funding raised information
				#print("=============funding raised information")
				try:
					funding_raised=sections[0].find_all("section", {"id":"funding-raised"})[0].select('tr[class*="investment-round"]')
					#funding_raised2=sections[0].find_all("section", {"id":"funding-raised"})[0]
					list1=[]
					for text1 in funding_raised:
						list2=[]
						for text2 in text1.find_all("div")[:-1]:
							list2.append(text2.text.strip())
						list1.append(",".join(list2))
					datarow.append(EXCELNEWLINE.join(list1))
				except Exception as e:
					datarow.append(" ")
				
			#print("============final result")
			for index1 in range(0,len(datarow)):
				text1 = datarow[index1]
				if type(text1)!=type(str()):
					datarow[index1]=str(text1,"utf-8")
				datarow[index1]=datarow[index1].replace('\n',' ')
				#print(datarow[index1],flush=True)
			#print(datarow)
			writer.writerow(datarow)
			if TEST and i==stop:
				break
		except Exception as e:
			print(str(e))
			print(filename) 
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
