import os
import sys

def get_file_path(filename = None):
    if filename == None:
       filename == __file__
    return os.path.realpath(filename).rsplit(os.sep, 1)[0]

def get_file_list(path, ext='.'):
    lst = []
    for fn in os.listdir(path):
        if ext in fn:
           lst.append(fn)
    return lst

def fread(filename):
    filename = os.path.realpath(filename)      
    if os.path.exists(filename) == False:
        return ''
    text = ''
    with open(filename, 'r') as f:
        text = f.read()
        f.close()
    return text

def fwrite(filename, text):
    filename = os.path.realpath(filename)      
    with open(filename, 'w') as f:
        f.write(text)
        f.close()
        return True
    return False