import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog 
from aui.Menu import PopMenu
from aui.TreeView import TreeView 
from fileio import *
import json
import re

        
#-------------------------------------------------------------------------
class FileTreeView(TreeView, PopMenu):
    def __init__(self, master, **kw):
        TreeView.__init__(self, master, **kw)
        self.data = {}
        self.dirs = []              
        self.files = []        
        self.click_select = 'double'
        style = ttk.Style()
        style.configure('Calendar.Treeview', rowheight=24)
        self.config(style='Calendar.Treeview')
        self.tag_configure('folder', font='Mono 10 bold', foreground='#557')
        self.tag_configure('file', font='Mono 10', foreground='#555')        
        
        self.currentpath = '.'    
        home_dir = os.path.expanduser("~")
        os.chdir(home_dir)
        self.text = ''
        self.data = {}
        self.pathvars = {}
        self.clicktime = 0
        self.previtem = None
        cmds = [('Open', self.on_open), ('Update', self.on_update)]
        cmds.append(('Delete', self.on_delete))
        cmds.append(('-', None))  
        cmds.append(('Rename', self.on_rename))
        cmds.append(('-', None))                
        cmds.append(('~/', self.go_home_path))
   
        self.add_popmenu(cmds)    
        self.bind('<ButtonRelease-1>', self.on_select)        
        self.bind_all('<<RenameFile>>', self.on_rename) 
       
    def add_file(self, filename):
        pass
        
    def add_dir(self, path):
        pass         
 
    def go_home_path(self, event=None):
        path = os.path.expanduser('~') 
        self.set_path(path)        
        
    def on_update(self, event=None):
        path = os.getcwd()
        if '__pycache__' in path:
            os.chdir('..')
            path = os.getcwd()
        self.set_path(path)        
     
    def on_open(self, event=None):
        item = self.focus() 
        data = self.data.get(item)
        if data == None:
            return
        path, tag = data
        self.open_file(path, tag)
        
    def on_rename(self, event=None):
        item = self.focus() 
        data = self.data.get(item)
        if data == None:
            return
        path, tag = data        
        oldname = os.path.basename(path).rsplit('.', 1)[0]
        self.msg.puts('oldname', oldname)
        if event.widget == self:
            s = 'Input the new name of (%s):' % oldname
            res = simpledialog.askstring('Rename %s' % oldname, s)
        else:
            filename, res = event.widget.getvar('<<RenameFile>>')
        path1 = path.replace(oldname, res)
        self.msg.puts('Rename', path, path1)
        self.data[item] = (path1, tag)
        self.item(item, text=os.path.basename(path1))
        os.rename(path, path1)        
        if os.path.exists(path):
           os.remove(path)       
        
    def on_delete(self, event=None):
        item = self.focus() 
        data = self.data.get(item)
        if data == None:
            return
        path, tag = data
        os.remove(path)
        self.delete(item)
                
    def set_path(self, dirpath):
        dirpath = os.path.realpath(dirpath)
        self.currenpath = dirpath
        for obj in self.get_children():
            self.delete(obj)
        self.data = {}
        self.pathvars = {}
        self.add_path('', dirpath)
        
    def add_folder(self, item, dirpath):        
        self.add_path(item, dirpath)  
        os.chdir(dirpath)
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
        
    def select_folder(self, item, path):
        #self.msg.puts('select_folder', item, path)
        dirpath = os.path.dirname(path)
        if path in self.pathvars:
           return self.pathvars.get(path)     
        if item == None:
           item = self.get_item(path)
        if item == None:
           return   
        self.add_folder(item, path)
        return item
        
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
        if tag == 'folder':            
            if doubleclick == True:
               self.set_path(path)
            else:
               self.select_folder(item, path)
            return
        if tag != 'file':
           return        
        if self.click_select == 'click' or doubleclick == True:
           self.open_file(path, tag)
           self.add_file(path)
            
    def open_file(self, path, tag):
        self.setvar('<<SelectFile>>', (path, tag))
        self.event_generate('<<SelectFile>>')
           
    def add_path(self, node, dirpath):
        #print('add_path', node, dirpath)
        if node == '':            
            item = self.insert('', 'end', text='..', tag='folder')
            p = os.path.realpath('..')
            self.data[item] = (p, 'folder')   
            self.pathvars[p] = item         
        if os.path.lexists(dirpath):
            os.chdir(dirpath)
        else:
            return
        lst = os.listdir(dirpath)        
        folders = []
        files = []   
        for s in lst:
            if s[0] == '.':
                continue
            path = os.path.realpath(s)
            if os.path.isfile(path) == True:
                files.append(s)
            elif os.path.isdir(path):
                folders.append(s)
        folders.sort()
        files.sort()                 
        for s in files:
           item = self.insert(node, 'end', text=s, tag='file')    
           self.data[item] = (os.path.realpath(s), 'file')
        for s in folders:
           item = self.insert(node, 'end', text=s, tag='folder') 
           self.data[item] = (os.path.realpath(s), 'folder')   
           #self.add_path(item, os.path.realpath(s))  
           #os.chdir(dirpath)      
             
    def active_item(self, item):
        self.selection_set([item])
        #self.item(item, open=True)
        self.focus(item)
        self.see(item)
        
    def active_file(self, filename): 
        path = os.path.dirname(filename)
        item = self.get_item(path)
        if item != None:
           self.select_folder(item, self.data.get(item)[0])           
           self.active_item(item) 
        item = self.get_item(filename)
        if item != None:
           self.active_item(item)
        return               

        

if __name__ == '__main__':   
    class Tester():
        def __init__(self, app):  
            self.app = app
            self.root = app.get_root()
            app.add_set1()                          
            app.tree.click_select = 'click'   
            app.tree.set_path('.')
            self.puts = app.msg.puts
       
            app.bind_all('<<SelectFile>>', self.on_select_file)  
            self.open_file(__file__)        
            
        def open_file(self, filename): 
            filename = os.path.realpath(filename)
            self.app.textbox.open(filename)
            self.app.event_generate("<<SetText>>")
            self.root.title(filename)

        def on_select_file(self, event=None):      
            path, tag = event.widget.getvar('<<SelectFile>>')
            if tag == 'file':
               self.open_file(path)                 
               
            
    from aui import App   
    app = App(title='Test FileTree', size=(1500,960))  
    Tester(app)
    app.mainloop()





