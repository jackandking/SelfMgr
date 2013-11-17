# -*- coding: utf-8 -*-
# Author: yingjil@amazon.com
# DateTime: 2013-11-17 16:45:38.574000
# Generator: https://github.com/jackandking/newpy
# Newpy Version: 1.2
# Newpy ID: 188
# Description: this utility will be used to store and sync all my input to all kinds consoles: cmd.exe. bash, zsh and etc.


## Unit Test

import unittest
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)

class CmdHistoryMgr:
  pass

class _UT(unittest.TestCase):

    @unittest.skip('not ready')
    def test1(self):
      l_c=CmdHistoryMgr()
      l_c.save()
      self.failUnless(os.path.isfile(l_c.tmpfile()))

def main():
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main()



