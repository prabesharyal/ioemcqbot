
import os

hashFile = 'BOT_API_HASH'
deftok = ""
if os.path.isfile(hashFile):
	deftok = open(hashFile).read()


defappname = "mcqquizbot"
TOKEN = os.environ.get('BOT_API_TOKEN') or deftok
APP_NAME = os.environ.get('APP_NAME') or defappname
print(TOKEN)
print(APP_NAME)
