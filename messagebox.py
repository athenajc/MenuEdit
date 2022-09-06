import os
import re
import sys
import time
import inspect
import subprocess
import tkinter as tk
import webbrowser

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

#-----------------------------------------------------------------------------------------
class TextObj(tk.Text):
    def __init__(self, master, **kw):
        tk.Text.__init__(self, master, **kw)
        self.vars = {}
        self.text = None       
        self.msg = self
        self.config(foreground='#121')
        self.config(background='#f5f5f3')    
        self.tag_config('bold', font='Mono 10 bold', background='#ddd')         
        
    def clear_all(self):
        self.tag_delete(self.tag_names())
        self.delete('0.0', 'end')              
        
    def select_none(self):
        self.tag_remove('sel', '0.0', 'end')
        
    def on_select_all(self):
        self.tag_add('sel', '0.0', 'end')
        
    def on_copy(self, event=None):
        self.clipboard_clear()
        text = self.get_text('sel')
        self.clipboard_append(text)   
        
    def on_paste(self, event=None):
        text = self.clipboard_get()
        self.insert('insert', text)
        
    def goto(self, p):
        if type(p) == int:
            p = str(p)
        elif type(p) == str:
           m = re.search('\d+', p)
           if m == None:
               return
           p = m.group(0)
        self.select_none()
        self.see(p + '.0')
        self.tag_add('sel', p + '.0', p + '.end')       
        
    def get_idx(self, i, j):  
        if j == 'e':
            return str(i) + '.end'
        return '%d.%d' % (i, j)
            
    def get_pos(self, idx):
        p = self.index(idx).split('.')
        return (int(p[0]), int(p[1]))
        
    def puts(self, *lst, end='\n'):
        lst1 = []
        for s in lst:
            lst1.append(str(s))
        text = ' '.join(lst1)
        self.insert('insert', text + end)
        self.see('end')
        
    def puts_tag(self, text, tag=None, head='', end='\n'):
        self.insert('insert', head)        
        idx1 = self.index('insert')
        self.insert('insert', text)        
        idx2 = self.index('insert')
        if tag != None:
            self.tag_add(tag, idx1, idx2)
        self.insert('insert', end)      
    
    def set_text(self, text):
        self.clear_all()
        self.text = text
        self.insert('insert', text)         
        self.linecount = text.count('\n')   
        
    def get_text(self, tag=None):
        if tag != None:
            p = self.tag_ranges(tag)
            if p == ():
                return ''
            idx1, idx2 = p
            return self.get(idx1, idx2)
        return self.get('0.0', 'end')                 
        
    def get_line_text(self, idx='insert'):
        if idx == 'prev' or idx == -1:
            i, j = self.get_pos('insert')
            if i > 1:
                i -= 1
        elif type(idx) == int:
            i = idx
        else:
            i, j = self.get_pos(idx)
        idx1 = self.get_idx(i, 0)
        idx2 = self.get_idx(i, 'e')
        return self.get(idx1, idx2)
        
    def select_line(self, idx):
        i, j = self.get_pos(idx)
        idx1 = self.get_idx(i, 0)
        idx2 = self.get_idx(i, 'e')
        self.tag_add('sel', idx1, idx2)
        self.see(idx)
        
    def get_word(self, idx='insert'):
        i, j = self.get_pos(idx)
        text = self.get_line_text(i)
        for m in re.finditer('\w+', text):
            if j >= m.start() and j <= m.end():
                return m.group(0)
        return ''

    def find_text(self, text=None, key=None):
        self.msg.clear_all()
        if key == None:
            key = self.get_word('insert')
        if text == None:
            text = self.get_text()  
        self.msg.puts('Find text: %s' % key) 
        lst = []
        i = 0               
        for line in text.splitlines():     
            i += 1       
            for m in re.finditer(key, line):
                s, e = m.start(), m.end()
                self.msg.puts_tag(line[s:e], 'bold', head =' %4d ' %i + line[:s], end=line[e:]+'\n')
                break        
        
    def delete_range(self, p):
        self.delete(p[0], p[1])
        
    def flush(self, text=''):        
        return
        
    def write(self, text):
        if '\n' in text:
            text = text.decode()
            for s in text.splitlines():
                self.puts(s, end='')
        self.puts('', end='\n')
        
    def fileno(self):
        return 1
 
    def list_str(self, lst):
        t = ' '
        text = ''
        n = (self.winfo_width() / 12)        
        for s in lst:
            t += s.ljust(20) + ' '
            if len(t) > n:
                text += t + '\n'
                t = ' '
        return text + t
        
    def put_list(self, lst):      
        self.puts(self.list_str(lst))
        
    def print_dct(self, dct):
        for s, v in dct.items():
            if v == []:
                continue
            self.puts_tag(s[0].upper()+s[1:], 'bold', head='\n', end='\n')
            self.put_list(v)             
           
class Messagebox(tk.Frame):
    def __init__(self, master, TextClass=TextObj, **kw):
        tk.Frame.__init__(self, master, **kw)         
        self.parent = master
        frame = tk.Frame(self)
        frame.pack(side='top', fill='both', expand=True)
        textobj = TextClass(frame)        
        textobj.pack(side='left', fill='both', expand=True)
        textobj.config(foreground='#121')
        textobj.config(background='#f5f5f3')    
        textobj.tag_config('bold', font='Mono 10 bold', background='#ddd')
        scrollbar = tk.Scrollbar(frame, command=textobj.yview)
        scrollbar.pack(side='left', fill='y', expand=False)
        textobj.scrollbar = scrollbar
        textobj['yscrollcommand'] = scrollbar.set 
        self.textobj = textobj
        self.textbox = None
        self.msg = textobj
        self.action = self.on_action
        menu = tk.Menu(self)
        menu.add_command(label='Goto', command=self.on_goto)
        menu.add_command(label='Find', command=self.on_find)
        menu.add_command(label='Google Search', command=self.on_google_search)
        menu.add_command(label='Clear', command=self.on_clear)
        menu.add_command(label='Select all', command=self.on_select_all)
        menu.add_command(label='Copy', command=self.on_copy)
        menu.add_command(label='Dir', command=self.cmd_dir)
        menu.add_command(label='Save', command=self.on_savefile)
        self.menu = menu
        textobj.bind('<ButtonRelease-1>', self.on_button1_up)   
        textobj.bind('<ButtonRelease-3>', self.on_button3_up) 
        textobj.bind('<KeyRelease>', self.on_keyup)  
        self.click_time = 0  
        self.cmds = {}
        self.bind_cmd('c,clear', self.cmd_clear)
        self.bind_cmd('cd', self.cmd_cd)
        self.bind_cmd('doc', self.cmd_doc)
        self.bind_cmd('dir', self.cmd_dir)
        self.bind_cmd('exec,run,test', self.cmd_exec)
        self.bind_cmd('execfile', self.cmd_execfile)        
        self.bind_cmd('f,find', self.cmd_find)
        self.bind_cmd('go,goto', self.cmd_goto)        
        self.bind_cmd('gr, findself,grep', self.cmd_grep)          
        self.bind_cmd('h,help', self.cmd_help)
        self.bind_cmd('ls', self.cmd_ls)
        self.bind_cmd('o,open', self.cmd_open)
        self.bind_cmd('re', self.cmd_re)
        self.bind_cmd('replace', self.cmd_replace)
        self.bind_cmd('time', self.cmd_time)
        self.locals = {}
        self.globals = {}
        self.cmdlist = ['dir self | grep scr\w+']
        
    def add_statusbar(self):
        self.textobj.config(height=5)
        statusbar = StatusBar(self, parent=None)
        statusbar.pack(side='top', fill='x', expand=False)    
        self.statusbar = statusbar
        return statusbar
        
    def get_textbox(self, action=None):
        tb = self.parent.textbox
        if tb == None:
            return None                     
        if action == None:
            return tb
        if action == 'text':
            return tb.get_text()
        elif action == 'seltext':
            return tb.get_text('sel')
        cmd = eval('tb.' + action[0])
        arg = action[1]
        return cmd(arg)
        
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
 
    def find_defines(self, text):
        textlines = text.splitlines()    
        for m in re.finditer('(?P<key>class|def)\s*(?P<name>\w+)\s*\(.*:', text):
            s, e = m.start(), m.end()     
            name = m.group('name')
            i = text[:s].count('\n')           
            line = textlines[i]
            j = line.find(name)                                
            j1 = j + len(name)
            self.puts_tag(name, 'bold', head =' %4d ' %(i+1) + line[:j], end=line[j1:]+'\n')
            
    def cmd_dir(self, arg=None):
        if arg == '' or arg == None:
            self.clear_all()
            text = self.get_textbox('text')
            self.find_defines(text)
            return
        print = self.puts
        if arg.strip() == '':
            arg = 'self'
        print('cmd_dir', arg)
        obj = eval(arg)
        print(obj)
        lst = dir(obj)
        dct = {}
        for s in lst:
            c = s[0]
            if not c in dct:
                dct[c] = [s]
            else:
                dct[c].append(s)
        self.textobj.print_dct(dct)
        
    def cmd_doc(self, arg):
        if arg == '':
            arg = 'self'
        self.puts(arg)
        obj = eval(arg)
        self.puts(inspect.getdoc(obj))
        
    def exec_file(self, filename):
        sys.stdout=self.textobj
        sys.stderr=self.textobj
        #os.execv('/bin/bash', ['/bin/bash', filename])  
        if filename.find('.py') > 0:
            cmd = 'python3'
        else:
            cmd = '/bin/bash'
        process = subprocess.Popen([cmd, filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        for s in out.splitlines():
            self.puts(s)
            
    def cmd_execfile(self, arg):
        self.exec_file(arg)
         
    def cmd_exec(self, arg):
        if arg == '':
            text = self.get_textbox().get_text()
            arg = text.replace('\n', '\n    ')       
        elif arg.find('.py') > 0:
            return self.exec_file(arg)     
        text = 'def test_1():\n    ' + arg + '\ntest_1()'
        exec(text)  
        
    def cmd_find(self, arg):        
        if self.textbox == None:
            self.puts('No get_textbox')
            return
        text = self.textbox.get_text()
        self.find_text(text, arg)
            
    def cmd_goto(self, arg):
        #self.puts('cmd_go arg=', [arg])
        self.action('goto', arg)        
    
    def find_text(self, text, key):
        self.textobj.find_text(text, key) 
                
    def cmd_grep(self, arg):    
        text = self.get_text()
        self.clear_all()
        self.find_text(text, arg)

    def cmd_help(self, arg):
        key = None
        self.clear_all()        
        if ' ' in arg:
            args = arg.split(' ', 1)
            arg = args[0]
            key = args[1]
        a = arg.split('.', 1)[0]
        if a == 'ttk':
            arg = arg.replace('ttk', 'tkinter.ttk', 1) 
            m = 'import tkinter\n'
        elif a == 'tk':
            arg = arg.replace('tk', 'tkinter', 1)       
            m = 'import tkinter\n' 
        elif key == 'm':
            m = 'import %s\n' % arg 
        else:
            m = ''
        sys.stdout = self
        self.puts(m, arg)    
        exec(m + 'help(%s)' % arg)           
        if key != None and key != 'm':
            self.cmd_grep(key)
        
    def cmd_ls(self, arg=''):
        if arg == '':
            arg = '.'
        lst = os.listdir(arg)
        lst.sort()
        self.textobj.put_list(lst)
        
    def cmd_open(self, arg=None):
        self.action('open', arg)  
               
    def cmd_others(self, text, cmd, arg=None):        
        if ' ' in arg:
            args = arg.split(' ')
        elif ',' in arg:
            args = arg.split(',')
        else:
            args = [arg]
        self.puts('cmd=', cmd, 'arg=', arg, 'args=', args)
        output = self.get_textbox(['on_button_action', cmd, args])                       
        self.puts(output)
        
    def cmd_re(self, arg):
        text = self.get_textbox(['get_text', ''])
                
    def cmd_replace(self, arg):
        self.puts('cmd_replace', arg)
        if not ' with ' in arg:
            self.puts(arg, 'Command Error, miss \' with \'')
            return
        args = arg.split(' with ')
        src = args[0].strip()
        dst = args[1].strip()
        self.puts(src, dst)
        textbox = self.get_textbox()
        text = textbox.get_text()
        text = text.replace(src, dst)
        textbox.set_text(text)
        self.find_text(text, dst)
        
    def cmd_time(self, arg):
        self.put_time()
            
    def proc_cmd(self, text):
        if ' ' in text:
            cmds = text.split(' ', 1)
        else:
            cmds = [text, '']
        arg = cmds[-1]
        cmd = cmds[0].lower()
        if cmd in self.cmds:            
            self.cmds[cmd](arg)
        else:
            self.cmd_others(text, cmd, arg)     
            
    def on_action(self, cmd, arg):     
        self.puts('no parent action binded')

    def on_clear(self):
        self.clear_all()        

    def on_command(self, text):
        text = text.strip()
        self.cmdlist.append(text)
        self.proc_cmd(text)       
   
    def on_find(self):
        text = self.textobj.get_text('sel')
        self.cmd_find(text)
        
    def on_google_search(self):
        base_url = "http://www.google.com/search?q="
        query = self.textobj.get_text('sel')
        webbrowser.open(base_url + query)
        
    def on_doubleclick(self):
        self.on_goto()                             
           
    def on_goto(self):        
        idx = self.textobj.index('insert')        
        text = self.get_line_text(idx).strip()  
        m = None
        if '.py\"' in text:
           m = re.search('\"[\w\/\s\.\-\_\d]+\"', text)      
           if m != None:            
              filename = m.group(0).replace('\"', '')
              print(filename)
              self.action('gotofile', filename) 
              text = text.split('.py', 1)[1]           
        elif '.py' in text:      
           m = re.match('[\w\/\s\.\-\_\d]+\:', text)      
           if m != None:            
              filename = m.group(0).replace(':', '')
              self.action('gotofile', filename) 
              text = text.split('.py', 1)[1]  
        elif 'not found' in text:
            s = text.replace(' not found', '').strip()
            self.cmd_find(s)
            return        
            
        m1 = re.search('(?P<line>\d+)', text) 
        if m1 != None:           
           if m != None:
              self.action('gotoline', m1.group('line'))
           else:   
              self.action('goto', m1.group('line'))                  
        #self.textobj.select_line(idx)    
        
    def on_keyup(self, event):
        if event.keysym  == 'Return':           
            text = self.get_line_text('prev')
            self.on_command(text)
            self.textobj.see('end')    

    def on_select_all(self):
        self.textobj(['tag_add', ('sel', '0.0', 'end')])

    def on_copy(self, event=None):
        self.textobj.on_copy(event)

    def on_button1_up(self, event):
        self.menu.unpost()
        if event.time - self.click_time < 300:
            self.on_doubleclick()
        self.click_time = event.time        
        
    def on_button3_up(self, event):
        x, y = event.x, event.y   
        x1 = self.winfo_rootx()     
        y1 = self.winfo_rooty()
        self.menu.post(x + x1, y + y1)
        
    def on_savefile(self, event=None):
        self.fwrite('tmp.txt')
                    
    def fwrite(self, filename):
        text = self.textobj.get_text()
        with open(filename, 'w') as f:
            f.write(text)
            f.close()
            self.puts(filename + ' saved.')
            
    def clear_all(self, text=None):
        self.textobj.delete('0.0', 'end')
        if text == 'time':
            self.put_time()
        elif text != None:
            self.puts(text)
        
    def get_text(self, tag=None):
        return self.textobj.get_text(idx) 
        
    def get_line_text(self, idx):
        return self.textobj.get_line_text(idx)        
        
    def puts_tag(self, text, tag=None, head='', end='\n'):
        self.textobj.puts_tag(text, tag, head, end)
        
    def put_time(self):
        self.puts(self.time())
        
    def time(self):
        return time.ctime().split(' ')[3]
        
    def puts(self, *text, end='\n'):
        for s in text:
            self.textobj.insert('end', str(s) + ' ')
        self.textobj.insert('end', end)
        self.textobj.see('end')        
        
    def puts_key_str(self, text, key, tag):
        p = text.split(key)
        last = p.pop()
        for t in p:
            self.puts(t, end='')
            self.puts_tag(key, tag=tag, end='')  
        self.puts(last, end='\n')

    def write(self, text):
        if text.strip() == '':
            return
        self.textobj.insert('end', str(text))
        
    def flush(self, text=''):
        return
        #self.textobj.insert('end', text)
     
    def fileno(self):
        return 1

#----------------------------------------------------------------------------------------------   
if __name__ == '__main__':   
    class TestFrame(tk.Frame):
        def __init__(self, master, cnf={}, **kw):
            tk.Frame.__init__(self, master)   
            master.mainframe = self
            msg = Messagebox(self)
            msg.place(x=0, rely=0.5, relwidth=1, relheight=0.5)               
            frame = tk.Frame(self)
            frame.place(x=0, rely=0, relwidth=1, relheight=0.5)        
          
            textbox = TextObj(frame)
            textbox.pack(side='left', fill='both', expand=True)
            scrollbar = tk.Scrollbar(frame, command=textbox.yview)
            scrollbar.pack(side='left', fill='y', expand=False)
            textbox.scrollbar = scrollbar
            textbox['yscrollcommand'] = scrollbar.set             
            msg.add_statusbar()        
            self.textbox = textbox
            msg.textbox = textbox
            self.msg = msg            
            textbox.msg = msg
            msg.parent = self
            msg.action = self.on_msg_action
            sys.stdout = msg
            sys.stderr = msg 
            
        def open_file(self, filename):   
            self.filename = filename
            filename = os.path.realpath(filename)      
            with open(filename, 'r') as f:
                text = f.read()
                f.close()
            self.textbox.set_text(text)
            self.textbox.goto(1)
            self.textbox.filename = filename    
            self.winfo_toplevel().title('MsgTest      ' + filename)
            self.msg.puts(filename + ' opened')
        
        def on_msg_action(self, cmd, arg):
            print('Receive ', cmd, arg)
            if cmd == 'open':
                self.open_file(arg)
            
    def main():
        root = tk.Tk()
        root.title('Messagebox tester')
        root.geometry('700x800')
        frame = TestFrame(root)
        frame.pack(fill='both', expand=True)        
        frame.mainloop()       

    main()



