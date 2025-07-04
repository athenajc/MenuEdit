import os
import re
import sys
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from operator import itemgetter, attrgetter

fileio.add_sys_path(('.', '..'))
from autocombo import AutoCombo

from get_modules import *        
   
from xmltree import XmlTree
from aui.ClassTree import NodeObj, ClassTree
from aui import Notebook, TreeView, PopMenu, aFrame
       
import DB
from DB import ModuleDB
from DB.ModuleDB import HelpObj

mdb = ModuleDB()  

#-------------------------------------------------------------------------
class ModuleTree(TreeView, PopMenu):
    def __init__(self, master, cmd_action=None, cnf={}, **kw):
        TreeView.__init__(self, master)
        self.frame = master
        self.data = {}     
        self.click_select = 'double'
        self.init_config()      
        self.cmd_action = cmd_action
        self.currentpath = ''    
        
        self.text = ''
        self.data = {}
        self.pathvars = {}
        self.clicktime = 0
        self.previtem = None
        cmds = [('Open', self.on_open), ('Update', self.on_update)]
        #cmds.append(('-', None))
        #cmds.append(('Close all', self.on_close_all))        
        
        self.add_popmenu(cmds)    
        self.bind('<ButtonRelease-1>', self.on_select)        
        self.set_path('')         

    def set_path(self, dirpath):
        self.currenpath = dirpath
        for obj in self.get_children():
            self.delete(obj)
        self.data = {}
        self.pathvars = {}
        self.add_path('', dirpath)
                

    def init_config(self):
        style = ttk.Style()
        style.configure('Calendar.Treeview', rowheight=24)
        self.config(style='Calendar.Treeview')
        self.tag_configure('module', font='Mono 10 bold', foreground='#557')
        self.tag_configure('class', font='Mono 10', foreground='#557')
        self.tag_configure('function', font='Mono 10', foreground='#555')  
        self.horizontal_scroll = ttk.Scrollbar(
            self.frame, orient="horizontal", command=self.xview
        )
        self.vertical_scroll = ttk.Scrollbar(
            self.frame, orient="vertical", command=self.yview
        )
        self.configure(
            xscrollcommand=self.horizontal_scroll.set,
            yscrollcommand=self.vertical_scroll.set,
        )

        self.horizontal_scroll.pack(side='bottom', fill='x')
        self.vertical_scroll.pack(side='right', fill='y')


    def on_update(self, event=None):
        #self.set_path(path)
        pass
        
    def on_open(self, event=None):
        item = self.focus() 
        data = self.data.get(item)
        if data == None or self.cmd_action == None:
            return
        path, tag = data
        self.cmd_action('module', (path, tag))    
        
    def add_module(self, item, dirpath):        
        self.add_path(item, dirpath)  
        self.pathvars[dirpath] = item
        self.item(item, open=1) 
        
    def get_item(self, path):        
        node = None
        for item in self.data:
            fpath, tag = self.data.get(item)            
            if fpath in path:
               #print(item, tag, fpath)
               node = item               
        return node
        
    def select_module(self, item, path):
        #self.msg.puts('select_module', item, path)
        dirpath = os.path.dirname(path)
        if path in self.pathvars:
           return self.pathvars.get(path)     
        if item == None:
           item = self.get_item(path)
        if item == None:
           return   
        self.add_module(item, path)
        return item
         
    def get_data(self):
        item = self.focus() 
        data = self.data.get(item)
        return data
        
    def on_select(self, event=None):        
        self.unpost_menu()
        item = self.focus()           
        if self.previtem == item and event.time - self.clicktime < 500:
            doubleclick = True            
            #self.msg.puts('on_select', item, self.item(item, option='text'))
        else:
            doubleclick = False
        self.previtem = item
        self.clicktime = event.time
        data = self.data.get(item)
        
        if data == None:
            return
        path, tag = data 
        
        if tag == 'module':            
            if doubleclick == True:
               self.set_path(path)
               return
        if tag == 'module':  
            self.select_module(item, path)
            self.event_generate("<<ModuleSelected>>")
            return            
        elif tag == 'class':
            self.select_module(item, path)
            self.event_generate("<<ClassSelected>>")
        else:
            print(data)
            print('event_generate<<FunctionSelected>>')
            self.event_generate("<<FunctionSelected>>")
            
        if self.cmd_action == None:
           return        
        if self.click_select == 'click' or doubleclick == True:
           self.cmd_action('module', (path, tag))
           #self.add_file(path)
                         
    def active_item(self, item):
        self.selection_set([item])
        #self.item(item, open=True)
        self.focus(item)
        self.see(item)
        
    def active_file(self, filename): 
        path = os.path.dirname(filename)
        item = self.get_item(path)
        if item != None:
           self.select_module(item, self.data.get(item)[0])           
           self.active_item(item) 
        item = self.get_item(filename)
        if item != None:
           self.active_item(item)
        return               
 
    def add_path(self, node, dirpath):
        #print('add_path', node, dirpath)
        if node == '': 
            lst = eval(DB.get_cache('modules.default'))
            dct = {'module':lst}   
        else:
            dct = get_module_members(dirpath)    
        if dirpath == '':                 
            head = ''
        else:
            head = dirpath + '.'     
        for key in dct:
            for s in dct[key]:
                item = self.insert(node, 'end', text=s, tag=key) 
                self.data[item] = (head + s, key)       

                
class ModuleFrame(aFrame):
    def __init__(self, master,  cmd_action=None, cnf={}, **kw):
        super().__init__(master)        
        layout = self.get('layout')
        self.moduletree = mtree = ModuleTree(self, cmd_action=cmd_action)        
        self.classtree = classtree = ClassTree(self)
        layout.add_V2(mtree, classtree, sep=0.6)        
        classtree.bind_act(cmd_action)
        



if __name__ == '__main__':   
    from aui import App, aFrame

    class TestFrame(aFrame):
        def __init__(self, app):       
            super().__init__(app)
            self.app = app
            self.root = app.root
            self.textbox = text = self.get('text')
            self.msg = msg = self.get('msg')
            layout = self.get('layout')                                    
            treeframe = ModuleFrame(self, cmd_action=self.on_command)
            layout.add_HV(treeframe, text, msg, sep=(0.3, 0.7))
            text.msg = msg
            treeframe.msg = msg         
            msg.textbox = text           
            
            self.moduletree = treeframe.moduletree
            self.classtree = treeframe.classtree

            self.moduletree.bind("<<ModuleSelected>>", self.on_module_selected)
            self.moduletree.bind("<<ClassSelected>>", self.on_class_selected)
            self.moduletree.bind("<<FunctionSelected>>", self.on_function_selected)
            
        def on_module_selected(self, event=None):
            pass
            
        def on_class_selected(self, event=None):
            name, tag = self.moduletree.get_data()
            self.on_select_path(name, tag)
            
        def on_function_selected(self, event=None):
            name, tag = self.moduletree.get_data()
            print('on_function_selected', name, tag, '\n')
            self.on_select_path(name, tag)
            
        def puts(self, *lst, end='\n'):
            for text in lst:
                self.msg.puts(str(text) + ' ')
            
        def fread(self, filename):
            with open(filename, 'r') as f:
                text = f.read()
                f.close()
                return text
                
        def set_path(self, path):
            pass
            
        def set_text(self, text):
            textbox = self.textbox
            textbox.delete('1.0', 'end')
            textbox.insert('1.0', text)
            textbox.tag_block()

        def on_select_path(self, name, tag):      
            text = get_help(name)
            self.set_text(text)

        def on_command(self, cmd, data=None, flag=None):
            if cmd == 'textbox':
                return self.textbox
            if cmd == 'path':
                self.on_select_path(data[0], data[1])
            elif cmd == 'class':
                self.textbox.tag_remove('sel', '1.0', 'end')                
                i, name, tag = data
                pos = self.textbox.index('%d.0' % i)
                self.textbox.see(pos)                  

                start = self.textbox.search(name, pos)
                
                end = start + '+%dc' % len(name)           
                self.textbox.tag_add('sel', start, end)
                
               
    app = App(title='Modules TreeView', size=(1200, 900))
    frame = TestFrame(app)
    frame.pack(fill='both', expand=True)
    #sys.stdout = frame.msg
    app.mainloop()   
    


