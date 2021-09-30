import tkinter as tk
import tkinter.ttk as ttk

import PlotWindow as pw
import EuclideanLib as el

import time
import datetime as dt
import sys
import spidev
import os
import pymysql

spi=spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3)<<8)+adc[2]#中位8bitのうちの下2bit+下位8bit
    return data#指定したadコンバータから返ってきたアドレスを渡す

def ConvertVolts(data,places):#dataは補正前の値、placesは有効桁数
    vRef=5
    volts=(data*vRef)/float(1023)
    volts=round(volts,places)
    return volts

def PressureUpdate():
    global sitTime
    global conn_dist
    global conn_time
    
    global isSat#isSat,それまで座っていたかのフラグ
    isSit = False
    threshold = 4.0#座っていると判断する圧力の閾値
    
    pressure = []
    for ch in range(2):
        data = ReadChannel(ch)#ch:引数に接続されたセンサの値を読み取る
        volts=ConvertVolts(data,2)
        
        p = 5-volts#ここに電圧から圧力に直す式入れる
        pressure.append(p)
        if p>threshold:
            isSit = True
            
    pressure.append(0)
    pressure.append(0)
            
    if isSit:
        if not isSat:
            isSat = True
            print('座った瞬間')
            sitTime = dt.datetime.now()
    else:
        if isSat:
            isSat = False
            print('立った瞬間')
            with conn_time.cursor() as cursor:
                dt_now = dt.datetime.now()
                sql = 'INSERT INTO sit VALUES(%s,now())'
                cursor.execute(sql,sitTime)#test
            conn_time.commit()
    
    testDict = {'rf':pressure[0],'rb':pressure[1],'lf':pressure[2],'lb':pressure[3]}
    
    with conn_dist.cursor() as cursor:
        cursor.execute("SELECT count(id) FROM posture")
        result = cursor.fetchone()
        count = result["count(id)"]#len(result),postureテーブルのレコード数を代入
    
        nearestID = 0#とりあえずエラー出ないように0を代入
        nearestDistance = 9999
                
        for num in range(count):#これnumに該当するやつなかったらエラーでるな...例外処理めんどい
            sql = "SELECT * FROM posture WHERE id=%s"
            cursor.execute(sql,num)#↑のsql文のidの部分にnumを入れて実行、num番目のレコードの体圧分布取り出してる
            result = cursor.fetchone()#該当するやつが複数あったとしても一番上のだけ持ってくる
                
            if(result != None):#応急例外防止処理
                dist = el.Distance(testDict,result)
        
                if nearestDistance > dist:
                    nearestDistance = dist
                    nearestID = num
                    
        sql = "SELECT * FROM posture WHERE id=%s"
        cursor.execute(sql,nearestID)#一番分布が似てたやつを取り出す
        result = cursor.fetchone()

    global root#こっからGUIとか代入
    global canvasRF
    global canvasRB
    global canvasLF
    global canvasLB
    size = pressCanvasSize/2#代入用一時変数
    canvasRF.delete('text_RF')
    canvasRF.create_text(size,size,text=pressure[0],font=('',64),anchor=tk.CENTER,tag='text_RF')
    canvasRB.delete('text_RB')
    canvasRB.create_text(size,size,text=pressure[1],font=('',64),anchor=tk.CENTER,tag='text_RB')
    canvasLF.delete('text_LF')
    canvasLF.create_text(size,size,text=pressure[2],font=('',64),anchor=tk.CENTER,tag='text_LF')
    canvasLB.delete('text_LB')
    canvasLB.create_text(size,size,text=pressure[3],font=('',64),anchor=tk.CENTER,tag='text_LB')
    
    global canvas_risk
    canvas_risk.delete('text_risk')
    canvas_risk.create_text(20,100,text=result['risk'],font=('',24),anchor=tk.W,tag='text_risk')
    global canvas_advice
    canvas_advice.delete('text_advice')
    canvas_advice.create_text(20,100,text=result['advice'],font=('',24),anchor=tk.W,tag='text_advice')
    
    time.sleep(0.1)
    root.after(1,PressureUpdate)


def WindowControl(event):
    global subWindow
    global button_text
    if subWindow == None:
        subWindow = pw.CreateWindow()
        button_text.set('クリックでグラフを隠す')
    else:
        subWindow = pw.DestroyWindow()
        button_text.set('クリックでグラフを表示')

conn_dist = pymysql.connect(
    user='root',
    passwd='password',
    host='localhost',
    db='HealthChairTest',
    charset = 'utf8mb4',
    cursorclass = pymysql.cursors.DictCursor
)

conn_time = pymysql.connect(
    user='root',
    passwd='password',
    host='localhost',
    db='DateTimeTest',
    charset = 'utf8mb4',
    cursorclass = pymysql.cursors.DictCursor
)

isSat = False#1つ前のループまで座っていたかのフラグ
sitTime = dt.datetime.now()
subWindow = None
    
root=tk.Tk()
w = root.winfo_screenwidth()
w = w-360
h = root.winfo_screenheight()
h = h-360
root.geometry("360x360+"+str(w)+"+"+str(h))
root['bg'] = '#ffffff'
root.title("HealthChair")#ポップアップウィンドウ
#root.attributes('-zoomed',1)
#ウィンドウ用意
"""
#危険性表示フレーム
frame_risk = tk.Frame(root,padx=10,pady=10)

risk_label = tk.Label(frame_risk,text='危険性',padx=10,font=('',40))

#risk_border = tk.Canvas(frame_risk,width=500,height=15)
#risk_border.create_line(0,3,500,3,fill='#000000')

canvas_risk=tk.Canvas(frame_risk,width=1080,height=200,bg='#ffffff')
canvas_risk.create_text(20,100,text='',font=('',24),anchor=tk.W,tag='text_risk')
#canvas_risk.place(x=660,y=60)

risk_label.pack()
#risk_border.pack()
canvas_risk.pack()
frame_risk.place(x=660,y=60)

#アドバイス表示フレーム
frame_advice = tk.Frame(root,padx=10,pady=10)

advice_label = tk.Label(frame_advice,text='アドバイス',padx=10,font=('',40))

#advice_border = tk.Canvas(frame_risk,width=500,height=15)
#advice_border.create_line(0,3,500,3,fill='#000000')

advice_text = tk.StringVar()
advice_text = 'アドバイスのテキスト'
canvas_advice=tk.Canvas(frame_advice,width=1080,height=200,bg='#ffffff')
canvas_advice.create_text(20,100,text='',font=('',24),anchor=tk.W,tag='text_advice')
#canvas_risk.place(x=660,y=60)

advice_label.pack()
#advice_border.pack()
canvas_advice.pack()
frame_advice.place(x=660,y=400)
"""

root.mainloop()
