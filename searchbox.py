import os
import tkinter as tk
from tkinter import ttk
from aui import Messagebox, aFrame, TextObj, TextSearch
from texteditor import TextEditor
import re
from fileio import *
    

class WordBox(TextObj):
    def __init__(self, frame, master, **kw):
        TextObj.__init__(self, frame, **kw) 
        self.bind('<ButtonRelease-1>', self.on_click)
        self.master = master
        self.tag_config('sel', foreground='black', background='#999')
        self.click_time = 0
        
    def on_doubleclick(self):
        self.master.on_find()

    def on_click(self, event=None):       
        idx = self.index('insert')
        text = self.get_line_text(idx).strip()
        self.master.set_findtext(text)
        idx1 = self.index(idx + ' linestart')        
        idx2 = self.index(idx + ' lineend')  
        self.tag_remove('sel', '1.0', 'end')
        self.tag_add('sel', idx1, idx2)
        if event.time - self.click_time < 300:
            self.on_doubleclick()            
        self.click_time = event.time

    def list_str(self, lst):
        t = ' '
        text = ''
        n = int(self.winfo_reqwidth() / 20)
        for s in lst:
            t += s.ljust(10) + ' '
            if len(t) > n:
                text += t + '\n'
                t = ' '
        return text + t
        
    def put_list(self, lst):
        self.puts(self.list_str(lst))
        
            

class SearchBox(tk.Frame, TextSearch):     
    def __init__(self, master, cmd_action=None):       
        super().__init__(master)
        self.root = self.winfo_toplevel()
        self.config(padx=5, pady=5)
        self.msg = None
        self.dct = {'pos':[]}
        # 建立標籤
        label = tk.Label(self, text='輸入要尋找的文字和要取代的文字')
        label.pack()

        # 建立文字輸入框
        frame0 = tk.Frame(self)
        frame0.pack(fill='x', expand=False)

        self.find_entry = tk.Entry(frame0)
        self.replace_entry = tk.Entry(frame0)        
        
        self.find_entry.pack()
        self.replace_entry.pack()
        
        # 建立按鈕
        frame = tk.Frame(self)
        frame.pack(fill='x', expand=False, pady=10)

        frame1 = tk.Frame(frame)
        frame1.pack(fill='x', expand=False)
        frame2 = tk.Frame(frame)
        frame2.pack(fill='x', expand=False)

        buttons = {}
        buttons[0] = tk.Button(frame1, text='尋找', width=10, command=self.on_find)
        buttons['replace'] = tk.Button(frame1, text='取代', command=self.on_replace_one)  
        buttons['replaceall'] = tk.Button(frame1, text='全部取代', command=self.on_replace_all)    
              
        buttons[2] = tk.Button(frame2, text='First', command=self.on_go_first)
        buttons[3] = tk.Button(frame2, text='Prev', command=self.on_go_prev)
        buttons[4] = tk.Button(frame2, text='Next', command=self.on_go_next)
        buttons[5] = tk.Button(frame2, text='Last', command=self.on_go_last)          
        
        for button in buttons.values():
            button.pack(side='left',fill='x', expand=True)

        frame4 = tk.Frame(frame)
        frame4.pack(fill='x', expand=False, pady=(10, 0))
        self.path_entry = tk.Entry(frame4)
        self.path_entry.pack(fill='x', expand=False)
        self.path_entry.insert(0, 'src;~/test/tk')
        button = tk.Button(frame4, text='Find in files', command=self.on_find_in_files)     
        button.pack(side='left', padx=10)      
        button = tk.Button(frame4, text='Search DB', command=self.on_search_db)     
        button.pack(side='left')        
        
        frame5 = tk.Frame(self)
        frame5.pack(fill='both', expand=True, pady=10)
        frame6 = tk.Frame(frame5)
        frame6.pack(fill='x', expand=False, pady=3)
        
        lst = ['[a-zA-Z]\w+', '\w\w+', '(?<=class)\s+\w+', '(?<=def)\s+\w+', 'self.\w+', '(?<=import)\s\w+',
               'get\w+', 'setw+', 'on_\w+', '__\w+']        
        self.re_entry = ttk.Combobox(frame6, values=lst)
        self.re_entry.pack(fill='x', expand=True, padx=3)
        self.re_entry.insert(0, '[a-zA-Z]\w+')
        self.re_entry.bind("<<ComboboxSelected>>", self.on_search_words)
        button = tk.Button(frame6, text='Search words', command=self.on_search_words)     
        button.pack()

        self.wordbox = WordBox(frame5, self)
        self.wordbox.pack(fill='both', expand=True, pady=5)
        self.pos_index = 0        
        #self.on_search_words()
        self.bind_all("<<SetText>>", self.on_update)
        self.bind_all("<<Text Find>>", self.on_set_entry)
        
    def on_find_in_files(self, event=None):
        if self.msg == None:
            self.msg = self.winfo_toplevel().msg
        key = self.find_entry.get()
        if key.strip() == '':
            return
        self.msg.clear_all()
        text = self.path_entry.get()                     
        pathlist = text.split(';')  
        self.find_in_files(pathlist, key)
        self.msg.update_tag(key=key)
        
    def on_search_db(self, event=None):        
        if self.msg == None:
            self.msg = self.winfo_toplevel().msg
        self.msg.clear_all()    
        key = self.find_entry.get()
        if key.strip() == '':
            return
        for p in db_search_key(key):
            fn, lst = p
            self.msg.puts(fn)
            for s in lst:
                self.msg.puts(s)
        self.msg.update_tag(key=key)
        
    def on_set_entry(self, event=None):
        textbox = self.get_textbox()
        pos = textbox.tag_ranges('sel')
        if pos == ():
            return
        start, end = pos
        text = textbox.get(start, end)
        self.find_entry.delete(0, 'end')
        self.find_entry.insert(0, text)

    def on_update(self, event=None):        
        self.on_search_words()
        
    def get_textbox(self):
        return self.root.textbox       
       
    def set_findtext(self, text):
        self.find_entry.delete(0, len(self.find_entry.get()))
        self.find_entry.insert(0, text)
        
    def on_search_words(self, event=None):
        textbox = self.get_textbox()
        text = textbox.get('1.0', 'end')
        pattern = self.re_entry.get()
        self.wordbox.delete('1.0', 'end')
        try:
            lst = re.findall(pattern, text)
        except:
            self.wordbox.puts('error')
            return
        if lst == []:
            return
        
        lst1 = list(set(lst))
        lst1.sort()
        lst2 = []
        for s in lst1:
            lst2.append(s.strip())
        s = '\n'.join(lst2)
        self.wordbox.set_text(s)

    def textpos(self, i):
        textbox = self.get_textbox()
        textbox.tag_remove('sel', '1.0', 'end')
        lst = self.dct['pos']
        if lst == []:
            lst = ['1.0', 'end']
        self.pos_index = i
        pos = textbox.tag_nextrange('find', lst[i])
        if pos == ():
            return
        start = pos[0]
        textbox.see(start)
        end = '{}+{}c'.format(start, self.find_len)
        textbox.tag_add('sel', start, end)
        textbox.tag_raise('sel')
    
    def getpos(self, key):     
        n = len(self.dct['pos'])
        if key == 'first':
            i = 0
        elif key == 'last':
            i = n-1
        elif key == 'next':            
            i = self.pos_index + 1
            if i >= n:
                i = 0
        else:                        
            i = self.pos_index - 1
            if i < 0:
                i = n - 1
        self.textpos(i)
        
    def on_go_first(self, event=None):
        self.getpos('first')
        
    def on_go_last(self, event=None):
        self.getpos('last')
        
    def on_go_next(self, event=None):
        self.getpos('next')
        
    def on_go_prev(self, event=None):
        self.getpos('prev')
        
    def tag_add(self, tag, pos, n):
        textbox = self.get_textbox()
        end = '{}+{}c'.format(pos, n)
        textbox.tag_add(tag, pos, end)
        self.dct['pos'].append(pos)
        return end
        
    def on_remove_tags(self, event=None):
        textbox = self.get_textbox()
        textbox.tag_remove('find', '1.0', 'end')
        
    def search_text(self, find_text):
        textbox = self.get_textbox()
        textbox.tag_remove('find', '1.0', 'end')

        self.find_len = len(find_text)
        # 在文字元件中尋找文字
        start = '1.0'
        n = len(find_text)
        self.dct['pos'] = ['1.0']
        current = textbox.index('insert')
        while True:
            start = textbox.search(find_text, start, nocase=True, stopindex='end')
            if not start:
                break      
            start = self.tag_add('find', start, n)
        p = textbox.tag_nextrange('find', '1.0')
        if p != ():    
           textbox.goto_pos(p[0])
        self.pos_index = 0
    
    def on_find(self, event=None):
        self.search_text(self.find_entry.get())
        if self.msg == None:
            self.msg = self.winfo_toplevel().msg        
        key = self.find_entry.get()
        textbox = self.winfo_toplevel().textbox
        filepath = textbox.filename
        text = textbox.get_text()
        self.find_in_text(filepath, text, key)
        self.msg.update_tag(key=key)
        
    def on_replace_one(self, event=None):        
        textbox = self.get_textbox()
        # 取得要尋找的文字和要取代的文字
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        pos = textbox.tag_nextrange('sel', '1.0')
        if pos == ():
            self.textpos(0)
            return
        start, end = pos
        textbox.replace(start, end, replace_text)
        self.getpos('next')
        
    def on_replace_all(self, event=None):
        textbox = self.get_textbox()
        textbox.tag_remove('find', '1.0', 'end')

        # 取得要尋找的文字和要取代的文字
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
    
        # 在文字元件中尋找文字
        start = '1.0'
        while True:
            start = textbox.search(find_text, start, nocase=True, stopindex='end')
            if not start:
                break
            end = '{}+{}c'.format(start, len(find_text))
            textbox.replace(start, end, replace_text)
            end = self.tag_add('find', start, len(replace_text))
            start = end


class TestFrame(aFrame):     
    def __init__(self, master):       
        super().__init__(master)
        root = self.winfo_toplevel()
        self.add_set1(SideFrame=SearchBox)
        root.textbox = self.textbox
        self.textbox.open(__file__)    
        #box = SearchBox(self.frames['LR'].left, self.on_select_class)
        #box.pack(fill='both', expand=True)
        #box.msg = msg
        self.searchbox = self.sideframe
        
        self.bind_all('<<gotofile>>', self.on_gotofile)  
        
    def on_gotofile(self, event):
        arg = event.widget.getvar("<<gotofile>>")
        self.textbox.open(realpath(arg))

    def on_select_class(self, cmd, name=None, key=None):      
        if cmd == 'textbox':
            return self.textbox
        elif cmd == 'find':
            return     
        
        # self.puts(cmd, name, key)
        if type(cmd) is tuple:
            text = self.textbox.text[:cmd[0]]
            n = text.count('\n')        
            self.textbox.see('%d.0' %n)  


if __name__ == '__main__':       
    from aui import App
    frame = App('Test searchbox', size=(1920, 1080), Frame=TestFrame)
    frame.searchbox.find_entry.insert(0, 'QFileSystemWatcher')
    frame.mainloop()




