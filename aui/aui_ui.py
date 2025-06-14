import os
import sys
import tkinter as tk
from tkinter import ttk
import time  


        
class TwoFrame(tk.Frame):    
    def __init__(self, master, type='v', sep=0.3, **kw):
        tk.Frame.__init__(self, master, **kw)  
        if type == 'left' or type == 'leftbar':
            self.init_leftbar(sep)
        elif type == 'top' or type == 'topbar':
            self.init_topbar(sep)
        elif type == 'right':
            self.init_right(sep)
        elif type == 'h':
            self.init_h(sep)
        else:
            self.init_v(sep)
            
    def get_frame(self):
        from aui.app import aFrame
        return aFrame(self)
        
    def init_leftbar(self, sep):
        w = sep*400
        frame1 = self.get_frame()
        frame1.place(x=0, y=0, width=w, relheight=1)
        frame2 = self.get_frame()
        frame2.place(x=w, y=0, relwidth=1, relheight=1)
        self.left = frame1
        self.right = frame2 
        
    def init_right(self, sep):  
        frame1 = self.get_frame()
        frame1.pack(side='left', fill='both', expand=True)
        frame2 = self.get_frame()
        frame2.pack(side='left', fill='y', expand=False)
        self.left = frame1
        self.right = frame2 
     
    def init_topbar(self, sep):
        h = sep * 300
        frame1 = self.get_frame()
        frame1.place(x=0, y=0, relwidth=1, height=h)
        frame2 = self.get_frame()
        frame2.place(x=0, y=h, relwidth=1, relheight=1) 
        self.top = frame1
        self.bottom = frame2
        
    def init_v(self, ysep): 
        frame0 = self.get_frame()
        frame0.place(x=0, y=0, relwidth=1, relheight=ysep)
        framespliter = tk.Frame(self, relief='raise', bd=1)
        framespliter.place(x=0, rely=ysep, relwidth=1, height=8)
        framespliter.config(cursor='hand2')
        frame1 = self.get_frame()
        dh = 8/1000
        frame1.place(x=0, rely=ysep+dh, relwidth=1, relheight=1-ysep-dh)
        framespliter.bind('<B1-Motion>', self.drag_spliter_v)
        framespliter.y = ysep
        self.spliter = framespliter
        self.f0 = frame0
        self.f1 = frame1
        self.top = frame0
        self.bottom = frame1
        
    def drag_spliter_v(self, event):
        y = event.y
        obj = self.spliter    
        ay = abs(y)    
        h = self.winfo_height()
        dh = (ay / h) /3
        if y < -1 and obj.y > 0.1:
            obj.y -= dh
        elif y > 1 and obj.y < 0.9:
            obj.y += dh           
        obj.place(rely = obj.y)
        self.f0.place(relheight=obj.y)
        y1 = obj.y + (5 / self.winfo_height())
        self.f1.place(rely=y1, relheight=1-y1)       
    
    def init_h(self, xsep):
        frameleft = self.get_frame()
        frameleft.place(x=0, y=0, relwidth=xsep, relheight=1)
        framespliter = tk.Frame(self, relief='raise', bd=1)
        framespliter.place(relx=xsep, y=0, width=6, relheight=1)
        framespliter.config(cursor='hand2')
        frameright = self.get_frame()
        dw = 6/1600
        frameright.place(relx=xsep+dw, y=0, relwidth=1-xsep-dw, relheight=1)
        framespliter.bind('<B1-Motion>', self.drag_spliter_h)
        framespliter.x = xsep
        self.spliter = framespliter
        self.f0 = frameleft
        self.f1 = frameright
        self.left = frameleft
        self.right = frameright        
        
    def drag_spliter_h(self, event):
        x = event.x
        obj = self.spliter    
        ax = abs(x)    
        w = self.winfo_width()
        if w == 1:
            w = 1920
        dw = (ax / w) /3
        if x < -1 and obj.x > 0.1:
            obj.x -= dw
        elif x > 1 and obj.x < 0.9:
            obj.x += dw           
        obj.place(relx = obj.x)
        self.f0.place(relwidth=obj.x)
        x1 = obj.x + (6 / w)
        self.f1.place(relx=x1, relwidth=1-x1)


        
class Notebook():
    def __init__(self, master, tab=None, cmd_action=None):
        if tab != None:
            style = ttk.Style(master)
            style.configure('lefttab.TNotebook', tabposition=tab)
            notebook = ttk.Notebook(master, style = 'lefttab.TNotebook')
        else:    
            notebook = ttk.Notebook(master)
        #notebook.pack(fill = 'both', expand=True)
        self.notebook = notebook
        self.place = notebook.place
        self.pack = notebook.pack
        if cmd_action == True:
            self.bind(cmd_action)
        
    def select(self, tab):
        nb = self.notebook  
        index = nb.index(tab)
        nb.select(index)
        
    def bind(self, action):
        self.notebook.bind('<ButtonRelease-1>', action)
        
    def reset(self):
        nb = self.notebook
        for tab in nb.tabs():
            nb.forget(tab)
        self.pages = {}
        
    def get_page(self):
        dct = self.notebook.tab('current')
        label = dct['text'].strip()
        return label        

    def add_page(self, label, widget=None):
        from aui import aFrame
        frame = aFrame(self.notebook)
        frame.pack(fill='both', expand=True)   
        frame.label = label      
        if widget != None:
            widget.notepage = frame
            widget.label = label                       
        self.notebook.add(frame, text=label)    
        #self.notebook.select(n)        
        return frame
        

class ScrollBar():
    def __init__(self, target):
        self.base = target
        scrollbar = ttk.Scrollbar(target, command=target.yview, cursor='arrow')
        scrollbar.place(relx=0.987, w=16, rely=0, relheight=1)
        self.scrollbar =  scrollbar
        target.config(yscrollcommand = self.on_scroll)
        target.bind('<Button-4>', self.on_scrollup)
        target.bind('<Button-5>', self.on_scrolldown)  
        
    def on_scrollup(self, event):  
        x, y = self.base.winfo_pointerxy()
        if self.base.winfo_containing(x, y):
           self.base.yview_scroll(-1, 'units')
    
    def on_scrolldown(self, event):
        x, y = self.base.winfo_pointerxy()
        if self.base.winfo_containing(x, y):
            self.base.yview_scroll(1, 'units')        
        
    def on_scroll(self, arg0, arg1):
        self.scrollbar.set(arg0, arg1) 
        
        
class ScrollFrame(tk.Text):
    def __init__(self, master):       
        super().__init__(master)
        self.config(state='disable')
        self.config(background = master.cget('background'))
        self.config(state= "disabled", font=('Mono', 20))        
        self.scrollbar = ScrollBar(self) 
        self.pack(fill='both', expand=True)
        
    def add(self, widget):
        self.window_create('end', window=widget)
        
    def get_frame(self):
        frame = tk.Frame(self)
        self.add(frame)
        return frame
        
    def puts(self, *lst, end='\n'):
        text = ''
        for s in lst:
            text += str(s) + ' '
        obj = self    
        obj.config(state= "normal")
        obj.insert('end', text + end)
        obj.config(state= "disable")
        
   

class FrameLayout():        
    def add_frame(self, frame, type=None, xsep=None, ysep=None):
        f0 = tk.Frame(frame)
        f1 = tk.Frame(frame)
        if type == 'v':            
            f0.pack(side='top', fill='x', expand=False)             
            f1.pack(side='top', fill='both', expand=True)  
        elif type == 'h':    
            f0.pack(side='left', fill='y', expand=False) 
            f1.pack(side='left', fill='both', expand=True)
        elif xsep != None:
            f0.place(x=0, y=0, relwidth=xsep, relheight=1)
            f1.place(relx=xsep, y=0, relwidth=1-xsep, relheight=1) 
        elif ysep != None:
            f0.place(x=0, y=0, relwidth=1, relheight=ysep)
            f1.place(x=0, rely=ysep, relwidth=1, relheight=1-ysep) 
        return f0, f1

    def add_spliter(self, master, ysep=0.5):
        frame0 = tk.Frame(master)
        frame1 = tk.Frame(master)
        frame0.place(x=0, y=0, relwidth=1, relheight=ysep)
        framespliter = tk.Frame(master, relief='raise', bd=1)
        framespliter.place(x=0, rely=ysep, relwidth=1, height=6)
        framespliter.config(cursor='hand2')
        dh = 6/1000
        frame1.place(x=0, rely=ysep+dh, relwidth=1, relheight=1-ysep-dh)
        framespliter.bind('<B1-Motion>', self.drag_spliter)
        framespliter.y = ysep
        self.spliter = framespliter
        framespliter.f0 = frame0
        framespliter.f1 = frame1      
        return frame0, frame1
        
    def drag_spliter(self, event):
        obj = event.widget
        h = self.winfo_height()
        obj.y += (event.y / h) /3
        if obj.y < 0.1:
            obj.y = 0.1
        elif obj.y > 0.9:
            obj.y = 0.9           
        y1 = obj.y + (6 / h)
        obj.place(rely = obj.y)
        obj.f0.place(relheight=obj.y)        
        obj.f1.place(rely=y1, relheight=1-y1)     
        
    def add_spliter_h(self, frame, xsep=0.5):
        frameleft = tk.Frame(frame)
        frameleft.place(x=0, y=0, relwidth=xsep, relheight=1)
        framespliter = tk.Frame(frame, relief='raise', bd=1)
        framespliter.place(relx=xsep, y=0, width=6, relheight=1)
        framespliter.config(cursor='hand2')
        frameright = tk.Frame(frame)
        dw = 6/1600
        frameright.place(relx=xsep+dw, y=0, relwidth=1-xsep-dw, relheight=1)
        framespliter.bind('<B1-Motion>', self.drag_spliter_h)
        framespliter.x = xsep
        self.spliter_h = framespliter
        framespliter.f0 = frameleft
        framespliter.f1 = frameright    
        return frameleft, frameright 
        
    def drag_spliter_h(self, event):
        w = self.winfo_width()
        obj = event.widget    
        obj.x += (event.x / w) /3
        if obj.x < 0.1:
            obj.x = 0.1
        if obj.x > 0.9:
            obj.x = 0.9        
        x1 = obj.x + (6 / w)     
        obj.place(relx = obj.x)
        obj.f0.place(relwidth=obj.x)        
        obj.f1.place(relx=x1, relwidth=1-x1)
   

if __name__ == '__main__':
    from aui import App
    app = App(title='Test', size=(900, 900))             
    app.add_test_msg()
    app.mainloop()

