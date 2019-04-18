#!/usr/bin/python                                                                                                      
#coding:utf-8

import pexpect
import sys
import time
#from support_felt_b import *
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i","--ip",   dest="oam_ip",    default='',                   help="Oam ip (eg. 135.252.245.137)")
parser.add_option("--passwd",    dest="passwd",    default="      ",             help="Build version")
parser.add_option("--action",    dest="action",    default="1",                  help="action: add or delete")
parser.add_option("--down_port", dest="down_port", default="1/1/6/19",           help="down_port")
parser.add_option("--up_port",   dest="up_port",   default="nt-a:xfp:4",         help="up_port")
parser.add_option("--vlan_start",dest="vlan_start",default="101",                help="start number of vlan")
parser.add_option("--vlan_num",  dest="vlan_num",  default="1",                  help=" number of vlan")
parser.add_option("--vlan_mode", dest="vlan_mode", default="residential-bridge", help="RB")
(options, args) = parser.parse_args()

ip_OAM     = options.oam_ip
passwd     = options.passwd
action     = options.action
down_port  = options.down_port
up_port    = options.up_port
vlan_start = int( options.vlan_start )
vlan_end   = vlan_start + int( options.vlan_num )
vlan_mode  = options.vlan_mode

#ip_OAM = "135.252.245.52"
#passwd = '      '

exp = pexpect.spawn('telnet %s' % ip_OAM)
def login(ip_OAM,passwd):
	#exp = pexpect.spawn('telnet %s' % ip_OAM)
	exp.timeout = 60
	exp.logfile_read = sys.stdout
	index = exp.expect(['login:','Unable to connect to remote host',pexpect.TIMEOUT])
	if index == 0:
	        exp.sendline('isadmin')
	elif index == 1:
	        sys.exit(1) 
	else:    
	        sys.exit(1) 
	exp.expect('password:')
	exp.sendline(passwd)
	exp.expect('isadmin>#')
login(ip_OAM,passwd)

def sleep_and_exit():
	exp.expect('isadmin')
	exp.sendline( 'exit all' )
	exp.expect('isadmin')
	exp.sendline( ' ' )
	exp.expect('isadmin')

# send CLI command
print( ' >>>>> send CLI command <<<<<  ' )
slot1      = down_port
slot1_type = "lt"
str_num    = 0
for str_id1 in range(len(slot1)):
	if (slot1[str_id1] != "/"):
		continue
	else :
		str_num = str_num + 1
		if (str_num <= 2):
			continue
		else :
			get_num1 = str_id1
			break		
lt1    	    = slot1[0:get_num1]  # "1/1/17"
port1_start = int( slot1[get_num1 + 1 :] )   #"17"
port1_end   = port1_start + 1

slot2      = up_port #"nt-a:xfp:4"  #  >> uplink <<
slot2_type = "lt"
str_num    = 0
if (slot2[0:2] != "nt"):
	for str_id in range(len(slot2)):
		if (slot2[str_id] != "/"):
			continue
		else :
			str_num = str_num + 1
			if (str_num <= 2):
				continue
			else :
				get_num = str_id
				break		
	lt2    	  = slot2[0:get_num]   # "1/1/17"
	port2     = slot2[get_num + 1 :]    #"17"
else :
	slot2_type = "nt"
	
#vlan_start  = 4060
#vlan_end    = vlan_start + 2 #512

def create_BP(a):
	if (slot2_type != "nt"):
		exp.sendline("configure bridge port " + lt2 + "/" + port2 )
	else:
		exp.sendline(" this is NT port ! " )
	sleep_and_exit()
	exp.sendline("configure bridge port " + lt1 + "/" + str(a) )
	sleep_and_exit()
	exp.sendline("configure bridge port " + lt1 + "/" + str(a) + " max-unicast-mac 1000" )
	sleep_and_exit()
def create_VP(a,c):
	print(" >>>>>>>>>>>>> create VLAN <<<<<<<<<<<<<<<< ")
	# create vlan			
	exp.sendline("configure vlan id " + str(c) + " mode " + vlan_mode  )
	sleep_and_exit()
	# create VP
	exp.sendline("configure bridge port " + lt1 + "/" + str(a) + " vlan-id " + str(c) + " vlan-scope network tag single-tagged " )
	sleep_and_exit()
	if (slot2_type != "nt"):
		exp.sendline("configure bridge port " + lt2 + "/" + port2  + " vlan-id " + str(c) + " vlan-scope network tag single-tagged " )
	else:
		exp.sendline(" this is NT port ! " )
	sleep_and_exit()
def create_VPLS(c):
	# VPLS
	exp.sendline("configure service vpls " + str(c) + " customer 1 v-vpls vlan " + str(c) + "  create" )
	exp.sendline("configure service vpls " + str(c) + " sap lt:" + lt1 + ":" + str(c) + " create" )
	if (slot2_type != "nt"):
		exp.sendline("configure service vpls " + str(c) + " sap lt:" + lt2 + ":" + str(c) + " create" )
	else:
		exp.sendline("configure service vpls " + str(c) + " sap " + slot2  + ":" + str(c) + " create" )
	exp.sendline("configure service vpls " + str(c) + " no shutdown" )
	sleep_and_exit()
	#info
	exp.sendline("configure service vpls " + str(c) ) # info configure service | match exact:"600"
	exp.sendline("info " )
	sleep_and_exit()

def delete_VP(a,c):
	print(" >>>>>>>>>>>>> deleting VLAN <<<<<<<<<<<<<<<< " )
	exp.sendline("configure bridge port " + lt1 + "/" + str(a)     + " no vlan-id " + str(c) )
	sleep_and_exit()
	if (slot2_type != "nt"):
		exp.sendline("configure bridge port " + lt2 + "/" + port2  + " no vlan-id " + str(c) )
	else:
		exp.sendline(" this is NT port ! " )
	exp.sendline("configure vlan no id " + str(c) )
	sleep_and_exit()
def delete_VPLS(c):
	exp.sendline("configure service vpls " + str(c) + " sap lt:" + lt1 + ":" + str(c) + " shutdown" )
	sleep_and_exit()
	exp.sendline("configure service vpls " + str(c) + " no sap lt:" + lt1 + ":" + str(c) )
	sleep_and_exit()
	if (slot2_type != "nt"):
		exp.sendline("configure service vpls " + str(c) + " sap lt:" + lt2 + ":" + str(c) + " shutdown" )
		sleep_and_exit()
		exp.sendline("configure service vpls " + str(c) + " no sap lt:" + lt2 + ":" + str(c) )
		sleep_and_exit()
	else:
		exp.sendline("configure service vpls " + str(c) + " sap " + slot2  + ":" + str(c) + " shutdown" )
		sleep_and_exit()
		exp.sendline("configure service vpls " + str(c) + " no sap " + slot2  + ":" + str(c) )
		sleep_and_exit()
	
	exp.sendline("configure service vpls " + str(c) + " shutdown " )
	sleep_and_exit()
	exp.sendline("configure service no vpls " + str(c) )
	sleep_and_exit()
	#info
	exp.sendline("info configure vlan id " + str(c) + " flat " )
	sleep_and_exit()

	
if ( action != "0" and action != "1" ):
	exp.sendline(" >>>>> forbidden input, please check whether in 0-1! <<<<<" )
else:

	# port 1
	for a in range(port1_start,port1_end,1):
		create_BP(a)
			
		# VLAN id
		for c in range(vlan_start,vlan_end,1) :
			if action == "1":
				create_VP(a,c)
				create_VPLS(c)
			else:
				delete_VP(a,c)
				delete_VPLS(c)



