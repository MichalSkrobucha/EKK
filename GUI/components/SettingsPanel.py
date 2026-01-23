from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
                             QFormLayout, QLineEdit)
from PyQt6.QtCore import Qt
from QKD_Algorithms_OLD.Logger import SimLogger

logger = SimLogger()


class SettingsPanel(QWidget):
    def __init__(self, protocol_name, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(15)

        # Budowanie sekcji wspólnych (Sim, Channel)
        self.add_sim_section()
        self.add_channel_section()

        # Różne ustawienia dla różnych protokołów
        if self.protocol_name in ["BB84", "SARG04"]:
            self.add_bb84_sarg_controls()
        elif self.protocol_name == "E91":
            self.add_e91_controls()

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

        # QBER Threshold (0.0 - 1.0 lub %)
        self.spin_qber = QDoubleSpinBox()
        self.spin_qber.setRange(0, 100)
        self.spin_qber.setValue(11.0)
        self.spin_qber.setSuffix(" %")
        self.sim_form.addRow("QBER Threshold:", self.spin_qber)
        self.spin_qber.valueChanged.connect(self.on_value_change)

        # Sim End (np. liczba bitów klucza)
        self.spin_sim_end = QSpinBox()
        self.spin_sim_end.setRange(10, 100000)
        self.spin_sim_end.setValue(1000)
        self.spin_sim_end.setSuffix(" bits")
        self.sim_form.addRow("Target Key Length:", self.spin_sim_end)
        self.spin_sim_end.valueChanged.connect(self.on_value_change)

    def add_channel_section(self):
        self.channel_form = self.create_group("🌐 Channel Properties")

        # Channel Length (km)
        self.spin_length = QDoubleSpinBox()
        self.spin_length.setRange(1, 200)
        self.spin_length.setValue(20)
        self.spin_length.setSuffix(" km")
        self.channel_form.addRow("Length:", self.spin_length)
        self.spin_length.valueChanged.connect(self.on_value_change)

        # Dampening (Tłumienie)
        self.spin_dampening = QDoubleSpinBox()
        self.spin_dampening.setRange(0, 10)
        self.spin_dampening.setValue(0.2)
        self.spin_dampening.setSuffix(" dB/km")
        self.channel_form.addRow("Attenuation:", self.spin_dampening)
        self.spin_dampening.valueChanged.connect(self.on_value_change)

        # Base Transform (Rotacja polaryzacji / błąd kanału)
        self.spin_transform = QDoubleSpinBox()
        self.spin_transform.setRange(0, 360)
        self.spin_transform.setValue(0)
        self.spin_transform.setSuffix(" °/km")
        self.channel_form.addRow("Polarization Rot.:", self.spin_transform)
        self.spin_transform.valueChanged.connect(self.on_value_change)

    # BB84 / SARG04
    def add_bb84_sarg_controls(self):
        # ALICE
        self.form_alice = self.create_group("👩 Alice (Sender)")

        self.spin_alice_mi = QDoubleSpinBox()
        self.spin_alice_mi.setRange(0.01, 5.0)
        self.spin_alice_mi.setValue(0.1)
        self.spin_alice_mi.setSingleStep(0.1)
        self.spin_alice_mi.setToolTip("Mean photon number per pulse (μ)")
        self.form_alice.addRow("Mean photons (μ):", self.spin_alice_mi)
        self.spin_alice_mi.valueChanged.connect(self.on_value_change)

        # BOB
        self.form_bob = self.create_group("👨 Bob (Receiver)")

        self.spin_bob_eff = QDoubleSpinBox()
        self.spin_bob_eff.setRange(0, 100)
        self.spin_bob_eff.setValue(90)
        self.spin_bob_eff.setSuffix(" %")
        self.form_bob.addRow("Efficiency:", self.spin_bob_eff)
        self.spin_bob_eff.valueChanged.connect(self.on_value_change)

        self.spin_bob_error = QDoubleSpinBox()
        self.spin_bob_error.setRange(0, 100)
        self.spin_bob_error.setValue(10)
        self.spin_bob_error.setSuffix(" %")
        self.spin_bob_error.setToolTip("Dark count probability / internal error")
        self.form_bob.addRow("Internal Error:", self.spin_bob_error)
        self.spin_bob_error.valueChanged.connect(self.on_value_change)

        # EVE
        self.form_eve = self.create_group("🕵️ Eve (Eavesdropper)")
        self.check_eve = QCheckBox("Enable")

        self.form_eve.addRow("Presence:", self.check_eve)

    # E91
    def add_e91_controls(self):
        # SOURCE
        self.form_source = self.create_group("🌟 Entangled Source")

        self.spin_n_photons = QSpinBox()
        self.spin_n_photons.setRange(1, 10000)
        self.spin_n_photons.setValue(1000)
        self.form_source.addRow("N Photons:", self.spin_n_photons)
        self.spin_n_photons.valueChanged.connect(self.on_value_change)

        self.combo_dist = QComboBox()
        self.combo_dist.addItems(["PDC (Parametric Down-Conversion)", "Ideal Bell State"])
        self.form_source.addRow("Distribution:", self.combo_dist)
        self.combo_dist.editTextChanged.connect(self.on_value_change)

        # ALICE
        self.form_alice = self.create_group("👩 Alice (Analyzer)")

        self.input_alice_bases = QLineEdit("0, 22.5, 45")
        self.input_alice_bases.setPlaceholderText("e.g. 0, 22.5, 45")
        self.form_alice.addRow("Bases (Angles):", self.input_alice_bases)
        self.input_alice_bases.editingFinished.connect(self.on_value_change)

        # BOB
        self.form_bob = self.create_group("👨 Bob (Analyzer)")

        self.spin_bob_eff_e91 = QDoubleSpinBox()
        self.spin_bob_eff_e91.setRange(0, 100)
        self.spin_bob_eff_e91.setValue(90)
        self.spin_bob_eff_e91.setSuffix(" %")
        self.form_bob.addRow("Efficiency:", self.spin_bob_eff_e91)
        self.spin_bob_eff_e91.valueChanged.connect(self.on_value_change)

        self.spin_bob_error_e91 = QDoubleSpinBox()
        self.spin_bob_error_e91.setValue(10)
        self.spin_bob_error_e91.setSuffix(" %")
        self.form_bob.addRow("Internal Error:", self.spin_bob_error_e91)
        self.spin_bob_error_e91.valueChanged.connect(self.on_value_change)

        self.input_bob_bases = QLineEdit("22.5, 45, 67.5")
        self.form_bob.addRow("Bases (Angles):", self.input_bob_bases)
        self.input_bob_bases.editingFinished.connect(self.on_value_change)
        #
        # EVE TODO?

    @staticmethod
    def on_value_change(value, sim_variable):
        if value != sim_variable:
            logger.log(f"Changed value {sim_variable} -> {value}")
            sim_variable = value

    @staticmethod
    def on_bases_change(self, value, sim_variable):
        bases = {}
        for i, base in enumerate(value.split(',;')):
            bases[int(i)] = float(sim_variable)
        logger.log(f"Changed value {sim_variable} -> {bases}")
        sim_variable = bases

    # def lock_settings(self):
    #     widgets_list = self.layout.findChildren(QWidget)
    #     for widget in widgets_list:
    #         widget.setEnabled(False)
    #
    # def unlock_settings(self):
    #     pass


