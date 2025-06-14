import tkinter as tk
import re

class TagObj(object):
    def __init__(self, tag, content, span, isend):
        self.tag = tag
        self.isend = isend
        content = content.strip()
        self.without_endtag = content.endswith('/')
        self.content = content        
        self.style = {}
        self.dct = self.get_content(self.content)
        self.span = span
        self.start, self.end = None, None
        self.flag = ''
        self.children = []                
        self.id = self.dct.get('id')
        self.xlink = self.dct.get('xlink:href')
        #self.items = self.dct.items
        self.keys = self.dct.keys
        self.values = self.dct.values
           
    def get(self, key, default=None):        
        if key in self.dct:
            return self.dct.get(key)
        if key in self.style:
            return self.style.get(key)            
        return default
            
    def items(self):
        return self.dct.items()
            
    def copy(self):
        obj = TagObj(self.tag, self.content, self.span, self.isend)
        obj.children = self.children.copy()
        return obj  
        
    def get_children(self):
        return self.children
    
    def get_content(self, text):
        dct = {}
        for m in re.finditer('(?P<item>[\w\.\:\/\-\#]+)\s*\=\s*\"(?P<value>[^\"]+)\"', text):    
            item, value = m.group('item'), m.group('value')     
            if ':' in item:
                item = item.split(':')[-1].strip()       
            dct[item] = value
            if item == 'style':
                self.style = self.get_style_dct(value)
                for k, v in self.style.items():
                    if dct.get(k) == None:
                       dct[k] = v
        return dct
        
    def get_style_dct(self, style_str):
        #"fill:rgb(0,0,255);stroke-width:3;stroke:rgb(0,0,0)"
        dct = {}
        for s in style_str.split(';'):
            if not ':' in s:
                continue
            p = s.split(':')
            k, v = p[0], p[1].strip()                        
            dct[k] = v
        return dct
        
class XmlTree(object):
    def __init__(self, text):
        self.get_xml_tree(text)

    def get_xml_tag(self, pobj, level):
        objlevel = level + 1     
        while self.tagobjs != []:
            obj = self.tagobjs.pop(0)
            tag = obj.tag            
            if obj.isend == '/':                
                i = self.tagends.index(tag)
                self.tagends.pop(i)
                return             
            pobj.children.append(obj)  
            if obj.without_endtag == True:
                continue     
            if self.tagends.count(tag) > 0:     
                self.get_xml_tag(obj, objlevel)               
        return 
               
    def get_xml_tree(self, text):
        self.tagends = []            
        tagobjs = []        
        #text = text.replace('\n', '')
        p1 = '(\<(?P<tag>[\w\:\-\_]+))'
        p2 = '((?P<content>[^\>]*)\>)'
        p3 = '((?P<tagend>\<\/[\w\:\-\_]+)\>)'
        pattern = '(%s\s*%s)|%s' % (p1, p2, p3)
        p0 = '\<[^\>]+\>'
        for m in re.finditer(pattern, text): 
            tag = m.group('tag')
            if tag == None:
               tag = m.group('tagend').replace('</', '')
               isend = '/'               
               self.tagends.append(tag)
               content = ''
            else:
               content = m.group('content')
               isend = ''                     
                     
            obj = TagObj(tag, content, m.span(), isend)   
            tagobjs.append(obj)    
        
        self.tagobjs = tagobjs.copy()
        self.root = self.tagobjs.pop(0)
        self.get_xml_tag(self.root,  0)    


if __name__ == '__main__':      
    from treeview import TestFrame
    def main():
        root = tk.Tk()
        root.title('Frame and Canvas')
        root.geometry('500x900') 
        frame = TestFrame(root)
        frame.pack(fill='both', expand=True)
        frame.on_select_file('/home/athena/src/svg/3depict.svg', '')
        frame.set_path('/home/athena/src/svg')
        frame.mainloop()   
    
    main()






