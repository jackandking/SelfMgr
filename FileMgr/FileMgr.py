# -*- coding: utf-8 -*-
# Author: yingjil@amazon.com
# DateTime: 2013-12-07 21:42:41.938000
# Generator: https://github.com/jackandking/newpy
# Newpy Version: 1.2
# Newpy ID: 202
# Description: except for code, FileMgr will cover all other files.
# Change log:
#2013/12/7 init from CodeMgr.py

__version__='0.1'

'''Contributors:
    yingjil@amazon.com
'''

# Configuration Area Start for users of filemgr
_author_ = 'yingjil@amazon.com'
# Configuration Area End

import os
if os.environ.get('SELFMGR_DEBUG'):
  _selfmgr_server_='localhost:8080'
  print "use local server in debug mode"
else:
  _selfmgr_server_='selfmgr.sinaapp.com'


from datetime import datetime
from optparse import OptionParser
import sys
import urllib,urllib2
import re
import socket
socket.setdefaulttimeout(30)
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)
import requests

header=''


def download_file_insecure(url, target):
    """
    Use Python to download the file, even though it cannot authenticate the
    connection.
    """
    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib2 import urlopen
    src = dst = None
    try:
        src = urlopen(url)
        # Read/write all in one block, so we don't create a corrupt file
        # if the download is interrupted.
        data = src.read()
        dst = open(target, "wb")
        dst.write(data)
    finally:
        if src:
            src.close()
        if dst:
            dst.close()
 
def download_file(option, opt_str, value, parser):
    filemgrid=value
    url="http://"+_selfmgr_server_+"/filemgr/"+filemgrid
    target=filemgrid
    if os.path.isfile(target): sys.exit("error: "+target+" already exist!")
    download_file_insecure(url,target)
    logging.info("Downloaded %s to %s."%(url,target))
    sys.exit()

def upload_file(option, opt_str, value, parser):
    filename=value
    if not os.path.isfile(filename): sys.exit("error: "+filename+" does not exist!")
    sys.stdout.write("uploading "+filename+"...")
    url="http://"+_selfmgr_server_+"/filemgr/upload"
    files={'content':open(filename,'rb')}
    try:
	i=requests.post(url,files=files).text
	print "done"
        print "weblink: http://"+_selfmgr_server_+"/filemgr/"+str(i)
    except:
        print "Unexpected error:", sys.exc_info()[0]
    sys.exit()

def main():
    usage = "usage: %prog [options] filename"
    parser = OptionParser(usage)
    parser.add_option("-u", "--upload", type="string", dest="filename",
                      help='''upload file to filemgr server as sample to others. the file must have a valid filemgr ID.''',
                      action="callback", callback=upload_file)
    parser.add_option("-d", "--download", type="string", dest="filemgrid",
                      help='''download file from filemgr server''',
                      action="callback", callback=download_file)
    parser.add_option("-q", "--quiet", help="run in silent mode",
                      action="store_false", dest="verbose", default=True)
    (options, args) = parser.parse_args()
    verbose=options.verbose

if __name__ == '__main__':
    main()


