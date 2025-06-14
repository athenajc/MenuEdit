import os, sys
p = os.path.dirname(os.path.realpath(__file__))
if not p in sys.path:
   sys.path.append(p)


from .helpframe import *
from .helpbox import *
