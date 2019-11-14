#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
This Script used for IME Mechanic Test Shipping
Script prefer for IME PV team use
"""

import collections
import re

import requests
from bs4 import BeautifulSoup

from patch_automation.core.conf import BZ_URL, SVC_PSWD, SVC_USER
from patch_automation.nodetest.log import logger
from common.bug import BugHandler
from pv_automation.verify.check import checks

# command used
FED_ERR = '{}.\nGet FED from comment FAILS, please check manually!'
CONTENT_PATTERN = r'\(\*\) Bug \d{6} - PATCH: \['
FED_PATTERN = r'\s*\(\d{1,3}\) Bug (\d{6}) -'
RFD_PATTERN = r'(\d{6})'
README_PATTERN = r'\* Bug ID (\d{6})\s'
ALL_API = 'http://bug-fixed-where.dev.sea1.apps.isilon.com/search/?bug={}'
CONTENT_ID = 'Find comment {} for patch content.'
FED_LOG = "Get FED from patch depend on:{}\nGet FED from latest comment {}:{}\n"
RFD_PATCH = 'Get RFD from patch depend on:\n {}'
RFD_README = 'Get RFD from README:\n {}'
CHK_DUP = "\n{} is found duplicate for: {} times in {} list!"
FED_CMP1 = "{} is not in latest comment\n"
FED_CMP2 = "{} is not in patch depends\n"
RFD_CMP1 = "{} is not in Ship Readme Bugs\n"
RFD_CMP2 = "{} is not in RFD depend\n"

def get_fed_list(job):
    """
    get fed list
    """
    # get fed from patch depend on, and convert from int to string
    bug_api = BugHandler(BZ_URL, SVC_USER, SVC_PSWD)
    fed_list = map(str, bug_api.get_depends(job.bug))

    # get fed from patch comment
    all_comment = list()
    comment_num = None
    match_comment = ''
    fed_comment = list()
    try:
        all_comment = bug_api.get_comments(job.bug)
    except Exception as error:
        logger.info(FED_ERR.format(error))
    for index, comment_text in enumerate(all_comment):
        if re.findall(CONTENT_PATTERN, comment_text['text']):
            comment_num = index
            logger.info(CONTENT_ID.format(index))
    if comment_num:
        match_comment = all_comment[comment_num]['text']

    fed_comment = re.findall(FED_PATTERN, match_comment)
    logger.info(FED_LOG.format(fed_list, comment_num, fed_comment))
    return fed_list, fed_comment

def get_rfd_list(fed_list):
    """
    get rfd list
    """
    rfd_list = list()
    fed_list = map(int, fed_list)
    for fed in fed_list:
        rfd_num = ''
        fix_where = requests.get(ALL_API.format(fed))
        soup = BeautifulSoup(fix_where.text, 'html.parser')
        rfd = soup.find_all('td', limit=2)
        if rfd:
            rfd_num = re.findall(RFD_PATTERN, rfd[0].get_text().encode('utf-8'))
        rfd_list.append(rfd_num[0])
    logger.info(RFD_PATCH.format(rfd_list))
    return rfd_list

def get_ship_bug():
    """
    get ship bug
    """
    with open('README', 'r') as file_handle:
        content = file_handle.read()
        readme_bug = re.findall(README_PATTERN, content)
    logger.info(RFD_README.format(readme_bug))
    return readme_bug

def is_duplicate(check_list, msg, list_tpye):
    """
    check whether duplicate in check_list
    """
    index = None
    dup = [{item:count} for item, count in \
          collections.Counter(check_list).items() if count > 1]
    if dup:
        for index, _ in enumerate(dup):
            bug = int(dup[index].keys()[0])
            bug_count = dup[index].values()[0]
            logger.info(CHK_DUP.format(bug, bug_count, list_tpye))
            msg += CHK_DUP.format(bug, bug_count, list_tpye)
        return True, msg
    return False, msg

@checks(succ='Check Duplicate Bugs in FED/RFD/Readme')
def check_duplicate(job, label=None, succ=None):
    """
    check duplicate
    """
    fed_list = job.fed_bug_depend
    rfd_list = job.rfd_bug_depend
    ship_list = job.rfd_readme
    fail_result = False
    fail_list = list()
    msg = ''
    # Check FED,RFD,Ship Readme list
    fail_fed, msg = is_duplicate(fed_list, msg, 'FED')
    fail_list.append(fail_fed)
    fail_rfd, msg = is_duplicate(rfd_list, msg, 'RFD')
    fail_list.append(fail_rfd)
    fail_readme, msg = is_duplicate(ship_list, msg, 'Readme')
    fail_list.append(fail_readme)
    if True in fail_list:
        fail_result = True
    job.manifest.add_report(label, succ, msg, failed=fail_result)

@checks(succ='Compare FED between depends-on and comment')
def cmp_feds(job, before=None, after=None, label=None, succ=None):
    """
    Compare FED between depends-on and comment
    """
    fail_result = False
    msg = 'FED_Depends | FED_Comment\n'
    logger.info("\n FED_Depends | FED_Comment")
    fed_list = set(before) if isinstance(before, list) else before
    fed_comment = set(after) if isinstance(after, list) else after
    for fed in fed_list:
        if fed in fed_comment:
            msg += "%s = %s\n" % (fed, fed)
            logger.info("%s = %s" % (fed, fed))
        else:
            msg += FED_CMP1.format(fed)
            fail_result = True
            logger.info(FED_CMP1.format(fed))
    for fed1 in fed_comment:
        if fed1 not in fed_list:
            msg += FED_CMP2.format(fed1)
            fail_result = True
            logger.info(FED_CMP2.format(fed1))
    job.manifest.add_report(label, succ, msg, failed=fail_result)
    return (fail_result, msg)

@checks(succ='Compare RFD between bugzilla and readme')
def cmp_rfd_ship(job, before=None, after=None, label=None, succ=None):
    """
    Compare RFD between bugzilla and readme
    """
    fail_result = False
    msg = 'RFD_Depend | RFD_Readme\n'
    logger.info("\n RFD_Depend | RFD_Readme")
    rfd_list = set(before) if isinstance(before, list) else before
    ship_bug = set(after) if isinstance(after, list) else after
    for rfd in rfd_list:
        if rfd in ship_bug:
            msg += "%s = %s\n" % (rfd, rfd)
            logger.info("%s = %s" % (rfd, rfd))
        else:
            msg += RFD_CMP1.format(rfd)
            fail_result = True
            logger.info(RFD_CMP1.format(rfd))
    for bug in ship_bug:
        if bug not in rfd_list:
            msg += RFD_CMP2.format(bug)
            fail_result = True
            logger.info(RFD_CMP2.format(bug))
    job.manifest.add_report(label, succ, msg, failed=fail_result)
    return (fail_result, msg)

def init_paras(job):
    """
    add parameters to use in job
    """
    job.fed_bug_depend = list()
    job.fed_bug_comment = list()
    job.rfd_bug_depend = list()
    job.rfd_readme = list()

@skippable
def compare_rfd(job):
    """
    Compare rfd bug with ship bug,
    1. compare FED between depends-on and comment
    2. get RFD from depends-on and readme
    3. compare RFD between depends-on and readme
    """
    ### compare FED ###
    init_paras(job)
    # get FED lists
    job.fed_bug_depend, job.fed_bug_comment = get_fed_list(job)
    # compare FED between depends-on and comment
    cmp_feds(job, before=job.fed_bug_depend,
             after=job.fed_bug_comment,
             label='verify_FED',
             succ='Compare FED between depends-on and comment')
    ### compare FRD ###
    # get RFD lists
    job.rfd_bug_depend = get_rfd_list(job.fed_bug_depend)
    job.rfd_readme = get_ship_bug()
    # compare RFD between FED and readme
    cmp_rfd_ship(job,
                 before=job.rfd_bug_depend,
                 after=job.rfd_readme,
                 label='verify_RFD',
                 succ='Compare RFD between bugzilla and readme')
    # Check Duplicate Bugs in FED/RFD/Ship
    check_duplicate(job,
                    label='check_duplicate',
                    succ='Check Duplicate Bugs in FED/RFD/Readme')
