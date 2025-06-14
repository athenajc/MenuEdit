import os
import re
import sys
import tkinter as tk
import webbrowser
import numpy as np
from textui import PopMenu
from textui import TextLinebar
import difflib
import pygments
from pygments.lexers import Python3Lexer
from pygments.formatters import HtmlFormatter
from textui import PopMenu, TextLinebar, TextObj
from DB.fileio import *
from codestyle import codestyle
import time
from runfile import ExecCmd

Q3a = "\"\"\""
Q3b = '\'\'\''
Q3 = [Q3a, Q3b]


class TextToken():        
    def init_lexer(self):
        self.lexer = Python3Lexer()
        self.init_config()
        self.load_code_style()
        
    def load_code_style(self):        
        dct = codestyle
        
        mono = ("Mono", 10) 
        bold = (mono[0], mono[1], 'bold')
        fgcolor = dct.get('foreground')
        bgcolor = dct.get('background')        
        tokens = dct['tokens']
        
        self.config(foreground=fgcolor)
        self.config(background=bgcolor)   
        self.config(insertbackground="#fa5")
        self.config(selectbackground="#555")
        self.tag_config('insert', bg=dct.get('insert_bg'))
        self.tag_config('sel', background ='#1a1a1f',  foreground='#999')
        self.tag_config('find', foreground='black', background='#999')
        self.tag_config('Q3', foreground=tokens.get('Token.Literal.String.Doc'))

        for token, data in tokens.items():
            self.tag_config(token, foreground=data, font=mono)                     
        
    def init_config(self):    
        monofont = ("Mono", 10)       
        self.config(padx=5)
        self.config(undo=99)       
        self.config(insertwidth=1)   
        self.config(exportselection=True)
        self.vars = {}       

    def map_tag(self, token, content):
        tag = token[0] 
        if tag == 'Text':
            return False
        if tag == 'Name':
            if token[-1] == tag:                        
                return False     
        return str(token)                 

    def get_tag_ranges(self, name):
        lst = self.tag_ranges(name)
        n = len(lst)
        lst1 = []
        for i in range(0, n, 2):
            a, b = lst[i], lst[i+1]
            lst1.append((str(a), str(b)))
        return lst1
        
    def remove_tags(self, idx1, idx2):  
        for s in self.tag_names():
            if s == 'sel':
                continue
            self.tag_remove(s, idx1, idx2)
            
    def tag_one_line(self, i, text):        
        j = 0
        lst = []        
        for token, content in self.lexer.get_tokens(text):            
            tag = self.map_tag(token, content)             
            n = len(content)                
            
            if tag == False:
                j += n
                continue                    
            #print((i, j), tag, token, '(%s)'%content)
            a = '%d.%d' % (i, j)
            b = '%d.%d' % (i, j+n)  
            if n == 3 and content in Q3:
                #print(i, j, n, content)
                if self.q3start == None:
                    self.q3start = a
                else:
                    lst.append(('Q3', self.q3start, b))
                    self.q3start = None
            if self.q3start == None:
               lst.append((tag, a, b))      
            j += n
        return lst
            
    def tag_lst(self, tag, lst):
        for a, b in lst:
            self.tag_add(tag, a, b)
            
    def tag_line(self, i=None, line=None):        
        if i == None:
            i = self.get_line_index('insert')
        s = str(i)
        a, b = s + '.0', s + '.end'    
        self.remove_tags(a, b)            
        if line == None:
            line = self.get(a, b)
        for p in self.tag_one_line(i, line):
            tag, a1, b1 = p
            self.tag_add(tag, a1, b1)  
        return line
        
    def tag_lines(self, l1, l2, lines=None):
        a, b = '%d.0' % l1, '%d.end'%l2
        self.remove_tags(a, b)
        if lines == None:
            lines = self.get(a, b).splitlines()
        n = len(lines)    
        for i in range(l1, l2+1):
            if i-l1 >= n:
                break
            for p in self.tag_one_line(i, lines[i-l1]): 
                tag, a1, b1 = p
                self.tag_add(tag, a1, b1)    
        return lines  
            
    def update_tag(self, a, b):         
        prelines = self.vars.get('lines', [])  
        if prelines == []:            
            self.tag_all()
            return  
        n = self.get_line_index('end')    
        b = min(n, b)  
        self.q3start = None 
        textlines = self.tag_lines(a, b)            
        self.vars['lines'][a:b] = textlines
        self.line_count = n   
 
    def tag_all(self):             
        self.vars['tagging'] = True
        text = self.get_text()  
        self.q3start = None        
        textlines = self.get_text().splitlines()
        self.vars['lines'] = textlines  
        n = len(textlines)
        self.tag_lines(1, n, textlines)             
        self.pre_text = text
        self.line_count = n        
        self.vars['tagging'] = False     
        
    def update_add(self, flag='range'): 
        updates = self.vars.get('updates', [])
        if flag == 'all':
            updates += [1, self.get_line_index('end')]            
        elif flag == 'range':            
            updates += self.get_current()
        else:
            updates += flag    
        self.vars['updates'] = updates
        
    def check_update(self):
        updates = self.vars.get('updates', [])
        if updates == [] or self.vars.get('tagging') == True:
            self.after(100, self.check_update)
            return                   
        
        updates += self.get_current()       
        n1, n2 = min(updates), max(updates)    
        
        if n2 - n1 > 300:
             self.vars['updates'] = [n1+300, n2]    
             n2 = n1 + 300
        else:
             self.vars['updates'] = []          
        self.update_tag(n1, n2)
        self.after(100, self.check_update)

class TextTab():
    def select_lines(self):
        p = self.tag_ranges('sel') 
        if p == ():
            self.tag_add('sel', 'insert linestart', 'insert lineend')
        else:
            self.tag_add('sel', 'sel.first linestart', 'sel.first lineend')
                
    def edit_selected_text(self, edit_action):
        if self.tag_ranges('sel') == ():
            idx1 = self.index('insert')
            idx2 = self.index(idx1 + ' lineend')
        else:
            idx1 = self.index('sel.first linestart')
            idx2 = self.index('sel.last lineend')  
        text = edit_action(self.get(idx1, idx2))        
        self.replace(idx1, idx2, text)   
        n = text.count('\n')
        i = self.get_line_index(idx1) 
        a = str(i) + '.0'
        b = str(i+n) + '.end'
        self.tag_add('sel', a, b) 
        self.update_add([i, i+n])
        
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
        
    def on_add_tab(self, event=None):
        self.select_lines()
        self.edit_selected_text(self.add_one_tab) 
        
    def on_remove_tab(self, event=None):
        self.select_lines()
        self.edit_selected_text(self.remove_one_tab) 
        
class TextUtils():     
    def clear_all(self, text=None):
        self.delete('1.0', 'end')
        self.remove_tags('1.0', 'end')    
        
    def update_all(self):
        self.tag_all()     

    def get_current(self):
        i = self.get_line_index('insert')
        j = self.get_line_index('current') 
        return [i, j]
        
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
        if not os.path.exists(filename):
            return      
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
              
    def goto_pos(self, pos):
        self.see(pos)
                
    def get_pos(self, idx):
        p = self.index(idx).split('.')
        return (int(p[0]), int(p[1]))

    def get_line_index(self, idx='current'):
        if type(idx) == int:
            return idx
        if type(idx) == str:
            if idx.isdigit():
               return int(idx)
            idx = self.index(idx)
        idx = self.index(idx).split('.')[0]
        return int(idx)

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

    def set_filename(self, filename):
        self.filename = filename
        if '.' in filename:
            self.ext = os.path.splitext(filename)[-1].replace('.', '')                          
        else:
            self.ext = ''
            
    def open(self, file):
        self.filename = file
        text = fread(file)
        self.insert('1.0', text)
        self.edit_reset()
        self.update_all()
        
    def set_status(self, var, value):      
        return  
        if self.statusbar == None:
            self.msg.puts(var, value)
            return
        self.statusbar.set_var(var, value)    
        
    def cmd_act(self, cmd, arg):
        if cmd == 'gotofile':
           if self.filename != arg:                  
              self.open(arg)
        elif cmd == 'gotoline':
           self.cmdlist.append((cmd, int(arg)))
        elif cmd == 'goto':
           self.cmdlist.append((cmd, int(arg)))               
        self.event_generate('<<check_cmd_list>>')  
             
    def check_cmdlist(self, event=None):
        if self.cmdlist == []:
           return
        cmd, arg = self.cmdlist.pop(0)
        #print(cmd, arg) 
        if cmd == 'update_text':
           self.update_tag()
        elif cmd == 'gotoline' or cmd == 'goto':              
           self.goto(arg) 

    def on_select_all(self, event=None):
        self.tag_add('sel', '1.0', 'end')    
        
    def on_update_all(self, event=None):
        self.tag_all() 
        
    def on_copy(self, event=None):
        self.clipboard_clear()
        text = self.get_text('sel')
        self.clipboard_append(text)

    def paste(self):
        text = self.clipboard_get()
        p = self.tag_ranges('sel')
        if p == () or p == None:
            self.insert('insert', text)    
        else:
            idx1, idx2 = p
            self.replace(idx1, idx2, text)     
        self.update_add([idx1, idx2])
        
    def on_paste(self, event=None):
        self.paste()
        
    def delete_text_before_paste(self):        
        p = self.tag_ranges('sel')
        if p == () or p == None:
            return
        a, b = p                
        self.tag_add('paste', str(a) + '-1c', str(b) + '+1c')
        self.delete(a, b)

    def on_key_v(self, event):   
        self.delete_text_before_paste()  
        self.update_add('range')
        
    def on_key_return(self, event): 
        idx = self.index('insert')
        self.insert(idx, self.get_prevline_indent(idx))
        n = self.get_line_index('insert') 
        self.update_add([n-1, n+1])

    def on_keydown(self, event):
        if event.state == 0x14 and event.keysym in 'vxz<>':
           self.update_add(self.get_current())  
               
    def on_keyup(self, event):      
        key = event.keysym          
        #self.set_status('key', str((event.state, event.keycode, key)) )        
        if key == 'Tab':
           self.edit_undo()   
           self.update_add('range')    
        elif event.state == 0x14:
            if key == 'a':
                self.on_select_all()
            elif key in 'vxz<>':
               self.update_add('range')  
        elif key.isascii():            
            self.update_add(self.get_current())  
        
    def on_double_click(self, event=None):
        self.event_generate("<<TextSelected>>")
            
class TextSearch():
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
        self.msg.update_tag(key=key)
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
            
    def get_file_list(self, path=None):        
        if path == None:
           path = dirname(realpath(self.filename))           
           #path = os.path.realpath(path + os.sep + '..')
        files = []   
        for fn in get_files(path):
            files.append(path + os.sep + fn)            
        return files
        
    def on_find_files(self, arg=None):        
        self.msg.clear_all()        
        idx, key = self.get_selected_word()
        if '\n' in key:
            key = key.split('\n', 1)[0]   
        files = self.get_file_list() 
        n = 0
        for fn in files:
            text = self.fread(fn)            
            lst1 = self.find_in_text(fn, text, key)            
            n += len(lst1)
        self.msg.update_tag(key=key)
        if n > 0:
            return
        files = self.get_file_list('~/src/aui') 
        for fn in files:
            text = self.fread(fn)         
            if text == None or text == '':
                continue   
            lst1 = self.find_in_text(fn, text, key)            
        self.msg.update_tag(key=key)    
            
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
        
    def on_find_text(self, event=None):
        self.msg.clear_all()
        self.event_generate("<<Text Find>>")
        idx, key = self.get_selected_word()
        if key != '':
            self.search_text(key)     
            
    def on_google_search(self, event=None):
        idx, key = self.get_selected_word()
        if key == '' or key == None:
            return
        base_url = "http://www.google.com/search?q="
        webbrowser.open(base_url + 'python ' + key)
        
    def on_search_help(self, event=None):
        idx, key = self.get_selected_word()                
        if 'ttk.' in key:
            key = key.replace('ttk.', 'tkinter.ttk.')
        elif 'tk.' in key and not 'Gtk' in key:
            key = key.replace('tk.', 'tkinter.')  
        self.setvar('<<FindObjKey>>', key)
        self.event_generate('<<FindObjHelp>>')
        #if self.helpbox != None:    
        #   self.helpbox.find_obj(key)   
   
class TextUI():
    def get_view_range(self):
        i = self.get_line_index('@0,0')
        j = i + 50
        return i, j

    def update_line_index(self):
        i, j = self.get_view_range() 
        self.linebar.scroll_set(i, j, self.dlineinfo)  

    def check_view_range(self):
        pos = self.dlineinfo('@0,0')
        if pos != self.pos:
            self.pos = pos
            self.update_line_index()
    
    def add_linebar(self, frame):
        self.linebar = TextLinebar(frame)
        self.linebar.pack(side='left', fill='y', expand=False) 
        self.pos = self.dlineinfo('@0,0')
        self.configure(yscrollcommand=self.on_scroll)        

    def on_scroll(self, arg0, arg1):
        self.scrollbar.set(arg0, arg1)    
        i, j = self.get_view_range() 
        self.linebar.scroll_set(i, j, self.dlineinfo)        
        if self.statusbar != None:
            self.update_line_index()
            self.set_status('Top', str(i))  
        
    def add_scrollbar(self, frame):
        scrollbar = tk.Scrollbar(frame, command=self.yview)
        scrollbar.pack(side='right', fill='y', expand=False)
        self.scrollbar = scrollbar
        self.config(yscrollcommand = self.on_scroll)   
            

class TextBox(tk.Text, TextUtils, PopMenu, TextSearch, TextTab, TextToken, TextUI):         
    def __init__(self, master, **kw):
        super().__init__(master, **kw)        
        self.config(padx=5)     
        self.config(undo=99) 
        self.config(exportselection=True)
        self.height = self.winfo_reqheight()
        #print(self.winfo_reqheight())
        self.tag_config('find', foreground='black', background='#999')
        self.vars = {}
        self.pre_text = ""
        self.line_count = 0
        self.msg = None
        self.statusbar = None
        self.init_popmenu()
        self.init_events()                        
        self.lexer = Python3Lexer()
        self.init_config()
        self.load_code_style()        
        self.tester = None
        self.after(100, self.check_update)
         
        
    def add_msgbox(self, frame):
        msg = Messagebox(frame)        
        statusbar = msg.add_statusbar()
        msg.pack(side='bottom', fill='both', expand=True)
        self.msg = msg
        msg.action = self.cmd_act 
        self.statusbar = statusbar     
        return msg
        
    def init_popmenu(self):
        cmds = [('Find', self.on_find_text),
                ('Goto Define', self.on_goto_define),
                ('Find in files', self.on_find_files),
                ('Help', self.on_search_help),
                ('Google Search', self.on_google_search),
                ('-'),
                ('Select All', self.on_select_all),
                ('Update', self.on_update_all),
                ('-'),
                ('Copy', self.on_copy),
                ('Paste', self.on_paste),
                ('-'),
                ('Add Tab', self.on_add_tab),
                ('Remove Tab', self.on_remove_tab),     
                ('-'),
                ('Exec', self.on_exec_cmd),   
                ]
        menu = self.add_popmenu(cmds)     

    def init_events(self):
        self.cmdlist = []
        for key in ['<F6>', '<Tab>', '<Control-period>']:
            self.bind(key, self.on_add_tab)
        for key in ['<F2>', '<Shift-Tab>', '<Control-comma>']:
            self.bind(key, self.on_remove_tab)   
        self.bind('<<check_cmd_list>>', self.check_cmdlist)
        self.bind('<KeyPress>', self.on_keydown)
        self.bind('<KeyRelease>', self.on_keyup)   
        self.bind('<Control-f>', self.on_find_text)
        self.bind('<KeyRelease-Return>', self.on_key_return)  
        self.bind('<Control-v>', self.on_key_v)     
        self.bind('<ButtonRelease-1>', self.on_click)
        self.bind_all('<<goto>>', self.on_goto)
        self.bind_all('<<gotoline>>', self.on_gotoline)
        
        self.click_time = 0
        
    def on_goto(self, event=None):
        arg = event.widget.getvar("<<goto>>")
        self.goto(arg)
        
    def on_gotoline(self, event=None):
        arg = event.widget.getvar("<<gotoline>>")
        self.goto(arg)        

    def on_click(self, event=None):       
        self.unpost_menu()
        if self.tag_ranges('find') :
            self.tag_remove('find', '1.0', 'end')
            
    def on_exec_cmd(self, event=None):        
        if self.tester == None:
            self.tester = ExecCmd(self, self.msg)
        text = self.get_text('sel')
        if text.strip() == '':
            text = self.get_text()
        
        self.tester.exec_text(text)

class SourceBox(TextBox, TextUI):
    def __init__(self, master, line=False, scroll=False):
        super().__init__(master)
        if line == True:
           self.add_linebar(master)   
        if scroll == True:   
           self.add_scrollbar(master)
  

class TextEditor(TextBox):
    def __init__(self, master, msgframe=None, **kw):
        super().__init__(master, **kw)         
        self.add_linebar(master)    
        if msgframe != None:
            self.add_msgbox(msgframe)
        self.add_scrollbar(master)
        
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
        

if __name__ == '__main__':   
    def test():
        from aui import App   
        app = App(title='Test TextEditor', size=(1500, 900))
        layout = app.get('layout')
        tree = app.add('filetree')
        msg = app.add('msg')
        frame = app.get('frame')
        textbox = TextEditor(frame)
        layout.add_HV(tree, frame, msg)
        textbox.msg = msg
        textbox.pack(fill='both', expand=True)
        #fn = '~/tmp/test.py'
        fn = '/home/athena/tmp/ver.py'
        
        tree.set_path('.')
        textbox.open(fn)
        
        msg.puts(textbox.filename)
        app.mainloop()     
    from mainframe import main
    test()

    

