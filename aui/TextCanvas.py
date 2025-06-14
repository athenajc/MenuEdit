import os
import re
import sys
import inspect
import subprocess
import tkinter as tk
from tkinter import font    
      
t = """
# comments
This is a string.
"""

t1 = """

testskla da alke
"""
#----------------------------------------------------------------------------------
class TextLine():
    def __init__(self, canvas, x, y, text, textlist):
        self.x0 = x
        self.y0 = y
        self.selitem = None
        self.bbox = (x, y, x, y)
        self.canvas = canvas
        self.msg = None
        self.text = text
        self.items = []
        self.len = 0
        self.sel_range = None
        self.selected = False    
        self.set_line_text(text, textlist)        
        
    def moveto(self, y):        
        dx = 0
        dy = y - self.y0       
        if self.selitem != None:
            self.canvas.move(self.selitem, dx, dy)
        for item in self.items:
            self.canvas.move(item, dx, dy)          
        self.y0 = y
        self.y1 += dy
        
    def clear(self):
        self.delete_sel_bar()
        for item in self.items:
            self.canvas.delete(item)
        self.items = []
        self.text = {}
            
    def inside(self, x, y):
        return (y >= self.y0 and y < self.y1)
        
    def overlape(self, x0, y0, x1, y1):
        x, y, x2, y2 = self.bbox 
        if y0 >= y and y0 <= y2:
            return True
        if y1 >= y and y1 <= y2:
            return True
        if (y >= y0 and y <= y1) or (y2 >= y0 and y2 <= y1):
            return True
        return False
            
    def delete_sel_bar(self):        
        if self.selitem != None:
            self.canvas.delete(self.selitem)
            self.selitem = None
            
    def draw_sel_bar(self, bkg, range):
        if self.selitem != None:
            self.delete_sel_bar()
        j0, j1 = range
        self.sel_range = (j0, j1)
        x0, x = self.get_range(j0)
        x1, x = self.get_range(j1)
        y0 = self.y0
        y1 = self.y1        
        selitem = self.canvas.create_rectangle(x0, y0, x1, y1, fill='#dcdcdf', outline='')
        self.canvas.lower(selitem)  
        self.selitem = selitem
        
    def unselect(self):
        self.selected = False
        self.sel_range = None
        self.delete_sel_bar()
        
    def select(self, j0, j1=None):        
        if self.selected == True and self.sel_range == (j0, j1):
            return  
        if j1 == 'e':
            j1 = self.len
        if j0 == 'line':
            j0, j1 = 0, self.len  
        if j0 > j1:
            j0, j1 = j1, j0        
        if j1 >= self.len:
            j1 = self.len
        if j0 < 0:
            j0 = 0      
        self.sel_range = (j0, j1)
        self.selected = True  
        self.delete_sel_bar() 
        if j1 == None or j0 == j1:
            return
        self.draw_sel_bar('#ddd', (j0, j1))    
            
    def set_line_text(self, text, taglist):
        self.clear()
        canvas = self.canvas      
        self.text = text
        self.taglist = None
        xlst = []  
        x, y = self.x0, self.y0       
        x1, y1 = x, y
        for text, tag in taglist:
            if text == '':
                continue            
            conf = canvas.vars.get(tag, {}) 
            font = conf.get('font', 'Mono 10')
            color = conf.get('color', '#111')     
            item = canvas.create_text(x, y, text=text, anchor='nw', font=font, fill=color, tag='text')             
            self.items.append(item)     
            bbox = canvas.bbox(item)
            x0, y0, x1, y1 = bbox
            n = len(text)
            w = (x1 - x0) / n
            for i in range(n):
                xlst.append((x, x+w))
                x += w
            x = x1                  
        xlst.append((x, x+8.5))      
        self.xlst = xlst    
        self.y1 = y1
        self.x1 = x1
        self.h = self.y1 - self.y0
        self.len = len(xlst)         
        
    def get_selected_text(self):
        if self.sel_range == None:
            return ''
        j0, j1 = self.sel_range
        return self.get_text_by_range(j0, j1-1)

    def get_text_by_range(self, j0, j1):
        n = len(self.text)
        if j1 == 'e':
            j1 = n-1
        if j0 > j1:
            j0, j1 = j1, j0
        if j0 < 0:
            j0 = 0        
        if j1 >= n:
            j1 = n-1
        return self.text[j0:j1+1] 
    
    def get_range(self, j):        
        if self.xlst == []:
            return (0,0)
        elif j >= self.len:
            return self.xlst[-1]
        else:
            return self.xlst[j]  
            
    def get_indent(self):
        s = self.text
        s1 = s.strip()
        if s1 == '':
            j0 = 0
        else:
            j0 = s.find(s1[0])
        return j0
        
    def find_text(self, key):
        return self.text.find(key)
            
#-------------------------------------------------------------------------------------
class TextEdit():            
    def on_keydown(self, event):        
        key = event.keysym         
        action = self.key_actions.get(key)
        char = event.char
        self.keystate = event.state
        if key == 'Shift_L':
            self.vars['Shift_L'] = True
        if event.state == 0x14:
            self.key_control(key)
        elif action != None:
            action(key)     
        elif char != '' and char != None:            
            self.key_insert(char) 
        elif event.state == 0x11:
            #self.msg.puts('shift tab', key, char)
            self.remove_tab()
        self.statusbar.set_var('Key', str((key, char, event.state))) 
        
    def on_keyup(self, event):        
        key = event.keysym 
        self.keystate = event.state
        if key == 'Shift_L':
            self.vars['Shift_L'] = False 
            self.keystate = 0           
        self.statusbar.set_var('Key', str((key, event.char, event.state)))
        
    def bind_key_actions(self):
        dct = {}
        dct['Left'] = self.key_move_left
        dct['Right'] = self.key_move_right
        dct['Up'] = self.key_move_up
        dct['Down'] = self.key_move_down
        dct['Prior'] = self.key_move_pageup
        dct['Next'] = self.key_move_pagedown        
        dct['Home'] = self.key_move_home
        dct['End'] = self.key_move_end
        dct['BackSpace'] = self.key_backspace
        dct['Delete'] = self.key_delete
        dct['Enter'] = self.key_enter
        dct['Return'] = self.key_enter
        dct['F5'] = self.remove_tab
        dct['F6'] = self.add_tab
        self.key_actions = dct
        self.control_acts = {'z':self.edit_undo, 'y':self.edit_redo, 'f':self.edit_find,
                             'c':self.edit_copy, 'v':self.edit_paste, 'x':self.edit_cut}
        self.shift_acts = {}        

    def key_control(self, key):
        #self.msg.puts('control', key)        
        act = self.control_acts.get(key)
        if act == None:
            return
        act()
        
    def insert_at_pos(self, pos, t):
        i, j = pos
        if t == '\t':
            t = '    '
        self.move_cursor(i, j+len(t))
        item = self.get_item(i) 
        s = item.text         
        n = len(s)   
        text = s[0:j] + t + s[j:]
        cursorpos = (i, j+len(t))
        self.replace_line(i, item, text, cursor=cursorpos)
        
    def key_insert(self, char):        
        if self.sel1 != None and self.sel0 != self.sel1:
            if char == '\t':
                self.add_tab()
                return
            else:    
                self.replace_sel(char)
                return                     
        self.insert_at_pos(self.cursorpos, char)
        
    def key_backspace(self, key):
        if self.sel1 != None and self.sel0 != self.sel1:
            self.replace_sel('')
            return
        i, j = self.cursorpos
        if i == 0 and j == 0:
            return
        item = self.get_item(i)       
        if j == 0:
            item0 = self.get_item(i - 1)
            text = item0.text + item.text
            self.replace_items((i-1, 0, i, item.len), text, cursor=(i-1, item0.len))  
        else:
            s = item.text
            n = len(item.text)
            if j > n:
                j = n
            text = s[0:j-1] + s[j:] 
            self.replace_line(i, item, text, cursor=(i, j-1))
        
    def key_delete(self, key):
        if self.sel1 != None and self.sel0 != self.sel1:
            self.replace_sel('')
            return
        i, j = self.cursorpos
        item = self.get_item(i) 
        s = item.text      
        if j < len(s):            
            text = s[0:j] + s[j+1:]
            self.replace_line(i, item, text, cursor=(i, j))
        else:                        
            item1 = self.get_item(i+1)
            text = item.text + item1.text
            self.replace_items((i, 0, i+1, item1.len), text, cursor=(i, j))
        
    def key_enter(self, key):    
        if self.sel1 != None and self.sel0 != self.sel1:
            self.replace_sel('')
            return                  
        i, j = self.cursorpos
        item = self.get_item(i)  
        if type(item.text) != str:
            #self.msg.puts('err',item.text)
            return       
        s = item.text
        indent = s.find(s.strip())
        text = s[:j] +'\n' + ' ' * indent  + s[j:]         
        self.replace_line(i, item, text, cursor=(i+1, indent))    
        
    def key_move_home(self, key):    
        i, j = self.cursorpos 
        i0, j0 = i, j
        item = self.get_item(i)
        self.move_cursor(i, 0)
        
    def key_move_end(self, key):    
        i, j = self.cursorpos 
        i0, j0 = i, j
        item = self.get_item(i)
        self.move_cursor(i, item.len) 
            
    def key_move_left(self, key):    
        i, j = self.cursorpos    
        item = self.get_item(i)
        if j > item.len:
            j = item.len
        j -= 1            
        if j < 0:
            i = self.set_line(i - 1)
            j = self.items[i].len  
        self.move_cursor(i, j)   
        
    def key_move_right(self, key):    
        i, j = self.cursorpos 
        item = self.get_item(i)
        j += 1
        if j > item.len:
            i = self.set_line(i + 1)
            j = 0 
        self.move_cursor(i, j)
         
    def key_move_up(self, key):    
        i, j = self.cursorpos 
        i = self.set_line(i - 1)
        self.move_cursor(i, j)
        
    def key_move_down(self, key):    
        i, j = self.cursorpos 
        i = self.set_line(i + 1)                                
        self.move_cursor(i, j)

    def key_move_pageup(self, key):    
        i, j = self.cursorpos 
        y0, y1 = self.yview_range
        n = y1 - y0
        self.yview_scroll(-1, 'page')
        i = self.set_line(i - n)
        self.move_cursor(i, j)
        
    def key_move_pagedown(self, key):    
        i, j = self.cursorpos 
        y0, y1 = self.yview_range
        n = y1 - y0
        self.yview_scroll(1, 'page')
        i = self.set_line(i + n)                               
        self.move_cursor(i, j)
        
    def get_selrange(self):
        i0, j0 = self.sel0
        i1, j1 = self.sel1           
        if i0 > i1:
            i0, i1 = i1, i0
            j0, j1 = j1, j0
        elif i0 == i1 and j0 > j1:
            j0, j1 = j1, j0
        return (i0, j0, i1, j1)
        
    def set_selrange(self, i0, j0, i1, j1):
        self.sel0 = (i0, j0)
        self.sel1 = (i1, j1)
            
    def add_tab(self, key=None):
        i, j = self.cursorpos 
        i0, j0, i1, j1 = self.get_selrange()
        space = ' ' * 4
        lst = []                   
        for item in self.items[i0:i1+1]:
            lst.append(space + item.text)         
        text = '\n'.join(lst)      
        item1 = self.get_item(i1)        
        self.sel1 = None   
        self.replace_items((i0, 0, i1, item1.len), text, cursor=(i, j))
        self.set_selrange(i0, 0, i1, item1.len)
            
    def remove_tab(self, key=None):
        if self.sel1 == None:
            return
        i, j = self.cursorpos 
        i0, j0, i1, j1 = self.get_selrange()  
        lst = []
        for item in self.items[i0:i1+1]:            
            lst.append('\n' + item.text)
        text = ''.join(lst)
        text = text.replace('\n    ', '\n')
        newtext = text[1:]
        item1 = self.get_item(i1)
        self.sel1 = None
        self.replace_items((i0, 0, i1, item1.len), newtext, cursor=(i, j))       
        self.set_selrange(i0, 0, i1, item1.len)
            
    def edit_find(self, arg=None):
        if arg != None:
            key = arg
        else:
            key = self.get_text('sel')
        if len(key) < 3:
            key, pos = self.get_current_word()
        if '\n' in key:
            key = key.split('\n', 1)[0]
        pass
                                
    def undo_replace(self, dct):   
        dst = dct.get('src')
        src = dct.get('dst')
        range = dct.get('range')
        i, j, i1, j1 = range
        n = src.count('\n') + 1
        i2 = i + n - 1
        item0 = self.get_item(i)
        item1 = self.get_item(i2)
        self.y = item0.y0 
        for item in self.get_items((i, i2)):
            item.clear()       
            self.items.pop(i)             
        self.insert_text(i, dst)       
        
    def edit_undo(self, arg=None):
        if self.records == []:
            return              
        dct = self.records.pop()  
        self.undolist.append(dct)      
        act = dct.get('act')
        if act == 'replace':          
            self.edit_modified.append(dict(act='undo', data=dct))
        
    def edit_redo(self, arg=None):
        if self.undolist == []:
            return  
        dct = self.undolist.pop()  
        self.edit_modified.append(dct)
        #self.msg.puts('redo')
        
    def edit_copy(self):   
        text = self.get_text('sel') 
        self.clipboard_clear()
        self.clipboard_append(text)    
    
    def edit_cut(self):
        text = self.get_text('sel') 
        self.clipboard_clear()
        self.clipboard_append(text)            
        self.replace_sel('')
        
    def edit_paste(self):
        text = self.clipboard_get()
        self.replace_sel(text)  
        
    def get_line_text(self, i):
        item = self.get_item(i)
        return item.text
        
    def get_current_word(self):
        i, j = self.cursorpos
        item = self.get_item(i)      
        for m in re.finditer('\w+', item.text):
            s, e = m.start(), m.end()
            if j >= s and j <= e:
                j = s
                return item.text[s:e], (s,e)
        return '', (0, 0)
        
    def goto_define(self, key):
        text = self.get_text()
        lst = re.findall('%s\s*\(.*:'%key, text)
        if lst == []:
            return      
        token = lst[-1]        
        i0 = text.find(token)
        i = text[0:i0].count('\n')     
        line = self.get_line_text(i)     
        j = line.find(key)
        self.set_selrange(i, j, i, j + len(key))
        self.set_line(i)
        self.move_cursor(i, j)  
        return     
        
    def on_goto_define(self, event=None):
        key = self.get_text('sel')
        if key == '':
            key, pos = self.get_current_word()
        self.goto_define(key)       
                    
    def on_search_help(self, event=None):
        text = self.get_text('sel')
        if 'ttk.' in text:
            text = text.replace('ttk.', 'tkinter.ttk.')
        elif 'tk.' in text:
            text = text.replace('tk.', 'tkinter.')
        self.helpbox.set_item(text)       
        
    def on_select_all(self, event=None):
        n = len(self.items)
        item0 = self.items[0]
        item1 = self.items[n-1]
        j0 = item0.len
        j1 = item1.len        
        self.select_lines = (0, j0, n-1, j1) 
        
    def on_replace(self, event=None):
        pass      
        
#------------------------------------------------------------------------------------------
class PopMenu():
    def add_popmenu(self, cmds=[]):
        menu = tk.Menu(self)
        self.menu = menu
        for p in cmds:
            if p[0] == '-':
                menu.add_separator()
            else:
                menu.add_command(label=p[0], command=p[1])         
        self.menu = menu   
        self.bind('<ButtonRelease-3>', self.post_menu)              
        self.menu.posted = False

    def unpost_menu(self, event=None):
        if self.menu.posted:
            self.menu.unpost()
        
    def post_menu(self, event=None):
        self.menu.posted = True
        x, y = event.x, event.y   
        x1 = event.widget.winfo_rootx()     
        y1 = event.widget.winfo_rooty()
        self.menu.post(x + x1, y + y1)
        
#-------------------------------------------------------------------------------------
class TextCanvas(tk.Canvas, TextEdit, PopMenu):
    def __init__(self, master, width=None, height=None, **kw):
        super().__init__(master, **kw)        
        self.width = width * 12
        self.height = height * 16  
        self.set_region(1200, 1600)
        self.config(bg='#f7f6f5')
        self.text = None
        self.vars = {}
        self.vars['canvas'] = self
        self.vars['Shift_L'] = False
        self.init_pattern()
        self.init_config()
        self.records = []
        self.undolist = []
        self.items = []
        self.indexitems = []
        self.x = 0
        self.y = 0
        self.font_w = 9
        self.index = 1
        self.yview_range = (0,0)
        self.linecount = 100
        self.set_region()
        self.select_lines = None
        self.sel0 = (0, 0)
        self.sel1 = None
        self.cursorpos = (0,0)
        self.cursorstatus = 0
        self.cursoritem = None
        self.keystate = 0
        self.events = []
        self.edit_modified = []
        self.config(insertbackground ='#333')
        self.config(insertofftime =300, insertontime=500, insertwidth=2)

        self.bind_key_actions()
        menucmds = [('Find', self.edit_find),
            ('Goto Define', self.on_goto_define),
            ('Help', self.on_search_help),
            ('-'),
            ('Replace', self.on_replace),
            ('-'),
            ('Select All', self.on_select_all),
            ('-'),
            ('Copy', self.edit_copy),
            ('Paste', self.edit_paste),
            ('-'),
            ('Add Tab', self.add_tab),
            ('Remove Tab', self.remove_tab)] 
        self.add_popmenu(menucmds)
        self.bind('<Button-4>', self.on_scrollup)
        self.bind('<Button-5>', self.on_scrolldown)  
        self.bind('<ButtonPress-1>', self.on_button_down)
        self.bind('<B1-Motion>', self.on_button_motion) 
        self.bind('<KeyPress>', self.on_keydown)
        self.bind('<KeyRelease>', self.on_keyup)
        self.focus_force()   
        self.click_time = 0
        self.ticks = 0   
        self.after(10, self.tick_action) 
        
    def set_line(self, i):
        n = self.linecount
        y0, y1 = self.yview_range
        n1 = y1 - y0
        if i < 0:
            i = 0       
        elif i > n - 1:
            i = n - 1    
        if i < y0 - 1 or i > y1 + 1:
            self.yview_moveto((i - n1/2) / n)  
        elif i <= y0:
            self.yview_moveto(i / n)          
        elif i >= y1:            
            self.yview_moveto((i - n1) / n)    
        return i
    
    def see_line(self, i):
        self.set_line(i)
        for item in self.get_items('sel'):
            item.unselect()        
        item = self.get_item(i)
        self.set_selrange(i, 0, i, item.len)
        
    def del_cursor(self):
        self.delete('cursor')
                
    def create_cursor(self):
        i, j = self.cursorpos        
        item = self.get_item(i)
        y0, y1 = item.y0, item.y1
        x0, x1 = item.get_range(j)
        self.cursoritem = self.create_rectangle(x0, y0, x0+1, y1, outline='#000', tag='cursor')
        self.cursorstatus = 1
                
    def move_cursor(self, i, j):
        self.cursorstatus = 'move'
        self.cursorpos = (i, j)
        if self.vars['Shift_L']:
            self.sel1 = (i, j)
        else:
            self.sel0 = (i, j)
            self.sel1 = (i, j)
        
    def draw_cursor(self):    
        i, j = self.cursorpos
        bbox = self.bbox('cursor')
        if bbox == None:
            self.del_cursor()
            self.create_cursor()
            return        
        bx, by, bx1, by1 = bbox
        item = self.get_item(i)
        x0, x1 = item.get_range(j)        
        dx = x0 - bx
        dy = item.y0 - by
        if dx != 0 or dy != 0:
            self.move(self.cursoritem, dx, dy) 
        self.itemconfig(self.cursoritem, outline='#000')
        self.cursorstatus = 1
        
    def check_cursor(self):
        if self.cursoritem == None:
            self.create_cursor()
        else:
            if self.cursorstatus == 1:
                self.itemconfig('cursor', outline='')
                self.cursorstatus = 0
            else:
                self.draw_cursor()
                
    def check_items(self):        
        if self.edit_modified == []:
            #self.setvar('EditorTextModified', False)
            return          
            
        #self.msg.puts(self.edit_modified)
        while self.edit_modified != []:
            dct = self.edit_modified.pop(0)
            act = dct.get('act')    
            if act == 'replace':
                self.records.append(dct)
                self.do_replace(dct)
            elif act == 'undo':
                #self.msg.puts('check_undo')
                self.undo_replace(dct.get('data'))
            if 'cursor' in dct:
                p = dct.get('cursor')
                i, j = p
                self.move_cursor(i, j)  
          
        y = self.items[0].y0
        i = 0
        for item in self.items: 
            if item.taglist != None:
                item.set_line_text(item.text, item.taglist)   
                i += 1       
            if item.y0 != y: 
                item.moveto(y)
                i += 1 
            y = item.y1
        self.update_line_count()
        self.edit_modified = []
            
    def tick_action(self):          
        self.ticks += 1
        if self.cursorstatus == 'move':
            self.draw_cursor()
        else:
            t = self.ticks % 45
            if t == 0:
                self.check_cursor()
        self.check_selection()
        self.check_items()
        self.after(10, self.tick_action)

    def get_item(self, i):
        n = len(self.items)
        if i < 0:
            i = 0
        elif i >= n:
            i = n - 1
        return self.items[i]
        
    def get_item_by_pos(self, x, y):
        for i, item in enumerate(self.items):
            if y >= item.y0 and y < item.y1:
                j = 0
                for x0, x1 in item.xlst:                   
                    if x >= x0 and x < x1:
                        return i, j
                    j += 1
                return i, j
        return self.cursorpos
             
    def select_none(self):
        for item in self.get_items('sel'):
            item.unselect()
        self.select_lines = None
        self.sel1 = None
            
    def on_button_down(self, event):
        self.unpost_menu()
        time_offset = event.time - self.click_time
        double_click = (time_offset < 500)
        self.click_time = event.time
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)  
        i, j = self.get_item_by_pos(x, y)       
        if self.vars['Shift_L']:
            self.sel1 = (i, j)
        elif double_click:
            item = self.get_item(i)
            word, pos = self.get_current_word()
            j0, j1 = pos
            self.select_lines = (i, j0, i, j1)  
            self.move_cursor(i, j0)          
            self.sel0 = (i, j0)
            self.sel1 = (i, j1)            
        else:
            self.select_lines = None             
            self.move_cursor(i, j)   
        if self.focus_get() != self:
            self.focus_set()   
        
    def on_button_motion(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)  
        i, j = self.get_item_by_pos(x, y) 
        self.sel1 = (i, j)
        self.select_lines = self.sel0, self.sel1  
        
    def check_selection(self):
        if self.sel1 == None or self.sel0 == self.sel1:
            for item in self.items:
                if item.selected:
                    item.unselect()
            return
        i0, j0, i1, j1 = self.get_selrange()
        for i, item in enumerate(self.items):  
            if i == i0:
                if i1 == i:
                    item.select(j0, j1)
                else:
                    item.select(j0, 'e')                    
            elif i == i1:
                item.select(0, j1)
            elif i > i0 and i < i1:
                item.select(0, 'e')    
            else:
                item.unselect()            
        
    def on_scrollup(self, event=None):  
        self.yview_scroll(-1, 'units')  
    
    def on_scrolldown(self, event):
        self.yview_scroll(1, 'units')       
        
    def set_region(self, w=1200, h=600):
        self.config(scrollregion=(0,0,w,h))
        self.w = w
        self.h = h     
    
    def get_region(self):
        return (self.w, self.h)       

    def tag_config(self, tag, **conf):
        if not tag in self.vars:
            self.vars[tag] = {'font': 'Mono 10', 'color': '#111'}
        for name in conf:
            self.vars[tag][name] = conf[name]    
            
    def init_config(self):
        sysfont = 'Mono 10 '      
        sysbold = sysfont + 'bold'  
        self.tag_config('key', font=sysbold, color='#338')
        self.tag_config('class', font=sysbold, color='#338')
        self.tag_config('classname', font=sysbold, color='#383')
        self.tag_config('str1', color='#a83')
        self.tag_config('str2', color='#a83')
        self.tag_config('int',  color='#393')
        self.tag_config('op',  color='gray')
        self.tag_config('self',  color='#333')
        self.tag_config('comments',  color='#789')
        self.tag_config('selected',  background='lightgray')        
                          
    def init_pattern(self):
        keys = 'from|import|def|class|if|else|elif|for|in|then|dict|list|continue|'
        keys += 'return|None|True|False|while|break|pass|with|as|try|exception'
        p0 = '(?P<class>class\s)(?P<classname>\s*\w+)'
        p1 = '|(?P<str1>\'[^\'\n]*\')|(?P<str2>\"[^\"\n]*\")'        
        p2 = '|(?<![\w])(?P<int>\d+)|(?P<op>[\=\+\-\*\/\(\)\.\%])|(?P<self>self)'       
        p3 = '|(?<![\w])(?P<key>%s)(?![\w])' % keys     
        p4 = '|(?P<comments>#.*)|\w+|[^\w]'     
        self.pattern = re.compile(p0 + p1 + p2 + p3 + p4)     
                
    def split_tokens(self, text):
        lst = []        
        for m in re.finditer(self.pattern, text):      
            tag = m.lastgroup        
            s = m.group(0)
            if tag == 'classname':                
                lst += [('class ', 'key'), (m.group(tag), tag)]
            else:
                lst.append((s, tag))
        if lst == []:
            lst.append(('    ', None))
        return lst
        
    def get_items(self, range=None):
        if range == None:
            return self.items
        elif range == 'sel':
            lst = []
            for item in self.items:
                if item.selected:
                    lst.append(item)
            return lst
        else:
            lst = []
            i, j = range
            for item in self.items[i:j+1]:
                lst.append(item)
            return lst
            
    def get_text(self, selrange=None):
        if selrange == None:
            lst = []
            for item in self.items:
                lst.append(item.text)
            return '\n'.join(lst) 
        elif selrange == 'sel':
            lst = []
            for item in self.get_items('sel'):
                lst.append(item.get_selected_text())
            return '\n'.join(lst) 
        else:
            i0, j0, i1, j1 = selrange                  
            if i0 == i1:
                item = self.get_item(i0)
                return item.get_text_by_range(j0, j1)                
            lst = []
            for i in range(i0, i1 + 1):
                item = self.get_item(i)
                if i == i0:
                    text = item.get_text_by_range(j0, 'e')
                elif i == i1:
                    text = item.get_text_by_range(0, j1)
                else:
                    text = item.text
                lst.append(text)      
            return '\n'.join(lst)    
                   
    def replace_sel(self, text):
        if self.select_lines == None:
            self.insert_at_pos(self.cursorpos, text)
            return          
        selrange = self.get_selrange()                
        i, j, i1, j1 = selrange
        if i == i1 and j > j1:
            j, j1 = j1, j  
        elif i1 < i:
            i, j, i1, j1 = i1, j1, i, j
        item0 = self.get_item(i)
        item1 = self.get_item(i1)
        text0 = item0.text[:j]
        text1 = item1.text[j1:]
        n = len(text)
        newtext = text0 + text + text1
        selrange = (i, 0, i1, item1.len)
        self.replace_items(selrange, newtext, cursor=(i, j+n))
        self.select_lines = None
        
    def replace_items(self, range, text, cursor=None):
        dct = dict(act='replace', range=range)
        dct['src'] = self.get_text(range)
        dct['dst'] = text
        if cursor != None:
            i, j = cursor
            self.move_cursor(i, j)
            dct['cursor'] = cursor
        self.edit_modified.append(dct)    
        
    def replace_line(self, i, item, text, cursor=None):        
        dct = dict(act='replace', range=(i, 0, i, item.len))
        dct['src'] = item.text
        dct['dst'] = text
        if cursor != None:
            i, j = cursor
            self.move_cursor(i, j)
            dct['cursor'] = cursor
        self.edit_modified.append(dct) 
                
    def do_replace(self, dct):       
        range = dct.get('range')
        if range == None:
            print('range = None') 
            return
        text = dct.get('dst', '')
        i, j, i1, j1 = range
        item = self.get_item(i)
        if i == i1:            
            if '\n' in text:
                self.y = item.y0 
                item.clear()       
                self.items.pop(i)             
                self.insert_text(i, text)
            else:
                taglist = self.split_tokens(text)
                item.set_line_text(text, taglist) 
            return 
        self.y = item.y0 
        for item in self.get_items((i, i1)):
            item.clear()       
            self.items.pop(i)             
        self.insert_text(i, text)
            
    def draw_line_text(self, i, y, text):
        taglist = self.split_tokens(text)               
        textitem = TextLine(self, self.x+64, self.y, text, taglist)       
        self.y = textitem.y1
        return textitem
        
    def insert_text(self, index, text):        
        for line in text.split('\n'):
            self.index = index
            textitem = self.draw_line_text(index, self.y, line)   
            self.items.insert(index, textitem)
            index += 1
       
    def draw_line_index(self, index, y0, y1):   
        bkg = self.create_rectangle(0, y0, 60, y1, fill='#cfcfcf', outline='')      
        item = self.create_text(5, y0, text=' %6d'%index, anchor='nw')        
        self.indexitems.append((item, bkg))
        
    def update_line_count(self):
        n = len(self.indexitems)
        n1 = len(self.items)   
        self.linecount = n1
        if n == n1:
            return     
        bottom = self.items[n1-1].y1 + 20
        self.delete('linebar')
        if n == 0:                      
            for i, item in enumerate(self.items): 
                self.draw_line_index(i+1, item.y0, item.y1)                
        elif n1 < n:
            for i in range(n1, n):
                p = self.indexitems.pop()
                self.delete(p[0])
                self.delete(p[1])
        elif n1 > n:
            for i in range(n, n1):
                item = self.items[i]
                self.draw_line_index(i+1, item.y0, item.y1)
        if bottom < 800:
            bkg = self.create_rectangle(0, 0, 60, 800, fill='#cfcfcf', outline='', tag='linebar')
            self.lower(bkg)
            bottom = 800
        else:
            bkg = self.create_rectangle(0, bottom-20, 60, bottom, fill='#cfcfcf', outline='', tag='linebar')            
            self.lower(bkg)
        self.set_region(h=bottom) 
        
    def clear_all(self):
        for item in self.find_all():
            if item != self.cursoritem:
                self.delete(item)
        self.items = []
        self.indexitems = []
        self.modified = []        
        self.x = 0
        self.y = 0
        self.index = 1      
            
    def insert(self, index, text):
        if type(index) == int:
            i = index            
        elif '.' in index:
            p = index.split('.')[0]
            i = int(p)
        elif index == 'end':
            i = self.linecount
        self.insert_text(i, text)
        
    def set_text(self, text):        
        self.clear_all()
        n = text.count('\n')
        self.text = text
        self.index = 0
        self.y = 0
        self.h = n * 20
        self.set_region(h=self.y)
        self.insert_text(0, text)    
        self.update_line_count()     

    def set_select_items(self, index1, index2):
        for i, item in enuermate(self.items):
            item.select(i >= index1 and i <= index2)          

            
#----------------------------------------------------------------------------------      
if __name__ == '__main__':    
    from fileio import *
    from aui import App
    app = App(title='Text Canvas Editor', size=(1000, 900))
    frame = app.twoframe(app, style='v', sep=0.7)
    
    textbox = TextCanvas(frame.top, width=80, height=30)
    textbox.pack(fill='both', expand=True)
    textbox.msg = app.add_msg(frame.bottom)
    text = fread(__file__)
    textbox.set_text(text)
    
    app.mainloop()
               








