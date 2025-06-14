import os
import re
import sys
import time
import inspect
import subprocess
import tkinter as tk
import webbrowser
import numpy as np
from aui.TextObj import Text
from aui.Menu import PopMenu
from fileio import *


class StatusBar(tk.Frame):
    def __init__(self, master, parent=None, **kw):
        tk.Frame.__init__(self, master, **kw)     
        self.parent = parent
        self.vars = {}    
        if parent != None:
            self.add_search_button()
        frame2 = tk.Frame(self, relief='sunk', bd=2)
        frame2.pack(side='left', fill='both', expand=True)
        self.textvar = tk.StringVar(value='test')
        self.label = tk.Label(frame2, textvariable=self.textvar, anchor='nw')
        self.label.pack(fill='both', expand=True)     
                
    def add_search_button(self):
        frame1 = tk.Frame(self, relief='sunk', bd=2)
        frame1.pack(side='left', fill='y')        
        self.entry = tk.Entry(frame1)
        self.entry.pack(side='left', fill='y', pady=5)
        button = tk.Button(frame1, text='Search')
        button.pack(side='left', fill='y',  pady=5)
        self.entry1 = tk.Entry(frame1)
        self.entry1.pack(side='left', fill='y', pady=5)
        button1 = tk.Button(frame1, text='Replace')
        button1.pack(side='left', fill='y', pady=5)     
        button.bind('<Button-1>', self.on_button_search)
        button1.bind('<Button-1>', self.on_button_replace)        
        
    def on_button_search(self, event):
        if self.parent == None:
            return
        key = self.entry.get()
        self.parent.call('find', key)
        return
        
    def on_button_replace(self, event):
        if self.parent == None:
            return        
        key = self.entry.get()
        replace = self.entry1.get()
        self.parent.call('replace', (key, replace))
        return
        
    def set_var(self, item, value):
        self.vars[item] = str(value)
        text = ''
        for s, v in self.vars.items():
            text += s + ' : ' + v + '    '
        self.textvar.set(text)
        
class Cmds():    
    def bind_cmd(self, key, action):
        for s in key.split(','):
            s = s.strip()
            if s == '':
                continue
            self.cmds[s] = action
        
    def cmd_cd(self, arg):
        if arg == '':
            self.puts(os.getcwd())
        else:
            path = os.path.realpath(arg)
            os.chdir(path)
            self.puts(os.getcwd())
                    
    def cmd_clear(self, arg=None):
        self.clear_all()      
         
    def cmd_test(self, arg):
        target = self.get_textbox()
        from aui import TestFrame        
        frame = TestFrame(target.filename)  
        
    def cmd_find(self, arg): 
        target = self.get_textbox()       
        if target == None:
            self.puts('No textbox')
            return
        text = target.get_text()
        self.find_in_text(target.filename, text, arg)
        self.update_tag(key=arg)
            
    def cmd_goto(self, arg):
        if self.textbox == None:
            self.puts('No get_textbox')
            return
        self.textbox.goto(arg)      
                
    def cmd_grep(self, arg):    
        text = self.get_text()
        self.clear_all()
        self.find_text(text, arg)

    def cmd_ls(self, arg=''):
        if arg == '':
            arg = '.'
        lst = os.listdir(arg)
        lst.sort()
        self.put_list(lst)
        
    def cmd_open(self, arg=None):
        self.action('open', arg)  
        
    def cmd_db(self, arg=None):                    
        from aui import TopFrame
        from DB.dbEditor import CodeFrame
        frame = TopFrame()    
        panel = frame.add('panel')
        panel.pack(fill='both', expand=True)   
        frame1 = CodeFrame(panel, arg)
        frame1.pack(fill='both', expand=True)         
            
    def cmd_run(self, arg=None):                    
        if arg == 'db':
            self.cmd_db()
            return
        from aui import TestFrame            
        frame = TestFrame(arg)       
        
    def re_get_prefix(self, text, prefix='class'):
        if text == '' or text == None:
           return
        a = re.findall(r'(?<=%s)\s+[\w\,]+'%prefix, text)        
        b = ','.join(a)
        self.puts(b)
        
    def cmd_get(self, cmd):
        text = self.get_editor_text()
        if cmd in ['class', 'def', 'import', 'if', 'from']:           
            return self.re_get_prefix(text, cmd)
        else:
            import DB
            res = DB.get(cmd)
            self.puts(res)
                    
    def cmd_exec(self, cmd, args):
        name, arg = args.split('(', 1)
        arg = arg.strip()[0:-1]
        if cmd == 'db':            
            import DB            
            func = eval('DB.' + name)
            res = func(eval(arg))
            self.puts(cmd, arg, res)
        elif cmd == 're':
            text = self.get_editor_text()
            if text == '' or text == None:
                return
            func = eval('re.' + name)            
            res = func(eval(arg), text)
            self.puts(cmd, arg, res)
        elif cmd == 'np':            
            func = eval('np.' + name)
            res = eval(cmd(arg))
            self.puts(cmd, arg, res)
            

class Messagebox(Text, PopMenu, Cmds):
    def __init__(self, master, **kw):        
        super().__init__(master, **kw)       
        self.root = master.winfo_toplevel()  
        self.pack(side='top', fill='both', expand=True)
        #self.init_dark_config()
        self.frame = master
        self.textbox = None
        self.msg = self
        self.action = self.on_action
        self.add_menu()
        self.vars = {}
        self.click_time = 0
        self.tester = None
        self.bind('<ButtonRelease-1>', self.on_button1_up)   
        self.bind('<KeyRelease>', self.on_keyup)  
        self.cmds = {}
        self.bind_cmd('clear', self.cmd_clear)        
        self.bind_cmd('test', self.cmd_test)          
        self.bind_cmd('goto', self.cmd_goto)    
        self.bind_cmd('cd', self.cmd_cd)    
        self.bind_cmd('ls', self.cmd_ls)
        self.bind_cmd('open', self.cmd_open)
        self.bind_cmd('find', self.cmd_find)
        self.bind_cmd('run', self.cmd_run)
        self.bind_cmd('db', self.cmd_db)
        self.bind_cmd('get', self.cmd_get)
        #self.pack(fill='both', expand=True)  
        
    def pprint(self, data):
        import pprint
        self.puts(pprint.pformat(data))
        
    def add_menu(self):
        cmds = [('Goto', self.on_goto),
                ('Find in Editor', self.on_find_in_editer),
                ('Google Search', self.on_google_search),
                ('-'),
                ('Select All', self.on_select_all),
                ('Update tag', self.update_tag),
                ('-'),
                ('Copy', self.on_copy),
                ('Clear', self.clear_all),
                ('-'),
                ('Save', self.on_savefile)                
                ]
        self.add_popmenu(cmds)  
        
    def add_statusbar(self):
        #self.config(height=5)
        statusbar = StatusBar(self.frame, parent=None)
        statusbar.pack(side='bottom', fill='x', expand=False)    
        self.statusbar = statusbar
        return statusbar
        
    def get_textbox(self, action=None):
        if self.textbox != None:
            return self.textbox
        if hasattr(self, 'root') == False:
            self.root = self.winfo_toplevel()
        if hasattr(self.root, 'textbox') == False:
            return None
        self.textbox = self.root.textbox      
        return self.textbox      
        
    def get_editor_text(self):
        target = self.get_textbox()       
        if target == None:
            self.puts('No textbox')
            return ''
        text = target.get_text()
        return text
            
    def on_action(self, cmd, arg):     
        #self.puts('no parent action binded')
        textbox = self.get_textbox()
        event = "<<%s>>" % cmd
        if textbox == None:
            textbox = self
        textbox.setvar(event, arg)
        textbox.event_generate(event)  

    def on_find_in_editer(self):
        text = self.get_text('sel')
        self.cmd_find(text)
        
    def on_doubleclick(self, event=None):
        self.on_goto()                             
           
    def on_goto(self):    
        if self.get_textbox() == None:
            return    
        idx = self.index('insert')        
        text = self.get_line_text(idx).strip()  
        m = None
        if '.py' in text:      
            fn = text.split('.py')[0] + '.py'
        else:
            fn = None    
            
        if fn != None and '.py\"' in text:
           m = re.search(r'\"[\~\w\/\s\.\-\_\d]+\"', text)      
           if m != None:            
              filename = m.group(0).replace('\"', '')
              self.action('gotofile', filename) 
              text = text.split('.py', 1)[1]           
        elif fn != None:      
           m = re.findall(r'[\~\w\/\s\.\-\_\d]+', fn)      
           if m != []:            
              filename = m[-1] 
              self.action('gotofile', filename) 
              text = text.split('.py', 1)[1]             
            
        m1 = re.search(r'(?P<line>\d+)', text) 
        if m1 != None:  
            n = m1.group('line')
            if m != None:
                self.action('gotoline', n)
            else:   
                self.action('goto', n)                  
        #self.select_line(idx)    
        
    def on_keyup(self, event):
        if event.keysym  == 'Return':           
            text = self.get_line_text('prev')
            self.on_command(text)
            self.see('end')    

    def on_button1_up(self, event):        
        self.unpost_menu()
        if event.time - self.click_time < 300:
            self.on_doubleclick()
        self.click_time = event.time    
        
    def on_savefile(self, event=None):
        fwrite('/home/athena/tmp/tmp.txt', self.get_text())

    def on_command(self, text):
        text = text.strip()
        if not ' ' in text:
            cmd, arg = text, ''
        else:
            cmd, arg = text.split(' ', 1)
        if cmd in self.cmds:
            self.cmds[cmd](arg)
            return
        if '.' in cmd:
            cmd, arg = cmd.split('.', 1)
            if cmd in ['db', 'np', 're']:
                return self.cmd_exec(cmd, arg)
        if self.tester == None:
            from runfile import ExecCmd        
            self.tester = ExecCmd(self.get_textbox(), self)
        self.tester.exec_text(text)  


        
class MsgBox(Messagebox):
    def __init__(self, master, **kw):
        Messagebox.__init__(self, master, **kw)
        pass
        
#----------------------------------------------------------------------------------------------   
if __name__ == '__main__':                  
    from aui import App   
    frame = App(title='Test Messagebox', size=(1500,860))
    frame.add_set1()
    frame.textbox.open(__file__)
    frame.filetree.set_path('.')
    frame.mainloop()




