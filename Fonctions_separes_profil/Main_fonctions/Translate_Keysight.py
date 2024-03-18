#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 08:18:24 2024

@author: gauthierrey
"""

# Translate Keysight
# > Foc length to volt
# > Send to Keysight

import json
import numpy as np

# Keysight generator 
import pyvisa as visa


def load_json(file_path):
    # Chargement des données depuis un fichier JSON
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    
    # Conversion des listes en arrays Numpy
    F0_list = np.array(data["F0"])
    F1_list = np.array(data["F1"])
    
    return F0_list, F1_list

# Utilisation de la fonction
F0, F1 = load_json('/Users/gauthierrey/Desktop/STAGE/Déplacement/Soft_atoms_displacement/Soft_atom_disp_E17/Fonctions_separes_profil/Parameters/Profil_foc.json')
keysight_adress = "USB0::2391::19207::MY59000570::0::INSTR"


def foc_to_volt_arr(tmp_arr_foc_time, Vmin=0, Vmax=10):
    """ Takes as input array of focal length at each step, returns array of 
    associated voltage power for one lens, that can be used for analog control. 
    
    WARNING: analo mode considers focal power and not focal length, so there 
    is a f -> d = 1/f transformation going on here.
        
    Takes input: 
            -tmp_arr_foc = [[fi, ti]], where fi is the lens focal length at 
            time ti; f in m and t in s.
            
            - Vmin: minimal voltage for the analog mapping (in V)
            
            - Vmax: maximal voltage for the analog mapping (in V)
            
    Returns output:
            - arr_volt = [[Vi, ti]], where Vi is the voltage analog control
            to apply at time ti; V in V and t in s.
            
            - dmin: minimal focal power, corresponding to Vmin
            - dmax: maximal focal power, corresponding to Vmax
            
             """
         
    # Init
    
    time_arr = tmp_arr_foc_time[:,1]
    tmp_arr_foc = tmp_arr_foc_time[:,0]
            
    arr_volt = np.array([])     
    
    # Compute 
    
    fmin = np.min(tmp_arr_foc)
    fmax = np.max(tmp_arr_foc)
    
    dmin =  1 / fmax
    dmax = 1 / fmin
    
    arr_volt = (1/tmp_arr_foc-dmin) * (Vmax - Vmin)/(dmax-dmin) 


    out_arr_val_volt = np.stack((arr_volt, time_arr), axis=-1)
    
    return out_arr_val_volt, dmin, dmax

def upload_waveform(waveform_tmp, amp_tmp, offset_tmp, channel_idx, sample_rate_tmp, device_adress_tmp, waveform_name_tmp):
    """ Functions that uploads a waveform to the keysight generator on the 
    corresponding channel, and setup phase synchronisation and trigger on. 
    
    Input: 
        - waveform = [Vi_norm], where Vi_norm is the voltage we want,
        but normalised (i.e. between -1 and 1).
       
        - amp_tmp = amplitude in V. 
        
        - offset_tmp = offset in V. 
        
        - channel_idx = index of the channel (0 or 1).
        
        - sample_rate_tmp = sampling rate in Hz.
        
        - device_adress_tmp = device address. 
        
        - waveform_name_tmp = waveform name.
        
        - create_macro_bool_tmp = boolean for 
        
    Output:
        
        -print check message "Waveforme succesfully uploaded."
    """ 
    
    
    # Load ress manager 
    rm = visa.ResourceManager('@py')

    # Connect to the device
    device_adress_tmp = str(device_adress_tmp) # insure good format
    inst = rm.open_resource(device_adress_tmp)
    print(inst.query("*IDN?"))
    
    # Send start message
    mess = "Arbitrary\nWaveform\nUpload"
    inst.write("DISP:TEXT '"+mess+"'")
    
    # Create directory
    inst.write("MMEMORY:MDIR \"INT:\\remoteAdded\"")
        
    # Set byte order 
    inst.write('FORM:BORD SWAP')
    
    # Clear volatile memory
    inst.write('SOUR'+str(channel_idx)+':DATA:VOL:CLE')
    
    # Write waveform on device
    inst.write_binary_values('SOUR'+str(channel_idx)+':DATA:ARB '+waveform_name_tmp+',', waveform_tmp, datatype='f', is_big_endian=False)

    # Waiting time
    inst.write('*WAI')
    
    # Name the waveform
    inst.write('SOUR'+str(channel_idx)+':FUNC:ARB '+waveform_name_tmp)
    
    
    # Set parameters
    inst.write('SOUR'+str(channel_idx)+':FUNC:ARB:SRAT ' + str(sample_rate_tmp))
    inst.write('SOUR'+str(channel_idx)+':VOLT:OFFS '+ str(offset_tmp))
    inst.write('SOUR'+str(channel_idx)+':FUNC ARB')
    inst.write('SOUR'+str(channel_idx)+':VOLT '+str(amp_tmp))
    
    
   
   
   
    # Error check
    instrument_err = "error"
    while instrument_err != '+0,"No error"\n':
        inst.write('SYST:ERR?')
        instrument_err = inst.read()
        if instrument_err[:4] == "-257":  #directory exists message, don't display
            continue;
        if instrument_err[:2] == "+0":    #no error
            continue;
        print(instrument_err)
        
    # Set trigger external + phase sync Test 21/11
    
    inst.write(' TRIG:SOUR EXT') 
    inst.write('SOURce'+str(channel_idx)+':PHASe:SYN')
    inst.write(' INIT')  
    
    # Close device
    inst.close()
    
    return (print("Channel setup, waiting for trigger"))
    

def prepare_generator_control(arr_volt_0, arr_volt_1, tmp_device_adress = keysight_adress):
    """ Functions that prepares the waveform generator channels 0 and 1, that
    are used to generaot rthe analog control signal. Returns a check message.
    
    Input: 
        - arr_volt_0 = [[Vi, ti]], where Vi is the voltage analog control
        to apply at time ti; V in V and t in s.
       
        - arr_volt_1 = [[Vi, ti]], where Vi is the voltage analog control
        to apply at time ti; V in V and t in s.
        
    Output:
        
        -print check message "Generator correctly set up"
    """ 
    
    # Init 
    
    V_arr_0 = arr_volt_0[:,0]
    V_arr_1 = arr_volt_1[:,0]
    
    time_arr = arr_volt_0[:,1]
    
    
    
    if not np.array_equal(arr_volt_0[:,1],arr_volt_1[:,1]):
        return print("Fail: Time array different between the two sequences.")
    
    # Compute 
    
    V_min_0 = np.min(V_arr_0)
    V_max_0 = np.max(V_arr_0)
    V_amp_0 = V_max_0 - V_min_0
    V_offset_0 = (V_max_0 - V_min_0)/2
    V_arr_0_norm = (V_arr_0 - V_offset_0)/V_amp_0

    
    V_min_1 = np.min(V_arr_1)
    V_max_1 = np.max(V_arr_1)
    V_amp_1 = V_max_1 - V_min_1
    V_offset_1 = (V_max_1 - V_min_1)/2
    V_arr_1_norm = (V_arr_1 - V_offset_1)/V_amp_1
    
    nb_points = np.size(time_arr)
    tmin = np.min(time_arr)
    tmax = np.max(time_arr)
    
    sample_rate = time_arr[1] - time_arr[0]
    
    # Upload waveforms 
    
    upload_waveform(V_arr_0_norm, V_amp_0, V_offset_0, 0, sample_rate, tmp_device_adress, "Channel 0 waveform")
    upload_waveform(V_arr_1_norm, V_amp_1, V_offset_1, 1, sample_rate, tmp_device_adress, "Channel 0 waveform")
    
    
    return print("Keysight properly setup")

V0, d0min, d0_max = foc_to_volt_arr(F0)
V1, d1min, d1_max = foc_to_volt_arr(F1)
prepare_generator_control(V0, V1, tmp_device_adress = keysight_adress)

