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
socket.setdefaulttimeout(13)
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)

header=''

def get_file_content(a_url):
  try:
    response=urllib2.urlopen(a_url)
    #for i in range(6):
      #response.readline()
    return response.read()[11:][:-13] 
  except:
    return "#timeout, please refer to "+a_url

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
import requests
def upload_file(option, opt_str, value, parser):
    filename=value
    if not os.path.isfile(filename): sys.exit("error: "+filename+" does not exist!")
    sys.stdout.write("uploading "+filename+"...")
    length = os.path.getsize(filename)
    params = urllib.urlencode({'filename': filename, 'content': open(filename,'rb')})
    url="http://"+_selfmgr_server_+"/filemgr/upload"
    files={'content':open(filename,'rb')}
    try:
        #f = urllib2.urlopen(url, params)
	i=requests.post(url,files=files)
	sys.exit()
	i=post_multipart("http://"+_selfmgr_server_,"/filemgr/upload",{},{'content',filename,open(filename,'rb').read()})
        #f = urllib2.urlopen(url, params)
	request = urllib2.Request(url, data=open(filename,'rb'))
	request.add_header('Cache-Control', 'no-cache')
	request.add_header('Content-Length', '%d' % length)
	#request.add_header('Content-Type', 'image/png')
	i = urllib2.urlopen(request).read().strip()
	print "done"
        print "weblink: http://"+_selfmgr_server_+"/filemgr/"+i
    except:
        print "Unexpected error:", sys.exc_info()[0]
    sys.exit()
import httplib, mimetypes

def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

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


