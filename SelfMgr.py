# -*- coding: utf-8 -*-
# Author: Yingjie.Liu@thomsonreuters.com
# DateTime: 2013-10-20 13:13:06.580000
# Generator: https://github.com/jackandking/newpy
# Newpy Version: 1.1
# Newpy ID: 180
# Description: I'm a lazy person, so you have to figure out the function of this script by yourself.

import unittest
import logging

import subprocess
import fileinput
from time import time, strftime
import re
import os
from datetime import datetime
import urllib,urllib2
import socket
socket.setdefaulttimeout(10)

if os.environ.get('SELFMGR_DEBUG'):
  _selfmgr_server_='localhost:8080'
  print "use local server in debug mode"
else:
  _selfmgr_server_='selfmgr.sinaapp.com'

_version_=1.0

class State:
  def init(self,a_t):
    raise Exception("this call is not supported in %s!"%(self.__class__.__name__))
  def start(self,a_t):
    raise Exception("this call is not supported in %s!"%(self.__class__.__name__))
  def load(self,a_t,a_id):
    raise Exception("this call is not supported in %s!"%(self.__class__.__name__))
  def end(self,a_t):
    raise Exception("this call is not supported in %s!"%(self.__class__.__name__))
  def upload(self,a_t):
    raise Exception("this call is not supported in %s!"%(self.__class__.__name__))
  def save(self,a_t):
    raise Exception("this call is not supported in %s!"%(self.__class__.__name__))
  def delete(self,a_t):
    raise Exception("this call is not supported in %s!"%(self.__class__.__name__))

def is_int(a):
  """Returns true if a can be an interger"""
  try:
    int (a)
    return True
  except:
    return False

class StateNull(State):
  def init(self,a_t):
    l_hist=a_t.m_hm.get(3)
    print "Latest Titles:"
    for l_i in range(len(l_hist)):
      print "=>[%d] %s"%(l_i,l_hist[l_i])
    while not a_t.m_title:
      a_t.m_title=raw_input("Please input your target: ").strip()
    if is_int(a_t.m_title):
      l_i=int(a_t.m_title)
      if l_i < len(l_hist):
        a_t.m_title=l_hist[l_i]
    print "=>Title: "+a_t.m_title
    a_t.m_hm.add(a_t.m_title)
    while not a_t.m_esti or int(a_t.m_esti) > 240 or int(a_t.m_esti) < 1:
      a_t.m_esti=raw_input("Please input your estimation (1-240minutes): ").strip()
    a_t.m_state=StateInited()
  def load(self,a_t,a_id):
    if a_t.m_lm.load(a_id,a_t):
      if a_t.m_result != "None":
        a_t.m_state=StateEnded()
      else:
        a_t.m_state=StateStarted()
    else:
      a_t.m_id=a_id
      a_t.m_state=StateNotFound()

class StateInited(State):
  def start(self,a_t):
    a_t.m_id=str(int(time()))
    a_t.m_dt=strftime('%Y-%m-%d %H:%M:%S')
    a_t.m_tm.start(a_t)
    a_t.m_state=StateStarted()

class StateStarted(State):
  def save(self,a_t):
    a_t.m_lm.llog(a_t)
    a_t.m_state=StateSaved()
  def end(self,a_t):
    a_t.m_result=raw_input("Have you done the task below\n\t"+a_t.m_title+"\n\t[y/n]").strip()
    if a_t.m_result != 'y':
      a_t.m_result='n'
    a_t.m_state=StateEnded()

class StateEnded(State):
  def upload(self,a_t):
    if a_t.m_lm.rlog(a_t):
      a_t.m_state=StateUploaded()
    else:
      if a_t.m_lm.llog(a_t):
        a_t.m_state=StateSaved()
      else:
        a_t.m_state=StateFailed()
  def end(self,a_t):
    pass

class StateSaved(State):
  def delete(self,a_t):
    pass

class StateUploaded(State):
  def delete(self,a_t):
    a_t.delete_endbat()
    a_t.m_state=StateDeleted()

class StateFailed(State):
  pass

class StateNotFound(State):
  def delete(self,a_t):
    a_t.delete_endbat()
    a_t.m_state=StateDeleted()
  def end(self,a_t):
    pass
  def upload(self,a_t):
    pass

class StateDeleted(State):
  pass

class Task:
  def __init__(self,a_name="undef",a_tm=None,a_lm=None,a_hm=None):
    self.m_name=a_name
    self.m_tm=a_tm
    self.m_lm=a_lm
    self.m_hm=a_hm
    self.m_title=None
    self.m_esti=None
    self.m_id=None
    self.m_dt=None
    self.m_result=None
    self.m_state=StateNull()

  def init(self):
    self.m_state.init(self)
    return self
  def start(self):
    self.m_state.start(self)
    return self
  def save(self):
    self.m_state.save(self)
    return self
  def load(self,a_id):
    self.m_state.load(self,a_id)
    return self
  def end(self):
    self.m_state.end(self)
    return self
  def upload(self):
    self.m_state.upload(self)
    return self
  def delete(self):
    self.m_state.delete(self)
    return self

  def endbat(self):
    return "End_"+self.m_id+".bat"
  def create_endbat(self):
    l_bat=open(self.endbat(),'w')
    if os.path.isfile("SelfMgr.py"):
      l_bat.write("SelfMgr.py "+self.m_id)
    else:
      l_bat.write("SelfMgr.exe "+self.m_id)
    l_bat.close()
    return self
  def delete_endbat(self):
    try:
      os.remove(self.endbat())
      logging.debug("Endbat delete succeeded...%s",self.endbat())
    except:
      logging.warning("Endbat delete failed...%s",self.endbat())
    return self
  def __str__(self):
    return "Name=%s:ID=%s:DateTime=%s:Title=%s:Minutes=%s:Result=%s\n"%(self.m_name,self.m_id,self.m_dt,self.m_title ,self.m_esti,str(self.m_result))
  def show(self):
    print self

  def encode(self):
    l_hash={"name":self.m_name,
        "datetime":self.m_dt,
        "title":self.m_title,
        "minutes":self.m_esti,
        "result":self.m_result,
        "version":_version_
        }
    return l_hash
  def decode(self,a_str):
    l_m=re.match("Name=(.*):ID=(\d+):DateTime=(.*):Title=(.*):Minutes=(\d+):Result=(.*)", a_str)
    if l_m:
      self.m_name=l_m.group(1)
      self.m_id=l_m.group(2)
      self.m_dt=l_m.group(3)
      self.m_title=l_m.group(4)
      self.m_esti=l_m.group(5)
      self.m_result=l_m.group(6)
      logging.debug("Decode succeeded...%s",self)
      return True
    else:
      logging.error("Decode failed from str: %s",a_str)
      return False

class Logger:
  def log(self,a_task):
    raise Exception("You must impl log()!")

class LocalLogger(Logger):
  def __init__(self, a_fn):
    self.m_logfn=a_fn
    open(self.m_logfn,'a').close()

  def log(self,a_task):
    logging.debug("LocalLogger.log...%s",a_task)
    try:
      l_f=open(self.m_logfn,'a')
      l_f.write(str(a_task))
      l_f.close()
      return True
    except:
      return False

  def load(self,a_id,a_task):
    logging.debug("LocalLogger.load...%s",a_id)
    l_found=False
    for l_line in fileinput.input(self.m_logfn, inplace=True):
      l_task=Task()
      if not l_task.decode(l_line):
        continue
      if not l_found and l_task.m_id == a_id:
        a_task.decode(l_line)
        l_found=True
        logging.debug("Found Task...%s",a_id)
      else:
        print l_line,

    if not l_found:
      logging.error("Task not found...%s",a_id)
      #raise Exception("Task not found for ID "+a_id)
      return False
    return True

class RemoteLogger(Logger):
  def __init__(self):
    self.m_proxyfn='proxy.txt'
  def log(self,a_task):
    l_ret='ko'
    try:
      if os.path.isfile(self.m_proxyfn):
        proxy = urllib2.ProxyHandler({'http': open(self.m_proxyfn).readline().strip()})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
      params = urllib.urlencode(a_task.encode())
      f = urllib2.urlopen("http://"+_selfmgr_server_+"/upload", params)
      l_ret=f.read()
    except:
      logging.error("Execption when upload")

    if l_ret == 'ok':
      logging.info("Upload succeeded...%s",a_task)
      return True
    else:
      logging.warning("Upload failed...%s",a_task)
      return False
    return None

class LoggerMgr(Logger):
  def __init__(self,a_fn):
    self.m_ll=LocalLogger(a_fn)
    self.m_rl=RemoteLogger()
  def llog(self,a_task):
    return self.m_ll.log(a_task)
  def rlog(self,a_task):
    return self.m_rl.log(a_task)
  def load(self,a_id,a_task):
    return self.m_ll.load(a_id,a_task)

class TimerMgr:
  def __init__(self):
    self.m_config="SnapTimer.ini"

  def start(self,a_task):
    a_task.create_endbat()
    self._adjust_config(a_task)
    self._start_timer()

  def _adjust_config(self,a_task):
    for line in fileinput.input(self.m_config, inplace=True):
      if line[:8] == "Minutes=" and a_task.m_esti != "":
        logging.debug("orig: "+line)
        print "Minutes=%s" % (a_task.m_esti)
      elif line[:8] == "Message=" and a_task.m_title !="":
        logging.debug("orig: "+line)
        print "Message=%s" % (a_task.m_title)
      elif line[:7] == "RunApp=" and a_task.m_id:
        logging.debug("orig: "+line)
        print "RunApp=%s" % (a_task.endbat())
      else:
        print line.rstrip('\n')

  def _start_timer(self):
    subprocess.Popen("SnapTimer.exe")

class HistoryMgr:
  def __init__(self,a_fn):
    self.m_fn=a_fn
    if not os.path.isfile(self.m_fn):
      l_f=open(self.m_fn,'w')
      l_f.write('Take a 10 minutes break!\n')
      l_f.close()
  def add(self,a_title):
    l_first=True
    for line in fileinput.input(self.m_fn, inplace=True):
      if l_first:
        print a_title.rstrip('\n')
        l_first=False
      print line.rstrip('\n')
  def get(self,a_n):
    l_f=open(self.m_fn,'r')
    l_i=0
    l_line=l_f.readline()
    l_hist=[]
    while l_i < a_n and  l_line:
      l_hist.append(l_line.rstrip('\n'))
      l_line=l_f.readline()
      l_i+=1
    return l_hist
    
class SelfMgr:
  def __init__(self):
    self.m_tm=TimerMgr()
    self.m_lm=LoggerMgr("tasklog.txt")
    self.m_hm=HistoryMgr("history.txt")
    self.m_name=self.get_name("name.txt")

  def get_name(self, a_fn):
    l_n=None
    if os.path.isfile(a_fn):
      l_f=open(a_fn,'r')
      l_n=l_f.readline().rstrip()
      l_f.close()
    else:
      while not l_n:
        l_n=raw_input("First time use, please input your name: ").strip()
      logging.info("Welcome <%s>",l_n)
      l_f=open(a_fn,'w')
      l_f.write(l_n)
      l_f.close()
    return l_n

  def start_task(self):
    Task(self.m_name,self.m_tm,self.m_lm,self.m_hm).init().start().save().show()

  def end_task(self,a_id):
    Task(self.m_name,self.m_tm,self.m_lm).load(a_id).end().upload().delete()

def start_task():
  logging.info("Start a new task...")
  SelfMgr().start_task()

def end_task(a_id):
  logging.info("End task: %s",a_id)
  SelfMgr().end_task(a_id)

class _UT(unittest.TestCase):
    def test1(self):
      logging.debug("in test1")
      l_rl=HistoryMgr('history.txt')
      l_rl.add('test history1')
      l_rl.add('test history2')
      l_rl.add('test history3')
      print l_rl.get(2)
      print l_rl.get(4)

import sys
def main(argv):
  logging.basicConfig(filename='runlog.txt',format='%(asctime)s;%(levelname)s:%(message)s',level=logging.DEBUG)
  if len(argv) < 2:
    #unittest.main(verbosity=2)
    start_task()
  else:
    end_task(argv[1])

if __name__ == '__main__':
    main(sys.argv)



