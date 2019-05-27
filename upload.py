#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import time
import bugzilla
sys.path.append(r'/root/ljw/workflow_tools')
sys.path.append(r'/root/ljw/pv_automation')
from fabric import api as fab
import paramiko  # 用于调用scp命令
from pv_automation.bugs import BugHandler as addattach
#from scp import SCPClient

''' <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Function Define >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> '''

###########################
#upload 1st way
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
#upload 2nd way
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

#upload()
#fab_remote()


###########################
#update bug 1st way
###########################
files = ['patch-243995.pkg','patch-243995.tgz','README']
def add_md5_sha():
    fab.env.user = 'root'
    fab.env.password = 'a'
    fab.env.prompts = DEFAULT_PATCH_PROMPTS
    fab.env.host_string = '10.7.145.67'
    with fab.cd('/root/test'):
	uld1    = fab.run('echo Patch uploaded to dogpools: ')
	uld2    = fab.run('echo http://dog-pools.west.isilon.com/data/patches/temp/%s' % files[1] )
	uld3    = fab.run('echo http://dog-pools.west.isilon.com/data/patches/temp/{}'.format(files[1])  )
	premd5  = fab.run('echo MD5s:')
	md5s    = fab.run('md5sum {}'.format(' '.join(files)))
	presha  = fab.run('echo SHAs:')
	sha256s = fab.run('sha256sum {}'.format(' '.join(files)))

        uld_all = """
Patch uploaded to dogpools:
http://dog-pools.west.isilon.com/data/patches/temp/{tgz}

MD5s:
{md5}

SHAs:
{sha256}
""".format(tgz=files[1],md5=md5s,sha256=sha256s) #% (files[1],md5s,sha256s)
        print uld_all
	
	SVC_USER = 'jlee1'
	SVC_PSWD = '&UJM,ki88'
	bug = addattach('https://bugs.west.isilon.com',SVC_USER,SVC_PSWD)
	bug.add_comments(246992,uld_all)

add_md5_sha()


###########################
#update bug 2nd way
###########################
def tar_patch(patch_pkg_name):
   patch_tgz_name = patch_pkg_name.replace('pkg', 'tgz')
   run_cmd('tar -zcvf {} {} README'.format(patch_tgz_name, patch_pkg_name))
   if not os.path.exists(patch_tgz_name):
       raise Exception('file not found')
   _, md5_value,_ = run_cmd('md5sum {} {} README'.format(patch_tgz_name, patch_pkg_name))
   _, sha256_value,_ = run_cmd('sha256sum %s %s README' % (patch_tgz_name, patch_pkg_name))
   url = 'http://dog-pools.west.isilon.com/data/patches/temp/' + patch_tgz_name
   return 'Patch uploaded to dogpools:\n{}\n\nMD5:\n{}\nSHA256:\n{}'.format(url, md5_value, sha256_value)

tar_patch(files[0])

