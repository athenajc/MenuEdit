import os
import re
import sys
import tkinter as tk
from tkinter import ttk
import re
from fileio import *

        
class ttkTree(ttk.Treeview):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.entryframe = None
        style = ttk.Style()
        style.configure('Calendar.Treeview', rowheight=24)
        self.config(style='Calendar.Treeview')
        self.tag_configure('folder', font='Mono 10 bold', foreground='#557')
        self.tag_configure('node', font='Mono 10', foreground='#555')    
        self.pack(fill='both', expand=True)
        self.bind('<ButtonPress-1>', self.on_click)           
    
    def enable_edit(self):
        self.bind('<Double-1>', self.on_edit_cell)   

    def on_click(self, event=None):
        if self.entryframe != None:
            self.entryframe.destroy()
            self.entryframe = None
            
    def remove_item(self, item):
        self.delete(item)
        
    def get_text(self, item, column=0):
        if item == 'focus':
            item = self.focus()
            if item == None or len(item) == 0:
                return ''
        dct = self.item(item)   
        n = column
        if type(column) == str and '#' in column:
            n = self.getint(column[1:]) 
        if n == 0:
            return str(dct.get('text'))
        n -= 1    
        data = dct.get('values')
        if n < len(data):
            return str(data[n])
        else:
            return ''
            
    def clear(self):
        for obj in self.get_children():
            self.delete(obj)
        
    def on_reset(self, event=None):
        self.clear()
        
    def on_edit_cell(self, event=None):
        item = self.identify_row(event.y)
        column = self.identify_column(event.x)       
        #print(item, column, self.item(item))
        box = self.bbox(item, column)       
        if len(box) == 0:
            return 
        x, y, w, h = box
        text = self.get_text(item, column)
        self.entryframe = frame = tk.Frame(self)
        if column == '#0':
            x += 16
        self.entryframe.place(x=x, y=y)        
        
        entry = tk.Entry(frame, width=10 + max(len(text), 5) )        
        entry.insert(0, text)
        entry.pack(side='left')
        entry.focus()
    
        def saveedit():
            self.set_node_data(item, entry.get())
            self.entryframe.destroy()
            self.entryframe = None
            
        def cancel():
            self.entryframe.destroy()
            self.entryframe = None
    
        button1 = ttk.Button(frame, text='OK',  command=saveedit)
        button1.pack(side='left')
        button2 = ttk.Button(frame, text='Cancel', command=cancel)
        button2.pack(side='left')
        
#-------------------------------------------------------------------------
class Listbox(ttkTree):        
    def set_header(self, header=['name', 'data']):
        for i, s in enumerate(header):
            self.heading('#' + str(i+1), text=s)
             
    def add_row(self, p):
        item = self.insert('', 'end', text=p[0])   
        for i in range(len(p)):
            s = p[i]
            if len(s) > 100:
                s = s[0:100]
            self.set(item, '#' + str(i+1), value=s)
        
    def add_list(self, lst):
        for p in lst:
            self.add_row(p)            
        
    def set_list(self, lst):
        self.clear()
        self.add_list(lst)
            
#-------------------------------------------------------------------------
class TreeView(ttkTree):
    def bind_click(self, action):
        self.click_select = 'click'   
        self.bind('<ButtonRelease-1>', action)    
 
    def get_focus_item_and_key(self):
        item = self.focus() 
        dct = self.item(item)
        key = dct.get('text')  
        return (item, key)
        
    def set_node_data(self, item, data):
        self.item(item, text=data) 
              
    def add_data_node(self, pnode, obj):
        key = str(obj)
        node = self.insert(pnode, 'end', text=key, tag='content') 
        self.item(node, open=1)
        return node
            
    def add_namelist(self, pnode, lst):
        for name in lst:            
            node = self.insert(pnode, 'end', text=name, tag='name') 
            
    def set_list(self, lst):
        self.clear()
        self.add_namelist('', lst)
        
    def add_list(self, pnode, lst):
        for p in lst:  
            self.add_node(pnode, p)  
            
    def add_node(self, pnode, obj):
        tp = type(obj)
        if tp in (list, tuple):
            self.add_list(pnode, obj)
        elif tp is dict:
            self.add_dct(pnode, obj)    
        else:
            self.add_data_node(pnode, obj)
            
    def add_dct(self, pnode, dct={}):
        for key, values in dct.items():
            node = self.insert(pnode, 'end', text=key, tag='dct') 
            self.item(node, open=1)
            self.add_node(node, values)  

    def new_node(self, event=None):
        items = self.selection()
        print(items)
        if items == ():
           self.add_data_node('', 'NewItem')
        else:
           self.add_data_node(items[0], 'NewItem')
           
    def get_dict(self, node=''):
        dct = {}
        for item in self.get_children(node):
            name = self.get_text(item)
            dct[name] = self.get_dict(item)
            
        return dct    
            
    def on_save(self, event=None):
        dct = self.get_dict()
        print(dct)
        self.add_dct('', dct)            

def lstview(lst=None):
    from aui import App
    app = App('A Listbox', size=(500, 800))   
    tree = Listbox(app, column=("name", "data", "note"), show='headings', height=5)    
    if lst == None:
       lst = ((1, 2), ('ab', 'cde'), (5, 6, 8))
    tree.set_header()
    tree.add_list(lst)
    app.mainloop() 
 
    
def dctview(dct=None):
    from aui import App
    app = App('TreeView Editor', size=(500, 800))   
    frame = app.add_test_msg(app)
    layout = frame.get('layout')
    panel = frame.get('panel', height=1)
    layout.add_top(panel, 50)
    tree = frame.add('tree')
    layout.add_box(tree)
    if dct == None:
        dct = {'a':123, 'b':['ab', 'cd', 'ef', {1:'test', 2:'pratice', 3:'operation'}]}
    
          
    buttons = [('Reset', tree.clear), 
               ('New', lambda event=None: tree.add_dct('', dct)),  
               ('Add', tree.new_node),  
               ('Save', tree.on_save),  
               ]
  
    panel.add_buttons(buttons)
    tree.enable_edit()
    tree.pack()
    tree.add_dct('', dct)
    app.mainloop() 

    
if __name__ == '__main__':  
     dctview()
    


