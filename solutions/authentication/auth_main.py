from auth_channel import channel
from auth_analysis import analysis


def main():
    # channel().run()
    a = analysis()
    a.getPossibleHashesCount(8, 8)


if __name__ == '__main__':
    main()
