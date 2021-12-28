
import requests
import json
from tools import importjson


url_pre = "https://raw.githubusercontent.com/FrozenCoder57/uniquemcqsheets/master/"


def fetch_sheet(no):
	sheet_num = int(no)
	req = requests.get(f'{url_pre}/mock-{str(no)}.json')
	dat = json.loads(req.text)
	return dat

# print(len(fetch_sheet(20)))