import tkinter as tk
from tkinter.simpledialog import Dialog
import numpy as np

lst = ['gray', 'brg', 'nipy_spectral', 'winter', 'viridis', 'ocean', 'inferno', 'cividis', 'gist_heat', 'copper']

def get_rgb(color):
    v = eval(color.replace('#', '0x'))
    b = v % 256
    g = int(v/256) % 256
    r = int(v/(256*256))
    return r, g, b
    
def clip(v):
    v = int(v)
    if v < 0:
        v = 0
    if v > 255:
        v = 255
    return v               
    
class GradBar(tk.Canvas):
    def __init__(self, master, x, y, w, h, color):
        super().__init__(master, width=w, height=h, border=2, relief='sunken', bg='#eaeaea')
        self.canvas = master        
        self.w, self.h = w+2, h+1
        self.rgb = get_rgb(color)
        self.color = color
        self.tag = 'Graybar'                     
        self.bind('<Button-1>', self.pick_color)
        master.add((x, y), self, self.tag)  
        self.objs = []
        self.draw()       
        
    def set_rgb(self, r, g, b):
        self.rgb = r, g, b
        self.draw()       
        
    def get_color(self):        
        return self.color
        
    def draw(self):
        for item in self.objs:
            self.delete(item)        
        n = 16      
        w = self.w / n
        r, g, b = self.rgb
        d = 128
        R = np.linspace(r-d, r+d, n)
        G = np.linspace(g-d, g+d, n)
        B = np.linspace(b-d, b+d, n)
        X = np.linspace(1, self.w, n)
        self.objs = []
        for x, r, g, b in zip(X, R, G, B):            
            color = '#%02x%02x%02x' % (clip(r), clip(g), clip(b) )
            item = self.create_rectangle(x, 1, x+w, self.h, fill=color, outline='', tag=color)   
            self.objs.append(item)
          
    def pick_color(self, event):
        x, y = event.x, event.y
        item = self.find_closest(x, y)
        tag = self.gettags(item)
        if tag == ():
            return
        self.canvas.set_by_grad(tag[0])
        
class RgbBar(tk.Canvas):
    def __init__(self, master, x, y, w, h, color):
        super().__init__(master, width=w, height=h, border=2, relief='sunken', bg='#eaeaea')
        self.canvas = master        
        self.w, self.h = w+2, h+1
        self.color = color
        self.value = 128
        self.tag = color + 'bar'               
        self.bar = self.create_rectangle(1, 1, self.w, self.h, fill=self.color, outline='')        
        self.bind('<B1-Motion>', self.on_b1_motion)
        self.bind('<Button-1>', self.on_b1_motion)
        master.add((x, y), self, self.tag)  
        self.draw()       
        
    def set_value(self, value):
        self.value = value
        self.draw()       
        
    def get_color(self):
        r, g, b = 0, 0, 0
        if self.color == 'red':
            r = self.value
        elif self.color == 'green':
            g = self.value
        else:
            b = self.value
        color = '#%02x%02x%02x' % (r, g, b) 
        return color
        
    def draw(self):
        w =  self.w * self.value / 255
        self.delete(self.bar)
        color = self.get_color()     
        self.bar = self.create_rectangle(1, 1, w, self.h, fill=color, outline='')   
        
    def on_b1_motion(self, event):
        w = self.canvasx(event.x)
        if w > self.w:
            w = self.w
        if w < 0:
            w = 0
        self.value = int(w * 255 / self.w)
        self.canvas.update_rgb()
        
    
class ColorCanvas(tk.Canvas):
    def __init__(self, master, color, **kw):
        super().__init__(master, **kw)
        from aui.ImageObj import cmap_colorbar
        self.color = color
        self.w = w = 600
        img = cmap_colorbar(lst, size=(w, 350))
        self.add_colorlabel(20, 10, color, 'src')
        self.add_colorlabel(20, 60, color, '')
        self.add_rgbbar(180, 7, w-205, 28, color)        
        item = self.add_image((0, 145), img, tag='colorbar')
        self.colorbar = img
        self.name = 'colorbar'
        self.tag_bind('colorbar', '<Button-1>', self.pick_color)
        
    def add(self, pos, widget, tag='widget'):
        x, y = pos
        item = self.create_window(x, y, window=widget, tag=tag)   
        self.moveto(item, x=x, y=y)
        
    def add_colorlabel(self, x, y, color, tag=''):        
        self.create_text(x, y+20, text=color, fill='black', font=(20), anchor='w', tag=tag+'name')
        x = x + 100
        self.create_rectangle(x, y, x+40, y+40, fill=color, outline='black', width=1, tag=tag+'color')
        
    def add_rgbbar(self, x, y, w, h, color):       
        R = RgbBar(self, x, y, w, h, 'red')
        G = RgbBar(self, x, y + h + 5, w, h, 'green')
        B = RgbBar(self, x, y + h * 2 + 8, w, h, 'blue') 
        self.gradbar = GradBar(self, 10, 110, self.w-26, 28, color)
        self.rgbbars = (R, G, B)        
        r, g, b = get_rgb(color)
        self.set_rgbvalue(r, g, b)        
        
    def add_image(self, pos, imageobj, anchor='nw', tag='imageobj'): 
        self.tkimage = imageobj.get_tkimage()      
        x, y = pos
        imageobj.pos = pos
        item = self.create_image(x, y, image=self.tkimage, anchor=anchor, tag=tag) 
        return item        
        
    def set_rgbvalue(self, r, g, b):        
        self.rgbbars[0].set_value(r)
        self.rgbbars[1].set_value(g)
        self.rgbbars[2].set_value(b)
        self.gradbar.set_rgb(r, g, b)
        
    def get_rgbvalues(self):    
        R, G, B = self.rgbbars
        r = R.value
        g = G.value
        b = B.value
        return r, g, b
        
    def update_rgb(self):
        r, g, b = self.get_rgbvalues()
        self.set_rgba((r, g, b, 256))        
        
    def set_by_grad(self, color):
        r, g, b = get_rgb(color)
        self.set_rgba((r, g, b, 256))        
        
    def set_rgba(self, rgba):
        r, g, b, a = rgba        
        self.set_rgbvalue(r, g, b)
        self.color_updated = True        
        color = '#%02x%02x%02x' % (r, g, b)   
        self.itemconfig('color', fill=color)
        self.itemconfig('name', text=color)
        self.color = color
        
    def pick_color(self, event):
        x, y = event.x, event.y    
        obj = event.widget        
        img = obj.colorbar
        ox, oy = img.pos
        rgba = img.get_pixel(x -ox, y-oy)
        self.set_rgba(rgba)
               
      
class ColorDialog(Dialog):
    def __init__(self, parent, title = 'Color Chooser', color = 'white', **kw):
        self.parent = parent
        self.color = color
        super().__init__(parent, title, **kw)                 
        
    def body(self, master):       
        canvas = ColorCanvas(master, self.color)
        canvas.config(width=600, height=450)
        canvas.pack(fill='both', expand=True)
        self.canvas = canvas
        
    def apply(self):
        self.parent.color = self.canvas.color 
        
    def destroy(self):        
        self.canvas = None
        Dialog.destroy(self)
        

def chooser_color(master, color):
    master.color = color
    dialog = ColorDialog(master, color=color)    
    return  master.color
    

def on_colorbutton(event):
    button = event.widget
    res = chooser_color(button, button.color)
    button.config(bg=button.color, text=button.color)
    

def color_canvas(panel, button, size=(600, 400)):
    w, h = size
    canvas = ColorCanvas(panel, button.color)
    canvas.config(width=w, height=h)
    panel.add(canvas)
    
    
if __name__ == '__main__':
    from aui import App          
    
    app = App(size=(600, 700))
    panel = app.add('panel')
    panel.pack()
    button = panel.add_button('test', on_colorbutton)
    button.color = button.cget('bg')
    button.panel = panel
    panel.add_colorbar()
    panel.add_sep(size=(1000, 30))
    color_canvas(panel, button, app.size)
    app.mainloop()




