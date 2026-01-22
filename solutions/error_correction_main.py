from error_correction_channel import channel

def main():
    c = channel()
    c.peek_keys()

    c.run_error_correction()
    c.run_privacy_amplification()


if __name__ == '__main__':
    main()
