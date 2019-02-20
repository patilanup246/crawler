#!/usr/bin/env python
import sys
from checker import checker
from colorama import Fore
from os import system as term
sys.dont_write_bytecode = True

phile=sys.argv[1]
filer=open(phile)
filer=list(filer)
checker=checker()
for item in filer:
    if checker.check(item):
        print(Fore.RED+'Bad proxy',item)
    else:
        phile=open('good.txt','w')
        phile.write(item)
        print(Fore.GREEN+'Good proxy',item)
