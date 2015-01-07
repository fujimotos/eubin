#!/usr/bin/env python3

import hashlib
import os

def load(logpath):
    if os.path.exists(logpath):
        with open(logpath) as fp:
            res = set(line.strip() for line in fp)
    else:
        res = set()
    return res
    
def append(logpath, hashstr):
    with open(logpath, 'a') as fp:
        fp.write(hashstr + '\n')

def create(logpath, hashlist):
    tmpfile = logpath + '.tmp'
    with open(tmpfile, 'w') as fp:
        for h in hashlist:
            fp.write(h + '\n')
    os.rename(tmpfile, logpath)

def md5sum(lines):
    md5 = hashlib.md5()
    for line in lines:
        md5.update(line)
    return md5.hexdigest()
