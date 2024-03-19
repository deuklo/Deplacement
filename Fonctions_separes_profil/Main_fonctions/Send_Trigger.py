import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import pyvisa
import time

class PulseGeneratorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Créer une layout vertical
        layout = QVBoxLayout()
        
        
        # Ajouter un label et un champ d'entrée pour la durée du pulse
        self.durationLabel = QLabel('Durée du Pulse (ms):')
        self.durationInput = QLineEdit()
        layout.addWidget(self.durationLabel)
        layout.addWidget(self.durationInput)
        
        # Ajouter un label et un champ d'entrée pour la tension
        self.voltageLabel = QLabel('Tension (V):')
        self.voltageInput = QLineEdit()
        layout.addWidget(self.voltageLabel)
        layout.addWidget(self.voltageInput)
        
        # Ajouter un bouton pour envoyer les valeurs
        self.sendButton = QPushButton('Envoyer')
        self.sendButton.clicked.connect(self.sendPulse)
        layout.addWidget(self.sendButton)
        
        # Configurer la layout de la fenêtre
        self.setLayout(layout)
        self.setWindowTitle('Générateur de Pulse')
        
        
    def sendPulse(self):
        # Récupérer la durée et la tension des champs d'entrée
        duration_ms = self.durationInput.text()
        voltage = self.voltageInput.text()
        
        # Convertir la durée en secondes pour la compatibilité avec certaines commandes d'instruments
        duration_s = float(duration_ms) / 1000
        
        # Initialiser le gestionnaire de ressources VISA
        rm = pyvisa.ResourceManager()
        
        # Remplacer par l'adresse VISA de votre GBF
        instrument_address = 'USB0::0x0957::0x4B07::MY59000570::0::INSTR'
        instrument = rm.open_resource(instrument_address)
        
        try:
            # Configurer le GBF pour un signal carré avec les paramètres spécifiés
            # Note : Ces commandes sont génériques et doivent être ajustées selon votre modèle de GBF.
            instrument.write(f'FUNC SQU')
            instrument.write(f'FREQ {1/duration_s}')
            instrument.write(f'VOLT:HIGH {voltage}')
            instrument.write(f'VOLT:LOW 0')
            instrument.write(f'OUTP 1')
            
            # Attendre la durée du pulse
            time.sleep(duration_s)
            
            # Éteindre la sortie
            instrument.write('OUTP 0')
            
            print(f"Pulse de {voltage}V pendant {duration_ms}ms envoyé.")
        except Exception as e:
            print(f"Erreur lors de l'envoi du pulse : {e}")
        finally:
            # Fermer la session VISA
            instrument.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PulseGeneratorGUI()
    ex.show()
    sys.exit(app.exec_())
