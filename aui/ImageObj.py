import numpy as np
import PIL
from PIL import Image, ImageTk, ImageDraw, ImageChops
from PIL import ImageFont, ImageOps, ImageFilter, ImageEnhance
import tkinter as tk
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
import math
import cairosvg 
import io
import os


#font = PIL.ImageFont.truetype('ChinSong1.ttf', 18)
font = ImageFont.load_default() 
docpath = '~/文件/Keep/text'

def load_svg0(filename, size=None):
    if size == None:
        p = GdkPixbuf.Pixbuf.new_from_file(filename)
    else:
        w, h = size
        p = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, w, h)
    w, h, c, r = p.get_width(), p.get_height(), p.get_n_channels(), p.get_rowstride()
    mode = ['', 'L', '', 'RGB', 'RGBA'][c]
    image = Image.frombytes(mode, (w, h), p.get_pixels(), "raw")
    
    return PIL.ImageTk.PhotoImage(image) 
    
def _load_svg(filename, size=None):
    # 1. 使用 CairoSVG 將 SVG 轉換為 PNG byte data (存在記憶體中)
    if size == None:
        png_data = cairosvg.svg2png(url=filename)
    else:
        w, h = size
        png_data = cairosvg.svg2png(url=filename, output_width=w, output_height=h)

    # 2. 將 PNG byte data 包裝成 Pillow 可以讀取的檔案物件
    png_bytes_io = io.BytesIO(png_data)

    # 3. 使用 Pillow 開啟 PNG data，得到 PIL.Image.Image 物件
    pil_image = Image.open(png_bytes_io)
    return pil_image    
    
def load_svg(filename, size=None):
    return _load_svg(filename, size)
        
def load_image(filename, size=None):
    ext = file_ext(filename)
    if ext == 'svg':
        return load_svg(filename, size)
    image = PIL.Image(filename)
    if size != None:
        return image.resize(size=size)
    return image    
    
def read_svg(url, size=None):
    return cairosvg.svg2png(url=url)  
    
def svg2tkimage(svg):
    s = svg.strip()
    if s == '':
        return
    if s[0] == '<':
        png = cairosvg.svg2png(bytestring=svg)
    else:
        png = cairosvg.svg2png(url=svg)    
    img = PIL.Image.open(io.BytesIO(png))
    img.show()
    #tkimage = PIL.ImageTk.PhotoImage(img) 
    #return tkimage
        
def text2image(filename, size=(256, 300)):
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
        w1 = font.getsize(text[i:i+n1])[0]
        if n1 < 200:
           n1 += (250 - w1) // 18        
        lst.append(text[i:i+n1])
        i += n1
    text = '\n'.join(lst[:8])    
    draw.multiline_text((5, 5), text, fill='black', font=font)
    return image
    

class tkImage(PIL.ImageTk.PhotoImage):
    def __init__(self, image=None, size=None, **kw):
        self.filename = ''
        if type(image) == str:
            self.filename = image                
            image = PIL.Image.open(self.filename)
        PIL.ImageTk.PhotoImage.__init__(self, image, size, **kw)
        self.pilimage = image
        self.size = image.size

        
class ButtonImage():
    def emboss1(self, d, lw, colors=None):
        w, h = self.size
        h -= 2
        w -= 1
        x0, y0 = d, d
        x1, y1 = w-d, h-d
        if colors == None:
            colors = ['#aaa', '#fff', '#eee', '#444', '#666']
        draw = self.draw    
        draw.rectangle((x0, y0, x1, y1), fill=colors[0])
        for i in range(1, lw):        
            draw.line((d, d, w-d, d), fill=colors[1])
            draw.line((d, d, d, h-d), fill=colors[2])        
            draw.line((d, h-d, w-d, h-d), fill=colors[3])
            draw.line((w-d, d, w-d, h-d), fill=colors[4])    
            d += 1           
        
    def emboss2(self, d, lw, colors=None):
        w, h = self.size
        h -= 2
        w -= 1
        x0, y0 = d, d
        x0 += 3
        y0 += 3
        x1, y1 = w-d, h-d
        if colors == None:
            colors = ['#aaa', '#fff', '#eee', '#444', '#666']
        draw = self.draw    
        draw.rectangle((x0, y0, x1, y1), fill=colors[0])
        for i in range(1, lw):        
            draw.line((d, d, w, d), fill=colors[1])
            draw.line((d, d, d, h), fill=colors[2])           
            d += 1           
        d = 5
        draw.rectangle((d, d, w-3, h-3), outline='#222', width=5)        

    def button_up(self, d):
        obj = ImageObj(size=self.size)
        colors = ['#aaa', '#eee', '#ddd', '#444', '#666']
        obj.emboss1(0, d, colors)
        obj.filter('GaussianBlur')
        return obj
        
    def button_down(self, d):
        obj = ImageObj(size=self.size)
        colors = ['#999', '#444', '#666', '#777', '#888']
        obj.emboss2(0, d, colors)
        obj.filter('GaussianBlur')
        return obj
        
    def button_rollover(self, d):
        obj = ImageObj(size=self.size)
        colors = ['#ddd', '#fff', '#eee', '#333', '#555']
        obj.emboss1(0, d, colors)
        obj.filter('GaussianBlur')
        return obj
        
    def button_disable(self, d):
        obj = ImageObj(size=self.size)
        colors = ['#999', '#aaa', '#bbb', '#555', '#666']
        obj.emboss2(0, d, colors)
        obj.filter('GaussianBlur')
        return obj        
            
    def get_button(self, mode='', d=15):
        size = self.size      
        image = self.pilimage  
        if mode == 'down':
            gray = self.button_down(d)
            image = ImageChops.overlay(image, gray.image)
        elif mode == 'rollover':
            gray = self.button_rollover(d)
            image = ImageChops.soft_light(image, gray.image)
        elif mode == 'disable':
            gray = self.button_disable(d)
            image = ImageChops.blend(image, gray.image, 0.5)              
        else:
            gray = self.button_up(d)
            image = ImageChops.overlay(image, gray.image)    
        return image
        
    def get_buttons(self, d):
        images = {}
        for mode in ['up', 'down', 'light', 'disable']:
            images[mode] = self.get_button(mode, d)
        return images
        
    def gen_button(self, fn, d):     
        images = self.get_buttons(d)
        for s, image in images.items():
            fn1 = fn.replace('.png', '_%s' % s)
            image.save(fn1)
     
class ImageFill():
    def get_x_sections(self, a):       
        a0 = a[0]
        lst = [[a0]]
        for a1 in a[1:]:
            if a1 - a0 == 1:
               lst[-1].append(a1)
            else:
               lst.append([a1])    
            a0 = a1
        return lst        
        
    def get_section_list(self, imgary, p0, thresh):
        h, w = imgary.shape
        sections = {}
        for y in range(-1, h+2):
            sections[y] = []
        z = np.zeros((h, w), dtype=int)
        ary = np.where(np.abs(imgary - p0) < thresh, 1, z)
        for y in range(0, h):        
            ary1 = ary[y]
            a = np.where(ary1 == 1)[0]
            if a.size == 0:
                continue
            for b in self.get_x_sections(a):  
                if b != []:           
                    sections[y].append( (b[0], b[-1]))            
        return sections    
        
    def is_connected(self, a, b):   
        if a[1] < b[0] or a[0] > b[1] or b[1] < a[0] or b[0] > a[1]:
            return False
        return True
                
    def check_lst_p0_connect(self, dct, y, a):       
        for b in dct[y-1]:
            if not (a[1] < b[0] or a[0] > b[1] or b[1] < a[0] or b[0] > a[1]):
                return (y-1, b)
        for b in dct[y+1]:
            if not (a[1] < b[0] or a[0] > b[1] or b[1] < a[0] or b[0] > a[1]):
                return (y+1, b)                
        return None  
        
    def find_closed_1(self, y, p):  
        p1 = self.check_lst_p0_connect(self.sections, y, p)
        if p1 == None:
            return -1 
        y1, b = p1
        self.dct[y1].append(b)    
        self.sections[y1].remove(b)   
        return (y1, b)                    
                    
    def find_closed_section(self):           
        found = -1  
        plst = []
        for y, lst in self.dct.items():
            for p in lst:
                p1 = self.find_closed_1(y, p)   
                if p1 != -1:
                    found += 1
                    plst.append(p1)
        if plst != []:
            for i in range(100):
                plst1 = []
                for y, p in plst:
                    p1 = self.find_closed_1(y, p)   
                    if p1 != -1:
                        found += 1
                        plst1.append(p1)
                if plst1 == []:
                    return found
                plst = plst1
        return found     
        
    def search_sections(self, sections, x, y): 
        lst = sections[y]
        for a in lst:   
            x0, x1 = a
            if x >= x0 and x <= x1:
                return (y, a)
        return None
                
    def find_closed_list(self, sections, xy, w, h): 
        x, y = xy   
        s0 = self.search_sections(sections, x, y)    
        if s0 == None:
            return {}   
        dct = {}
        for y in range(-1, h+2):
            dct[y] = []
        dct[s0[0]].append(s0[1])    
        self.dct = dct
        self.sections = sections
        for i in range(100): 
            found = self.find_closed_section()  
            if found == -1:
                print('search times', i)
                break
        return self.dct         
                
    def get_fill_list(self, xy, thresh): 
        x, y = xy
        h, w = self.shape       
        x = min(w-1, x)
        y = min(h-1, y)
        x = max(0, x)
        y = max(0, y)
        imgary = self.get_array('L')         
        p0 = imgary[y, x]           
        sectlst = self.get_section_list(imgary, p0, thresh)
        dct = self.find_closed_list(sectlst, xy, w, h)
        return dct
        
class ImageObj(ImageFill, ButtonImage):
    def __init__(self, filename=None, size=None, mode="RGBA", image=None, autoclip=None):         
        if type(filename) == PIL.Image.Image:
           image = filename
           filename = ''
        self.filename = filename        
        self.pilimage = image        
        self.file_ext = ''
        if image != None:
            self.set_image(image)
        elif filename != None:
            self.load(filename, size, autoclip)
        elif size != None:
            self.new_image(size, mode)
            
    def new(**kw):
        img = Image.new(**kw)
        return ImageObj(image=img)
        
    def open(filename, size=None):
        if '.svg' in filename:
            obj = ImageObj(filename, size=size)
            return obj
        img = Image.open(filename)        
        return ImageObj(filename=filename, image=img, size=size)
        
    def thumbnail(filename, size):
        if '.svg' in filename:
            obj = ImageObj(filename, size=size)
        else:
            img = Image.open(filename)
            img.thumbnail(size)
            obj = ImageObj(image=img)
        return obj
        
    def from_array(a, mode):
        img = Image.fromarray(a, mode)
        return ImageObj(image=img)
        
    def from_surface(surface):
        w, h = surface.get_width(), surface.get_height()
        buffer = surface.get_data().tobytes()
        image = Image.frombuffer('RGBA', (w, h), buffer,'raw','BGRA',0,1)
        return ImageObj(image=image)
        
    def from_pixbuf(p, size=None):
        w, h, c, r = p.get_width(), p.get_height(), p.get_n_channels(), p.get_rowstride()
        mode = ['', 'L', '', 'RGB', 'RGBA'][c]
        image = Image.frombytes(mode, (w, h), p.get_pixels(), "raw")               
        if size != None:
            image = image.resize(size)
        return ImageObj(image=image)   
        
    def copy(self):
        return ImageObj(image=self.pilimage.copy())
        
    def set_array(self, a):
        image = Image.fromarray(a)
        self.set_image(image)
        
    def new_image(self, size, mode="RGBA"):
        img = Image.new(mode=mode, size=size)
        self.set_image(img)
                
    def set_image(self, img):
        w, h = img.size
        self.size = (w, h)       
        self.shape = (h, w)
        self.pilimage = img
        self.image = img
        self.draw = None
        
    def get_draw(self):
        if self.draw == None:
           self.draw = ImageDraw.Draw(self.pilimage)
        return self.draw   
        
    def get_clip_box(self, image):
        ary = self.get_1bit_array(image)               
        h, w = ary.shape      
        p0 = ary[0, 0]   
        a = np.where(ary != p0)        
        a0, a1 = a[0], a[1]
        y0, y1 = min(a0), max(a0)
        x0, x1 = min(a1), max(a1)
        return (x0, y0, x1, y1)
        
    def clip_image(self, image, axis=None):    
        box = self.get_clip_box(image)
        x0, y0, x1, y1 = box
        w, h = image.size
        if axis == 'x':        
            dy = (y1 - y0)/2
            w2 = w / 2
            x0 = int(w2 - dy)
            x1 = int(w2 + dy)
        elif axis == 'y':
            dx = (x1 - x0) / 2
            h2 = h / 2
            y0 = int(h2 - dx)
            y1 = int(h2 + dx)        
        img1 = image.crop(box=(x0-1, y0-1, x1+2, y1+2)) 
        return img1
        
    def auto_clip(self, size=None, axis=None):
        image = self.clip_image(self.pilimage, axis)
        if size != None:
            image = image.resize(size)
        self.set_image(image)    
    
    def reload(self):
        return self.load(self.filename)
        
    def clear(self):
        w, h = self.size
        z = np.zeros((h, w, 4), dtype=np.uint8)
        img = Image.fromarray(z)
        self.set_image(img)            
        
    def read_svg(self, text, size=(128, 128)):
        return None
        #w, h = size
        #c, r = 4, 4*w
        #bps = c * 8
        #colorspace = GdkPixbuf.Colorspace.RGB
        #'colorspace', 'has_alpha', 'bits_per_sample', 'width', 'height', and 'rowstride'
        #p = GdkPixbuf.Pixbuf.new_from_data(text.encode(), colorspace, True, bps, w, h, r)
        #w, h, c, r = p.get_width(), p.get_height(), p.get_n_channels(), p.get_rowstride()
        #mode = 'RGBA'
        #image = Image.frombytes(mode, (w, h), p.get_pixels(), "raw")
        #return image
        
    def load_svg(self, filename, size=None):
        return _load_svg(filename, size)
    
    def load(self, filename, size=None, autoclip=None):
        self.filename = filename
        if not '.' in filename:
            print('error', filename)
            return
        self.file_ext = filename.rsplit('.', 1)[1]
        if self.file_ext == 'svg':
            img = self.load_svg(filename, size)
            size = None
        else:
            print(filename)
            img = PIL.Image.open(filename)
        if autoclip != None:
            img = self.clip_image(img, axis=autoclip)
        if size != None:
            img = img.resize(size)
        self.set_image(img)
        return img
        
    def save(self, filename, box=None, size=None, mode=None):
        image = self.pilimage
        if box != None:
            image = image.crop(box=box)
        if size != None:
            image = image.resize(size)        
        if mode != None:
            image = image.convert(mode)    
        image.save(filename)        
        
    def convert(self, mode):
        image = self.pilimage
        if image.mode != mode:
            image = image.convert(mode)
            self.pilimage = image
        return image
        
    def split(self):
        return self.pilimage.split()
        
    def get_alpha(self):
        #red, green, blue, alpha = self.pilimage.split()
        alpha = self.pilimage.getchannel(3)
        return alpha
        
    def get_array(self, mode=None, size=None, image=None):
        if image == None:
            image = self.pilimage
        if size != None:
            image = image.resize(size)
        if mode == '1':
            return self.get_1bit_array(image) 
        elif mode == 'RGBA32':
            img = image.convert('RGBA')
            buf = img.tobytes()
            w, h = image.size
            ary = np.frombuffer(buf, dtype=np.uint32).reshape((h, w))
            return ary
        elif mode != None:
            if image.mode != mode:
               image = image.convert(mode)
            return np.asarray(image)
        return np.asarray(image)
        
    def get_gray_image(self):
        return self.pilimage.convert("L")
        
    def array2image(self, a, mode="L"):
        if 'float' in str(a.dtype):
            if np.max(a) <= 1.:
               a = np.uint8(a * 255)
            else:
               a = np.uint8(a)
        return PIL.Image.fromarray(a, mode)
        
    def get_1bit_array(self, image=None, mean=None):
        if image == None:
            image = self.pilimage
        gray = image.convert("L")
        a = np.asarray(gray)
        if mean == None:
           m = int(np.mean(a))     
        else:
           m = mean
        z = np.zeros(a.shape, dtype=np.uint8)
        b = np.where(a < m, 1, z) 
        return b
        
    def get_gray(self):
        return np.asarray(self.get_gray_image())       
    
    def get_tkimage(self, image=None, box=None, size=None):
        if image == None:
            image = self.pilimage
        if box != None:
            image = image.crop(box=box)  
        if size != None:
            image = image.resize(size)      
        return PIL.ImageTk.PhotoImage(image)    
        
    def crop(self, box=None):
        img = self.pilimage.crop(box=box)        
        self.set_image(img)
        
    def resize(self, size):        
        if self.filename != None and '.svg' in self.filename:
            img = self.load_svg(self.filename, size=size)
        else:
            img = self.pilimage.resize(size=size)
        self.set_image(img)
        
    def get_pixels(self):
        return self.pilimage.tobytes()

    def get_pixel(self, x, y):
        return self.pilimage.getpixel((x, y))
        
    def set_pixel(self, x, y, color):                
        self.pilimage.putpixel((int(x), int(y)), color)
        
    def draw_line(self, x0, y0, x1, y1, color):        
        draw = self.get_draw()  
        draw.line((x0, y0, x1, y1), fill=color) 
   
    def draw_rect(self, x0, y0, x1, y1, outline=None, fill=None):      
        draw = self.get_draw()  
        draw.rectangle((x0, y0, x1, y1), outline=outline, fill=fill)
        
    def fill(self, color):
        x0, y0 = 0, 0
        x1, y1 = self.size
        draw = self.get_draw()  
        draw.rectangle((x0, y0, x1, y1), fill=color)
        
    def draw_text(self, pos, text, fill=(0, 0, 0), font=None):
        #self.draw.text(xy, text, fill=None, font=None, anchor=None, spacing=0, align=”left”) 
        draw = self.get_draw()  
        draw.text(pos, text, fill=fill, font=font)
        
    def floodfill(self, xy, color, thresh): 
        draw = self.get_draw()                    
        dct = self.get_fill_list(xy, thresh)     
        for y, lst in dct.items():
            for x0, x1 in lst:  
                draw.line((x0, y, x1, y), color)
                
    def linear_gradient(self, colorname, w, h, mode='l'):                  
        cmapfunc = plt.get_cmap(colorname)
        if mode == 'l':
           gradient = np.linspace(0, 1, h)  
           colors = cmapfunc(gradient)
           a = np.uint8(colors*255)
           a1 = np.stack([a] * w, axis=1)      
        else:
           gradient = np.linspace(0, 1, w)  
           colors = cmapfunc(gradient)
           a = np.uint8(colors*255)
           a1 = np.stack([a] * h, axis=0)      
        h1, w1, c = a1.shape    
        image = Image.fromarray(a1)
        return image
        
    def radial_gradient(self, colorname, w, h):        
        mx = w / 2
        my = h / 2
        r = max(mx, my)*1.5    
        vfunc = np.vectorize(lambda y, x: (math.sqrt((x-mx)**2 + (y-my)**2)) / r)
        p = np.fromfunction(vfunc, (h, w))
        cmapfunc = plt.get_cmap(colorname)
        colors = cmapfunc(p)
        a = np.uint8(colors*255)               
        h1, w1, c = a.shape    
        image = Image.fromarray(a)
        return image
        
    def gradient(self, mode, colorname, pos=(0, 0), size=None):
        if size == None:
            size = self.size
        w, h = size
        if mode == 'radial' or mode == 'r':
           image = self.radial_gradient(colorname, w, h)
        else:
           image = self.linear_gradient(colorname, w, h, mode)
        self.pilimage.alpha_composite(image, dest=pos)
        return image
                 
    def composite(self, obj, dest=(0, 0)):        
        self.pilimage.alpha_composite(obj.pilimage, dest=dest)
        
    def draw_image(self, pos, obj):
        x, y = pos
        pos = (int(x), int(y))
        img = obj.pilimage   
        if img.mode != 'RGBA':
            self.pilimage.paste(img, pos)
            return     
        alpha = img.getchannel(3)        
        self.pilimage.paste(img, pos, mask=alpha)

    def transparent(self, color=None):
        a = self.get_array('RGBA32')     
        h, w = a.shape   
        if color == None:
            color = a[0, 0]    
        buf = np.where(a == color, 0xff, a)  
        ary = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))              
        self.set_array(ary)      
        return self
    
    def mirror(self):
        self.pilimage = ImageOps.mirror(self.pilimage)
       
    def flip(self):
        self.pilimage = ImageOps.flip(self.pilimage)
         
    def emboss(self):
        self.pilimage = self.pilimage.filter(ImageFilter.EMBOSS)
        
    def blur(self, tag=None):
        if tag == 'guass':
            self.pilimage = self.pilimage.filter(ImageFilter.GaussianBlur)
        elif tag == 'Color3DLUT':
            self.pilimage = self.pilimage.filter(ImageFilter.Color3DLUT)
        else:
            self.pilimage = self.pilimage.filter(ImageFilter.BLUR)
        
    def boxblur(self, radius):
        self.pilimage = self.pilimage.filter(ImageFilter.BoxBlur(radius))        
        
    def filter(self, name):
        cmd = 'self.pilimage = self.pilimage.filter(ImageFilter.%s)' % name
        exec(cmd)
        
    def brightness(self, factor):
        self.pilimage = ImageEnhance.Brightness(self.pilimage).enhance(factor)  
        
    def constrast(self, factor):
        self.pilimage = ImageEnhance.Contrast(self.pilimage).enhance(factor)        
        
    def show(self, image=None, box=None, size=None):
        root = tk.Tk()
        root.title('Image - ' + str(self.filename))
        if type(image) == np.ndarray:
           image = self.array2image(image)
        tkimage = self.get_tkimage(image, box, size)
        panel = tk.Label(root, image = tkimage)
        panel.pack()  
        root.mainloop()                 

class ImageLabel(tk.Frame):
    def __init__(self, master, obj=None, tkimage=None, filename=None):       
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self)
        self.label.pack(fill='both', expand=True)        
        if obj != None:
            tkimage = obj.get_tkimage()
        elif tkimage == None:
            imgobj = ImageObj.open(filename)
            tkimage = imgobj.get_tkimage()
        if tkimage != None:    
           self.set_image(tkimage)        
   
    def set_image(self, tkimage):
        self.tkimage = tkimage
        self.label.configure(image = self.tkimage)         
        
class ImageViewer(tk.Toplevel):
    def __init__(self, master, filename, **kw):       
        tk.Toplevel.__init__(self, master, **kw)
        self.wm_title(filename)
        label = tk.Label(self)
        label.pack(fill='both', expand=True)
        filename = os.path.realpath(filename)
        img = ui.ImageObj(filename)
        print(img.size)
        w, h = img.size
        s = max(w, h)
        if s < 400:
           m = int(400 / s)
           w, h = w * m, h * m
           img = ui.ImageObj(filename, size=(w, h)) 
        self.tkimage = img.get_tkimage()
        label.configure(image = self.tkimage) 
        self.imgobj = img
        self.label = label
        self.geometry('%dx%d' % (w, h))
        self.bind('<Configure>', self.on_configure)
        
    def on_configure(self, event=None):
        w, h = event.width, event.height
        self.imgobj.resize((w, h))
        self.tkimage = self.imgobj.get_tkimage()
        self.label.configure(image = self.tkimage) 
        
def cmap_colorbar(lst, size=(800, 600)):
    img = ImageObj(size=size)
    n = len(lst)
    w, h = size
    h1 = (h - 10) // (n+1)
    y = 5
    for cmap in lst:
        img.gradient('lh', cmap, (10, y), (w-20, h1-5))
        y += h1 
    return img
    
def plot_cmap(lst):       
    plt.plot_color_gradients('Cmap', lst)
    plt.show()

def draw_cmap(lst):
    img = cmap_colorbar(lst)
    img.show()

def get_cmap_colors(name, n=256):
    cmapfunc = plt.get_cmap(name)
    gradient = np.linspace(0, 1, n)  
    colors = cmapfunc(gradient)
    lst = []
    for r, g, b, a in np.uint8(colors*255):
        lst.append('#%02x%02x%02x' % (r, g, b))
    return lst

def pixbuf2image(p):
    w, h, c, r = p.get_width(), p.get_height(), p.get_n_channels(), p.get_rowstride()
    mode = ['', 'L', '', 'RGB', 'RGBA'][c]
    image = Image.frombytes(mode, (w, h), p.get_pixels(), "raw")
    return image    
    
       
if __name__ == '__main__':

    def shadow(obj):
        w, h = obj.size  
                 
        r, g, b, alpha = obj.split()
        a = np.array(alpha)    
        b = a.flatten().astype(float)  
        b = b * 0.75
        b = b.astype(np.uint8).reshape(a.shape)
        b = np.pad(b, (4, 4), 'constant', constant_values=0)        
        
        alpha = ImageObj.from_array(b, 'L')
        alpha.boxblur(4)
        
        obj1 = ImageObj.new(size=alpha.size, mode='RGBA', color=0xff000000)
        obj1.pilimage.putalpha(alpha.pilimage)
                  
        obj2 = ImageObj.new(mode='RGB', size=(w+8, h+8), color=0xffdddd)

        obj2.draw_image((0, 0), obj1) 
        obj2.draw_image((0, 0), obj)          
        return obj2
        
    def test_image_obj(fn):
        obj = ImageObj(fn)     
        obj1 = shadow(obj)
        obj1.show() 
        
    def main(fn):
        image_viewer(fn)  
        #test('mono/0.png') 
    #test_image_obj('/home/athena/Images/icons/akonadiconsole.png')
    fn = os.path.expanduser('~/data/svg/camera.svg')
    if 0:
        obj = ImageObj(filename=fn)
        obj.show()
    
    if 1:
        from aui import App
        app = App(title='Show Image', size=(600,600))
        label = app.get('image', filename=fn)
        label.place(x=0, y=0, relwidth=1, relheight=1)
        app.mainloop()




