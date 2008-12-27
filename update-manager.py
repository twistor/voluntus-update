#!/usr/bin/env python
from updatelib import *

mask,addfilename,updatefilename,removefilename = optionsParserForUpdateManager()
createLogFile()
hostlist = getHostList()

addfile    = readFileList(addfilename)
addfile    = breakUpFileList(addfile)

updatefile = readFileList(updatefilename)
updatefile = breakUpFileList(updatefile)

removefile = readFileList(removefilename)
removefile = breakUpFileList(removefile)

for hostname,hostkey,clientkey in hostlist:
    client = connectToHost(hostname,hostkey,clientkey)
    sftp = client.open_sftp()
    for file in addfile:
        filePut(file[0],file[1],file[2],file[3],mask,sftp)
    for file in updatefile:
        fileUpdate(file[0],file[1],file[2],file[3],sftp)
    for file in removefile:
        fileRemove(file[0],sftp)
    sftp.close()
    client.close()
#testing out git

print 'happy happy joy joy'