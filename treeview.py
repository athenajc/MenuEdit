import os
import re
import sys
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from operator import itemgetter, attrgetter
from ui import PopMenu
from ui import TagTextObj, TwoFrame
from xmltree import XmlTree       
import fileio
from runfile import RunFile
        
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
        
#---------------------------------------------------------------------------------
class ClassTree(ttk.Treeview, PopMenu):
    def __init__(self, master, select_action=None, cnf={}, **kw):
        ttk.Treeview.__init__(self, master)
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
        self.select_action = select_action    
        self.text = ''
        self.clicktime = 0     
        self.init_pattern()        

    def on_enter(self, event=None):
        self.on_update()
        
    def on_update(self, event=None):
        if self.textbox != None:    
            text = self.textbox.get_text()  
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
            self.select_action(i, name, key)
        
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
                m = re.search('\s*(?P<key>class|def)\s+(?P<name>\w+)\s*[\(\:]', line)
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
            elif indent <=1 and re.match('[\w\_]+\(', s):
                name = s.split('(', 1)[0]                
                indent = 3      
                tagtext = s.split('(', 1)[0] + ' (%d)' %i
            elif indent <=1 and re.match('[\w\_]+\s*\:', s):
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
        p0 = '\.\.\s(?P<z_cmd>\w+)\:\:(?P<z_content>.*)'
        p1 = '\#\#+(?P<a_h1>[^\#]+)\#\#+\n|\*\*+(?P<b_h2>[^\*]+)\*\*+\n|\=\=+(?P<c_h3>[^\=]+)\=\=+\n'
        p2 = '\n(?P<e_h5>[^\n]+)\n\=\=+\n|\n(?P<f_h6>[^\n]+)\n\~\~+\n'
        p3 = '\n(?P<d_h4>[^\n]+)\n\*\*+\n|\n(?P<g_h7>[^\n]+)\n\-\-+\n'
        p4 = '\n(?P<h_minus>\s*\-\s*\w[^(\n\n)]+)|(?<=\:)(?P<z_colon>\:\n\n)'       
        p = '(%s)|(%s)|(%s)|(%s)|(%s)' % (p0, p1, p2, p3, p4)
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
        
class FileView(tk.Frame):
    def __init__(self, master, **kw):       
        tk.Frame.__init__(self, master)
        self.textobj = TagTextObj(self)
        self.textobj.pack(fill='both', expand=True)
        
    def set_text(self, text):
        self.textobj.set_text(text)   
             
class ClassNotebook(tk.Frame):
    def __init__(self, master, select_action=None, cnf={}, **kw):
        tk.Frame.__init__(self, master)
        self.pages = {}
        self.select_action = select_action
        notebook = ttk.Notebook(self)
        notebook.pack(fill = 'both', expand=True)
        self.notebook = notebook
        self.tree1 = self.add_page('Class', ClassTree) 
        self.tree2 = self.add_page('Preview', FileView)                 
            
        notebook.pack(fill='both', expand=True)
        notebook.bind('<ButtonRelease-1>', self.switch_page)        
    
    def set_text(self, text):
        self.tree1.set_text(text)
        self.tree2.set_text(text)
            
    def switch_page(self, event=None):
        dct = self.notebook.tab('current')
        label = dct['text'].strip()
        print('label')

    def add_page(self, label, widgetclass):
        frame = tk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)         
        widget = widgetclass(frame, select_action = self.select_action)
        widget.pack(fill='both', expand=True)         
        widget.notepage = frame
        self.notebook.add(frame, text=label.center(17))        
        #n = len(self.pages)        
        #self.notebook.select(n)        
        return widget                  
        
#-------------------------------------------------------------------------
class TreeView(ttk.Treeview):
    def __init__(self, master, **kw):
        ttk.Treeview.__init__(self, master, **kw)
        style = ttk.Style()
        style.configure('Calendar.Treeview', rowheight=24)
        self.config(style='Calendar.Treeview')
        self.tag_configure('folder', font='Mono 10 bold', foreground='#557')
        self.tag_configure('file', font='Mono 10', foreground='#555')        
        
#-------------------------------------------------------------------------
class FileTreeView(TreeView, PopMenu):
    def __init__(self, master, select_action=None, cnf={}, **kw):
        TreeView.__init__(self, master)
        self.data = {}
        self.dirs = []              
        self.files = []        
        self.click_select = 'double'
        style = ttk.Style()
        style.configure('Calendar.Treeview', rowheight=24)
        self.config(style='Calendar.Treeview')
        self.tag_configure('folder', font='Mono 10 bold', foreground='#557')
        self.tag_configure('file', font='Mono 10', foreground='#555')        
        self.select_action = select_action
        self.currentpath = '.'    
        home_dir = os.path.expanduser("~")
        os.chdir(home_dir)
        self.text = ''
        self.data = {}
        self.pathvars = {}
        self.clicktime = 0
        self.previtem = None
        cmds = [('Open', self.on_open), ('Update', self.on_update)]
        cmds.append(('-', None))
        cmds.append(('Create project', self.on_create_project))
        cmds.append(('-', None))
        
        cmds.append(('~/src/', self.go_src_path))
        cmds.append(('~/', self.go_home_path))
        cmds.append(('~/py', self.go_py_path))
        cmds.append(('~/py/test', self.go_test_path))
        cmds.append(('~/py/game', self.go_game_path))
        
        self.add_popmenu(cmds)    
        self.bind('<ButtonRelease-1>', self.on_select)         

    def on_create_project(self, event=None):           
        item = self.focus() 
        data = self.data.get(item)
        if data == None or self.select_action == None:
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
                    
        fileio.fwrite(path + os.sep + 'project.prj', str(dct))
        
    def add_file(self, filename):
        pass
        
    def add_dir(self, path):
        pass
         
    def go_src_path(self, event=None):
        path = os.path.expanduser('~') + os.sep + 'src'
        self.set_path(path)
 
    def go_home_path(self, event=None):
        path = os.path.expanduser('~') 
        self.set_path(path)
        
    def go_py_path(self, event=None):
        path = os.path.expanduser('~') + os.sep + 'py'
        self.set_path(path)
 
    def go_test_path(self, event=None):
        path = os.path.expanduser('~') + os.sep + 'py/test'
        self.set_path(path)      
           
    def go_game_path(self, event=None):
        path = os.path.expanduser('~') + os.sep + 'py/game'
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
        if data == None or self.select_action == None:
            return
        path, tag = data
        self.select_action(path, tag)
        
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
        if self.select_action == None or tag != 'file':
           return        
        if self.click_select == 'click' or doubleclick == True:
           self.select_action(path, tag)            
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

class DirTreeView(FileTreeView):
    def __init__(self, master, select_action=None, cnf={}, **kw):
        FileTreeView.__init__(self, master, select_action, cnf={}, **kw)        
        self.dirs = []              
        self.files = []
        self.history_item = ''
        
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

class PrjFiles(TreeView, PopMenu, RunFile):
    def __init__(self, master, select_action=None, **kw):
        TreeView.__init__(self, master, **kw)        
        self.mainfile = ''
        self.prjpath = ''
        self.files = []
        self.data = {}
        cmds = [('Open', self.on_open)]
        cmds.append(('Run', self.on_run))        
        self.add_popmenu(cmds)
        frame = tk.Frame(master)
        frame.pack(side='top', fill='x', expand=False)
        self.add_button(frame, 'Open', self.on_open)
        self.add_button(frame, 'Close', self.on_close)
        self.add_button(frame, 'Run', self.on_run)
        self.previtem = None
        self.clicktime = 0
        self.select_action = select_action
        self.bind('<ButtonRelease-1>', self.on_select)   
        
    def get_app(self):
        root = self.winfo_toplevel()
        if hasattr(root, 'app'):
            return root.app
        return None
        
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
        if self.select_action == None or tag != 'file':
           return        
        if doubleclick == True:
           self.select_action(path, tag)            
        
    def add_button(self, frame, label, action):
        button = tk.Button(frame, text=label)
        button.pack(side='left')
        button.bind('<ButtonRelease-1>', action)
        return button

    def on_run(self, event=None):
        if self.mainfile == '':
            return
        fn = self.mainfile        
        app = self.get_app()
        if app != None:
            app.run(fn)
        else:
            self.run(fn)

    def file_dialog(self, dialog, op='Open', mode='r'):
        filepath = '/home/athena/src/py/'        
        filename = dialog(defaultextension='.prj', mode = mode,
               filetypes = [('Project files', '.prj'), ('all files', '.*')],
               initialdir = filepath,
               initialfile = '',
               parent = self,
               title = op + ' File dialog'
               )
        if filename == None:
            return None
        return filename.name   
        
    def on_open(self, event=None):   
        filename = self.file_dialog(tk.filedialog.askopenfile, 'Open', 'r')   
        print('Filedialog return (%s)'%filename) 
        if filename == None or filename == '':
            return
        self.set_prj(filename)
        app = self.get_app()
        if app != None:
            app.set_prj(fn)            
            
    def on_close(self, event=None):
        app = self.get_app()
        if app != None:
            app.set_prj('')
        for obj in self.get_children():
            self.delete(obj)
        self.data = {}
        self.mainfile = ''
            
    def set_prj(self, fn):
        if fn == '':
            return
        try:
            text = fileio.fread(fn)
            dct = eval(text)
        except:
            return            
        dirpath = os.path.dirname(fn)
        self.prjpath = dirpath
        for obj in self.get_children():
            self.delete(obj)
        self.data = {}
        fn = dirpath + os.sep + 'main.py'
        if os.path.exists(fn):
            self.mainfile = fn
        for dir, files in dct.items():
            p = dirpath + dir 
            if dir == '':
                item = ''                
            else:
                item = self.add_dir(dir, p)        
            for fn in files:
                self.add_file(item, fn, p + os.sep + fn)
            
    def add_file(self, node, name, path):       
        item = self.insert(node, 'end', text=name, tag='file') 
        self.data[item] = (path, 'file') 
        self.files.append(path)        
        
    def add_dir(self, name, path):     
        item = self.insert('', 'end', text=name, tag='folder') 
        self.data[item] = (os.path.realpath(path), 'folder')                 
        return item
            

class TreeNotebook(tk.Frame):
    def __init__(self, master, select_action=None, cnf={}, **kw):
        tk.Frame.__init__(self, master)
        self.pages = {}
        self.select_action = select_action
        notebook = ttk.Notebook(self)
        notebook.pack(fill = 'both', expand=True)
        self.notebook = notebook
        self.tree1 = self.add_page('File', FileTreeView) 
        self.tree2 = self.add_page('Favorite', DirTreeView)    
        self.tree3 = self.add_page('Project', PrjFiles)             
            
        notebook.pack(fill='both', expand=True)
        notebook.bind('<ButtonRelease-1>', self.switch_page)
        self.tree1.set_path(os.getcwd())
        p0 = '/home/athena/src'
        p1 = p0 + '/py'
        for s in [p0, p1, p1 + '/example', p1 + '/test', p1 + '/game']:
            self.tree2.add_dir(s)            
    
    def set_path(self, path):
        self.tree1.set_path(path)
            
    def switch_page(self, event=None):
        dct = self.notebook.tab('current')
        label = dct['text'].strip()

    def add_page(self, label, widgetclass):
        frame = tk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)         
        widget = widgetclass(frame, select_action = self.select_action)
        widget.pack(fill='both', expand=True)         
        widget.notepage = frame
        self.notebook.add(frame, text=label.center(17))        
        #n = len(self.pages)        
        #self.notebook.select(n)        
        return widget            
           


if __name__ == '__main__':   
    import ui
    from ui import Messagebox 
    class TestFrame(tk.Frame):
        def __init__(self, master, select_act=None):       
            tk.Frame.__init__(self, master)
            self.select_act = select_act
            frame = TwoFrame(self, sep=0.8, type='v')
            frame.pack(fill='both', expand=True)
            frame1 = TwoFrame(frame.top, sep=0.5, type='v')
            frame1.pack(fill='both', expand=True)
            notebook1 = ClassNotebook(frame1.top, select_action=self.on_select_class)
            notebook1.pack(fill='both', expand=True)
            self.classview = notebook1.tree1
            self.fileview = notebook1.tree2
            
            notebook2 = TreeNotebook(frame1.bottom, select_action=self.on_select_file)
            notebook2.pack(fill='both', expand=True)
            msg = Messagebox(frame.bottom)
            msg.pack(side='bottom', fill='x', expand=False)
            statusbar = msg.add_statusbar()
            self.msg = msg
            treeview = notebook2.tree1
            treeview.msg = self
            treeview.click_select = 'click'
            treeview.set_path('/home/athena/src')
            treeview.active_file('/home/athena/src/menutext/idle.py')
            treeview.update()
            self.treeview = treeview
            notebook2.tree2.add_file(__file__)
            notebook2.tree2.add_file('/home/athena/src/menutext/menutext.py')
            notebook2.tree3.set_prj('/home/athena/src/py/game/PlantsVsZombies/project.prj')
            
        def puts(self, *lst, end='\n'):
            for text in lst:
                self.msg.puts(str(text) + ' ')
            
        def fread(self, filename):
            with open(filename, 'r') as f:
                text = f.read()
                f.close()
                return text
                
        def set_path(self, path):
            self.treeview.set_path(path)
            
        def on_select_file(self, filename, tag):
            self.puts(filename)
            text = self.fread(filename)
            self.classview.set_text(text, filename)
            self.fileview.set_text(text)
            if self.select_act != None:
                self.select_act(text)
            
        def on_select_class(self, i, name, key):      
            #self.textbox.goto(i, name, key) 
            self.puts(i, name, key)
            if type(i) is tuple:
                text = self.textbox.text[:i[0]]
                n = text.count('\n')        
                self.textbox.see('%d.0' %n)      
               
    def main():
        root = tk.Tk()
        root.title('Frame and Canvas')
        root.geometry('500x900') 
        frame = TestFrame(root)
        frame.pack(fill='both', expand=True)
        #frame.on_select_file('/home/athena/src/help/test.rst', '')
        frame.set_path('/home/athena/src/py/game')
        frame.mainloop()   
    
    main()



