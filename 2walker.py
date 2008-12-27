#!/usr/bin/env python

import os
from updatelib import *
import re

config = '/root/test.cfg'

lines = readConf(config)
rootdir2,rootdir1,excludedirs,excludefiles,outputdir = configParserForWalker(lines)

trim1 = setTrim(rootdir1)
trim2 = setTrim(rootdir2)
oldfiles = index(rootdir2,trim2,excludedirs,excludefiles)
newfiles = index(rootdir1,trim1,excludedirs,excludefiles)

added,removed,changed = fileLists(oldfiles,newfiles)
addedline   = putFileListInLine(added)
removedline = putFileListInLine(removed)
changedline = putFileListInLine(changed)

writeFileList(addedline,outputdir,'added.txt')
writeFileList(removedline,outputdir,'removed.txt')
writeFileList(changedline,outputdir,'changed.txt')
