import os
import sys
import re
import tkinter
import tkinter as tk
from tkinter import ttk
import importlib
import webbrowser
import pydoc
import pathlib
import zlib
from aui.aui_ui import TwoFrame
from aui import PopMenu, TextObj   
from tk_html_widgets import HTMLLabel, HTMLText, HTMLScrolledText
from autocombo import AutoCombo 
from DB.ModuleDB import *    
from pprint import pprint, pformat

mdb = ModuleDB()  
htmldoc = pydoc.HTMLDoc()

class HelpObj(ModuleObj):
    def __init__(self, name):
        ModuleObj.__init__(self, name)
        self.doc = None
        if self.load_db() == False:
            self.module = self.get_module()
            self.members = self.get_members('dct')             
            self.objtype = str(self.obj).split(' ', 1)[0][1:]
            #self.save_to_db()
        if self.members == {}:
           self.members = self.get_members('dct')     
            
    def save_to_db(self):
        print('Save to DB', self.name)
        db = mdb.get_db()         
        keytypes = {'name':'string', 'module':'string', 'type':'string', 'members':'string', 'data':'string'} 
        lst = []
        data = (self.name, self.module, self.objtype, str(self.members), '')
        lst.append(data)      
        db.from_list('modules', keytypes, lst)

    def load_db(self):       
        #print('Load from DB', self.name)       
        res = mdb.fetch('Select * from modules where name = \"%s\"' % self.name)
        if res == None or res == []:
            return False
        data = res[0]
        name, module, objtype, members, data1 = data
        self.module = module
        self.members = eval(members)
        self.objtype = objtype               
        return True
        
    def load_doc_db(self):                 
        res = mdb.fetch('Select data from doc where name = \"%s\"' % self.name)
        if res == None or res == []:
            return False      
        data = res[0][0]
        text = zlib.decompress(data).decode()
        self.doc = text   
        return True     
    
    def get_list(self):
        return list(dir(self.obj))        
        
    def get_html(self, title=' %s:'):
        try:
            obj = self.obj       

            text = pydoc.render_doc(obj, title=title, renderer=htmldoc)            
            if text == None and obj != None:
                text = self.get_attr('__doc__') 
            self.doc = text    
            return self.doc
        except:
            print(self.name, 'no help doc')  
            
    def render_doc(self, title=' %s:'):
        if self.doc != None:
            return self.doc
        if self.load_doc_db():
            return self.doc       
        try:
            obj = self.obj       
            text = pydoc.render_doc(obj, title=title)            
            if text == None and obj != None:
                text = self.get_attr('__doc__') 
            self.doc = text    
            return self.doc
        except Exception as e:
            print(self.name, 'no help doc')  
            print(e)

class HelpDoc():
    objs = {}
    def get_obj(self, name):        
        if name in self.objs:
            return self.objs[name]
        obj = HelpObj(name)
        self.objs[name] = obj
        return obj        
        
    def get_help(self, objname): 
        if '*' in objname:
            return None
        obj = self.get_obj(objname)        
        text = obj.render_doc(title='\nPython Library Documentation: \n    %s') 
        if text == None:
            lst = self.mdb.search(objname)
            text = '\n'.join(lst)    
        return text   
            
class HelpBox(TextObj, PopMenu, HelpDoc):
    def __init__(self, master, **kw):
        super().__init__(master, **kw) 
        self.config(width=50)
        self.winfo_toplevel().helpbox = self
        self.limit = 32768*2
        self.width = 1000
        
        self.mdb = ModuleDB()        
        text = self.mdb.getvar('module.namemap')
        self.name_map = eval(text)
        default_modules = eval(self.mdb.getvar('module.default'))
        self.default_list = default_modules
        self.module_list = self.mdb.get_modules()        
        self.sys_module_list = list(sys.modules.keys())        
        self.config(wrap='none')
        self.init_config()
        self.init_popmenu()
        self.click_time = 0  
        self.objname = None
        self.obj = None
        self.pos_dct = {}   
 
        self.bind('<KeyRelease>', self.on_keyup)        
        self.objname = '-'
        self.module = ''
        self.docmode = ''        
                       
    def on_keyup(self, event):
        key = event.keysym
        state = event.state
        if state == 0x14 and  key == 'f':
            self.find_text()
        elif key == 'F1':
            self.on_open_module()   
        
    def init_config(self):
        self.config(foreground='#555')
        self.tag_config('find', font='Mono 10 bold', foreground='#555')
        self.tag_config('sel', font='Mono 10 bold', foreground='#000', background='#aaa')
        self.tag_config('title', font='Mono 11 bold', foreground='#333') 
        self.tag_config('bold', font='Mono 10 bold', foreground='#333', background='#ddd')
        self.tag_config('function', font='Mono 10', foreground='#000')      
        self.tag_config('helpon', font='Mono 10 bold', foreground='#000', background='#ddd')   
        self.tag_config('colon', font='Mono 10 bold', foreground='#555')
        self.tag_config('black', font='Mono 10', foreground='#000')
        self.tag_config('word', font='Mono 10', foreground='#222')
        self.tag_config('gray', font='Mono 10', foreground='#333')
        
    def init_popmenu(self):
        cmds = []
        cmds.append(('Goto', self.on_goto))   
        cmds.append(('-'))         
        cmds.append(('Search Obj', self.on_search_obj))
        cmds.append(('-')) 
        cmds.append(('Find in Text', self.on_find_text)) 
        cmds.append(('-')) 
        cmds.append(('Google Search', self.on_google_search))
        cmds.append(('Open Source', self.on_open_source))
        cmds.append(('-')) 
        cmds.append(('Clear', self.clear_all))     
        cmds.append(('-'))
        cmds.append(('Select All', self.on_select_all))    
        cmds.append(('Copy', self.on_copy))              
        self.add_popmenu(cmds)    
        
    def select_obj(self, name):
        self.setvar('SetHelpObj', name)
        self.event_generate('<<SetHelpObj>>') 

    def on_show_doc(self, event=None):    
        if self.docmode == 'show':  
            return
        self.puts('-'*60 + '\n')
        text = self.get_help(self.module)
        index = self.index('end')
        p = self.docbutton.range #self.tag_ranges('button')

        if p != ():
           self.delete(p[0] + '-1l', p[1])
           self.update()
        
        self.puts(text)
        self.tag_update() 
        
        self.goto_pos(p[0], p[1])       
        self.docmode = 'show'            

    def on_open_source(self, event=None):      
        self.event_generate("<<OpenSource>>")
        
    def goto_pos(self, p, end=None):
        self.select_none()
        self.see(p)        
        if end != None:
            self.tag_add('sel', p, end)
        else:
            self.tag_add('sel', p + ' linestart', p + ' lineend +1c') 

    def get_select_obj_word(self):
        text = self.get_text('sel')
        if text == '' or ' ' in text:
            text = self.get_word('insert')
        return text    
            
    def on_goto(self, event=None):
        text = self.get_text('sel')
        if text == '' or ' ' in text:
            text = self.get_word('insert') 
        print(text, self.objname, self.module)           
        
        if self.objname != '':
            if text.find(self.objname + '.') == 0:
                pass
            else:
                text = self.objname + '.' + text
        self.set_obj(text)            
            
    def find_text(self, key):
        text = self.get_text()
        self.find_in_text('', text, key)
        
    def on_find_text(self, event=None):        
        text = self.get_text('sel')
        if text == None or len(text) <= 2:
            return              
        self.msg.clear_all()
        self.msg.puts('Search ', text, ':')    
        self.find_text(text)
        self.msg.update_tag(key=text)
        
    def on_google_search(self, event=None):
        base_url = "http://www.google.com/search?q="
        text = self.get_text('sel')
        if text == None:
            return 
        head = self.objname
        if text in head:
            text = ''
        webbrowser.open(base_url + 'python ' + head + ' ' + text)                 
   
    def tag_update(self):
        text = self.get_text()
        if text == None:
            return        
 
        lst = re.findall('', text)
        start = '1.0'
        for s in lst:
            start = self.search(s, start)       
            end = start + '+2c'                 
            self.replace(start, end, '')
            self.tag_add('bold', start+'-1c', start)
        self.tag_lower('bold')    
        lst = self.tag_ranges('bold')     
        n = len(lst)   
        dct = {}
        for i in range(0, n, 2):            
            p1, p2 = lst[i], lst[i+1]
            s = self.get(p1, p2)
            if '_' in s:
                continue
            dct[s] = str(p1)            
        self.pos_dct = dct

    def find_in_module_list(self, t):
        t = t.lower()
        lst = []            
        for s in self.module_list:
            if s.lower().find(t) == 0:
                lst.append(s)
        self.put_list(lst)                    
        return lst  
                    
    def get_module_members(self, objname):
        obj = self.get_obj(objname)
        dct = obj.members
        return dct               
        
    def print_module_list(self):
        self.put_list(lst = self.default_list)
        self.put_list(self.module_list, bychar=True)
        #self.put_list(lst=self.sys_module_list, bychar=True)  
        
    def show_lst(self, key, lst):
        self.puts('Search Item:', key, '\n')
        for s in lst:
            self.puts(s)
        self.event_generate("<<ObjChanged>>")   
        
    def search_name(self, name):
        res = self.mdb.search(name)
        self.show_lst(name, res) 
          
    def on_search_obj(self, event=None):
        text = self.get_select_obj_word()
        self.clear_all()
        self.search_name(text)
        
    def show_root(self):
        self.module = ''
        self.docmode = ''
        self.print_module_list()
        self.event_generate("<<ObjChanged>>")
        
    def show_members(self, name):
        self.print_dct(self.obj.members)   
        self.puts('\n')
        
    def show_module(self, objname):
        self.module = objname        
        self.show_members(objname)        
        self.event_generate("<<ObjChanged>>")
        n = self.get_line_index('end')
        if n < 30:
            self.show_help(self.module)   
        else:
            self.docmode = 'hide'
            pos = self.index('end')
            self.docbutton = self.add_button(pos, text='Show Doc', command=self.on_show_doc)        
          
    def show_help(self, objname):
        n = self.get_line_index('end') 
        if n < 5 and self.obj != None:
            if self.obj.members != {}:
                self.print_dct(self.obj.members)   
                self.puts('\n')
            else:   
                self.puts('')
                self.put_list(self.obj.get_list())
                
        self.docmode = 'show'
        text = self.get_help(objname)        
        self.puts(text)
        self.tag_update() 
        if self.obj == None:
            self.search_name(text)
            return
        n = self.get_line_index('end')        
        if n < 30:
            doc = self.obj.get_doc()   
            if doc != '':
                self.puts(doc)
                    
    def set_obj(self, name):
        obj = self.get_obj(name)
        if self.obj == obj:
            return             
        
        self.objname = name     
        self.obj = obj  
        self.clear_all()             
        
        if name == '':            
            self.show_root()
            return      
                          
        self.puts_tag(name, 'title', end='\n')
        obj = self.obj = self.get_obj(name)
        if obj == None or obj.obj == None:
            self.puts('No such item :', name)
            self.search_name(name)   
            self.event_generate("<<ObjChanged>>")
            return
            
        module = obj.module
        self.puts(obj.module, obj.obj)
        
        if name == module:
            self.show_module(name)
            n = self.get_line_index('end')
            if n > 10:
               return
        else:
            self.module = self.obj.get_module()
       
        self.show_help(name)         
        self.event_generate("<<ObjChanged>>")
        self.goto_pos('1.0', '1.0')  
        

    def obj_cmd(self, cmd, name):
        self.clear_all()
        if name in self.name_map:
            name = self.name_map.get(name)
        self.module = name
        self.objname = name
        obj = self.obj = self.get_obj(name)
        
        self.puts_tag((cmd, name), 'title', end='\n')
        if obj == None or obj.obj == None:
            cmd = 'db'
        else:    
            self.puts(obj.obj)
        
        if cmd == 'help':
            self.show_help(name)
        elif cmd == 'dir':
            self.put_list(obj.get_list())
        elif cmd == 'db':
            self.search_name(name)   
        elif cmd == 'doc':
            doc = obj.get_doc()   
            if doc != '':
                self.puts(doc)
            else:
                self.show_help(name)    
        elif cmd == 'src': 
            self.event_generate("<<OpenSource>>")           
            self.show_help(name)            
        elif cmd == 'list':
            self.show_members(name)               
        elif cmd == 'func':
            dct = self.get_module_members(name)     
            self.put_list(dct.get('function'))
        elif cmd == 'class':
            dct = self.get_module_members(name)     
            self.put_list(dct.get('class'))
             
        self.event_generate("<<ObjChanged>>")   
        
def test_html_doc(name):
    mobj = HelpObj(name)
    print(mobj.obj)
    text = mobj.get_html()
    import webview
    webview.create_window(name, html=text)
    webview.start()
    return  

if __name__ == '__main__':       
    from helpframe import HelpFrame     
    def test_helpbox():
        root = tk.Tk()
        root.title('Help Box')
        root.geometry('600x800')
        frame = HelpFrame(root)
        frame.set_obj('ttk help')
        frame.pack(fill='both', expand=True)
        frame.mainloop()   

    #test_html_doc('json')
    test_helpbox()

    
    

