# -*- coding: utf-8 -*-
# Author: yingjil@amazon.com
# DateTime: 2013-12-03 16:57:50.763000
# Generator: https://github.com/jackandking/newpy
# Newpy Version: 1.2
# Newpy ID: 196
# Description: CodeMgr will manage all my code files. create/upload/download/sample.
# Change log:
#2013-12-03 4:59:23 PM 2.0 init from newpy.py

__version__='2.0'

'''Contributors:
    Yingjie.Liu@thomsonreuters.com
    yingjil@amazon.com
'''

# Configuration Area Start for users of newpy
_author_ = 'yingjil@amazon.com'
# Configuration Area End

_newpy_server_='newxx.sinaapp.com'
#_newpy_server_='localhost:8080'

from datetime import datetime
from optparse import OptionParser
import sys,os
import urllib,urllib2
import re
import socket
socket.setdefaulttimeout(13)

header='''
python: >
  # -*- coding: utf-8 -*-
  # Author: %s
  # DateTime: %s
  # Generator: https://github.com/jackandking/SelfMgr/CodeMgr
  # Newpy Version: %s
  # Newpy ID: %s
  # Description: I'm a lazy person, so you have to figure out the function of this script by yourself.
'''

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

def write_sample_to_file(newpy_id=0,
                         id_list=None,
                         filename=None,
                         comment=None):
    if id_list is None: id_list=sample_blocks.iterkeys()
    if filename is None: file=sys.stdout
    else: file=open(filename,'w')
    print >> file, header%(_author_, datetime.now(), __version__, newpy_id)
    for i in id_list:
        if i not in sample_blocks.iterkeys(): print "invalid sample ID, ignore",i; continue
        print >> file, ""
        if comment: print >> file, "'''"
        print >> file, '##',sample_blocks[i][0]
        if sample_blocks[i][1][:5] == "http:":
          print >> file, ""
          print >> file, get_file_content(sample_blocks[i][1])
        else:
          print >> file, sample_blocks[i][1]
        if comment: print >> file, "'''"
        print >> file, ""
    if file != sys.stdout: file.close()

def list_sample(option, opt_str, value, parser):
    print "Here are the available samples:"
    print "---------------------------------------"
    for i in sorted(sample_blocks.iterkeys()):
        print i,"=>",sample_blocks[i][0]
    print "---------------------------------------"
    sys.exit()

def submit_record(what,verbose):
    params = urllib.urlencode({'which': __version__, 'who': _author_, 'what': what})
    if verbose: sys.stdout.write("apply for newpy ID...")
    newpyid=0
    try:
        f = urllib2.urlopen("http://"+_newpy_server_+"/newpy", params)
        newpyid=f.read()
        if verbose: print "ok, got",newpyid
    #except urllib2.HTTPError, e:
        #print e.reason
    except:
        #print "Unexpected error:", sys.exc_info()[0]
        if verbose: print "ko, use 0"

    return newpyid
 
def upload_file(option, opt_str, value, parser):
    filename=value
    if not os.path.isfile(filename): sys.exit("error: "+filename+" does not exist!")
    file=open(filename,"r")
    line=file.readline()
    newpyid=0
    while line:
        line=file.readline()
        m=re.search('# Newpy ID: (\d+)',line)
        if m: 
            newpyid=int(m.group(1))
            break
    file.close
    if newpyid == 0: sys.exit("error: no valid newpy ID found for "+filename)
    sys.stdout.write("uploading "+filename+"(newpyid="+str(newpyid)+")...")
    params = urllib.urlencode({'filename': filename, 'content': open(filename,'rb').read()})
    try:
        f = urllib2.urlopen("http://"+_newpy_server_+"/newpy/upload", params)
        print f.read()
        print "weblink: http://"+_newpy_server_+"/newpy/"+str(newpyid)
    except:
        print "Unexpected error:", sys.exc_info()[0]
    sys.exit()

def main():
    usage = "usage: %prog [options] filename"
    parser = OptionParser(usage)
    parser.add_option("-s", "--samples", type="string", dest="sample_list", metavar="sample-id-list",
                      help='''select samples to include in the new file,
                      e.g. -s 123, check -l for all ids''',default="")
    parser.add_option("-l", "--list", help="list all the available samples.", action="callback", callback=list_sample)
    parser.add_option("-u", "--upload", type="string", dest="filename",
                      help='''upload file to newpy server as sample to others. the file must have a valid newpy ID.''',
                      action="callback", callback=upload_file)
    parser.add_option("-c", "--comment", dest="comment",
                      action="store_true", help="add samples with prefix '#'" )
    parser.add_option("-q", "--quiet", help="run in silent mode",
                      action="store_false", dest="verbose", default=True)
    parser.add_option("-o", "--overwrite", help="overwrite existing file",
                      action="store_true", dest="overwrite")
    parser.add_option("-t", "--test", help="run in test mode, no file generation, only print result to screen.",
                      action="store_true", dest="test")
    parser.add_option("-r", "--record", help="submit record to improve newpy (obsolete, refer to -n)",
                      action="store_true", dest="record")
    parser.add_option("-n", "--norecord", help="don't submit record to improve newpy",
                      action="store_false", dest="record", default=True)
    (options, args) = parser.parse_args()
    verbose=options.verbose
    sample_list=options.sample_list

    if options.test is None:
        if len(args) != 1:
            parser.error("incorrect number of arguments, try -h")

        filename=args[0]+'.py'
        if options.overwrite is None and os.path.isfile(filename): sys.exit("error: "+filename+" already exist!")

    else:
        filename=None

    if options.record: newpy_id=submit_record(sample_list,verbose)
    else: newpy_id=0

    write_sample_to_file(newpy_id=newpy_id,
                         id_list= sample_list,
                         filename=filename,
                         comment=options.comment)
    if verbose and filename: print "generate",filename,"successfully."

if __name__ == '__main__':
    main()

