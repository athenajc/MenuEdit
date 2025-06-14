import os
import zlib
from DB.ModuleDB import ModuleDB
from helpbox import HelpObj
import DB

mdb = ModuleDB()  
db = DB.open('modules')

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
    path = get_path('data') + '/help/'
    for m in db.get_modules():
        filename = path + m + '.txt'
        if os.path.exists(filename):
            continue
        print(m)
        obj = HelpObj(m)
        text = obj.render_doc(title='\nPython Library Doc: \n    %s') 
        fwrite(filename, text)
    
def get_default_modules_doc():
    lst = []
    modules = eval(db.get_cache('module.default'))    
    for m in modules:
        obj = HelpObj(m)
        text = obj.render_doc(title='\nPython Library Doc: \n    %s')
        ztext = zlib.compress(text.encode())
        data = (obj.name, ztext)
        lst.append(data)
    return lst    
                    
def create_doc_table():    
    #db.remove_table('doc')
    #db.create('doc')
    
    table = db.get_table('doc')
    lst = get_default_modules_doc()
    table.add_list(lst)
    
def test_doc(name = 'tkcode'): 
    res = db.getdata('doc', name)
    data = eval(res)
    if data in [None, []]:
        return ''
    text = zlib.decompress(data).decode()
    return text
    
if __name__ == '__main__':   
    #create_doc_table()
    print(test_doc())
    #db.show()

