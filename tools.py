from string import Template
import base64
import json
def importjson(fn):
	return json.load(open(fn))

def atob(str):
	return base64.b64decode(str)


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {}
    d["M"], d["S"] = divmod(tdelta.seconds, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)