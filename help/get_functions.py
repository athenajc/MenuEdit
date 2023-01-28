import os
import re
import sys
import pydoc
import pathlib
import inspect
import pkgutil
from help_config import default_modules, name_map_list
from get_modules import *
from fileio import *
from pprint import pprint
from aui import SqlDB
import pandas as pd
import numpy as np

def get_sys_paths():
    for p in sys.path:
        print(p)
        
def walk_obj(objname, lst, modules, level):
    if objname.find('_') == 0:
        return
    obj = get_obj(objname)
    dct = get_module_members(objname, obj)        
    head = objname + '.'
    for obj1 in dct['function']:
        if obj1.find('_') != 0:
            lst.append(head+obj1)
    if level > 0 and level <=3:
        for obj1 in dct['module']:
            if obj1.find('_') == 0:
                continue
            if not obj1 in modules:
                #print(obj1)
                walk_obj(head + obj1, lst, level+1)

    for obj1 in dct['class']:
        if obj1.find('_') == 0:
            continue
        walk_obj(head + obj1, lst, modules, -1)        
        #functions = inspect.getmembers(get_obj(objname + '.' + obj1), inspect.isfunction)
        #if functions != []:
        #   print(objname, obj1, functions)

def walk_modules(modules):
    lst1 = []
    for objname in modules:
        print(objname)
        lst = []    
        walk_obj(objname, lst, modules, 0)    
        lst1 += lst
    
    return lst1
    
def get_func_fields(head, name):
    objname = head + name
    func = get_obj(objname)
    args, defaults, doc = '', '', ''    
    try:
        doc = str(func.__doc__)
        args = ', '.join(func.__code__.co_varnames)
        defaults = str(func.__defaults__)
        data = (objname, name, args, defaults, doc)
    except:
        data = (objname, name,  args, defaults, doc)
    return data
    
def get_obj_funcs(objname, lst, modules, level):
    if objname.find('_') == 0:
        return
    obj = get_obj(objname)
    module = objname.split('.')[0]
    dct = get_module_members(objname, obj)        
    head = objname + '.'
    for obj1 in dct['function']:
        if obj1.find('_') != 0:
            #lst.append(get_func_fields(head, obj1))
            lst.append((head+obj1, obj1, module))
    if level > 0 and level <=3:
        for obj1 in dct['module']:
            if obj1.find('_') == 0:
                continue
            if not obj1 in modules:
                #print(obj1)
                get_obj_funcs(head + obj1, lst, level+1)

    for obj1 in dct['class']:
        if obj1.find('_') == 0:
            continue
        get_obj_funcs(head + obj1, lst, modules, -1)     

def get_all_function_list(modules):
    lst1 = []
    for objname in modules:
        print(objname)
        lst = []    
        get_obj_funcs(objname, lst, modules, 0)    
        lst1 += lst
    lst = list(set(lst1))
    lst.sort()    
    print(len(lst))
    return lst

def check_before_add_to_lst(lst, name):
    head = name.split('.', 1)[0]
    for s in lst:
        if s.split('.', 1)[0] == head:
            return False
    return True
    

    
def test_get_func_args():
    lst = [('pyatspi.','Accessible_getitem'), ('tkinter.Text.', 'tag_add')]
    for a, b in lst:
        func = get_func_fields(a, b)
        for s in func:
            print(s)
        #print(s, func.__code__.co_argcount, func.__code__.co_varnames, func.__defaults__)
        #print(func.__doc__)
        #print(dir(obj))
       # arg = inspect.getargs(obj)
       # print(arg)
       

def func_list_to_db():
    lst = get_lst('modules')
    func_lst = get_all_function_list(lst)
    db = SqlDB("/home/athena/data/help/func.db")
    keytypes = {'path':'string', 'name':'string', 'module':'string'} 
    db.from_list('func', keytypes, func_lst)                                          
    db.close()
    

def fetchset(db, table, key, order=''):
    #SELECT DISTINCT Country FROM Customers ORDER by
    res = db.execute("SELECT %s FROM %s" % (key, table))  
    print(type(res))
    return
    a = np.array(res.fetchall())[:, 0]
    return a
    
def func_namelist_to_db():
    db = SqlDB("/home/athena/data/help/func.db")
    lst = db.fetchall('SELECT COUNT(path), name FROM func GROUP BY name ORDER BY COUNT(path) DESC')     
    # GROUP BY name, ORDER BY name
    pprint(lst[0:10])
    pprint(lst[-10:])   
    return lst
    db = SqlDB("/home/athena/data/help/funcmap.db")
    #(objname, name, func.__code__.co_varnames, func.__defaults__, func.__doc__)
    #keytypes = {'path':'string', 'name':'string', 'args':'string', 'defaults':'string', 'doc':'string'}
    keytypes = {'name':'string', 'path':'string'} 
    db.from_list('func', keytypes, name_lst)                                          
    db.close()
    
      
    
if __name__ == '__main__': 
    #test_get_func_args()
    if 0:
        func_list_to_db()
    #query_func_from_db('tag_a')    
    func_namelist_to_db()
    
        
        

