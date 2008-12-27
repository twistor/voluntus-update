#!/usr/bin/env python
from updatelib import *

config = '/root/test.cfg'

lines = readConf(config)
rootdir2,rootdir1,excludedirs,excludefiles,outputdir = configParserForWalker(lines)
print rootdir2
print rootdir1
print excludedirs
print excludefiles
print outputdir
