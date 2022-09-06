import sys
import os
import tkinter as tk
import subprocess

class RunFile():
    def read_output(self):        
        sys.stdout.flush()
        self.process.stdout.flush()
        s = self.process.stdout.read()
        print(s)
            
    def start_process(self, cmd):
        self.process_running = True      
        self.process = subprocess.Popen(cmd, universal_newlines=True,          
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        self.read_output()       
        self.on_stop_process()
        
    def on_stop_process(self):      
        self.process_running = False      
        os.chdir(self.curdir)
            
    def run(self, fn):
        if fn == '':
            return
        self.curdir = os.curdir
        path = os.path.dirname(fn)
        os.chdir(path)
        self.start_process(['/usr/bin/python3', fn]) 

if __name__ == '__main__':   
    test = RunFile()
    test.run('/home/athena/src/py/game/PlantsVsZombies/main.py')
