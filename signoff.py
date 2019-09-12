#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
This Script used for IME Mechanic Test Shipping
Script prefer for IME PV team use
'''

import os
import sys
import subprocess
import argparse
import difflib
import requests
import color
from bs4 import BeautifulSoup

PARSER = argparse.ArgumentParser()
PARSER.add_argument("Base", type=str, help="Base bug list, check Bugzilla comment. \
Please copy Bugzilla comment bug list(exclude Patch bug) to a file. Within content is ok")
PARSER.add_argument("Final", type=str, help="Ship readme bug list, check final  \
readme review file. Please copy final readme review file bug list to another file. \
 Within content is ok")
PARSER.add_argument("-d", "--draft", type=str, help="Draft readme file you want \
compare to final readme. It will compare FINAL against DRAFT")
ARGS = PARSER.parse_args()

'''
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Global Variable >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'''

#1. User setup variables according to target
#BASEFILE = './Base'
#FINALFILE = './Final'

#2. Common variables, not change normally
BASEFILE = ARGS.Base
FINALFILE = ARGS.Final
DRAFTFILE = ARGS.draft

'''
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Class Define >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'''

class Logger(object):
    '''logger'''
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "w+")
    def write(self, message):
        '''write'''
        self.terminal.write(message)
        self.log.write(message)
    def close(self):
        '''close'''
        # Redirect to console
        sys.stdout = self.terminal
        # Close file to save content
        self.log.close()

    def flush(self):
        '''flush'''
        pass

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Function Define >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def get_fed_list(base_file):
    '''get fed list'''
    cmd = "cat " + base_file
    ret = subprocess.check_output(cmd, shell=True)
    print "\nBase Bug Content: \n%s\n" % ret
    cmd = 'cat ' + base_file + " | grep ') Bug ' | awk '{print $3}' | sort"
    ret = subprocess.check_output(cmd, shell=True)
    fed_list = ret.split()
    print "\nFED List: %s\n" % fed_list
    return fed_list

def get_rfd_list(fed_list):
    '''get rfd list'''
    sys.stdout = Logger('./Temp')
    for fed in fed_list:
        all_url = 'http://bug-fixed-where.dev.sea1.apps.isilon.com/search/?bug='+ str(fed)
        print fed,
        fix_where = requests.get(all_url)
        soup = BeautifulSoup(fix_where.text, 'html.parser')
        #print(soup)
        rfd = soup.find_all('td', limit=2)
        for txt in rfd:
            print txt.get_text(),
        print
    # Redirect to console
    sys.stdout.close()

    cmd = "cat ./Temp | awk '{print $2}' | sort"
    ret = subprocess.check_output(cmd, shell=True)
    rfd_list = ret.split()
    print "\nRFD List: %s\n" % rfd_list
    clean_up('./Temp')
    return rfd_list

def get_ship_bug(final_file):
    '''get ship bug'''
    cmd = "cat " + final_file
    ret = subprocess.check_output(cmd, shell=True)
    print "\nShip Bug Content: \n%s\n" % ret
    cmd = "cat " + final_file + " | grep '* Bug ID ' | awk '{print $4}' | sort"
    ret = subprocess.check_output(cmd, shell=True)
    ship_bug = ret.split()
    print "\nShip Readme Bug List: %s\n" % ship_bug
    return ship_bug

def cmp_rfd_ship(rfd_list, ship_bug):
    '''cmp rfd bug with ship bug'''
    print "\n RFDs  |  Bugs"
    print "---------------"
    for rfd in rfd_list:
        if rfd in ship_bug:
            print "%s = %s" % (rfd, rfd)
        else:
            print color.use_style("%s is not in Ship Readme Bugs" % rfd, fore='red', mode='bold')
    for bug in ship_bug:
        if bug not in rfd_list:
            print color.use_style("%s is not in RFDs List" % bug, fore='red', mode='bold')

def clean_up(clean_file):
    '''clean up config '''
    cmd = 'rm -rf ' + clean_file
    os.system(cmd)

def check_duplicate(fed_list, rfd_list, ship_list):
    '''check duplicate'''
    #1. Check FED list
    for item in fed_list:
        if fed_list.count(item) > 1:
            print color.use_style("\n%s is found duplicate for: %d times in FED list!\n " \
                  % (item, fed_list.count(item)), fore='red', mode='bold')
    #2. Check RFD list
    for item in rfd_list:
        if rfd_list.count(item) > 1:
            print color.use_style("\n%s is found duplicate for: %d times in RFD list!\n " \
                  % (item, rfd_list.count(item)), fore='red', mode='bold')
    #3. Check Ship list
    for item in ship_list:
        if ship_list.count(item) > 1:
            print color.use_style("\n%s is found duplicate for: %d times in Ship list!\n" \
                  % (item, ship_list.count(item)), fore='red', mode='bold')

def cmp_final_readme(draft_reame, final_readme):
    '''cmp final readme'''
    with open(draft_reame, 'r') as d_fd:
        d_content = d_fd.readlines()
    with open(final_readme, 'r') as f_fd:
        f_content = f_fd.readlines()
    diff = difflib.HtmlDiff()
    result = diff.make_file(d_content, f_content)
    with open('./Draft_Final_Compare.html', 'w+') as file_handle:
        file_handle.writelines(result)
    print "\nCompared result file 'Draft_Final_Compare.html' created successfully!\n"


# <<<< Main Function >>>>


if __name__ == '__main__':
    print color.use_style("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 1. \
Get Base FEDs List <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n", fore='blue', mode='bold')
    FED_LIST = get_fed_list(BASEFILE)

    print color.use_style("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 2. \
Get Related RFDs List <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n", fore='blue', mode='bold')
    RFD_LIST = get_rfd_list(FED_LIST)

    print color.use_style("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 3. \
Get Ship Readme Bugs List <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n", fore='blue', mode='bold')
    SHIP_BUG = get_ship_bug(FINALFILE)

    print color.use_style("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 4. \
Final RFDs against Ship Bugs <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n", fore='blue', mode='bold')
    cmp_rfd_ship(RFD_LIST, SHIP_BUG)

    print color.use_style("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 5. \
Check Duplicate Bugs in FED/RFD/Ship <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\
<<<<\n", fore='blue', mode='bold')
    check_duplicate(FED_LIST, RFD_LIST, SHIP_BUG)

    if DRAFTFILE is not None:
        print color.use_style("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 6. \
Final draft readme against final readme <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\
<<<\n", fore='blue', mode='bold')
        cmp_final_readme(DRAFTFILE, FINALFILE)

    print color.use_style("\nAll tasks done!\n", fore='green', mode='bold')
