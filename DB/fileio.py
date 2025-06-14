import os
import sys
import venv
from pathlib import Path
from collections import namedtuple
import urllib3
import io
import re
import numpy as np
from pprint import pprint 
#import DB

#>>> print(sys._home)
#/home/athena/.local/share/uv/python/cpython-3.13.3-linux-x86_64-gnu/bin
#>>> print(sys.prefix)
#/home/athena/.venv
#>>> print(sys.base_exec_prefix)
#/home/athena/.local/share/uv/python/cpython-3.13.3-linux-x86_64-gnu
#>>> print(sys.exec_prefix)
#/home/athena/.venv
#>>> print(sys.path[-1])


pdct = {}
data_path = os.path.expanduser('~/.cache/data/')

def get_data_path():
    return data_path 

def realpath(path):
    if '~' in path:
        i = path.find('~')
        path = path[i:]
        path = os.path.expanduser(path)    
    path = os.path.realpath(path) 
    return path

def fread(filename, path = None):
    if path != None:
        filename = path + os.sep + filename
    else:
        filename = realpath(filename)      
    text = ''
    try:
        with open(filename, 'r') as f:
            text = f.read()
            f.close()
    except Exception as e:
        print(e)                     
    return text

def fwrite(filename, text, path = None):
    if path != None:
        filename = path + os.sep + filename
    else:
        filename = realpath(filename)     
    try:   
        with open(filename, 'w') as f:
            f.write(text)
            f.close()
            return True
    except Exception as e:
        print(e)
    return False


def init_db_path():
    datapath = os.path.expanduser('~/data')
    
def init_path():
    fn = get_data_path() + 'path.dct'
    if os.path.exists(fn):
        text = fread(fn)
        dct = eval(text)
        return dct
    dct = {}
    userpath = os.path.expanduser('~/') 
    cachepath = userpath + '.cache/'
    datapath = cachepath + 'data/'
    p1 = sys.prefix + '/lib'
    p2 = sys.path[-1]  #/home/athena/.venv/lib/python3.13/site-packages
    p3 = userpath + 'src'
    p4 = userpath + 'test'
    p5 = userpath + 'tmp'
    
    dct ={'usr':userpath, 'local':p2, 'src':p3, 'test':p4, 'tmp':p5, 'p1':p1, 'p2':p2, 'p5':p5, 'dist':p5,
           'db':datapath, 'icon': datapath+"/icon", 'gallery':datapath+"/image", 'data':datapath}
    fwrite(fn, str(dct))
    return dct           
    
def get_path(name):
    global pdct
    if pdct == {}:
        pdct = init_path()
    if name == 'data':
        return get_data_path()
    path = pdct.get(name, None)
    
    if name in ['db', 'data', 'gallery', 'icon', 'src', 'local', 'icon', 'dist', 'tmp', 'test']:
        pdct = init_path()
    if path == None and name == 'data':
       path = os.path.expanduser('~/.cache/data')

    return path + os.sep #realpath(path) 
    

def file_ext(filename):
    if not '.' in filename:
        return ''
    ext = filename.rsplit('.', 1)[-1]
    return ext
    
def dirname(filename = None):
    if filename == None:
       filename == __file__
    return os.path.dirname(filename)
    
def invalid_path(path):
    if '.git' in path or '/_' in path or '.dist-info' in path:
         return True
    return False
    
def get_filedb():
    from DB import FileDB
    return FileDB()
    
def add_sys_path(arg):
    if type(arg) == str:
        lst = (arg)
    else:
        lst = arg
    for p in lst:    
        p = realpath(p)
        if not p in sys.path:
           sys.path.append(p)
     
def get_dirs(path=None):   
    path = realpath(path)
    lst = []   
    cwd = os.getcwd()
    os.chdir(path)
    for root, dirs, files in os.walk('.', followlinks=False):   
        if invalid_path(root):
            continue 
        s = root[2:]
        if s != '':    
           lst.append(s)    
    os.chdir(cwd)                     
    return lst
    
    
def get_files(path=None, ext='.py'):   
    path = realpath(path)
    lst = []   
    sep = os.sep    
    for d in [''] + get_dirs(path):
        root = path + sep + d
        for fn in os.listdir(root):
            if not fn.endswith(ext):
                continue
            if fn[0] in ['.', '_']:
                continue           
            lst.append(d + sep + fn)  
    return lst
    
def search_file(path, name):   
    lst = []   
    for p1 in get_files(path):         
        if name in p1:
           fn = path + os.sep + p1
           lst.append(fn)             
    return lst

def search_file_list(lst, name):
    files = []
    for p in lst:
        files += search_file(p, name)
    return files     
        
def search_package_files(name):
    p1 = sys.path[-1]
    p2 = '/usr/lib/python3'
    lst = search_file_list([p1, p2], name)
    return lst    
    
def find_in_text(path, text, key):
    if not key in text:
        return []
    i = -1     
    n = len(key)   
    lst1 = []
    for line in text.splitlines():
        i += 1           
        j = line.find(key)
        if j == -1:
            continue
        j1 = j + n
        lst1.append((i, j, line))
        #head = path + ': %4d '%(i+1) + line[0:j]
        #print(key, tag='bold', head=head, end=line[j1:] + '\n') 
    return lst1  
    
def db_search_key(key):
    fdb = get_filedb()
    res = fdb.find_text(key)
    plst = []
    for path in res:        
        text = fread(path)
        lst = find_in_text(path, text, key)
        plst.append((path, lst))
    return plst
    
def walkdir(path='.', ext='.py'):   
    if '~' in path:
        path = os.path.expanduser(path)    
    path = os.path.realpath(path) 
    plst = []
    lst = []
    index = 0
    for root, dirs, files in os.walk(path, topdown=False):
        if '.git' in root or '/_' in root or '.dist-info' in root:
            continue 
        if not root in plst:
            plst.append(root)
            index = plst.index(root)
        if plst[index] != root:
            index = plst.index(root)
                
        for name in files:
            if name.endswith('.py'):
               lst.append((index, name))
        #for name in dirs:
        #    print(os.path.join(root, name))
    return plst, lst
    


def listdir(path, ext='.'):
    lst = []
    path = realpath(path)
    for fn in os.listdir(path):
        if ext in fn:
           lst.append(fn)
    return lst


    
def flatten(lst):
    return list(np.array(lst).flatten())
    
def flatstr(lst):
    lst = list(np.array(lst).flatten())
    return ','.join(lst)
    
def read_url(url, rawdata=False, method='get', fields={}):    
    #print('read_url', url, method)
    http = urllib3.PoolManager()        
    if method == 'get':
       response = http.request('GET', url)
    else:
       response = http.request('POST', url, fields=fields) 
    status = response.status
    readable = response.readable()
    if status != 200 or readable == False:
        print(url, 'status=', status, 'readable=', readable)
        return 'error', ''       
    content_type = response.info().get('Content-Type')
    #print(content_type)
    data_type = content_type.split('/', 1)[0]   
    #print(data_type, response.isclosed()) 
    if data_type == 'text':
        f = io.BytesIO(response.data)
        text = f.read().decode('utf-8')
        return data_type, text
    else:
        return data_type, response.data
    
def get_cdb(): 
    return DB.open('cache')
    

class Inspect:
    def reFindDir(obj, key):        
        s = str(dir(obj))
        return re.findall(rf'{key}[\w\_]*', s)
        
    def findTK(obj):
        return Inspect.reFindDir(obj, 'TK')
        
def findTK(obj):
    return Inspect.reFindDir(obj, 'TK')
    
def init_db_file():
    db = get_filedb()
    key = 'lastgroup'
    res = db.find_text(key)
    for path in res:
        print(path)
        text = fread(path)
        lst = find_in_text(path, text, key)
        for s in lst:
            print(s)
                
if __name__ == '__main__':      
    #print(search_file_list(['~/src'], 'tmp'))
    #print(search_package_files('end'))

    #for v in ['prefix', 'platform', 'version', '_home', 'exec_prefix', 'base_prefix', 'path']:
    #    s = v+ ':         '
    #    print(s[:16], venv.sys.__getattribute__(v))
 
    #print(pdct, pdct == {})
    print(get_path('data'))
    

