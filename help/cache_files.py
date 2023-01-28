import os
import sys

from ModuleDB import ModuleDB
from SqlDB import CacheDB
from pprint import pprint, pformat
import re
import pygments
from pygments.lexers import Python3Lexer
import pandas as pd
from pathlib import Path
from collections import Counter, ChainMap
from dataclasses import dataclass

from fileio import fread, fwrite, walkdir
import aui
from aui import *

# ChainMap   一個類似 dict 的類別，用來為多個對映 (mapping) 建立單一的視圖 (view)
# Counter  dict 的子類別，用來計算可雜湊 (hashable) 物件的數量

db = ModuleDB()
lexer = Python3Lexer()

def get_modules():
    return db.fetch_modules()   
 
def test():    
    lst = db.fetch('SELECT * FROM module_file')
    for m in lst[1:2]:
        name, path = m
        path = os.path.dirname(path)
        files = walkdir(path)
        

        
def grep_key(fn, key):
    try:
        text = fread(fn)
    except:
        return []    
    if not key in text:
        return []
        
    lst = re.findall('[\w\_]+%s[\w\_]+' %key, text)
    print(lst)
    return lst
    
def test_search_files_key(path, key):
    path = '/home/athena/.local/lib/python3.8/site-packages'
    #path = '/usr/lib/python3.8/lib2to3'
    lst = walkdir(path)
    for fn in lst:
        print(fn)
        grep_key(fn, key)     
    
#test_search_files_key('/usr/lib/python3.8', 'asynio')


def grep(fn):
    try:
       text = fread(fn)
    except:
       return []
    if 0:
        dct = {}    
        dct['file'] = str(fn)
        dct['class'] = re.findall('(?<=class\s)\s*[\w\_]+', text)
        dct['def'] = re.findall('(?<=def\s)\s*[\w\_]+', text)
        dct['counter'] = dict(Counter(re.findall('[\w\_]{3,128}', text)))
    #pprint(dct)
    return Counter(re.findall('[\w\_]{3,128}', text))
    
def grep_tuple(fn):
    try:
       text = fread(fn)
    except:
       return []
    dct = {}
    dct['files'] = str(fn)
    dct['class'] = re.findall('(?<=class\s)\s*[\w\_]+', text)
    dct['def'] = re.findall('(?<=def\s)\s*[\w\_]+', text)
    words = re.findall('[a-zA-Z][\w\_]{2,64}', text)
    dct['words'] = list(set(words))

    lst = []    
    lst.append( str(fn))
    for k in ['class', 'def', 'words']:
        lst.append(','.join(dct[k]))
   
    #pprint(dct)
    return lst

    
def gen_file_index_data(index):
    #path = '/usr/lib/python3.8/lib2to3'
    db = SqlDB("/home/athena/data/test1.db") 
    keytypes = {'file':'string', 'class':'text', 'def':'text', 'words':'text'} 
    if index == 0:
        path = '/usr/lib/python3.8'
    else:    
        path = '/home/athena/.local/lib/python3.8/site-packages'
        
    datalist = []
    flst = walkdir(path)
    i = 0
    for fn in flst:
        print(i, fn)
        data = grep_tuple(fn)
        if data != []:
           datalist.append(data)
        i += 1
    #pprint(dct)
    db.from_list('file_index', keytypes, datalist)
    print('done')

def gen_file_index_db():
    gen_file_index_data(0)
    gen_file_index_data(1)

def grep1(fn):
    try:
       text = fread(fn)
    except:
       return []
    return re.findall('[\w\_]{3,128}', text)

def store_filelist():
    path0 = '/usr/lib/python3.8'
    path1 = '/home/athena/.local/lib/python3.8/site-packages'        
    lst = []

    flst = walkdir(path0) + walkdir(path1)
    
    
    fwrite('/home/athena/data/pyfile.list', str(flst))
    return 
        
def test():
    db = CacheDB()
    text = db.get('python file list')[0]

    flst = eval(text)    

    i = 0
    for fn in flst:
        print(i, fn)
        #lst += grep1(fn)
        i += 1
    return    
    dct = dict(Counter(lst))
    #text = pformat(dct)
    datalist = [(k,v) for k,v in dct.items()]
    keytypes = {'word':'string', 'counter':'integer'} 
    db = SqlDB("/home/athena/data/test1.db") 
    db.from_list('word_count', keytypes, datalist)
    #fwrite('/home/athena/tmp/counter.json', text)

store_filelist()

