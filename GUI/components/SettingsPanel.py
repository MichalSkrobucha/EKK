from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
                             QFormLayout, QLineEdit, QSpinBox, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal
from QKD_Algorithms.Common.config import cfg


class SettingsPanel(QWidget):
    sig_setting_changed = pyqtSignal(str, object)

    def __init__(self, protocol_name, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(15)

        # Budowanie sekcji wspólnych (Sim)
        if self.protocol_name != "MAC":
            self.add_sim_section()

        # Różne ustawienia dla różnych protokołów
        if self.protocol_name in ["BB84", "SARG04"]:
            self.add_channel_section()
            self.common_section()

            self.add_bb84_sarg_controls()

        elif self.protocol_name == "E91":
            self.add_e91_controls()

        elif self.protocol_name == "MAC":
            self.add_mac_controls()

        self.layout.addStretch()

    def create_group(self, title):
        group = QGroupBox(title)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setContentsMargins(10, 10, 10, 10)
        group.setLayout(form)
        self.layout.addWidget(group)
        return form

    # SEKCJE WSPÓLNE
    def add_sim_section(self):
        self.sim_form = self.create_group("⚙️ Simulation Settings")

        # QBER Threshold
        self.spin_qber = QDoubleSpinBox()
        self.spin_qber.setRange(0, 100)
        self.spin_qber.setValue(cfg.sim.qber_threshold)
        self.spin_qber.setSuffix(" %")
        self.sim_form.addRow("QBER Threshold:", self.spin_qber)
        self.spin_qber.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("qber_threshold", val)
        )

        # Sim End (liczba bitów klucza)
        self.spin_key_length = QSpinBox()
        self.spin_key_length.setRange(10, 100000)
        self.spin_key_length.setSingleStep(128)
        self.spin_key_length.setValue(cfg.sim.key_length)
        self.spin_key_length.setSuffix(" bits")
        self.sim_form.addRow("Target Key Length:", self.spin_key_length)
        self.spin_key_length.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("key_length", val)
        )

    def common_section(self):
        self.spin_bob_eff = QDoubleSpinBox()
        self.spin_bob_eff.setRange(0, 100)
        self.spin_bob_eff.setValue(cfg.bb84.bob_efficiency)
        self.spin_bob_eff.setSingleStep(10)
        self.spin_bob_eff.setSuffix(" %")
        self.spin_bob_eff.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("bob_eff", val)
        )

        self.spin_bob_error = QDoubleSpinBox()
        self.spin_bob_error.setRange(0, 100)
        self.spin_bob_error.setValue(cfg.bb84.bob_error)
        self.spin_bob_error.setSingleStep(10)
        self.spin_bob_error.setSuffix(" %")
        self.spin_bob_error.setToolTip("Dark count probability / internal error")
        self.spin_bob_error.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("bob_error", val)
        )

    def add_channel_section(self):
        self.channel_form = self.create_group("🌐 Channel Properties")

        # Channel Length (km)
        self.spin_length = QDoubleSpinBox()
        self.spin_length.setRange(1, 200)
        self.spin_length.setValue(cfg.channel.length_km)
        self.spin_length.setSuffix(" km")
        self.channel_form.addRow("Length:", self.spin_length)
        self.spin_length.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("channel_length", val)
        )

        # Dampening (Tłumienie)
        self.spin_dampening = QDoubleSpinBox()
        self.spin_dampening.setRange(0, 10)
        self.spin_dampening.setSingleStep(0.1)
        self.spin_dampening.setValue(cfg.channel.dumpening_per_km)
        self.spin_dampening.setSuffix(" dB/km")
        self.channel_form.addRow("Dampening:", self.spin_dampening)
        self.spin_dampening.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("dampening", val)
        )

        # Base Transform (Rotacja polaryzacji / błąd kanału)
        self.spin_transform = QDoubleSpinBox()
        self.spin_transform.setRange(0, 360)
        self.spin_transform.setValue(cfg.channel.base_transform_per_km)
        self.spin_transform.setSingleStep(15)
        self.spin_transform.setSuffix(" °/km")
        self.channel_form.addRow("Base Transform:", self.spin_transform)
        self.spin_transform.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("base_transform", val)
        )

    # BB84 / SARG04
    def add_bb84_sarg_controls(self):
        # ALICE
        self.form_alice = self.create_group("👩 Alice (Sender)")

        self.spin_alice_mi = QDoubleSpinBox()
        self.spin_alice_mi.setRange(0.01, 5.0)
        self.spin_alice_mi.setValue(cfg.bb84.alice_mi)
        self.spin_alice_mi.setSingleStep(0.1)
        self.spin_alice_mi.setToolTip("Mean photon number per pulse (μ)")
        self.form_alice.addRow("Mean photons (μ):", self.spin_alice_mi)
        self.spin_alice_mi.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("alice_mi", val)
        )

        # BOB
        self.form_bob = self.create_group("👨 Bob (Receiver)")

        self.form_bob.addRow("Efficiency:", self.spin_bob_eff)
        self.form_bob.addRow("Internal Error:", self.spin_bob_error)

        # EVE
        self.form_eve = self.create_group("🕵️ Eve (Eavesdropper)")
        self.check_eve = QCheckBox("Enable")
        self.check_eve.setChecked(cfg.bb84.eve_present)
        self.check_eve.toggled.connect(
            lambda val: self.sig_setting_changed.emit("if_eve", val)
        )
        self.form_eve.addRow("Presence:", self.check_eve)

    # E91
    def add_e91_controls(self):
        # SOURCE
        # self.form_source = self.create_group("🌟 Entangled Source")
        #
        # self.spin_n_photons = QSpinBox()
        # self.spin_n_photons.setRange(1, 10)
        # self.spin_n_photons.setValue(cfg.e91.n_photons)
        # self.form_source.addRow("N Photons:", self.spin_n_photons)
        # self.spin_n_photons.valueChanged.connect(
        #     lambda val: self.sig_setting_changed.emit("n_photons", val)
        # )
        #
        # self.combo_dist = QComboBox()
        # self.combo_dist.addItems(["PDC (Parametric Down-Conversion)", "Ideal Bell State"])
        # self.form_source.addRow("Distribution:", self.combo_dist)
        # self.combo_dist.editTextChanged.connect(
        #     lambda val: self.sig_setting_changed.emit("distribution", val)
        # )

        # PARMS - P & S_THRESHOLD

        self.form_params = self.create_group("Parameters")
        self.p_spin = QDoubleSpinBox()
        self.p_spin.setRange(0.01, 1.00)
        self.p_spin.setValue(1.0)
        self.p_spin.setSingleStep(0.01)

        self.form_params.addRow("Probability of entanglement: ", self.p_spin)
        self.p_spin.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("p", val))

        self.s_spin = QDoubleSpinBox()
        self.s_spin.setRange(1.41, 2.82)
        self.s_spin.setValue(2.0)
        self.s_spin.setSingleStep(0.01)

        self.form_params.addRow("S Threshold: ", self.s_spin)
        self.s_spin.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("s_thresh", val))

        # ALICE
        self.form_alice = self.create_group("👩 Alice (Analyzer)")

        self.input_alice_bases = QLineEdit(", ".join(map(str, cfg.e91.alice_bases.values())))
        self.input_alice_bases.setPlaceholderText("e.g. 0, 22.5, 45")
        self.form_alice.addRow("Bases (Angles):", self.input_alice_bases)

        self.input_alice_bases.editingFinished.connect(
            lambda: self.sig_setting_changed.emit("alice_bases", self.input_alice_bases.text())
        )

        self.input_alice_bases.setEnabled(False)

        # BOB
        self.form_bob = self.create_group("👨 Bob (Analyzer)")

        # self.form_bob.addRow("Efficiency:", self.spin_bob_eff)
        # self.form_bob.addRow("Internal Error:", self.spin_bob_error)

        self.input_bob_bases = QLineEdit(", ".join(map(str, cfg.e91.bob_bases.values())))
        self.form_bob.addRow("Bases (Angles):", self.input_bob_bases)

        self.input_bob_bases.editingFinished.connect(
            lambda: self.sig_setting_changed.emit("bob_bases", self.input_bob_bases.text())
        )

        self.input_bob_bases.setEnabled(False)
        #
        # EVE
        self.form_eve = self.create_group("🕵️ Eve (Eavesdropper)")
        self.check_eve = QComboBox()
        self.check_eve.addItems(
            ["No Eve", "Eve measures after base exchange", "Eve measures before Alice",
             "Eve measures between Alice & Bob", "Eve measures after Bob"])
        self.check_eve.currentTextChanged.connect(
            lambda val: self.sig_setting_changed.emit("eve_mode", val)
        )
        self.form_eve.addRow("Eve Mode:", self.check_eve)

    def add_mac_controls(self):
        self.hash_params = self.create_group("Hash Parameters")
        self.m_exp = QDoubleSpinBox()
        self.m_exp.setRange(1, 8)
        self.m_exp.setValue(4)
        self.m_exp.setSingleStep(1)

        self.hash_params.addRow("Bits of message space: ", self.m_exp)
        self.m_exp.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("m_exp", val))

        self.t_exp = QDoubleSpinBox()
        self.t_exp.setRange(1, 8)
        self.t_exp.setValue(2)
        self.t_exp.setSingleStep(1)

        self.hash_params.addRow("Bits of tag space", self.t_exp)
        self.t_exp.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("t_exp", val))

        self.mteve_params = self.create_group("Eve parameters")
        self.given = QDoubleSpinBox()
        self.given.setRange(0, 100)
        self.given.setValue(4)
        self.given.setSingleStep(1)

        self.mteve_params.addRow("Exchanged messages: ", self.given)
        self.given.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("mts_given", val))

        self.to_forge = QDoubleSpinBox()
        self.to_forge.setRange(0, 100)
        self.to_forge.setValue(4)
        self.to_forge.setSingleStep(1)

        self.mteve_params.addRow("Tags to forge: ", self.to_forge)
        self.to_forge.valueChanged.connect(
            lambda val: self.sig_setting_changed.emit("to_forge", val))

    @staticmethod
    def on_bases_change(self, value, sim_variable):
        bases = {}
        for i, base in enumerate(value.split(',;')):
            bases[int(i)] = float(sim_variable)
        sim_variable = bases

    def set_inputs_enabled(self, enabled: bool):
        """Metoda pomocnicza do włączania/wyłączania elementów"""
        for group in self.findChildren(QGroupBox):
            group.setEnabled(enabled)

    def lock_settings(self):
        """Blokuje edycję"""
        self.set_inputs_enabled(False)

    def unlock_settings(self):
        """Odblokowuje edycję"""
        self.set_inputs_enabled(True)
