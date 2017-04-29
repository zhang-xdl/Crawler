__author__ = 'zhang'

# encoding:utf-8
import urllib.request
import urllib.error
import urllib.response
# import urllib2
import json
# import cookielib
import http.cookiejar
import time
import re
#获取Cookiejar对象（存在本机的cookie消息）
cookie = http.cookiejar.CookieJar()
#自定义opener,并将opener跟CookieJar对象绑定
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
#安装opener,此后调用urlopen()时都会使用安装过的opener对象
urllib.request.install_opener(opener)

home_url = 'http://bj.lianjia.com/'
auth_url = 'https://passport.lianjia.com/cas/login?service=http%3A%2F%2Fbj.lianjia.com%2F'
chengjiao_url = 'http://bj.lianjia.com/chengjiao/'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    # 'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'passport.lianjia.com',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
}
# 获取lianjia_uuid
req = urllib.request.Request('http://bj.lianjia.com/')
opener.open(req)
# 初始化表单
# req = urllib2.Request(auth_url, headers=headers)
req = urllib.request.Request(auth_url, headers=headers)
result = opener.open(req)
# print(result.info())
# print(result.headers)
print(result.headers['Set-Cookie'])
# print(cookie)
# 获取cookie和lt值
pattern = re.compile(r'JSESSIONID=(.*)')
# jsessionid = pattern.findall(result.info().getheader('Set-Cookie').split(';')[0])[0]
jsessionid = pattern.findall(result.headers['Set-Cookie'].split(';')[0])[0]
# .decode('utf-8')#python3这句代码 会报错
html_content = result.read().decode('utf-8')

pattern = re.compile(r'value=\"(LT-.*)\"')
lt = pattern.findall(html_content)[0]

pattern = re.compile(r'name="execution" value="(.*)"')
execution = pattern.findall(html_content)[0]

# print(cookie)
# opener.open(lj_uuid_url)
# print(cookie)
# opener.open(api_url)
# print(cookie)

# data
data = {
    'username': 'YOUR USERNAME',
    'password': 'YOUR PASSWORD',
    # 'service': 'http://bj.lianjia.com/',
    # 'isajax': 'true',
    # 'remember': 1,
    'execution': execution,
    '_eventId': 'submit',
    'lt': lt,
    'verifyCode': '',
    'redirect': '',
}
# urllib进行编码
# post_data=urllib.urlencode(data)
post_data=urllib.parse.urlencode(data).encode(encoding='UTF8')
# header
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Content-Length': '152',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'passport.lianjia.com',
    'Origin': 'https://passport.lianjia.com',
    'Pragma': 'no-cache',
    'Referer': 'https://passport.lianjia.com/cas/login?service=http%3A%2F%2Fbj.lianjia.com%2F',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'X-Requested-With': 'XMLHttpRequest',
}

headers2 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    # 'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'bj.lianjia.com',
    'Pragma': 'no-cache',
    'Referer': 'https://passport.lianjia.com/cas/xd/api?name=passport-lianjia-com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
}
# req = urllib2.Request(auth_url, post_data, headers)
# req = urllib.Request(auth_url, post_data, headers)
req = urllib.request.Request(auth_url, post_data, headers)
try:
    result = opener.open(req)
    print(result.info())
# except urllib2.HTTPError, e:
#     print e.getcode()
#     print e.reason
#     print e.geturl()
#     print "-------------------------"
#     print e.info()
#     print(e.geturl())
#     req = urllib2.Request(e.geturl())
#     result = opener.open(req)
#     req = urllib2.Request(chengjiao_url)
#     result = opener.open(req).read()
#     print(result)
except urllib.error.HTTPError as e:
    print (e.getcode())
    print (e.reason)
    print (e.geturl())
    print ("-------------------------")
    print (e.info())
    print(e.geturl())
    req = urllib.Request(e.geturl())
    result = opener.open(req)
    req = urllib.Request(chengjiao_url)
    result = opener.open(req).read()
    print(result)
