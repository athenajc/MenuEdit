import tkinter as tk
import re
import tkcode

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
           
#------------------------------------------------------------------------------------------
class PopMenu():    
    def add_popmenu(self, cmds=[]):
        menu = tk.Menu(self)
        self.menu = menu
        for p in cmds:
            if p[0] == '-':
                menu.add_separator()
            else:
                menu.add_command(label=p[0], command=p[1])         
        self.menu = menu   
        self.menu.show = False
        self.bind('<ButtonRelease-1>', self.unpost_menu)
        self.bind('<ButtonRelease-3>', self.post_menu) 
        return self             

    def unpost_menu(self, event=None):
        if self.menu.show:
           self.menu.unpost()
        
    def post_menu(self, event=None):
        x, y = event.x, event.y   
        x1 = self.winfo_rootx()     
        y1 = self.winfo_rooty()
        self.menu.post(x + x1, y + y1)           
        self.menu.show = True

#-------------------------------------------------------------------------------------------  
class TextLinebar(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, **kw)  
        self.config(background='#ccc')
        n = 50
        label0 = tk.Label(self, text='\n'*n, background='#ccc', width=5, anchor='nw')
        label0.pack(side='left', fill='y', expand='False')        
        self.textvar = tk.StringVar()
        label = tk.Label(self, background='#ccc', anchor='ne')
        label.place(x=1,y=0)    
        label.config(textvariable=self.textvar) 
        label.config(font='Mono 10', foreground='#333')
        self.label = label 
        self.set_range(1, n)
            
    def scroll_set(self, i0, i1, bboxcmd):               
        if i1 == 0:
            return      
        bbox = bboxcmd(str(i0) + '.0')  
        if bbox == None:
            return       
        y0 = bbox[1] 
        ytop = y0 - 2              
        text = ''       
        top = i0                    
        if i1 - i0 < 40:
            i1 = i0 + 40
        for i in range(i0, i1+1):
             bbox = bboxcmd(str(i+1) + '.0')
             if bbox != None:                 
                 y = bbox[1]     
                 h = int((y - y0)/bbox[3])
                 if h == 0:
                     h = 1
                 else:
                     text += '%5d '% i + '\n' * h
                 y0 = y
             else:
                 text += '%5d '% i + '\n'
        self.textvar.set(text)
        self.label.place(x=0, y=ytop)  
        self.update()
        
    def set_range(self, i0, i1=None):
        text = ''          
        for i in range(i0, i1):
            text += '%5d \n' % i
        self.textvar.set(text)  

#----------------------------------------------------------------------------------  
class TextObj(tk.Text):
    def __init__(self, master, **kw):
        tk.Text.__init__(self, master, **kw)
        self.vars = {}
        self.text = None       
        self.msg = None
        self.config(foreground='#121')
        self.config(background='#f5f5f3')    
        self.tag_config('bold', font='Mono 10 bold', background='#ddd')         
        
    def clear_all(self):
        self.tag_delete(self.tag_names())
        self.delete('1.0', 'end')              
        
    def select_none(self):
        self.tag_remove('sel', '1.0', 'end')
        
    def on_select_all(self):
        self.tag_add('sel', '1.0', 'end')
        
    def on_copy(self, event=None):
        self.clipboard_clear()
        text = self.get_text('sel')
        self.clipboard_append(text)   
        
    def on_paste(self, event=None):
        text = self.clipboard_get()
        self.puts(text)
        
    def goto(self, p):
        if re.match('\d+', p) == None:
            return
        self.select_none()
        self.see(p + '.0')
        self.tag_add('sel', p + '.0', p + '.end')       
        
    def get_idx(self, i, j):  
        if j == 'e':
            return str(i) + '.end'
        return '%d.%d' % (i, j)
            
    def get_pos(self, idx):
        p = self.index(idx).split('.')
        return (int(p[0]), int(p[1]))
        
    def puts(self, *lst, end='\n'):
        text = ''
        for s in lst:
            text += str(s) + ' '
        self.insert('insert', text + end)
        
    def puts_tag(self, text, tag=None, head='', end='\n'):
        self.insert('insert', head)        
        idx1 = self.index('insert')
        self.insert('insert', text)        
        idx2 = self.index('insert')
        if tag != None:
            self.tag_add(tag, idx1, idx2)
        self.insert('insert', end)          
    
    def list_str(self, lst):
        t = ' '
        text = ''
        n = int(self.winfo_reqwidth() / 20)
        for s in lst:
            t += s.ljust(20) + ' '
            if len(t) > n:
                text += t + '\n'
                t = ' '
        return text + t
        
    def put_list(self, lst, bychar=False):
        if bychar == False:      
            self.puts(self.list_str(lst))
        else:
            dct = {}
            lst1 = []
            for s in lst:
                c = s[0].lower()
                if not c in lst1:
                    lst1.append(c)
            lst1.sort()
            for c in lst1:
                dct[c] = []
            for s in lst:
                c = s[0].lower()
                dct[c].append(s)
            self.print_dct(dct)
        
    def print_dct(self, dct):
        for s, v in dct.items():
            if v == []:
                continue
            self.puts_tag(s[0].upper()+s[1:], 'bold', head='\n', end='\n')
            self.put_list(v)  
    
    def set_text(self, text):
        self.clear_all()
        self.text = text
        self.insert('insert', text)         
        
    def get_text(self, tag=None):
        if tag != None:
            p = self.tag_ranges(tag)
            if p == ():
                return ''
            idx1, idx2 = p
            return self.get(idx1, idx2)
        return self.get('1.0', 'end -1c')     
                    
    def get_line_index(self, idx='current'):
        if type(idx) == int:
            return idx
        if type(idx) == str:
            if re.fullmatch('\d+', idx) != None:
               return int(idx)
            idx = self.index(idx)
        idx = self.index(idx).split('.')[0]
        return int(idx)

    def get_line_text(self, idx=None):
        if idx == None or idx == 'current':
            idx = self.index('insert')
            p = idx.split('.')[0]
        elif type(idx) == int:
            p = str(idx)
        else:
            p = idx.split('.')[0]
        idx1 = p + '.0'
        idx2 = p + '.end'
        return self.get(idx1, idx2)
        
    def get_word(self, idx='insert'):
        i, j = self.get_pos(idx)
        text = self.get_line_text(i)
        for m in re.finditer('[\w\.]+', text):
            if j >= m.start() and j <= m.end():
                return m.group(0)
        return ''

    def find_text(self, key=None):
        if self.msg == None:
            return
        #self.msg.clear_all()
        if key == None:
            key = self.get_word('insert')        
        text = self.get_text()  
        self.msg.puts('Textobj find text: %s' % key) 
        if not key in text:
            return False
        lst = []
        i = 0               
        for line in text.splitlines():     
            i += 1       
            for m in re.finditer(key, line):
                s, e = m.start(), m.end()
                self.msg.puts_tag(line[s:e], 'bold', head =' %4d ' %i + line[:s], end=line[e:]+'\n')
                lst.append(i)
        return lst
        
    def delete_range(self, p):
        self.delete(p[0], p[1])
        
    def add_widget(self, index, widget):
        self.window_create(index, window=widget)
        
    def add_button(self, index, text, command=None, **kw):        
        button = tk.Button(self, text=text, command=command, **kw)
        self.window_create(index, window=button)
        end = self.index('end')
        self.tag_add('button', index, end)
        button.range = (index, end)
        return button

    def flush(self, text=''):
        return
        
    def write(self, text):
        if text.strip() == '':
            return
        self.insert('insert', str(text))
        
#----------------------------------------------------------------------------------  
class FrameLayout():        
    def add_frame(self, frame, type=None, xsep=None, ysep=None):
        f0 = tk.Frame(frame)
        f1 = tk.Frame(frame)
        if type == 'v':            
            f0.pack(side='top', fill='x', expand=False)             
            f1.pack(side='top', fill='both', expand=True)  
        elif type == 'h':    
            f0.pack(side='left', fill='y', expand=False) 
            f1.pack(side='left', fill='both', expand=True)
        elif xsep != None:
            f0.place(x=0, y=0, relwidth=xsep, relheight=1)
            f1.place(relx=xsep, y=0, relwidth=1-xsep, relheight=1) 
        elif ysep != None:
            f0.place(x=0, y=0, relwidth=1, relheight=ysep)
            f1.place(x=0, rely=ysep, relwidth=1, relheight=1-ysep) 
        return f0, f1

    def add_spliter(self, master, ysep=0.5):
        frame0 = tk.Frame(master)
        frame1 = tk.Frame(master)
        frame0.place(x=0, y=0, relwidth=1, relheight=ysep)
        framespliter = tk.Frame(master, relief='raise', bd=1)
        framespliter.place(x=0, rely=ysep, relwidth=1, height=6)
        framespliter.config(cursor='hand2')
        dh = 6/1000
        frame1.place(x=0, rely=ysep+dh, relwidth=1, relheight=1-ysep-dh)
        framespliter.bind('<B1-Motion>', self.drag_spliter)
        framespliter.y = ysep
        self.spliter = framespliter
        framespliter.f0 = frame0
        framespliter.f1 = frame1      
        return frame0, frame1
        
    def drag_spliter(self, event):
        obj = event.widget
        h = self.winfo_height()
        obj.y += (event.y / h) /3
        if obj.y < 0.1:
            obj.y = 0.1
        elif obj.y > 0.9:
            obj.y = 0.9           
        y1 = obj.y + (6 / h)
        obj.place(rely = obj.y)
        obj.f0.place(relheight=obj.y)        
        obj.f1.place(rely=y1, relheight=1-y1)     
        
    def add_spliter_h(self, frame, xsep=0.5):
        frameleft = tk.Frame(frame)
        frameleft.place(x=0, y=0, relwidth=xsep, relheight=1)
        framespliter = tk.Frame(frame, relief='raise', bd=1)
        framespliter.place(relx=xsep, y=0, width=6, relheight=1)
        framespliter.config(cursor='hand2')
        frameright = tk.Frame(frame)
        dw = 6/1600
        frameright.place(relx=xsep+dw, y=0, relwidth=1-xsep-dw, relheight=1)
        framespliter.bind('<B1-Motion>', self.drag_spliter_h)
        framespliter.x = xsep
        self.spliter_h = framespliter
        framespliter.f0 = frameleft
        framespliter.f1 = frameright    
        return frameleft, frameright 
        
    def drag_spliter_h(self, event):
        w = self.winfo_width()
        obj = event.widget    
        obj.x += (event.x / w) /3
        if obj.x < 0.1:
            obj.x = 0.1
        if obj.x > 0.9:
            obj.x = 0.9        
        x1 = obj.x + (6 / w)     
        obj.place(relx = obj.x)
        obj.f0.place(relwidth=obj.x)        
        obj.f1.place(relx=x1, relwidth=1-x1)         

      

def test_textobj():               
    from ui import TwoFrame, MsgBox
    from fileio import fread
    root = tk.Tk()
    root.title('TextEditor')
    root.geometry('800x900')    
    frame = TwoFrame(root, type='v', sep=0.8)
    frame.pack(fill='both', expand=True) 
    textobj = TextObj(frame.top)
    textobj.pack(fill='both', expand=True)
    msg = MsgBox(frame.bottom)
    msg.pack(fill='both', expand=True)        
    textobj.msg = msg
    text = fread(__file__)  
    textobj.set_text(text)
    frame.mainloop()                 

if __name__ == '__main__':     
    test_textobj()

