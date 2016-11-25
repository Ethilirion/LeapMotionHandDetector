import win32con,win32security,win32process
import sys
import servicemanager

servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0xF000, ("Subprocess",""))

# python createprocessasuser.py "program to run" "arguments"

# Panneau de configuration / Outils d'administration / Strategie de securite locale / Strategies locales / Attribution des droits d'utilisateur / Remplacer un jeton de niveau processus (ajouter utilisateur courant)

# First create a token. We're pretending this user actually exists on your local computer or Active Directory domain.
user = "Pierre"
pword = "BRevmzgv"
domain = "." # means current domain
logontype = win32con.LOGON32_LOGON_INTERACTIVE
provider = win32con.LOGON32_PROVIDER_WINNT50

token = win32security.LogonUser(user, domain, pword , logontype, provider)

# Now let's create the STARTUPINFO structure. Read the link above for more info on what these can do.
startup = win32process.STARTUPINFO()

# if (len(sys.argv) > 1):
	# # \ == \\
	# print(sys.argv[1])
	# appname = sys.argv[1]
# else:
	# exit()
# if (len(sys.argv) > 2):
	# print(sys.argv[2])
	# arguments = sys.argv[2]
# else:
	# arguments = ""

hasPriv = False
privileges = win32security.GetTokenInformation(token, win32security.TokenPrivileges)
for i in privileges:
	if i[0] == win32security.LookupPrivilegeValue(None, win32security.SE_TCB_NAME):
		hasPriv = True
if (hasPriv == False):
	tuplePriv = (win32security.LookupPrivilegeValue(None, win32security.SE_TCB_NAME), win32security.SE_PRIVILEGE_ENABLED)
	print(tuplePriv)
	privileges = privileges + (tuplePriv,)
	print(privileges)
	win32security.AdjustTokenPrivileges(token, False, privileges)

# Finally, create a cmd.exe process using the "ltorvalds" token.
appname = "c:\\windows\\system32\\cmd.exe"
priority = win32con.NORMAL_PRIORITY_CLASS
win32process.CreateProcessAsUser(token, appname, None, None, None, True, priority, None, None, startup)
