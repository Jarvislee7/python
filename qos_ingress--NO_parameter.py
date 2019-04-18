#!/usr/bin/python
#coding:utf-8

import pexpect
import sys
import time
from support_felt_b import *

ip_OAM = "135.252.245.52"
passwd = '      '

login(ip_OAM,passwd)

# send CLI command
print( ' >>>>> send CLI command <<<<<  ' )

slot      = "1/1/1/1" 
lt_mode   = "downlink"
action    = "0"        # [0:del] [1:add] [other:quit]
ing_start = 11
ing_end   = ing_start + 29
str_num   = 0
for str_id in range(len(slot)):
	if (slot[str_id] != "/"):
		continue
	else :
		str_num = str_num + 1
		if (str_num <= 2):
			continue
		else :
			get_num = str_id
			break
lt    	  = slot[0:get_num]   #"1/1/17"
port      = slot[get_num + 1 :]    #"17"
prt  	  = slot        #lt + "/" + port
trans 	  = lt + ":sfp:" + port 

if ( action != "0" and action != "1" ):
	exp.sendline(" >>>>> forbidden input, please check whether in 0-1! <<<<<" )
	sleep_and_exit()
elif ( action == "1"):
	exp.sendline(" >>>>> adding qos ingress! <<<<<" )
	for i in range(ing_start,ing_end,1):
		id = str(i)
		exp.sendline( ' configure vlan id 12' + id + ' mode cross-connect' )
		sleep_and_exit()
		exp.sendline( ' configure qos profiles ingress-qos ing_' + id + ' dot1-p0-tc 0 dot1-p1-tc 1 dot1-p2-tc 2 dot1-p3-tc 3 dot1-p4-tc 4 dot1-p5-tc 5 dot1-p6-tc 6 dot1-p7-tc 7 dot1-p0-color yellow dot1-p1-color yellow dot1-p2-color yellow dot1-p3-color yellow dot1-p0-pol-tc 0 dot1-p1-pol-tc 1 dot1-p2-pol-tc 2 dot1-p3-pol-tc 3 dot1-p4-pol-tc 4 dot1-p5-pol-tc 5 dot1-p6-pol-tc 6 dot1-p7-pol-tc 7 ' )
		sleep_and_exit()
		exp.sendline( ' configure vlan id 12' + id + ' in-qos-prof-name name:ing_' + id )
		sleep_and_exit()
else :
	exp.sendline(" >>>>> deleting qos ingress! <<<<<" )
	for i in range(ing_start,ing_end,1):
		id = str(i)
		exp.sendline( ' configure vlan id 12' + id + ' no in-qos-prof-name ' )
		sleep_and_exit()
		exp.sendline( ' configure qos profiles no ingress-qos ing_' + id  )
		sleep_and_exit()
		exp.sendline( ' configure vlan no id 12' + id )
		sleep_and_exit()
exp.sendline( ' info configure qos profiles ingress-qos flat ' )
sleep_and_exit()


