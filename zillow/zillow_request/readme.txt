#readme.txt

#crawl only 1 zipcode
python crawller_zillow.py --zipcode 90001 

#crawl multiple zipcodes from a file
python crawller_zillow.py --zipcode_file resources/zipcodes.txt 

#use different IP addresses from a list
python crawller_zillow.py --zipcode 90001 --proxy_file resources/proxy.txt

#output to a different output file
python crawller_zillow.py --zipcode 90001 --output_file results/temp.csv
