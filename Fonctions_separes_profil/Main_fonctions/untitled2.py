import pyvisa as visa
from time import sleep
import struct
import numpy as np
import csv
import os

# Définir les paramètres directement dans le script
filename = "/Users/gauthierrey/Desktop/Deplacement/Fonctions_separes_profil/Main_fonctions/rampe.dat"  # Chemin vers le fichier contenant la forme d'onde arbitraire
address = "142.104.60.122"  # Adresse de l'appareil
pulse_height = "0.1"  # Hauteur d'impulsion de la forme d'onde arbitraire
macro = False  # Générer un macro pour charger cette forme d'onde
delimiter = " "  # Délimiteur dans le fichier de forme d'onde

# Conversion du délimiteur si nécessaire
if delimiter == "tab":
    delimiter = "\t"

# Traitement du nom du fichier
name = os.path.splitext(os.path.basename(filename))[0]
if len(name) > 12:
    name = name[:12]
    print("Arb name truncated to " + name)

# Charger la forme d'onde arbitraire
samplePeriod = 0
num = 0
tlast = -1
arb = []
with open(filename, 'r') as f:
    reader = csv.reader(f, delimiter=delimiter)
    for t, p in reader:
        arb.append(float(p))
        if tlast != -1:
            samplePeriod += (float(t) - float(tlast))
            num += 1
        tlast = t

# Calculer le taux d'échantillonnage
samplePeriod /= num
sRate = str(1 / samplePeriod)

# Mise à l'échelle du signal entre -1 et 1
sig = np.asarray(arb, dtype='f4') / max(abs(arb))

# Connexion à l'appareil
rm = visa.ResourceManager('@py')
inst = rm.open_resource(f"TCPIP::{address}::INSTR")

# Envoi des commandes à l'appareil
inst.write("DISP:TEXT 'Uploading\nArbitrary\nWaveform'")
inst.write("MMEMORY:MDIR \"INT:\\remoteAdded\"")
inst.write('FORM:BORD SWAP')
inst.write('SOUR1:DATA:VOL:CLE')
inst.write_binary_values('SOUR1:DATA:ARB ' + name + ',', sig, datatype='f', is_big_endian=False)
inst.write('*WAI')
inst.write('SOUR1:FUNC:ARB ' + name)
inst.write('SOUR1:FUNC:ARB:SRAT ' + sRate)
inst.write('SOUR1:VOLT:OFFS 0')
inst.write('SOUR1:FUNC ARB')
inst.write(f'SOUR1:VOLT {pulse_height}')
inst.write(f'MMEM:STOR:DATA "INT:\\remoteAdded\\{name}.arb"')
inst.write("DISP:TEXT ''")

# Vérification des erreurs
instrument_err = "error"
while instrument_err != '+0,"No error"\n':
    inst.write('SYST:ERR?')
    instrument_err = inst.read()
    if not instrument_err.startswith("+0"):
        print(instrument_err)

# Fermeture de la connexion à l'appareil
inst.close()

# Génération d'un macro, si demandé
if macro:
    macroFile = "load_" + name + ".awg"
    with open(macroFile, 'w') as f:
        f.write("# Macro generated for loading the arb waveform\n")
        f.write(f"MMEMORY:LOAD:DATA1 \"INT:\\remoteAdded\\{name}.arb\"\n")
        f.write("SOURCE1:FUNCTION ARB\n")
        f.write(f"SOURCE1:FUNCtion:ARBitrary \"INT:\\remoteAdded\\{name}.arb\"\n")
    