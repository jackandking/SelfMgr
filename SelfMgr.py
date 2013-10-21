# -*- coding: utf-8 -*-
# Author: Yingjie.Liu@thomsonreuters.com
# DateTime: 2013-10-20 13:13:06.580000
# Generator: https://github.com/jackandking/newpy
# Newpy Version: 1.1
# Newpy ID: 180
# Description: I'm a lazy person, so you have to figure out the function of this script by yourself.


## Unit Test

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
else:
  _selfmgr_server_='selfmgr.sinaapp.com'

class Task:
  def __init__(self,a_name="undef",a_tm=None,a_lm=None):
    self.m_name=a_name
    self.m_tm=a_tm
    self.m_lm=a_lm
    self.m_title=None
    self.m_esti=None
    self.m_id=None
    self.m_dt=None
    self.m_result=None
  def init(self):
    self.m_title=raw_input("Please input your target: ").strip()
    self.m_esti=raw_input("Please input your estimation (minutes): ").strip()
    self.m_id=str(int(time()))
    self.m_dt=strftime('%Y-%m-%d %H:%M:%S')
    return self
  def endbat(self):
    return "End_"+self.m_id+".bat"
  def inited(self):
    return self.m_title!= None
  def valid(self):
    return self.m_result != None
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
  def start(self):
    self.m_tm.start(self)
    self.m_lm.log(self)
    return self
  def end(self):
    if self.inited():
      self.m_result=raw_input("Have you done the task below\n\t"+self.m_title+"\n\t[y/n]").strip()
      if self.m_result != 'y':
        self.m_result='n'
    return self
  def save(self):
    self.m_lm.log(self)
    return self
  def __str__(self):
    return "Name=%s:ID=%s:DateTime=%s:Title=%s:Minutes=%s:Result=%s\n"%(self.m_name,self.m_id,self.m_dt,self.m_title ,self.m_esti,str(self.m_result))
  def show(self):
    print self
  def load(self,a_id):
    self.m_lm.load(a_id,self)
    return self

  def encode(self):
    l_hash={"name":self.m_name,
        "datetime":self.m_dt,
        "title":self.m_title,
        "minutes":self.m_esti,
        "result":self.m_result}
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
    else:
      logging.error("Decode failed from str: %s",a_str)
    return self

class Logger:
  def log(self,a_task):
    raise Exception("You must impl log()!")

class LocalLogger(Logger):
  def __init__(self, a_fn):
    self.m_logfn=a_fn
  def log(self,a_task):
    if a_task.valid():
      l_t=Task()
      for l_line in fileinput.input(self.m_logfn, inplace=True):
        if l_t.decode(l_line).m_id == a_task.m_id:
          logging.debug("Remove succeeded...%s",a_task)
        else:
          print l_line,
    else:
      l_f=open(self.m_logfn,'a')
      l_f.write(str(a_task))
      l_f.close()
  def load(self,a_id,a_task):
    l_f=open(self.m_logfn,'r')
    l_line=l_f.readline()
    if not l_line:
      logging.error("Load nothing from "+self.m_logfn)
    while l_line:
      a_task.decode(l_line)
      if a_task.m_id == a_id:
        return True 
      l_line=l_f.readline()
    logging.error("Task not found for ID "+a_id)
    a_task.m_id=a_id
    return False
  def remove(self,a_task):
    l_t=Task()
    for l_line in fileinput.input(self.m_logfn, inplace=True):
      if l_t.decode(l_line).m_id == a_task.m_id:
        logging.debug("Remove succeeded...%s",a_task)
      else:
        print l_line,

class RemoteLogger(Logger):
  def log(self,a_task):
    l_ret='ko'
    try:
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
  def log(self,a_task):
    if a_task.valid() and self.m_rl.log(a_task):
      logging.debug("Try to remove...%s",a_task)
      self.m_ll.remove(a_task)
    else:
      self.m_ll.log(a_task)
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
    
class SelfMgr:
  def __init__(self):
    self.m_tm=TimerMgr()
    self.m_lm=LoggerMgr("tasklog.txt")
    self.m_name=self.get_name("name.txt")

  def get_name(self, a_fn):
    l_n="undef"
    try:
      if os.path.isfile(a_fn):
        l_f=open(a_fn,'r')
        l_n=l_f.readline().rstrip()
        l_f.close()
      else:
        l_n=raw_input("First time use, please input your name: ").strip()
        logging.info("Welcome %s",l_n)
        l_f=open(a_fn,'w')
        l_f.write(l_n)
        l_f.close()
    except:
      logging.warning("Exception during read/write %s",a_fn)
    return l_n

  def start_task(self):
    Task(self.m_name,self.m_tm,self.m_lm).init().start().show()

  def end_task(self,a_id):
    Task(self.m_name,self.m_tm,self.m_lm).load(a_id).end().save().delete_endbat()

class _UT(unittest.TestCase):

    def test1(self):
      logging.debug("in test1")
      l_rl=RemoteLogger()
      l_rl.log(Task().init().end())

def start_task():
  logging.info("Start a new task...")
  SelfMgr().start_task()

def end_task(a_id):
  logging.info("End task: %s",a_id)
  SelfMgr().end_task(a_id)

import sys
def main(argv):
  logging.basicConfig(filename='runlog.txt',format='%(asctime)s;%(levelname)s:%(message)s',level=logging.INFO)
  if len(argv) < 2:
    #unittest.main(verbosity=2)
    start_task()
  else:
    end_task(argv[1])

if __name__ == '__main__':
    main(sys.argv)



