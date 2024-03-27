import json
import numpy as np 
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap
import sys

class ParametresWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration des paramètres")
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()

        # Layout pour les paramètres
        param_layout = QVBoxLayout()

        self.label_t1 = QLabel("T1 (Durée de la première pente en ns):")
        self.edit_t1 = QLineEdit()
        param_layout.addWidget(self.label_t1)
        param_layout.addWidget(self.edit_t1)

        self.label_t2 = QLabel("T2 (Durée de l'attente en ns):")
        self.edit_t2 = QLineEdit()
        param_layout.addWidget(self.label_t2)
        param_layout.addWidget(self.edit_t2)

        self.label_vmax = QLabel("Vmax (Vitesse maximale en m/s):")
        self.edit_vmax = QLineEdit()
        param_layout.addWidget(self.label_vmax)
        param_layout.addWidget(self.edit_vmax)

        self.button_sauvegarder = QPushButton("Sauvegarder")
        self.button_sauvegarder.clicked.connect(self.sauvegarder_parametres)
        param_layout.addWidget(self.button_sauvegarder)

        # Layout pour l'image
        image_layout = QVBoxLayout()
        pixmap = QPixmap("/Users/gauthierrey/Desktop/Capture d’écran 2024-03-27 à 16.08.08.png")  # Remplacez "chemin_vers_votre_image.jpg" par le chemin de votre image
        pixmap = pixmap.scaledToWidth(400) 
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_layout.addWidget(image_label)

        layout.addLayout(param_layout)
        layout.addLayout(image_layout)

        self.setLayout(layout)
        
    def sauvegarder_parametres(self):
        T1 = float(self.edit_t1.text())
        T2 = float(self.edit_t2.text())
        vmax = float(self.edit_vmax.text())
        
        f = 2.32E15 # Fréquence du laser en Hz

        AOM_1 = 110E6  # Pulsation du premier AOM en Hz
        AOM_1_0 = AOM_1
        AOM_2_0 = AOM_1_0
        c = 299792458 # Vitesse de la lumière

        V = vmax # Vitesse qu'on veut atteindre en m/s

        f_1 = f + 2*AOM_1 # Fréquence du Laser après passer dans le premier AOM
        f_2 = f_1 * ((c-V)/(c+V)) # Fréquence que doit avoir le second Laser

        AOM_2 = (f_2 - f)/2 # Fréquence que doit avoir le second AOM 

        print(AOM_2 / 1E6 )
        Delta_AOM = AOM_2 - AOM_1

        AOM_1 = AOM_1 - Delta_AOM/2
        AOM_2 = AOM_2 - Delta_AOM/2

        print(AOM_1 / 1E6, AOM_2/1E6, Delta_AOM/1E6)

        def sauvegarder_parametres(t1, t2, v_i1, v_f1, v_i2, v_f2):
            # Modèle de texte avec des placeholders pour t1, t2, v_i1, v_i2, v_f1, v_f2
            modele_texte = [
                '::<Spec. Reg. RF0> | trig. in BNC A ::',
                '::<Spec. Reg. RF1> | trig. in BNC A ::',
                '::<Dyn. Reg. RF0, type:freq> | v_i = {v_i1} Hz; v_f = {v_f1} Hz; t = {t1} ns; a = 1.0 dBm; o = 0.0 rad::',
                '::<Dyn. Reg. RF1, type:freq> | v_i = {v_i2} Hz; v_f = {v_f2} Hz; t = {t1} ns; a = 1.0 dBm; o = 0.0 rad::',
                '::<Spec. Reg. RF1> | wait {t2} ns::',
                '::<Spec. Reg. RF0> | wait {t2} ns::',
                '::<Dyn. Reg. RF0, type:freq> | v_i = {v_f1} Hz; v_f = {v_i1} Hz; t = {t2} ns; a = 1.0 dBm; o = 0.0 rad::',
                '::<Dyn. Reg. RF1, type:freq> | v_i = {v_f2} Hz; v_f = {v_i2} Hz; t = {t2} ns; a = 1.0 dBm; o = 0.0 rad::'
            ]

            # Mise à jour du modèle avec les valeurs fournies
            texte_mis_a_jour = [ligne.format(t1=t1, t2=t2, v_i1=v_i1, v_f1=v_f1, v_i2=v_i2, v_f2=v_f2) for ligne in modele_texte]
            
            # Enregistrement dans un fichier JSON
            chemin_fichier = '/Users/gauthierrey/Desktop/Deplacement/Fonctions_separes_profil/t.json'
            with open(chemin_fichier, 'w') as fichier:
                for ligne in texte_mis_a_jour:
                    json.dump([ligne], fichier)
                    fichier.write('\n')
            
            return chemin_fichier

        # Mise à jour du modèle avec les valeurs fournies
        chemin_fichier = sauvegarder_parametres(T1, T2, AOM_1_0, AOM_1, AOM_2_0, AOM_2)

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParametresWidget()
    window.show()
    sys.exit(app.exec_())
