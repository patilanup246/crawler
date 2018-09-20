#!python
# -*- coding: utf-8 -*-
import os, glob, csv
from bs4 import BeautifulSoup
import re,  codecs, sys

FOLDER="./raw/startups/"
IN_FILENAME="record"
TEMP_FILENAME="temp.csv"
OUT_FILENAME="results/startups.csv"
FILE_EXTENSION=".html"
TEST=True
DELIM=","
NEWLINE="\n"
stop=1
start_no=1
max_no=len(glob.glob(FOLDER+"*"+FILE_EXTENSION))


#print max_no if TEST else None
print(max_no)
filename=""
header=["No","Name","Adress", "Phone","Fax","Email",
	"Website", "Executive Contact", "Classifications", "Company Profile"]
with open(OUT_FILENAME,'w',encoding="utf-8" ) as out_file:
	writer = csv.writer(out_file, delimiter=DELIM, lineterminator="\n") 
	writer.writerow(header)
	for i in range(start_no,max_no):
		filename=FOLDER+IN_FILENAME+str(i)+FILE_EXTENSION
		datarow=[]
		datarow.append(str(i))
		try:
			with open(filename, 'r', encoding="utf-8") as html_file:
				soup=BeautifulSoup(html_file,'html.parser')
				sections=soup.find_all('section')
				print(len(sections)) 
				if len(sections)<3: 
					break
				#heading
				general=sections[0].find_all("section", {"id":"general"})[0]
				print("=============header information")
				heading=general.find_all("div",{"class":"flex md9 column"})[0]
				list1=[]
				#print(heading.text.encode("utf-8"))
				print(heading)
				#print(name.get_text())
				
				#for text1 in heading.text.encode("utf-8").strip().split(NEWLINE):
					#list1.append(text1.encode("utf-8").strip())
					#list1.append(text1)
				for text1 in list1:
					print(text1)
					datarow.append(text1)
				#datarow = datarow + list1
				#body details
				print("=============body details information")
				body=general.find_all("div",{"class":"flex entity__details xs12"})[0]
				#for text1 in body.select('div[class*="xs12 md9"]'):
				#	print(text1.get_text().strip().encode("utf-8"))
				for text1 in body.select('div[class*="layout wrap"]')[:-1]:
					datarow.append(text1.find_all('div')[1].text.encode("utf-8").strip())
				#datarow = datarow + body.select('div[class*="layout wrap"]')[:-1]
				#print(body.select('div[class*="read-more__content"]')[0].get_text().encode("utf-8"))
				try:
					datarow.append(body.select('div[class*="read-more__content"]')[0].get_text().encode("utf-8"))
				except:
					datarow.append(" ")
				#contact information
				print("=============contact details information")
				contact=general.find_all("div",{"class":"contact card"})[0]
				try:
					datarow.append(contact.select('li[class*="address"]')[0].get_text().encode("utf-8"))
					datarow.append(contact.select('li[class*="website"]')[0].get_text().strip())
					datarow.append(contact.select('li[class*="email"]')[0].get_text().strip())
					datarow.append(contact.select('li[class*="phone"]')[0].get_text().strip())
				except:
					datarow.append(" ")
					pass
				#team information
				print("=============team information")
				try:
					team=sections[0].find_all("section", {"id":"team"})[0].select('h4[class*="team"]')
					team1=sections[0].find_all("section", {"id":"team"})[0]
					team_text=""
					for text1 in team:
						team_text += text1.text.strip() + ","
						team_text += text1.next_sibling.text.strip() + "\r\n"
					datarow.append(team_text)
				except:
					datarow.append(" ")	
				#print(general.encode("utf-8"))
				#funding information
				print("=============funding information")
				try:
					funding=sections[0].find_all("section", {"id":"funding"})[0].find_all("div",{"class":"section__sub-legend"})
					for text1 in funding:
						datarow.append(text1.next_sibling.text.strip())
				except:
					datarow.append(" ")
				#funding raised information
				print("=============funding raised information")
				try:
					funding_raised=sections[0].find_all("section", {"id":"funding-raised"})[0].find_all("tr",{"class":"investment-round hasToggle"})
					list1=[]
					for text1 in funding_raised:
						list2=[]
						for text2 in text1.find_all("div")[:-1]:
							list2.append(text2.text.strip())
						list1.append(",".join(list2))
					datarow.append("\r\n".join(list1))
				except:
					datarow.append(" ")
				
			print("============final result")
			for j in range(0,len(datarow)):
				text1 = datarow[j]
				if type(text1)!=type(str()):
					datarow[j]=str(text1,"utf-8")
			print(datarow)
			writer.writerow(datarow)
			if TEST and i==stop:
				break
		except Exception as e:
			print(str(e))
			print(filename) 
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			break
