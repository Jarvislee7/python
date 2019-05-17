#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import time
from fabric import api as fab
import paramiko  # 用于调用scp命令
#from scp import SCPClient

''' <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Function Define >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> '''

###########################
# 1st way
###########################
def upload( remote_path="/root/test2/", file_path="./package/README"):
    print 
    print ' >>>>>>>>>>>>>>>>>>>>> 1st way <<<<<<<<<<<<<<<<<<<<<<<<<<'
    print 
    host = "10.7.145.67"  # 服务器ip地址
    port = 22  # 端口号
    username = "root"  # ssh 用户名
    password = "a"  # 密码
    file_tgz = "patch-243995.tgz"
    file_path   = "/root/ljw/package/" + file_tgz
    remote_path = "/root/test2/" + file_tgz

    ssh = paramiko.SSHClient()#这行代码的作用是允许连接不在know_hosts文件中的主机。
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host,  port, username, password)

    stdin, stdout, stderr = ssh.exec_command('cd /root/test2; ls' )
    print stdout.readlines()
    print stderr.readlines()

    sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
    try:
	sftp.put(file_path, remote_path)
    except FileNotFoundError as e:
        print("系统找不到指定文件" + local_path)
    else:
        print("文件上传成功")
    sftp.close()
    ssh.close()


###########################
# 2nd way
###########################
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
}

def fab_remote():
    print 
    print ' >>>>>>>>>>>>>>>>>>>>> 2nd way <<<<<<<<<<<<<<<<<<<<<<<<<<'
    print 
    fab.env.user = 'root'
    fab.env.password = 'a'
    fab.env.prompts = DEFAULT_PATCH_PROMPTS
    fab.env.host_string = '10.7.145.67'
#    fab.env.host_string = '10.224.37.177'
    with fab.cd('/root/test'):
	fab.run('ls')
	fab.put('./package/*','/root/test')
	fab.run('ls | grep -E "README|pkg|tgz"')

upload()
fab_remote()



