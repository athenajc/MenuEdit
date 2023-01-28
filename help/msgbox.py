import tkinter as tk
from aui import PopMenu, TagTextObj 
import re
 
class HelpMsgBox(TagTextObj, PopMenu):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.config(width=50)
        self.helpbox = None
        self.msg = self
        self.cmds = {}                      
        self.bind_cmd('c,clear', self.cmd_clear)        
        self.bind_cmd('doc', self.cmd_doc)
        self.bind_cmd('dir', self.cmd_dir)       
        self.bind_cmd('f,find', self.cmd_find)
        self.bind_cmd('go,goto', self.cmd_goto)        
        menucmds = []        
        menucmds.append(('Goto', self.cmd_goto))
        menucmds.append(('Find', self.cmd_find)) 
        menucmds.append(('-'))
        menucmds.append(('Copy', self.on_copy))
        menucmds.append(('Paste', self.on_paste))
        menucmds.append(('-'))
        menucmds.append(('Clear', self.cmd_clear))        
        self.add_popmenu(menucmds)
        self.click_time = 0
        self.bind('<ButtonRelease-1>', self.on_button1_up)
        self.bind('<Return>', self.on_enter)
        self.pack(fill='both', expand=True)
        
    def on_enter(self, event=None):        
        text = self.get('insert linestart', 'insert lineend').strip()
        if text == '':
            return
        self.puts('\nYou enter :' + text)
        if ' ' in text:
            cmd, arg = text.split(' ', 1)
            if cmd in self.cmds:
                action = self.cmds.get(cmd)
                action(arg)
        
    def on_doubleclick(self):
        helpbox = self.get_helpbox()
        if helpbox == None:
            return
        idx = self.index('insert')
        text = self.get_line_text(idx).strip()        
        for s in re.findall('\d+', text):
            helpbox.goto(int(s) + 1)
            return
                
    def on_button1_up(self, event):
        self.menu.unpost()
        if event.time - self.click_time < 300:
            self.on_doubleclick()
        self.click_time = event.time      
        
    def bind_cmd(self, key, action):
        for s in key.split(','):
            s = s.strip()
            if s == '':
                continue
            self.cmds[s] = action   
          
    def cmd_clear(self, arg=None):
        self.clear_all()
        
    def cmd_doc(self, arg):
        if arg == '':
            arg = 'self'
        self.puts(arg)
        obj = get_obj(arg) 
        self.puts(inspect.getdoc(obj))
        
    def cmd_dir(self, arg=None):
        self.puts(arg)
        obj = get_obj(arg)        
        self.put_list(dir(obj))
  
    def cmd_find(self, arg=None):
        helpbox = self.get_helpbox()
        if helpbox == None:
            return
        if arg == None:
            arg = self.get_word()
            
        pos = helpbox.search(arg, 'insert +10c')
        self.puts(pos)
        if pos == '' or pos == None:
            return
        helpbox.goto(pos)        
            
    def cmd_goto(self, arg=None):
        helpbox = self.get_helpbox()
        if helpbox == None:
            return
        if arg == None:
            text = self.get_line_text()
            lst = re.findall('\s\d+\s', text)
            if lst == []:
                arg = self.get_word()
            else:
                arg = lst[0].strip()
        helpbox.goto(arg)  
        
    def get_helpbox(self, action=None): 
        if self.helpbox != None:
            return self.helpbox      
        root = self.winfo_toplevel()       
        if hasattr(root, 'helpbox'):
            self.helpbox = root.helpbox
            return root.helpbox
            
    def get_textbox(self, action=None): 
        if self.helpbox != None:
            return self.helpbox      
        root = self.winfo_toplevel()       
        if hasattr(root, 'helpbox'):
            self.helpbox = root.helpbox
            return root.helpbox

if __name__ == '__main__':
    from aui import *
    from helpframe import HelpFrame
    frame = App(title='APP', size=(600,860))
    #frame1 = twoframev(frame, sep=0.7)
    #msg = HelpMsgBox(frame1.bottom)
    helpbox = HelpFrame(frame)
    frame.mainloop()
