import serial

def set_frequency(ser, frequency_hz):
    """
    Envoie une commande au DDS pour régler la fréquence de sortie.
    :param ser: L'objet Serial connecté au FlexDDS-NG.
    :param frequency_hz: La fréquence souhaitée en Hz.
    """
    # Conversion de la fréquence en Hz en mot de réglage de fréquence (FTW)
    ftw = frequency_hz_to_ftw(frequency_hz)
    # Envoi de la commande pour configurer la fréquence
    # Remplacer 'SPI_WRITE_ADDRESS' et 'FTW_REGISTER' par les valeurs réelles
    command = f"dcp spi:FTW={ftw}\r\n"
    ser.write(command.encode())

def frequency_hz_to_ftw(frequency_hz):
    """
    Convertit une fréquence en Hz en un mot de réglage de fréquence (FTW) pour le DDS.
    :param frequency_hz: La fréquence souhaitée en Hz.
    :return: Le FTW correspondant.
    """
    # Cette fonction doit être adaptée selon les spécifications du DDS
    # Ici, c'est juste un placeholder pour illustrer le processus
    return int((frequency_hz / 30e6) * 2**32)

# Configuration initiale de la communication série
serial_port = '/dev/ttyUSB0'  # Adapter selon le système
baud_rate = 9600  # La vitesse de bauds peut varier selon le dispositif

# Création de l'objet Serial
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# Réglage de la fréquence à 30 MHz
set_frequency(ser, 30e6)

# Fermeture de la communication série
ser.close()
