import os
import re
import sys
import pydoc
import pathlib

import inspect
import pkgutil
from DB.fileio import *
from DB import SqlDB
import pandas as pd
import numpy as np
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from pprint import pprint
from help_config import default_modules, name_map_list
sys_module_list = list(sys.modules.keys())

objdct = {}        

def get_obj(thing):
    global objdct
    if type(thing) != str:
        return thing
    if thing in objdct:
        return objdct.get(thing)
    try:    
        obj, name = pydoc.resolve(thing)
        objdct[name] = obj
    except:
        return None    
    return obj
    
def get_attr(obj, key):
    if obj == None:
        return None
    if hasattr(obj, key) == False:
        return None
    try:
        return obj.__getattribute__(key)
    except:            
        return None
        
def get_doc(obj):
    doc = get_attr(obj, '__doc__')
    return doc

def get_help(objname, obj=None): 
    if '*' in objname:
        #objname = objname.replace('*')
        return None
    if obj == None:
        obj = get_obj(objname)
    if obj == None:
        return None        
    try:    
        text = pydoc.render_doc(obj, title='%s:')
    except:
        return None    
    return text      

def get_dir_members(name, obj):
    lst = []
    head = name + '.'
    for s in dir(obj):
        if s[0:1] != '_':
            objname = head + s
            lst.append(objname)            
    return lst
    
def pkg_iter_modules(lst=[]):     
    for p in pkgutil.iter_modules():
        importer, name, ispkg = p
        importer = str(importer)
        if not 'python' in importer or '_' in name:
            continue
        if ispkg and not name in lst:
            lst.append(name)                  
    return lst             

def get_module_members(objname, obj=None):
    #self.msg.puts('get_module_members', objname)      
    if obj == None:
        obj = get_obj(objname)
    dct = {'module':[], 'class':[], 'function':[]}
    try:
        for name, des in inspect.getmembers(obj):
            for item in dct:
                if str(des).find(item) == 1:                    
                    dct[item].append(name)
    except:
        print('get_module_members error')        
    return dct   
    
def get_members(objname, obj=None):   
    dct = get_module_members(objname, obj)      
    lst = dct['module'] + dct['class'] + dct['function']      
    return lst

def get_subobjs(objname, obj=None):    
    dct = get_module_members(objname, obj)      
    lst = dct['module'] + dct['class']    
    return lst
    
def get_classes(objname, obj=None):    
    dct = get_module_members(objname, obj)      
    lst = dct['class']    
    return lst


iter_modules = pkg_iter_modules(list(default_modules)) 
all_modules = iter_modules + sys_module_list

def get_lst(objname, obj=None):
    if objname == 'modules':
        return iter_modules
    elif objname == 'default_modules':
        return default_modules    
    if obj == None:    
        obj = get_obj(objname)    
    lst = get_dir_members(objname, obj)
    return lst

def get_obj_module(name):
    if name == '':
        return ''
    if name in default_modules:
        return name
    obj = get_obj(name)
    if inspect.ismodule(obj):
        return name
    if '.' in name:
        name = name.rsplit('.', 1)[0]
        return get_obj_module(name)
    return ''    

def get_sourcefile(objname):
    obj = get_obj(objname)
    file = inspect.getsourcefile(obj)
    return file

    
if __name__ == '__main__':    
    pass


 

