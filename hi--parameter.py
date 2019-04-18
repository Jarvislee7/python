#!/usr/bin/python
#coding:utf-8

import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--num","-n", dest="num",default="1", help="numbers")
(options, args) = parser.parse_args()

num=int(options.num)

def laugh():
    print 'Ha '

if __name__ == "__main__":

    for i in range (1,num):
        print i
	for j in range (1,i+1):
	        laugh()

