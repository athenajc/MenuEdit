from tkinter import ttk
from aui.TreeView import TreeView
import re, sys

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
        self.bind('<ButtonRelease-1>', self.on_select)    
        self.bind('<Enter>', self.on_enter)  
        self.bind_all("<<SwitchTextBox>>", self.on_update)
        self.bind_all("<<SetText>>", self.on_update)        
        self.cmd_action = None #self.winfo_toplevel().cmd_action    
        self.text = ''
        self.clicktime = 0     
        self.init_pattern()       
       
    def bind_act(self, act):
        self.cmd_action = act
        
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
             

class ClassView():
    def __init__(self, app):
        self.tester = None
        self.app = app
        self.init_ui(app)
    
    def open(self, path):
        self.app.root.title(path)
        self.msg.puts(path)
        self.text.open(path)        
        text = self.text.get_text()
        self.classtree.set_text(text)
        
    def on_select_file(self, event=None):        
        obj = event.widget
        path, tag = obj.getvar('<<SelectFile>>')
        self.open(path)        
        
    def on_select_class(self, cmd, data=None):
        if cmd == 'textbox':
            return self.text
        elif cmd == 'class':
            i, name, key = data
            self.text.goto(i)
        
    def add_filetree(self, app, msg):
        import DB
        from aui.FileTree import FileTreeView
        filetree = FileTreeView(app.treeframe)
        path = '/link'
        filetree.set_path(path)
        filetree.click_select = 'click' 
        filetree.bind('<<SelectFile>>', self.on_select_file)
        self.filetree = app.filetree = filetree
        filetree.msg = msg
        return filetree
        
    def on_new(self, event=None):
        self.text.set_text('')
        self.text.filename = '/home/athena/tmp/tmp.py'
        
    def on_save(self, event=None):
        pass
        
    def on_exec_cmd(self, event=None): 
        if self.tester == None:
            from runfile import ExecCmd 
            self.tester = ExecCmd(self, self.msg)
        text = self.text.get_text('sel')
        if text.strip() == '':
            text = self.text.get_text()   
        sys.stdout = self.msg          
        self.tester.exec_text(text)
        
    def on_test(self, event=None):
        from aui import RunServer    
        app = self
        filename = self.text.filename
        self.puts = self.msg.puts    
        sys.stdout = self.msg    
        app.server = RunServer(app, filename)  
        
    def add_textbox(self, app, msg):
        bg='#323c44'
        panel = app.get('panel', bg=bg)
        from aui.TextObj import Text
        layout = panel.get_obj('layout')
        bar = panel.get_obj('panel', bg=bg)
        layout.add_top(bar, 52)
        #bar.pack(side='top')
        buttons = [('   New   ', self.on_new), 
                   ('   Save   ', self.on_save), 
                   ('', ''), 
                   ('   Exec   ', self.on_exec_cmd),
                   ('      Test      ', self.on_test)]
        bar.add_buttons(buttons, style='h',  space=1, bg=bg, fg='white', pady=0)
        self.text = app.text = text = Text(panel, dark=True)
        #text.pack(side='top', fill='both', expand=True)
        layout.add_box(text)
        text.msg = msg
        msg.textbox = text
        self.open('/home/athena/tmp/tmp.py')
        text.panel = panel
        return text
        
    def add_classtree(self, app, msg):
        app.root.cmd_action = self.on_select_class
        self.classtree = classtree = app.classtree = ClassTree(app.treeframe)        
        classtree.msg = msg
        classtree.bind_act(self.on_select_class)
        return classtree
        
    def init_ui(self, app):          
        msg = self.msg = app.msg = app.get('msg')        
        app.treeframe = treeframe = app.get('frame')
        layout = treeframe.get('layout')
        filetree = self.add_filetree(app, msg)
        classtree = self.add_classtree(app, msg)
        layout.add_V2(filetree, classtree, 0.5)          
        
        layout = app.get('layout')
        text = self.add_textbox(app, msg)     
        layout.add_HV(treeframe, text.panel, msg, (0.3, 0.7))        


def class_view(app=None):
    from aui import TopFrame
    if app == None:
       app = TopFrame()
    panel = app.add('panel')
    panel.pack(fill='both', expand=True)
    ClassView(panel)          
         
    
if __name__ == '__main__':   
    from aui import App
    
    app = App(size=(1200, 900))
    def on_test(event=None):
        class_view()
    panel = app.add('panel', height=1)
    panel.pack()
    button = panel.add_button('test', on_test)
    #ClassView(app)
   
    app.mainloop() 


