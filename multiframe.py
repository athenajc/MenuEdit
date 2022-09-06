import os
import re
import sys
import time
import inspect
import subprocess
import tkinter as tk
from tkinter import filedialog
from textbox import TextBox
from messagebox import Messagebox

class TwoFrame(tk.Frame):
    def __init__(self, master, type='v', sep=0.3, cnf={}, **kw):
        tk.Frame.__init__(self, master)  
        if type == 'h':
            self.init_h(sep)
        else:
            self.init_v(sep)
     
    def init_v(self, ysep): 
        frame0 = tk.Frame(self)
        frame0.place(x=0, y=0, relwidth=1, relheight=ysep)
        framespliter = tk.Frame(self, relief='raise', bd=1)
        framespliter.place(x=0, rely=ysep, relwidth=1, height=8)
        framespliter.config(cursor='hand2')
        frame1 = tk.Frame(self)
        dh = 8/1000
        frame1.place(x=0, rely=ysep+dh, relwidth=1, relheight=1-ysep-dh)
        framespliter.bind('<B1-Motion>', self.drag_spliter_v)
        framespliter.y = ysep
        self.spliter = framespliter
        self.f0 = frame0
        self.f1 = frame1
        self.top = frame0
        self.bottom = frame1
        
    def drag_spliter_v(self, event):
        y = event.y
        obj = self.spliter    
        ay = abs(y)    
        h = self.winfo_height()
        dh = (ay / h) /3
        if y < -1 and obj.y > 0.1:
            obj.y -= dh
        elif y > 1 and obj.y < 0.9:
            obj.y += dh           
        obj.place(rely = obj.y)
        self.f0.place(relheight=obj.y)
        y1 = obj.y + (5 / self.winfo_height())
        self.f1.place(rely=y1, relheight=1-y1)       
    
    def init_h(self, xsep):
        frameleft = tk.Frame(self)
        frameleft.place(x=0, y=0, relwidth=xsep, relheight=1)
        framespliter = tk.Frame(self, relief='raise', bd=1)
        framespliter.place(relx=xsep, y=0, width=6, relheight=1)
        framespliter.config(cursor='hand2')
        frameright = tk.Frame(self)
        dw = 6/1600
        frameright.place(relx=xsep+dw, y=0, relwidth=1-xsep-dw, relheight=1)
        framespliter.bind('<B1-Motion>', self.drag_spliter_h)
        framespliter.x = xsep
        self.spliter = framespliter
        self.f0 = frameleft
        self.f1 = frameright
        self.left = frameleft
        self.right = frameright        
        
    def drag_spliter_h(self, event):
        x = event.x
        obj = self.spliter    
        ax = abs(x)    
        w = self.winfo_width()
        dw = (ax / w) /3
        if x < -1 and obj.x > 0.1:
            obj.x -= dw
        elif x > 1 and obj.x < 0.9:
            obj.x += dw           
        obj.place(relx = obj.x)
        self.f0.place(relwidth=obj.x)
        x1 = obj.x + (6 / self.winfo_width())
        self.f1.place(relx=x1, relwidth=1-x1)      
        
class MenuFrame(tk.Frame):
    def __init__(self, master, items=[], cnf={}, **kw):
        tk.Frame.__init__(self, master, **kw)
        self.button = {}
        for key in items:
            if key != '':
                self.button[key] = tk.Button(self, text=key, relief='flat')
                self.button[key].pack(side='left')   
            label = tk.Label(self, text='|', fg='#aaa')
            label.pack(side='left')                
        self.entry = tk.Entry(self)
        self.entry.pack(side='left')  

    def bind_action(self, item, action):
        self.button[item].bind('<ButtonRelease-1>', action)    
        

class NoteButton(tk.Canvas):
    def __init__(self, master, text='', cnf={}, **kw):
        tk.Canvas.__init__(self, master)
        self.w = 175
        self.h = 28
        self.text = text
        self.draw_button(text)  

        self.bind('<Enter>', self.on_enter)    
        self.bind('<Leave>', self.on_leave)
        self.bind('<ButtonPress-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.tag_bind('btn', '<ButtonRelease-1>', self.on_click_tag)   
        
    def set_active(self, active=False):
        self.active = active
        if self.active:
            self.itemconfigure('bg',fill='#bbb')
            self.itemconfigure('text',fill='#000', activefill='#000')
            self.itemconfigure('line0',fill='#fff')
            x = self.w - 16
            y = 0
            self.create_text(x-0, y+0, text='x', anchor='nw', fill='#eee', activefill='#fff',  tag='btn0') 
            self.create_text(x-1, y+1, text='x', anchor='nw', fill='#777', activefill='#222',  tag='btn0') 
            self.create_text(x-1, y+1, text='x', anchor='nw', fill='#777', activefill='#000',  tag='btn')              
        else:
            self.delete('btn0')
            self.delete('btn')
            self.itemconfigure('bg',fill='#ddd')        
            self.itemconfigure('text',fill='#777', activefill='#333')
            self.itemconfigure('line0',fill='#ccc')
        
    def draw_button(self, text):
        h = self.h
        text = '    ' + text + '    '
        w = int(len(text) * 7.5)
        self.w = w
        self.active = False
        self.config(width=w+1, height=h+1)
        self.action = {}        
        self.create_rectangle(1, 1, w, h+3, fill='#ccc', tag='bg')
        self.create_line(1, h+3, 1, 1, w-1, 1, fill='#fff', tag='line0') 
        self.create_line(w-1, 1, w-1, h+3,       fill='#000', tag='line1')        
        self.create_text(5, 2, text=text, anchor='nw', fill='#777', activefill='#000', tag='text') 
        
    def set_text(self, text):    
        self.delete('bg')        
        self.delete('line0')
        self.delete('line1')
        self.delete('text')        
        self.text = text
        self.draw_button(text)
        
    def bindact(self, name, action):
        self.action[name] = action
        
    def on_click_tag(self, event):
        name = self.itemcget('current', option='text')      
        action = self.action.get(name)  
        if action == None:
            return
        event.text = self.text
        event.name = name
        action(event)        
        
    def on_press(self, event):
        self.itemconfigure('line0',fill='#000')
        self.itemconfigure('line1',fill='#fff')
        self.itemconfigure('bg',fill='#ccc')

    def on_release(self, event):
        if self.active:
            self.itemconfigure('line0',fill='#fff')
        else:
            self.itemconfigure('line0',fill='#ccc')
        self.itemconfigure('line1',fill='#000')
        self.itemconfigure('bg',fill='#ccc')        
        
    def on_enter(self, event):
        if self.active:
            self.itemconfigure('bg',fill='#eee')
        else:
            self.itemconfigure('bg',fill='#eee')
        
    def on_leave(self, event):
        if self.active:
            self.itemconfigure('bg',fill='#ccc')
        else:
            self.itemconfigure('bg',fill='#ddd')
            
class MultiFrame(tk.Frame):
    def __init__(self, master, switch_action=None, close_action=None, cnf={}, **kw):
        tk.Frame.__init__(self, master)
        self.master = master
        self.switch_action = switch_action
        self.close_action = close_action
        frame1 = tk.Frame(self)
        frame1.pack(side='top', fill='y', expand=False)

        self.init_buttons(frame1)
        self.panel = tk.Frame(self)
        self.panel.pack(side='top', fill='both', expand=True)
        self.obj = {}
        
    def add_frame(self, name, content, widgetclass):
        obj = widgetclass(self.panel)
        obj.place(x=0, y=0, relwidth=1, relheight=1)
        self.obj[name] = obj
        button = self.add_button(name, content, self.on_switch)
        obj.button = button
        button.obj = obj
        self.current = name
        obj.objname = name
        return obj  

    def init_buttons(self, frame):
        frame2 = tk.Frame(frame)
        frame2.place(x=0, y=2, relwidth=1, relheight=1)        
        self.frametop = frame2
        label = tk.Label(frame, text = ' ' * 16, width=600)
        label.pack(fill='both', expand=True)          
        frame2.lift()
        self.button = {}
        
    def add_button(self, name, content='', action=None):
        button = NoteButton(self.frametop, text=content, width=16)
        button.name = name
        button.pack(side='left', fill='both', expand='false')
        if action != None:
            button.bind('<ButtonPress-1>', action)
        button.bindact('x', self.on_close)
        self.button[name] = button
        self.update_buttons(name)        
        return button
        
    def remove_button(self, name):
        button = self.button.get(name)
        if button == None:
            return
        button.pack_forget()
        self.button.pop(name)
        button.destroy()
        button = None
        for s in self.button.keys():
            self.switch_to(s)
            break
        
    def bind_action(self, name, action):
        self.button[name].bind('<ButtonPress-1>', action)       
    
    def update_buttons(self, key): 
        for name in self.button:
            button = self.button[name]
            button.set_active(name == key) 
        
    def switch_to(self, name, event=None):
        if self.obj.get(name) == None:
            return
        self.current = name
        self.obj[name].lift()
        self.update_buttons(name)          
        self.switch_action(name)  
        
    def on_switch(self, event):
        self.switch_to(event.widget.name, event)
        
    def on_close(self, event):
        if self.close_action != None:
            self.after(10, self.close_action)
    
    def change_name(self, name, content):
        old = self.current
        button = self.button.pop(old)
        button.name = name
        self.button[name] = button
        obj = self.obj[self.current]
        obj.name = name
        self.obj[name] = obj
        self.obj.pop(self.current)
        self.current = name         
        button.set_text(content)  
             
class MultiTextFrame(tk.Frame):
    def __init__(self, root, master, switch_action=None, cnf={}, **kw):
        tk.Frame.__init__(self, master)
        self.root = root
        self.parent_switch_action = switch_action
        self.textframe = None
        self.textobj = {}        
        self.multiframe = MultiFrame(self, self.on_switch_frame, self.on_close_frame)
        self.multiframe.pack(fill='both', expand=True)                
                   
    def get_text(self, tag=None):
        if self.textframe == None:
            return ''
        return self.textframe.get_text(tag)
        
    def new_file(self):
        if self.textobj.get('noname') == None:
            textframe = self.add_fileframe('noname', TextFrame)
            textframe.textbox.set_text('\n'*25)
            return textframe
        for i in range(1, 5):
            name = 'noname_' + str(i)
            if self.textobj.get(name) == None:
                textframe = self.add_fileframe(name, TextFrame)
                textframe.textbox.set_text('\n'*25)
                return textframe
        return None
        
    def switch_to(self, widget, filename):
        self.textframe = widget
        self.parent_switch_action(widget, filename)
        
    def on_switch_frame(self, filename):        
        widget = self.textobj.get(filename)
        if widget == None:
            print(filename, ' not found')
            return
        self.switch_to(widget, filename)
        return widget
        
    def on_close_frame(self): 
        self.close_file()  
            
    def add_fileframe(self, filename, widgetclass):        
        labeltext = os.path.split(filename)[-1]
        objname = filename
        widget = self.multiframe.add_frame(objname, labeltext, widgetclass)
        widget.set_root(self.root)
        widget.filename = filename
        self.textobj[filename] = widget        
        self.switch_to(widget, filename)
        return widget    
        
    def close_frame(self, widget):
        if self.textobj == {}:
            return 'error'
        filename = widget.filename            
        self.multiframe.remove_button(filename)        
        widget.place_forget()
        widget.destroy()
        if filename in self.textobj:
            self.textobj.pop(filename)     
        else:
            print('Error ', filename, ' not found')
        if self.textobj == {}:
            return 'empty'
        for name in self.textobj:    
            self.on_switch_frame(name)
            break            

    def file_dialog(self, dialog, op='Open', mode='r'):
        filename = dialog(defaultextension='.py', mode = mode,
               filetypes = [('Python files', '.py'), ('all files', '.*')],
               initialdir = '/home/athena/src/py',
               initialfile = '',
               parent = self,
               title = op + ' File dialog'
               )
        if filename == None:
            return None
        return filename.name
        
    def open_file(self, filename): 
        if len(self.textobj) >= 6:
            self.msg.puts('File count %d : Open too much!' % len(self.textobj) )
            return                 
        filename = os.path.realpath(filename)
        if filename in self.textobj:            
            textframe = self.on_switch_frame(filename)
            self.multiframe.switch_to(filename)
            return textframe        
        textframe = self.add_fileframe(filename, TextBox) 
        textframe.open_file(filename)  
        self.switch_to(textframe, filename)
        return textframe       
        
    def on_new_file(self, event=None):
        self.textframe = self.new_file()
        
    def on_open_file(self, event=None):   
        if len(self.textobj) >= 6:
            self.msg.puts('File count %d : Open too much!' % len(self.textobj) )
            return  
        filename = self.file_dialog(filedialog.askopenfile, 'Open', 'r')   
        print('Filedialog return (%s)'%filename) 
        if filename == None or filename == '':
            return
        self.textframe = self.open_file(filename)
            
    def on_saveas_file(self, event=None):
        filename = self.file_dialog(filedialog.asksaveasfile, 'Save as', 'w')           
        if filename == None or filename == '':
            print('Error : Filedialog return (%s)'%filename) 
            return
        print('Filedialog return (%s)'%filename)         
        self.saveas_file(filename)        
        
    def on_save_file(self, event=None):   
        self.save_file(filename) 
        
    def on_close_file(self, event=None):   
        self.close_file() 
        
    def change_filename(self, oldname, filename):                
        labeltext = os.path.split(filename)[-1]
        self.multiframe.change_name(filename, labeltext)                
        obj = self.textobj.pop(oldname)
        obj.filename = filename
        self.textobj[filename] = obj
        
    def saveas_file(self, filename):
        oldname = self.textframe.filename
        self.textframe.saveas_file(filename)
        self.change_filename(oldname, filename)
        self.on_switch_frame(filename)
        
    def save_file(self):
        self.textframe.save_file()
         
    def close_file(self):
        self.close_frame(self.textframe)
        if self.textobj == {}:
            self.new_file()                   

    def on_exec(self, event):
        if self.textframe == None:
            return                
        self.msg.clear_all()
        text = self.textframe.get_text()
        text = text.replace('\n', '\n    ')
        text = 'def test_test1():\n    ' + text + '\ntest_test1()'
        exec(text)          
        return
        
    def on_button_action(self, act):
        act = act.strip()
        if act.find('save as') == 0:
            act = act.replace('save as', 'saveas')
        if ' ' in act:
            args = act.split(' ')
            cmd = args.pop(0)    
        if act == 'new':
            self.on_new_file()
        elif act == 'open':
            self.on_open_file()            
        elif act == 'save':
            self.textframe.save_file()
        elif act == 'saveas':
            self.on_saveas_file()
        elif act == 'close':
            self.on_close_file()            
        else:
            self.textframe.on_button_action(act)   

    def on_entry_input(self, event):
        key = event.keysym
        text = event.widget.get()
        if key == 'Return':
            self.on_button_action(text)            
    
    def exec_file(self, filename):
        self.msg.puts(time.ctime())
        self.msg.puts('exec', filename)
        if filename.endswith('.py'):
            cmd = 'python3'
        else:
            cmd = '/bin/bash'
        self.msg.puts(cmd)
        proc = subprocess.Popen([cmd, filename])

    def on_test_file(self, event=None):
        self.msg.clear_all()
        filename = self.textframe.filename
        self.textframe.save_file()
        self.exec_file(filename)
        
if __name__ == '__main__':       
                
    class MultiFrameTester(tk.Frame):
        def __init__(self, master, filename, cnf={}, **kw):
            tk.Frame.__init__(self, master)
            self.root = master                
            menubar = MenuFrame(self, items='New,Open,Save,Save as,Close,Test'.split(','))
            menubar.pack(side='top', fill='x', expand=False)        
            frame = TwoFrame(self, sep=0.6, type='v')
            frame.pack(fill='both', expand=True)        
            msgbox = Messagebox(frame.bottom)   
            msgbox.pack(fill='x', expand=False)    
            msgbox.parent = self
            self.msg = msgbox               
            textframe = MultiTextFrame(self, frame.top, self.switch_frame)
            textframe.pack(fill='both', expand=True)
            self.textframe = textframe                
            textframe.msg = msgbox
            textframe.puts = msgbox.puts
                              
            self.open_file(filename)
             
            menubar.bind_action('New', self.textframe.on_new_file)
            menubar.bind_action('Open', self.textframe.on_open_file)
            menubar.bind_action('Save', self.textframe.on_save_file)
            menubar.bind_action('Save as', self.textframe.on_saveas_file)
            menubar.bind_action('Close', self.textframe.on_close_file)    
            menubar.bind_action('Test', self.textframe.on_test_file)
            menubar.entry.bind('<KeyRelease>', self.textframe.on_entry_input) 
            
        def getobj(self, name):
            if name == 'msg':
                return self.msg
            elif name == 'statusbar':
                return None
            return None
            
        def switch_frame(self, widget, filename):
            self.current_file = widget.filename
            self.root.title('Test MultiFrame - [ %s ]' % widget.filename)
    
        def open_file(self, filename):        
            self.textframe.open_file(filename)
             
        def close_file(self):
            self.textframe.close_file()
            
        def test_file(self, filename):
            self.textframe.exec_file(filename)
            
        def do_update(self, flag=None):
            pass
                
    def test_textframe(root, filename):
        root.title('Test TextFrame - ' + filename)
        frame = TextFrame(root)
        frame.textbox.open_file(filename)
        frame.pack(fill='both', expand=True)
        frame.mainloop()    
        
    def test_multiframe(root, filename):
        root.title('Test MultiFrame - ' + filename)
        frame = MultiFrameTester(root, filename)
        frame.pack(fill='both', expand=True)
        frame.mainloop()
                                   
    def main(filename):
        root = tk.Tk()    
        root.geometry('1200x900')
        test_multiframe(root, filename)    

    os.chdir('/home/athena/src/py')
    main('/home/athena/src/py/tmp/t.py')


