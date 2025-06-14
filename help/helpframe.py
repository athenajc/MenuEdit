import os
import sys
import re
import tkinter as tk
from tkinter import ttk
import webbrowser
import pathlib

from aui.aui_ui import TwoFrame
from aui.Menu import PopMenu
from aui.TextObj import TextObj
from aui.Messagebox import Messagebox   
from msgbox import HelpMsgBox  
from help_config import default_modules, name_map_list
from autocombo import AutoCombo 
from get_modules import *
from helpbox import HelpBox
from DB.ModuleDB import *        


class Toolbar():
    def init_toolbar(self, frame):
        frame1 = tk.Frame(frame)
        frame1.pack(side='top', fill='x', expand=False, padx=10)

        self.menu = self.create_menu_button(frame1)
        button_back = tk.Button(frame1, text='<', relief='flat')
        button_back.pack(side='left')     
        self.obj_combo = self.add_obj_combo(frame1)    
    
        self.find_combo = self.add_find_combo(frame1)
        button_find = tk.Button(frame1, text='Find', relief='flat')
        button_find.pack(side='left')
        button_find.bind('<ButtonRelease-1>', self.on_button_find)
        button_back.bind('<ButtonRelease-1>', self.on_button_back)  

    def add_obj_combo(self, frame):
        combo = AutoCombo(frame, auto=True, values=self.module_list)
        combo.pack(side='left', fill='x', expand=True)        
        combo.bind('<Return>', self.on_select_obj_combo) 
        combo.bind("<<ComboboxSelected>>", self.on_select_obj_combo)
        return combo
        
    def add_find_combo(self, frame):
        combo = AutoCombo(frame, values=get_lst('default_modules'))
        combo.pack(side='left', fill='x', expand=False, padx=3) 
        combo.bind("<Return>", self.on_button_find)
        combo.bind("<<ComboboxSelected>>", self.on_button_find)
        return combo

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


    
class HelpFrame(tk.Frame, PopMenu, Toolbar):
    def __init__(self, master, msgbox=None, **kw):
        tk.Frame.__init__(self, master)
        self.mdb = ModuleDB()
        text = self.mdb.getvar('module.namemap')
        self.name_map = eval(text)
        self.objname = '-'     
        self.module = ''        
        self.module_list = get_lst('modules')
        self.init_toolbar(self)
        self.helpbox = self.add_helpbox(self)    
        self.puts = self.helpbox.puts    
        
        self.set_obj('')
        self.bind_all("<<ObjChanged>>", self.on_obj_changed)
        self.bind_all('<<FindObjHelp>>', self.on_find_obj)
        self.pack(fill='both', expand=True)

    def add_helpbox(self, frame):
        frame1 = TwoFrame(frame, sep=0.75, type='v')
        frame1.pack(fill='both', expand=True)
        msgbox = HelpMsgBox(frame1.bottom)   
        msgbox.pack(fill='both', expand=True)           
        box = HelpBox(frame1.top, wrap=None)
        box.pack(side='left',fill='both', expand=True)
        box.msg = msgbox
        box.parent = self
        self.msg = msgbox        
        msgbox.textbox = box
        return box
          
    def get_objname(self, word):
        if self.objname != '':
            if word.find(self.objname + '.') == 0:
                return word
            objname = self.objname + '.' + word
        else:
            objname = word 
        return objname

    def on_obj_combo_keyup(self, event=None):
        if event.keysym == 'Return':            
            self.on_select_obj_combo(event)  
            
    def on_select_obj_combo(self, event=None):
        word = event.widget.get()
        if word in self.name_map:
            word = self.name_map.get(word)
        if self.module != '':
            word = self.module + '.' + word
            
        self.set_obj(word, flag='obj')            

    def on_button_find(self, event=None):
        word = self.find_combo.get()
        if word == '':
            return
        if not word in self.find_combo['values']:
            self.on_find_text()   
            return
        
        objname = self.get_objname(word)
        obj = get_obj(objname)
        if inspect.ismodule(obj) or inspect.isclass(obj):            
            self.set_obj(objname)
            return     
        pos = self.helpbox.pos_dct.get(word, None)
        if pos == None:
            pos = self.helpbox.search(word, '1.0')
        if pos != None and pos != '':
            self.helpbox.goto_pos(pos + 'linestart', pos + ' lineend')            
            
    def on_obj_changed(self, event=None):
        objname = self.helpbox.objname
        self.obj_combo.set_text(objname)
        if objname == '':
            lst = get_lst('default_modules')
            self.find_combo['values'] = lst 
            return
        obj = self.helpbox.get_obj(objname) 

        if objname == '': 
            pass
        elif obj.objtype == 'module': 
            lst = obj.get_members('all')  
        elif obj.objtype == 'class':    
            lst = list(self.helpbox.pos_dct.keys())
            lst += obj.get_members('all')
        else:
            lst = list(self.helpbox.pos_dct.keys())
        self.find_combo['values'] = lst            
        self.add_history(objname)
        self.objname = objname          
       
    def menu_item_selected(self, *args):
        item = self.selected_item.get()
        self.set_obj_combo_text(item)
        self.set_obj(item)       
                
    def on_button_back(self, event):
        s = self.obj_combo.get().strip()
        if not '.' in s:
            self.set_obj('')
            self.obj_combo.set_text('') 
        else:
            p = s.split('.')
            s = '.'.join(p[0:-1])
            self.set_obj(s)     
            self.obj_combo.set_text(s)   
        self.helpbox.goto_pos('1.0', '1.0')
        
    def on_find_text(self, event=None):
        self.msg.clear_all()
        s = self.find_combo.get().strip()
        if s != '':
            self.helpbox.find_text(s)
        
    def set_obj_combo_text(self, s):
        if self.obj_combo.get() == s:
            return
        self.obj_combo.delete(0, 'end')
        self.obj_combo.insert('insert', s)              
        
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
        return s
        
    def get_sourcefile(self):
        obj = get_obj(self.helpbox.objname)
        file = inspect.getsourcefile(obj)
        return file
        
    def add_history(self, name):
        if not name in self.history_list:
            self.history_list.append(name)
            self.menu.add_radiobutton(label=name, value=name, variable=self.selected_item)    

    def cmd_arg(self, word):
        cmd, arg = word.split(' ', 1)
        cmds = ['dir', 'doc', 'src', 'list', 'func', 'class', 'db', 'help']
        if cmd in cmds:            
            self.helpbox.obj_cmd(cmd, arg)  
            return True  
        elif arg in cmds:   
            self.helpbox.obj_cmd(arg, cmd)    
            return True
        self.puts('404: Not Found', word)    
        return False     
            
    def set_obj(self, name, flag='obj', map=False):
        if self.objname == name:
            return            
        self.helpbox.clear_all()
        if '*' in name:
            self.find_obj(name)
            return
        if ' ' in name:    
            self.cmd_arg(name)
            return
                        
        if map == True:            
            name = self.get_name_map(name)
        self.add_history(name)
        self.objname = name  
        self.obj_combo.set_text(name)
  
        if self.helpbox.objname != name:
           self.helpbox.set_obj(name)    
            
    # call from textbox
    def find_obj(self, item=''):
        self.msg.clear_all()
        if item == '':
            self.msg.puts('key is empty')
            return   
        self.msg.puts('Find key', item)    
        res = self.mdb.search(item.replace('*', '') )
        #self.msg.puts('res', res)
        if res == []:
            self.helpbox.set_obj(item)
            return
        self.helpbox.show_lst(item, res)
        self.obj_combo['values'] = res

    def on_find_obj(self, event=None):        
        key = event.widget.getvar('<<FindObjKey>>')
        #print(key, '<<FindObjKey>>')
        self.find_obj(key)
            
    def open_file(self, filename):
        self.helpbox.open_file(filename)
        

        
if __name__ == '__main__':            
    def test_helpbox():
        root = tk.Tk()
        root.title('HelpFrame')
        root.geometry('600x800')
        frame = HelpFrame(root)
        frame.set_obj('pydoc list')
        frame.pack(fill='both', expand=True)
        frame.mainloop()   
    from DB.fileio import *
    add_sys_path([realpath('..')])

    #from mainframe import main
    #main()     
    test_helpbox()
    



