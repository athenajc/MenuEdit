import tkinter as tk

from aui import App, aFrame, ImageObj, Layout, Text, TreeView, FileTreeView
from aui import MenuBar, Messagebox

def add_text(master, TextClass=Text):
    if TextClass == None:
        TextClass = Text
    textbox = TextClass(master)
    if hasattr(textbox, 'init_dark_config'):
        textbox.init_dark_config()   
    textbox.tag_config('find', foreground='black', background='#999')    
    return textbox
    
def add_msg( master):
    msg = Messagebox(master)
    msg.tk.setvar('msg', msg)    
    master.msg = msg
    return msg
    
def add_filetree(master, TreeFrame=FileTreeView):
    tree = TreeFrame(master)
    tree.tk.setvar('filetree', tree)   
    master.filetree = tree
    master.tree = tree
    return tree
    
def add_tree(master, TreeFrame=TreeView):
    tree = TreeFrame(master)
    tree.tk.setvar('filetree', tree)   
    master.tree = tree
    return tree
    
def add_menu(master):
    names = 'New,Open,,Close,,History,,Save,Save as,,Undo,Redo,,Copy,Cut,Paste,,'
    names += 'Add Tab,Remove Tab,,Graph'
    menubar = MenuBar(master, items=names.split(',')) 
    return menubar
    
def add_set1(app):
    layout = Layout(app)
    menu = add_menu(app)
    layout.add_left(menu, 100)
    f0 = app.textbox = add_text(app)
    f0.init_dark_config()
    f1 = app.msg = add_msg(app)    
    tree = app.tree = add_tree(app)
    layout.add_set1(objs=(tree, f0, f1))
    

def test_layout():               
    app = App(title='APP', size=(1500,860))
    add_set1(app)
    app.mainloop()
    
def test_image():
    w, h = 800, 600
    size = w, h
    bkg = ImageObj(size=size) 
    bkg.get_draw()          
    bkg.gradient('r', 'GnBu')
    bkg.draw.rectangle((10, 10, w-10, h-10), outline=(0, 0, 0, 128))
    bkg.draw.rectangle((9, 9, w-11, h-11), outline=(255, 255, 255, 180))
    bkg.show()
    
if 1:
    test_layout()
else:    
    test_image()
    

