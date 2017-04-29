__author__ = 'zhang'

import urllib.request
import urllib.parse

values = {}
values['username'] = "1289356001@qq.com"
values['password'] = "xdl201234"
data = urllib.parse.urlencode(values).encode('utf-8')
url = "http://passport.csdn.net/account/login?from=http://my.csdn.net/my/mycsdn"
response =  urllib.request.urlopen(url,data).read()
response = response.decode('UTF-8','ignore')
print(response)

