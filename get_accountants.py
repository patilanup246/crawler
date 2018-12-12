import os, glob, csv
from bs4 import BeautifulSoup
import re,  codecs

FOLDER="./raw/accountants/"
IN_FILENAME="page"
TEMP_FILENAME="temp.csv"
OUT_FILENAME="results/accountants.csv"
FILE_EXTENSION=".html"
TEST=False
DELIM=","
stop=1
max_no=len(glob.glob(FOLDER+"*"+FILE_EXTENSION))


#print max_no if TEST else None
filename=""
header=["No","Name","Adress", "Phone","Fax","Email",
	"Website", "Executive Contact", "Classifications", "Company Profile"]
with open(OUT_FILENAME,'w',encoding='utf-8' ) as out_file:
	writer = csv.writer(out_file, delimiter=DELIM, lineterminator="\n") 
	writer.writerow(header)
	for i in range(1,max_no):
		filename=FOLDER+IN_FILENAME+str(i)+FILE_EXTENSION
		datarow=[]
		datarow.append(str(i))
		with open(filename) as html_file:
			soup=BeautifulSoup(html_file,'html.parser')
			top_table=soup.find_all('div',{'id':'directoryDetails'})[0]
			name=top_table.find('h1')
			#print name.text.replace('\r',' ').replace('\n',' ').strip()
			datarow.append(name.text.replace('\r',' ').replace('\n',' ').strip())

			##############
			row1=top_table.find_all('p',{'class':'control-group'})[2]
			spans=row1.find_all('span')
			list1=[]
			for span in spans:
				span_text = span.text.replace('\r',' ').replace('\n',' ').strip()
				#span_text=span.text.encode('utf8','ignore').replace('\r',' ').replace('\n',' ').strip()
				#span_text=span_text.replace('\xc2',' ').replace('\xa0',' ').strip()
				list1.append(span_text)		
			list1 = filter(None,list1)
			address=" ".join(list1)
			#print address
			datarow.append(address)
			##############
			row2=row1.findNext('div',{'class':'col-md-6'})
			list1=[]
			#for detail in details.strings:
			for detail in row2.findAll(text=True):
				#detail=detail.encode('utf8','ignore').replace('\r',' ').replace('\n',' ').replace('\xc2',' ').replace('\xa0',' ').strip()
				detail=detail.replace('\r',' ').replace('\n',' ').replace('\xc2',' ').replace('\xa0',' ').strip()
				list1.append(detail)
			list1= filter(None,list1)
			datarow+=list1
			#datarow.append(",".join(list1))
			##############
			row3=row2.findNext('div')
			contact=row3.text.replace('\r','').replace('\n','')
			datarow.append(contact)
			#print repr(contact)
			row5=top_table.findAll('div',{'class':'row'})[5]
			details=row5.findAll('span',{'class':'data-font'})
			list1=[]
			for detail in details:
				list1.append(detail.text)
			list1= filter(None,list1)
			#print ",".join(list1)
			#print list1
			#datarow=datarow + list1
			datarow.append(",".join(list1))
			##################print list1
			row6=top_table.findAll('div',{'class':'row'})[6].findChildren('td')[0]
			profile=row6.text.replace('\n',' ').replace('\r',' ').strip()
			#profile=row6.text.replace("-","-").encode('utf8').replace("\\xe2\\x80\\x99","'").replace('\r',' ').replace('\n',' ')
			datarow.append(profile)
		print(datarow)
		writer.writerow(datarow)
		if TEST and i==stop:
			break

#with open(TEMP_FILENAME,'r') as infile, open(OUT_FILENAME, 'w+b') as outfile:
#	new_header=["Name","Job Title", "Registration Type", "Date of Admission","Key Practice",
#	"Name of Law Practice", "Type of Law Practice", "Email",
#	"Tel", "Address"]
#	writer = csv.DictWriter(outfile, fieldnames=new_header, extrasaction='ignore', delimiter = DELIM)
#	writer.writeheader()
#	for row in csv.DictReader(infile):
#		writer.writerow(row)

