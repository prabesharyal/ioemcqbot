
import os

hashFile = 'BOT_API_HASH'
deftok = ""
if os.path.isfile(hashFile):
	deftok = open(hashFile).read()


defappname = "mcqquizbot"
defadm = ["semlohsofficial","PrabeshAryal"]
TOKEN = os.environ.get('BOT_API_TOKEN') or deftok
APP_NAME = os.environ.get('APP_NAME') or defappname
APP_NAME = os.environ.get('USERNAMES') or defappname

ADMINS = os.environ.get("ADMINS_LIST") or defadm

if os.environ.get("ADMINS_LIST"):
	ADMINS = ADMINS.split(";")

print(TOKEN)
print(APP_NAME)
print("Admins are: ",ADMINS)
