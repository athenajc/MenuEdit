import os
import sys
import re
import inspect
import tkinter
import tkinter as tk
from tkinter import ttk
import importlib
import webbrowser

import PyQt5
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Pango, GtkSource, GLib, GObject, Gio, Gdk, GdkPixbuf
from gi.repository import WebKit2
import numpy
import subprocess
import pkgutil
from multiframe import TwoFrame
from textui import PopMenu, TextObj               
        
class MsgBox(TextObj, PopMenu):
    def __init__(self, master, **kw):
        TextObj.__init__(self, master, **kw)
        self.textbox = None
        self.msg = self
        self.cmds = {}                      
        self.bind_cmd('c,clear', self.cmd_clear)        
        self.bind_cmd('doc', self.cmd_doc)
        self.bind_cmd('dir', self.cmd_dir)       
        self.bind_cmd('f,find', self.cmd_find)
        self.bind_cmd('go,goto', self.cmd_goto)        
        menucmds = []        
        menucmds.append(('Goto', self.cmd_goto))
        menucmds.append(('Find', self.cmd_find)) 
        menucmds.append(('-'))
        menucmds.append(('Copy', self.on_copy))
        menucmds.append(('Paste', self.on_paste))
        menucmds.append(('-'))
        menucmds.append(('Clear', self.cmd_clear))        
        self.add_popmenu(menucmds)
        self.click_time = 0
        self.bind('<ButtonRelease-1>', self.on_button1_up)
        
    def on_doubleclick(self):
        idx = self.index('insert')
        text = self.get_line_text(idx).strip()
        m = re.search('(?P<line>\d+)\s', text) 
        if m != None:            
            self.get_textbox(['goto', m.group('line')])
                
    def on_button1_up(self, event):
        self.menu.unpost()
        if event.time - self.click_time < 300:
            self.on_doubleclick()
        self.click_time = event.time      
        
    def bind_cmd(self, key, action):
        for s in key.split(','):
            s = s.strip()
            if s == '':
                continue
            self.cmds[s] = action   
          
    def cmd_clear(self, arg=None):
        self.clear_all()
        
    def cmd_doc(self, arg):
        if arg == '':
            arg = 'self'
        self.puts(arg)
        obj = eval(arg)
        self.puts(inspect.getdoc(obj))
        
    def cmd_dir(self, arg=None):
        self.puts(arg)
        obj = eval(arg)
        self.puts(obj)
        self.puts(dir(obj))
  
    def cmd_find(self, arg=None):
        if arg == None:
            arg = self.get_word()
        text = self.get_textbox('text')
        self.find_text(text, arg)
            
    def cmd_goto(self, arg=None):
        if arg == None:
            text = self.get_line_text()
            lst = re.findall('\s\d+\s', text)
            if lst == []:
                arg = self.get_word()
            else:
                arg = lst[0].strip()
        self.get_textbox(['goto', arg])  
        
    def get_textbox(self, action=None):        
        tb = self.textbox        
        if tb == None:
            return None                     
        if action == None:
            return tb
        elif action == 'text':
            return tb.get_text()
        elif action == 'sel':
            return tb.get_text('sel')
        cmd = eval('tb.' + action[0])
        arg = action[1]
        return cmd(arg)        
        
class HelpBox(TextObj, PopMenu):
    def __init__(self, master, **kw):
        TextObj.__init__(self, master, **kw) 
        self.module_list = []
        self.default_list = ['builtins', 'os', 'sys', 're', 'tkinter', 'gi.repository', 'inspect', 
            'pkgutil', 'subprocess', 'numpy', 'scipy', 'matplotlib', 'skimage', 'cairo', 'PyQt5', 'PIL', 'PIL.Image', 'PIL.ImageDraw']
        self.sys_module_list = list(sys.modules.keys())
        self.pkg_iter_modules()
        self.init_pattern()
        self.init_config()
        self.init_popmenu()
        self.click_time = 0  
        self.bind('<KeyRelease>', self.on_keyup)
                
    def on_keyup(self, event):
        key = event.keysym
        state = event.state
        if state == 0x14 and  key == 'f':
            self.find_text()
        elif key == 'F1':
            self.on_open_module()
    
    def init_pattern(self):
        p = '(?P<title>[A-Z\s\-\_\:]+)|(?P<function>\w+)(?=\()' 
        p += '|(?P<helpon>Help on .*\:)|(?P<colon>\w.+\:)'
        self.pattern = re.compile(p)   
        p = '(?P<title>^[A-Z][A-Z\s\-\_\:]+)|(?P<function>\w+)\s*(?=\()|(?P<colon>\w.+\:)'
        self.help_pattern = re.compile(p)                    
        
    def init_config(self):
        self.config(foreground='#555')
        self.tag_config('find', font='Mono 10 bold', foreground='#555')
        self.tag_config('title', font='Mono 11 bold', foreground='#333') 
        self.tag_config('bold', font='Mono 10 bold', foreground='#333')
        self.tag_config('function', font='Mono 10', foreground='#000')      
        self.tag_config('helpon', font='Mono 10 bold', foreground='#000', background='#ddd')   
        self.tag_config('colon', font='Mono 10 bold', foreground='#555')
        self.tag_config('black', font='Mono 10', foreground='#000')
        self.tag_config('word', font='Mono 10', foreground='#222')
        self.tag_config('gray', font='Mono 10', foreground='#333')
        
    def init_popmenu(self):
        cmds = []
        cmds.append(('Goto', self.on_open_module))
        cmds.append(('Find', self.on_find_text))    
        cmds.append(('Google Search', self.on_google_search))
        cmds.append(('Copy', self.on_copy))        
        cmds.append(('-'))
        cmds.append(('Select All', self.on_select_all))    
        cmds.append(('Clear All', self.clear_all))           
        self.add_popmenu(cmds)    
        
    def on_open_module(self, event=None):
        text = self.get_text('sel')
        if text == '' or ' ' in text:
            text = self.get_word('insert')
        if text in self.module_list:
            self.parent.set_obj(text)
        else:
            head = self.entry_obj.get()
            if head != '':
                text = head + '.' + text
            self.parent.set_obj(text)
            
    def on_open_member(self, event=None):
        text = self.get_text('sel')
        if text == None:
            return        
        elif re.match('[\w\.]+', text) != None:
            head = self.entry_obj.get()
            if head != '':
                text = head + '.' + text
            self.parent.set_obj(text)  
            
    def on_find_text(self, event=None):
        text = self.get_text('sel')
        if text == None:
            return              
        self.find_text(text)
        
    def on_google_search(self, event=None):
        base_url = "http://www.google.com/search?q="
        text = self.get_text('sel')
        if text == None:
            return 
        head = self.entry_obj.get()
        if text in head:
            text = ''
        webbrowser.open(base_url + 'python ' + head + ' ' + text)
        
    def puts(self, *lst, end='\n'):
        text = ''
        if lst == None:
            text = 'None'
        elif lst == []:
            text = '[]'
        else:
            for s in lst:
                if s == None:
                    s = 'None'
                if type(s) != str:
                    s = str(s)
                text += s + ' '
        self.insert('insert', text + end)
        
    def list_str(self, lst):
        t = ' '
        text = ''
        n = int(self.winfo_reqwidth() / 20)
        for s in lst:
            t += s.ljust(20) + ' '
            if len(t) > n:
                text += t + '\n'
                t = ' '
        return text + t
        
    def put_list(self, lst, bychar=False):
        if bychar == False:      
            self.puts(self.list_str(lst))
        else:
            dct = {}
            lst1 = []
            for s in lst:
                c = s[0].lower()
                if not c in lst1:
                    lst1.append(c)
            lst1.sort()
            for c in lst1:
                dct[c] = []
            for s in lst:
                c = s[0].lower()
                dct[c].append(s)
            self.print_dct(dct)
        
    def print_dct(self, dct):
        for s, v in dct.items():
            if v == []:
                continue
            self.puts_tag(s[0].upper()+s[1:], 'bold', head='\n', end='\n')
            self.put_list(v)       
        
    def tag_update(self):
        text = self.get_text()
        if text == None:
            return        
        i = 0       
        for line in text.splitlines():             
            i += 1
            p = str(i) + '.'
            s = line.strip().lower()
            if s in ['module', 'class', 'function', 'name']:
                self.tag_add('bold', p + '0', p + str(len(line)))
                continue
            if s[0:4] == 'help':
                self.tag_add('helpon', p + '0', p + str(len(line)))
                continue
            m = re.search(self.help_pattern, line)            
            if m == None or m.start() > 8:                
                continue     
            
            for tag, s in m.groupdict().items():
                if s == None:
                    continue
                i1 = line.find(s, m.start())
                i2 = i1 + len(s)
                self.tag_add(tag, p + str(i1), p + str(i2))          

    def find_in_module_list(self, t):
        t = t.lower()
        lst = []            
        for s in self.module_list:
            if s.lower().find(t) == 0:
                lst.append(s)
        self.put_list(lst)                    
        return lst  
            
    def get_help(self, objname): 
        self.help_text = ''
        sys.stdout = self    
        help(objname)       
        sys.stdout = self.msg  
            
    def try_import(self, m):    
        module = None   
        try:
            module = __import__(m, globals=globals())               
        except:
            module = None
        return module             
        
    def get_module_members(self, modulename, printout=True):
        #self.msg.puts('get_module_members', modulename)      
        if type(modulename) == str:
            if modulename == 'builtins':
                return {}
            try:
                module = eval(modulename)
            except:
                module = self.try_import(modulename) 
        dct = {'module':[], 'class':[], 'function':[]}
        for name, des in inspect.getmembers(module):
            for item in dct:
                if str(des).find(item) == 1:                    
                    dct[item].append(name)
        if printout == True:
           self.print_dct(dct)
        return dct        
        
    def get_class_members(self, classname):
        lst = []
        for name, des in inspect.getmembers(classname):            
            if str(des).find('function') == 1:                    
                lst.append(name)    
        return lst          
        
    def print_module_list(self):
        self.put_list(lst = self.default_list)
        self.put_list(self.module_list, bychar=True)
        #self.put_list(lst=self.sys_module_list, bychar=True)
        
    def pkg_iter_modules(self): 
        lst = list(self.default_list)
        for p in pkgutil.iter_modules():
            importer, name, ispkg = p
            importer = str(importer)
            if not 'python' in importer or '_' in name:
                continue
            if ispkg and not name in lst:
                lst.append(name)            
        self.module_list = lst        
        
    def get_dir(self, objname):
        self.try_import(objname)
        obj = eval(objname)
        dct = {'module':[], 'class':[], 'function':[]}
        for s in dir(obj):
            subobj = eval(objname + '.' + s)
            if inspect.ismodule(subobj):
                dct['module'].append(s)
                #self.puts(s, 'module') 
            elif inspect.isclass(subobj):
                dct['class'].append(s)
                #self.puts(s, 'class') 
            elif inspect.ismethod(subobj) or inspect.isfunction(subobj):
                dct['function'].append(s)
                #self.puts(s, 'isfunction') 
        self.print_dct(dct)
        return dct
        
    def fwrite(self, text, filename):
        with open(filename, 'w') as f:
            f.write(text)
            f.close()
            self.msg.puts(filename + ' saved.')
           
    def fread(self, filename):
        if os.path.exists(filename) == False:
            return ''
        with open(filename, 'r') as f:
            text = f.read()
            f.close()
            return text
        return ''
        
    def set_obj(self, objname):
        #print('(%s)'%objname)
        self.clear_all()        
        if objname == '':            
            self.print_module_list()
            return                    
        obj_filename = '/home/athena/src/help/text/%s.txt' % objname
        if os.path.exists(obj_filename):
            text = self.fread(obj_filename)
            self.puts(text)
            self.tag_update()
            return
        if objname in self.module_list:
            self.get_module_members(objname, True)     
        self.get_help(objname)
        self.tag_update() 
        text = self.get_text()
        if text != None:
           self.fwrite(text, obj_filename)
        
    def find_obj(self, objname, head='', modules=None, level=0):
        if objname == '':
            return     
        if level > 5 or modules == []:
            return
        if level == 0:   
            if objname in self.sys_module_list:
                return objname
            if '.' in objname:
                p = objname.rsplit('.', 1)
                m = p[0]
                module_name = self.find_obj(m)
                if module_name != '':
                    modules = [module_name]
                    objname = p[1]                
            elif objname in self.module_list:
                return objname
            elif objname[0] == 'Q':
                modules = ['PyQt5']
            elif objname in ['Gtk', 'GObject', 'GtkSource', 'Pango', 'WebKit2', 'GLib', 'Gio', 'Gdk', 'GdkPixbuf']:
                return 'gi.repository.' + objname
            else:
                modules = self.default_list                
        if objname in modules:
            return objname
        for m in modules:
            if level != 0:
                if m in ['os', 'sys', 'stat', 're', 'inspect'] or head.find(m) == 0:
                    continue
            if head == '':
                m1 = m
            else:
                m1 = head + '.' + m
            dct = self.get_module_members(m1, False)
            if dct == {}:
                continue    
            if objname in (dct['module'] + dct['class'] + dct['function']):
                return '%s.%s' % (m1, objname)
            if dct['module'] == []:
                continue
            s = self.find_obj(objname, m1, dct['module'], level+1)            
            if s != '' and s != None:
                if s.find(m1) == 0:
                    return s
                return m1 + '.' + s
        return ''
          
        
class HelpFrame(tk.Frame, PopMenu):
    def __init__(self, master, msgbox=None, cnf={}, **kw):
        tk.Frame.__init__(self, master)
        self.read_map()
        frame = self
        self.pack(fill='both', expand=True)
        
        frametop = tk.Frame(self)
        frametop.pack(side='top', fill='x', expand=False)
        self.menu = self.create_menu_button(frametop)
        button_back = tk.Button(frametop, text='<', relief='flat')
        button_back.pack(side='left')       
        entry_obj = tk.Entry(frametop, width=12)
        entry_obj.pack(side='left', fill='x', expand=True)
        label = tk.Label(frametop, text='.')
        label.pack(side='left')
        entry_find = tk.Entry(frametop, width=12)
        entry_find.pack(side='left')   
        button_find = tk.Button(frametop, text='Find', relief='flat')
        button_find.pack(side='left') 
        if msgbox == None:
            frame1 = TwoFrame(frame, sep=0.75, type='v')
            frame1.pack(fill='both', expand=True)
            msgbox = MsgBox(frame1.bottom)   
            msgbox.pack(fill='x', expand=False)           
            textbox = HelpBox(frame1.top, width=120, wrap=None)
            textbox.place(x=0, y=0, width=1000, relheight=1) 
            scrollbar = tk.Scrollbar(frame1.top, command=textbox.yview)
        else:
            textbox = HelpBox(frame, width=120, wrap=None)
            textbox.place(x=0, y=0, width=1000, relheight=1) 
            scrollbar = tk.Scrollbar(frame, command=textbox.yview)        
        scrollbar.pack(side='right', fill='y', expand=False)
        textbox.scrollbar = scrollbar
        textbox['yscrollcommand'] = scrollbar.set                  
        textbox.entry_obj = entry_obj
        textbox.msg = msgbox
        textbox.parent = self
        self.msg = msgbox        
        msgbox.textbox = textbox
        self.entry_obj = entry_obj
        self.entry_find = entry_find
        self.textbox = textbox
        self.helpbox = textbox
        self.set_obj('')
        button_back.bind('<ButtonRelease-1>', self.on_button_back)
        button_find.bind('<ButtonRelease-1>', self.on_button_find)    
        entry_obj.bind('<KeyRelease>', self.on_entry_obj_keyup) 
        entry_find.bind('<KeyRelease>', self.on_entry_find_keyup) 

    def on_entry_obj_keyup(self, event=None):
        if event.keysym == 'Return':            
            self.set_obj(event.widget.get(), map=True)                
        
    def on_entry_find_keyup(self, event=None):
        if event.keysym == 'Return':
            text = self.textbox.find_text(event.widget.get())
        
    def menu_item_selected(self, *args):
        item = self.selected_item.get()
        self.set_entry_obj_text(item)
        self.helpbox.set_obj(item)
        
    def create_menu_button(self, frame):
        self.history_list = ['']
        self.selected_item = tk.StringVar()
        self.selected_item.trace("w", self.menu_item_selected)
        
        menu_button = ttk.Menubutton(frame, text='')
        menu = tk.Menu(menu_button, tearoff=0)
        for item in self.history_list:
            menu.add_radiobutton(
                label=item,
                value=item,
                variable=self.selected_item)

        # associate menu with the Menubutton
        menu_button["menu"] = menu

        menu_button.pack(side='left', expand=False)
        return menu
                
    def on_button_back(self, event):
        s = self.entry_obj.get().strip()
        if not '.' in s:
            self.set_obj('')
        else:
            p = s.split('.')
            s = '.'.join(p[0:-1])
            self.set_obj(s)        
        
    def on_button_find(self, event):
        self.msg.clear_all()
        s = self.entry_find.get().strip()
        if s != '':
            self.textbox.find_text(s)
        
    def set_entry_obj_text(self, s):
        self.entry_obj.delete(0, 'end')
        self.entry_obj.insert('insert', s)              
        
    def get_name_map(self, s):
        dct = self.name_map        
        key = s.lower().strip()
        if key in dct:
            return dct.get(key)
        if not '.' in s:
            return s
        p = s.split('.', 1)
        key = p[0].lower().strip()
        if key in dct:
            return dct.get(key) + '.' + p[1]           
        p = s.rsplit('.', 1)
        key = p[0].lower().strip()
        if key in dct:
            return dct.get(key) + '.' + p[1]
        #for k, v in dct.items():            
        #    if s.lower().startswith(k):
        #       s = s.replace(k, v)
        return s
        
    def set_obj(self, s, map=False):
        if map == True:            
            s = self.get_name_map(s)
 
        if not s in self.history_list:
            self.history_list.append(s)
            self.menu.add_radiobutton(label=s, value=s, variable=self.selected_item)
        self.set_entry_obj_text(s)
        self.helpbox.set_obj(s) 
            
    # call from textbox
    def find_obj(self, item=''):
        self.msg.clear_all()
        if item != '':
            objname = self.textbox.find_obj(item)
            if objname != '':
                self.set_obj(objname)
                return
            else:
                self.msg.puts(item, 'not found')
        self.textbox.find_text(item)
            
    def open_file(self, filename):
        self.textbox.open_file(filename)
            
    def read_map(self):
        dct = {}
        path = os.path.dirname(__file__) + os.sep
        with open(path + 'help_map.lst', 'r') as f:
            text = f.read()            
            for s in text.splitlines():
                if not '=' in s:
                    continue
                k, v = s.split('=')
                dct[k.strip()] = v.strip()
        self.name_map = dct
        
        
if __name__ == '__main__':            
    def test_helpbox():
        root = tk.Tk()
        root.title('HelpFrame')
        root.geometry('600x800')
        frame = HelpFrame(root)
        frame.mainloop()   
         
    test_helpbox()
    



