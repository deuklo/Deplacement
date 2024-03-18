#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 09:03:28 2024

@author: gauthierrey
"""


import numpy as np
import json


# Plot 
import matplotlib.pyplot as plt



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
    #plot_arr_speed(tmp_in_arr_val)
    
    
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

def sort_arr_time(tmp_arr):
    """  Takes an array=[zi,ti] and returns the same but sorted in time (ti).
    """
    
    tmp_arr = tmp_arr[tmp_arr[:, 1].argsort()]
    
    
    return(tmp_arr)


## Plot 

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


def pos_to_phase_arr(tmp_arr_pos_time, tmp_phase_ref = phase_ref, mode = "non_sym", tmp_lambda = lambda_laser):
    """ Takes as input array of positions at each step, returns array of 
    associated phase to apply on each source. Note that source channel 0 is on
    MOT side (focal center 10 cm at pos z = 7mm, positive direction) and 
    channel 0 is on capa side(focal center 10 cm at z = 7 mm, negative direction)
    
    Takes input: 
            -tmp_arr_pos = [[zi, ti]], where zi is the atoms position at 
            time ti; z in m and t in s.
            
            - tmp_phase_ref = phase needed to get light spot at z=0
            
            - mode: way of computing the phase, either
            -> "sym": both phased are changed
            -> "non-sym": only phase of 1 is changed
            
            - tmp_lambda: wavelength of laser
            
    Returns output:
            - arr_phi_0 = [[phii, ti]], where phii is the channel 0 phase at 
            time ti; phi in rad and t in s.
            
            - arr_phi_1 = [[phii, ti]], where phii is the channel 1 phase at 
            time ti; phi in rad and t in s. """
    
    # Init
    
    time_arr = tmp_arr_pos_time[:,1]
    tmp_arr_pos = tmp_arr_pos_time[:,0]
            
    arr_phi_0 = np.array([])     
    arr_phi_1 = np.array([])  
    
    K_L = 2 * np.pi / tmp_lambda # Wavevector associated, 1/K = disp per 2 pi

    # Computation
    
    for z in tmp_arr_pos:
        
        if mode == "sym":
            
            phi_0 = -(tmp_phase_ref + ((z*K_L)%(2*np.pi)))/2
            arr_phi_0 = np.append(arr_phi_0, np.array([phi_0]))
        
            phi_1 = +(tmp_phase_ref + ((z*K_L)%(2*np.pi)))/2
            arr_phi_1 = np.append(arr_phi_1, np.array([phi_1]))
            
        if mode == "non_sym":
            
            phi_0 = 0
            arr_phi_0 = np.append(arr_phi_0, np.array([phi_0]))
        
            phi_1 = (tmp_phase_ref + (z*K_L)%(2*np.pi))
            arr_phi_1 = np.append(arr_phi_1, np.array([phi_1]))
         
    out_arr_val_phi_0 = np.stack((arr_phi_0, time_arr), axis=-1)
    out_arr_val_phi_1 = np.stack((arr_phi_1, time_arr), axis=-1)
    
    
    return out_arr_val_phi_0, out_arr_val_phi_1

          
def speed_to_freq_arr(tmp_arr_speed_time, tmp_freq_ref = freq_ref, mode = "non_sym", tmp_lambda = lambda_laser):
    """ Takes as input array of speed at each step, returns array of 
    associated frequencies to apply on each source. Note that source channel 0 is on
    MOT side (focal center 10 cm at pos z = 7mm, positive direction) and 
    channel 0 is on capa side(focal center 10 cm at z = 7 mm, negative direction)
    
    Takes input: 
            -tmp_arr_speed = [[vi, ti]], where zi is the atoms position at 
            time ti; v in m/s and t in s.

            - mode: way of computing the phase, either
            -> "sym": both phased are changed
            -> "non-sym": only phase of 1 is changed
            
            - tmp_lambda: wavelength of laser
            
    Returns output:
            - arr_freq_0 = [[freqi, ti]], where freqi is the channel 0 frequency
            at time ti; freq in Hz and t in s.
            
            - arr_freq_1 = [[freqi, ti]], where freqi is the channel 1 frequency
            at time ti; freq in Hz and t in s. """
    
    # Init
    
    time_arr = tmp_arr_speed_time[:,1]
    tmp_arr_speed = tmp_arr_speed_time[:,0]
            
    arr_freq_0 = np.array([])     
    arr_freq_1 = np.array([])  
    

    # Computation
    
    for v in tmp_arr_speed:
        
        delta_freq = 2 * v / tmp_lambda # freq difference needed to get speed v
        
        if mode == "sym":
            
            arr_freq_0 = np.append(arr_freq_0, np.array([tmp_freq_ref-delta_freq/2]))
            arr_freq_1 = np.append(arr_freq_1, np.array([tmp_freq_ref+delta_freq/2]))
            
        if mode == "non_sym":
            
            arr_freq_0 = np.append(arr_freq_0, np.array([tmp_freq_ref]))
            arr_freq_1 = np.append(arr_freq_1, np.array([tmp_freq_ref+delta_freq/2]))
         
    out_arr_val_freq_0 = np.stack((arr_freq_0, time_arr), axis=-1)
    out_arr_val_freq_1 = np.stack((arr_freq_1, time_arr), axis=-1)
    
    
    return out_arr_val_freq_0, out_arr_val_freq_1

def save_json(F0_list, F1_list, file_path):
    F0_list = F0_list.tolist()
    F1_list = F1_list.tolist()
    data = {"F0": F0_list, "F1": F1_list}
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)  # Ajout de l'indentation


# Compute for DDS

Z_DDS, V_DDS = input_speed_arr(L, Discret_rate_DDS)
#plot_arr_pos_speed(Z_DDS,V_DDS)

P0, P1 = pos_to_phase_arr(Z_DDS)
# plot_arr_pos_phi(Z_DDS, P0, P1)

f0, f1 = speed_to_freq_arr(V_DDS)
#plot_arr_pos_freq(Z_DDS, f0, f1)
#plot_arr_pos_freq_diff(Z_DDS, f0, f1)
#plot_arr_speed_freq_diff(V_DDS, f0, f1)

profil_freq_path = "/Users/gauthierrey/Desktop/STAGE/Déplacement/Soft_atoms_displacement/Soft_atom_disp_E17/Fonctions_separes_profil/Parameters/Profil_frequencies.json"
# Enregistrement des données dans un fichier JSON avec une indentation de 4
save_json(f0, f1, profil_freq_path)


