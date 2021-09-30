import os
import pymysql
import datetime as dt

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rc('font',family='Noto Sans CJK JP')

def TimePlot():
    conn = pymysql.connect(
        user='root',
        passwd='password',
        host='localhost',
        db='DateTimeTest',
        charset = 'utf8mb4',
        cursorclass = pymysql.cursors.DictCursor
    )
    
    #dt_now = dt.datetime.now()
    dt_now = dt.date.today()
    sitTimeList = []
    
    with conn.cursor() as cursor:
        for hour in range(24):#秒間隔テスト用、本番は24
            sql = 'SELECT SUM(sitting) FROM sittimetest WHERE date=%s and hour=%s'#今日のやつのみ取得
            cursor.execute(sql,(dt_now,hour))#test
            result = cursor.fetchone()
        
            if(result['SUM(sitting)'] != None):
                sumSitting = int(result['SUM(sitting)'])
                sitTimeList.append(sumSitting/60)
                #sitTimeList.append(sumSitting)
            else:
                sitTimeList.append(0)
        
    x = list(range(len(sitTimeList)))

    os.makedirs('Desktop/PlotImage',exist_ok=True)

    plt.bar(x,sitTimeList,width=0.9,align='edge',color='#0000ff')
    #なぜか色を指定しておかないと他から呼び出したときに積み上げ棒グラフになっていて色が変わるのだ…

    plt.grid(True)
    plt.title(dt_now)
    plt.xlabel('時間[時]')
    plt.ylabel('着座時間[分]')
    plt.xlim(0,24)
    plt.ylim(0,65)
    
    plt.savefig('Desktop/PlotImage/SitTime.png')
    