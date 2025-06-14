import tkinter as tk
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GdkPixbuf
from PIL import Image, ImageTk

class PixelBuffer():
    def __init__(self, pixbuf=None): 
        self.pixbuf = pixbuf
        self.window = None
        self.filename = None
        self.pixels = None
        self.pixary = None
       
    def set_pixbuf(self, pb):
        self.pixbuf = pb
        self.pixels = pb.get_pixels()
        self.w, self.h = pb.get_width(), pb.get_height()
        self.channels = pb.get_n_channels()
        self.rowstride = pb.get_rowstride()
        self.pixary = self.get_array()
        
    def load(self, filename):
        self.set_pixbuf(GdkPixbuf.Pixbuf.new_from_file(filename))
        return self.pixbuf
        
    def save(self, filename):
        self.pixbuf.savev(filename, "png", [], [])
        
    def get_info(self):
        p = self.pixbuf
        if p == None:
            return
        w,h,c,r=p.get_width(), p.get_height(), p.get_n_channels(), p.get_rowstride()
        return (w, h, c, r)
    
    def capture_window(self, win=None, box=None):
        if win == None:
            return
        geo = win.get_geometry()   
        if box == None:
            x, y, w, h = 0, 0, geo.width, geo.height       
        else:
            x, y, w, h = box
        self.set_pixbuf(Gdk.pixbuf_get_from_window(win, x, y, w, h))        
        return self.pixbuf
        
    def get_pixels(self):
        return self.pixbuf.get_pixels()

    def get_pixel(self, x, y):        
        i = self.rowstride * y + self.channels * x
        return self.pixels[i:i+3]
        
    def search(self, pixel):     
        return np.where(np.all(self.pixary, axis=-1)) 
        
    def search_image(self, img):
        img1 = self.pixary
        img2 = img.pixary
        h, w, c = img1.shape
        h1, w1, c = img2.shape
        a = self.search(img2[0, 0])
        ay, ax = a[0], a[1]
        for i in range(ax.size):
            x, y = ax[i], ay[i]    
            if np.array_equal(img1[y:y+h1, x:x+w1], img2):
                #print('search_image found at', (x, y), ' search time =', i+1)
                return True    
        return False

    def get_array(self):        
        w,h,c,r= self.get_info()
        a = np.frombuffer(self.pixels, dtype=np.uint8)
        if a.shape[0] == w*c*h:
            a1 = a.reshape( (h, w, c) )
        else:
            b=np.zeros((h,w*c),'uint8')
            for j in range(h):
                b[j,:]=a[r*j:r*j+w*c]
            a1 = b.reshape( (h, w, c) )            
        if c == 3:
            return a1
        else:
            return a1[:,:,:3]
     
    def get_image(self):        
        w,h,c,r = self.get_info()
        mode = "RGB"
        if self.pixbuf.get_has_alpha() == True:
            mode = "RGBA"
        im = Image.frombytes(mode, (w, h), self.pixels, "raw", mode, r)
        return im
        
    def preview(self):
        root = tk.Tk()
        root.title('Image of pixbuf - ' + self.filename )
        img = self.get_image()
        img2 = ImageTk.PhotoImage(img)         
        canvas = tk.Canvas(root, width=img.size[0], height=img.size[1])
        canvas.pack()        
        canvas.create_image(0,0, anchor=tk.NW, image=img2)        
        root.mainloop()






