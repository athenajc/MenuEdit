import tkinter as tk
from tkinter import ttk
from pprint import pformat
import PIL
import re
import DB

class Button(tk.Button):
    def __init__(self, master, text='', action=None, pack=None, **kw):
        super().__init__(master, text=text, cursor='arrow', **kw)
        self.bg = self.cget('bg') # '#d9d9d9'
        self.group = []
        self.name = text
        self.text = text
        self.action = action     
        self.bind('<ButtonRelease-1>', self.on_click)   
        if pack != None:
           self.pack(*pack)
           
    def on_click(self, event=None):
        if self.action != None:
            self.action(event)
        
    def set_state(self, state=True):
        if state:
            self.config(relief='raised', bg='#d0d0ff', fg='#000')
            self.focus()  
        else:    
            self.config(relief='flat', bg=self.bg, fg='#555')              

def add_button(master, name, action=None, pack=(), **kw):
    btn = Button(master, text=name)
    if action != None:
       btn.bind('<ButtonRelease-1>', action)
    if pack != None:
       btn.pack(pack)
    return btn
    
class tkOptionMenu(tk.OptionMenu):
    def __init__(self, master, items=['abcd'], act= None, **kw):
        var = self.var = tk.StringVar()
        var.set(items[0])
        super().__init__(master, var, *items, **kw)        
        self.config(cursor='hand2', width=10)
        self.tkvar = var
        name = self.cget('menu')
        self.menu = self.nametowidget(name)
        self.items = items
        if act != None:
           var.trace("w", self.on_trace)
           self.act = act

    def get(self):
        return self.tkvar.get()
        
    def set(self, text):
        self.tkvar.set(text)
        
    def set_text(self, text):
        self.tkvar.set(text)
        
    def add(self, label): 
        self.items.append(label)       
        self.menu.add_command(label=label, command=tk._setit(self.var, label))
        
    def set_items(self, items):
        self.items = []
        self.menu.delete(0, 'end')        
        for s in items:
            self.add(s)
                   
    def on_trace(self, event=None, arg1=None, arg2=None):    
        name = self.get()
        event = tk.Event()
        event.widget = self
        event.text = name
        self.act(event)
    
class tkEntry(tk.Entry):        
    def set(self, text):
        n = len(self.get())
        self.delete(0, n)
        self.insert(0, text)     
    
class LabelEntry():
    def __init__(self, master, text='', cmd=None, label=None, **kw):
        self.master = master
        if label != None:
            label = tk.Label(master, text=label, bg='#232323', fg='white', font=(14))
            label.pack(side='left', padx=5)
        self.entry = tk.Entry(master, **kw)    
        self.entry.pack(side='left', fill='x', expand=False, padx=5)
            
    def add_button(self, *data):
        text, action = data
        btn = add_button(self.master, text, action)
        btn.pack(side='left', padx=5)
        return btn
        
    def get(self):
        return self.entry.get()
        
    def set(self, text):
        entry = self.entry
        n = len(entry.get())
        entry.delete(0, n)
        entry.insert(0, text)       
        
         
def add_entry(frame, label=None, button=None, **kw):                      
    entry = LabelEntry(frame, label=label, **kw)
    if button != None:
        entry.add_button(button)   
    return entry
    


class AutoCombo(ttk.Combobox):
    def __init__(self, master, auto=False, **kw):
        ttk.Combobox.__init__(self, master, **kw)
        self.auto = auto
        self.default_values = list(self['values'])
        self._values = self.default_values
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace('w', self.on_changed)       
        self.pre_token = '' 
        
    def on_changed(self, name, index, mode):    
        if self.get() == self.pre_token:
            return
        self.event_generate('<<TextChanged>>')      
        token = self.get()
        if token == '':
            self['values'] = self.default_values
            self.close_listbox()
            self.pre_token = token
            return
        if self.auto == True:
            if token[-1] == '.':
                self['values'] = get_lst(token.rsplit('.', 1)[0])  
                #self.event_generate('<Down>')                     
                    
        words = self.comparison()        
        if len(words) == 1:
            if len(token) > len(self.pre_token):
                word = words[0]           
                n = len(token) 
                self.insert(n, words[0][n:])
                self.update()
        if words:
            self.update_listbox(words)
        else:
            self.close_listbox()
        self.pre_token = token

    def set_list(self, words):
        self['values'] = words 
        
    def set_text(self, text):
        self.var.set(text)
        
    def close_listbox(self):
        self.event_generate('<Up>')
        
    def update_listbox(self, words):
        if 0: #self.auto == True:
            self['values'] = words        
        
    def matches(self, fieldValue, acListEntry):
        pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
        return re.match(pattern, acListEntry)

    def comparison(self):
        return [ w for w in self['values'] if self.matches(self.var.get(), w) ]

def add_combo(master, text='', values=[]):
    combo = AutoCombo(master, values=values)
    combo.set_text(text)
    return combo
    
def add_sep(panel, w=1, h=100, padx=1, pady=1, bg=None):
    if bg == None:
        bg = panel.cget('bg')
    frame = tk.Frame(panel, width=w, height=h, bg=bg) #'#979899')
    panel.add(frame)


class PopMenu():
    def add_popmenu(self, cmds=[], master=None):
        if master == None:
            master = self
        menu = tk.Menu(master)
        for p in cmds:
            if p[0] == '-':
                menu.add_separator()
            else:
                menu.add_command(label=p[0], command=p[1])         
        self.menu = menu   
        self.menu.show = False
        master.bind('<ButtonRelease-1>', self.unpost_menu)
        master.bind('<ButtonRelease-3>', self.post_menu)             

    def unpost_menu(self, event=None):
        if self.menu.show == False:
            return
        self.menu.unpost()
        self.menu.show = False
        
    def post_menu(self, event=None):
        x, y = event.x, event.y   
        x1 = event.widget.winfo_rootx()     
        y1 = event.widget.winfo_rooty()
        self.menu.post(x + x1, y + y1)
        self.menu.show = True
        

class ToolBar(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, **kw)
        self.button = {}
        self.images = {}
        self.pressed = None
        self.bg = self.cget('bg')
        
    def set_pressed(self, label):
        if self.pressed != None:
            self.button[self.pressed].configure(relief='flat')
            self.button[self.pressed].configure(bg=self.bg)
        self.button[label].configure(relief='sunken')
        self.button[label].configure(bg='#777')
        self.pressed = label
            
    def load_image(self, filename):
        img = PIL.Image.open(filename).resize((32, 32))
        tkimage = PIL.ImageTk.PhotoImage(img)
        self.images[filename] = tkimage
        return tkimage
        
    def add_label(self, text, **kw):        
        label = tk.Label(self, text=text, **kw)
        label.pack(side='left')
        return label
        
    def add_button(self, label, image, action):
        img = self.load_image(image)
        button = tk.Button(self, relief='flat', compound='left', image=img)
        button.pack(side='left')
        self.button[label] = button
        button.label = label
        button.bind('<ButtonRelease-1>', action)
        return button        
        
    def add_spinbox(self, label='', value=3, vrange=(1,30), svar=None, action=None):
        if svar == None:
            svar = tk.StringVar(value=value)
        self.add_label(text=label)
        r0, r1 = vrange
        spin_box = ttk.Spinbox(self, from_=r0, to=r1, textvariable=svar, wrap=True, width=3)
        spin_box.pack(side='left')
        spin_box.svar = svar
        if action != None:
           spin_box.bind('<ButtonRelease-1>', action) 
           spin_box.bind('<KeyRelease>', action) 
        return spin_box 
        
    def add_vline(self):
        frame = tk.Frame(self, relief='sunken', bg='#777777', borderwidth=2)
        frame.pack(side='left', fill='y', expand=False, padx=1)
        

class MenuBar(tk.Frame):
    def __init__(self, master, items=[], style='v', relief='flat', **kw):
        super().__init__(master)
        self.button = {}
        self.style = style
        self.relief = relief
        self.bg = self.cget('bg')
        self.sep_color = '#979899'
        self.add_buttons(items, **kw)
        
    def reset(self):        
        for widget in self.pack_slaves():
            widget.destroy()
        self.buttons = {}        
        
    def add_button(self, key, action=None, **kw):
        button = Button(self, text=key, relief=self.relief, action=action, **kw)
        if self.style == 'v':
            button.pack(side='top', fill='x')
        else:    
            button.pack(side='left', fill='y')        
        self.button[key] = button
        
    def add_sep(self, h=1):
        if self.style == 'v':
           sep = tk.Frame(self, width=100, height=1, bg=self.sep_color)
           sep.pack(side='top', fill='x', pady=5) 
        else:
           sep = tk.Frame(self, width=1, height=40, bg=self.sep_color)
           sep.pack(side='left', fill='y', padx=5) 
        
    def add_buttons(self, items, **kw):        
        self.button = {}
        for key in items:
            action = None
            if type(key) in (tuple, list):
                if key[0] in ['', '-']:
                    self.add_sep()
                else:
                    self.add_button(key[0], key[1], **kw)
                
            elif key != '' and key != '-':
                self.add_button(key, action, **kw)
            else:
                self.add_sep()
        return self.button        
          
    def bind_action(self, item, action):
        self.button[item].bind('<ButtonRelease-1>', action) 
         


class ObjCommon():    
    from tkinter import filedialog as fd
    
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
            p = filetypes.get(name, (name, '*.'+name))        
            ftlst.append(p)  
        return ftlst
    
    def askopenfile(self, title='Open a file', path='/link', ext='py'):          
        return fd.askopenfile(title=title, initialdir=path, filetypes=self.get_filetypes(ext))
        
    def askopenfilename(self, title='Open an image', path=None, ext='img'):          
        if path == None:
           if ext == 'img':
              path =  '/link/data'
           else:
              path = '/link'
        return fd.askopenfilename(title=title, initialdir=path, filetypes=self.get_filetypes(ext))
                
    def askopenfiles(self, title='Open files', path='/link', ext='py'):          
        return fd.askopenfiles(title=title, initialdir=path, filetypes=self.get_filetypes(ext))
        
    def asksaveasfile(self, title='Save as file', path='/link', ext='py'):          
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
        
    def packfill(self, obj=None):
        if obj == None:
            self.pack(fill='both', expand=True)
        else:    
            obj.pack(fill='both', expand=True)
        
    def ask(self, op='openfile', **kw):
        if 'open' in op:
            if op == 'openfile':
                return askopenfile(**kw)
            if op == 'openfilename':
                return askopenfilename(**kw)    
            if op == 'openfiles':
                return askopenfiles(**kw)            
        if op == 'savefile' or op == 'saveasfile':
            return asksaveasfile(**kw)
        if op == 'string':
            return askstring(**kw)    
            

    def get_obj(self, name, **kw):        
        master = self
        if name == 'frame':
            from aui.app import aFrame
            return aFrame(master, **kw)
        elif name == 'layout':
            from aui.Layout import Layout
            return Layout(master, **kw)    
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
            from aui.app import ImageLabel
            widget = ImageLabel(master, **kw)

         
class Panel(tk.Text, ObjCommon):
    def __init__(self, master, style='h', items=None, size=None, **kw):        
        super().__init__(master, **kw)        
        self.size = size
        self.style = style
        self.root = master.winfo_toplevel()
        self.relief = 'flat'
        self.master = master
        self.auto_fill_objs = []
        self.base = self
        self.menu = None
        self.bg = master.cget('background')
        self.config(background = self.bg)
        self.config(state= "disabled", font=(20), cursor='arrow')        
        self.widgets = []
        self.limit = 1000
        if items != None:
            self.add_menu(items)
        self.get = self.get_obj    
        self.bind('<Configure>', self.on_configure)
        
    def on_configure(self, event=None):
        if self.auto_fill_objs == []:
            return
        for obj in self.auto_fill_objs:
            if 'x' in obj.fill:
                if hasattr(obj, 'font_width'):
                    w = obj.font_width
                    obj.config(width = ((event.width-w)//w-1))    
                else:
                    obj.config(width = event.width)  
            if 'y' in obj.fill:
                obj.config(height = event.height - 30)           
            
    def add_scrollbar(self):
        from aui.aui_ui import ScrollBar
        self.scrollbar = ScrollBar(self)        

    def reset(self):        
        self.base.delete('1.0', 'end')
        for widget in self.widgets:
            widget.destroy()
        self.widgets = []
        
    def puts(self, *lst, end='\n'):
        text = ''
        for s in lst:
            text += str(s) + ' '
        if len(text) > self.limit:
            text = text[0:self.limit]    
        obj = self    
        obj.config(state= "normal")
        obj.insert('end', text + end)
        obj.config(state= "disabled")
        
    def add_space(self, n = 1):
        if self.style == 'v':
            obj = tk.Label(self, text='', height=n, bg=self.bg)
        else:
            obj = tk.Label(self, text='', width=n, bg=self.bg)
        self.add(obj)        
        
    def newline(self, w=1920, h=1, bg=None):
        if bg == None:
            bg = self.cget('bg')
        frame = tk.Frame(self, width=w, height=h, bg=bg)  
        self.add(frame)
    
    def add_sep(self, size=None):
        if size == None:
            if self.size != None:
                w, h = self.size
            else:
                w, h = 100, 50
        else:
            w, h = size    
        if self.style == 'v':
            add_sep(self, w, 1, pady=15)              
        else:
            self.add_space(1) 
            add_sep(self, 1, h)
            self.add_space(1)         
       
    def insert_widget(self, index, widget):        
        if type(widget) == str:
            self.insert('end', widget)
            widget.panelpos = self.index('insert')
        else:
            self.widgets.append(widget)
            self.window_create(index, window=widget)
            widget.panelpos = self.index('insert')
        
    def add(self, widget, fill=None):
        if type(widget) == list:
            for obj in widget:
                self.insert_widget('end', obj)
        elif type(widget) == str:
            self.insert('end', widget)
        else:     
            widget.panelpos = self.index('end')
            self.insert_widget('end', widget)
            if fill != None:
                widget.fill = fill
                widget.y = int(self.index('end').split('.', 1)[0]) * 24
                self.auto_fill_objs.append(widget)
        if self.style == 'v':
            self.insert('end', '\n')
        
    def add_menu(self, items, pos='1.0', style=None, **kw): 
        self.menuitems = items       
        if style == None:
            style = self.style
        self.menu = menu = MenuBar(self, style=style, items=items)
        self.insert_widget(pos, menu)        
        return menu
        
    def add_options(self, label='', items=[], act=None):
        if label != '':
            self.add_label(label)
            self.add_space()
        optmenu = tkOptionMenu(self, items, act)
        self.add(optmenu)
        return optmenu
        
    def add_combo(self, label = '', text='', values=[], act=None):
        if label != '':
            self.add_label(label)            
        combo = add_combo(self, text, values)
        if act != None:
            combo.bind('<Return>', act) 
            combo.bind("<<ComboboxSelected>>", act)           
        self.add(combo)
        return combo
        
    def add_label(self, text, **kw):
        label = tk.Label(self, text=text, **kw)    
        self.add(label)
        return label
        
    def add_textvar(self):       
        textvar = tk.StringVar()
        label = tk.Label(self, textvariable=textvar, padx=20)
        label.textvar = textvar
        self.add(label)         
        return label
        
    def add_button(self, name, action=None, **kw):
        button = Button(self, text=name, action=action, **kw)
        self.add(button)
        if self.style == 'v':
            button.config(width=12, relief='flat')
            #button.pack(fill='x')
            self.insert('end', '\n')        
        return button
        
    def add_buttons(self, buttons, style='h', space=0, **kw):
        self.add_sep()
        lst = []   
        self.button = {}
        for a, b in buttons:   
            if a.strip() == '-' or a.strip() == '':
                self.add_sep()
                continue        
            btn = self.add_button(a, b, **kw)   
            if space != 0:
               self.add_space(space)
            lst.append(btn) 
            self.button[a] = btn
        self.add_sep()
        return lst
        
    def add_entry(self, label='', button=None, act=None, **kw):   
        labelobj = None
        if label != '':
            labelobj = self.add_label(label)
        entry = tkEntry(self, **kw)    
        self.add(entry)
        entry.label = labelobj
        entry.set_text = entry.set
        self.add_space()
        if act != None:
            entry.bind('<Return>', act) 
        return entry
        
    def on_select_color(self, event=None):  
        from aui import chooser_color, on_colorbutton    
        button = event.widget
        color = chooser_color(button, color=button.color)       
        button.color = color
        button.config(fg=color, bg=color, activebackground=color)
        button.config(text=str(color))
    
    def on_commit_colors(self, event):        
        lst = []
        for bn in self.buttons:
            lst.append(bn.color)
        text = pformat(lst)    
        DB.set_cache('colors', text)
    
    def add_colorbar(self, act=None): 
        from aui.ColorDialog import on_colorbutton       

        colors = eval(DB.get_cache('colors'))
        lst = []
        for color in colors:
            button = self.add_button(color, act)
            button.bind('<Button-3>', self.on_select_color)
            button.config(font=('bold', 9), fg=color, bg=color, activebackground=color, width=4)
            button.color = color
            lst.append(button)
        self.add_button('Update DB', self.on_commit_colors)     
        self.buttons =  lst


#----------------------------------------------------------------------------------      
if __name__ == '__main__':   
    from aui import App
    app = App(title='APP', size=(1024, 768))    
    
    def on_test(event):
        s = event.widget.text
        if s == 'Reset':
            menubar = event.widget.master
            menubar.reset()
            menubar.add_buttons([('Test', on_test), ('ABCD', on_test)])
        else:
            text = s + '\n' + str(event)
            app.showinfo(title=s, msg=text)
        
    def test_menubar(frame):                 
        names = 'Reset,Open,,Close,,History,,Save,Save as,,Undo,Redo,,Copy,Cut,Paste,,'
        names += 'Add Tab,Remove Tab,,Exec,,Run'
        items = []
        for s in names.split(',') :
            if s == '':
                items.append('-')
            else:
                items.append((s, on_test))        
 
        panel = Panel(frame, items=items, style='h', relief='raise', height=1)
        panel.pack(side='top')
        
        panel = Panel(frame, items=items, style='v', relief='raise', width=8)
        panel.pack(side='left')
 
        
     
    test_menubar(app)  
    panel = Panel(app)
    combo = panel.add_combo(label='dbFile:', values=['code', 'note'])
    options = panel.add_options(items=['code', 'note'] )
    panel.add_colorbar()
    msg = panel.get('msg')
    panel.add(msg, fill='x')
    options.set_items(['note', 'code', 'file'])
    
    panel.packfill()
    app.mainloop() 



