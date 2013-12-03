# -*- coding: utf-8 -*-
# Author: yingjil@amazon.com
# DateTime: 2013-11-17 16:45:38.574000
# Generator: https://github.com/jackandking/newpy
# Newpy Version: 1.2
# Newpy ID: 188
# Description: this utility will be used to store and sync all my input to all kinds consoles: cmd.exe. bash, zsh and etc.

import os
import yaml
from datetime import date
import subprocess
import sys
import socket
import time
import re
import urllib,urllib2
socket.setdefaulttimeout(10)

if os.environ.get('SELFMGR_DEBUG'):
  _selfmgr_server_='localhost:8080'
  print "use local server in debug mode"
else:
  _selfmgr_server_='selfmgr.sinaapp.com'

_version_=1.0

## Unit Test

import unittest
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)

class HistoryFile:
  def __init__(self,a_fn):
    self.m_filename=a_fn
  def append(self, a_content):
    if a_content:
      l_f=open(self.m_filename,'a')
      l_f.write(a_content+'\n')
      l_f.close()
      logging.debug("append sth into "+self.m_filename)
    else:
      logging.warning("ignore None when appending.")
    return self


class LocalHistoryFile(HistoryFile):
  def get_new_block(self):
    l_f=open(self.m_filename)
    l_line=l_f.readline()
    l_lines=[]
    while l_line:
      l_lines.append(l_line)
      if HistoryBlockTag().claim(l_line):
        l_lines[:]=[]
      l_line=l_f.readline()
    return HistoryBlock(l_lines)



class AllHistoryFile(HistoryFile):
  def get_last_tag(self):
    if os.path.exists(self.m_filename):
      l_f=open(self.m_filename)
      l_t=HistoryBlockTag(l_f.readlines()[-1])
      logging.info("last tag: "+str(l_t))
      return l_t
    else:
      return HistoryBlockTag()

class HistoryBlock:
  def __init__(self, a_lines):
    self.m_lines=a_lines
    self.m_tag=HistoryBlockTag()
  def get_tag(self):
    return self.m_tag
  def size(self):
    return len(self.m_lines)
  def empty(self):
    return len(self.m_lines) == 0
  def urlencode(self):
    l_hash={'content':"".join(self.m_lines)+"\n"+str(self.m_tag)}
    return l_hash

class HistoryLine:
  pass

g_block_tag="SyncBlock"
class HistoryBlockTag:
  def __init__(self, a_line=None):
    if a_line:
      self.m_line=a_line
      self.decode()
    else:
      self.m_host=socket.gethostname()
      self.m_time=time.time()
      self.encode()
  def decode(self):
    l_m=re.match(g_block_tag+':([-\w]+):(\d+)',self.m_line)
    if l_m:
      self.m_host=l_m.group(1)
      self.m_time=l_m.group(2)
    else:
      raise Exception("decode failed: "+self.m_line)
    return self
  def encode(self):
    if self.m_host and self.m_time:
      self.m_line="%s:%s:%d"%(g_block_tag,self.m_host,self.m_time)
    else:
      raise Exception("encode failed: "+self.m_host+","+self.m_time)
  def urlencode(self):
    l_hash={'tag':self.m_line}
    return l_hash
  def __str__(self):
    return str(self.m_line)
  def claim(self, a_str):
    if a_str[:9] == "SyncBlock":
      return True
    else:
      return False

g_config="""
nt:
  home: c:\\SelfMgr\\CmdHistoryMgr
  all: allhistory_%s.txt
posix:
  home: ~/
  all: .allhistory_%s
"""%(date.today().year, date.today().year)

class CmdHistoryMgr:
  def __init__(self):
    l_config=yaml.load(g_config)
    print yaml.dump(l_config)
    self.m_home=l_config[os.name]['home']

    self.config_system()

    self.m_all=os.path.join(self.m_home,l_config[os.name]['all'])
    self.m_LHF=LocalHistoryFile(self.m_local)
    self.m_AHF=AllHistoryFile(self.m_all)
  def config_system(self):
    if not os.path.isdir(self.m_home):
      os.makedirs(self.m_home)
    if os.name == 'nt': 
      if not os.path.exists(os.path.join(os.environ['LOCALAPPDATA'],"clink")):
        print "please install %s first then try again!" %( download('https://clink.googlecode.com/files/','clink_0.4_setup.exe'))
        sys.exit(1)
      self.m_local=os.environ['LOCALAPPDATA']+"\\clink\\.history"
      print "localfile:"+self.m_local
  def sync(self):
    l_b=self.m_LHF.get_new_block()
    if l_b.empty():
      logging.warning("nothing to sync as no new cmd in local file.")
      return self
    if self.upload(l_b):
      self.m_LHF.append(str(l_b.get_tag()))
    l_bs=self.download(self.m_AHF.get_last_tag())
    if l_bs:
      self.m_AHF.append(l_bs)
    else:
      logging.warning("nothing downloaded.")
    #self.m_AHF.get_last_tag_by_host(socket.gethostname())
    return self

  def upload(self, a_block):
    l_ret='ko'
    try:
      params = urllib.urlencode(a_block.urlencode())
      f = urllib2.urlopen("http://"+_selfmgr_server_+"/cmdhistorymgr/upload", params)
      l_ret=f.read()
    except:
      logging.error("Execption when upload")

    if l_ret == 'ok':
      logging.info("Upload %d lines succeeded...",a_block.size())
      return True
    else:
      logging.warning("Upload failed...%s",a_block.get_tag())
      return False

  def download(self, a_tag):
    l_ret=None
    try:
      params = urllib.urlencode(a_tag.urlencode())
      f = urllib2.urlopen("http://"+_selfmgr_server_+"/cmdhistorymgr/download", params)
      l_ret=f.read()
    except:
      logging.error("Execption when download")
    logging.info("Download %d lines succeeded...",l_ret.count('\n'))
    return l_ret

def has_clink():
    cmd = ['clink', 'set']
    devnull = open(os.path.devnull, 'wb')
    try:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except:
            return False
    finally:
        devnull.close()
    return True
     
def _clean_check(cmd, target):
    """
    Run the command to download target. If the command fails, clean up before
    re-raising the error.
    """
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        if os.access(target, os.F_OK):
            os.unlink(target)
        raise

def download_file_curl(url, target):
    #cmd = ['curl', url, '--silent', '--output', target]
    cmd = ['curl', url,'-k', '--output', target]
    _clean_check(cmd, target)

def has_curl():
    cmd = ['curl', '--version']
    devnull = open(os.path.devnull, 'wb')
    try:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except:
            return False
    finally:
        devnull.close()
    return True

download_file_curl.viable = has_curl

def download_file_wget(url, target):
    cmd = ['wget', url, '--quiet', '--output-document', target]
    _clean_check(cmd, target)

def has_wget():
    cmd = ['wget', '--version']
    devnull = open(os.path.devnull, 'wb')
    try:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except:
            return False
    finally:
        devnull.close()
    return True

download_file_wget.viable = has_wget

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

download_file_insecure.viable = lambda: True

def get_best_downloader():
    downloaders = [
        download_file_curl,
        download_file_wget,
        download_file_insecure,
    ]

    for dl in downloaders:
        if dl.viable():
            return dl

def download(download_base, file_name, to_dir=os.curdir, downloader_factory=get_best_downloader):
    """Download sth from a specified location and return its filename

    ``downloader_factory`` should be a function taking no arguments and
    returning a function for downloading a URL to a target.
    """
    # making sure we use the absolute path
    to_dir = os.path.abspath(to_dir)
    url = download_base + file_name
    saveto = os.path.join(to_dir, file_name)
    if not os.path.exists(saveto):  # Avoid repeated downloads
        logging.warning("Downloading %s", url)
        downloader = downloader_factory()
        downloader(url, saveto)
    return os.path.realpath(saveto)

class _UT(unittest.TestCase):

    def test_hbt(self):
      l_b=HistoryBlockTag('SyncBlock:ping-PC:1385817487')
      l_b.decode()

    def test_upload(self):
      l_c=CmdHistoryMgr()
      l_c.m_LHF.append("testcmd")
      print l_c.m_home
      l_c.sync()
      #self.failUnless(os.path.isfile(l_c.tmpfile()))

    def test_sync(self):
      l_c=CmdHistoryMgr()
      l_c.sync()

def main():
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main()



