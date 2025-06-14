import os
import re
import sys
from fileio import realpath, fread, fwrite
import tkinter as tk
import tkinter.filedialog
from aui import MenuBar
import json
import time

class MenuActions():    
    def unpost_history(self):
        if self.hmenu != None:
            self.hmenu.unpost()
            self.hmenu.unbind_all('<ButtonRelease-1>')
            self.hmenu = None  
        
    def on_select_history(self, event=None):
        menu = self.hmenu        
        #self.msg.puts(event)
        if menu == None:
            return
        if event.x > menu.winfo_reqwidth():
            self.unpost_history()        
            return
        n = menu.index('end')
        y = event.y
        lst = []
        for i in range(n+1):
            lst.insert(0, (i, menu.yposition(i)))
        for i, py in lst:
            if y >= py:
                self.open_file(self.vars['history'][i-1])
                break                        
        self.unpost_history()        
        
    def on_open_history(self, event):
        if self.hmenu != None:
            self.unpost_history()          
            return
        menu = tk.Menu()        
        menu.bind_all('<ButtonRelease-1>', self.on_select_history) 
        for s in self.vars['history'] :
            menu.add_command(label=s)          
        x, y = event.x, event.y  
        x1 = self.winfo_rootx() + menu.winfo_reqwidth() + 20  
        y1 = self.winfo_rooty()
        menu.post(x + x1, y + y1 + 100)  
        self.hmenu = menu         

    def on_add_tab(self, event=None):   
        self.textbox.on_add_tab()
    
    def on_remove_tab(self, event=None):   
        self.textbox.on_remove_tab()

    def on_undo(self, event=None):   
        self.textbox.edit_undo()
        self.textbox.event_generate("<<TextModified>>")
    
    def on_redo(self, event=None):   
        self.textbox.edit_redo()
        self.textbox.event_generate("<<TextModified>>")
          
    def on_copy(self, event=None):   
        self.textbox.edit_copy()        
    
    def on_cut(self, event):
        self.textbox.edit_cut()
        
    def on_paste(self, event):
        self.textbox.edit_paste() 
         
    def on_select_class(self, i, name, key):  
        if type(i) is tuple:
            text = self.textbox.text[:i[0]]
            n = text.count('\n') + 1      
            #self.textbox.see('%d.0' %n)
            self.textbox.goto(n, name, key) 
        else:    
            self.textbox.goto(i, name, key)        
   
            
    def on_select_action(self, cmd, data=None, flag=None):
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
                
    def on_new_file(self, event=None):
        self.new_file()
        
    def on_close_file(self, event=None):
        self.close_file()
        
    def file_dialog(self, dialog, op='Open', mode='r'):
        fn = self.textbox.filename
        if fn == 'noname' or fn == None or fn == '':
            fn = self.vars['history'][-1]
        filepath = os.path.dirname(realpath(fn))     
 
        filename = dialog(defaultextension='.json', mode = mode,
               filetypes = [('Json/Text files', r'*.json *.txt'), ('all files', '.*')],
               initialdir = filepath,
               initialfile = '',
               parent = self,
               title = op + ' File dialog'
               )
        if filename == None:
            return None
        return filename.name        
        
    def on_open_source(self, event=None): 
        filename = self.helpbox.get_sourcefile()
        if filename == None or filename == '':            
            return
        self.open_file(filename)
        
    def on_open_file(self, event=None):   
        filename = self.file_dialog(tk.filedialog.askopenfile, 'Open', 'r')   
        print('Filedialog return (%s)'%filename) 
        if filename == None or filename == '':
            return
        self.open_file(filename)
                    
    def on_save_file(self, event=None):   
        text = self.textbox.get_text()
        filename = self.textbox.filename
        self.msg.puts('on_save_file ', filename)
        self.save_file(text, filename)  

    def on_saveas_file(self, event=None):
        filename = self.file_dialog(tk.filedialog.asksaveasfile, 'Save as', 'w')           
        if filename == None or filename == '':
            print('Error : Filedialog return (%s)'%filename) 
            return
        print('Filedialog return (%s)'%filename)         
        self.saveas_file(filename)        
        
    def load_file(self, fn):
        self.textbox.filename = fn
        self.textbox.open(fn)        
        text = self.textbox.get_text()
        s = text.strip()
        n = len(text.splitlines())
        if n < 20:
            fsize = 12 + (100 - n)//20
        else:
            fsize = 12
        self.textbox.set_font_size(fsize)
        if s[0] == '{':
            dct = json.loads(text) 
            self.textbox.set_text(dct['textContent'] + '\n\n')
            self.textbox.puts('Tag:' + dct['labels'][0]['name'])
        
    def open_file(self, filename): 
        filename = realpath(filename)            
        ext = os.path.splitext(filename)[1].replace('.', '')
        
        if not filename in self.vars['history']:
            self.vars['history'].insert(0, filename)  
        self.load_file(filename)
 
        self.set_filename(filename)
        self.msg.puts(filename + ' opened')
        
    def save_file(self, text, filename):
        if filename == None:
            return  
        filename = realpath(filename)     
        if text == fread(filename):
           self.msg.puts(filename + ' not modified')
           return 
        fwrite(filename, text)              
        
    def saveas_file(self, filename):
        text = self.textbox.get_text()
        fwrite(filename, text)
        self.msg.puts(filename + ' saved')      
        self.close_file()
        self.open_file(filename)   
        self.set_filename(filename)   
        
    def close_file(self):
        self.new_file()   
        
    def new_file(self):
        self.textbox.set_text('')
        filename = time.strftime("%Y%m%d_%H%M%S") + '.txt'
        self.set_filename(filename)
         
    def set_filename(self, filename):
        self.filename = self.textbox.filename = filename
        self.winfo_toplevel().title('A-None    -      ' + filename)

    def add_menubar(self, fmenu):
        names = 'New,Open,,Close,,History,,Save,Save as,,Undo,Redo,,Copy,Cut,Paste,,'
        names += 'Add Tab,Remove Tab,,Graph'
        menubar = MenuBar(fmenu, items=names.split(',')) 
        menubar.pack(side='top', fill='x', expand=False)
        cmds = [('Open', self.on_open_file),
                ('History', self.on_open_history),
                ('Save', self.on_save_file),
                ('Save as', self.on_saveas_file),
                ('New', self.on_new_file),
                ('Close', self.on_close_file),  
                ('Copy', self.on_copy),      
                ('Cut', self.on_cut),   
                ('Paste', self.on_paste),
                ('Undo', self.on_undo),   
                ('Redo', self.on_redo),      
                ('Add Tab', self.on_add_tab),   
                ('Remove Tab', self.on_remove_tab)]
        for a, b in cmds:
            menubar.bind_action(a, b)
        self.menubar = menubar
        self.hmenu = None
        


