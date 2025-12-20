from Source import Source
from Photon import Photon


def test():
    s = Source(3, [(1.0, [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5])])

    ph1, ph2, ph3 = s.generate()

    ph1.measure(-1)
    ph2.measure(-1)
    ph3.measure(-1)

    b1 = ph1.bit
    b2 = ph2.bit
    b3 = ph3.bit

    print(b1, b2, b3, b1 == b2 == b3)

    return b1


def main():
    for _ in range(1_000):
        test()


if __name__ == '__main__':
    main()
