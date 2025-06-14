import numpy as np
from scipy.special import comb
import xml.etree.ElementTree as ET
import re
from PIL import Image, ImageTk, ImageDraw, ImageFont
import tkinter as tk
import matplotlib.path as mpath
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.figure import Figure
from matplotlib import patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon 
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import aui

#-------------------------------------------------------------------------------------------------------- 
class PatchObj(object):
    def __init__(self, mode,  points, ec, fc=None, lw=2):  
        if mode == 'pencil':
            patch = self.add_polygon(points, ec=ec, lw=lw)
        elif mode == 'rect':
            patch = self.add_rect(points, ec=ec, fc=fc, lw=lw)
        elif mode == 'line':
            patch = self.add_line(points, ec=ec, lw=lw)
        elif mode == 'curve':
            patch = self.add_path(points, ec=ec, lw=lw)
        else:
            patch = None
        self.mode = mode
        self.patch = patch
        self.obj = patch
        
    def set_points(self, points):
        patch = self.patch  
        mode = self.mode      
        if mode == 'pencil':
            patch.set_xy(points)
        elif mode == 'rect':
            x0, y0 = points[0]
            x1, y1 = points[-1]
            patch.set_width(x1-x0)
            patch.set_height(y1-y0)
        elif mode == 'line':
            patch.set_xy([points[0], points[-1]])
        elif mode == 'curve':
            path = self.get_path(points)
            patch.set_path(path)
        elif mode == 'text':
            patch.set_position(points[-1])    

    def add_polygon(self, points, fc='none', ec='black', lw=2, closed=False):
        patch = patches.Polygon(points, fc=fc, ec=ec, lw=lw)
        patch.set_closed(closed)        
        return patch
        
    def points_to_path(self, points):
        verts = [points[0]]
        codes = [Path.MOVETO]   
        for p in points[1:-1]:
            verts.append(p)
            codes.append(Path.CURVE3)               
        verts.append(points[-1])
        codes.append(Path.LINETO)
        path = Path(verts, codes) 
        return path
        
    def add_path(self, points, fc='none', ec='black', lw=2):
        path = self.points_to_path(points) 
        patch = patches.PathPatch(path, fc=fc, ec=ec, lw=lw)
        return patch
        
    def add_rect(self, points, fc='none', ec=(0,0,0), lw=2):
        x, y = points[0]
        x1, y1 = points[-1]
        patch = patches.Rectangle(points[0], x1-x, y1-y, fc=fc, ec=ec, lw=lw)
        return patch
        
    def add_line(self, points, fc='none', ec='black', lw=2):
        p0 = points[0]        
        p1 = points[-1]
        patch = patches.Polygon([p0, p1], fc=fc, ec=ec, lw=lw, closed=False)
        return patch        
        
#-------------------------------------------------------------------------------------------------------- 
class FigureAgg(object):
    def __init__(self, size, dpi, **kw):
        w, h = size               
        self.pixel_size = (w, h)
        self.dpi = dpi
        self.figure = self.create_figure(w/dpi, h/dpi, dpi)  

    def create_figure(self, w, h, dpi):        
        self.size = (w, h)
        figure = Figure(figsize=self.size, dpi=dpi, frameon=False)    
        FigureCanvasAgg(figure)        
        self.init_figure(figure)
        return figure
        
    def init_figure(self, figure):
        figure.clear()
        w, h = self.size
        figure.patch.set_visible(False)
        ax = figure.add_axes([0, 0, 1, 1]) 
        ax.set_ymargin(-0.01)
        ax.set_xmargin(-0.01)
        ax.axis('off') 
        ax.invert_yaxis()                 
        x = [0, w, w, 0, 0]
        y = [0, 0, h, h, 0]
        ax.plot(x, y)                
        figure.canvas.draw()
        self.figure_canvas = figure.canvas
        self.ax = ax
        
    def gradient(self, mode, colorname):
        w0, h0 = self.size
        m = h0/w0
        w, h = 50, int(50*m)
        mx = w / 2
        my = h / 2
        r = max(mx, my)*1.5            
        vfunc = np.vectorize(lambda y, x: ( (x-mx)**2 + (y-my)**2) ) 
        p = np.fromfunction(vfunc, (h, w))   
        p = np.sqrt(p) / r
        self.ax.imshow(p, interpolation='bilinear', cmap=colorname, extent=[0, w0, 0, h0])
        
    def add_patch(self, patch):
        self.ax.add_patch(patch)

    def set_size(self, size):        
        w, h = size        
        w = max(w, 60)
        h = max(h, 60)
        self.pixel_size = (w, h)
        self.canvas.delete('figure')
        w, h = w/self.dpi, h/self.dpi
        self.figure = self.create_figure(w, h, 100)        
        
    def update(self):
        self.figure.canvas.draw()
    
    def save(self, filename):
        self.figure.savefig(filename, dpi=100)     
        
    def get_rgba(self):
        rgba = np.asarray(self.figure_canvas.buffer_rgba())
        return rgba
        
    def get_image(self):   
        data, (w, h) = self.figure_canvas.print_to_buffer()  
        image = Image.frombytes("RGBA", (w, h), data, "raw")
        return image               
        
#-------------------------------------------------------------------------------------------------------- 
class FigureTk(FigureAgg):
    def __init__(self, canvas, size, **kw):     
        self.canvas = canvas
        w, h = size
        self.pixel_size = (w, h)
        dpi = 100
        self.dpi = dpi
        self.figure = self.create_figure(w/dpi, h/dpi, dpi)       
         
    def create_figure(self, w, h, dpi):
        self.size = (w, h)
        figure = Figure(figsize=(w, h), dpi=dpi, frameon=False)    
        figure.patch.set_visible(False)
        figure_canvas = FigureCanvasTkAgg(figure, self.canvas)      
        self.tkphoto = figure_canvas._tkphoto     
        self.canvas.create_image(0, 0, image=self.tkphoto, anchor='nw', tag='figure')  
        self.init_figure(figure)
        return figure           
   
    def add_text(self, x, y, text, font=None, color='black'):
        if font == None:
            font = ('Sans-Serif', 15)
        fname = font[0]
        size = font[1]
        print(text, size)
        obj = self.ax.text(x, y, text, fontsize=size, fontfamily=fname, color=color)    
        #obj = self.ax.text(x, y, text, fontsize=size, color=color)    
        obj.mode = 'text'    
        self.update() 
        return obj
        
    def add_patchobj(self, patch):
        self.ax.add_patch(patch.obj)
        
    def add_patch(self, mode, points, ec, lw=2):                
        patch = PatchObj(mode, points, ec, lw)
        self.ax.add_patch(patch.obj)
        return patch
            
    def set_patch_points(self, patch, points):
        if patch.mode == 'text':
            patch.set_position(points[-1])
        else:
            patch.set_points(points)
        self.update()  
        
class FigureCanvas(tk.Canvas):
    def __init__(self, master, width, height, **kw):
        super().__init__(master, **kw) 
        self.size = (width, height)
        self.line_width = 3
        self.points = []
        self.patches = []
        self.actions = []
        self.mode = 'curve'
        self.patch = None
        self.statusbar = None
        self.font = ('Sans-Serif', 16)
        self.textobj = None
        self.imageobj = None
        self.pause = False
        self.dpi = 100
        self.color = 'black'
        self.figure = FigureTk(self, (width, height))    
        self.bind('<B1-Motion>', self.on_button_motion)
        self.bind('<ButtonPress-1>', self.on_mousedown) 
        self.bind('<ButtonRelease-1>', self.on_mouseup) 
        self.bind('<Motion>', self.on_motion)
        self.bind_all('<KeyPress>', self.on_keydown) 
    
    def on_keydown(self, event):
        key = event.keysym    
        if key == 's':
            self.figure.save('test.svg')
        dct = {'l':'line', 'r':'rect', 'p':'pencil', 'c':'curve'}
        if key in dct:
            self.mode = dct[key]
        
    def on_motion(self, event):
        x, y = event.x/self.dpi, event.y/self.dpi
        if self.mode == 'text':
            if self.textobj == None:
                self.textobj = self.figure.add_text(x, y, self.input_text, self.font, self.color)
                print(self.textobj)
            else:
                self.textobj.set_position((x, y))
                self.figure.update()
            
    def on_mousedown(self, event):
        x, y = event.x/self.dpi, event.y/self.dpi
        self.points = [(x, y)]
        w, h = self.size
        #self.color = (x / w, y / h, (x + y) / (w+h))
        color = self.color
        if self.mode == 'text':
            self.patch = self.figure.add_text(x, y, self.input_text, self.font, self.color)
        elif self.mode == 'fill':
            return
        else:
            self.patch = PatchObj(self.mode, self.points, ec=color, fc='none', lw=self.line_width)  
            self.figure.ax.add_patch(self.patch.obj)    
        self.patches.append(self.patch)            
        
    def on_button_motion(self, event):  
        x, y = event.x, event.y  
        x1, y1 = (x/self.dpi, y/self.dpi)
        x0, y0 = self.points[-1]
        if max(abs(x1-x0), abs(y1-y0)) > 0.01:
           self.points.append((x1, y1)) 
        if self.patch != None:
            self.figure.set_patch_points(self.patch, self.points)            
            
    def on_mouseup(self, event):
        self.points = []
        self.patch = None
        
    def set_font(self, font=()):
        self.font = font
        name = font[0]
        size = font[1]        
        if self.textobj != None:
            self.textobj.set_fontname(name)
            self.textobj.set_fontsize(size)
            self.figure.update()
        
    def set_mode(self, mode, text=None):
        self.mode = mode
        if text != None:
            self.input_text = text
        self.points = []   
            
    def set_color(self, color='black'):
        if color == 'erase':
            color = self.colors['erase']
        self.color = color 
        if self.textobj != None:
            self.textobj.set_color(color)
            self.figure.update()       
    
    def get_color(self):
        return self.color     
        
    def do_undo(self, event=None):
        pass
        
    def do_redo(self, event=None):
        pass
                   
    def do_crop(self, box=None):
        pass 
        
    def new_image(self, size=None):
        if size == None:
            size = self.size
        image = Image.new(mode='RGBA', size=size)
        self.draw = ImageDraw.Draw(image)
        return image
        
    def on_new_image(self, size=(640,480)):  
        self.clear_all()
        self.filename = ''
        w, h = size
        self.set_size(w, h) 
        self.imageobj = aui.ImageObj(size=size)   
        self.update_tkimage()    
        
    def on_resize_image(self, size):
        size0 = self.size
        w, h = size               
        self.imageobj.resize(size=size) 
        self.actions.append(('resize', (size0, size))) 
        self.set_size(w, h)
        self.update_tkimage()
        
    def load_image(self, fn):  
        self.filename = fn
        self.imageobj = ui.ImageObj(filename=fn) 
        w, h = self.imageobj.size
        self.set_size(w, h)           
        self.update_tkimage()
        
    def update_tkimage(self):
        self.delete('imageobj')   
        self.tkimage = self.imageobj.get_tkimage()              
        self.create_image(0,0, image=self.tkimage, anchor='nw', tag='imageobj')      
        self.lower('imageobj')           
       
    def save_image(self, fn):        
        w, h = self.size
        image = self.figure.get_image()
        print('image', image.size, image.mode, 'self', self.size)
        if self.imageobj == None:
            image.save(fn)
        else:
            print(self.imageobj.image.mode)
            self.imageobj.image.alpha_composite(image)
            self.imageobj.save(fn)
        self.filename = fn
        
    def on_clear_image(self):
        pass
        
    def clear_all(self):
        pass
                    
    def set_size(self, w, h):
        self.size = w, h
        self.configure(width=w, height=h)
        self.set_region(w, h)
        self.figure.set_size((w, h))
        
    def set_region(self, w, h):
        h = max(h, 400)
        self.config(scrollregion=(0,0,w,h))
        self.w = w
        self.h = h  
        
    def on_scrollup(self, event):
        self.yview_scroll(-1, "units")
    
    def on_scrolldown(self, event):
        self.yview_scroll(1, "units")  
        
    def get_line_width(self):
        svar = self.vars.get('line_width', None)
        if svar == None:
            return 8
        v = svar.get()
        return int(v)                     
                   
    def set_status(self, item, value):
        if self.statusbar != None:
           self.statusbar.set_var(item, str(value))
           
    def set_pause(self, pause):
        self.pause = pause

if __name__ == '__main__':   
    from imagedraw import MainFrame, main_app 
    def main():
        root = tk.Tk()
        root.title('ImageCanvas')
        root.geometry('600x400')
        frame = FigureCanvas(root, (600, 400))
        frame.pack(fill='both', expand=True)    
        frame.mainloop()
    main_app()
    


