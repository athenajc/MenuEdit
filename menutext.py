#!/usr/bin/python3
import os
import re
import sys
import inspect
import subprocess
import webbrowser
import time 
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from messagebox import Messagebox
from helpbox import HelpFrame
from treeview import ClassTree, FileTreeView, TreeNotebook
from textbox import ScrollText   
from textui import FrameLayout, PopMenu
import ui
import fileio
       
class ImageViewer(tk.Toplevel):
    def __init__(self, master, filename, **kw):       
        tk.Toplevel.__init__(self, master, **kw)
        self.wm_title(filename)
        label = tk.Label(self)
        label.pack(fill='both', expand=True)
        filename = os.path.realpath(filename)
        img = ui.ImageObj(filename)
        print(img.size)
        w, h = img.size
        s = max(w, h)
        if s < 400:
           m = int(400 / s)
           w, h = w * m, h * m
           img = ui.ImageObj(filename, size=(w, h)) 
        self.tkimage = img.get_tkimage()
        label.configure(image = self.tkimage) 
        self.image = img
        self.label = label
        self.geometry('%dx%d' % (w, h))
        self.bind('<Configure>', self.on_configure)
        
    def on_configure(self, event=None):
        w, h = event.width, event.height
        self.image.resize((w, h))
        self.tkimage = self.image.get_tkimage()
        self.label.configure(image = self.tkimage) 
        
#----------------------------------------------------------------------------------
class MenuBar(tk.Frame):
    def __init__(self, master, items=[], cnf={}, **kw):
        tk.Frame.__init__(self, master, **kw)
        self.button = {}
        for key in items:
            if key != '':
                self.button[key] = tk.Button(self, text=key, relief='flat')
                self.button[key].pack(side='top', fill='both', expand=False, pady=5)             
            else:
                frame = tk.Frame(self, width=100, height=1, background='#999')
                frame.pack(pady=5) 
          
    def bind_action(self, item, action):
        self.button[item].bind('<ButtonRelease-1>', action)   
        
class TextNotebook():
    def switch_textbox(self, textbox):
        self.textbox = textbox
        self.msg.textbox = textbox    
        self.classbox.textbox = textbox             
        self.classbox.set_text(textbox.get_text(), textbox.filename)   
        self.root.title('TextEditor - ' + textbox.filename)         
        
    def add_textframe(self, filename, text):
        frame = tk.Frame(self.notebook)
        frame.pack(fill='both', expand=True)
        textbox = ScrollText(frame)
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
        filename = os.path.realpath(filename)
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
        self.add_textframe('/home/athena/tmp/noname.py', '\n' * 30)
        
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
class MenuTextFrame(tk.Frame, FrameLayout, TextNotebook):
    def __init__(self, master, filename, cnf={}, **kw):
        tk.Frame.__init__(self, master) 
        root = self.winfo_toplevel()    
        self.root = root
        self.root.app = self
        self.parent = master
        self.msg = None    
        self.callback = None
        self.compared = False
        self.vars = {}
        self.vars['history'] = []
        self.prjfile = ''
        self.prjview = None
        
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
        self.statusbar = statusbar        
                
        helpbox = HelpFrame(fhelp)  
        helpbox.pack(fill='both', expand=True)  
        self.helpbox = helpbox  
                
        fltop, flbottom = self.add_spliter(flist, ysep=0.6)
        classbox = ClassTree(fltop, self.on_select_class, relief='sunk', bd=1)
        classbox.pack(fill='both', expand=True)   
        self.classbox = classbox            
        tree_notebook = TreeNotebook(flbottom, self.on_select_file, relief='sunk', bd=1)
        tree_notebook.pack(fill='both', expand=True)  
        listbox = tree_notebook.tree1
        listbox.set_path(os.getcwd())  
        classbox.msg = msg
        listbox.msg = msg
        self.listbox = listbox
        self.fav_dir_tree = tree_notebook.tree2
        self.prjview = tree_notebook.tree3
        
        msg.parent = self
        msg.action = self.on_cmd_action
        sys.stdout = self.msg
        sys.stderr = self.msg  
        self.update()        
        self.filename = filename
        self.after(10, self.load_ini)                     
                   
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
            
    def on_new_file(self, event=None):
        self.new_file()
        
    def on_close_file(self, event=None):
        self.close_file()
        
    def file_dialog(self, dialog, op='Open', mode='r'):
        fn = self.textbox.filename
        if fn == 'noname' or fn == None or fn == '':
            fn = self.vars['history'][-1]
        filepath = os.path.dirname(os.path.realpath(fn))        
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
                
    def open_file(self, filename): 
        if self.search_file(filename) == True:
           return 
        if len(self.files) > 10:
           self.msg.puts('Open too much')
           return
        filename = os.path.realpath(filename)            
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
        filename = os.path.realpath(filename)     
        if text == fileio.fread(filename):
           #self.msg.puts(filename + ' not modified')
           return 
        fileio.fwrite(filename, text)              
        
    def saveas_file(self, filename):
        text = self.textbox.get_text()
        self.textbox.filename = filename
        fileio.fwrite(filename, text)
        self.msg.puts(filename + ' saved')      
        self.close_file()
        self.open_file(filename)   
        self.winfo_toplevel().title('TextEditor      ' + filename)          
                    
    def popen(self, cmd, fn):
        process = subprocess.Popen([cmd, fn],
                                universal_newlines=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT)
        while process.poll() == None:
            self.msg.puts(process.stdout.read(), end='')
            self.msg.update()
        s = process.stdout.read()
        if s != '':
           self.msg.puts(s)
            
    def pyshell_test(self, fn):
        from idlelib.pyshell import test_file
        test_file(fn)
          
    def process_communicate(self):
        out, err = self.process.communicate(timeout=10)
        text = out + err
        text = text.decode()
        for s in text.splitlines():
            self.msg.puts(s)
            
    def read_output(self):        
        #print('read output', time.time())
        sys.stdout.flush()
        self.process.stdout.flush()
        s = self.process.stdout.read()
        if s != '':
           self.msg.puts(s, end='')
           self.update()
            
    def start_process(self, cmd):
        self.msg.puts(cmd)
        root = self.winfo_toplevel() 
        self.process_running = True      
        self.process = subprocess.Popen(cmd, universal_newlines=True,          
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #print('start_process', time.time())                
        
        def poller():            
            #print('poller()', time.time())
            #print('.')
            if self.process is not None:
                res = self.process.poll() 
                if res != None:                    
                    self.on_stop_process()
                    return          
                self.read_output()                         
                # process is still running
                self.after(1, poller)  # continue polling
                root.update_idletasks()
            else:
                return
        delay = 1  # milliseconds
        self.after(delay, poller)
        root.update_idletasks()
        #self.read_output()
        
    def on_stop_process(self):      
        #print('on_stop_process', time.time())
        self.process_running = False                          
        path = os.getcwd()
        if '__pycache__' in path:
            os.chdir('..')            
             
    def open_html(self, url):        
        #url = path.replace('/home/athena/src/html', "http://localhost")
        webbrowser.open(url, new=0, autoraise=True)
        
    def run_py(self, path):
        #if self.prjfile != '':
        #    if path in self.prjview.files and self.prjview.mainfile != '':
        #        path = self.prjview.mainfile                
        p = path.rsplit(os.sep, 1)
        os.chdir(p[0])
        fn = p[1]
        
        if 1:
            self.start_process(['/usr/bin/python3', path])
        else:            
            self.popen('/usr/bin/python3', path) 
        #self.pyshell_test(path)
        
    def run(self, fn):
        self.msg.clear_all()
        if '.py' in fn:
            self.run_py(fn)
            
    def on_run(self, event=None):
        if self.textbox == None:
            return       
        self.msg.clear_all()             
        filename = self.textbox.filename 
        path = os.path.realpath(filename)
        #ext = path.rsplit('.')[1].lower()    
        ext = os.path.splitext(path)[1].replace('.', '')
        if ext in ['png', 'jpg']:             
           self.start_process(['xviewer', path])
           return
        elif ext == 'svg':    
            pypath = '/home/athena/src/svg/svgpath.py'
            self.start_process(['python3', pypath, path])
            return
        elif ext == 'rst':
            pypath = '/home/athena/src/menutext/rstview.py'
            self.start_process(['python3', pypath, path])
            return
        text = self.textbox.get_text()           
        if filename == 'noname':
            filename = 'noname.py'
            fileio.fwrite(filename, text)
        else:            
            self.save_file(text, filename)
            
        if ext == 'html':
            self.open_html(path)      
        elif ext == 'py':    
            if text[0:6] == '#main=':
                p = path.rsplit(os.sep, 1)             
                line1 = text.splitlines()[0]
                fn = line1[6:].strip()                
                path = os.path.realpath(fn)        
            self.run_py(path)
        elif ext == 'lua':    
            self.popen('lua', path)            
               
    def on_exec(self, event=None):
        if self.textbox == None:
            return       
        self.msg.clear_all()     
        filename = self.textbox.filename 
        path = os.path.realpath(filename)
        ext = os.path.splitext(path)[1].replace('.', '')        
        if ext in ['svg', 'png', 'jpg']:               
           #self.start_process(['xviewer', path])
           viewer = ImageViewer(self, path)
           return  
        elif ext == 'rst':
            pypath = '/home/athena/src/menutext/rstview.py'
            self.start_process(['python3', pypath, path])
            return
        else:
           self.textbox.on_exec_cmd(event)
        
    def get_ini_filename(self):
        path = os.path.realpath(__file__)
        dir = os.path.dirname(path)
        if dir == '':
            fn = 'editor.ini'
        else:
            fn = dir + os.sep + 'editor.ini' 
        return fn
            
    def load_ini(self):
        self.update()
        fn = self.get_ini_filename()
        text = ''
        if os.path.exists(fn) == False:
            print(fn, 'not found')
            return
        else:
            with open(fn, 'r') as f:
                text = f.read()
                f.close()        
        if text.strip() == '':
           return 
        dct = eval(text)
        files = dct.get('files', [])        
        self.prjfile = dct.get('project', '')
        self.prjview.set_prj(self.prjfile)
        lastfile = None       
        self.vars['history'] = history = dct.get('history')                
        for fn in history:
            self.fav_dir_tree.add_file(fn)            
            path = fn.rsplit(os.sep, 1)[0]
            self.fav_dir_tree.add_dir(path)
        if not (self.filename == None or self.filename == ''):
           files.append(self.filename)    
        for filename in files:
           filename = os.path.realpath(filename)
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
        dct['project'] = self.prjfile
        n = len(self.vars['history'])
        if n > 15:
            n = 15
        dct['history'] = self.vars['history'][0:n]
        text = str(dct)
        fn = self.get_ini_filename()
        with open(fn, 'w') as f:
            f.write(text)
            f.close()
            
    def destroy(self):
        self.save_ini()
        
#----------------------------------------------------------------------------------                    	
def main(filename):      
    root = tk.Tk()
    root.title('TextEditor')
    root.geometry('1700x1000')    
    try:
        icon = '/home/athena/.icons/applications-astronomy.png'
        root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=icon))
    except:
        pass    
    frame = MenuTextFrame(root, filename)
    frame.pack(fill='both', expand=True)       
    frame.mainloop()             
    
if __name__ == '__main__':    
    filename = None
    srcpath = os.path.dirname(__file__)
    #print('argv', len(sys.argv))
    print(sys.argv)
    if len(sys.argv) > 1:
        filename = sys.argv[1]   
        filename = os.path.realpath(filename)  
        #srcpath = os.path.dirname(filename)   
        #print('argv', filename, srcpath)
    
    if os.path.exists(srcpath):
       os.chdir(srcpath)
    main(filename)
    




