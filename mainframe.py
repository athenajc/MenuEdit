#!/usr/bin/python3
import os
import re
import sys
import inspect
import webbrowser
import time 
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
from aui import Messagebox
from help import HelpFrame
from treeview import SideNotebook
from texteditor import TextEditor
from textui import FrameLayout, PopMenu, MenuBar
from fileio import *
from runfile import RunFile   
import DB as db        
          
class TextNotebook():
    def switch_textbox(self, textbox):
        self.textbox = textbox
        self.msg.textbox = textbox    
        self.root.textbox = textbox
        self.event_generate("<<SwitchTextBox>>")
        #self.classbox.textbox = textbox             
        #self.classbox.set_text(textbox.get_text(), textbox.filename)   
        self.root.title('TextEditor - ' + textbox.filename)         
        
    def add_textframe(self, filename, text):
        frame = tk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        textbox = TextEditor(frame)
        textbox.pack(fill='both', expand=True)    
        textbox.msg = self.msg
        textbox.statusbar = self.statusbar
        textbox.helpbox = self.helpbox       
        textbox.classbox = self.classbox   
        textbox.update()
        self.update()       
        if filename.endswith('.js'):
           if not '\n' in text:
               text = text.replace(';', '; \n')
               text = text.replace('}', '} \n')
        textbox.set_filename(filename)
        textbox.set_text(text)        
        textbox.update()
        self.update()    
        label = filename.split(os.sep)[-1]
        if label in self.files:
            for i in range(1,10):
                s = label + '(%d)'%i  
                if not s in self.files:
                    label = s
                    break                  
        textbox.filename = filename   
        self.files[label] = textbox               
        self.notebook.add(frame, text=label.center(17))
        n = len(self.files)
        i = n - 1
        self.notebook.select(i)
        self.switch_textbox(textbox)
        return textbox        
        
    def switch_frame(self, event=None):
        dct = self.notebook.tab('current')
        label = dct['text'].strip()
        textbox = self.files.get(label)
        if textbox == None:
            return
        self.switch_textbox(textbox)
        
    def search_file(self, filename):
        if self.files == {}:
           return False
        filename = realpath(filename)
        id = 0
        for label in self.files:
            tb = self.files.get(label)
            if tb.filename == filename:
               self.switch_textbox(tb)
               self.notebook.select(id)
               return True
            id += 1
        return False 
        
    def add_notebook(self, frame):
        self.files = {}
        notebook = ttk.Notebook(frame)
        self.notebook = notebook
        notebook.pack(fill='both', expand=True)
        notebook.bind('<ButtonRelease-1>', self.switch_frame)
        
    def new_file(self):
        self.add_textframe('/home/athena/tmp/noname.py', '\n' * 10)
        
    def close_file(self):
        tab_id = self.notebook.index('current')
        dct = self.notebook.tab(tab_id)
        label = dct['text'].strip()        
        textbox = self.files.get(label) 
        self.msg.puts('close file ' + textbox.filename)
        textbox.filename = None
        self.notebook.forget(tab_id)                
        self.files.pop(label)
        if self.files == {}:
            self.new_file()
        else:
            i = len(self.files) - 1
            if i < 0:
              i = 0
            self.notebook.select(i)
        self.switch_frame()               
        
#----------------------------------------------------------------------------------            
class MenuTextFrame(tk.Frame, FrameLayout, TextNotebook, RunFile):
    def __init__(self, master, filename, **kw):
        super().__init__(master, cursor="arrow", name='app') 
       
        self.run_alone = (filename != None)
        print(self.run_alone)
        root = self.winfo_toplevel()    
        root.app = self
        root.cmd_action = self.on_select_action    
        self.root = root
        self.root.app = self
        self.parent = master
        self.msg = None    
        self.compared = False
        self.vars = {}
        self.vars['history'] = []
        #self.prjview = None
        self.server = None
        
        frame0, frame1 = self.add_spliter_h(self, xsep=0.2)
        fmenu, flist = self.add_frame(frame0, xsep=0.3)
        self.add_menu(fmenu)

        frame2, fhelp = self.add_spliter_h(frame1, xsep=0.7)        
        ftext, fmsg = self.add_spliter(frame2, ysep=0.75)
        self.add_notebook(ftext)
         
        msg = Messagebox(fmsg)
        msg.pack(fill='both', expand=True)
        msg.parent = self
        statusbar = msg.add_statusbar()   
        self.msg = msg
        root.msg = msg
        self.puts = msg.puts
        self.statusbar = statusbar        
                  
        helpbox = HelpFrame(fhelp)  
        helpbox.pack(fill='both', expand=True)  
        self.helpbox = helpbox  
                
        tree_nb = SideNotebook(flist)
        tree_nb.pack(fill='both', expand=True)
        tree_nb.set_msg(msg)
        self.classbox = tree_nb.pages['Class']        
        self.listbox = tree_nb.pages['File']
        self.fav_dir_tree = tree_nb.pages['History']
        #self.prjview = tree_nb.pages['Project']
         
        self.listbox.set_path(os.getcwd())  
        
        msg.parent = self
        msg.action = self.on_cmd_action
        sys.stdout = self.msg
        sys.stderr = self.msg  
        self.update()        
        self.filename = filename
        if not self.run_alone:            
            self.after(10, self.load_ini)       
        else:
            self.after(10, self.open_file, filename)
        self.bind_all("<<OpenSource>>", self.on_open_source) 
        self.bind_all('<<gotofile>>', self.on_gotofile)  
        
    def on_gotofile(self, event):
        arg = event.widget.getvar("<<gotofile>>")
        self.puts(arg)
        self.open_file(realpath(arg)) 
                   
    def set_prj(self, fn):
        self.prjfile = fn
                
    def on_cmd_action(self, cmd, arg):
        #print('Receive ', cmd, arg) 
        if cmd == 'open':
            self.open_file(arg)
        elif cmd == 'gotofile':
           if self.textbox.filename != arg:
              self.open_file(arg)
        elif cmd == 'gotoline':
           self.textbox.cmdlist.append((cmd, int(arg)))
           #print('goto', int(arg), len(textbox.items))
        elif cmd == 'goto':
           self.textbox.cmdlist.append((cmd, int(arg)))
           #self.textbox.see_line(int(arg))
        self.textbox.event_generate('<<check_cmd_list>>') 
                
    def add_menu(self, fmenu):
        names = 'New,Open,,Close,,History,,Save,Save as,,Undo,Redo,,Copy,Cut,Paste,,'
        names += 'Add Tab,Remove Tab,,Exec,,Run'
        menubar = MenuBar(fmenu, items=names.split(',')) 
        menubar.pack(side='top', fill='x', expand=False)
        menubar.bind_action('Open', self.on_open_file)
        menubar.bind_action('History', self.on_open_history)
        menubar.bind_action('Save', self.on_save_file)
        menubar.bind_action('Save as', self.on_saveas_file)
        menubar.bind_action('New', self.on_new_file)  
        menubar.bind_action('Close', self.on_close_file)  
        menubar.bind_action('Copy', self.on_copy)      
        menubar.bind_action('Cut', self.on_cut)   
        menubar.bind_action('Paste', self.on_paste)
        menubar.bind_action('Undo', self.on_undo)   
        menubar.bind_action('Redo', self.on_redo)      
        menubar.bind_action('Add Tab', self.on_add_tab)   
        menubar.bind_action('Remove Tab', self.on_remove_tab)            
        menubar.bind_action('Exec', self.on_exec)
        menubar.bind_action('Run', self.on_run)
        self.menubar = menubar
        self.hmenu = None

    def unpost_history(self):
        if self.hmenu != None:
            self.hmenu.unpost()
            self.hmenu.unbind_all('<ButtonRelease-1>')
            self.hmenu = None  
        
    def on_select_history(self, event=None):
        menu = self.hmenu        
        self.msg.puts(event)
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
        
    def on_select_file(self, path, tag):      
        if tag == 'file':
            self.open_file(path)         
            
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

            start = self.textbox.search(name, '%d.0' % (i))
            if len(start) == 0:
                start = pos
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
        filepath = '/link' #os.path.dirname(realpath(fn))        
        filename = dialog(defaultextension='.py', mode = mode,
               filetypes = [('Python files', '.py'), ('all files', '.*')],
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
                
    def on_run(self, event=None):
        self.do_run_file()
        
    def on_exec(self, event=None):
        self.do_exec()
        
    def open_file(self, filename): 
        if self.search_file(filename) == True:
           return 
        if len(self.files) > 10:
           self.msg.puts('Open too much')
           return
        filename = realpath(filename)            
        ext = os.path.splitext(filename)[1].replace('.', '')
        if ext in ['png', 'jpg']:
           self.start_process(['xviewer', filename])
           return           
        if not filename in self.vars['history']:
            self.vars['history'].insert(0, filename)  
        with open(filename, 'r') as f:
            text = f.read()
            f.close()
        self.textbox = self.add_textframe(filename, text)
        self.textbox.filename = filename    
        self.winfo_toplevel().title('TextEditor      ' + filename)
        self.msg.puts(filename + ' opened')
            
    def save_file(self, text, filename):
        if filename == None:
            return  
        filename = realpath(filename)     
        if text == fread(filename):
           #self.msg.puts(filename + ' not modified')
           return 
        fwrite(filename, text)              
        
    def saveas_file(self, filename):
        text = self.textbox.get_text()
        self.textbox.filename = filename
        fwrite(filename, text)
        self.msg.puts(filename + ' saved')      
        self.close_file()
        self.open_file(filename)   
        self.winfo_toplevel().title('TextEditor      ' + filename)    
           
    def load_ini(self):
        self.update()        
        text = db.get_cache('menutext.ini')
        dct = eval(text)
        files = dct.get('files', [])        
        lastfile = None       
        self.vars['history'] = history = dct.get('history')                
        for fn in history:
            self.fav_dir_tree.add_file(fn)            
            path = fn.rsplit(os.sep, 1)[0]
            self.fav_dir_tree.add_dir(path)
        if not (self.filename == None or self.filename == ''):
           files.append(self.filename)    
        for filename in files:
           filename = realpath(filename)
           if os.path.exists(filename) == False:
              self.msg.puts(filename + ' not exists.')
              continue
           self.open_file(filename)
           self.update()
           lastfile = filename        

        if lastfile != None:
           path = os.path.dirname(lastfile)
           parent = os.path.split(path)[0]
           os.chdir(parent)        
           self.listbox.set_path(parent)   
           self.listbox.active_file(lastfile)
           self.listbox.update()
        else:
           self.new_file()
                
    def save_ini(self):
        lst = []
        for s, v in self.files.items():
            fn = v.filename
            if fn.strip() == '':
               continue
            lst.append(fn)
        dct = {}
        dct['files'] = lst
        n = len(self.vars['history'])
        if n > 15:
            n = 15
        dct['history'] = self.vars['history'][0:n]
        text = str(dct)        
        db.set_cache('menutext.ini', text)
            
    def destroy(self):
        try:
           if not self.run_alone:
               self.save_ini()
        except Exception as e:
           print(e)
        
#----------------------------------------------------------------------------------                    	
def get_filename():
    filename = None
    srcpath = os.path.dirname(__file__)

    if len(sys.argv) > 1:
        print(sys.argv)
        filename = sys.argv[1]   
        filename = realpath(filename)  
    
    if os.path.exists(srcpath):
       os.chdir(srcpath)
    return filename

def main():      
    root = tk.Tk()
    root.title('TextEditor')
    root.geometry('1800x1023')   
    root.tk.setvar('appname', 'menutext')
    try:
        filename = get_filename()
        icon = realpath('~/data/icon/menutext.png')
        root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=icon))        
    except:
        pass    
    frame = MenuTextFrame(root, filename)
    frame.pack(fill='both', expand=True)       
    root.mainloop()             
    
if __name__ == '__main__':     
    main()



