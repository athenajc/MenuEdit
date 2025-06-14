import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import PIL
from PIL import Image, ImageTk
from aui.ImageObj import ImageObj, load_svg
from fileio import *

font = PIL.ImageFont.truetype('ChinSong1.ttf', 14) 
docpath = '/home/athena/文件/Keep/text'

def text2image(filename, size=(128, 128)):
    text = fread(filename)
    w, h = size
    image = PIL.Image.new(size=(w, h), mode='RGBA')
    draw = PIL.ImageDraw.Draw(image)
    draw.rectangle((0, 0, w, h), fill='white')
    n = min(len(text), 300)
    lst = []
    i = 0
    while i < n:
        n1 = 32        
        w1 = font.getbbox(text[i:i+n1])[0]
        if n1 < 100:
           n1 += (100 - w1) // 18        
        lst.append(text[i:i+n1])
        i += n1
    text = '\n'.join(lst[:8])    
    draw.multiline_text((5, 5), text, fill='black', font=font)
    draw.rectangle((w-3, 0, w, h), fill='white')
    draw.rectangle((0, h-3, w, h), fill='white')
    return image

imgdct = {}
thumbdct = {}
def init_thumb():
    image = load_svg(filename='/home/athena/data/svg/thumb.svg', size=(146, 146))
    imgdct['thumb.tkimage'] = image

    
def load_thumb(filename):
    if filename in thumbdct:
        return thumbdct[filename]
    filepath = realpath(filename)
    #img = ImageObj(filepath, size=(90, 90))
    #tkimage = img.get_tkimage()
    image = text2image(filepath)
    tkimage = PIL.ImageTk.PhotoImage(image)
    thumbdct[filename] = tkimage
    return tkimage
     

class Canvas(tk.Canvas):
    def __init__(self, master,  **kw):           
        super().__init__(master, **kw)
        self.rect = self.create_rectangle        
        
class ImageThumb(Canvas):
    def __init__(self, master, filename, size):
        w, h = size           
        super().__init__(master, width=w, height=h)
        self.size = w, h
        self.selected = False
        self.bg = '#f5f3f3'
        self.outline = '#999' 
        self.fill = self.bg
        thumbtk = imgdct.get('thumb.tkimage')
        self.create_image(0, 0, image=thumbtk, anchor='nw', tag='frame')
        
        self.tkimage = load_thumb(filename)
        self.create_image(w//2-4, h//2-4, image=self.tkimage,  tag='imageobj')      
       
        fn = filename.split(os.sep)[-1] 
        self.create_text(w//2-3, h-15, text=fn, anchor='n', tag='text', font=('mono',8))
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)      
        #self.bind('<ButtonRelease-1>', self.on_click)
        
    def on_select(self, selected):
        self.selected = selected        
        if self.selected:
            w, h = self.size
            item = self.create_rectangle(0, 0, w-10, h, fill='gray', outline='#999', tag='selected') 
            self.tag_lower('selected')
        else:
            self.delete('selected')
            
    def on_click(self, event):
        self.selected = not self.selected
        self.on_select(self.selected)
       
    def on_enter(self, event=None):
        self.itemconfigure('rect', fill='yellow', outline='yellow')        
        
    def on_leave(self, event=None):        
        self.itemconfigure('rect', fill=self.bg, outline=self.outline)  
        
class ImageGrid(tk.Frame):
    def __init__(self, master):   
        super().__init__(master)
        self.row, self.col = 0, 0
        self.w = 400
        self.cellsize = (150, 150)
        self.objs = []
        self.clear_all()
        self.bind('<Configure>', self.on_configure)         
        
    def on_click(self, event):
        for obj in self.objs:
            if obj == event.widget:
                obj.on_select(True)
            elif obj.selected:
                obj.on_select(False)        
            
    def on_configure(self, event):
        w, h = event.width, event.height
        d = w - self.w
        if d > -5 and d < 5:
            return
        self.w = w
        self.row, self.col = 0, 0
        for obj in self.objs:
            self.grid_obj(obj)
        
    def clear_all(self):
        self.row, self.col = 0, 0
        self.objs = []
        
    def is_image(self, fn):
        ext = fn.split('.')[-1]
        if ext in ['svg', 'png', 'gif', 'jpg']:
            return True
        else:
            return False
            
    def add_dir(self, path):        
        lst = os.listdir(path)
        lst.sort()
        if path[-1] != os.sep:
            path += os.sep
        for s in lst[0:10]:
            fn = path + s
            if os.path.isfile(fn):
                self.add_image(fn)
                
    def grid_obj(self, obj):
        obj.grid(row=self.row, column=self.col, padx=2, pady=2)
        self.col += 1
        w, h = self.cellsize
        if self.col * w + w > self.w:
            self.row += 1
            self.col = 0
            
    def add_image(self, fn):
        w, h = self.cellsize
        obj = ImageThumb(self, fn, size=(w, h))
        self.objs.append(obj)
        self.grid_obj(obj)
        obj.bind('<ButtonRelease-1>', self.on_click)
        return obj
        

class Frame(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, **kw)
        init_thumb()
        self.pack(fill='both', expand=True)
        frame = tk.Frame(self)
        frame.pack(fill='x', expand=False)
        button = tk.Button(frame, text='Add file', bg='#eaeaea')
        button.pack(side='left', fill='none', expand=False)
        button.bind('<ButtonRelease-1>', self.on_open_file)
        self.grid = ImageGrid(self)
        self.grid.pack(fill='both', expand=True)
        
        self.grid.add_dir(docpath)        
         
    def file_dialog(self, dialog, op='Open', mode='r'):        
        filepath = dirname(realpath(docpath))        
        filename = dialog(defaultextension='.svg', mode = mode,
               filetypes = [('Image files', '.*'), ('all files', '.*')],
               initialdir = filepath,
               initialfile = '',
               parent = self,
               title = op + ' File dialog'
               )
        if filename == None:
            return None
        return filename.name                
                
    def open_file(self, filename):
        obj = self.grid.add_image(filename)
        obj.filename = filename
        
    def on_open_file(self, event=None):   
        filename = self.file_dialog(filedialog.askopenfile, 'Open', 'r')   
        print('Filedialog return (%s)'%filename) 
        if filename == None or filename == '':
            return
        self.open_file(filename)
            
if __name__ == '__main__':   
    from aui import App
    app = App('Image Grid', size=(1000, 1000))
    
    frame = Frame(app)
    app.mainloop()
    


