from random import randint


def try_hash(q, r):
    M = 16
    p = 17
    T = 4

    tag_ctr = {t: 0 for t in range(T)}

    for m in range(M):
        tag: int = ((m * q + r) % p) % T
        tag_ctr[tag] += 1

    # print(q, r, tag_ctr)

    for t in range(4):
        if tag_ctr[t] != 4:
            break
    else:
        print(q, r)


def main():
    for q in range(1, 16):
        for r in range(16):
            try_hash(q, r)


if __name__ == '__main__':
    main()
