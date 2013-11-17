@echo off
REM Author: Yingjie.Liu@thomsonreuters.com
REM DateTime: 2013-10-21 15:49:31.138000
REM Generator: https://github.com/jackandking/newbat
REM Newbat Version: 0.1
REM Newbat ID: 0
REM Description: I'm a lazy person, so you have to figure out the function of this script by yourself.

python setup.py py2exe
copy SnapTimer.* dist
copy readme.md dist\readme.txt
