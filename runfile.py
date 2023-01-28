import sys
import os
import tkinter as tk
import subprocess
import threading
from subprocess import Popen, PIPE
import time
from aui import MenuBar, TwoFrame, TextObj
import fileio
import webbrowser
from fileio import *
        
def popen_run(cmds, filepath, server):
    puts = server.puts
    try:
        
        process = subprocess.Popen(cmds,
                                universal_newlines=True, bufsize=0,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        server.process = process
    except Exception as e:
        puts(e)
        process.running = False
        return 
    process.running = True
    
    while process.running:
        time.sleep(0.001)
        line = process.stdout.readline()
        if line != '':
            puts(line, end='')
        else:
            if process.poll() != None:
               process.running = False
               break    
    process.running = False
    
class RunServer():
    def __init__(self, master, filename):
        self.puts = master.puts
        self.master = master
        self.filename = filename    
        self.process = None   
        self.puts('Test %s ...' % filename) 
        self.run_test()       
        
    def run_test(self):
        fn = self.filename       
        path = os.path.dirname(fn)
        os.chdir(path) 
        if '.py' in fn:
            cmds = ['/usr/bin/python3', fn]
            arg = fn
        elif '.go' in fn:
            cmds = ['/usr/bin/go', 'run', fn]
            arg = fn
        self.thread = threading.Thread(target=popen_run, args=(cmds, fn, self))
        self.thread.daemon = True
        self.thread.start()  
        
    def stop(self):
        if self.process != None:
           self.process.running = False       


class RunFile(): 
    def run_py(self, filename):                
        self.server = RunServer(self, filename) 
        
    def start_process(self, cmd):
        #self.msg.puts(cmd)
        pass
             
    def open_html(self, url):        
        webbrowser.open(url, new=0, autoraise=True)        
            
    def run_others(self, path, ext):
        if ext == 'go':
            self.run_py(path)
        elif ext == 'html':
            self.open_html(path)
        elif ext in ['png', 'jpg']:             
           self.start_process(['xviewer', path])
        elif ext == 'svg':    
            pypath = '/home/athena/src/svg/svgpath.py'
            self.start_process(['python3', pypath, path])
        elif ext == 'rst':
            pypath = '/home/athena/src/menutext/rstview.py'
            self.start_process(['python3', pypath, path])
        elif ext == 'lua':    
            self.start_process(['lua', path]) 
            
    def check_file(self):
        text = self.textbox.get_text()       
        filename = self.textbox.filename     
        if filename == 'noname':
            filename = 'noname.py'
            filename = realpath(fileanme)
            fileio.fwrite(filename, text)
        else:            
            filename = realpath(filename)
            self.save_file(text, filename)
        path = os.path.dirname(filename)
        if '.' in filename:
            ext = filename.rsplit('.', 1)[-1]    
        else:
            ext = ''                
        return filename, path, ext, text    
            
    def do_run_file(self, event=None):
        if self.textbox == None:
            return       
        filename, path, ext, text = self.check_file()    
        self.msg.clear_all()    
        if ext != 'py':
            self.run_others(filename, ext)
        else:         
            res = compile(text, filename, 'exec')
            self.run_py(filename)         
               
    def do_exec(self):
        if self.textbox == None:
            return       
        self.msg.clear_all()     
        filename, path, ext, text = self.check_file()       
        if ext in ['svg', 'png', 'jpg']:               
           viewer = ui.ImageViewer(self, path)
           return  
        elif ext == 'rst':
            pypath = '/home/athena/src/menutext/rstview.py'
            self.start_process(['python3', pypath, path])
            return
        else:
            self.textbox.on_exec_cmd(event)     
   

class TestFrame(tk.Frame):
    def __init__(self, master, filename):       
        tk.Frame.__init__(self, master)
        button = tk.Button(self, text='Test', bg='#eaeaea', width=30, height=3)
        button.pack()
        button.bind('<Button-1>', self.on_click)
        self.entry = tk.Entry(self)
        self.entry.pack(fill='x', expand=False, padx=10, pady=3)         
        self.entry.insert(0, filename)           
        self.text = TextObj(self)
        self.text.pack(fill='both', expand=True)
        self.puts = self.text.puts         
        self.server = None 
        
    def precheck(self, filename):                
        text = fileio.fread(filename)
        try:
            res = compile(text, filename, 'exec')
            return True
        except Exception as e:
            self.puts(e)
            return False
            
    def on_click(self, event):
        filename = self.entry.get()        
        if not '.py' in filename or self.precheck(filename):
            self.server = RunServer(self, filename)    
                

def test_app(filename):
    from aui import App
    app = App('Test RunFile', size=(900, 800))
    app.root.geometry('900x800+400+100') 
    frame1 = TestFrame(app, filename)
    frame1.pack(fill='both', expand=True)    
    app.mainloop()

if __name__ == '__main__':  
    fn = '/home/athena/tmp/test_run.py' 
    fn = '/home/athena/src/menutext/get_functions.py'
    fn = '/home/athena/tmp/hello.go'
    test_app(fn)
    
    
    
