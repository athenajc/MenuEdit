import tkinter as tk
from tkinter import *
from aui import Text

editor = None

# Convert an RGB tuple to a HEX string using the % Operator
# 02 means print 2 characters
# x means hexadecimal
def rgbToHex(rgb):
    return "#%02x%02x%02x" % rgb

def search_re(pattern, i, line, offset):
    matches = []
               
    for match in re.finditer(pattern, line):
        matches.append(
            (f"{i + 1}.{match.start()}", f"{i + 1}.{match.end() - offset}")
        )
    return matches            
    

def redraw(editor):
    display = editor.display  
    display['state'] = NORMAL

    # Clear the Display Area
    display.clear_all()

    # Insert the content of the Edit Area into the Display Area
    text = editor.get_text()

    # Save Raw Text for later
    textRaw = text

    # Remove Unwanted Characters
    text = ''.join(text.split('#'))
    text = ''.join(text.split('*'))

    display.insert(1.0, text)    
    
    for i, line in enumerate(textRaw.splitlines()):         
        m = re.search('^\s*(\#+)', line)
        if m: 
            n = len(m.group(1))
            start = line.find('#')
            display.tag_add(f'Header{n}', f"{i + 1}.{start}", f"{i + 1}.end")        
            continue  
        # Loop through each replacement, unpacking it fully
        for pattern, name, offset in editor.patterns:
            for m in re.finditer(pattern, line):
                display.tag_add(name, f"{i + 1}.{m.start()}", f"{i + 1}.{m.end() - offset}")   

    display['state'] = DISABLED
    

def changes(event=None):
    if event == None:
        return
    editor = event.widget      
    redraw(editor)
    

# Style Setup
editorBackground = rgbToHex((40, 40, 40))
editorTextColor = rgbToHex((230, 230, 230))
displayBackground = rgbToHex((60, 60, 60))
displayTextColor = rgbToHex((200, 200, 200))

caretColor = rgbToHex((255, 255, 255))

# Width of the Textareas in characters
width = 10

# Fonts
editorfontName = 'Courier'
displayFontName = 'Calibri'

# Font Sizes
normalSize = 15
h1Size = 40
h2Size = 30
h3Size = 20

# font Colors
h1Color = rgbToHex((240, 240, 240))
h2Color = rgbToHex((200, 200, 200))
h3Color = rgbToHex((160, 160, 160))


# Replacements tell us were to insert tags with the font and colors given
replacements = [
    [
        '^\s*#[a-zA-Z\s\d\?\!\.]+$',
        'Header1',
        f'{displayFontName} {h1Size}', 
        h1Color,
        0
    ], [
        '^\s*##[a-zA-Z\s\d\?\!\.]+$',
        'Header2', 
        f'{displayFontName} {h2Size}',
        h2Color,
        0
    ], [
        '^\s*###[a-zA-Z\s\d\?\!\.]+$', 
        'Header3', 
        f'{displayFontName} {h3Size}', 
        h3Color,
        0        
    ], [
        '\*.+?\*', 
        'Bold', 
        f'{displayFontName} {normalSize} bold', 
        displayTextColor,
        2
    ],
]

        
def add_editor(frame):    
    root = frame.winfo_toplevel()
    # Setting the Font globaly
    root.option_add('*Font', 'Courier 15')
    
    # Making the Editor Area
    editor = Text(frame.left, height=5, width=width)
    editor.config(bg=editorBackground,
        fg=editorTextColor,
        border=30,
        relief=FLAT,
        insertbackground=caretColor,
        font=('Courier', 15)
    )
    #editor.pack(expand=1, fill=BOTH)

    editor.bind('<KeyRelease>', changes)
    editor.focus_set()
    
    # Insert a starting text
    editor.insert(INSERT, """#Heading 1
    
    ##Heading 2
    
    ###Heading 3
    
    This is a *bold* move!
    
    
    - Markdown Editor -
    
    """)       
    
    # Making the Display Area
    display = Text(frame.right,  height=5,  width=width, )
    display.config(bg=displayBackground,
        fg=displayTextColor,
        border=30,
        relief=FLAT,
        font=f"{displayFontName} {normalSize}",)
    #display.pack(expand=1, fill=BOTH)
    lst = []
    for pattern, name, fontData, colorData, offset in replacements:
        print(name, fontData, colorData, offset)
        display.tag_config(name, font=fontData, foreground=colorData)  
        if not 'Header' in name:    
           lst.append((pattern, name, offset))
    editor.patterns = lst    
    # Disable the Display Area so the user cant write in it
    # We will have to toggle it so we can insert text
    display['state'] = DISABLED
    #root.markdown_editor = editor
    editor.display = display
    editor.redraw = redraw
    redraw(editor)
    return editor
    
if __name__ == '__main__':    
    from aui import App    
    app = App(title='Markdown Editor', size=(1500,860))
    frame = app.twoframe(app, 'h', 0.5)
    editor = add_editor(frame)       
    app.mainloop()

