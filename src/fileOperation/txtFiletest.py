__author__ = 'zhang'
# list = ['foo', 'bar']
# list.append("item")
# fl=open('d:/text.txt', 'w')
# for i in list:
#     fl.write(i)
#     fl.write("\n")
# fl.close()

import re
from bs4 import BeautifulSoup

#
# str = "http://bj.lianjia.com/xiaoqu/1111027381727/"
#
# print(str)
# href_array = re.findall(r"[0-9]+",str)
#
#
# print(type(href_array))
# print(href_array)
# print(href_array[0])

str = """<div class="info">
   <div class="title">
      <a href="http://bj.lianjia.com/chengjiao/BJTJ86209317.html" target="_blank">运河湾 3室2厅 128平米</a>
	</div>
	<div class="address">
	  <div class="houseInfo">
	  <span class="houseIcon"></span>南 北 | 其他 | 有电梯</div>
	  <div class="dealDate">2013.09</div>
	  <div class="totalPrice"><span class="number">545</span>万</div>
	</div>
	<div class="flood">
	     <div class="positionInfo"><span class="positionIcon"></span>高楼层(共33层) 2009年建板塔结合</div>
	     <div class="source">其他公司成交</div>
	     <div class="unitPrice">
	     <span class="number">40834</span>
	     元/平</div>
	</div>
	<div class="dealHouseInfo">
	  <span class="dealHouseIcon"></span>
	  <span class="dealHouseTxt">


	  </span>
	</div>
	<div class="dealCycleeInfo">
	    <span class="dealCycleIcon"></span>
	    <span class="dealCycleTxt">
		<span>挂牌570万</span>
		<span>成交周期13天</span>
		</span>
	</div>
</div>"""


# <span>房屋满五年</span>
soup =BeautifulSoup(str)
cj=soup.find('div',{'class':'info'})
# print(cj.find('a'))
# 获得楼层 朝向
content=cj.find('div',{'class':'houseInfo'})
print(content.text)
chaoxiang_zhuangxiu_dianti =content.text.split('|')
chaoxiang = chaoxiang_zhuangxiu_dianti[0]
zhuangxiu = chaoxiang_zhuangxiu_dianti[1]
dianti = chaoxiang_zhuangxiu_dianti[2]
# print(chaoxiang)
# print(zhuangxiu)
# print(dianti)

# 楼层 建造时间
positionInfo=cj.find('div',{'class':'positionInfo'})
loucheng_nianxian = positionInfo.text.split()
loucheng = loucheng_nianxian[0]
nianxian = re.findall(r"[0-9]+",loucheng_nianxian[1])

# 签约时间',u'签约单价',u'签约总价',
dealDate = cj.find('div',{'class':'dealDate'}).text
# 签约总价
totalPriceinfo = cj.find('div',{'class':'totalPrice'})
totalPrice = totalPriceinfo.find('span')
if totalPrice == None:
    totalPrice = '暂无价格'
else:
    totalPrice = totalPrice.text
    print(totalPrice)
#     u'签约单价'
unitPriceinfo = cj.find('div',{'class':'unitPrice'})
unitPrice = unitPriceinfo.find('span')
if unitPrice == None:
    unitPrice = '暂无价格'
else:
    unitPrice = unitPrice.text
    print(unitPrice)

# u'房产类型',u'学区',u'地铁'
fangchanleixing = '暂无'
dealHouseInfo = cj.find('div',{'class':'dealHouseInfo'})
if dealHouseInfo ==None:
	fangchanleixing = '暂无'
	xuequ = '暂无'
	subway = '暂无'
else:
	dealHouseTxt = dealHouseInfo.find('span',{'class':'dealHouseTxt'}).findAll('span')
	length = len(dealHouseTxt)
	dealHouseTxtStr = ''.join(cj.find('div',{'class':'dealHouseInfo'}).text.strip().split())

	if dealHouseTxt == None:
		fangchanleixing = '暂无'
		subway = '暂无'
	else:
		if len(dealHouseTxt)>1:
			fangchanleixing = dealHouseTxt[0].text
			subway = dealHouseTxt[1].text
		else:
			if dealHouseTxtStr.find(u'线')!=-1:
				subway = dealHouseTxt[0].text
			if dealHouseTxtStr.find(u'房')!=-1:
				fangchanleixing = dealHouseTxt[0].text

print(fangchanleixing)
# print(subway)


