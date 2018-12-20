import requests
from itertools import cycle
import traceback
import time, glob, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#If you are copy pasting proxy ips, put in the list below
#proxies = ['121.129.127.209:80', '124.41.215.238:45169', '185.93.3.123:8080', '194.182.64.67:3128', '106.0.38.174:8080', '163.172.175.210:3128', '13.92.196.150:8080']
#proxies = get_proxies()
proxies = ["81.30.71.165:80"]

proxy_pool = cycle(proxies)

url = 'https://httpbin.org/ip'
for i in range(1,len(proxies)+1):
    #Get a proxy from the pool
    proxy = next(proxy_pool)
    print(proxy)
    print("Request #%d"%i)
    try:
        response = requests.get(url,proxies={"http": proxy, "https": proxy},verify=False, timeout=5 )
        print(response.json())
    except Exception as e:
        #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
        #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
        print("Skipping. Connnection error", e)
        pass

response = requests.get(url, verify=False)
print(response.json())
