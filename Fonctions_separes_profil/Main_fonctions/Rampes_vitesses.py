# Ce programme sort les fréquences qu'on doit mettre aux aoms pour faire la courbe montée, stable puis descente en donnant la vitesse max et les différents temps.

import json
import numpy as np 

f = 2.32E15 # Fréquence du laser en Hz

AOM_1 = 110E6  # Pulsation du premier AOM en Hz
AOM_1_0 = AOM_1
AOM_2_0 = AOM_1_0
c = 299792458 # Vitesse de la lumière

V = 1 # Vitesse qu'on veut atteindre en m/s

f_1 = f + 2*AOM_1 # Fréquence du Laser après passer dans le premier AOM
f_2 = f_1 * ((c-V)/(c+V)) # Fréquence que doit avoir le second Laser

AOM_2 = (f_2 - f)/2 # Fréquence que doit avoir le second AOM 

print(AOM_2 / 1E6 )
Delta_AOM = AOM_2 - AOM_1

AOM_1 = AOM_1 - Delta_AOM/2
AOM_2 = AOM_2 - Delta_AOM/2

print(AOM_1 / 1E6, AOM_2/1E6, Delta_AOM/1E6)



#%%
import json

T1 = 4000 # Durée de la première pente en ns
T2 = 5000 # Durée de l'attente en ns 

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

# Exemple d'utilisation de la fonction
# Remplacer les valeurs de t1, t2, v_i1, v_f1, v_i2, v_f2 avec les vôtres
chemin_fichier = sauvegarder_parametres(T1, T2, AOM_1_0, AOM_1, AOM_2_0, AOM_2)
print(f"Les paramètres ont été sauvegardés dans le fichier : {chemin_fichier}")
