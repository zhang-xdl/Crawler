__author__ = 'zhang'

import urllib.request
import urllib.parse
import re
import xlwt
import sqlite3
import random
import threading
from bs4 import BeautifulSoup
import xlsxwriter
# import importlib,sys
# importlib.reload(sys)
#
# sys.setdefaultencoding("utf-8")

import LianJiaLogIn





#Some User Agents
hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
     {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
     {'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}, \
     {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'}, \
     {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}, \
     {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
     {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
     {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'}, \
     {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
     {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
     {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'}, \
     {'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'}, \
     {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]


#北京区域列表
# regions=[u"东城",u"西城",u"朝阳",u"海淀",u"丰台",u"石景山","通州",u"昌平",u"大兴",u"亦庄开发区",u"顺义",u"房山",u"门头沟",u"平谷",u"怀柔",u"密云",u"延庆",u"燕郊"]
# regions=[u"dongcheng",u"xicheng",u"chaoyang",u"haidian",u"fengtai",u"shijingshan","tongzhou",u"changping",u"daxing",u"yizhuangkaifaqu",u"shunyi",u"fangshan",u"mentougou",u"pinggu",u"huairou",u"miyun",u"yanqing",u"yanjiao"]
regions=["tongzhou",u"changping"]


lock = threading.Lock()


class SQLiteWraper(object):
    """
    数据库的一个小封装，更好的处理多线程写入
    """
    def __init__(self,path,command='',*args,**kwargs):
        self.lock = threading.RLock() #锁
        self.path = path #数据库连接参数

        if command!='':
            conn=self.get_conn()
            cu=conn.cursor()
            cu.execute(command)

    def get_conn(self):
        conn = sqlite3.connect(self.path)#,check_same_thread=False)
        conn.text_factory=str
        return conn

    def conn_close(self,conn=None):
        conn.close()

    def conn_trans(func):
        def connection(self,*args,**kwargs):
            self.lock.acquire()
            conn = self.get_conn()
            kwargs['conn'] = conn
            rs = func(self,*args,**kwargs)
            self.conn_close(conn)
            self.lock.release()
            return rs
        return connection

    @conn_trans
    def execute(self,command,method_flag=0,conn=None):
        cu = conn.cursor()
        try:
            if not method_flag:
                cu.execute(command)
            else:
                cu.execute(command[0],command[1])
            conn.commit()
        except sqlite3.IntegrityError as e:
            #print e
            return -1
        except Exception as e:
            print (e)
            return -2
        return 0

    @conn_trans
    def fetchall(self,command="select * from xiaoqu",conn=None):
        cu=conn.cursor()
        lists=[]
        try:
            cu.execute(command)
            lists=cu.fetchall()
        except Exception as e:
            print (e)
            pass
        return lists

    @conn_trans
    def cj_fetchall(self,command="select * from chengjiao",conn=None):
        cu=conn.cursor()
        lists=[]
        try:
            cu.execute(command)
            lists=cu.fetchall()
        except Exception as e:
            print (e)
            pass
        return lists


def gen_xiaoqu_insert_command(info_dict):
    """
    生成小区数据库插入命令
    """
    info_list=[u'小区名称',u'小区标识',u'大区域',u'小区域',u'小区户型',u'建造时间']
    t=[]
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    t=tuple(t)
    command=(r"insert into xiaoqu values(?,?,?,?,?,?)",t)
    return command


def gen_chengjiao_insert_command(info_dict):
    """
    生成成交记录数据库插入命令
    """
    info_list=[u'链接',u'小区名称',u'户型',u'面积',u'朝向',u'楼层',u'建造时间',u'签约时间',u'签约单价',u'签约总价',u'房产类型',u'学区',u'地铁']
    t=[]
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    t=tuple(t)
    command=(r"insert into chengjiao values(?,?,?,?,?,?,?,?,?,?,?,?,?)",t)
    return command


# def xiaoqu_spider(db_xq,url_page=u"http://bj.lianjia.com/xiaoqu/pg1rs%E6%98%8C%E5%B9%B3/"):
def xiaoqu_spider(db_xq,url_page=u"http://bj.lianjia.com/xiaoqu/changping/pg1/"):
    """
    爬取页面链接中的小区信息
    """
    try:
        # req = urllib2.Request(url_page,headers=hds[random.randint(0,len(hds)-1)])
        req = urllib.request.Request(url_page,headers=hds[random.randint(0,len(hds)-1)])
        # source_code = urllib2.urlopen(req,timeout=10).read()
        source_code = urllib.request.urlopen(req,timeout=10).read()
        # plain_text=unicode(source_code)#,errors='ignore')
        soup = BeautifulSoup(source_code)
    except (urllib.request.HTTPError, urllib.request.URLError) as e:
        print (e)
        exit(-1)
    except Exception as e:
        print (e)
        exit(-1)

    xiaoqu_list=soup.findAll('div',{'class':'info'})
    # xiaoqu_list=soup.findAll('div',{'class':'title'})
    # # 移除第一个
    # del xiaoqu_list[0]
    for xq in xiaoqu_list:
        info_dict={}
        type_xq = type(xq)
        xiaoqu_a = xq.find('a')
        xiaoqu_href = xiaoqu_a.get('href')
        info_dict.update({u'小区名称':xq.find('a').text})

        href_array = re.findall(r"[0-9]+",xiaoqu_href)
        info_dict.update({u'小区标识':href_array[0]})
        content=(xq.find('div',{'class':'positionInfo'}).renderContents().strip()).decode('utf-8')
        info=re.sub(r"<.*?[^>]>",'',content)
        info=re.sub(r"\n",'',info)
        print(info)
        info_array = info.split()
        typeArray = type(info_array)
        info_dict.update({u'大区域':info_array[0]})
        info_dict.update({u'小区域':info_array[1]})
        info_dict.update({u'小区户型':info_array[2]})
        info_dict.update({u'建造时间':info_array[4]})
        # content.encode("utf-8")
        write_info_file(info_array)
        # # 获得价钱
        # price=soup.findAll('div',{'class':'totalPrice'})
        # price_value = price.find('span').text
        # info_dict.update({u'价钱/平':price_value})
        command=gen_xiaoqu_insert_command(info_dict)
        db_xq.execute(command,1)
        # insert_xiaoqu_excel_file(info_dict)

def write_info_file(info_array):
    file = open('d:/text.txt', 'a',encoding= 'utf8')
    file.write(info_array[0]+" ")
    file.write(info_array[1]+" ")
    file.write(info_array[2]+" ")
    file.write(info_array[4]+"\n")

# def do_xiaoqu_spider(db_xq,region=u"昌平"):
def do_xiaoqu_spider(db_xq,region=u"昌平"):
    """
    爬取大区域中的所有小区信息
    """
    # url="http://bj.lianjia.com/xiaoqu/rs"+region+"/"
    url=u"http://bj.lianjia.com/xiaoqu/"+region+"/"
    try:
        # req = urllib2.Request(url,headers=hds[random.randint(0,len(hds)-1)])
        req = urllib.request.Request(url,headers=hds[random.randint(0,len(hds)-1)])
        # source_code = urllib2.urlopen(req,timeout=5).read()
        source_code = urllib.request.urlopen(req,timeout=5).read()
        # plain_text=unicode(source_code)#,errors='ignore')
        # plain_text=urllib.parse.unquote (source_code)#,errors='ignore')
        soup = BeautifulSoup(source_code)
    except (urllib.request.HTTPError, urllib.request.URLError) as e:
        print (e)
        exit(-1)
    except Exception as e:
        print (e)
        exit(-1)
    d= soup.find('div',{'class':'page-box house-lst-page-box'}).get('page-data')
    # exec(d)
    # print(type(eval(d)))
    d = eval(d)
    total_pages=d['totalPage']
    url_page=u"http://bj.lianjia.com/xiaoqu/%s/pg%d/" %(region,1)
    # t=threading.Thread(target=xiaoqu_spider,args=(db_xq,url_page))
    xiaoqu_spider(db_xq,url_page)
    threads=[]
    for i in range(total_pages):
        # url_page=u"http://bj.lianjia.com/xiaoqu/pg%drs%s/" % (i+1,region)
        url_page=u"http://bj.lianjia.com/xiaoqu/%s/pg%d/" %(region,i+1)
        t=threading.Thread(target=xiaoqu_spider,args=(db_xq,url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def chengjiao_spider(db_cj,url_page=u"http://bj.lianjia.com/chengjiao/pg26c2011047640650/"):
    """
    爬取页面链接中的成交记录
    """
    try:
        # req = urllib2.Request(url_page,headers=hds[random.randint(0,len(hds)-1)])
        req = urllib.request.Request(url_page,headers=hds[random.randint(0,len(hds)-1)])
        # source_code = urllib2.urlopen(req,timeout=10).read()
        source_code = urllib.request.urlopen(req,timeout=10).read()
        # plain_text=unicode(source_code)#,errors='ignore')
        # plain_text=urllib.parse.unquote (source_code)#,errors='ignore')
        soup = BeautifulSoup(source_code)
    except (urllib.request.HTTPError, urllib.request.URLError) as e:
        print (e)
        exception_write('chengjiao_spider',url_page)
        exit(-1)
    except Exception as e:
        print (e)
        exception_write('chengjiao_spider',url_page)
        exit(-1)

    cj_list=soup.findAll('div',{'class':'info'})
    for cj in cj_list:
        info_dict={}
        href=cj.find('a')
        if not href:
            continue
        info_dict.update({u'链接':href.attrs['href']})
        content=cj.find('a').text.split()
        if content:
            info_dict.update({u'小区名称':content[0]})
            info_dict.update({u'户型':content[1]})
            info_dict.update({u'面积':content[2]})
        # content=unicode(cj.find('div',{'class':'con'}).renderContents().strip())
        # content=urllib.parse.unquote (cj.find('div',{'class':'con'}).renderContents().strip())

        content=cj.find('div',{'class':'houseInfo'})
        print(content.text)
        chaoxiang_zhuangxiu_dianti =content.text.split('|')
        chaoxiang = chaoxiang_zhuangxiu_dianti[0]
        zhuangxiu = chaoxiang_zhuangxiu_dianti[1]
        if len(chaoxiang_zhuangxiu_dianti)>2:
            dianti = chaoxiang_zhuangxiu_dianti[2]
        else:
            dianti = '暂无信息'


        info_dict.update({u'朝向':chaoxiang})

        # 楼层 建造时间
        positionInfo=cj.find('div',{'class':'positionInfo'})
        loucheng_nianxian = positionInfo.text.split()
        loucheng = loucheng_nianxian[0]
        nianxian = ''.join(re.findall(r"[0-9]+",loucheng_nianxian[1]))

        info_dict.update({u'建造时间':nianxian})
        info_dict.update({u'楼层':loucheng})

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

        info_dict.update({u'签约时间':dealDate})
        info_dict.update({u'签约单价':unitPrice})
        info_dict.update({u'签约总价':totalPrice})

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
        xuequ = '暂无'
        info_dict.update({u'房产类型':fangchanleixing})
        info_dict.update({u'学区':xuequ})
        info_dict.update({u'地铁':subway})
        command=gen_chengjiao_insert_command(info_dict)
        db_cj.execute(command,1)


def xiaoqu_chengjiao_spider(db_cj,xq_id=u"2011047640650"):
    """
    爬取小区成交记录
    """
    # url=u"http://bj.lianjia.com/chengjiao/rs"+urllib2.quote(xq_name)+"/"
    url=u"http://bj.lianjia.com/chengjiao/c"+xq_id+"/"
    try:
        req = urllib.request.Request(url,headers=hds[random.randint(0,len(hds)-1)])
        source_code = urllib.request.urlopen(req,timeout=10).read()
        # plain_text=urllib.parse.unquote (source_code)#,errors='ignore')
        # plain_text=unicode(source_code)#,errors='ignore')
        soup = BeautifulSoup(source_code)
    except (urllib.request.HTTPError, urllib.request.URLError) as e:
        print (e)
        exception_write('xiaoqu_chengjiao_spider',xq_id)
        return
    except Exception as e:
        print (e)
        exception_write('xiaoqu_chengjiao_spider',xq_id)
        return
    content=soup.find('div',{'class':'page-box house-lst-page-box'})
    total_pages=0
    if content:
        d=content.get('page-data')
        d = eval(d)
        total_pages=d['totalPage']
        # exec(d)
        # total_pages=d['totalPage']

    threads=[]
    for i in range(total_pages):
        # url_page=u"http://bj.lianjia.com/chengjiao/pg%drs%s/" % (i+1,urllib2.quote(xq_name))
        url_page=u"http://bj.lianjia.com/chengjiao/pg%dc%s/" % (i+1,xq_id)
        # url=u"http://bj.lianjia.com/chengjiao/c"+xq_id+"/"
        t=threading.Thread(target=chengjiao_spider,args=(db_cj,url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def do_xiaoqu_chengjiao_spider(db_xq,db_cj):
    """
    批量爬取小区成交记录
    """
    count=0
    xq_list=db_xq.fetchall()
    for xq in xq_list:
        xiaoqu_chengjiao_spider(db_cj,xq[1])
        count+=1
        print ('have spidered %d xiaoqu' % count)
    print ('done')


def exception_write(fun_name,url):
    """
    写入异常信息到日志
    """
    lock.acquire()
    f = open('log.txt','a')
    line="%s %s\n" % (fun_name,url)
    f.write(line)
    f.close()
    lock.release()


def exception_read():
    """
    从日志中读取异常信息
    """
    lock.acquire()
    f=open('log.txt','r')
    lines=f.readlines()
    f.close()
    f=open('log.txt','w')
    f.truncate()
    f.close()
    lock.release()
    return lines


def exception_spider(db_cj):
    """
    重新爬取爬取异常的链接
    """
    count=0
    excep_list=exception_read()
    while excep_list:
        for excep in excep_list:
            excep=excep.strip()
            if excep=="":
                continue
            excep_name,url=excep.split(" ",1)
            if excep_name=="chengjiao_spider":
                chengjiao_spider(db_cj,url)
                count+=1
            elif excep_name=="xiaoqu_chengjiao_spider":
                xiaoqu_chengjiao_spider(db_cj,url)
                count+=1
            else:
                print ("wrong format")
            print ("have spidered %d exception url" % count)
        excep_list=exception_read()
    print ('all done ^_^')

def insert_xiaoqu_excel_file(info_dict):
    workbook = xlsxwriter.Workbook("xiaoqu.xlsx")
    colom = 2
    savedata("1", ["小区名称", "小区标识","大区域", "小区域", "小区户型", "均价"])
    for day_list in info_dict:
        # 存储数据
        savedata(("%d" % (colom)), day_list)
        # 一共7天数据
        colom = colom + 1
        if len(day_list[1]) == 1:
            day_list[1] = "   " + day_list[1] + "     "
        elif len(day_list[1]) == 2:
            day_list[1] = "  " + day_list[1] + "    "
        elif len(day_list[1]) == 4:
            day_list[1] = " " + day_list[1] + " "
        elif len(day_list[1]) == 3:
            day_list[1] = "  " + day_list[1] + "  "

        if len(day_list[0]) == 6:
            day_list[0] = day_list[0] + " "
        if len(day_list[3]) == 1:
            day_list[3] = day_list[3] + " "
        print("| " + day_list[0] + " | " + day_list[1] + " | " + day_list[2] + "℃ ~ " + day_list[3] + "℃ |")
        print("-----------------------------------------")
        # 操作完毕关闭excel 类似数据库操作
        workbook.close()
# 存储数据 方法
def savedata(colom, content_list):
    # 创建excel
    workbook = xlsxwriter.Workbook("xiaoqu.xlsx")
    # 创建sheet
    worksheet = workbook.add_worksheet("xiaoqu")
    # 清空列以及行数
    worksheet.set_column("A:A", 1)
    worksheet.set_column("B:B", 1)
    worksheet.set_column("C:C", 1)
    worksheet.set_column("D:D", 1)
    worksheet.set_column("E:E", 1)
    # 传入参数 colom: 操作的行 content_list:行中每列内容
    colom_a = "A" + colom
    colom_b = "B" + colom
    colom_c = "C" + colom
    colom_d = "D" + colom
    colom_e = "E" + colom
    # 日期
    worksheet.write(colom_a, content_list[0])
    # 天气
    worksheet.write(colom_b, content_list[1])

    worksheet.write(colom_c, content_list[2])

    worksheet.write(colom_d, content_list[3])

    worksheet.write(colom_c, content_list[4])
    # 最高温度 - 最低温度
    # worksheet.write(colom_c, content_list[2] + "-" + content_list[3])

if __name__=="__main__":
    # command="create table if not exists xiaoqu (name TEXT primary key UNIQUE,xiaoqu_id TEXT,regionb TEXT, regions TEXT, style TEXT, year TEXT)"
    # db_xq=SQLiteWraper('lianjia-xq.db',command)
    # #
    command="create table if not exists chengjiao (href TEXT primary key UNIQUE, name TEXT, style TEXT, area TEXT, orientation TEXT, floor TEXT, year TEXT, sign_time TEXT, unit_price TEXT, total_price TEXT,fangchan_class TEXT, school TEXT, subway TEXT)"
    db_cj=SQLiteWraper('lianjia-cj.db',command)
    #
    # #爬下所有的小区信息
    # for region in regions:
    #     do_xiaoqu_spider(db_xq,region)
    #
    # #爬下所有小区里的成交信息
    db_xq=SQLiteWraper('lianjia-xq.db')
    # db_cj=SQLiteWraper('lianjia-cj.db')
    do_xiaoqu_chengjiao_spider(db_xq,db_cj)
    #
    # #重新爬取爬取异常的链接
    # exception_spider(db_cj)

    cj_list=db_cj.cj_fetchall()
    # file = open('d:/cj_list.txt', 'a',encoding= 'utf8')
    # # file.write('链接                小区名称           户型      面积       朝向      楼层     建造时间    签约时间      签约单价（元）/平米     签约总价（万元）     房产类型     学区      地铁 ')
    # file.writelines('链接                                   小区名称           户型      面积       朝向      楼层     建造时间    签约时间      签约单价（元）/平米     签约总价（万元）     房产类型     学区      地铁 ')
    # file.write('\n')
    workbook = xlwt.Workbook(encoding='utf-8')

    sheet = workbook.add_sheet('cj_list',cell_overwrite_ok=True)
    item = ['链接','小区名称','户型','面积','朝向','楼层','建造时间','签约时间',' 签约单价（元）/平米 ','签约总价（万元）','房产类型','学区','地铁']
    for i in range(1,14):
        sheet.write(0,i,item[i-1])
    i = 1
    for cj in cj_list:
         for k in range(1,14):
            sheet.write(i,k,cj[k-1])
         i = i+1
    workbook.save("d:/cj_list.xls")
        # print(cj[0])
        # file.write(cj[0]+"                 ")
        # file.write(cj[1]+"          ")
        # file.write(cj[3]+"     ")
        # file.write(cj[4]+"/平     ")
        # file.write(cj[5]+"     ")
        # file.write(cj[6]+"     ")
        # file.write(cj[7]+"     ")
        # file.write(cj[8]+"(元)/平米     ")
        # file.write(cj[9]+"万     ")
        # file.write(cj[10]+"     ")
        # file.write(cj[11]+"     ")
        # file.write(cj[12]+"     ")
