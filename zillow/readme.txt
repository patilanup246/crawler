#readme.txt

The script has two modes:
(1) download all data to local folders and parse them one by one
(2) crawl the zillow website and get data on the fly


(1) download all data to local folders and parse the html files:
#download file to local folder ./raw
crawler_zillow.py download --zipcode 90001
crawler_zillow.py download --zipcode_file zip_codes.txt 

#parse all files in the local folder ./raw, the output will be in ./output.csv
crawller_zillow.py parse

(2) crawl the zillow webssite and get data on the fly
#crawl the zillow website on the fly and output to ./output.csv
crawller_zillow.py crawl --zipcode 90001

#crawl the zillow website based on the lsit of zipcodes and  and output to ./output.csv
crawller_zillow.py crawl --zipcode_file zip_codes.txt 

#optional: write to a different output file
crawller_zillow.py crawl --zipcode_file zip_codes.txt --output_file ./output2.csv
crawller_zillow.py parse --output_file ./output3.csv

