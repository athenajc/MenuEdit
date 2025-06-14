import os
import sys
import tkinter as tk
from tkinter import ttk
import time  

def get_box( box):  
    lst = []    
    for v in box:
        if type(v) == tk.DoubleVar:
            lst.append(v.get())
        else:
            lst.append(v)                        
    return lst
    
class SpliterVarV(tk.Frame):
    def __init__(self, layout, sepvar, yrange=(0.1, 0.9)):
        super().__init__(layout.master, relief='raise', bd=2, bg='white')
        self.layout = layout
        self.config(cursor='hand2')
        self.bind('<B1-Motion>', self.drag_v)
        self.sepvar = sepvar  
        self.yrange = yrange 
        
    def drag_v(self, event):
        obj = event.widget
        h = self.layout.size[1]
        obj_y = self.sepvar.get()
        obj_y += (event.y / h) /3
        y1, y2 = self.yrange
        if obj_y < y1:
            obj_y = y1
        elif obj_y > y2:
            obj_y = y2           
        y1 = obj_y + (8 / h) 
        self.sepvar.set(obj_y)   
        self.layout.update_objs()    


class SpliterVarH(tk.Frame):
    def __init__(self, layout, sepvar, xrange=(0.1, 0.9)):
        super().__init__(layout.master, relief='raise', bd=2)
        self.layout = layout
        self.config(cursor='hand2')        
        self.sepvar = sepvar  
        self.xrange = xrange
        self.bind('<B1-Motion>', self.drag_h)
            
       
    def drag_h(self, event):        
        x1, x2 = self.xrange
        obj = event.widget
        obj_x = self.sepvar.get()
        x = event.x
        dw = (abs(x)  / self.layout.size[0]) /3
        if x < -1 and obj_x > x1:
            obj_x -= dw
        elif x > 1 and obj_x < x2:
            obj_x += dw    
        
        self.sepvar.set(obj_x)     
        self.layout.update_objs() 
                
         
class AuiObj():
    def add_textobj(self, master, TextClass=None):
        if TextClass == None:
            from .TextObj import Text
            TextClass = Text
        textbox = TextClass(master)
        if hasattr(textbox, 'init_dark_config'):
            textbox.init_dark_config()   
        textbox.tag_config('find', foreground='black', background='#999')    
        return textbox
        
    def add_msg(self, master):
        from .Messagebox import Messagebox
        msg = Messagebox(master)
        msg.tk.setvar('msg', msg)    
        master.msg = msg
        return msg
        
    def add_filetree(self, master):
        from .FileTree import FileTreeView
        tree = FileTreeView(master)
        tree.tk.setvar('filetree', tree)   
        master.filetree = tree
        master.tree = tree
        return tree
        
    def add_tree(self, master):
        from .TreeView import TreeView
        tree = TreeView(master)
        tree.tk.setvar('filetree', tree)   
        master.filetree = tree
        master.tree = tree
        return tree
        
    def add_menu(self, master):
        from .Menu import MenuBar
        names = 'New,Open,,Close,,History,,Save,Save as,,Undo,Redo,,Copy,Cut,Paste,,'
        names += 'Add Tab,Remove Tab,,Graph'
        menubar = MenuBar(master, items=names.split(',')) 
        return menubar
        

class CanvasPanel(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.master = master
        self.config(background = "#d9d9d9")
        self.objs = []
        self.pos = 0, 0
        self.set_region(h=1000)   
        #self.add_scrollbar()        
        
    def add(self, obj, tag='obj', box=None):
        if box != None:
            x, y, x1, y1 = box
            item = self.create_window(x, y, window=obj, anchor='nw', tag=tag)
            self.itemconfig(item, width=x1-x, height=y1-y)
        else:    
            x, y = self.pos
            item = self.create_window(5, y+10, window=obj, anchor='nw', tag=tag)
        self.update()
        self.objs.append(obj)
        x0, y0, x1, y1 = self.bbox(item)
        self.pos = 0, y1      
        if y1 > self.h:  
           self.set_region(y1+50)
            
    def add_scrollbar(self):
        from aui.aui_ui import ScrollBar
        self.scrollbar = ScrollBar(self)        

    def reset(self):        
        for item in self.find_all():
            self.delete(item)
        for obj in self.objs:
            obj.destroy()
        self.y = 0
        self.objs = []
        self.set_region(500)
        
    def set_region(self, h):
        self.h = h    
        self.config(scrollregion = (0,0,800, h))

class Layout(AuiObj):     
    def __init__(self, master, **kw):              
        self.master = master
        self.root = master.winfo_toplevel()           
        self.tk = master.tk     
        self.objs = []
        self.seps = {}
        w, h = master.winfo_width(), master.winfo_height()
        self.vars = dict(left=0, top=0, right=1, bottom=1, w8=8/w, h8=8/h)        
        self.left, self.top = 0, 0
        
        self.size = self.root.size        
        self.w, self.h = w, h
        self.box = 0, 0, 1, 1 
        master.bind('<Configure>', self.on_config_master)        
        
    def on_config_master(self, event):
        w = event.width
        h = event.height
        self.vars['left'] = self.left/w
        self.vars['top'] = self.top/h
        self.vars['w8'] = 8/w
        self.vars['h8'] = 8/h
        self.size = w, h      
        self.w, self.h = w, h
        self.update_objs()
        
    def pack(self, **kw):
        pass        
        
    def get_value(self, v):            
        if type(v) == float:
            return v
        elif v in self.seps:                
            return self.get_sep(v)
        elif v in self.vars:
            return self.vars.get(v, 0)
        if type(v) == tk.DoubleVar:
            return v.get()
        else:
            return v
        
    def add(self, widget, box):
        if not widget in self.objs:   
            widget.box = box
            self.objs.append(widget)
            self.place_obj(widget)            
  
    def get_box(self, box):
        lst = []        
        for item in box:
            t = type(item)
            if t == float:
                v = item
            elif t == str and '+' in item: 
                a, b = item.split('+')
                a = self.get_value(a)
                b = self.get_value(b)
                v = a + b
            else:
                v = self.get_value(item)
            lst.append(v)
        return lst
        
    def place_obj(self, obj):        
        x, y, w, h = self.get_box(obj.box)        
        #x += 6/self.size[0]
        if x > 1:
            x = x/self.size[0]
        if y > 1:
            y = y/self.size[1]       
        obj.place(relx=x, rely=y, relwidth=w-x, relheight=h-y) 
           
    def update_objs(self):       
        w, h = self.size
        for obj in self.objs:
            self.place_obj(obj) 
           
    def update_sep(self, *event):    
        name = event[0]
        self.update_objs()                
        
    def get_sep(self, name):
        name = str(name)
        return self.seps[name].get()
        
    def set_sep(self, name, value):
        name = str(name)
        self.seps[name].set(value)
        
    def add_sepvar(self, value, name):
        obj = tk.DoubleVar(value=value, name=name)
        #obj.trace('w', self.update_sep)  
        self.seps[name] = obj
        return obj
        
    def add_left(self, obj, w=100):
        x, y = self.left, self.top
        obj.place(x=x, y=y, width=w, relheight=1)
        self.left += w
        self.vars['left'] = self.left/self.size[0]   
        left, top, right, bottom = self.box           
        self.box = 'left', top, right, bottom     
        
    def add_top(self, obj, h=32):
        x, y = self.left, self.top
        obj.place(x=x, y=y, relwidth=1, height=h)
        self.top += h        
        self.vars['top'] = self.top/self.size[1]    
        left, top, right, bottom = self.box           
        self.box = left, 'top', right, bottom

    def add_xsep(self, sep=0.5, xrange=(0.25, 0.75), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        xsep = 'xsep' + str(sep)
        sepvar = self.add_sepvar(value=sep, name=xsep)
        splith = SpliterVarH(self, sepvar, xrange=xrange)  
        self.add(splith, box=(xsep, top, xsep+'+w8', bottom))
        return xsep        
        
    def add_ysep(self, sep=0.5, yrange=(0.2, 0.9), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        ysep = 'ysep' + str(sep)        
        sepvar = self.add_sepvar(value=sep, name=ysep)                      
        splitv = SpliterVarV(self, sepvar, yrange=yrange)    
        self.add(splitv, box=(left, ysep, right, ysep + '+h8'))
        return ysep        
        
    def add_H2(self, f0, f1, sep=0.5, xrange=(0.25, 0.75), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        xsep = self.add_xsep(sep, xrange=xrange, box=box)
        self.add(f0, box=(left, top, xsep, bottom))
        self.add(f1, box=(xsep+'+w8', top, right, bottom))
        
    def add_V2(self, f0, f1, sep=0.5, yrange=(0.2, 0.9), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        ysep = self.add_ysep(sep, yrange, box)  
        self.add(f0, box=(left, top, right, ysep))
        self.add(f1, box=(left, ysep + '+h8', right, bottom))  
        
    def add_H3(self, f0, f1, f2, sep=(0.2, 0.75), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        sep1, sep2 = sep
        xsep1 = self.add_xsep(sep1, xrange=(0.11, 0.5), box=box)
        xsep2 = self.add_xsep(sep2, xrange=(0.55, 0.9), box=box)   
        self.add(f0, box=(left, top, xsep1, bottom))
        self.add(f1, box=(xsep1+'+w8', top, xsep2, bottom))       
        self.add(f2, box=(xsep2+'+w8', top, right, bottom)) 
        
    def add_H4(self, f0, f1, f2, f3, sep=(0.2, 0.6, 0.8), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        sep1, sep2, sep3 = sep
        xsep1 = self.add_xsep(sep1, xrange=(0.11, sep1+0.2), box=box)
        xsep2 = self.add_xsep(sep2, xrange=(sep2-0.2, sep2+0.2), box=box)   
        xsep3 = self.add_xsep(sep3, xrange=(sep3-0.2, 0.97), box=box) 
        self.add(f0, box=(left, top, xsep1, bottom))
        self.add(f1, box=(xsep1+'+w8', top, xsep2, bottom))       
        self.add(f2, box=(xsep2+'+w8', top, xsep3, bottom)) 
        self.add(f3, box=(xsep3+'+w8', top, right, bottom)) 
        
    def add_HV(self, f0, f1, f2, sep=(0.3, 0.7), xrange=(0.1, 0.8), yrange=(0.2, 0.9), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        sep1, sep2 = sep        
        xsep = self.add_xsep(sep1, xrange, box)
        ysep = self.add_ysep(sep2, yrange, box=(xsep+'+w8', top, right, bottom))     
        self.add(f0, box=(left, top, xsep, bottom))
        self.add(f1, box=(xsep+'+w8', top, right, ysep))
        self.add(f2, box=(xsep+'+w8', ysep + '+h8', right, bottom)) 
        
    def add_VH(self, f0, f1, f2, sep=(0.7, 0.3), xrange=(0.1, 0.8), yrange=(0.2, 0.9), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        sep1, sep2 = sep   
        xsep = self.add_xsep(sep2, xrange, box=(left, top, right, bottom))   
        ysep = self.add_ysep(sep1, yrange, box=(left, top, xsep, bottom))        
               
        self.add(f0, box=(left, top, xsep, ysep))
        self.add(f1, box=(left, ysep+'+h8', xsep, bottom))
        self.add(f2, box=(xsep+'+w8', top, right, bottom)) 
        
    def add_HVH(self, f0, f1, f2, f3, sep=(0.3, 0.5, 0.7), yrange=(0.2, 0.9), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        sep1, sep2, sep3 = sep        

        xsep1 = self.add_xsep(sep1, xrange=(0.11, 0.5), box=box)
        xsep2 = self.add_xsep(sep3, xrange=(0.55, 0.9), box=box)   
        ysep = self.add_ysep(sep2, yrange, box=(xsep1+'+w8', top, xsep2, bottom))     
        self.add(f0, box=(left, top, xsep1, bottom))
        self.add(f1, box=(xsep1+'+w8',          top, xsep2, ysep))
        self.add(f2, box=(xsep1+'+w8', ysep + '+h8', xsep2, bottom)) 
        self.add(f3, box=(xsep2+'+w8', top, right, bottom)) 
    
    def add_box(self, frame, box=None):
        if box == None:
            box = self.box
        self.add(frame, box=box)        
        

if __name__ == '__main__':
    from aui import App, Panel    
    app = App(title='Test', size=(1100, 900))   
    layout = Layout(app)

    f1 = tk.Text(app, bg='#aaa')
    f2 = tk.Text(app, bg='white')
    f3 = tk.Frame(app, bg='lightblue')
    
    ftop = tk.Frame(app, bg='gray')    
    layout.add_top(ftop, 60)
    fleft = tk.Frame(app, bg='lightgray')    
    layout.add_left(fleft, 100)
    
    layout.add_HV(f1, f2, f3)
    f1.insert('1.0', 'layout.add_V2(f1, f2, 0.6, (0.2, 0.9)) ')
    f2.insert('1.0', 'F2 f2 = tk.Text(app, bg=white)')
    #layout.add_H3(f1, f2, f3) 

    app.mainloop()






