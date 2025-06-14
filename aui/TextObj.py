import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import re
import os
import webbrowser
from fileio import *
from pprint import pprint, pformat

def rgbToHex(rgb):
    return "#%02x%02x%02x" % rgb
    

class TextLinebar(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, **kw)  
        self.config(background='#ccc')
        
        n = 50
        label0 = tk.Label(self, text='\n'*n, background='#ccc', width=5, anchor='nw')
        label0.pack(side='left', fill='y', expand='False')        
        self.textvar = tk.StringVar()
        label = tk.Label(self, background='#ccc', anchor='ne')
        label.place(x=1,y=0)    
        label.config(textvariable=self.textvar) 
        label.config(font='Mono 10', foreground='#333')
        self.label = label 
        self.set_range(1, n)
            
    def scroll_set(self, i0, i1, bboxcmd):               
        if i1 == 0:
            return      
        bbox = bboxcmd(str(i0) + '.0')  
        if bbox == None:
            return       
        y0 = bbox[1] 
        self.label.place(x=0, y=y0-2)        
        text = ''       
        top = i0                    
        if i1 - i0 < 40:
            i1 = i0 + 40
        for i in range(i0, i1+1):
             bbox = bboxcmd(str(i+1) + '.0')
             if bbox != None:                 
                 y = bbox[1]     
                 h = int((y - y0)/bbox[3])
                 if h == 0:
                     h = 1
                 else:
                     text += '%5d '% i + '\n' * h
                 y0 = y
             else:
                 text += '%5d '% i + '\n'
        self.textvar.set(text)
        
    def set_range(self, i0, i1=None):
        text = ''          
        for i in range(i0, i1):
            text += '%5d \n' % i
        self.textvar.set(text)
        
class PopMenu():
    def add_popmenu(self, cmds=[]):
        menu = tk.Menu(self)
        self.menu = menu
        for p in cmds:
            if p[0] == '-':
                menu.add_separator()
            else:
                menu.add_command(label=p[0], command=p[1])         
        self.menu = menu   
        self.bind('<ButtonRelease-1>', self.unpost_menu)
        self.bind('<ButtonRelease-3>', self.post_menu)    
        return menu
        
    def add_menu_cmd(self, label, cmd):
        self.menu.add_command(label=label, command=cmd)          

    def unpost_menu(self, event=None):
        self.menu.unpost()
        
    def post_menu(self, event=None):
        x, y = event.x, event.y   
        x1 = event.widget.winfo_rootx()     
        y1 = event.widget.winfo_rooty()
        self.menu.post(x + x1, y + y1)
        

class TextSearch():
    def find_in_text(self, path, text, key):
        lst = find_in_text(path, text, key)
        if lst == []:            
            return lst
        if path != '':    
           self.msg.puts(path)
        for i, j, s in lst:
            self.msg.puts('    ', '%10s  ' % str((i, j)), s)
        self.msg.puts('')        
        return lst             
        
    def find_in_path(self, path, key):
        sep = os.sep
        if sep in path:
            head, tail = path.split(sep, 1)
            if head in pdct:
                path = pdct.get(head) + sep + tail
        elif path in pdct:
           path = pdct.get(path)           
        path = realpath(path)
        files = []   
        
        files = get_files(path) 
        #self.msg.puts('Search in Files %d' % len(files))        
        if files == []:
            return
        if path[-1] != sep:
            path += sep   
        msg = self.msg    
        endline = str(msg.get_line_index('end')-1) + '.'
        n = 0
        for fn1 in files:   
            fn = path + fn1  
            if not os.path.exists(fn):
                continue
            msg.insert(endline+'0', fn)
            msg.update()
            text = fread(fn)
            lst = self.find_in_text(fn, text, key)
            
            if lst == []:
                msg.delete(endline+'0', endline+'end')
            else:
                msg.puts()
                n += len(lst)
                endline = str(msg.get_line_index('end')-1) + '.'
        return n        
            
    def find_in_files(self, pathlist, key):        
        self.msg.clear_all()   
        self.msg.puts(pathlist)  
        n = 0        
        for path in pathlist:
            path = get_path(path)
            self.msg.puts(path)
            n += self.find_in_path(path, key)
        self.msg.puts(f'{n} Found')
            
    def on_open_url(self, event=None):
        idx, url = self.get_selected_word()
        if url == '' or url == None:
            return
        webbrowser.open(url)
            
    def on_google_search(self, event=None):
        idx, key = self.get_selected_word()
        if key == '' or key == None:
            return
        base_url = "http://www.google.com/search?q="
        webbrowser.open(base_url + key)
        
class TextTag():    
    def init_config(self):    
        monofont = ('Mono', 10)     
        self.font = monofont  
        self.color = '#121'
        self.config(font=monofont)
        #self.config(padx=5)
        self.config(foreground=self.color)
        self.config(background='#f5f5f3')        
        self.config(undo=99)          
        self.config(exportselection=True)
        self.vars = {}

        bold = ('bold')
        self.tag_config('key', font=bold, foreground='#338')
        self.tag_config('class', font=bold, foreground='#338')
        self.tag_config('classname', font=bold, foreground='#383')
        self.tag_config('str1', foreground='#a73')
        self.tag_config('str2', font=bold, foreground='#a73')
        self.tag_config('int', font=bold, foreground='#383')
        self.tag_config('op',  foreground='gray')
        self.tag_config('self',  foreground='#333')
        self.tag_config('comments',  foreground='#789')
        self.tag_config('selected',  background='lightgray')
        self.tag_config('find', font=bold, foreground='#111', background='#a5a5a3')
        self.key_tagnames = ['key', 'class', 'classname', 'str1', 'str2', 
                             'int', 'op', 'self', 'comments', 'find']
        
    def init_dark_config(self):
        monofont = ('Mono', 10)
        self.color = '#d8dee9'
        self.config(font=monofont)
        #self.config(padx=5)
        self.config(foreground='#d8dee9')
        self.config(background='#323c44')        
        self.config(undo=99)          
        self.config(exportselection=True)
        self.config(insertbackground="#f0a050")
        self.config(selectbackground="#000", selectforeground="#000")
        self.tag_config('insert', background="#343434")
        self.tag_config('sel', background ='#202327',  foreground='#777777')
        self.tag_config('find', foreground='black', background='#999')
        self.tag_config('Q3', foreground='#99c794')
        
        self.vars = {}
        bold = (monofont[0], monofont[1], 'bold')
        self.tag_config('key', foreground='#c695c6')
        self.tag_config('class', foreground='#9695d6')
        self.tag_config('classname', foreground='#f9ae58')
        self.tag_config('str1', foreground='#99c794')
        self.tag_config('str2', foreground='#99c794')
        self.tag_config('int',  foreground='#f9ae58')
        self.tag_config('op',  foreground='#5fb4b4')
        self.tag_config('self',  foreground='#e37373')
        self.tag_config('comments',  foreground='#a6acb9')
        self.tag_config('selected',  background='#f9ae58')
        self.tag_config('find',  background='yellow')

        self.key_tagnames = ['key', 'class', 'classname', 'str1', 'str2', 'int', 'op', 'self', 'comments'
                           'h1', 'h2', 'h3', 'hide'] 
        
    def add_linebar(self, frame):
        self.linebar = TextLinebar(frame)
        self.linebar.pack(side='left', fill='y', expand=False) 
        self.pos = self.dlineinfo('@0,0')
        self.configure(yscrollcommand=self.on_scroll)   
        
    def init_pattern(self):
        keys = 'from|import|def|class|if|else|elif|for|in|then|dict|list|continue|return'
        keys += '|None|True|False|while|break|pass|with|as|try|except|not|or|and|do|const|local'
        p0 = r'(?P<class>class)\s+(?P<classname>\w+)'
        p1 = r'|(?P<str1>\'[^\'\n]*\')|(?P<str2>\"[^\"\n]*\")'        
        p2 = r'|(?<![\w])(?P<int>\d+)|(?P<op>[\=\+\-\*\/\(\)\.\%])|(?P<self>self)'       
        p3 = r'|(?<![\w])(?P<key>%s)(?![\w])' % keys     
        p4 = r'|(?P<comments>#.*)'     
        self.pattern = re.compile(p0 + p1 + p2 + p3 + p4)          

    def split_tokens(self, text):    
        lst = [] 
        for m in re.finditer(self.pattern, text):
            i, j = m.start(), m.end()            
            for tag, s in m.groupdict().items():
                if s != None:                           
                    lst.append((s, text.find(s, i), tag))  
        return lst
                    
    def remove_tags(self, idx1, idx2):        
        for s in self.key_tagnames:
            self.tag_remove(s, idx1, idx2)

    def add_tag_list(self, i, lst):
        head = str(i) + '.'
        for p in lst:        
            s, j, tag = p
            idx1 = head + str(j)
            idx2 = head + str(j+len(s))
            self.tag_add(tag, idx1, idx2)
        
    def tag_line(self, i, text):
        self.remove_tags('%d.0'%i, '%d.end'%i)      
        s = text.strip()
        if s == '':
            return
        elif s[0] == '#':      
            lst = [(text, 0, 'comments')]  
        else:            
            lst = self.split_tokens(text)
        if lst != []:
            self.add_tag_list(i, lst)
        return lst
        
    def tag_key(self, key, tag='bold', text=None):
        start = '1.0'
        pend = '+%dc' % len(key)
        if text == None:
            text = self.get_text()
        for s in re.findall(key, text):                    
            pos = self.search(key, start)  
            self.tag_add(tag, pos, pos + pend)
            start = pos + pend
        self.tag_raise(tag)    
        
    def update_tag(self, key=None):   
        if self.pattern == None:
            return            
        i = 1    
        text = self.get_text()
        for line in text.splitlines():           
            self.tag_line(i, line)       
            i += 1
        if key != None:
            self.tag_key(key, 'find', text=text)
        self.pre_text = text         
    
    def set_text(self, text):
        self.clear_all()
        self.text = text
        self.insert('insert', text)         
        self.linecount = text.count('\n')   
        self.update_tag()        
        
    def select_line(self, idx):
        i, j = self.get_pos(idx)
        idx1 = self.get_idx(i, 0)
        idx2 = self.get_idx(i, 'e')
        self.tag_add('sel', idx1, idx2)
        self.see(idx)      


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

class TextUtils(PopMenu, TextSearch, TextTag, TextTab):    
    def set_font_size(self, n):
        self.config(font=(self.font[0], n))
        
    def on_goto(self, event=None):
        arg = event.widget.getvar("<<goto>>")
        self.goto(arg)
        
    def on_gotoline(self, event=None):
        arg = event.widget.getvar("<<gotoline>>")
        self.goto(arg)        
  
    def on_update_text(self, event=None):
        #self.update_set('check')
        pass
        
    def on_savefile(self, event=None):
        if self.filename != None:
           fwrite(self.filename, self.get_text())
        
    def on_find_text(self, event=None):
        self.msg.clear_all()
        self.event_generate("<<Text Find>>")
        idx, key = self.get_selected_word()
        if key == '':
            return
        filepath = self.filename
        text = self.get_text()
        self.find_in_text(filepath, text, key)
        self.msg.update_tag(key=key)
        
    def _add_pop_menu_(self):
        cmds = [('Find', self.on_find_text),
                ('-'),
                ('Google search', self.on_google_search),
                ('Open Url', self.on_open_url),
                ('-'),
                ('Save', self.on_savefile),                
               ]
        return self.add_popmenu(cmds)  
        
    def ___button1_up___(self, event):
        if event.time - self.click_time < 300:
            self.event_generate("<<DoubleClick>>")
        self.click_time = event.time 

    def clear_all(self):
        self.tag_delete(self.tag_names())
        self.delete('1.0', 'end')              
        
    def select_none(self):
        self.tag_remove('sel', '1.0', 'end')
        
    def on_select_all(self):
        self.tag_add('sel', '1.0', 'end')
        
    def on_copy(self, event=None):
        self.clipboard_clear()
        text = self.get_text('sel')
        self.clipboard_append(text)   
        
    def on_paste(self, event=None):
        text = self.clipboard_get()
        self.puts(text)
        
    def see_line(self, i):
        self.tag_remove('sel', '1.0', 'end')
        i = self.get_line_index(i)               
        p = str(i)
        self.see(p + '.0') 
        self.tag_add('sel', p + '.0', p + '.end')                  
         
    def goto(self, arg, name=None, key=None):        
        self.see_line(arg)    
        
    def goto_pos(self, pos):
        self.see(pos)     
        
    def get_idx(self, i, j):  
        if j == 'e':
            return str(i) + '.end'
        return '%d.%d' % (i, j)
            
    def get_pos(self, idx):
        p = str(self.index(idx)).split('.')
        return (int(p[0]), int(p[1]))
        
    def puts(self, *lst, end='\n'):
        text = ''
        for s in lst:
            text += str(s) + ' '
        if len(text) > self.limit:
            text = text[0:self.limit]    
        self.insert('end', text + end)
        
    def puts_tag(self, text, tag=None, head='', end='\n'):
        self.insert('end', head)        
        idx1 = self.index('end')
        if len(text) > 1024:
            text = text[0:1023]   
        self.insert('end', text)        
        idx2 = self.index('end')
        if tag != None:
            self.tag_add(tag, idx1, idx2)
        self.insert('end', end)     

    def list_str(self, lst):
        t = ' '
        text = ''
        if hasattr(self, 'width'):
            w = self.width
        else:    
            w = self.winfo_width()
        n = int(w / 20)
        for s in lst:
            t += s.ljust(20) + ' '
            if len(t) > n:
                text += t + '\n'
                t = ' '
        return text + t
        
    def put_list(self, lst, bychar=False):
        if bychar == False:      
            self.puts(self.list_str(lst))
        else:
            dct = {}
            lst1 = []
            for s in lst:
                c = s[0].lower()
                if not c in lst1:
                    lst1.append(c)
            lst1.sort()
            for c in lst1:
                dct[c] = []
            for s in lst:
                c = s[0].lower()
                dct[c].append(s)
            self.print_dct(dct)
        
    def print_dct(self, dct):
        if dct == None:
            return
        for s, v in dct.items():
            if v == []:
                continue
            self.puts_tag(s[0].upper()+s[1:], 'bold', head='\n', end='\n')
            self.put_list(v)  

    def tag_block(self):
        text = self.get_text()
        if not '' in text:
            return
        lst = re.findall(r'', text)
        start = '1.0'
        for s in lst:
            start = self.search(s, start)       
            end = start + '+2c'                 
            self.replace(start, end, '')
            self.tag_add('bold', start+'-1c', start)   
        
    def get_text(self, tag=None):
        if tag != None:
            p = self.tag_ranges(tag)
            if p == ():
                return ''
            idx1, idx2 = p
            return self.get(idx1, idx2)
        return self.get('1.0', 'end -1c')                 
        
    def get_line_index(self, idx='current'):
        if type(idx) == int:
            return idx
        if type(idx) == str:
            if re.fullmatch(r'\d+', idx) != None:
               return int(idx)
            idx = self.index(idx)
        idx = self.index(idx).split('.')[0]
        return int(idx)
        
    def get_line_text(self, idx=None):
        if idx == 'prev':
            idx = self.get_line_index('insert') - 1
            
        if type(idx) == int:
            p = str(idx)
            idx1 = p + '.0'
            idx2 = p + '.end'
        else:
            idx1 = self.index(idx + ' linestart')        
            idx2 = self.index(idx + ' lineend')         
        return self.get(idx1, idx2)
        
    def get_word(self, idx='insert'):
        i, j = self.get_pos(idx)
        text = self.get_line_text(i)
        for m in re.finditer(r'[\w\.]+', text):
            if j >= m.start() and j <= m.end():
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
        
    def delete_range(self, p):
        self.delete(p[0], p[1])
        
    def add_widget(self, index, widget):
        self.window_create(index, window=widget)
        
    def add_button(self, index, text, command=None, **kw):        
        button = tk.Button(self, text=text, command=command, **kw)
        self.window_create(index, window=button)
        end = self.index('end')
        self.tag_add('button', index, end)
        button.range = (index, end)
        return button
        
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
               
    def get_current(self):
        i = self.get_line_index('insert')
        j = self.get_line_index('current') 
        return [i, j]
        
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
            
    def update_add(self, flag='range'):
        self.update_tag()
            
    def flush(self, text=''):
        return
        
    def write(self, text):
        if text.strip() == '':
            return
        self.insert('insert', str(text))
        
    def open(self, filename):        
        filename = realpath(filename)      
        self.filename = filename
        text = ''
        with open(filename, 'r') as f:
            text = f.read()
            f.close()
            self.set_text(text)
        return text
        
    def get_font_width(self):
        font = self.font
        family, size = font
        
        font = tkfont.Font(family=family, size=size)
        self.font_width = font.measure("1234567890") //10
        
    def init_all(self):
        self.vars = {}
        self.font = ('Mono', 10) 
        self.limit = 32768
        self.text = None       
        self.pattern = None
        self.config(foreground='#121')
        self.config(background='#f5f5f3')    
        self.config(padx = 5)
        self.tag_config('bold', font=('bold'), background='#ddd')  
        self.tag_config('find', font=('bold'), foreground='#111', background='yellow')
        self.get_font_width()             
        self.click_time = 0
        self.filename = None
        self.popmenu = self._add_pop_menu_()
        self.bind('<ButtonRelease-1>', self.___button1_up___)      
        self.bind('<<TextUpdated>>', self.on_update_text)
        self.bind('<<goto>>', self.on_goto)
        self.bind('<<gotoline>>', self.on_gotoline)       
        for key in ['<F6>', '<Tab>', '<Control-period>']:
            self.bind(key, self.on_add_tab)
        for key in ['<F2>', '<Shift-Tab>', '<Control-comma>']:
            self.bind(key, self.on_remove_tab)  
        self.bind('<KeyPress>', self.on_keydown)
        self.bind('<KeyRelease>', self.on_keyup)  
        self.bind('<Control-v>', self.on_key_v)               
        
    def init_code_editor(self):
        self.vars = {}
        self.text = None       
        self.msg = self
        self.config(foreground='#121')
        self.config(background='#f5f5f3')    
        self.tag_config('bold', font=('bold'), background='#ddd')       
        keys = 'from|import|def|class|if|else|elif|for|in|then|dict|list|continue|return'
        keys += '|None|True|False|while|break|pass|with|as|try|except|not|or|and|do|const|local'
        self.keywords = keys.split('|')
        self.init_config()        
        self.init_pattern()   
        

        
class TextObj(tk.Text, TextUtils):
    def __init__(self, master, scroll=True, fill=True, **kw):
        super().__init__(master, **kw)
        self.init_all()                       
        if fill == True:
           self.place(x=0, y=0, relwidth=1, relheight=1) 
        if scroll == True:
           self.add_scrollbar(self.master)               
        #self.bind('<Configure>', self.on_config)
        
    def add_scrollbar(self, frame):
        from aui.aui_ui import ScrollBar
        self.scrollbar = ScrollBar(self)   
        
    def on_config(self, event=None):
        self.get_font_width()
        n = event.width//self.font_width
        self.config(width=n-2)

        
class Text(TextObj):
    def __init__(self, master, scroll=True, fill=True, dark=False, **kw):
        super().__init__(master, scroll, fill, **kw)
        self.init_code_editor()
        if dark == True:
            self.init_dark_config()
 


class TextEntry(tk.Text, TextUtils):
    def __init__(self, master, text='', **kw):
        super().__init__(master, text, **kw)
        self.mode = 'entry'
        self.rows = []
        self.iscode = False
        self.ln = 1        
        self.init_all()              
        
    def init_code_config(self):
        self.mode = 'code'
        
        self.config(wrap='char')
        self.bind('<FocusIn>', self.on_focus_in)
        self.bind('<FocusOut>', self.on_focus_out)               
        
    def get_data(self):
        if self.edit_modified() == True:
            self.data = self.get_text()
            self.edit_modified(False)            
        return self.data
             
    def set_name(self, name):
        self.mode = 'name'
        self.data = name
        self.insert('1.0', name)
        self.ln = 1
        self.config(height=1)
        self.edit_modified(False)
        
    def set_data(self, text):             
        self.mode = 'text'
        if type(text) != str:
            text = str(text)
        ln = text.count('\n') 
        n = len(text)
        if ln < 2 and n > 300:
            text = pformat(text)
        self.ln = text.count('\n') + 1
        self.config(heigh=min(self.ln, 3))        
        self.iscode = text.count('\n') > 2
        if self.iscode or len(text) > 100:
            self.init_code_config() 
        self.data = text        
        self.set_text(text[0:200])
        self.edit_modified(False)
            
    def init_text(self):
        self.init_pattern()
        self.init_dark_config()
        self.set_text(self.data)    
        self.edit_modified(False)
        
    def on_focus_in(self, event=None):
        n = min(self.ln+2, 30)
        for obj in self.rows:
            obj.config(height=n)
        if self.pattern == None:
            self.init_text()       
        else:
            self.init_dark_config()     
        
    def on_focus_out(self, event=None):
        self.init_config()
        for obj in self.rows:
            obj.config(heigh=3)        
            

TagTextObj = Text



if __name__ == '__main__':    
    from aui import App, Layout   
    import DB
    app = App(title='Test Textobj', size=(1600, 1080))  
    
    def on_select(event):        
        obj = event.widget
        path, tag = obj.getvar('<<SelectFile>>')
        app.msg.puts(path)
        app.text.open(path)        

    if 0:

        text = Text(app)
        text.init_dark_config()
        text.open(__file__)
    else:
              
        app.add_set1(app)
        app.textbox.open(__file__)
        path = DB.get_path('local')
        tree = app.filetree
        tree.set_path(path)
        tree.click_select = 'click' 
        tree.bind('<<SelectFile>>', on_select)

    app.mainloop()        

    
