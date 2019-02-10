#!/usr/bin/env python
import os
import re
import csv

FILENAME = "./results/instagram_5000_emails_delivery1.csv"
#FILENAME = "./results/source.csv"
OUTPUT_FILE = "./results/temp.csv"

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def get_email_from_text(str1):
    print(str1.encode('utf-8'))
    #str1 = str1.encode('utf-8')
    email_result = ""
    list2 = []
    tempStr = ""
    count = 0
    for e in str1:
        count = count + 1
        if (re.sub('[ -~]', '', e)) == "":
            # do something here
            tempStr += e
        elif tempStr != "":
            list2.append(tempStr)
            tempStr = ""
        if count == len(str1) and tempStr != "":
            list2.append(tempStr)
            tempStr = ""
    for i in list2:
        if EMAIL_REGEX.match(i):
            email_result = i
            break
    return email_result


with open(FILENAME, 'r', encoding = 'utf-8') as input_file:
    for line in input_file:
        list1 = line.strip().split(',')
        email = get_email_from_text(list1[1])
        print(email)

        if email != "":
            datarow = []
            datarow.append(list1[0])
            datarow.append(email)
            datarow.append(list1[2])
            with open(OUTPUT_FILE, 'a', encoding ='utf-8') as output:
                writer = csv.writer(output, delimiter=",", lineterminator="\n")
                writer.writerow(datarow)
