import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from operator import itemgetter, attrgetter
from aui import PopMenu
from aui import Text, TwoFrame
from xmltree import XmlTree       

from runfile import RunFile
from searchbox import SearchBox
import DB as db
from DB.fileio import *
        
def realpath(path):    
    if '~' in path:
        i = path.find('~')
        path = path[i:]
        path = os.path.expanduser(path)    
    path = os.path.realpath(path) 
    return path
    
class NodeObj(object):
    def __init__(self, node, data=None):
        self.node = node
        if data != None:
            self.data = data
            i, text, key = data
            self.index = i
            self.text = text
            self.key = key
            
    def get_data(self):
        return self.data
        
class Notebook(tk.Frame):
    def __init__(self, master, cnf={}, **kw):
        tk.Frame.__init__(self, master)
        self.pages = {}
        notebook = ttk.Notebook(self)
        notebook.pack(fill = 'both', expand=True)
        self.notebook = notebook       
        notebook.pack(fill='both', expand=True)
        notebook.bind('<ButtonRelease-1>', self.switch_page)   
                    
    def switch_page(self, event=None):
        dct = self.notebook.tab('current')
        label = dct['text'].strip()

    def add_page(self, label, widgetclass):
        frame = tk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)                          
        widget = widgetclass(frame)
        widget.pack(fill='both', expand=True)         
        widget.notepage = frame
        self.notebook.add(frame, text=label.center(17))  
        self.pages[label] = widget
        return widget  

#-------------------------------------------------------------------------
class TreeView(ttk.Treeview, PopMenu):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        style = ttk.Style()
        style.configure('Calendar.Treeview', rowheight=24)
        self.config(style='Calendar.Treeview')
        self.tag_configure('folder', font='Mono 10 bold', foreground='#557')
        self.tag_configure('file', font='Mono 10', foreground='#555')   
        
#---------------------------------------------------------------------------------
class ClassTree(TreeView):
    def __init__(self, master, cnf={}, **kw):
        super().__init__(master)
        self.textbox = None
        self.filename = None
        self.data = {}
        style = ttk.Style()
        style.configure('Calendar.Treeview', rowheight=23)
        self.config(style='Calendar.Treeview')
        self.tag_configure('class', font='Mono 10 bold', foreground='#557')
        self.tag_configure('def', font='Mono 10', foreground='#555')
        self.tag_configure('if', font='Mono 10', foreground='#335')
        self.tag_configure('content', font='Mono 10', foreground='#335')
        self.tag_configure('title', font='Mono 10 bold', foreground='#557')
        self.tag_configure('subtitle', font='Mono 10 bold', foreground='#335')
        cmds = [('Update', self.on_update)]
        self.add_popmenu(cmds)    
        self.bind('<ButtonRelease-1>', self.on_select)    
        self.bind('<Enter>', self.on_enter)  
        self.bind_all("<<SwitchTextBox>>", self.on_update)
        self.bind_all("<<SetText>>", self.on_update)        
        self.cmd_action = self.winfo_toplevel().cmd_action    
        self.text = ''
        self.clicktime = 0     
        self.init_pattern()        

    def on_enter(self, event=None):
        self.on_update()        
        
    def on_update(self, event=None):
        textbox = self.cmd_action('textbox')
        if textbox == None:
            root = self.winfo_toplevel()
            if hasattr(root, 'textbox'):
                textbox = root.textbox
                self.textbox = textbox
        if textbox != None:    
            text = textbox.get('1.0', 'end')  
            if self.text != text:
                self.set_text(text)        
        
    def on_select(self, event=None):
        self.unpost_menu()
        if event.time - self.clicktime < 500:
            doubleclick = True            
            self.on_update()
        else:
            doubleclick = False
        self.clicktime = event.time   
             
        item = self.focus()
        data = self.data.get(item)
        if data != None:
            if type(data) == NodeObj:
                i, name, key = data.get_data()
            else:
                i, name, key = data
            self.cmd_action('class', (i, name, key))
        
    def get_py_tree(self, text):
        objlist = ['']
        prev_indent = -1
        i = 0                
        self.data = {}     
        for line in text.splitlines():     
            i += 1          
            if line[0:2] == 'if':
                indent = 0              
                key = 'if'
                name = line
                objname = line
            else:
                m = re.search(r'\s*(?P<key>class|def)\s+(?P<name>\w+)\s*[\(\:]', line)
                if m == None:
                    continue
                key = m.group('key')
                name = m.group('name')
                objname = name + ' (%d)'%i
                indent = line.find(key)
            if indent == 0:
                obj = self.insert('', 'end', text=objname, tag=key)  
                self.data[obj] = (i, name, key)
                objlist.append(obj)
                prev_indent = indent
            elif indent > prev_indent:
                obj = self.insert(objlist[-1], 'end', text=objname, tag=key) 
                self.data[obj] = (i, name, key)
            elif indent <= prev_indent:
                objlist.pop()
                prev_indent = indent
                obj = self.insert(objlist[-1], 'end', text=objname, tag=key)  
                self.data[obj] = (i, name, key)     
                
    def get_help_tree(self, text):
        objlist = ['']
        prev_indent = -1
        prev_line = ''
        self.data = {}     
        keys = 'Class|NAME|DESCRIPTION|PACKAGE|CLASSES|FUNCTIONS|Function|Help|class'.split('|')
        for j, line in enumerate(text.splitlines()):     
            i = j + 1
            s = line.strip()
            if s == '':
                continue      
            c = line[0]    
            if s[0] == '|':
               s = s[1:].strip()       
            word = s.split(' ')
            name = word[0].strip()       
            key = 'content'
            tagtext = s + ' (%d)' % i
            indent = line.find(word[0]) // 4
            #print(indent, word[0])
            if name in keys or c.isalpha():
                indent = 0                
                key = 'title'
            elif name in ['Methods']:                    
                indent = 1
                key = 'subtitle'   
            elif prev_line.startswith('>>>'):
                #prev_line = s
                continue
            elif indent <=1 and re.match(r'[\w\_]+\(', s):
                name = s.split('(', 1)[0]                
                indent = 3      
                tagtext = s.split('(', 1)[0] + ' (%d)' %i
            elif indent <=1 and re.match(r'[\w\_]+\s*\:', s):
                name = s.split(':', 1)[0]                
                tagtext = s.split(':', 1)[0] + ' (%d)' %i
                indent = 2      
            else:                
                #prev_line = s
                continue
            if indent == 0:
                obj = self.insert('', 'end', text=tagtext, tag=key)  
                self.data[obj] = (i, name, key)
                objlist.append(obj)
                prev_indent = indent
            elif indent > prev_indent:
                obj = self.insert(objlist[-1], 'end', text=tagtext, tag=key) 
                self.data[obj] = (i, name, key)
                prev_indent = indent
            elif indent <= prev_indent:
                if len(objlist) > 1:
                   objlist.pop()
                prev_indent = indent
                obj = self.insert(objlist[-1], 'end', text=tagtext, tag=key)  
                self.data[obj] = (i, name, key)            
            prev_line = s     
               
    def add_xml_obj(self, pobj, pnode):
        for obj in pobj.children:
            tag = obj.tag
            node = self.insert(pnode, 'end', text=tag, tag=tag) 
            self.data[node] = (obj.span, obj.id, obj.tag)
            self.item(node, open=1)
            for k, v in obj.dct.items():
                node1 = self.insert(node, 'end', text='%s: %s'%(k, v), tag='content')      
            self.add_xml_obj(obj, node)
            
    def get_xml_tree(self, text):
        tree = XmlTree(text)
        obj = tree.root
        tag = obj.tag
        node = self.insert('', 'end', text=tag, tag=tag) 
        self.data[node] = (obj.span, obj.id, obj.tag)
        self.item(node, open=1)
        for k, v in obj.dct.items():
            node1 = self.insert(node, 'end', text='%s: %s'%(k, v), tag='content')          
        self.add_xml_obj(obj, node)          
              
    def rst_reader(self, text):        
        lst = []
        i0 = 0
        self.tags = []
        for m in re.finditer(self.rst_pattern, text):
            i, j = m.span()
            if i - i0 > 1:
               lst.append(dict(tag='text', text=text[i0:i], span=(i0, i)))
            dct = dict(keys=[])   
            for k, v in m.groupdict().items():
                if v != None:
                    dct[k] = v
                    dct['tag'] = k     
                    dct['keys'].append(k)
                    self.tags.append(k)            
            dct['text'] = text[i:j]
            dct['span'] = (i, j)
            lst.append(dct)
            i0 = j
        return lst
            
    def add_node(self, pnode, objlist, i, tagtext, key):
        node = self.insert(pnode, 'end', text=tagtext, tag=key)  
        obj = NodeObj(node, data=(i, tagtext, key))
        if pnode == '':
            obj.parent = obj
        else:
             obj.parent = objlist[-1]
        self.data[node] = obj
        objlist.append(obj) 
        return obj
                
    def get_rst_tree(self, text):
        objlist = [NodeObj('')]
        prev_indent = -1
        self.data = {}     
        lst = self.rst_reader(text)
        i = 0
        levels = {}
        tag_set = sorted(set(self.tags))  
        for i, tag in enumerate(tag_set):
            p = tag.split('_')
            key = p[-1]       
            if p[0] != 'z':
                levels[key] = i            
        level_max = max(levels.values())+1
        for dct in lst:            
            tag = dct.get('tag')
            tagtext = dct.get(tag).strip().split('\n')[0]
            #print(tag, tagtext)
            key = tag.split('_')[-1]
            name = tag
            indent = levels.get(key, level_max+1)             
            if indent == 0:
                self.add_node('', objlist, i, tagtext, key)                
            elif indent >= prev_indent:
                if indent > prev_indent:
                    parent = objlist[-1]
                else:
                    parent = objlist[-1].parent
                obj = self.add_node(parent.node, objlist, i, tagtext, key)
                obj.parent = parent
            elif indent < prev_indent:
                if len(objlist) > 1:
                   objlist.pop()                
                if indent < level_max:
                   parent = objlist[-1].parent
                   obj = self.add_node(parent.node, objlist, i, tagtext, key)
                   obj.parent = parent     
            prev_indent = indent    
            i += dct.get('text').count('\n')                          
                            
    def init_pattern(self):
        p0 = r'\.\.\s(?P<z_cmd>\w+)\:\:(?P<z_content>.*)'
        p1 = r'\#\#+(?P<a_h1>[^\#]+)\#\#+\n|\*\*+(?P<b_h2>[^\*]+)\*\*+\n|\=\=+(?P<c_h3>[^\=]+)\=\=+\n'
        p2 = r'\n(?P<e_h5>[^\n]+)\n\=\=+\n|\n(?P<f_h6>[^\n]+)\n\~\~+\n'
        p3 = r'\n(?P<d_h4>[^\n]+)\n\*\*+\n|\n(?P<g_h7>[^\n]+)\n\-\-+\n'
        p4 = r'\n(?P<h_minus>\s*\-\s*\w[^(\n\n)]+)|(?<=\:)(?P<z_colon>\:\n\n)'       
        p = r'(%s)|(%s)|(%s)|(%s)|(%s)' % (p0, p1, p2, p3, p4)
        self.rst_pattern = re.compile(p)
        
    def set_text(self, text, filename=None):
        if text == self.text:
            return
        self.text = text
        tree = self
        for obj in self.get_children():
            self.delete(obj)
        text = text.strip()
        if text == '':
            return        
        if filename == None:
            filename = self.filename
        else:
            self.filename = filename
        if filename == None:
            ext = '.py'
        else:
            ext = os.path.splitext(filename)[1]
        if ext == '.py':
            self.get_py_tree(text) 
        elif ext == '.rst':
            self.get_rst_tree(text)
        elif ext == '.txt':
            self.get_help_tree(text)    
        elif ext in ['.xml', '.svg'] or text[0] == '<':
            self.get_xml_tree(text)
        else:
            self.get_py_tree(text)   
        for obj in self.get_children():
            self.item(obj, open=1)
        return     
             
        
#-------------------------------------------------------------------------
class FileTreeView(TreeView):
    def __init__(self, master, cmd_action=None, cnf={}, **kw):
        super().__init__(master)
        self.data = {}
        self.dirs = []              
        self.files = []        
        self.click_select = 'double'
        style = ttk.Style()
        style.configure('Calendar.Treeview', rowheight=24)
        self.config(style='Calendar.Treeview')
        self.tag_configure('folder', font='Mono 10 bold', foreground='#557')
        self.tag_configure('file', font='Mono 10', foreground='#555')        
        self.cmd_action = self.winfo_toplevel().cmd_action   
        self.currentpath = '.'    
        home_dir = os.path.expanduser("~")
        os.chdir(home_dir)
        self.text = ''
        self.data = {}
        self.pathvars = {}
        self.clicktime = 0
        self.previtem = None
        cmds = [('Update', self.on_update)]
        cmds.append(('-', None))        
        cmds.append(('/link', self.go_link_path))
        cmds.append(('~/', self.go_home_path))
        cmds.append(('-', None))
        cmds.append(('~/src/', self.go_src_path))
        cmds.append(('~/tmp/', self.go_tmp_path))
        cmds.append(('~/test', self.go_test_path))        
        
        self.add_popmenu(cmds)    
        self.bind('<ButtonRelease-1>', self.on_select)         

    def on_create_project(self, event=None):           
        item = self.focus() 
        data = self.data.get(item)
        if data == None or self.cmd_action == None:
            return
        path, tag = data
        self.create_project(path)
        
    def create_project(self, path):
        dct = {}
        for root, dirs, files, rootfd in os.fwalk(path):
            dir = root.replace(path, '')
            for fn in files:
                if fn.endswith('.py'):
                    if not dir in dct:
                        dct[dir] = []
                    dct[dir].append(fn)
                    
        fwrite(path + os.sep + 'project.prj', str(dct))
        
    def add_file(self, filename):
        pass
        
    def add_dir(self, path):
        pass         
       
    def go_link_path(self, event=None):
        path = '/link'
        self.set_path(path)   
        
    def go_src_path(self, event=None):
        path = realpath('~/src')
        self.set_path(path)
 
    def go_home_path(self, event=None):
        path = realpath('~') 
        self.set_path(path)
        
    def go_tmp_path(self, event=None):
        path = realpath('~/tmp') 
        path = os.path.expanduser('~') + os.sep + 'tmp'
        self.set_path(path)
 
    def go_test_path(self, event=None):
        path = realpath('~/test') 
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
        if data == None or self.cmd_action == None:
            return
        path, tag = data
        self.cmd_action('path', (path, tag))
        
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
        if self.cmd_action == None or tag != 'file':
           return        
        if self.click_select == 'click' or doubleclick == True:
           self.cmd_action('path', (path, tag))
           self.add_file(path)
            
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
        

class History(FileTreeView):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)  
        appname = master.tk.getvar('appname')
        if appname == None:
            appname = 'test_tree'
        self.key_name = appname + '.history'   
        history = {} 
        res = db.get_cache(self.key_name)
        if len(res) > 0 and '{' in res:
            history = eval(res)

        dirs = history.get('dirs', ['/link', '/link/src'] )              
        files = history.get('files', [])
        self.history_item = ''
        self.bind('<FocusIn>', self.on_focus_in)
        self.bind('<FocusOut>', self.on_focus_out)  
        for p in dirs:
            self.add_dir(p)
        
    def on_focus_in(self, event=None):
        pass        
        
    def on_focus_out(self, event=None):
        self.cache_data()
        
    def cache_data(self):
        text = str({'dirs': self.dirs, 'files':self.files})
        text = text.replace(',', ',\n')
        #print('del history', text)
        db.set_cache(self.key_name, text)
        
    def add_file(self, filename):
        if filename in self.files:
            return        
        fn = os.path.realpath(filename)
        fdir = fn.rsplit(os.sep, 1)[0]
        self.add_dir(fdir)           
             
        fname = fn.rsplit(os.sep, 1)[1]
        item = self.insert(self.history_item, 'end', text=fname, tag='file') 
        self.data[item] = (fn, 'file') 
        self.files.append(filename)
        
    def add_dir(self, path):
        if not path in self.dirs:
            self.dirs.insert(0, path)
            self.set_path(path)
        
    def set_path(self, dirpath):
        dirpath = os.path.realpath(dirpath)
        self.currenpath = dirpath
        for obj in self.get_children():
            self.delete(obj)
        self.data = {}
        self.pathvars = {}
        
        for s in self.dirs:            
            s1 = s.split(os.sep)[-1]
            item = self.insert('', 'end', text=s1, tag='folder') 
            self.data[item] = (os.path.realpath(s), 'folder')                 
        self.history_item = self.insert('', 'end', text='[History]', tag='')
        self.item(self.history_item, open=True)
        for s in self.files:        
            fn = os.path.realpath(s)     
            p = fn.rsplit(os.sep, 1)
            item = self.insert(self.history_item, 'end', text=p[1], tag='file') 
            self.data[item] = (fn, 'file') 


class FilesNotebook(Notebook):
    def __init__(self, master, cnf={}, **kw):
        super().__init__(master)
        self.filetree = self.add_page('File', FileTreeView) 
        self.history = self.add_page('History', History)    
        self.set_path('/link')                
    
    def set_path(self, path):
        self.filetree.set_path(path)            
 
                
class SideFrame(tk.Frame):
    def __init__(self, master, cnf={}, **kw):
        tk.Frame.__init__(self, master)
        
        frame = TwoFrame(self, sep=0.5, type='v')
        frame.pack(fill='both', expand=True)
        self.classtree = ClassTree(frame.top)
        self.classtree.pack(fill='both', expand=True)
                   
        self.notebook = FilesNotebook(frame.bottom)
        self.notebook.pack(fill='both', expand=True)
        self.pages = self.notebook.pages
        self.pages['Class'] = self.classtree
            

class SideNotebook(Notebook):
    def __init__(self, master, cnf={}, **kw):
        Notebook.__init__(self, master)        
        root = master.winfo_toplevel()    
        self.app = root.app  
        self.textbox = None
        self.page1 = self.add_page('Class+File', SideFrame)  
        self.pages['Search'] = self.add_page('SearchBox', SearchBox)    
        for k, v in self.page1.pages.items():
            self.pages[k] = v
        self.filetree = self.pages['File']
        self.classtree = self.pages['Class']     
              
    
    def get_textbox(self):
        self.textbox = self.app.textbox
    
    def set_text(self, text):
        self.classtree.set_text(text) 
        
    def set_msg(self, msg):
        self.msg = msg
        self.puts = msg.puts
        
    def set_path(self, path):
        self.filetree.set_path(path)
        
    def open_file(self, filename): 
        self.get_textbox()
        filename = os.path.realpath(filename)
        self.textbox.open(filename)
        self.classtree.event_generate("<<SetText>>") 
        self.classtree.on_update() 

    def on_select_file(self, path, tag):      
        if tag == 'file':
            self.open_file(path)      
        
    def on_command(self, cmd, data=None, flag=None):
        self.get_textbox()
        if cmd == 'textbox':
            return self.textbox
        if cmd == 'path':
            self.on_select_file(data[0], data[1])
        elif cmd == 'class':
            self.textbox.tag_remove('sel', '1.0', 'end')                
            i, name, tag = data
            pos = self.textbox.index('%d.0' % i)
            self.textbox.see(pos)                  

            start = self.textbox.search(name, pos)
            
            end = start + '+%dc' % len(name)           
            self.textbox.tag_add('sel', start, end)
                

if __name__ == '__main__':   
    from aui import aFrame, App 
    from texteditor import TextEditor
    class TestFrame(aFrame):
        def __init__(self, master, **kw):       
            super().__init__(master, **kw)
            root = master.winfo_toplevel()
            root.app = self
            root.cmd_action = self.on_command
            frame = self.twoframe(self, style='h', sep=0.3)     
            text, msg = self.add_textmsg(frame.right, TextEditor)   

            mainframe = SideNotebook(frame.left)
            mainframe.pack(fill='both', expand=True)
            mainframe.msg = msg
            self.mainframe = mainframe
            mainframe.open_file(__file__)                      

        def on_command(self, cmd, data=None, flag=None):
            self.mainframe.on_command(cmd, data, flag)
                
    app = App(title='Test Tree', size=(1100, 800), Frame=TestFrame)           
    app.mainloop()



