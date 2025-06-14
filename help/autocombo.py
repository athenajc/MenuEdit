#python3
# tkinter tk.Text autocompletion
import os
import re
import tkinter as tk
from tkinter import ttk
from get_modules import *
    
class AutoCombo(ttk.Combobox):
    def __init__(self, master, auto=False, **kw):
        ttk.Combobox.__init__(self, master, **kw)
        self.auto = auto
        self.default_values = list(self['values'])
        self._values = self.default_values
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace('w', self.on_changed)       
        self.pre_token = '' 
        
    def on_changed(self, name, index, mode):    
        if self.get() == self.pre_token:
            return
        self.event_generate('<<TextChanged>>')      
        token = self.get()
        if token == '':
            self['values'] = self.default_values
            self.close_listbox()
            self.pre_token = token
            return
        if self.auto == True:
            if token[-1] == '.':
                self['values'] = get_lst(token.rsplit('.', 1)[0])  
                #self.event_generate('<Down>')                     
                    
        words = self.comparison()        
        if len(words) == 1:
            if len(token) > len(self.pre_token):
                word = words[0]           
                n = len(token) 
                self.insert(n, words[0][n:])
                self.update()
        if words:
            self.update_listbox(words)
        else:
            self.close_listbox()
        self.pre_token = token

    def set_list(self, words):
        self['values'] = words 
        
    def set_text(self, text):
        self.var.set(text)
        
    def close_listbox(self):
        self.event_generate('<Up>')
        
    def update_listbox(self, words):
        if 0: #self.auto == True:
            self['values'] = words        
        
    def matches(self, fieldValue, acListEntry):
        pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
        return re.match(pattern, acListEntry)

    def comparison(self):
        return [ w for w in self['values'] if self.matches(self.var.get(), w) ]
        

if __name__ == '__main__':   
    from aui import TextObj
    import pydoc
    import pathlib
    import sys
    import inspect
    import pkgutil

    class Frame(tk.Frame):
        def __init__(self, master):       
            tk.Frame.__init__(self, master)
            frame = tk.Frame(self)
            frame.pack(fill='both', expand=False)
            lst = list(sys.modules.keys())
    
            self.entry = AutoCombo(frame, auto=True, values=lst, width=32)
            self.entry.pack(side='left', fill='x', expand=False, padx=10)
    
            button = tk.Button(frame, text='Enter')
            button.pack(side='left', expand=False)
            
            self.text = TextObj(self)
            self.text.pack(fill='both', expand=True)
            self.puts = self.text.puts
            self.entry.puts = self.text.puts
            
            button.bind("<ButtonRelease-1>", self.on_click)
            self.entry.bind("<<ComboboxSelected>>", self.on_click)
    
        def get_help(self, objname): 
            try:
                obj, name = pydoc.resolve(objname)
                text = pydoc.render_doc(obj, title='\nPython Library Documentation: \n    %s')
            except:
                print('get_help error')
                text = ''
            return text
    
        def on_click(self, event):
            self.entry.close_listbox()
            self.text.clear_all()
            text = self.get_help(self.entry.get())
            self.text.puts(text)
            self.text.tag_block()
    
    def main():
        root = tk.Tk()
        root.geometry('500x500+400+200')
        root.title('Auto Complete Combo')
        frame = Frame(root)
        frame.pack(fill='both', expand=True)
        sys.stdout = frame.text
        frame.mainloop()
 
    main()
