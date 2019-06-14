#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"duc extend"

import re
from optparse import OptionParser
from fabric import api as fab

DEFAULT_PATCH_PROMPTS = {
    'Would you like to proceed?': 'yes',
    'are you sure? (yes/[no]): ': 'yes',
    'you would like to do this?? (yes/[no]):': 'yes',
    'Are you sure you want to continue connecting (yes/no)?':'yes',
}

parser = OptionParser()
parser.add_option("--user", dest="user", default='jlee1', help="user")
parser.add_option("--passwd", dest="passwd", default="&UJM,ki882", help="password")
(options, args) = parser.parse_args()
login_usr = options.user
login_psw = options.passwd

def duc_extend():
    """extend ductnet"""
    fab.env.user = login_usr #'jlee1'
    fab.env.password = login_psw #'&UJM,ki882'
    fab.env.prompts = DEFAULT_PATCH_PROMPTS
    fab.env.host_string = 'remotedev04.prod.sea1.west.isilon.com'
    lst = fab.run('dt vcluster list | grep "id:" | awk \'{print $2}\' ')
    cluster_list = re.findall(r'\n(\d+)', lst)
    print cluster_list

    for i_ls in cluster_list:
        print "####################################################################"
        print "cluster: ", i_ls
        fab.run('curl https://ducttape.west.isilon.com/api/v2.0/clusters/' \
                 + i_ls + '/extend')
        print "####################################################################"
        print ""

    lst2 = fab.run('dt vclient list | grep "id:" | awk \'{print $2}\' ')
    client_list2 = re.findall(r'\n(\d+)', lst2)
    for j_ls in client_list2:
        print "####################################################################"
        print "client: ", j_ls
        fab.run('curl https://ducttape.west.isilon.com/api/v2.0/clients/' \
                 + j_ls + '/extend')
        print "####################################################################"
        print ""


def main():
    """"main program"""
    duc_extend()


if __name__ == '__main__':
    main()
