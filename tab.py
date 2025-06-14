import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

class TextTab():
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

    def edit_selected_text(self, command):
        p = self.tag_ranges('sel')
        if p == ():
            idx1 = self.index('insert')
            idx2 = idx1.split('.')[0] + '.end'
        else:
            idx1, idx2 = p            
        text = self.get(idx1, idx2)
        text = command(text)
        self.replace(idx1, idx2, text)    
        self.tag_add('sel', idx1, idx2)        
            
    def add_tab(self, key=None, space=4):
        self.on_add_tab()
        
    def remove_tab(self, key=None, space=4):
        self.on_remove_tab()
        
    def on_add_tab(self, flag=None):        
        p = self.tag_ranges('sel')
        self.msg.puts(p)
        if p == ():
            self.puts('    ')
            self.update_all()   
            return
        self.select_lines()
        self.edit_selected_text(self.add_one_tab) 
        self.update_all()   	 
        
    def on_remove_tab(self, event=None):
        self.select_lines()
        self.edit_selected_text(self.remove_one_tab) 
        self.update_all()         

#----------------------------------------------------------------------------------      
if __name__ == '__main__':   
    from textbox import TextBox
    from messagebox import Messagebox     
    
    class TextBox1(TextBox, TextTab):
        def __init__(self, master, **kw):
            TextBox.__init__(self, master, **kw)        
            self.bind('<Tab>', self.on_add_tab)       
        def update_line_index(self):
            pass 
                
    def main():               
        #os.chdir('/home/athena/src/MenuEdit')
        root = tk.Tk()
        root.title('TextEditor')
        root.geometry('800x900')    
        frame = tk.Frame(root)
        frame.pack(fill='both', expand=True)  
        topframe = tk.Frame(frame)
        topframe.pack(side='top', fill='both', expand=True)
        bottomframe = tk.Frame(frame)       
        bottomframe.pack(side='bottom', fill='both', expand=True)
        textbox = TextBox1(topframe)
        textbox.pack(fill='both', expand=True)
        
        msg = Messagebox(bottomframe)        
        statusbar = msg.add_statusbar()
        msg.pack(side='bottom', fill='x', expand=False)
        textbox.msg = msg
        textbox.statusbar = statusbar        
    
        def fread(filename):
            with open(filename, 'r') as f:
                text = f.read()
                f.close()
                return text        
        
        def open_file(fn):
            if os.path.exists(fn) == False:
               return
            text = fread(fn)
            textbox.filename = fn
            textbox.set_text(text)
            root.title('TextEditor - ' + fn)
            
        def cmd_act(cmd, arg):
            print('cmd_act ', cmd, arg)
            if cmd == 'gotofile':
               if textbox.filename != arg:                  
                  open_file(arg)
            elif cmd == 'gotoline':
               textbox.cmdlist.append((cmd, int(arg)))
               #print('goto', int(arg), len(textbox.items))
            elif cmd == 'goto':
               textbox.cmdlist.append((cmd, int(arg)))               
            textbox.event_generate('<<check_cmd_list>>')  
                 
        msg.action = cmd_act  
        fn = __file__
        open_file(fn) 
        frame.mainloop()       
        
    main()












