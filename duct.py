#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"duc extend"

import re
from fabric import api as fab

DEFAULT_PATCH_PROMPTS = {
    'Would you like to proceed?': 'yes',
    # The uninstall command prompt when a patch may be rebooted.
    'Would you like to proceed? (yes/[no]):': 'yes',
    'Would you like to proceed? (yes/[no]): ': 'yes',
    'Would you like to continue? [yes/No]:': 'yes',
    'Would you like to continue?  [yes/No]:': 'yes',
    # Used for all kinds of confirmations - install, uninstall, abort, archive.
    'Are you sure? (yes/[no]): ': 'yes',
    'Are you sure? (yes/[no]):': 'yes',
    'are you sure? (yes/[no]): ': 'yes',
    # The SECOND upgrade confirmation after running archive framework
    'you would like to do this?? (yes/[no]):': 'yes',
    'Are you sure you want to continue connecting (yes/no)?':'yes',
}


def duc_extend():
    """extend ductnet"""
    fab.env.user = 'jlee1'
    fab.env.password = '&UJM,ki88'
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
