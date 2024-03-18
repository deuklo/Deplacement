#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 11:05:41 2024

@author: gauthierrey
"""
import json
import numpy as np

# Lire les données depuis le fichier JSON
with open('Profil_position.json', 'r') as fichier_json:
    Z_opt_json = json.load(fichier_json)

# Convertir la liste en array NumPy
Z_opt = np.array(Z_opt_json)

# Maintenant, Z_opt est un array NumPy que vous pouvez utiliser ailleurs dans votre code.
