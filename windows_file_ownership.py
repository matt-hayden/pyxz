#!env python
# http://timgolden.me.uk/python/win32_how_do_i/get-the-owner-of-a-file.html

import win32api
import win32con
import win32security

FILENAME = "temp.txt"
open (FILENAME, "w").close ()

def get_username():
	return win32api.GetUserNameEx(win32con.NameSamCompatible)

def get_owner(path):
	sd = win32security.GetFileSecurity (path, win32security.OWNER_SECURITY_INFORMATION)
	owner_sid = sd.GetSecurityDescriptorOwner ()
	name, domain, type = win32security.LookupAccountSid (None, owner_sid)
	return domain+'\\'+name