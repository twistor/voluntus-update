#!/usr/bin/env python
import os
import paramiko
import base64
import MySQLdb
import stat
from optparse import OptionParser
import fchksum
import sys

def createLogFile():
    paramiko.util.log_to_file('/tmp/paramiko.log')

def filePut(filename,mode,mask,sftp):
    mode = int(mode,8)
    localfilename = mask+'/'+filename
    try:
        sftp.put(localfilename, filename)
        sftp.chmod(filename,mode)
    except IOError:
        if mkdirRecurs(filename,mask,sftp):
            try:
                sftp.put(localfilename, filename)
                sftp.chmod(filename,mode)
            except error:
                print error
        else:
            print 'mkdirRecurs failed'
            sys.exit()

def fileRemove(filename,sftp):
    try:
        sftp.remove(filename)
    except IOError, error:
        print error

def fileUpdate(filename,mode,sftp):
    mode = int(mode,8)
    try:
        sftp.chmod(filename,mode)
    except IOError, error:
        print error

def readFileList(file):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def writeFileList(list,dir,name):
    f = open(dir + '/' + name, 'w')
    f.writelines(list)
    f.close()

def breakUpFileList(list):
    blist = []
    for file in list:
        file = file.split('\t')
        blist.append([file[0],file[2]],file[3],file[4])
    return blist

def connectToHost(hostname,hostkey,clientkey):
    client = paramiko.SSHClient()
    hkey = paramiko.RSAKey(data=base64.decodestring(hostkey))
#    ckey = not sure how to get this yet
    client.get_host_keys().add(hostname, 'ssh-rsa', hkey)
    try:
        client.connect("", username="sysadmin", port=13833)
        return client
    except paramiko.SSHException, error:
        print error
        client.close()
        return False

def mkdirRecurs(file, mask, sftp):
    fileparts = file.split('/')
    fileparts.pop()
    fileparts.pop(0)
    dir = "/"
    for i in fileparts:
        try:
            mode = getStat(mask+dir)
            sftp.mkdir(dir+i, mode=mode[0])
            sftp.chown(dir+i,mode[1],mode[2])
            return True
        except IOError:
            dir = dir + "/"


def getStat(filename):
    filestat = os.lstat(filename)
    mode=stat.S_IMODE(filestat[stat.ST_MODE])
    uid = filestat[stat.ST_UID]
    gid = filestat[stat.ST_GID]
    U = 0
    G = 0
    O = 0
    S = 0
    if mode & stat.S_IRUSR:
        U = U + 4
    if mode & stat.S_IRGRP:
        G = G + 4
    if mode & stat.S_IROTH:
        O = O + 4
    if mode & stat.S_IWUSR:
        U = U + 2
    if mode & stat.S_IWGRP:
        G = G + 2
    if mode & stat.S_IWOTH:
        O = O + 2
    if mode & stat.S_IXUSR:
        U = U + 1
    if mode & stat.S_IXGRP:
        G = G + 1
    if mode & stat.S_IXOTH:
        O = O + 1
    if mode & stat.S_ISUID:
        S = S + 4
    if mode & stat.S_ISGID:
        S = S + 2
    if mode & stat.S_ISVTX:
        S = S + 1
    return [int(str(S)+str(U)+str(G)+str(O),8),uid,gid]

def index(directory,trim,excludedirs,excludefiles):
    stack = [directory]
    files = []
    while stack:
        directory = stack.pop()
        directory = os.path.abspath(directory)
        for file in os.listdir(directory):
            fullname = os.path.join(directory, file)
            truncname = fullname[trim:]
            if truncname not in excludedirs and truncname not in excludefiles:
                if os.path.isfile(fullname) and not os.path.islink(fullname):
                    mode = getStat(fullname)
                    files.append([truncname,fchksum.fmd5t(fullname)[0],oct(mode[0]),str(mode[1]),str(mode[2])])
                if os.path.isfile(fullname) and os.path.islink(fullname):
                    mode = getStat(fullname)
                    files.append([truncname,"symlink to file",oct(mode[0]),str(mode[1]),str(mode[2])])
                if os.path.isdir(fullname) and os.path.islink(fullname):
                    mode = getStat(fullname)
                    files.append([truncname,"symlink to directory",oct(mode[0]),str(mode[1]),str(mode[2])])
                if os.path.isdir(fullname) and not os.path.islink(fullname) and os.listdir(fullname) == []:
                    mode = getStat(fullname)
                    files.append([truncname,"empty dir",oct(mode[0]),str(mode[1]),str(mode[2])])
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    stack.append(fullname)
            else:
                print "excluding", fullname
    return files

#more what the real getHostInfo will look like
#def getHostList():
#    db = MySQLdb.connect(host="localhost", user="joe", passwd="secret",db="hostkeys")
#    cursor = db.cursor()
#    cursor.execute("SELECT * FROM keys")
#    hostlist = cursor.fetchall()
#    return hostlist


def getHostList():
#   stub to get things going
    tmphostkey = ''
    tmpclientkey = ''
    hostlist = [('',tmphostkey,tmpclientkey)]
    return hostlist

def optionsParserForUpdateManager():
    parser = OptionParser()
    parser.add_option("-m", "--mask", help="the mount point of the new image")
    parser.add_option("-a", "--addfile", help="add file")
    parser.add_option("-u", "--updatefile", help="update file")
    parser.add_option("-r", "--removefile", help="remove file")
    (options, args) = parser.parse_args()
    if options.mask is None:
        parser.print_help()
        sys.exit()
    if options.addfile is None:
        parser.print_help()
        sys.exit()
    if options.updatefile is None:
        parser.print_help()
        sys.exit()
    if options.removefile is None:
        parser.print_help()
        sys.exit()
    options.mask            = os.path.abspath(options.mask)
    options.addfilename     = os.path.abspath(options.addfilename)
    options.updatefilename  = os.path.abspath(options.updatefile)
    options.removefilename  = os.path.abspath(options.removefile)
    return options.mask,options.addfilename,options.updatefilename,options.removefilename

def optionParserForWalker():
    parser = OptionParser()
    parser.add_option("-n", "--rootdir1", help="root new filesystem")
    parser.add_option("-f", "--filedir", help="directory to output files")
    parser.add_option("-o", "--rootdir2", help="root nold filesystem")
    parser.add_option("-c", "--config", help="configuration file")
    (options, args) = parser.parse_args()
    if options.config:
        return options.config
    if options.rootdir1 is None:
        parser.print_help()
        sys.exit()
    if options.rootdir2 is None:
        parser.print_help()
        sys.exit()
    if options.filedir is None:
        parser.print_help()
        sys.exit()
    options.rootdir1 = os.path.abspath(options.rootdir1)
    options.rootdir2 = os.path.abspath(options.rootdir2)
    options.filedir  = os.path.abspath(options.filedir)
    return options.rootdir1,options.rootdir2,options.filedir

def fileLists(oldfiles,newfiles):
    added = []
    removed = []
    changed = []
    removediff = []
    changeddiff = []
    removedfinal = []
    addedfinal =   []
    for file in newfiles:
        if file not in oldfiles:
            added.append(file)
    for file in oldfiles:
        if file not in newfiles:
            removed.append(file)
    for i in removed:
        removediff.append([i[0],i[1]])
    for file in added:
        if [file[0],file[1]] in removediff:
            changed.append(file)
    for i in changed:
        changeddiff.append([i[0],i[1]])
    for i in removed:
        if [i[0],i[1]] not in changeddiff:
            removedfinal.append(i)
    for i in added:
        if [i[0],i[1]] not in changeddiff:
            addedfinal.append(i)
    return addedfinal,removedfinal,changed

def putFileListInLine(list):
    listline = []
    for file in list:
        listline.append(file[0]+'\t'+file[1]+'\t'+file[2]+'\t'+file[3]+'\t'+file[4]+'\t'+'\n')
    return listline

def setTrim(rootdir):
    if rootdir == '/':
        return 0
    else:
        return(len(rootdir))

def readConf(filename):
    values = []
    file = open(filename,'r')
    lines = [line for line in file.readlines() if line.strip()]
    file.close()
    options = [line.strip() for line in lines if line[0] != '#']
    for i in options:
        a = i.split('=')[0].strip()
        b = i.split('=')[1].strip()
        values.append((a,b))
    values = dict(values)
    return values

def configParserForWalker(config):
    olddir = config['olddir']
    newdir = config['newdir']
    savedir = config['savedir']
    excludedirs = config['excludedirs'].split(',')
    excludedirspathed = [os.path.abspath(line) for line in excludedirs]
    excludefiles = config['excludefiles'].split(',')
    excludefilespathed = [os.path.abspath(line) for line in excludefiles]
    return olddir,newdir,excludedirspathed,excludefilespathed,savedir
