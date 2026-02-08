from Common.SimManager import SimManager
from .ChannelMAC import ChannelMAC as channel
from .AnalysisMAC import AnalysisMAC as analysis

class SimManagerMAC(SimManager):
    pass

# E91

#     def simLoop(self):
#         """
#         Simulates QKD (du-uh)
#         """
#         self._initial_print()
#         self.is_running = True
#         while self.is_running:
#             self.sim_next_step()
#         self.is_running = False

def main():
    # channel().run()
    a = analysis()
    a.getPossibleHashesCount(8, 8)


if __name__ == '__main__':
    main()
