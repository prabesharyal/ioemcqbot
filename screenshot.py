import json
import os
from fetchsheet import fetch_sheet
import sys
import subprocess
from tools import importjson

def shot_page(sh_n):
	rfname = f'./processedsheets/processed-{str(sh_n)}.json';
	if os.path.isfile(rfname):
		print('Loading from cache')
		return importjson(rfname)
	print('Fetching Sheets')
	c_sheet = fetch_sheet(sh_n)
	open(f'./toimg/fetchedsheet-{str(sh_n)}.json','w').write(json.dumps(c_sheet))
	print('Subprocess starting')
	proc = subprocess.run(["node", "./toimg/screenshot.js",str(sh_n)])
	print('Subprocess end')
	return importjson(rfname)
	# print(c_sheet)
