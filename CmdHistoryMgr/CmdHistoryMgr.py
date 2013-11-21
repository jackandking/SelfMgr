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

## Unit Test

import unittest
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)

class HistoryFile:
  def __init__(self,a_fn):
    self.m_filename=a_fn
  pass

class LocalHistoryFile(HistoryFile):
  pass

class AllHistoryFile(HistoryFile):
  pass

class HistoryBlock:
  pass

class HistoryLine:
  pass

class HistoryBlockTag:
  pass

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
    self.config_system()
    l_config=yaml.load(g_config)
    print yaml.dump(l_config)
    self.m_home=l_config[os.name]['home']
    self.m_all=os.path.join(self.m_home,l_config[os.name]['all'])
    self.m_LHF=LocalHistoryFile(self.m_local)
    self.m_AHF=AllHistoryFile(self.m_all)
  def config_system(self):
    if os.name == 'nt':
      if not has_clink():
        print "please install %s first then try again!" %( download('https://clink.googlecode.com/files/','clink_0.4_setup.exe'))
        sys.exit(1)
      self.m_local=os.path.join(os.environ['LOCALAPPDATA'],"\\clink\\.history")
      print self.m_local

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
    cmd = ['curl', url, '--silent', '--output', target]
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

    def test1(self):
      l_c=CmdHistoryMgr()
      print l_c.m_home
      #l_c.save()
      #self.failUnless(os.path.isfile(l_c.tmpfile()))

def main():
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main()



