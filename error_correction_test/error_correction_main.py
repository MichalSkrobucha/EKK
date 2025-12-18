from error_correction_channel import channel


def main():
    c = channel()
    c.peek_keys()
    c.run()

    # c.alice.privacy_amplification()
    # c.bob.privacy_amplification()


if __name__ == '__main__':
    main()
