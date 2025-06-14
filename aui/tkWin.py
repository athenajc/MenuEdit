import tkinter as tk
from PIL import Image, ImageTk
from aui.ImageObj import ImageObj, ImageLabel

class tkFrame(tk.Frame):
    def __init__(self, master, **kw):       
        super().__init__(master, **kw)
        pass

    def add_frame(self, frame):
        if frame == None:
            frame = self
        frame1 = tkFrame(frame)
        frame1.pack(fill='both', expand=True)
        return frame1
        
    def add_image(self, imgobj, side='left', frame=None):
        if type(imgobj) != ImageObj:            
            imgobj = ImageObj(image = imgobj)
        if frame == None:
            frame = self    
        label = ImageLabel(frame, imgobj)
        label.pack(side=side, fill='both', expand=True) 
        return label
        
    def add_images(self, lst, frame=None):
        if lst == []:
            return
        x, y = 0, 0            
        frame1 = self.add_frame(frame)
        for p in lst:
            if type(p) == tuple:
                x, y, img = p
            else:
                img = p
            self.add_image(img, frame=frame1)               
        return frame1  
        
class tkCanvas(tk.Canvas):
    def __init__(self, master, image=None, filename=None, images=[], size=None, **kw):       
        tk.Canvas.__init__(self, master, **kw)
        self.points = []
        self.color = 0
        self.images = []
        self.mouse_btn = 0
        self.mode = 'fill'
        self.show = self.mainloop     
        
        self.keys = {}
        self.keys['Control_L'] = False
        
        self.bind_all('<KeyPress>', self.on_keydown) 
        self.bind_all('<KeyRelease>', self.on_keyup)  
        if size == None:
           w, h = 800, 600       
        else:
           w, h = size
        self.view_size = (w, h)
        self.configure(width=w, height=h)
        if image != None:
            self.image = image
        else:
            self.image = Image.new("RGBA", (w, h))
        self.view_image = self.image
        if images != []:
            self.add_images(images)
        if filename != None:
            obj = self.load_image(filename)    
        self.update_tkimage() 
        
    def load_image(self, filename, pos=(0, 0)):
        obj = ImageObj(filename)        
        obj.x, obj.y = pos
        self.images.append(obj)   
        self.img = obj 
        n = len(self.images)
        if n == 1:
            self.image = obj.image
            self.configure(width=obj.w, height=obj.h) 
            self.view_size = (obj.w, obj.h)
        else:
            self.image.alpha_composite(obj.image, dest=pos)     
        return obj            
        
    def update_tkimage(self, size=None):        
        self.delete('imageobj')
        if size == None:
           self.view_image = self.image.copy()
        else:
           self.view_image = self.image.resize(size)
        self.tkimage = ImageTk.PhotoImage(self.view_image) 
        self.create_image(0, 0, image=self.tkimage, anchor='nw', tag='imageobj') 

    def set_mode(self, mode):
        self.mode = mode
    
    def zoom(self, op='in'):        
        size = self.view_size
        w, h = size
        if op == 'in':
           w = int(w * 1.1)
           h = int(h * 1.1)
        else:
           w = int(w * 0.9)
           h = int(h * 0.9)
        self.view_size = w, h
        #print('zoom',op, w, h)
        self.update_tkimage(size=(w, h))        
        
    def on_keydown(self, event = None):
        #print( ('keydown', event.keysym, event))
        key = event.keysym
        self.keys[key] = True
        if key == 'Up' and self.keys['Control_L'] == True:
            self.zoom('in')
        elif key == 'Down' and self.keys['Control_L'] == True:
            self.zoom('out')
            
    def on_keyup(self, event = None):
        #print(('keyup', event))
        self.keys[event.keysym] = False
        
    def show(self):
        root = self.winfo_toplevel()
        root.mainloop()
        

class tkWin(tkFrame):
    def __init__(self, master, **kw):       
        super().__init__(master, **kw)
        pass

    def show(self):
        root = self.winfo_toplevel()
        root.mainloop()        
   
def tkwin(image=None, filename=None, images=[], size=(800, 600), flag=None):
    root = tk.Tk()
    if filename != None:
        title = 'Image - ' + str(filename)
    else:
        title = 'Tkinter Test Win'
    root.title(title)     
    frame = tkWin(root)    
    frame.pack(fill='both', expand=True)  
    if image != None:
        frame.add_image(image)
    elif filename != None:
        frame.load_image(filename)
    elif images != None:
        frame.add_images(images)
    if flag == 'show':
       frame.show()  
    return frame   

def pixbuf2image(p):
    w, h, c, r = p.get_width(), p.get_height(), p.get_n_channels(), p.get_rowstride()
    mode = ['', 'L', '', 'RGB', 'RGBA'][c]
    image = Image.frombytes(mode, (w, h), p.get_pixels(), "raw")
    return image    
    


if __name__ == '__main__':                 
    def test_tkwin():
        w, h = 800, 600
        size = w, h
        bkg = ImageObj(size=size)        
        draw = bkg.get_draw()   
        bkg.gradient('r', 'GnBu')
        draw.rectangle((10, 10, w-10, h-10), outline=(0, 0, 0, 128))
        draw.rectangle((9, 9, w-11, h-11), outline=(255, 255, 255, 180))
        frame = tkwin()
        frame.add_image(bkg)
        frame.show()

    test_tkwin()



