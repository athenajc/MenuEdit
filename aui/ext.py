import tkinter as tk
import networkx as nx

import matplotlib.pyplot as plt
from pprint import pprint
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pydot
matplotlib.use('TkAgg')

def show(G=None, **kw):    
    if G != None:
        nx.draw(G, **kw)
    plt.show()

def draw_canvas(canvas, G=None, **kw):
    plt.clf()
    if G != None:
        nx.draw(G, **kw)
    ax = plt.gca()
    figure_canvas_agg = FigureCanvasTkAgg(ax.figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg
    
def from_dot(data):
    dot = pydot.graph_from_dot_data(data)        
    g = dot[0]
    G = nx.nx_pydot.from_pydot(g)
    G.dot = g
    return G

def App(title='App', size=(800, 600), icon=None):
    from aui import tkApp, aFrame
    root = tkApp(title, size, icon)
    frame = root.add(aFrame)
    return frame
    