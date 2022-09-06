import os
import re
import sys
import tkinter as tk


class RstText(tk.Text):
    def __init__(self, master, **kw):
        tk.Text.__init__(self, master, **kw)
        self.text = ''    
        self.config(dict(padx=10, pady=10))
        self.vars = {}
        self.bg = self.cget('background')
        self.init_config()
        self.init_pattern()  
        
    def init_config(self):    
        monofont = ('Mono', 10)       
        self.color = '#121'
        self.config(font=monofont)
        self.config(padx=5)
        self.config(foreground=self.color)
        self.config(background='#f5f5f3')        
        self.config(undo=99)          
        self.config(exportselection=True)
        self.vars = {}
        self.key_tagnames = ['key', 'class', 'classname', 'str1', 'str2', 'int', 'op', 'self', 'comments']
        bold = (monofont[0], monofont[1], 'bold')
        self.tag_config('text', font='Mono 10')
        self.tag_config('h1', font='Mono 20 bold', foreground='#333') 
        self.tag_config('h2', font='Mono 18 bold', foreground='#333') 
        self.tag_config('h3', font='Mono 16 bold', foreground='#333') 
        self.tag_config('h4', font='Mono 14 bold', foreground='#333') 
        self.tag_config('h5', font='Mono 13 bold', foreground='#333') 
        self.tag_config('h6', font='Mono 12 bold', foreground='#333') 
        self.tag_config('h7', font='Mono 11 bold', foreground='#333')
        self.tag_config('title', font='Mono 10 bold', foreground='#000')          
        self.tag_config('toc', font='Mono 10 bold', foreground='#000')  
        self.tag_config('bold', font='Mono 10 bold')
        self.tag_config('italic', font='Mono 10 italic bold') 
        self.tag_config('fix', font='TkFixedFont 10', foreground='#222', background='#e2e1e2')   
        self.tag_config('squote', font='Mono 10', foreground='#000', background='#ddd')     

        self.tag_config('key', font=bold, foreground='#338')
        self.tag_config('class', font=bold, foreground='#338')
        self.tag_config('classname', font=bold, foreground='#383')
        self.tag_config('str1', foreground='#c83')
        self.tag_config('str2', foreground='#c83')
        self.tag_config('int',  foreground='#383')
        self.tag_config('op',  foreground='gray')
        self.tag_config('self',  foreground='#333')
        self.tag_config('comments',  foreground='#789')
        self.tag_config('selected',  background='lightgray')
        self.tag_config('hilight',  background='yellow')
             
        self.tag_config('block', font='Mono 10 bold', foreground='#555', background='#ddd')   
        self.tag_config('colon', font='Mono 10 bold', foreground='#555')
        
        self.tag_config('sectnum', font='Mono 10', foreground='#222')
        self.tag_config('gray', font='Mono 10', foreground='#333')        
        self.tag_config('dot', font='Mono 6', foreground='#333')       
                
    def init_pattern(self):            
        h = '#*=*=~-'
        self.dct123 = {'#':'h1', '*':'h2', '=':'h3'}
        self.dct456 = {'*':'h4', '=':'h5', '~':'h6', '-':'h7'}
        
        p = '\*\*(?P<bold>[^\*]+)\*\*|\*(?P<italic>[^\*]+)\*|\`\`(?P<fix>[^\`]+)\`\`|\`(?P<squote>[^\`]+)\`'      
        self.pattern = re.compile(p)
         
        p0 = '\.\.\s(?P<cmd>\w+)\:\:(?P<content>.*)'
        p1 = '\#\#+(?P<h1>[^\#]+)\#\#+\n|\*\*+(?P<h2>[^\*]+)\*\*+\n|\=\=+(?P<h3>[^\=]+)\=\=+\n'
        p2 = '\n(?P<h5>[^\n]+)\n\=\=+\n|\n(?P<h6>[^\n]+)\n\~\~+\n'
        p3 = '\n(?P<h4>[^\n]+)\n\*\*+\n|\n(?P<h7>[^\n]+)\n\-\-+\n'
        p4 = '\n(?P<minus>\s*\-\s*\w[^(\n\n)]+)|(?<=\:)(?P<colon>\:\n\n)'       
        p = '(%s)|(%s)|(%s)|(%s)|(%s)' % (p0, p1, p2, p3, p4)
        self.rst_pattern = re.compile(p)
        
    def click_link(self, event=None):
        link = event.widget
        idx0, idx1 = self.tag_nextrange(link.goto, '0.0')
        self.tag_remove('sel', '0.0', 'end')        
        a = self.index(idx0 + '+10l')        
        self.see(a)
        self.tag_add('sel', idx0, idx1)
               
    def add_link(self, text, goto):
        cnf = dict(activeforeground='white', fg='black')
        bg = self.cget('background')
        link = tk.Label(self, text=text, font=('Mono 10 underline'), relief='flat', fg='black', bg=bg)
        link.goto = goto
        link.pack()
        link.bind('<Button-1>', self.click_link)
        link.bind('<Enter>', lambda e: e.widget.config(fg='grey', cursor='arrow'))
        link.bind('<Leave>', lambda e: e.widget.config(fg='black'))
        self.window_create('end', window=link)
        self.insert('end', '\n')
        
    def add_label(self, text, tag):
        font = self.tag_cget(tag, 'font')
        fg = self.tag_cget(tag, 'foreground')   
        bg = self.cget('background')    
        n = text.count('\n')
        dct = {'h1':(49,3, 'center'), 'h2':(56,2, 'center'), 'h3':(60,1, 'center')}
        w, h, jst = dct.get(tag, (80, n+2, 'left'))        
        label = tk.Label(self, text=text, width=w, height=h, font=font, fg=fg, bg=bg, justify=jst)
        label.pack(fill='x', expand=True)        
        self.window_create('end', window=label)
        
    def add_text(self, text, tag='text'):
        n = text.count('\n')  
        tbox = tk.Text(self, height=n+1, relief='flat', padx=20, pady=10)
        tbox.pack(fill='x', expand=True) 
        tbox.insert('end', text) 
        self.window_create('end', window=tbox)
            
    def add_dot(self, dtype='dot'):
        bg = self.cget('background')
        canvas = tk.Canvas(self, width=12, height=12, bg=bg, highlightthickness=0)
        canvas.create_oval((3, 3, 10, 10), fill='black', width = 3)
        self.window_create('end', window=canvas)
        
    def split_tokens(self, text):    
        lst = [] 
        for m in re.finditer(self.pattern, text):
            i, j = m.start(), m.end()            
            for tag, s in m.groupdict().items():
                if s != None:                           
                    lst.append((s, text.find(s, i), tag))  
        return lst
        
    def add_tag_list(self, i, lst):
        head = str(i) + '.'
        for p in lst:        
            s, j, tag = p
            idx1 = head + str(j)
            idx2 = head + str(j+len(s))
            self.tag_add(tag, idx1, idx2)
        
    def remove_tags(self, idx1, idx2):        
        for s in self.key_tagnames:
            self.tag_remove(s, idx1, idx2)
            
    def puts_tag(self, text, tag=None, head='', end='\n'):
        self.insert('insert', head)        
        idx1 = self.index('insert')
        self.insert('insert', text)        
        idx2 = self.index('insert')
        if tag != None:
            if type(tag) == str:
                self.tag_add(tag, idx1, idx2)
            else:
                i = int(idx1.split('.')[0])
                self.add_tag_list(i, tag)
        self.insert('insert', end)
        return idx1, idx2
        
    def get_sectnum(self):
        lst = []
        for m in re.finditer('(?P<sect>[^\n]+)\n\~+\n', self.text):
            sect = m.group('sect')
            lst.append(sect)            
        self.sects = lst    
            
    def put_contents(self, text):
        self.puts_tag(text, 'toc')        
        i = 1
        for sect in self.sects:            
            s = str(i) + '. ' + sect   
            self.puts('  ', end='')
            self.add_link(s, 'section' + str(i))    
            i += 1
            
    def get_command(self, cmd, content):
        print((cmd, content))
        if cmd == 'sectnum':
            self.get_sectnum()
        elif cmd == 'contents':
            self.put_contents(content)            
    
    def parse_line(self, dct):      
        tag = dct.get('tag')
        #if tag != 'text':
        #   print('tag', tag, dct.get(tag))
        if tag in ['h1', 'h2', 'h3']:
            self.add_label(dct.get(tag), tag)
        elif tag in ['h4', 'h5', 'h6', 'h7']  :
            self.puts('')
            if tag == 'h6':
                tag1 = 'section' + str(self.sectindex)
                self.puts(' ' + dct.get(tag) + ' ', (tag, tag1))
                self.sectindex += 1
            else:
                self.puts(' ' + dct.get(tag) + ' ', tag)
        elif tag == 'content':
            self.get_command(dct.get('cmd'), dct.get('content'))
            self.puts('')
        elif tag == 'minus':
            text = dct.get(tag)  
            i = text.find(text.strip())
            if i <= 1:
               self.puts('●', 'dot', end='')
               self.puts(text.strip()[1:])
            else:        
               text = text[0:i] + '⦁' + text[i+1:]
               self.puts_text(text)
        elif tag == 'colon':
            text = dct.get(tag)
            self.puts('')
            self.add_text(text, 'block')
        else:
            self.puts_text(dct.get('text'))                
        
    def rst_reader(self, text):        
        lst = []
        i0 = 0
        for m in re.finditer(self.rst_pattern, text):
            i, j = m.span()
            if i - i0 > 1:
               lst.append(dict(tag='text', text=text[i0:i], span=(i0, i)))
            dct = dict(keys=[])   
            for k, v in m.groupdict().items():
                if v != None:
                    dct[k] = v
                    dct['tag'] = k     
                    dct['keys'].append(k)
            if dct.get('tag') == 'colon':
                j1 = text.find('\n\n', j+2)
                dct['colon'] = text[j+2:j1]            
                j = j1
            dct['text'] = text[i:j]
            dct['span'] = (i, j)
            lst.append(dct)
            i0 = j
            
        for dct in lst:                   
            self.parse_line(dct)       
                                    
    def clear_all(self):
        self.delete('0.0', 'end')
        
    def puts(self, text='', tag=None, end='\n'):
        if tag == None:
           self.insert('end', text + end)
        else:
           self.insert('end', ' ' + text + ' ', tag)
           self.insert('end', end)
        
    def puts_text(self, text, end='\n'):          
        i0 = 0
        for m in re.finditer(self.pattern, text):
            i, j = m.span()
            self.insert('end', text[i0:i])
            for k, v in m.groupdict().items():     
                if v != None:
                   if '\n' in v:
                       s0, s1 = v.split('\n')
                       self.puts(s0 + ' ', k, end='\n')  
                       self.puts(s1, k, end='')  
                   else:
                       self.puts(v, k, end='')  
            i0 = j 
        self.insert('end', text[i0:] + end)                  
        
    def set_text(self, text):
        self.clear_all()   
        self.text = text  
        self.sectindex = 1
        self.rst_reader(self.text)               
        #self.scrollbar.lift()
        
class RstView(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, **kw)
        self.textbox = RstText(self, width=100)
        self.textbox.pack(side='left',fill='both', expand=True)
        self.add_scrollbar()
        
    def add_scrollbar(self):        
        scrollbar = tk.Scrollbar(self, command=self.textbox.yview)
        scrollbar.pack(side='right', fill='y', expand=False)
        self.scrollbar = scrollbar
        self.textbox.config(yscrollcommand = self.on_scroll)    
        
    def on_scroll(self, arg0, arg1):
        self.scrollbar.set(arg0, arg1)    
        
    def set_text(self, text):
        self.textbox.set_text(text)
        
#----------------------------------------------------------------------------------      
if __name__ == '__main__':   
    from fileio import fread
    
    class Frame(tk.Frame):    
        def __init__(self, master, filename=None, **kw):
            tk.Frame.__init__(self, master, **kw)
            textbox = RstView(self)
            textbox.pack(fill='both', expand=True)
            if filename != None:
               text = fread(filename)
               textbox.set_text(text)
            
    def main(filename=''):
        root = tk.Tk()
        root.title('Frame and Text')
        root.geometry('900x900')
        frame = Frame(root, filename)
        frame.pack(fill='both', expand=True)
        frame.mainloop()
    
    import os, sys            
    if len(sys.argv) > 1:
        filename = sys.argv[1] 
        main(filename=filename)        
    else:
        fn = '/home/athena/src/help/test.rst'
        main(fn)

