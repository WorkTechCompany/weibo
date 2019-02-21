# -*- coding:utf-8 -*-
import wx
import pymysql
import time
from blog import sendmessage
from concurrent.futures import ThreadPoolExecutor

def connect_db():
    db = pymysql.connect(host='cd-cdb-nmj4h99o.sql.tencentcdb.com', user='bryant', password='leekobe24', db='blog',
                         port=63625, charset='utf8')
    print('连接数据库成功！')
    return db

def openfile(event):  # 定义打开文件事件
    print(event)
    path = path_text.GetValue()
    with open(path, "r", encoding="utf-8") as f:  # encoding参数是为了在打开文件时将编码转为utf8
        content_text.SetValue(f.read())

def save_blog(event):
    db = connect_db()
    info = content_text.GetValue().split('\n')
    count = 0
    repeat_list = ''
    for item in info:
        result = item.split('----')
        if len(result) == 3:
            conn = db.cursor()  # 获取指针以操作数据库
            user = result[0]
            sql = 'SELECT user FROM blog where user=%s' % user
            conn.execute(sql)
            repeat_result = conn.fetchone()
            if repeat_result:
                repeat_list += item + '\n'
                continue
            password = result[1]
            name = result[2]
            status = 0
            t = [user, password, name, status]
            sql = u"INSERT INTO blog(user,password,name,status) VALUES (%s,%s,%s,%s)"
            conn.execute(sql, t)
            db.commit()  # 提交操作
            count += 1
    print('成功插入%d条数据' % (count))
    repeat.SetValue(repeat_list)

def open_thread(event):
    db = connect_db()
    conn = db.cursor()  # 获取指针以操作数据库
    use_times = start_count.GetValue()
    # if use_times == '':
    #     print('请输入运行次数')
    #     return

    # cardcode = CardCode()
    # result = cardcode.__vaild__(b'pin.png')
    print(use_times)
    card_number = []
    # with open('blog.txt', 'r') as f:
    #     for i in f.readlines():
    #         card_number.append(i.replace('卡号:', '').strip())
    # sql = 'SELECT user,password,name  FROM blog WHERE status=0 ORDER BY id LIMIT %d' % int(use_times)
    sql = 'SELECT user,password,name  FROM blog WHERE status=0 ORDER BY id'
    conn.execute(sql)
    blog_list = conn.fetchall()

    executor = ThreadPoolExecutor(max_workers=1)
    # user_id = get_uuid(32)
    # mac_site = get_mac_address()
    print('开启线程')
    task = executor.submit(start, blog_list)
    time.sleep(1)

def start(blog_list):
    for item in blog_list:
        print(item)
        print('开始运行')
        print(failed_user_list)
        user = item[0]
        password = item[1]
        name = item[2]
        print(user, password, name)
        check = sendmessage(user, password)
        if check:
            sql = "UPDATE blog SET status = 1 WHERE user = %s" % user
            success_user_list += item + '\n'
        else:
            print('失败')
            print(failed_user_list)
            failed_user_list += (user + '----' + password + '----' + name + '\n')
        print('aaaa',failed_user_list)
        success_info.SetValue(success_user_list)
        failed_info.SetValue(failed_user_list)


app = wx.App()
frame = wx.Frame(None, title="Gui Test Editor", pos=(250, 10), size=(1000, 800))

path_text = wx.TextCtrl(frame, pos=(5, 5), size=(330, 24))
open_button = wx.Button(frame, label="打开", pos=(350, 5), size=(50, 24))
open_button.Bind(wx.EVT_BUTTON, openfile)  # 绑定打开文件事件到open_button按钮上

save_button = wx.Button(frame, label="存入数据库", pos=(410, 5), size=(70, 24))
save_button.Bind(wx.EVT_BUTTON, save_blog)

content_text = wx.TextCtrl(frame, pos=(5, 39), size=(475, 500), style=wx.TE_MULTILINE)
wx.StaticText(frame, -1, "数据库已存在数据",(15, 550))
repeat = wx.TextCtrl(frame, pos=(5, 600), size=(475, 140), style=wx.TE_MULTILINE)
repeat.SetValue('暂无')

wx.StaticText(frame, -1, "请输入运行次数",(500, 5))
start_count = wx.TextCtrl(frame, pos=(600, 5), size=(50, 24))
start_button = wx.Button(frame, label="开始", pos=(680, 5), size=(70, 24))
start_button.Bind(wx.EVT_BUTTON, open_thread)  # 绑定打开文件事件到open_button按钮上

start_button = wx.Button(frame, label="停止", pos=(780, 5), size=(70, 24))
wx.StaticText(frame, -1, "成功账户信息",(500, 50))
success_info = wx.TextCtrl(frame, pos=(500, 100), size=(475, 300))
wx.StaticText(frame, -1, "失败账户信息",(500, 430))
failed_info = wx.TextCtrl(frame, pos=(500, 450), size=(475, 300))

frame.Show()
app.MainLoop()
