import tkinter as tk
from namedcolors import named_colors

class ColorBox(tk.Canvas):
    def __init__(self, master, **kw):
        tk.Canvas.__init__(self, master, **kw)  
        self.colors = named_colors
        lst = [ '#dfdfdf', '#000000', '#ffffff', '#dddddd', '#777777', '#555555', '#333333']
        self.colorlist = lst + list(self.colors.values())
        self.colorindex = 0
        self.size = (600, 600)
        for r in range(0, 255, 40):
            for g in range(0, 255, 32):
                for b in range(0, 255, 64):
                    c = '#%02x%02x%02x' % (r, g, b)
                    self.colorlist.append(c)
        self.draw_colors()
        self.bind('<Motion>', self.on_motion)
        self.bind('<ButtonPress-1>', self.on_mousedown)
        
    def set_color(self, color):
        self.colorlist[self.colorindex] = color
        self.draw_colors()
        self.lift('selected')
        
    def move_select(self, x, y):
        self.delete('motion')
        item = self.find_closest(x, y)        
        box = self.bbox(item)        
        if box == None:
            return
        self.create_rectangle(box, outline='white', tag='motion', dash=(5,3))
        
    def on_mousedown(self, event=None):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y) 
        self.move_select(x, y)
        item = self.find_closest(x, y)
        i = 0
        for t in self.gettags(item):
            if t[0] in '0123456789':
               i = int(t)
               self.colorindex = i
               break
        self.set_scale_color(self.colorlist[i])
        self.delete('selected')
        box = self.bbox(item)        
        if box == None:
            return
        self.create_rectangle(box, outline='white', width=2, tag='selected')
         
    def set_size(self, w, h):
        self.size = (w, h)
        self.draw_colors()
            
    def on_motion(self, event=None):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y) 
        self.move_select(x, y)
        
    def draw_colors(self):
        self.delete('colors')
        w, h = self.size
        i = 0
        color = self.colorlist      
        n = len(color)  
        for y in range(0, 600, 30):
            for x in range(0, w-20, 30):
                item = self.create_rectangle(x, y+20, x+30, y+20+30, fill=color[i], tag=(str(i), 'colors'))                
                i += 1
                if i >= n:                    
                    return            
                    
        
class OneColorBox(tk.Canvas):
    def __init__(self, master, **kw):
        tk.Canvas.__init__(self, master, **kw)  
        self.create_rectangle(10, 10, 80, 80, fill='white', tag='color')
        
    def set_color(self, color):
        self.itemconfigure('color', fill=color)
        
class ColorFrame(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, **kw)
        self.set_color_action = self.set_color_action_default
        self.colorbox = ColorBox(self, width=600, height=600, bg='white')
        self.colorbox.pack(side='top', fill='both', expand=True)  
        self.colorbox.set_scale_color = self.set_scale_color
        self.colorindex = 0
        frame = tk.Frame(self)
        frame.pack(side='top', fill='both', expand=True)
        self.current_color = OneColorBox(frame, width=100, height=100)
        self.current_color.pack(side='left') 
        frame1 = tk.Frame(frame)
        frame1.pack(side='left', fill='both', expand=True)
        self.obj = {}
        self.obj['r'] = self.add_scale(frame1, 'R')
        self.obj['g'] = self.add_scale(frame1, 'G')
        self.obj['b'] = self.add_scale(frame1, 'B')              
     
        self.bind('<Configure>', self.on_configure)
        for s in 'rgb':
            self.obj[s].bind("<ButtonRelease-1>", self.on_set_scale)
            self.obj[s].bind("<B1-Motion>", self.on_pull_scale)
        
    def set_colors(self, colors):
        self.colorbox.colorlist = colors.copy()
        
    def get_colors(self):
        return self.colorbox.colorlist
        
    def set_color_action_default(self, color):
        pass
        
    def bind_act(self, event, action):
        self.set_color_action = action
        
    def on_configure(self, event=None):
        w, h = event.width, event.height
        self.colorbox.set_size(w, h)
        
    def add_scale(self, frame, label):
        frame1 = tk.Frame(frame)
        frame1.pack(side='top', fill='both', expand=True)
        labelobj = tk.Label(frame1, text=label)
        labelobj.pack(side='right')        
        var = tk.IntVar()
        obj = tk.Scale(frame1, from_=0, to=255, variable = var, orient='horizontal')
        obj.pack(side='right', fill='both', expand=True)
        obj.var = var
        return obj        
       
    def set_scale_color(self, color):
        self.colorindex = self.colorbox.colorindex
        #print('set_scale_color', color, type(color))
        self.current_color.set_color(color)
        r = int(color[1:3], 16)        
        g = int(color[3:5], 16)         
        b = int(color[5:7], 16)         
        self.obj['r'].set(r)
        self.obj['g'].set(g)
        self.obj['b'].set(b)
        self.set_color_action(color)
        
    def on_set_scale(self, event=None):
        r = self.obj['r'].var.get()
        g = self.obj['g'].var.get()
        b = self.obj['b'].var.get()
        c = '#%02x%02x%02x' % (r, g, b)
        self.current_color.set_color(c)
        self.set_color_action(c)
        self.colorbox.set_color(c)
        
    def on_pull_scale(self, event=None):
        r = self.obj['r'].var.get()
        g = self.obj['g'].var.get()
        b = self.obj['b'].var.get()
        c = '#%02x%02x%02x' % (r, g, b)
        self.current_color.set_color(c)        
        self.set_color_action(c)
        self.colorbox.set_color(c)
    
if __name__ == '__main__':           
    def main():
        root = tk.Tk()
        root.title('Color box')
        root.geometry('600x800')
        frame = ColorFrame(root)
        frame.pack(fill='both', expand=True)
        frame.mainloop()
    
    main()

