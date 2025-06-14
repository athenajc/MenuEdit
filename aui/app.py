import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
from aui.cache import *
from aui.Menu import MenuBar

user_path = os.path.expanduser('~/')
data_path = os.path.expanduser('~/.cache/data/')

def get_data_path():
    return data_path 

class ImageLabel(tk.Label):
    def __init__(self, master, obj=None, **kw):       
        super().__init__(master)
        from .ImageObj import ImageObj
        if obj == None:
            obj = ImageObj(**kw)
        self.imgobj = obj    
        self.update()
        self.bind('<Configure>', self.on_resize)
        
    def on_resize(self, event):
        w, h = event.width, event.height
        self.imgobj.resize(size=(w, h))
        self.update()
        
    def gradient(self, mode, cmap):
        bkg = self.imgobj                  
        bkg.gradient(mode, cmap)
        w, h = bkg.size
        bkg.get_draw()
        bkg.draw.rectangle((10, 10, w-10, h-10), outline=(0, 0, 0, 128))
        bkg.draw.rectangle((9, 9, w-11, h-11), outline=(255, 255, 255, 180))
    
    def update(self):
        self.tkimage = self.imgobj.get_tkimage()
        self.configure(image = self.tkimage) 
        
class Canvas(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)  
        self.root = master.winfo_toplevel()
        self.x, self.y = 0, 0
        self.objs = []
           
    def add(self, pos, widget, tag='widget'):
        x, y = pos
        self.create_window(x, y, window=widget, tag=tag)        
        
    def add_image(self, pos, imageobj, anchor='nw', tag='imageobj'): 
        tkimage = imageobj.get_tkimage()      
        x, y = pos
        imageobj.pos = pos
        item = self.create_image(x, y, image=tkimage, anchor=anchor, tag=tag) 
        self.objs.append(tkimage)
        return item                  


def set_icon(app, icon=None):    
    if icon == None:
        icon = get_data_path() + '/icon/puzzle.spng'
    try:    
        if not '/' in icon:
            icon = get_data_path() + '/icon/' + icon    
        root = app.winfo_toplevel()
        root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=icon))  
    except:
        print('load icon', icon, 'fail')

from tkinter import filedialog as fd
class ObjCommon():    
    filetypes = {
        'py': ('Python files', '*.py, *.txt'),
        'txt': ('Text files', '*.txt, *.py'),
        'img': ('Image files', '*.png *.svg *.jpg'),
        'image': ('Image files', '*.png *.svg *.jpg'),
        'all': ('All files', '*.*'),
        '*': ('All files', '*.*') 
    }    
        
    def get_filetypes(self, ext):
        ftlst = []
        for name in [ext, 'all']:
            p = self.filetypes.get(name, (name, '*.'+name))        
            ftlst.append(p)  
        return ftlst
    
    def askopenfile(self, title='Open a file', path='/link', ext='py'):          
        return fd.askopenfile(title=title, initialdir=path, filetypes=self.get_filetypes(ext))
        
    def askopenfilename(self, title='Open an image', path=None, ext='img'):          
        if path == None:
           if ext == 'img':
              path =  get_data_path()
           else:
              path = get_user_path()
        return fd.askopenfilename(title=title, initialdir=path, filetypes=self.get_filetypes(ext))
                
    def askopenfiles(self, title='Open files', path=user_path, ext='py'):          
        return fd.askopenfiles(title=title, initialdir=path, filetypes=self.get_filetypes(ext))
        
    def asksaveasfile(self, title='Save as file', path=user_path, ext='py'):          
        return fd.asksaveasfilename(title=title, initialdir=path, filetypes=self.get_filetypes(ext))
    
    def askstring(self, title, prompt):
        from tkinter import simpledialog
        answer = simpledialog.askstring(title, prompt)
        return answer

    def showinfo(self, title=None, msg=None, **options):
        from tkinter.messagebox import showinfo
        showinfo(title=title, message=msg, **options)
        
    def get_root(self):
        return self.winfo_toplevel()
        
    def ask(self, op='openfile', **kw):
        if 'open' in op:
            if op == 'openfile':
                return self.askopenfile(**kw)
            if op == 'openfilename':
                return self.askopenfilename(**kw)    
            if op == 'openfiles':
                return self.askopenfiles(**kw)            
        if op == 'savefile' or op == 'saveasfile':
            return self.asksaveasfile(**kw)
        if op == 'string':
            return self.askstring(**kw)    
            
    def init_colors(self):
        text = get_cache('aui.colors')            
        if text == None or text == '':
            dct = {'green': '#99c794', 'comment': '#a6acb9', 'key': '#9695d6', 'bg': '#323c44', 
               'text': '#d8dee9', 'dark': '#202327', 'str': '#f9ae58', 'in': '#e37373', 
               'name': '#5fb4b4', 'gray': '#777777', 'fg': '#acacac', 'def': '#c695c6'}
            set_cache('aui.colors', str(dct))
        else:
            dct = eval(text)
        self.colors = dct

    def add_obj_name(self, master, name, **kw):        
        if name == 'frame':
            return aFrame(master, **kw)
        elif name == 'msg':
            from aui.Messagebox import Messagebox
            return Messagebox(master)
        elif name == 'tree':
            from aui.TreeView import TreeView
            return TreeView(master)
        elif name == 'text':
            from aui.TextObj import Text
            return Text(master, **kw)
        elif name == 'filetree':
            from aui.FileTree import FileTreeView
            return FileTreeView(master)
        elif name == 'panel':
            from aui.Menu import Panel
            return Panel(master, **kw)    
        elif name == 'menu':
            from aui.Menu import MenuBar
            return MenuBar(master, **kw)    
        elif name == 'canvas':
            return Canvas(master, **kw)      
        elif name == 'image':
            widget = ImageLabel(master, **kw)
                
    def add_frame(self, objclass=None, master=None, **kw):
        if master == None:
            master = self        
        if objclass == None:
            frame = aFrame(master, **kw)
        else:    
            frame = objclass(master, **kw)
        frame.size = self.size
        return frame
        
    def packfill(self, obj=None):
        if obj == None:
            self.pack(fill='both', expand=True)
        else:    
            obj.pack(fill='both', expand=True)
        
    def add(self, obj='frame', **kw):
        if obj == 'frame':
            return aFrame(self, **kw)
        elif type(obj) == str:    
            return self.add_obj_name(self, obj, **kw)
        else:
            return aFrame(self, **kw)   
        
    def get_layout(self, master=None):
        from aui.Layout import Layout
        if master == None:
            master = self
        layout = Layout(master)
        return layout       
        
    def get(self, name, **kw):
        if name == 'layout':
            return self.get_layout(self)        
        if name in ['frame', 'text', 'msg', 'tree', 'filetree', 'nb', 'panel', 'menu', 'canvas']:
            return self.add_obj_name(self, name, **kw)     
        if name == 'image':            
            return ImageLabel(self, **kw)    
        if name in globals():
            return globals().get(name)            
        return self.tk.getvar(name)            

            
        
class aFrame(tk.Frame, ObjCommon):     
    def __init__(self, master, pack=True, **kw):       
        super().__init__(master, **kw)
        self.master = master
        self.root = master.winfo_toplevel()
        self.layout = None
        if pack == True:  
           self.pack(fill='both', expand=True)   

    def mainloop(self):
        self.root.mainloop()    
        
    def run(self, WidgetClass=None, arg=None):
        if WidgetClass != None:       
            if arg != None:    
                frame = WidgetClass(self, arg)
            else:
                frame = WidgetClass(self)
            frame.pack(fill='both', expand=True) 
        frame.mainloop()
        
    def add_frame(self, master, **kw):
        return aFrame(master, **kw)          
        
    def add_buttons(self, master, buttons, side='top'):   
        from aui.Menu import Panel     
        if master == None:
            master = self
        panel = Panel(master)
        panel.pack(side = side)
        return panel.add_buttons(buttons)
        
    def twoframe(self, master, style='', sep=0.5):
        from aui.aui_ui import TwoFrame
        frame = TwoFrame(master, type=style, sep=sep)  
        frame.pack(fill='both', expand=True) 
        return frame
        
    def add_menu(self, master, **kw):
        if master==None:
            master = self
        self.menubar = MenuBar(master, **kw)
        return self.menubar        

    def add_combo(self, master, text='', values=[], **kw):
        from aui.Menu import AutoCombo
        combo = AutoCombo(master, values=values)
        combo.set_text(text)
        combo.pack(**kw)
        return combo
        
    def add_label(self, master, text, **kw):
        label = tk.Label(master, text=text, **kw)    
        label.pack(**kw)
        return label                     
        
    def add_msg(self, master=None):
        if master==None:
            master = self
        self.msg = master.get('msg') 
        return self.msg    
        
    def add_set1(self, master=None, SideFrame=None, TextClass=None):
        if master==None:
            master = self
        layout = master.get('layout')
        if TextClass == None:
            self.text = text = master.get('text')
            text.init_dark_config()   
        else:
            self.text = text = TextClass(master)
         
        if SideFrame == None:
            self.tree = tree = master.get('filetree')
        else:
            self.tree = tree = SideFrame(master)       
        msg = self.add_msg(master)
        layout.add_HV(tree, text, msg, (0.3, 0.7))
        p = text, msg, tree
        msg.textbox = tree.textbox = text
        self.msg = tree.msg = text.msg = msg
        self.textbox, self.msg, self.filetree = p 
        return p        
        
    def add_test_msg(self, master=None):
        if master==None:
            master = self
        frame = self.twoframe(master, style='v', sep=0.7)
        msg = self.add_msg(frame.bottom)
        sys.stdout = msg         
        return frame.top
        
    def set_icon(self, icon=None):
        self.root.set_icon(icon)


               
class TopFrame(tk.Toplevel, ObjCommon):    
    def __init__(self, title='Test Frame', size=(1300, 900), **kw):       
        super().__init__(**kw)
        w, h = size
        self.size = (w, h)
        self.title(title)
        self.init_colors()
        self.root = self
        self.setvar('root', self)
        self.geometry('%dx%d'%(w, h))        
        
    def set_icon(self, icon=None):
        set_icon(self, icon)
        
class tkApp(tk.Tk, ObjCommon):
    def __init__(self, title='tkApp', size=(1024, 768), icon=None):
        super().__init__()
        self.title(title)
        self.init_colors()  
        self.setvar('root', self)
        appname = title.replace(' ', '')
        self.setvar('appname', appname)
        self.set_size(size)
        
    def set_icon(self, icon=None):
        set_icon(self, icon)
        
    def set_size(self, size):
        w, h = size        
        self.geometry('%dx%d'%(w, h)) 
        self.size = size
        
    def setvar(self, key, value):
        self.tk.setvar(key, value)
        
    def getvar(self, key):
        self.tk.getvar(key)       
        
    
        
                    
    
def App(title='A frame', size=(800, 600), Frame=None, icon=None):    
    root = tkApp(title, size, icon)
    if Frame == None:
        frame = root.get('frame')
    else:
        frame = Frame(root)
        frame.pack(fill='both', expand=True)
    frame.size = size
    frame.root = root
    root.app = root
    return frame
    


if __name__ == '__main__':
    import sys
    print(sys.path)
    app = App()
    #app.set_icon()
    #app.add_set1()
    #print(app.tk.getvar('app'))
    print([app.root.colors])
    print(app.bbox())
    app.mainloop()
    
    


