
import os

hashFile = 'BOT_API_HASH'
deftok = ""
if os.path.isfile(hashFile):
	deftok = open(hashFile).read()

TOKEN = os.environ.get('BOT_API_TOKEN') or deftok
print(TOKEN)
