import os
import zlib
from aui.ModuleDB import ModuleDB
from helpbox import HelpObj

mdb = ModuleDB()  

def get_module_members_list(modules):     
    lst = []
    for m in modules:
        obj = HelpObj(m)
        data = (obj.name, obj.module, obj.objtype, str(obj.members), '')
        lst.append(data)
    return lst    
        
def create_module_members_table():
    mdb = ModuleDB()
    db = mdb.get_db() 
    modules = eval(mdb.getvar('module.default'))
    
    keytypes = {'name':'string', 'module':'string', 'type':'string', 'members':'string', 'data':'string'} 
    lst = get_module_members_list(modules)
    db.from_list('modules', keytypes, lst)
    
def get_modules():
    mdb = ModuleDB()
    db = mdb.get_db()   
    res = db.fetchall('select name from modules')
    return flatten(res)
    
def update_module_members_table(modules):
    mdb = ModuleDB()
    db = mdb.get_db()   
    
    for m in modules:
        db.execute('DELETE FROM modules WHERE name = \"%s\";' % m)  
    db.commit()
    keytypes = {'name':'string', 'module':'string', 'type':'string', 'members':'string', 'data':'string'} 
    lst = get_module_members_list(modules)
    db.from_list('modules', keytypes, lst)

def check_data(modules):    
    db = mdb.get_db() 
    p = str(tuple(modules))
    res = db.fetchall('select * from modules where name in %s' % p)
    return res
    
def test():
    mdb = ModuleDB()
    name = 'tkinter'
    res = mdb.fetch('Select * from modules where name = \"%s\"' % name)
    data = res[0]
    name, module, objtype, members, data1 = data
    print(name)
    print(module)
    print(objtype)
    print(eval(members))
    
def save_all_doc():
    db = ModuleDB()
    path = '/home/athena/data/help/'
    for m in db.get_modules():
        filename = path + m + '.txt'
        if os.path.exists(filename):
            continue
        print(m)
        obj = HelpObj(m)
        text = obj.render_doc(title='\nPython Library Doc: \n    %s') 
        fwrite(filename, text)
                
def create_doc_table():
    mdb = ModuleDB()
    db = mdb.get_db() 
    modules = eval(mdb.getvar('module.default'))    
    keytypes = {'name':'string', 'doc':'string'} 
    lst = []
    for m in modules:
        obj = HelpObj(m)
        text = obj.render_doc(title='\nPython Library Doc: \n    %s')
        ztext = zlib.compress(text.encode())
        data = (obj.name, ztext)
        lst.append(data)
    #from_list(self, table, keytypes, lst):
    db.from_list('doc', keytypes, lst)
    
def test_doc():
    name = 'tkcode'
    mdb = ModuleDB()
    db = mdb.get_db() 
    res = mdb.fetch('Select doc from doc where name = \"%s\"' % name)
    if res == None or res == []:
        return False     
    data = res[0][0]
    text = zlib.decompress(data).decode()
    return text
    
if __name__ == '__main__':   
    text = test_doc()
    print(text)

