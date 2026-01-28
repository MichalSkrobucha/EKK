from auth_channel import channel
from auth_analysis import analysis


def main():
    # channel().run()
    a = analysis()
    a.run_analysis()


if __name__ == '__main__':
    main()
