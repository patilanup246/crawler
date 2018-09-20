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
		with open(filename, encoding="utf-8") as html_file:
			soup=BeautifulSoup(html_file,'html.parser')
			sections=soup.find_all('section')
			print(len(sections)) 
			if len(sections)<3: 
				break
			#general=sections[0].text.encode("utf-8")
			general=sections[0].find_all("section", {"id":"general"})[0]
			heading=general.find_all("div",{"class":"flex md9 column"})[0]
			list1=[]
			for text1 in heading.text.strip().split(NEWLINE):
				list1.append(text1.encode("utf-8").strip())
			for text1 in list1:
				print(text1)
			body=general.find_all("div",{"class":"flex entity__details xs12"})[0]
			details=body.find_all("div",{"class":"flex section__legend xs12 md3"})
			for text1 in details:
				print(text1.text)
	
			#print(",".join(list1))
			#print(heading.text.encode("utf-8").strip())
			team=sections[0].find_all("section", {"id":"team"})[0].find_all("h4")
			print("leng team: ",len(team))
			for text1 in team[1:]:
				print(text1.text.strip(), text1.next_sibling.text.strip())
			general=sections[0].text
			#print(general.encode("utf-8"))
			funding=sections[0].find_all("section", {"id":"funding"})[0].find_all("div",{"class":"section__sub-legend"})
			for text1 in funding:
				print(text1.text.strip(),  text1.next_sibling.text.strip())
			funding_raised=sections[0].find_all("section", {"id":"funding-raised"})[0].find_all("tr",{"class":"investment-round hasToggle"})
			for text1 in funding_raised:
				list1=[]
				for text2 in text1.find_all("div")[:-1]:
					list1.append(text2.text.strip())
				print(",".join(list1))
			#name=top_table.find('h1')
			#print name.text.replace('\r',' ').replace('\n',' ').strip()
			#datarow.append(name.text.replace('\r',' ').replace('\n',' ').strip())

			###############
			#row1=top_table.find_all('p',{'class':'control-group'})[2]
			#spans=row1.find_all('span')
			#list1=[]
			#for span in spans:
			#	span_text = span.text.replace('\r',' ').replace('\n',' ').strip()
			#	#span_text=span.text.encode('utf8','ignore').replace('\r',' ').replace('\n',' ').strip()
			#	#span_text=span_text.replace('\xc2',' ').replace('\xa0',' ').strip()
			#	list1.append(span_text)		
			#list1 = filter(None,list1)
			#address=" ".join(list1)
			##print address
			#datarow.append(address)
			###############
			#row2=row1.findNext('div',{'class':'col-md-6'})
			#list1=[]
			##for detail in details.strings:
			#for detail in row2.findAll(text=True):
			#	#detail=detail.encode('utf8','ignore').replace('\r',' ').replace('\n',' ').replace('\xc2',' ').replace('\xa0',' ').strip()
			#	detail=detail.replace('\r',' ').replace('\n',' ').replace('\xc2',' ').replace('\xa0',' ').strip()
			#	list1.append(detail)
			#list1= filter(None,list1)
			#datarow+=list1
			##datarow.append(",".join(list1))
			###############
			#row3=row2.findNext('div')
			#contact=row3.text.replace('\r','').replace('\n','')
			#datarow.append(contact)
			##print repr(contact)
			#row5=top_table.findAll('div',{'class':'row'})[5]
			#details=row5.findAll('span',{'class':'data-font'})
			#list1=[]
			#for detail in details:
			#	list1.append(detail.text)
			#list1= filter(None,list1)
			##print ",".join(list1)
			##print list1
			##datarow=datarow + list1
			#datarow.append(",".join(list1))
			###################print list1
			#row6=top_table.findAll('div',{'class':'row'})[6].findChildren('td')[0]
			#profile=row6.text.replace('\n',' ').replace('\r',' ').strip()
			#profile=row6.text.replace("-","-").encode('utf8').replace("\\xe2\\x80\\x99","'").replace('\r',' ').replace('\n',' ')
			#datarow.append(profile)
		print(datarow)
		writer.writerow(datarow)
		if TEST and i==stop:
			break

