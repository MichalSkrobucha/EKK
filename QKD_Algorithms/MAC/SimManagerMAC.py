from MAC.ChannelMAC import ChannelMAC as channel


class SimManagerMAC():
    m_exp = 4
    t_exp = 2
    given_mts = 2
    eve_forgeries = 2

    def __init__(self):
        self.c = channel(self.m_exp, self.t_exp, given_mts=self.given_mts, eve_forgeries=self.eve_forgeries)

    def run_sim(self):
        self.c.run()


def main():
    s = SimManagerMAC()
    s.run_sim()


if __name__ == '__main__':
    main()
