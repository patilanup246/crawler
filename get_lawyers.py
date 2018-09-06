import os, glob, csv
from bs4 import BeautifulSoup
import re, urllib2

FOLDER="./raw/lawyers/"
IN_FILENAME="page"
TEMP_FILENAME="temp.csv"
OUT_FILENAME="results/lawyers.csv"
FILE_EXTENSION=".html"
TEST=False
DELIM=","
stop=1
max_no=len(glob.glob(FOLDER+"*"+FILE_EXTENSION))


#print max_no if TEST else None
filename=""
header=["No","Name","Registration Type", "Job Title","Date of Admission","Key Practice",
	"", "Name of Law Practice", "Type of Law Practice", "Email",
	"Website", "Tel","", "Address"]
count=0
with open(OUT_FILENAME,'w+b') as out_file:
	writer = csv.writer(out_file, delimiter=DELIM, lineterminator="\n") 
	writer.writerow(header)
	for i in range(1,max_no):
		filename=FOLDER+IN_FILENAME+str(i)+FILE_EXTENSION
		with open(filename) as html_file:
			soup=BeautifulSoup(html_file,'lxml')
			top_table=soup.find_all('table',{'id':'Tbl_Search'})[0]
			tables=top_table.find_all('table',{'class':'table lsra-search'})
			for table in tables:
				datarow=[]
				count+=1
				datarow.append(str(count))
				rows = table.findChildren(['th','tr'])
				for row in rows[1:]:
					cells = row.findChildren('td')
					for cell in cells:
						if cell.string is None:
							datarow.append("")
							continue
						#print repr(cell.string) if TEST else do_nothing() 
						text = str(cell.string.encode('utf8','ignore').strip())
						text = text.replace('\r',' ').replace('\n',' ').replace('  ',' ')
						#print repr(text) if TEST else do_nothing() 
						if text.startswith("+") or text.startswith("-"):
							text = '\''+text
						datarow.append(text)
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

