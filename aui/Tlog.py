import time


class Tlog(object):
    def __init__(self):
        self.t0 = time.time()
        self.logs = []        
        
    def log(self, tag=''):
        t1 = time.time()
        offset = round((t1-self.t0)* 1000, 3)
        if tag == '':
            tag = str(len(self.logs)+1)
        self.logs.append((tag, offset))
        self.t0 = time.time()
        
    def puts(self, s=''):
        self.log(s)
        for tag, offset in self.logs:
            print(tag + ':' , offset)

























