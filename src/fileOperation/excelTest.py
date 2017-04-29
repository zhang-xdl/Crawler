__author__ = 'zhang'
import xlwt
import sqlite3
import threading
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

workbook = xlwt.Workbook(encoding='utf-8')

sheet = workbook.add_sheet('cj_list1',cell_overwrite_ok=True)
item = ['链接','小区名称','户型','面积','朝向','楼层','建造时间','签约时间',' 签约单价（元）/平米 ','签约总价（万元）','房产类型','学区','地铁']

# db_xq=SQLiteWraper('lianjia-xq.db')
# db_cj=SQLiteWraper('lianjia-cj.db')
# # do_xiaoqu_chengjiao_spider(db_xq,db_cj)
# #
# # #重新爬取爬取异常的链接
# # exception_spider(db_cj)
#
# cj_list=db_cj.cj_fetchall()
# file = open('d:/cj_list.txt', 'a',encoding= 'utf8')
# # file.write('链接                小区名称           户型      面积       朝向      楼层     建造时间    签约时间      签约单价（元）/平米     签约总价（万元）     房产类型     学区      地铁 ')
# file.write('\n')
# for cj in cj_list:
for i in range(1,14):
    iten = item[i-1]
    sheet.write(0,i,item[i-1])
    # sheet.write(0,cj[0])
    # sheet.write(1,cj[1])
    # sheet.write(2,cj[2])
    # sheet.write(3,cj[3])
    # sheet.write(4,cj[4])
    # sheet.write(5,cj[5])
    # sheet.write(6,cj[6])
    # sheet.write(7,cj[7])
    # sheet.write(8,cj[9])
    # sheet.write(9,cj[9])
    # sheet.write(10,cj[10])
    # sheet.write(11,cj[11])
    # sheet.write(12,cj[12])

workbook.save("d:/cj_list1.xls")
