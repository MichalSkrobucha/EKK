class StatisticsManager:
    def __init__(self):
        pass

    def calculate_statistics(self, sim_manager, protocol_name, current_step):
        """
        Pobiera stan symulacji i zwraca słownik z gotowymi metrykami.
        Obliczenia są ograniczone do 'current_step', aby nie pokazywać danych z przyszłości.
        """
        limit = current_step + 1 if current_step >= 0 else 0

        sim_end = getattr(sim_manager, 'sim_end', 0)
        if sim_end == 0:
            sim_end = getattr(sim_manager, 'n_photons', 10)

        if current_step >= sim_end:
            data_limit = sim_end
        else:
            data_limit = limit

        stats = {
            "stage": self._determine_stage(sim_manager, protocol_name, current_step, sim_end),
            "total_photons": 0,
            "raw_key_len": 0,
            "error_count": 0,
            "final_key_len": 0
        }

        # TOTAL PHOTONS
        if protocol_name == "E91":
            if hasattr(sim_manager, 'source') and hasattr(sim_manager.source, 'message'):
                available = len(sim_manager.source.message)
                stats["total_photons"] = min(available, data_limit)
        else:
            if hasattr(sim_manager, 'alice') and hasattr(sim_manager.alice, 'message'):
                available = len(sim_manager.alice.message)
                stats["total_photons"] = min(available, data_limit)

        # RAW KEY & ERROR COUNT
        alice = sim_manager.alice
        bob = sim_manager.bob

        if protocol_name == "E91":
            a_bits = [entry['bit'] for entry in alice.results]
            b_bits = [entry['bit'] for entry in bob.results]
        else:
            a_bits = getattr(alice, 'bits', [])
            b_bits = getattr(bob, 'bits', [])

        if protocol_name == "SARG04":
            a_bases = getattr(alice, 'sendBases', [])
            b_bases = getattr(bob, 'bases', [])
        elif protocol_name == "E91":
            a_bases = [entry['base'] for entry in alice.results]
            b_bases = [entry['base'] for entry in bob.results]
        else:
            a_bases = getattr(alice, 'bases', [])
            b_bases = getattr(bob, 'bases', [])

        calc_range = min(len(a_bases), len(b_bases), len(a_bits), len(b_bits), data_limit)

        raw_len = 0
        errors = 0

        for i in range(calc_range):
            if str(a_bases[i]) == str(b_bases[i]):
                raw_len += 1
                if a_bits[i] != b_bits[i]:
                    errors += 1

        stats["raw_key_len"] = raw_len
        stats["error_count"] = errors

        if hasattr(bob, 'keyBits') and bob.keyBits:
            stage_str = stats["stage"]
            if "Privacy" in stage_str or "Finished" in stage_str:
                stats["final_key_len"] = len(bob.keyBits)

        return stats

    def _determine_stage(self, sim_manager, protocol, step, sim_end):
        """
        Określa nazwę etapu.
        """
        if step < 0:
            return "Idle / Ready"

        # Faza Transmisji: indeksy od 0 do sim_end - 1
        if step < sim_end:
            return f"Transmission ({step + 1}/{sim_end})"

        # Fazy Post-Processingu: indeksy od sim_end w górę
        post_step = step - sim_end

        if protocol == "BB84":
            if post_step == 0: return "Basis Exchange"
            if post_step == 1: return "Sifting"
            if post_step == 2: return "Sampling"
            if post_step == 3: return "Error Correction"
            if post_step == 4: return "Privacy Amplification"
            return "Finished"

        elif protocol == "SARG04":
            if post_step == 0: return "Announcing States"
            if post_step == 1: return "Sifting States"
            if post_step == 2: return "Sampling"
            if post_step == 3: return "Error Correction"
            if post_step == 4: return "Privacy Amplification"
            return "Finished"

        elif protocol == "E91":
            if post_step == 0: return "Basis Matching"
            if post_step == 1: return "CHSH Analysis"
            if post_step == 2: return "Error Correction"
            if post_step == 3: return "Privacy Amplification"
            return "Finished"

        return "Processing..."
