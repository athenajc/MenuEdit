import os
import sys

def realpath(fn):
    return os.path.realpath(os.path.expanduser(fn))
    
def fread(filename, path = None):
    if path != None:
        filename = path + os.sep + filename
    else:
        filename = realpath(filename)      
    if not os.path.exists(filename):
        return None
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
    
#get_cache('aui.colors') 

def get_cache(item):
    try:
        text = fread(item, os.path.expanduser('~/.cache/data'))
        return text
    except Exception as e:
        print(e)
        return None
    
def set_cache(item, text):
    fwrite(item, str(text), os.path.expanduser('~/.cache/data'))  
    
if __name__ == '__main__':
    print(get_cache('aui.colors'))    
