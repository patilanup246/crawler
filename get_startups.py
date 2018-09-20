#!python
# -*- coding: utf-8 -*-
import os, glob, csv
from bs4 import BeautifulSoup
import re,  codecs

FOLDER="./raw/startups/"
IN_FILENAME="record"
TEMP_FILENAME="temp.csv"
OUT_FILENAME="results/startups.csv"
FILE_EXTENSION=".html"
TEST=True
DELIM=","
NEWLINE="\n"
stop=243
start_no=243
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
			print(heading.encode("utf-8"))
			list1=[]
			for text1 in heading.select('div'):
				print(text1.text.encode("utf-8"))
			#print(heading.encode("utf-8"))
			#for text1 in heading.text.encode("utf-8").strip().split(NEWLINE):
				#list1.append(text1.encode("utf-8").strip())
				#list1.append(text1)
			#for text1 in list1:
			#	print(text1)
				#datarow.append(text1)
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
			datarow.append(body.select('div[class*="read-more__content"]')[0].get_text().encode("utf-8"))
			#contact information
			print("=============contact details information")
			contact=general.find_all("div",{"class":"contact card"})[0]
			datarow.append(contact.select('li[class*="address"]')[0].get_text().encode("utf-8"))
			datarow.append(contact.select('li[class*="website"]')[0].get_text().strip())
			datarow.append(contact.select('li[class*="email"]')[0].get_text().strip())
			datarow.append(contact.select('li[class*="phone"]')[0].get_text().strip())
			#team information
			print("=============team information")
			team=sections[0].find_all("section", {"id":"team"})[0].select('h4[class*="team"]')
			team1=sections[0].find_all("section", {"id":"team"})[0]
			team_text=""
			for text1 in team:
				team_text += text1.text.strip() + ","
				team_text += text1.next_sibling.text.strip() + "\r\n"
			datarow.append(team_text)
			general=sections[0].text
			#print(general.encode("utf-8"))
			#funding information
			print("=============funding information")
			funding=sections[0].find_all("section", {"id":"funding"})[0].find_all("div",{"class":"section__sub-legend"})
			for text1 in funding:
				datarow.append(text1.next_sibling.text.strip())
			#funding raised information
			print("=============funding raised information")
			funding_raised=sections[0].find_all("section", {"id":"funding-raised"})[0].find_all("tr",{"class":"investment-round hasToggle"})
			list1=[]
			for text1 in funding_raised:
				list2=[]
				for text2 in text1.find_all("div")[:-1]:
					list2.append(text2.text.strip())
				list1.append(",".join(list2))
			datarow.append("\r\n".join(list1))
			
		print("============final result")
		for text1 in datarow:
			print(text1.encode("ascii"))
		print(datarow)
		writer.writerow(datarow)
		if TEST and i==stop:
			break

