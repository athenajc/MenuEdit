import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

class Dialog(tk.Toplevel):
    def __init__(self, parent, x, y, title = None):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = None
        self.initial_focus = None        
        
    def init_dialog(self, x, y):
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)
        self.geometry("+%d+%d" % (x, y))
        self.initial_focus.focus_set()
        self.wait_window(self)
        
    def add_entry(self, master, labeltext='', default_text='', w=7):
        frame = tk.Frame(master)
        frame.pack()
        label = tk.Label(frame, text=labeltext, width=w)
        label.pack(side='left')
        entry = tk.Entry(frame)
        entry.pack(side='left')
        entry.insert(0, default_text)
        return entry        

    def close_dialog(self):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()       
        
class ReplaceDialog(Dialog):
    def __init__(self, parent, x, y, title = None, find='', replace=''):    
        Dialog.__init__(self, parent, x, y, title) 
        self.findstr = find
        self.replacestr = replace
        self.act_args = ()
        self.init_ui()
        self.init_dialog(x, y)                      
        
    def init_ui(self):
        topframe = tk.Frame(self)
        topframe.pack(side='top', fill='both', expand=True)
        bodyframe = tk.Frame(topframe)
        self.initial_focus = self.add_body(bodyframe)
        bodyframe.pack(side='left', padx=5, pady=5)
        rightframe = tk.Frame(topframe)
        rightframe.pack(side='right', padx=5, pady=5)
        bottomframe = tk.Frame(self)
        bottomframe.pack(side='bottom', padx=5, pady=5)
        self.buttonbox(rightframe, bottomframe)

    def add_body(self, master):
        self.entryfind = self.add_entry(master, 'Find', self.findstr, w=7)
        self.entryreplace = self.add_entry(master, 'Replace', self.replacestr, w=7)        

    def buttonbox(self, rightframe, bottomframe):
        box = tk.Frame(bottomframe)
        bnFindNext = tk.Button(rightframe, text="Find Next", width=10, command=self.on_find_next)
        bnFindNext.pack(side='left', padx=5, pady=5)        
        bnReplaceOne = tk.Button(box, text="Replace one", width=10, command=self.on_replace_one)
        bnReplaceOne.pack(side='left', padx=5, pady=5)        
        bnReplaceAll = tk.Button(box, text="Replace all", width=10, command=self.on_replace_all, default='active')
        bnReplaceAll.pack(side='left', padx=5, pady=5)
        bnCancel = tk.Button(box, text="Cancel", width=10, command=self.on_cancel)
        bnCancel.pack(side='left', padx=5, pady=5)
        self.bind("<Return>", self.on_replace_all)
        self.bind("<Escape>", self.on_cancel)
        box.pack()

    def validate(self):
        return 1 # override   
        
    def do_action(self, act=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.act_args = (act, self.entryfind.get(), self.entryreplace.get())
        self.close_dialog()
        
    def on_replace_one(self, event=None):
        self.do_action("Replace one")
        
    def on_replace_all(self, event=None):
        self.do_action("Replace all") 
        
    def on_find_next(self, event=None):
        self.do_action("Find Next") 
        
    def on_cancel(self, event=None):
        self.close_dialog()       
           

#----------------------------------------------------------------------------------      
if __name__ == '__main__':   
    from textbox import ScrollText
    from messagebox import Messagebox     
    
    class TextBox1(ScrollText):
        def __init__(self, master, **kw):
            ScrollText.__init__(self, master, **kw)        
            self.bind('<Control-r>', self.on_replace)
            self.bind('<Control-f>', self.on_replace)        
       
        def find_next(self, s):
            self.find_text(s)   
            current = self.index('sel.first + %dc' % len(s))
            idx1 = self.search(s, current, stopindex='end')
            if idx1 == '':
                idx1 = self.search(s, '0.0')
                if idx1 == '':
                    return False
            idx2 = self.index(idx1 + '+%dc' % len(s))
            self.msg.puts('tag_add', idx1, idx2)       
            self.tag_remove('sel', '1.0', 'end')     
            self.see(idx1)
            self.tag_add('sel', idx1, idx2)
            
        def replace_range(self, idx1, idx2, find, replace):
            self.msg.puts('Replace selected text: (%s->%s)' % (find, replace) )    
            find_str = find
            replace_str = replace
            stop = False
            n0, n1 = len(find_str), len(replace_str)
            while not stop:
                index = self.search(find_str, idx1, stopindex=idx2)
                if index == '':
                    stop = True
                    break
                i = int(self.index(index).split('.')[1])      
                self.replace(index, index + ' +%dc' % n0, replace_str)
                line = self.get_line_text(index)
                self.msg.puts(index, idx1, line[:i], end='')
                self.msg.puts_tag(find_str + '==>' + replace_str, tag='bold', end=line[i + n1:]+'\n') 
            self.update_all()       
                
        def do_replace(self, args):
            if args == None or args == ():
                return
            self.msg.puts('do_replace', args)
            act, find, replace = args
            self.vars['find'] = find
            self.vars['replace'] = replace
            if act == "Replace all":
               self.replace_range('0.0', 'end', find, replace)
            elif act ==  "Replace one":
               p = self.tag_ranges('sel')
               if p == ():
                  idx1 = self.index('current wordstart')
                  idx2 = self.index(idx1 + '+%dc' % len(find))
               else:
                  idx1, idx2 = p
               self.replace_range(idx1, idx2, find, replace)  
            elif act == "Find Next":
               self.find_next(find) 
               self.open_replace_dialog()
            
        def open_replace_dialog(self):                       
            find = '' #self.vars.get('find', '')
            replace = self.vars.get('replace', '')
            if find == '':
                find = self.get_text('sel')
                if find == '':
                    w = self.get_current_word()
                    if not '\n' in w:
                        find = w
            idx = self.index('sel.first')
            bbox = self.bbox(idx)            
            if bbox == None:
                x, y = 400, 400
            else:
                x, y, w, h = bbox    
            x += self.winfo_rootx() + 100
            y += self.winfo_rooty() + 100
            self.msg.puts(x, y)
            sel_range = self.tag_ranges('sel.first') 
            if sel_range != ():
                idx1, idx2 = sel_range
                self.tag_add('sel', idx1, idx2)
            dialog = ReplaceDialog(self, x, y, 'Replace', find=find, replace=replace)
            self.do_replace(dialog.act_args)
            
        def on_replace(self, event=None):
            self.open_replace_dialog()
                
    def main():               
        os.chdir('/home/athena/src/menutext')
        root = tk.Tk()
        root.title('TextEditor')
        root.geometry('800x900')    
        frame = tk.Frame(root)
        frame.pack(fill='both', expand=True)  
        bottomframe = tk.Frame(frame)       
        bottomframe.pack(side='bottom', fill='both', expand=True)
        msg = Messagebox(bottomframe)        
        statusbar = msg.add_statusbar()
        msg.pack(side='bottom', fill='x', expand=False)
        
        topframe = tk.Frame(frame)
        topframe.pack(side='top', fill='both', expand=True)
        textbox = TextBox1(topframe)
        textbox.pack(fill='both', expand=True)
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








