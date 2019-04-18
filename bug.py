#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import bugzilla
from hi import *

if __name__ == "__main__":
    bug = bugzilla.Bugzilla('https://bugs.west.isilon.com','jlee1','$RFVbgt55')
    bug
    dir(bug)
    aa=bug.getbug('243891')
    print(aa.keywords)
    print(aa.status)
    laugh()