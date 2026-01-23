import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# from .Analysis import *
from QKD_Algorithms_OLD.Logger import SimLogger
from BB84.SimManagerBB84 import SimManagerBB84
from BB84 import main as bb84_main

# from SARG import main as sarg_main

if __name__ == "__main__":
    print("Uruchamiam symulację BB84...")
    bb84_main.run_simulation()
