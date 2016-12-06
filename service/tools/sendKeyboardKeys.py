import win32com.client
import time
import SendKeys
import os
from ctypes import *
import sys

# to log
import logging
logging.basicConfig(filename='../lol/sendKeyboardKeys.log',level=logging.DEBUG)

logging.info('sendkeys : ' + str(sys.argv))

if (len(sys.argv) > 1):
	shell = win32com.client.Dispatch("WScript.Shell")
	shell.SendKeys(sys.argv[1]) 

	