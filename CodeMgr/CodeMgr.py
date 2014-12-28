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
def gen_header(ext, newxx_id):
  try:
    return g_header[ext]%(_author_, datetime.now(), __version__, newxx_id)
  except KeyError:
    print "No header defined for ["+ext+"], use default header."
    return g_header['*']%(_author_, datetime.now(), __version__, newxx_id)


def get_file_content(a_url):
  try:
    response=urllib2.urlopen(a_url)
    #for i in range(6):
      #response.readline()
    return response.read()[11:][:-13] 
  except:
    return "#timeout, please refer to "+a_url

def write_sample_to_file(newxx_id=0,
                         filename=None,
                         ):
    ext = os.path.splitext(filename)[1]
    file=open(filename,'w')
    print >> file, gen_header(ext,newxx_id)
    print >> file, ""
    file.close()

def search_sample(option, opt_str, value, parser):
    params = urllib.urlencode({'which': __version__, 'who': _author_, 'keywords': value})
    print "Keywords: "+value
    try:
        f = urllib2.urlopen("http://"+_newxx_server_+"/newxx/search", params)
        print f.read()
        print "..."
        print "http://"+_newxx_server_+"/newxx/<newxxid>"
        print "http://"+_newxx_server_+"/newxx/view/<id>"
    except urllib2.HTTPError, e:
        print e.reason
    except:
        print "Unexpected error:", sys.exc_info()[0]
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
    #parser.add_option("-k", "--key", type="string", dest="key_sample", metavar="key-sample",help='a key word for samples.', action='callback',callback=list_key_sample)
    parser.add_option("-s", "--search", type="string", dest="search", metavar="search-sample",help='search samples with the key word.', action='callback',callback=search_sample)
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

    if options.test is None:
        if len(args) != 1:
            parser.error("incorrect number of arguments, try -h")

        filename=args[0]
        if options.overwrite is None and os.path.isfile(filename): sys.exit("error: "+filename+" already exist!")

    else:
        filename=None

    if options.record: newxx_id=submit_record(filename,verbose)
    else: newxx_id=0

    write_sample_to_file(newxx_id=newxx_id,
                         filename=filename)
    if verbose and filename: print "generate",filename,"successfully."

if __name__ == '__main__':
    main()

