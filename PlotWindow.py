import tkinter as tk
import tkinter.ttk as ttk

import TimeBarPlot as plot

root_pw = None
img_pw = None

def CreateWindow():
    global root_pw
    global img_pw
    
    root_pw=tk.Tk()
    root_pw.geometry('740x560')
    root_pw['bg'] = '#ffffff'
    root_pw.title("着座時間棒グラフ")
    
    canvas_plot=tk.Canvas(root_pw,height=540,width=720)
    
    plot.TimePlot()
    img_pw=tk.PhotoImage(file="/home/pi/Desktop/PlotImage/SitTime.png",master=canvas_plot)
    canvas_plot.create_image(360,270,image=img_pw,anchor=tk.CENTER)

    canvas_plot.place(x=10,y=10)
    return root_pw

def DestroyWindow():
    global root_pw
    root_pw.destroy()
    return None
    