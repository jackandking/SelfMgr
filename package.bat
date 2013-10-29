@echo off
REM Author: Yingjie.Liu@thomsonreuters.com
REM DateTime: 2013-10-22 19:41:07.741000
REM Generator: https://github.com/jackandking/newbat
REM Newbat Version: 0.1
REM Newbat ID: 5
REM Description: I'm a lazy person, so you have to figure out the function of this script by yourself.

copy dist SelfMgr
del SelfMgr\history.txt
del SelfMgr\name.txt
del SelfMgr\runlog.txt
del SelfMgr\tasklog.txt
del SelfMgr\proxy.txt
del SelfMgr\End_*.bat
zip -r SelfMgr.zip SelfMgr
