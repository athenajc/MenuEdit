
from aui import App           

#----------------------------------------------------------------------------------------------   
if __name__ == '__main__':  
    app = App(title='APP', size=(1500,860))
    app.add_set1()
    app.textbox.open(__file__)
    app.filetree.set_path('.')
    app.msg.puts('find test')
    app.mainloop()



