# -*- coding: utf-8 -*-
# Author: yingjil@amazon.com
# DateTime: 2013-12-03 16:57:50.763000
# Generator: https://github.com/jackandking/newpy
# Newpy Version: 1.2
# Newpy ID: 196
# Description: CodeMgr will manage all my code files. create/upload/download/sample.
# Change log:
#2013-12-03 4:59:23 PM 2.0 init from newpy.py
#2014-02-18 20:29:20 2.1 rm yaml for old version py

__version__='2.0'

'''Contributors:
    Yingjie.Liu@thomsonreuters.com
    yingjil@amazon.com
'''

# Configuration Area Start for users of newxx
_author_ = 'yingjil@amazon.com'
# Configuration Area End

import os
if os.environ.get('SELFMGR_DEBUG'):
  _newxx_server_='localhost:8080'
  print "use local server in debug mode"
else:
  _newxx_server_='newxx-jackandking.rhcloud.com'


from datetime import datetime
from optparse import OptionParser
import sys
import urllib,urllib2
import re
import socket
socket.setdefaulttimeout(13)
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)

g_header={
'py':''' 
# -*- coding: utf-8 -*-
# Author: %s
# DateTime: %s
# Generator: https://github.com/jackandking/SelfMgr/CodeMgr
# Newxx Version: %s
# Newxx ID: %s
# Description: I'm a lazy person, so you have to figure out the function of this script by yourself.
''',
'zsh':''' 
#!/usr/zsh
# Author: %s
# DateTime: %s
# Generator: https://github.com/jackandking/SelfMgr/CodeMgr
# Newxx Version: %s
# Newxx ID: %s
# Description: I'm a lazy person, so you have to figure out the function of this script by yourself.
''',
'*':''' 
# Author: %s
# DateTime: %s
# Generator: https://github.com/jackandking/SelfMgr/CodeMgr
# Newxx Version: %s
# Newxx ID: %s
# Description: I'm a lazy person, so you have to figure out the function of this script by yourself.
'''
}
def get_header(ext,header=g_header):
  try:
    return header[ext]
  except KeyError:
    print "No header defined for "+ext+", use default header."
    return header["*"]

sample_blocks = '''
python:
  0: 
    - Hello World
    - >
world=raw_input("Hello:")
World='python is case sensitive'
print "Hello",world + "!"
  1: 
    - If-Else inside While
    - >
from time import time
while not None:
    if int(time()) % 2:
            print "True"
            continue
    else:
            break
'''
    

def get_file_content(a_url):
  try:
    response=urllib2.urlopen(a_url)
    #for i in range(6):
      #response.readline()
    return response.read()[11:][:-13] 
  except:
    return "#timeout, please refer to "+a_url

def write_sample_to_file(ext,newxx_id=0,
                         filename=None,
                         ):
    if filename is None: file=sys.stdout
    else: file=open(filename,'w')
    print >> file, get_header(ext)%(_author_, datetime.now(), __version__, newxx_id)
    print >> file, ""
    if file != sys.stdout: file.close()

def list_key_sample(option, opt_str, value, parser):
    pass
def list_sample(option, opt_str, value, parser):
    print "Here are the available samples:"
    print "---------------------------------------"
    for i in sorted(sample_blocks.iterkeys()):
        print i,"=>",sample_blocks[i][0]
    print "---------------------------------------"
    sys.exit()

def submit_record(what,verbose):
    params = urllib.urlencode({'which': __version__, 'who': _author_, 'what': what})
    if verbose: sys.stdout.write("apply for newxx ID...")
    newxxid=0
    try:
        f = urllib2.urlopen("http://"+_newxx_server_+"/newxx", params)
        newxxid=f.read()
        if verbose: print "ok, got",newxxid
    #except urllib2.HTTPError, e:
        #print e.reason
    except:
        #print "Unexpected error:", sys.exc_info()[0]
        if verbose: print "ko, use 0"

    return newxxid

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
    newxxid=value
    url="http://"+_newxx_server_+"/newxx/raw/"+newxxid
    target=newxxid
    if os.path.isfile(target): sys.exit("error: "+target+" already exist!")
    download_file_insecure(url,target)
    logging.info("Downloaded %s to %s."%(url,target))
    sys.exit()

def upload_file(option, opt_str, value, parser):
    filename=value
    if not os.path.isfile(filename): sys.exit("error: "+filename+" does not exist!")
    file=open(filename,"r")
    line=file.readline()
    newxxid=0
    while line:
        line=file.readline()
        m=re.search('# Newxx ID: (\d+)',line)
        if m: 
            newxxid=int(m.group(1))
            break
    file.close
    if newxxid == 0: sys.exit("error: no valid newxx ID found for "+filename)
    sys.stdout.write("uploading "+filename+"(newxxid="+str(newxxid)+")...")
    params = urllib.urlencode({'filename': filename, 'content': open(filename,'rb').read()})
    try:
        f = urllib2.urlopen("http://"+_newxx_server_+"/newxx/upload", params)
        print f.read()
        print "weblink: http://"+_newxx_server_+"/newxx/"+str(newxxid)
    except:
        print "Unexpected error:", sys.exc_info()[0]
    sys.exit()

def main():
    usage = "usage: %prog [options] filename"
    parser = OptionParser(usage)
    parser.add_option("-e", "--ext", type="string", dest="ext", metavar="a-language-ext",help='one of py,pl,bat,sh',default='py')
    parser.add_option("-k", "--key", type="string", dest="key_sample", metavar="key-sample",help='a key word for samples.', action='callback',callback=list_key_sample)
    parser.add_option("-l", "--list", help="list all the available samples.", action="callback", callback=list_sample)
    parser.add_option("-u", "--upload", type="string", dest="filename",
                      help='''upload file to newxx server as sample to others. the file must have a valid newxx ID.''',
                      action="callback", callback=upload_file)
    parser.add_option("-d", "--download", type="string", dest="newxxid",
                      help='''download file from newxx server''',
                      action="callback", callback=download_file)
    parser.add_option("-q", "--quiet", help="run in silent mode",
                      action="store_false", dest="verbose", default=True)
    parser.add_option("-o", "--overwrite", help="overwrite existing file",
                      action="store_true", dest="overwrite")
    parser.add_option("-t", "--test", help="run in test mode, no file generation, only print result to screen.",
                      action="store_true", dest="test")
    parser.add_option("-n", "--norecord", help="do not apply for newxx id.",
                      action="store_false", dest="record", default=True)
    (options, args) = parser.parse_args()
    verbose=options.verbose
    ext=options.ext

    if options.test is None:
        if len(args) != 1:
            parser.error("incorrect number of arguments, try -h")

        filename=args[0]+'.'+ext
        if options.overwrite is None and os.path.isfile(filename): sys.exit("error: "+filename+" already exist!")

    else:
        filename=None

    if options.record: newxx_id=submit_record(filename,verbose)
    else: newxx_id=0

    write_sample_to_file(ext,newxx_id=newxx_id,
                         filename=filename)
    if verbose and filename: print "generate",filename,"successfully."

if __name__ == '__main__':
    main()

