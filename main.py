from SimManager import SimManager

def main() -> None:
    simManager = SimManager()
    # # Bez Ewy
    # simManager.ifEve = False
    # simManager.simLoop()

    # Z Ewą
    simManager.ifEve = True
    simManager.simLoop()

if __name__ == '__main__':
    main()
