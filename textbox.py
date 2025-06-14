import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import webbrowser

from textui import PopMenu, TextLinebar
     
class TextToken():     
    def init_py(self):
        pint = r'(?<![\w])(?P<int>(0x[\dabcdefABCDEF]+)|([\d\.\+\-]+))'
        pint1 = r'(?P<int>\d[\d\.e]*)'
        p = r'(?P<ln>\n+)|%s|(?P<word>[\w]+)|(?P<comments>\#[^\n]*)|' % pint
        p += r'(?P<str2>\"[^\"]*\")|(?P<str1>\'[^\']*\')|(?P<op>[\=\+\-\*\/\(\)\.\%\,])'
        p += r'|(?<=class)\s(?P<classname>\w+)'
        self.pattern = re.compile(p)    
            
        keys = 'from|import|def|class|if|else|elif|for|in|then|dict|list|continue|return'
        keys += '|None|True|False|while|break|pass|with|as|try|except|not|or|and|do|const|local'
        p1 = pint + r'|(?P<key>^%s)' % keys
        self.pattern1 = re.compile(p1)  
        
    def init_txt(self):        
        p = r'(?P<title>^[A-Z][A-Z\s\-\_\:]+)|(?P<function>\w+)\s*(?=\()|(?P<colon>\w.+\:)'
        p += r'|(?P<str1>\'[^\']*\')|(?P<str2>\"[^\"]*\")|(?P<word>[\w]+)'  
        self.pattern = re.compile(p)
        
        keys = r'Class|NAME|DESCRIPTION|PACKAGE\sCONTENTS|CLASSES|Function|Help\son'
        keys = keys.split('|')
        p1 = r'(?<![\w])(?P<int>[\d\.\+\-]+)|(?P<helpon>^%s)' % keys
        self.pattern1 = re.compile(p1)  
            
    def init_pattern(self):
        if self.ext == 'txt':
            self.init_txt()
        else:
            self.init_py()  
        self.init_token_vars()
            
    def remove_tags(self, idx1, idx2):        
        for s in self.tag_names():
            self.tag_remove(s, idx1, idx2)
            
    def init_token_vars(self):                                
        self.prev_ranges = ()
        self.tag_list = []    
        self.line_count = 0        
               
    def replace_str(self, text):
        q = '\"'
        def reps(s0):
            if not '\n' in s0:
                return q + 's' * (len(s0)+4) + q
            lst = []            
            for s in s0.splitlines():
                 n = len(s)
                 if n > 2:
                     n -= 2
                 lst.append(q+'s'*n+q)
            return '\n'.join(lst)
                 
        q3 = '\"\"\"'
        if q3 in text:               
            i = 0    
            lst = []
            for s in text.split(q3):                              
                if i == 0:
                   lst.append(s)
                else:
                   s = reps("\"aa" +s+"bb\"")
                   lst.append(s)
                i = 1 - i             
            text = ''.join(lst)
        text = text.replace('\\\"', '@&').replace('\\\'', '@$') 
        return text        
       
    def do_tag_p(self, tag, p):
        i1, j1, i2, j2 = p       
        idx1 = self.get_idx(i1, j1)
        idx2 = self.get_idx(i2, j2)                
        self.tag_add(tag, idx1, idx2)
        
    def m2tagp(self, m):        
        p0, p1 = m.span()        
        tag = m.lastgroup  
        s = m.group(0)      
        i, j = self.ln[-1]
        if tag == 'ln':        
            self.ln.append((i+len(s), p1))
            return
        elif tag == 'word':          
            m1 = re.fullmatch(self.pattern1, s)
            if m1 != None:
                tag = m1.lastgroup
                #self.msg(m1, m1.lastgroup )  
        if tag in ['word', 'space']:            
            return     
        else:
            return (tag, i, p0-j, i, p1-j)  
        
    def tag_pattern(self, lst, l1, l2):                
        idx1 = '%d.0' % l1
        idx2 = '%d.0' % (l2 + 1)
        self.remove_tags(idx1, idx2)        
        for item in lst:
            tag, i, j1, i2, j2 = item
            if i >= l1 and i <= l2:
               self.do_tag_p(tag, (i, j1, i2, j2))      
               
    def get_tag_list(self, l1, l2, lst=None):
        if lst == None:
            lst = self.tag_list
        lst1 = []
        for p in lst:
            i = p[1]
            if i >= l1 and i <= l2:
                lst1.append(p)  
        return lst1    
                    
    def create_tag_list(self, text0):    
        text = self.replace_str(text0)     
        self.ln = [(1, 0)]
        self.prev_word = ''  
        lst = []
        for m in re.finditer(self.pattern, text):
            p = self.m2tagp(m)  
            if p != None: 
                tag, i1, j1, i2, j2 = p                
                lst.append(p)
        return lst              
        
    def get_update_range(self, text, n1, n2):        
        if self.pre_text == '':
            return 1, n2           
        l1 = self.get_line_index('current')
        l2 = self.get_line_index('insert')
        if l1 > l2:
            l1, l2 = l2, l1
        l1 -= 2 
        l2 += 1
        if l1 < 1:
            l1 = 1  
        lines1 = self.pre_text.splitlines()
        lines2 = text.splitlines()
        if lines1[0:l1] != lines2[0:l1]:
            return 1, n2
        d = n2 - n1
        #self.msg('l1, l2', l1, l2, d, len(lines1[l2-d:]), len(lines2[l2:]), lines1[l2-d:] == lines2[l2:])
        if lines1[l2-d:] == lines2[l2:]:            
            return l1, l2
        else:
            return l1, n2    
        
    def get_tag_ranges(self, tag):
        lst = []
        tlst = self.tag_ranges(tag)
        n = len(tlst)
        for i in range(0, n, 2):
            p0, p1 = tlst[i], tlst[i+1]
            s0, s1 = str(p0).split('.')
            s2, s3 = str(p1).split('.')
            i1, j1, i2, j2 = int(s0), int(s1), int(s2), int(s3)
            lst.append((i1, j1, i2, j2))
        return lst    
        
    def dump_tags(self):
        dct = {}
        for tag in ('key', 'class', 'classname', 'str1', 'str2', 'int', 'op', 'self', 'comments'):
            dct[tag] = self.get_tag_ranges(tag)
        return dct
        
    def get_lines_dct(self, text):
        lines = text.splitlines()
        lst = []
        n = len(lines)
        dct = {}
        for i, s in enumerate(lines):
            if s in dct:
                dct[s].append(i)
            else:
                dct[s] = [i]
        return dct       

    def update_tag(self):        
        text = self.get_text()
        if self.pre_text == text:
            return          
        n = self.get_line_index('end')
        l1, l2 = self.get_update_range(text, self.line_count, n)   
        #print(l1, l2)   
        lst = self.create_tag_list(text)
        self.tag_pattern(lst, l1, l2)       
        self.pre_text = text
        self.tag_list = lst
        self.line_count = n          
       
#----------------------------------------------------------------------------------------
class TextBoxText():          
    def set_text(self, text):
        self.clear_all()    
        self.text = text   
        self.insert('1.0', text)
        self.update_all()     
        self.update_line_index()  
        self.edit_reset()        
        
    def get_text(self, tag=None):
        if tag != None:
            p = self.tag_ranges(tag)
            if p == ():
                return ''
            idx1, idx2 = p[0], p[1]
            return self.get(idx1, idx2)        
        return self.get('1.0', 'end -1c')       
        
    def fread(self, filename):        
        with open(filename) as f:
            text = f.read()
            f.close()
            return text
                          
    def see_line(self, i):
        self.tag_remove('sel', '1.0', 'end')
        i = self.get_line_index(i)               
        p = str(i)
        self.tag_add('sel', p + '.0', p + '.end')  
        self.see(p + '.0')         
         
    def goto(self, arg, name=None, key=None):        
        self.see_line(arg)
        
    def get_idx(self, i, j):  
        if j == 'e':
            return str(i) + '.end'
        return '%d.%d' % (i, j)
            
    def get_pos(self, idx):
        p = self.index(idx).split('.')
        return (int(p[0]), int(p[1]))
        
    def get_idx_head(self, idx):
        return idx.split('.')[0]
        
    def get_line_index(self, idx='current'):
        if type(idx) == int:
            return idx
        if type(idx) == str:
            if re.fullmatch(r'\d+', idx) != None:
               return int(idx)
            idx = self.index(idx)
        idx = self.index(idx).split('.')[0]
        return int(idx)

    def get_line_range(self, idx):
        idx1 = self.index(idx + ' linestart')        
        idx2 = self.index(idx + ' lineend')        
        return idx1, idx2
        
    def get_line_text(self, idx):
        if type(idx) == int:
            p = str(idx)
            idx1 = p + '.0'
            idx2 = p + '.end'
        else:
            idx1 = self.index(idx + ' linestart')        
            idx2 = self.index(idx + ' lineend')         
        return self.get(idx1, idx2)
        
    def get_current_word(self):
        text = self.get('insert wordstart')  
        m = re.search(r'\w+', text)
        if m != None:        
           return m.group(0)
        return ''
        
    def get_selected_word(self):
        key = self.get_text('sel')
        if len(key) < 2:
            idx = self.index('insert wordstart')
            key = self.get_current_word()
        else:
            idx = self.index('sel.first')  
        return idx, key
   
    def get_prevline_indent(self, idx):
        idx1 = self.index(idx + ' -1 lines')
        text = self.get(idx1 + ' linestart', idx1 + ' lineend') 
        s = text.strip()        
        indent = text.find(s)
        s0 = s.split(' ', 1)[0]
        if s0 in ['def', 'class', 'if', 'for', 'while', 'else', 'elif']:
            indent += 4
        return ' ' * indent       
        
    def select_lines(self):
        p = self.tag_ranges('sel') 
        if p == ():
            self.tag_add('sel', 'insert linestart', 'insert lineend')
        else:
            self.tag_add('sel', 'sel.first linestart', 'sel.first lineend')
        
#----------------------------------------------------------------------------------------   
class TextBoxEdit():        
    def set_modified(self):
        if self.modified == False:
            self.modified = True
            self.set_status('Modified', "True")           
            
    def on_text_changed(self, event):  
        self.update_tag()
        #self.linebar.update_lines(self.line_count)        
        
    def on_keydown(self, event):
        if event.state == 0x14:
            if event.keysym in 'vxz<>':
               self.update_set('check')  
               
    def on_keyup(self, event):
        key = event.keysym          
        self.set_status('key', str((event.state, event.keycode, key)) )        
        if key == 'Tab':
           self.edit_undo()   
           self.update_set('all')    
        elif event.state == 0x14:
            if key == 'a':
                self.on_select_all()
            elif key in 'vxz<>':
               self.update_set('all')  
        else:        
           self.update_set('check')          
        
    def on_key_v(self, event):   
        self.delete_text_before_paste()  
        self.update_set('check')
        
    def on_key_return(self, event):    
        idx = self.index('insert')
        self.insert(idx, self.get_prevline_indent(idx))
        self.update_set('check')
                
    def remove_one_tab(self, text):     
        lst = []
        for s in text.splitlines():
            s = s[:4].strip() + s[4:]
            lst.append(s)
        return '\n'.join(lst)
    
    def add_one_tab(self, text):
        lst = []
        for s in text.splitlines():
            lst.append('    ' + s)
        return '\n'.join(lst)      
        
    def remove_text(self, text):
        return ''

    def edit_selected_text(self, edit_action):
        if self.tag_ranges('sel') == ():
            idx1 = self.index('insert')
            idx2 = self.index(idx1 + ' lineend')
        else:
            idx1 = self.index('sel.first linestart')
            idx2 = self.index('sel.last lineend')  
        text = edit_action(self.get(idx1, idx2))
        self.replace(idx1, idx2, text)    
        self.tag_add('sel', idx1, idx2)       
        
    def on_add_tab(self, event=None):
        self.select_lines()
        self.edit_selected_text(self.add_one_tab) 
        self.update_set()   	 
        
    def on_remove_tab(self, event=None):
        self.select_lines()
        self.edit_selected_text(self.remove_one_tab) 
        self.update_set()         

    def on_copy(self, event=None):
        self.clipboard_clear()
        text = self.get_text('sel')
        self.clipboard_append(text)
        
    def on_paste(self, event=None):
        text = self.clipboard_get()
        p = self.tag_ranges('sel')
        if p == () or p == None:
            self.insert('insert', text)    
        else:
            idx1, idx2 = p
            self.replace(idx1, idx2, text)     
        self.update_set()
               
    def on_button_action(self, act, arg=None):
        if type(act) == list:
            arg = act[1]
            act = act[0]
        self.msg.puts('TextBox on_button_act', act, arg)
        if act == 'undo':
            try:
                self.edit_undo()
            except:
                self.root.warning('Nothing to undo')
        elif act == 'redo':
            try:
                self.edit_redo()
            except:
                self.root.warning('Nothing to redo')
        elif act == 'copy':
            self.on_copy()
        elif act == 'paste':
            self.on_paste()
        elif act == 'add tab' or act == 'add_tab':
            self.on_add_tab()
        elif act == 'remove tab' or act == 'remove_tab':
            self.on_remove_tab()       
        elif act == 'sel':
            if arg[0] == 'all':
                self.tag_add('sel', '1.0', 'end')
            else:    
                self.msg.puts(arg[0], arg[1])
                self.tag_add('sel', arg[0], arg[1])      

    def search_text(self, key, idx1='1.0', idx2='end'):  
        self.msg.puts('Find text:', key) 
        lst = []
        idx = idx1
        n = len(key)
        while idx != '':
            idx = self.search(key, idx, stopindex=idx2, forwards=True)
            if idx == '':
                break                     
            line = self.get_line_text(idx)
            i, j = self.get_pos(idx)            
            lst.append(i)
            head = '%4d '%(i) + line[0:j]
            self.msg.puts_tag(key, tag='bold', head=head, end=line[j+n:] + '\n') 
            idx = self.index(idx + ' lineend')
        return lst
        
    def find_in_text(self, path, text, key):
        i = -1     
        n = len(key)   
        lst1 = []
        for line in text.splitlines():
            i += 1           
            j = line.find(key)
            if j == -1:
                continue
            j1 = j + n
            lst1.append((i, j, line))
            head = path + ': %4d '%(i+1) + line[0:j]
            self.msg.puts_tag(key, tag='bold', head=head, end=line[j1:] + '\n') 
        return lst1 
            
    def on_find_text(self, event=None):
        self.msg.clear_all()
        idx, key = self.get_selected_word()
        if key != '':
            self.search_text(key)            

    def get_file_list(self, path=None):
        if path == None:
           path = os.path.dirname(os.path.realpath(self.filename))
           path = os.path.realpath(path + os.sep + '..')
        os.chdir(path)
        self.msg.puts(path +'/:')
        lst = os.listdir(path)   
        files = []   
        for s in lst:
            if s[0] == '.':
                continue
            filepath = os.path.realpath(s)                       
            if filepath.endswith('.py') and os.path.isfile(filepath):
                files.append(filepath)
        for s in lst:
            if s[0] == '.':
                continue
            filepath = os.path.realpath(s)                       
            if os.path.isdir(filepath):
                files += self.get_file_list(filepath)            
        #files.sort() 
        return files
        
    def on_find_files(self, arg=None):        
        self.msg.clear_all()        
        idx, key = self.get_selected_word()
        if '\n' in key:
            key = key.split('\n', 1)[0]   
        files = self.get_file_list()              
        for fn in files:
            text = self.fread(fn)
            lst1 = self.find_in_text(fn, text, key)    
            
    def cmd_find(self, args):  
        self.search_text(args)      
                
    def replace_selected_range(self, args):
        self.msg.puts('Replace selected text: (%s)' % str(args) )    
        find_str = args[0]
        replace_str = args[1]               
        p = self.tag_ranges('sel')
        if p == ():
            return False
        idx1, idx2 = p
        stop = False
        n0, n1 = len(find_str), len(replace_str)
        while not stop:
            index = self.search(find_str, idx1, stopindex=idx2)
            if index == '':
                stop = True
                break
            p = index.split('.')    
            i = int(p[1])
            j0 = i + n0
            j1 = i + n1
            idx1 = p[0] + '.' + str(j0) 
            self.replace(index, idx1, replace_str)
            line = self.get_line_text(index)            
            self.msg.puts(index, idx1, line[:i], end='')
            self.msg.puts_tag(find_str + '==>' + replace_str, tag='bold', end=line[j1:]+'\n') 
        return            
            
    def cmd_replace(self, args):  
        self.msg.clear_all()
        if self.tag_ranges('sel') != ():
            self.replace_selected_range(args)
            return        
        text = self.get_text()        
        self.msg.puts('Replace text: (%s)' % str(args) )        
        find_str = args[0]
        replace_str = args[1]        
        lst = []
        i = 0         
        for line in text.splitlines():     
            i += 1       
            for m in re.finditer(find_str, line):
                s, e = m.start(), m.end()
                idx1 = '%d.%d' % (i, s)
                idx2 = '%d.%d' % (i, e)
                self.replace(idx1, idx2, replace_str)
                self.msg.puts(' %4d ' %i, s,e, line[:s], end='')
                self.msg.puts_tag(line[s:e], tag='bold', end=line[e:]+'\n')       
        self.update_all()              

    def delete_text_before_paste(self):
        p = self.tag_ranges('sel')
        if p == () or p == None:
            return
        idx1, idx2 = p        
        a = self.add_idx(idx1, -1)
        b = self.add_idx(idx2, 1)
        self.tag_add('paste', a, b)
        self.delete(idx1, idx2)
        
    def add_idx(self, idx, v):        
        p = str(idx).split('.')
        i = int(p[1]) + v
        if i < 0:
            i = 0
        return p[0] + '.' + str(i)    
        
    def edit_copy(self):   
        self.on_copy()   
    
    def edit_cut(self):
        self.on_copy()
        self.edit_selected_text(self.remove_text) 
        self.select_none()
        
    def edit_paste(self):
        self.on_paste()
                
class TextBox(tk.Text, TextToken, TextBoxEdit, TextBoxText, PopMenu):
    def __init__(self, master, **kw):
        tk.Text.__init__(self, master, **kw)  
        self.root = None
        self.master = master
        self.vars = {}       
        self.modified = False
        self.filename = ''
        self.ext = ''
        self.pre_text = ''
        self.classbox = None   
        self.helpbox = None
        self.init_config()        
        self.init_pattern()
        act = {} 
        act['undo'] = self.edit_undo
        act['redo'] = self.edit_redo
        self.button_action = act
        self.cmdlist = []
        keys = 'from|import|def|class|if|else|elif|for|in|then|dict|list|continue|return'
        keys += '|None|True|False|while|break|pass|with|as|try|except|not|or|and|do|const|local'
        self.keywords = keys.split('|')
        self.g_vars = globals()
        self.l_vars = locals()           
             
        cmds = [('Find', self.on_find_text),
                #('Goto Define', self.on_goto_define),
                ('Find in files', self.on_find_files),
                ('Help', self.on_search_help),
                ('Google Search', self.on_google_search),
                ('-'),
                ('Select All', self.on_select_all),
                ('-'),
                ('Copy', self.on_copy),
                ('Paste', self.on_paste),
                ('-'),
                ('Add Tab', self.on_add_tab),
                ('Remove Tab', self.on_remove_tab),
                ('-'),
                ('Eval', self.on_eval_cmd),
                ('Exec', self.on_exec_cmd),
                
                ]
        menu = self.add_popmenu(cmds)        
   
        self.bind('<ButtonRelease-1>', self.on_click)
        self.bind('<KeyPress>', self.on_keydown)
        self.bind('<KeyRelease>', self.on_keyup) 
        self.bind('<<check_cmd_list>>', self.check_cmdlist)
        for key in ['<F6>', '<Tab>', '<Control-period>']:
            self.bind(key, self.on_add_tab)
        for key in ['<F2>', '<Shift-Tab>', '<Control-comma>']:
            self.bind(key, self.on_remove_tab)   
        self.bind('<Control-f>', self.on_find_text)
        self.bind('<Control-v>', self.on_key_v)
        self.bind('<KeyRelease-Return>', self.on_key_return)  
        self.bind_all('<<text_changed>>', self.on_text_changed)                   
        self.tag_list = []                     
        self.insert('1.0', '\n'*30)                  
        
    def set_filename(self, filename):
        self.filename = filename
        if '.' in filename:
            self.ext = os.path.splitext(filename)[-1].replace('.', '')                          
        else:
            self.ext = ''
        self.init_pattern()    
        
    def check_cmdlist(self, event=None):
        if self.cmdlist == []:
           return
        cmd, arg = self.cmdlist.pop(0)
        #print(cmd, arg) 
        if cmd == 'update_text':
           self.update_tag()
        elif cmd == 'gotoline' or cmd == 'goto':              
           self.goto(arg)
              
    def set_var(self, key, value):
        self.vars[key] = value

    def on_button_action(self, act, arg=None):
        if type(act) == list:
            arg = act[1]
            act = act[0]
        self.msg.puts('TextBox on_button_act', act, arg)
        if act in self.button_action:
            self.button_action[act](arg)
        
    def add_command(self, label, command):
        menu.add_command(label=label, command=command)
        
    def init_config(self):    
        monofont = ('Mono', 10)       
        self.color = '#121'
        self.config(font=monofont)
        self.config(padx=5)
        self.config(foreground=self.color)
        self.config(background='#f5f5f3')        
        self.config(undo=99)          
        self.config(exportselection=True)
        self.vars = {}
        bold = (monofont[0], monofont[1], 'bold')
        self.tag_config('key', font=bold, foreground='#338')
        self.tag_config('class', font=bold, foreground='#338')
        self.tag_config('classname', font=bold, foreground='#383')
        self.tag_config('str1', foreground='#c83')
        self.tag_config('str2', foreground='#c83')
        self.tag_config('int',  foreground='#383')
        self.tag_config('op',  foreground='gray')
        self.tag_config('self',  foreground='#333')
        self.tag_config('comments',  foreground='#789')
        self.tag_config('selected',  background='lightgray')
        self.tag_config('find',  background='yellow')
        self.tag_config('curline', background='#e7e7e7') 
        self.tag_config('title', font='Mono 11 bold', foreground='#333', background='#ddd') 
        self.tag_config('bold', font='Mono 10 bold', foreground='#333')
        self.tag_config('function', font='Mono 10', foreground='#000')      
        self.tag_config('helpon', font='Mono 10 bold', foreground='#555', background='#ddd')   
        self.tag_config('colon', font='Mono 10 bold', foreground='#555')
        self.tag_config('black', font='Mono 10', foreground='#000')
        self.tag_config('word', font='Mono 10', foreground='#222')
        self.tag_config('gray', font='Mono 10', foreground='#333')        
        self.key_tagnames = ['key', 'class', 'classname', 'str1', 'str2', 'int', 'op', 'self', 'comments'] 
                
    def on_clear(self, event=None):
        self.textbox.clear_all()
          
    def select_none(self):
        self.tag_remove('sel', '1.0', 'end')        
              
    def select_class(self, i, name, key):               
        self.select_none()
        text = self.get_line_text(i)
        if name in text:
            idx = str(i) + '.0'
            self.see(idx)
            idx = self.search(name, idx)
            self.tag_add('sel', idx, idx+'+%dc'%len(name))
        else:
            self.goto_define(name)          
            
    def on_search_help(self, event=None):
        idx, key = self.get_selected_word()                
        if 'ttk.' in key:
            key = key.replace('ttk.', 'tkinter.ttk.')
        elif 'tk.' in key and not 'Gtk' in key:
            key = key.replace('tk.', 'tkinter.')        
        if self.helpbox != None:    
           self.helpbox.find_obj(key)                
     
    def on_google_search(self, event=None):
        idx, key = self.get_selected_word()
        if key == '' or key == None:
            return
        base_url = "http://www.google.com/search?q="
        webbrowser.open(base_url + 'python ' + key)
        
    def on_click(self, event=None):
        self.update_line_index()
        
    def try_eval(self, s, g_vars, l_vars):    
        if s == '':
            return    
        try:
           r = eval(s, g_vars, l_vars) 
           self.msg.puts(r)
        except:
           pass
                   
    def try_exec(self, s, g_vars, l_vars):
        try:
           r = exec(s, g_vars, l_vars)         
        except:
           pass
        self.try_eval(s, g_vars, l_vars)            

    def try_exec1(self, s, g_vars, l_vars):
        r = exec(s, g_vars, l_vars)         
        self.try_eval(s, g_vars, l_vars) 
           
    def exec_cmd(self, s, g_vars, l_vars):
        if s == '':
            return
        s = s.strip()
        if s == '':
            return
        self.msg.puts_tag('>>> ' + s, 'bold')
        if s.find('print') == 0:
            s = s[6: -1]
            self.try_exec1(s, g_vars, l_vars)
        else:
            self.try_exec1(s, g_vars, l_vars)
               
    def on_exec_cmd(self, event=None): 
        text = self.get_text('sel')   
        if text == '':
            text = self.get_text()              
        for s in self.get_text().splitlines():
            if s.find('import') >= 0:
               exec(s, self.g_vars, self.l_vars)           
        for s in text.splitlines():
            self.exec_cmd(s, self.g_vars, self.l_vars)   
            
    def on_eval_cmd(self, event=None): 
        text = self.get_text('sel')   
        if text == '':
            return
        for s in text.splitlines():
            self.try_eval(s.strip(), self.g_vars, self.l_vars)    
                                   
    def clear_all(self):
        self.remove_tags('1.0', 'end') 
        self.tag_delete(self.tag_names())
        self.delete('1.0', 'end')
        
    def on_select_all(self, event=None):
        self.tag_add('sel', '1.0', 'end')                                   
                
    def update_set(self, flag='check'):  
        self.update_flag = flag
        #self.event_generate('<<text_changed>>')
        self.update_tag()  
        if self.modified == False:
           self.set_modified()
              
    def update_all(self, flag=None):                
        self.update_tag()        
        if flag == 'all' and self.root != None:
            self.root.do_update('class')          
    
    def set_status(self, var, value):        
        if self.statusbar == None:
            self.msg.puts(var, value)
            return
        self.statusbar.set_var(var, value)    
        
#-------------------------------------------------------------------------------------
class ScrollText(TextBox):
    def __init__(self, master, **kw):
        frame = tk.Frame(master)
        frame.pack(fill='both', expand=True)
        TextBox.__init__(self, frame, **kw)   
        self.frame = frame      
        self.master = master
        self.statusbar = None
        self.linebar = TextLinebar(frame)
        self.linebar.pack(side='left', fill='y', expand=False)     
        self.width = self.winfo_reqwidth()
        scrollbar = tk.Scrollbar(frame, command=self.yview)
        scrollbar.pack(side='right', fill='y', expand=False)
        self.scrollbar = scrollbar
        self.config(yscrollcommand = self.on_scroll)       
            
    def add_widget(self, idx, widget):
        self.window_create(idx, window=widget)
            
    def get_view_range(self):
        i = self.get_line_index('@0,0')
        j = self.get_line_index('@0,%d'%self.winfo_vrootheight())
        return i, j
        
    def update_line_index(self):
        self.tag_remove('curline', '1.0', 'end')
        p1 = self.index('insert').split('.')[0]
        idx1 = p1 + '.0'
        idx2 = p1 + '.end'
        self.tag_add('curline', idx1, idx2)  
        self.tag_lower('curline') 
        
        if self.statusbar == None:
            return
        n = self.index('end').split('.')[0]
        p = self.index(tk.CURRENT)        
        self.set_status('line', '%s/%s' % (p, n))     
                
    def on_scroll(self, arg0, arg1):
        self.scrollbar.set(arg0, arg1)    
        i, j = self.get_view_range() 
        self.linebar.scroll_set(i, j, self.dlineinfo)        
        if self.statusbar != None:
            self.update_line_index()
            self.set_status('Top', str(i))  

    def goto_define(self, key):      
        text = self.get_text()  
        pattern = r'(class|def)\s+(%s)\s*\(|(%s)\s+\=' % (key, key)
        m = re.search(pattern, text)
        if m != None:
            idx = self.search(m.group(0), '1.0')
            idx1 = idx.split('.')[0] + '.end'
            self.tag_add('sel', idx, idx1)
            self.see(idx)     
            return True
        for fn in self.get_file_list():
            text = self.fread(fn)
            m = re.search(pattern, text)
            if m != None:  
                self.find_in_text(fn, text, m.group(0))
                return                    

    def search_define(self, key):    
        text = self.get_text()  
        pattern = r'(class|def)\s+(%s)\s*\(' % key 
        m = re.search(pattern, text)
        if m != None:
            self.goto(self.search(m.group(0), '1.0'))   
            return True
        lst = self.search_text(key, '1.0', 'end')
        if lst != []:
           self.goto(lst[0])   
           return 
        for fn in self.get_file_list():
            text = self.fread(fn)
            m = re.search(pattern, text)
            if m != None:  
                self.find_in_text(fn, text, m.group(0))
                return    
        
    def search_self(self, idx):
        idx = self.search('class ', 'current', stopindex='1.0', backwards=True)
        if idx == '':
            return ''
        self.goto(idx)    
        
    def on_goto_define(self, event=None): 
        self.msg.clear_all()
        idx, key = self.get_selected_word()    
        if key == 'self':
            self.search_self(idx)
        else:
            self.search_define(key)     
            

        
#---------------------------------------------------------------------------------- 
def test_textbox(filename='', TextBox=ScrollText):
    from aui import Messagebox, TwoFrame
    from fileio import fread
    root = tk.Tk()
    root.title('TextEditor')
    root.geometry('1024x900')    
    frame = TwoFrame(root, type='v', sep=0.7)
    frame.pack(fill='both', expand=True)  
    
    textbox = ScrollText(frame.top)
    textbox.pack(fill='both', expand=True)
    
    msg = Messagebox(frame.bottom)        
    statusbar = msg.add_statusbar()
    msg.pack(side='bottom', fill='both', expand=True)
    textbox.msg = msg
    textbox.statusbar = statusbar     
    
    def open_file(fn):
        if os.path.exists(fn) == False:
           return
        text = fread(fn)
        textbox.set_filename(fn)
        textbox.set_text(text)
        if '.rst' in fn:
            from rstview import RstView
            rstview = RstView(textbox)
            rstview.set_text(text)
            textbox.add_widget('0.0', rstview)            
            
        root.title('TextEditor - ' + fn)
        
    def cmd_act(cmd, arg):
        if cmd == 'gotofile':
           if textbox.filename != arg:                  
              open_file(arg)
        elif cmd == 'gotoline':
           textbox.cmdlist.append((cmd, int(arg)))
        elif cmd == 'goto':
           textbox.cmdlist.append((cmd, int(arg)))               
        textbox.event_generate('<<check_cmd_list>>')  
             
    msg.action = cmd_act  
    if filename != '':
       open_file(filename) 
    frame.mainloop()
        
#----------------------------------------------------------------------------------      
if __name__ == '__main__':   
    fn = __file__      
    #fn = '/home/athena/tmp/ver.py'
    #fn = '/home/athena/src/help/test.rst'
    test_textbox(fn)          
        



