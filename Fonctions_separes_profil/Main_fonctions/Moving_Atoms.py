
from qutip import *
import numpy as np
from scipy import *
from scipy import signal
import time
from time import sleep
import json


# Plot 
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.cbook as cbook
from matplotlib.path import Path
from matplotlib.patches import PathPatch


# Optotune 
from optoKummenberg import UnitType
from optoICC import connect, DeviceModel# , WaveformType #Pas sûr de ce package, je crois qu'il n'existe pas 
import optoICC

# Keysight generator 
import pyvisa as visa
import struct
import csv
import os

#### Parameters 


parameters_path = "/Users/gauthierrey/Desktop/STAGE/Déplacement/Soft_atoms_displacement/Soft_atom_disp_E17/Fonctions_separes_profil/Parameters/parameters.json"
# Lecture du fichier JSON
with open(parameters_path, 'r') as f:
    params = json.load(f)

# Accès aux valeurs
lambda_laser = params["lambda_laser"]
trap_waist = params["trap_waist"]
input_beam_waist = params["input_beam_waist"]
input_beam_pos = params["input_beam_pos"]
phase_ref = params["phase_ref"]
freq_ref = params["freq_ref"]
L = np.array(params["L"])  # Conversion de la liste en array NumPy
Discret_rate_opt = params["Discret_rate_opt"]
Discret_rate_DDS = params["Discret_rate_DDS"]


def sort_arr_time(tmp_arr):
    """  Takes an array=[zi,ti] and returns the same but sorted in time (ti).
    """
    
    tmp_arr = tmp_arr[tmp_arr[:, 1].argsort()]
    
    
    return(tmp_arr)
            

def input_pos_arr(tmp_in_arr_val, tmp_rate):
  
    """ Use input array of positions to return output array of atoms positions and speed,
    discretised according to the hardware baudrate.
    
    Takes input: 
            -tmp_in_arr_val = [[zi, ti]], where zi is the atoms position at 
            time ti; z in m and t in s.
            
            - discretisation rate in Hz.
            
    Returns output:
            -out_arr_val_pos = [[zi, ti]], idem but discretised. 
            -out_arr_val_speed = [[vi, ti]], idem but discretised. """
            
    # Init
    
    tmp_in_arr_val = sort_arr_time(tmp_in_arr_val) # makes sure input time sorted
    plot_arr_pos(tmp_in_arr_val)
    
    
    tmin = tmp_in_arr_val[0][-1]
    tmax = tmp_in_arr_val[-1][-1]
    
    time_step = 1/tmp_rate
    time_arr = np.arange(tmin, tmax+time_step, time_step)
    
    pos_arr = np.array([])
    speed_arr = np.array([])
    
    # Comput
    
    for idx in range(len(tmp_in_arr_val)-1):
        
        # For each segment, add values position time
       
        zi,ti = tmp_in_arr_val[idx]
        zf,tf = tmp_in_arr_val[idx+1]
        
        segment_speed = (zf-zi)/(tf-ti)
        print(zi,ti,zf,tf)
        
        # Compute time list 
        
        tmp_time = np.arange(ti, tf, time_step)
        
        # Compute pos list 
        
        tmp_f = lambda t: zi + segment_speed * (t-ti)
        tmp_pos = tmp_f(tmp_time)
        
        pos_arr = np.append(pos_arr, tmp_pos)
        
        # Compute speed list 
        tmp_speed = np.ones(len(tmp_time)) * segment_speed
        speed_arr = np.append(speed_arr, tmp_speed)
        
    
    pos_arr = np.append(pos_arr, tmp_in_arr_val[-1,0]) # Add last pos value
    speed_arr = np.append(speed_arr, np.array([0])) # Set final speed to 0
    
    # Format 
    
    out_arr_val_pos = np.stack((pos_arr, time_arr), axis=-1)
    out_arr_val_speed = np.stack((speed_arr, time_arr), axis=-1)
    
    return(out_arr_val_pos, out_arr_val_speed)


def input_speed_arr(tmp_in_arr_val, tmp_rate, zi = 0):
    
    
  
    """ Use input array of speed to return output array of atoms positions and speed,
    discretised according to the hardware baudrate.
    
    Takes input: 
            -tmp_in_arr_val = [[vi, ti]], where vi is the atoms speed at 
            time ti; v in m/s and t in s.
            
            - discretisation rate in Hz.
            
            - zi: initial position (0 by default, MOT center)
            
    Returns output:
            -out_arr_val_pos = [[zi, ti]], idem but discretised. 
            -out_arr_val_speed = [[vi, ti]], idem but discretised."""
            
    # Init
    
    tmp_in_arr_val = sort_arr_time(tmp_in_arr_val) # makes sure input time sorted
    plot_arr_speed(tmp_in_arr_val)
    
    
    tmin = tmp_in_arr_val[0][-1]
    tmax = tmp_in_arr_val[-1][-1]
    
    time_step = 1/tmp_rate
    time_arr = np.arange(tmin, tmax+time_step, time_step)
    
    pos_arr = np.array([zi])
    speed_arr = np.array([])
    
    # Comput
    
    for idx in range(len(tmp_in_arr_val)-1):
        
        # For each segment, add values: acceleration / time
       
        vi,ti = tmp_in_arr_val[idx]
        vf,tf = tmp_in_arr_val[idx+1]
        
        segment_acc = (vf-vi)/(tf-ti)
        print(vi,ti,vf,tf)
        
        # Compute time list 
        
        tmp_time = np.arange(ti, tf, time_step)
        
        # Compute speed list 
        
        tmp_f = lambda t: vi + segment_acc * (t-ti)
        tmp_speed = tmp_f(tmp_time)
        
        speed_arr = np.append(speed_arr, tmp_speed)
        
        
        
    #  Compute pos list
    
    for v in speed_arr:
        
        tmp_pos = pos_arr[-1] + v * time_step
        pos_arr = np.append(pos_arr, tmp_pos)
    
    speed_arr = np.append(speed_arr, np.array([0])) # Set final speed to 0
    
    # Format 
    
    out_arr_val_pos = np.stack((pos_arr, time_arr), axis=-1)
    out_arr_val_speed = np.stack((speed_arr, time_arr), axis=-1)
    return(out_arr_val_pos, out_arr_val_speed)


def pos_to_foc_arr(tmp_arr_pos_time, w0i = input_beam_waist, z0i = input_beam_pos, w0f = trap_waist):
    """ Takes as input array of positions at each step, returns array of 
    associated focal power for each lens (0 and 1). Note that lens 0 is on
    MOT side (focal center 10 cm at pos z = 7mm, positive direction) and 
    lens 1 is on capa side (focal center 10 cm at z = 7 mm, negative direction)
    
    Takes input: 
            -tmp_arr_pos = [[zi, ti]], where zi is the atoms position at 
            time ti; z in m and t in s.
            
            
    Returns output:
            - arr_foc_0 = [[fi, ti]], where fi is the lens 0 focal length at 
            time ti; f in m and t in s.
            
            - arr_foc_1 = [[fi, ti]], where fi is the lens 1 focal length at 
            time ti; f in m and t in s. """
      
    # Init
    
    time_arr = tmp_arr_pos_time[:,1]
    tmp_arr_pos = tmp_arr_pos_time[:,0]
            
    arr_foc_0 = np.array([])     
    arr_foc_1 = np.array([])   
    
    # Comput foc array
    
    for z in tmp_arr_pos:
        
        z0f_0 = 10e-2 + (z - 7e-3)  # central position + (z - shift MOT)
        z0f_1 = 10e-2 - (z - 7e-3)  # central position - (z - shift MOT)
        
        tmp_f0 = compute_foc_opt_setup(w0i, z0i, w0f, z0f_0)
        tmp_f1 = compute_foc_opt_setup(w0i, z0i, w0f, z0f_1)
        
        
        arr_foc_0 = np.append(arr_foc_0, np.array([tmp_f0]))
        arr_foc_1 = np.append(arr_foc_1, np.array([tmp_f1]))
        
     
    
    out_arr_val_foc_0 = np.stack((arr_foc_0, time_arr), axis=-1)
    out_arr_val_foc_1 = np.stack((arr_foc_1, time_arr), axis=-1)
    
    
    return out_arr_val_foc_0, out_arr_val_foc_1


def plot_arr_pos(tmp_arr):
    
    fig, ax = plt.subplots()
    
    ax.plot(tmp_arr[:,1]*1e3, tmp_arr[:,0]*1e3)
    ax.set_xlabel("Time [ms]")
    ax.set_ylabel("Position [mm]")
    return 

def plot_arr_speed(tmp_arr):
    
    fig, ax = plt.subplots()
    
    ax.plot(tmp_arr[:,1]*1e3, tmp_arr[:,0], color = 'r')
    ax.set_xlabel("Time [ms]")
    ax.set_ylabel("Speed [m/s]")
    
    return 

def plot_arr_pos_speed(tmp_arr_pos, tmp_arr_speed):
    
    fig, ax_z = plt.subplots()
    ax_v = ax_z.twinx()
    
    ax_z.plot(tmp_arr_pos[:,1]*1e3, tmp_arr_pos[:,0]*1e3, color = 'b')
    ax_z.set_xlabel("Time [ms]")
    ax_z.set_ylabel("Position [mm]", color = 'b')
    ax_z.set_title("Atoms position and speed over time")
    
    ax_v.plot(tmp_arr_speed[:,1]*1e3, tmp_arr_speed[:,0], color = 'g')
    ax_v.set_ylabel("Speed [m/s]", color = 'g')
    
    return

def plot_arr_pos_f(tmp_arr_pos, tmp_arr_focal_0, tmp_arr_focal_1):
    
    fig, ax_z = plt.subplots()
    ax_v = ax_z.twinx()
    
    ax_z.plot(tmp_arr_pos[:,1]*1e3, tmp_arr_pos[:,0]*1e3, color = 'b')
    ax_z.set_xlabel("Time [ms]")
    ax_z.set_ylabel("Position [mm]", color = 'b')
    ax_z.set_title("Atoms position and focal length over time")
    
    ax_v.plot(tmp_arr_focal_0[:,1]*1e3, tmp_arr_focal_0[:,0]*1e2, label = "DT0", color = 'r')
    ax_v.plot(tmp_arr_focal_1[:,1]*1e3, tmp_arr_focal_1[:,0]*1e2, label = "DT1", color = 'g')
    ax_v.set_ylabel("Focal length [cm]")
    
    plt.legend()
    
    return

def plot_arr_pos_V(tmp_arr_pos, tmp_arr_volt_0, tmp_arr_volt_1):
    
    fig, ax_z = plt.subplots()
    ax_v = ax_z.twinx()
    
    ax_z.plot(tmp_arr_pos[:,1]*1e3, tmp_arr_pos[:,0]*1e3, color = 'b')
    ax_z.set_xlabel("Time [ms]")
    ax_z.set_ylabel("Position [mm]", color = 'b')
    ax_z.set_title("Atoms position and voltage applied over time")
    
    ax_v.plot(tmp_arr_volt_0[:,1]*1e3, tmp_arr_volt_0[:,0], label = "DT0", color = 'r')
    ax_v.plot(tmp_arr_volt_1[:,1]*1e3, tmp_arr_volt_1[:,0], label = "DT1", color = 'g')
    ax_v.set_ylabel("Keyseight voltage [V]")
    
    plt.legend()
    
    return
    

def plot_arr_pos_phi(tmp_arr_pos, tmp_arr_phi_0, tmp_arr_phi_1):
    
    fig, ax_z = plt.subplots()
    ax_v = ax_z.twinx()
    
    ax_z.plot(tmp_arr_pos[:,1]*1e3, tmp_arr_pos[:,0]*1e3, color = 'b')
    ax_z.set_xlabel("Time [ms]")
    ax_z.set_ylabel("Position [mm]", color = 'b')
    ax_z.set_title("Atoms position and focal length over time")
    
    ax_v.plot(tmp_arr_phi_0[:,1]*1e3, tmp_arr_phi_0[:,0], label = "Channel 0", color = 'r')
    ax_v.plot(tmp_arr_phi_1[:,1]*1e3, tmp_arr_phi_1[:,0], label = "Channel 1", color = 'g')
    ax_v.plot(tmp_arr_phi_1[:,1]*1e3, tmp_arr_phi_0[:,0]-tmp_arr_phi_1[:,0], label = "Relative phase", color = 'k')
    ax_v.set_ylabel("Phase of each source [rad]")
    
    plt.legend()
    
    return


def plot_arr_pos_freq(tmp_arr_pos, tmp_arr_freq_0, tmp_arr_freq_1):
    
    fig, ax_z = plt.subplots()
    ax_v = ax_z.twinx()
    
    ax_z.plot(tmp_arr_pos[:,1]*1e3, tmp_arr_pos[:,0]*1e3, color = 'b')
    ax_z.set_xlabel("Time [ms]")
    ax_z.set_ylabel("Position [mm]", color = 'b')
    ax_z.set_title("Atoms position and focal length over time")
    
    ax_v.plot(tmp_arr_freq_0[:,1]*1e3, tmp_arr_freq_0[:,0]*1e-6,
              label = "Channel 0", color = 'r')
    ax_v.plot(tmp_arr_freq_1[:,1]*1e3, tmp_arr_freq_1[:,0]*1e-6,
              label = "Channel 1", color = 'g')
    ax_v.plot(tmp_arr_freq_1[:,1]*1e3, (tmp_arr_freq_0[:,0]-tmp_arr_freq_1[:,0])*1e-6, 
              label = "Frequency difference", color = 'k')
    ax_v.set_ylabel("Frequency of each source [MHz]")
    
    plt.legend()
    
    return

def plot_arr_pos_freq_diff(tmp_arr_pos, tmp_arr_freq_0, tmp_arr_freq_1):
    
    fig, ax_z = plt.subplots()
    ax_v = ax_z.twinx()
    
    ax_z.plot(tmp_arr_pos[:,1]*1e3, tmp_arr_pos[:,0]*1e3, color = 'b')
    ax_z.set_xlabel("Time [ms]")
    ax_z.set_ylabel("Position [mm]", color = 'b')
    ax_z.set_title("Atoms position and focal length over time")
    
    
    ax_v.plot(tmp_arr_freq_1[:,1]*1e3, (tmp_arr_freq_0[:,0]-tmp_arr_freq_1[:,0])*1e-6, 
              label = "Frequency difference", color = 'k')
    ax_v.set_ylabel("Frequency [MHz]")
    
    plt.legend()
    
    return

def plot_arr_speed_freq_diff(tmp_arr_speed, tmp_arr_freq_0, tmp_arr_freq_1):
    
    fig, ax_z = plt.subplots()
    ax_v = ax_z.twinx()
    
    ax_z.plot(tmp_arr_speed[:,1]*1e3, tmp_arr_speed[:,0], color = 'b')
    ax_z.set_xlabel("Time [ms]")
    ax_z.set_ylabel("Speed [m/s]", color = 'b')
    ax_z.set_title("Atoms speed and frequency difference length over time")
    

    ax_v.plot(tmp_arr_freq_1[:,1]*1e3, (tmp_arr_freq_0[:,0]-tmp_arr_freq_1[:,0])*1e-6, 
              label = "Frequency difference", color = 'g')
    ax_v.set_ylabel("Frequency [MHz]")
    
    plt.legend()
    
    return

def save_json(np_array, file_path, mode='write'):
    """
    Sauvegarde un array NumPy dans un fichier JSON.

    :param np_array: Array NumPy à sauvegarder.
    :param file_path: Chemin vers le fichier JSON.
    :param mode: 'write' pour écrire (remplace le contenu existant) ou 'append' pour ajouter.
    """
    # Convertir l'array NumPy en liste
    data_to_save = np_array.tolist()

    # Déterminer le mode d'ouverture du fichier
    open_mode = 'w' if mode == 'write' else 'a'

    # Sauvegarder dans le fichier JSON
    with open(file_path, open_mode) as file:
        # Si on append, il faut traiter différemment car json ne supporte pas directement l'append
        if open_mode == 'a':
            try:
                # D'abord, lire le contenu existant
                existing_data = json.load(open(file_path, 'r'))
                # Si le contenu existant n'est pas une liste, le convertir en liste
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
                # Ajouter la nouvelle donnée
                existing_data.append(data_to_save)
                # Réécrire le fichier avec les données mises à jour
                json.dump(existing_data, open(file_path, 'w'))
            except json.JSONDecodeError:
                # Si le fichier est vide ou ne contient pas du JSON valide, écrire la nouvelle donnée
                json.dump(data_to_save, file)
        else:
            json.dump(data_to_save, file)


#%%
Z_opt, V_opt = input_speed_arr(L, Discret_rate_opt)
#%%
profil_position_path = "/Users/gauthierrey/Desktop/STAGE/Déplacement/Soft_atoms_displacement/Soft_atom_disp_E17/Fonctions_separes_profil/Parameters/Profil_position.json"
profil_speed_path = "/Users/gauthierrey/Desktop/STAGE/Déplacement/Soft_atoms_displacement/Soft_atom_disp_E17/Fonctions_separes_profil/Parameters/Profil_speed.json"
save_json(Z_opt, profil_position_path)
save_json(V_opt, profil_speed_path)
#%%
translate_optics_path = 'Translate_Optics.py'
with open(translate_optics_path) as file:
    script = file.read()
exec(script)

translate_DDS_path = "Translate_DDS.py"
with open(translate_DDS_path) as file:
    script = file.read()
exec(script)


