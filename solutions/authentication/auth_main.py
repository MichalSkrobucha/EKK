from auth_hash import hash
from auth_channel import channel

from random import choice


def find_eq_prob_hashes(M: int, T: int) -> list[tuple[int, int]]:
    p = hash.next_prime(M)

    hashes: list[tuple[tuple[int, int], int]] = []
    eq_prob: int = M // T

    for q in range(1, p):
        for r in range(p):
            h: hash = hash(M, T, q, r)

            tag_ctr: dict[int, int] = {i: 0 for i in range(T)}
            diff: int = 0

            for m in range(M):
                tag_ctr[h(m)] += 1

            for v in tag_ctr.values():
                diff += abs(v - eq_prob)

            hashes.append(((q, r), diff))

    min_diff: int = min(hashes, key=lambda h: h[1])[1]

    eq_prob_hashes: list[tuple[int, int]] = [(q, r) for ((q, r), d) in hashes if d <= min_diff + 2 * T]

    return eq_prob_hashes


def main():
    M: int = 2 ** 8
    T: int = 2 ** 4

    hashes: list[tuple[int, int]] = find_eq_prob_hashes(M, T)
    qr: tuple[int, int] = choice(hashes)

    c: channel = channel(M, T, hashes, qr, 2)
    c.run()


if __name__ == '__main__':
    main()
