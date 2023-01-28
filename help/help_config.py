default_modules = ['builtins', 'os', 'sys', 're', 'tkinter',  'inspect',                 
            'pandas', 'pandas.DataFrame', 'sqlite3', 'dict', 'list', 'str',
            'numpy.ndarray', 'numpy', 'scipy', 'matplotlib',
            'tkcode', 'json', 'openai', 'pprint', 
            'pkgutil', 'subprocess',  'skimage', 'gi.repository',
             'cairo',  'PIL', 'PIL.Image', 'PIL.ImageDraw']
             
name_map_list =  {'ax': 'matplotlib.axes.Axes',
     'box': 'matplotlib.transforms.Bbox',
     'bz': 'matplotlib.bezier',
     'cmap': 'matplotlib.colors.LinearSegmentedColormap',
     'draw': 'PIL.ImageDraw',
     'fig': 'matplotlib.figure.Figure',
     'figure': 'matplotlib.figure.Figure',
     'gdk': 'gi.repository.Gdk',
     'geo': 'shapely.geometry',
     'gio': 'gi.repository.Gio',
     'glib': 'gi.repository.GLib',
     'gobject': 'gi.repository.GObject',
     'gtk': 'gi.repository.Gtk',
     'image': 'PIL.Image',
     'img': 'PIL.Image',
     'line': 'shapely.geometry.linestring',
     'mp': 'matplotlib',
     'np': 'numpy',
     'pango': 'gi.repository.Pango',
     'patch': 'matplotlib.patches',
     'path': 'matplotlib.path.Path',
     'pil': 'PIL',
     'pixbuf': 'gi.repository.GdkPixbuf',
     'plot': 'matplotlib.pyplot',
     'plt': 'matplotlib.pyplot',
     'poly': 'shapely.geometry.polygon',
     'polygon': 'matplotlib.patches.Polygon',
     'tk': 'tkinter',
     'trans': 'matplotlib.transforms',
     'ttk': 'tkinter.ttk'}


if __name__ == '__main__':   
    import os
    import pprint

    def read_map():        
        dct = {}
        path = os.path.dirname(__file__) + os.sep
        with open(path + 'help_map.lst', 'r') as f:
            text = f.read()            
            for s in text.splitlines():
                if not '=' in s:
                    continue
                k, v = s.split('=')
                dct[k.strip()] = v.strip()
        pprint.pprint(dct)

    def get_modules(): 
        import pkgutil
        from ui import Tlog
        t = Tlog()
        lst = list(default_modules)
        for p in pkgutil.iter_modules():
            importer, name, ispkg = p
            importer = str(importer)
            if not 'python' in importer or '_' in name:
                continue
            if ispkg and not name in lst:
                lst.append(name)   
        t.puts()         
        #pprint.pprint(lst, indent=4, width=80)
    read_map()

