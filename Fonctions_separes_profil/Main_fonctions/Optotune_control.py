# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 18:22:26 2022

@author: Guillaume
"""

#### CODE FOR THE NEW CONTROLLER ####

### Package import 

import numpy as np
import time
from time import sleep
from optoKummenberg import UnitType
from optoICC import connect, DeviceModel, WaveformType
import optoICC




### Main code 

## Parameters set 

manip_test_bool = False
vector_test_bool = False
analog_test_bool =  False 

## Connection 

icc4c = connect() #Connecting to board. Port can be specified like connect(port='COM12')
print()
print("Board info")

#Getting board info
serial_number = icc4c.BoardEEPROM.getSerialNumber()[0].decode('UTF-8')
fw_version = f"{icc4c.Status.GetFirmwareVersionMajor()[0]}.{icc4c.Status.GetFirmwareVersionMinor()[0]}.{icc4c.Status.GetFirmwareVersionRevision()[0]}"

print(f"Board serial number: {serial_number}")
print(f"Board firmware version: {fw_version}")

# Connection chec

is_lens_connected = False

connected_devices = [DeviceModel(icc4c.MiscFeatures.GetDeviceType(0)), DeviceModel(icc4c.MiscFeatures.GetDeviceType(1)),
                     DeviceModel(icc4c.MiscFeatures.GetDeviceType(2)), DeviceModel(icc4c.MiscFeatures.GetDeviceType(3))]
print(f"Connected devices: {''.join('{},'.format(x.name) for x in connected_devices)}")
print()
print("Driving lens")
first_connected_lens = None
for idx, device in enumerate(connected_devices):
    if device.value in [DeviceModel.EL_1030_C, DeviceModel.EL_1030_TC, DeviceModel.EL_1230_TC, DeviceModel.EL_1640_TC]:
        first_connected_lens = (device, idx)
        break

if first_connected_lens is None:
    print("No lens connected")
    
else:
    
    # Set lens channel 
    icc4c_lens_channel = icc4c.channel[first_connected_lens[1]]
    
    is_lens_connected = True 
    print("Lens connected !")
    
## Manipulation tests- adapted from icc4c_example.py

if is_lens_connected and manip_test_bool:
    
    
    
    # Check lens serial number 
    lens_serial_number = icc4c_lens_channel.DeviceEEPROM.getSerialNumber()[0].decode('UTF-8')
    print(f"Lens {first_connected_lens[0].name} ({lens_serial_number}) found on channel {first_connected_lens[1]}")

    # Check device EEPROM (internal persistent memory)
    print("Device EEPROM")

    eeprom_version = f"{icc4c_lens_channel.DeviceEEPROM.GetEEPROMversion()[0]}.{icc4c_lens_channel.DeviceEEPROM.GetEEPROMsubversion()[0]}"
    print(f"EEPROM version: {eeprom_version}")
    
    eeprom_bytes = icc4c_lens_channel.DeviceEEPROM.GetEEPROM(0, 10)
    eeprom_size = icc4c_lens_channel.DeviceEEPROM.GetEEPROMSize()[0]
    print(f"Printing {len(eeprom_bytes)}/{eeprom_size} bytes saved in EEPROM: {''.join('{:02x},'.format(x) for x in eeprom_bytes)}")

    
    # Temperature measurement 
    lens_temperature = icc4c_lens_channel.TemperatureManager.GetDeviceTemperature()[0]
    print(f"Lens temperature: {lens_temperature}°C")
    
    # Get current range
    min_lens_current = icc4c_lens_channel.DeviceEEPROM.GetMaxNegCurrent()[0] # in mA
    max_lens_current = icc4c_lens_channel.DeviceEEPROM.GetMaxPosCurrent()[0] # in mA
    print(f"Minimum current is {min_lens_current} mA, maximum current is {max_lens_current} mA")


    # Set static current mode
    print(f"Setting static current")
    #Setting input system to static input
    icc4c_lens_channel.StaticInput.SetAsInput()
    
    
    # Set different current values
    for current in range(int(min_lens_current), int(max_lens_current)+1, int((max_lens_current-min_lens_current)/5)):
        #Value has to be converted from mA to A
        current_in_A = float(current)/1000
        print(f"Current {current_in_A} A")
        icc4c_lens_channel.StaticInput.SetCurrent(current_in_A)
        sleep(1)
        
    # Set back current to zero
    print("Setting static current to 0 A")
    icc4c_lens_channel.StaticInput.SetCurrent(0.0)
    print(" ")
    
    # Signal generator test
    print("Running signal generator")
    icc4c_lens_channel.SignalGenerator.SetAsInput() # Signal gen mode
    icc4c_lens_channel.SignalGenerator.SetUnit(UnitType.CURRENT) # Set units
    icc4c_lens_channel.SignalGenerator.SetShape(WaveformType.SINE.value) # Set shape
    icc4c_lens_channel.SignalGenerator.SetAmplitude(0.2) # Set amp
    icc4c_lens_channel.SignalGenerator.SetFrequency(5) # Set freq
    icc4c_lens_channel.SignalGenerator.Run()

    for index in range(5):
        print(".", end="")
        sleep(1)

    # Stop generator 
    icc4c_lens_channel.SignalGenerator.Stop()
    
    
    
    
## Test with a vector generator

if is_lens_connected and vector_test_bool: 

    # The hard part... building a vector.
    # ----------------------------------
    # pick a frequency, trans time, amplitude, and phase
    frequency_Hz = 5
    time_transition_ms = 2
    amplitude_A = 0.1
    phase_deg = 0.0
    # calculate number of samples
    period = 1 / frequency_Hz
    num_samples = period * optoICC.SAMPLING_FREQ
    # we want an even number of samples per period, so it can be divided in two halves
    num_samples = round(num_samples / 2.0) * 2
    half_num_samples = num_samples // 2
    # samples in transition and holding time
    nsamples_tr = round(time_transition_ms / 1000 * optoICC.SAMPLING_FREQ)
    nsamples_hold = half_num_samples - nsamples_tr
    # linspace takes both start and stop points, we need to discard the stop point and add one more sample point,
    # so we use nsamples+1 and discard the last element of the vector [:-1]
    vector = list(np.linspace(start=-amplitude_A, stop=amplitude_A, num=nsamples_tr + 1)[:-1]) \
             + [amplitude_A] * nsamples_hold \
             + list(np.linspace(start=amplitude_A, stop=-amplitude_A, num=nsamples_tr + 1)[:-1]) \
             + [-amplitude_A] * nsamples_hold
    break_idx = round(phase_deg / 360.0 * len(vector))
    vector = vector[break_idx:] + vector[:break_idx]
    
    # now the easy part, send vector to the board!
    # ----------------------------------
    
    # Send vector to board
    icc4c.VectorPatternMemory.SetPattern(index=0, vector=vector)
    
    # Define VPU mode
    vpu = icc4c.Channel_1.VectorPatternUnit
    
    # Set vector mode
    vpu.SetAsInput()
    
    # Set vector parameters (freq, start - end, unit)
    vpu.SetStart(0)
    vpu.SetEnd(len(vector) - 1)
    vpu.SetFreqSampleSpeed(optoICC.SAMPLING_FREQ)
    vpu.SetUnit(optoICC.UnitType.CURRENT)
    
    # Run vetcor for 5 sec
    vpu.Run() # start
    sleep(5) # 5 seconds
    vpu.Stop() # stop
    
    # Set precise number of cycle and wait for trigger
    vpu.SetCycles(5)
    vpu.SetExternalTrigger(1) # NB: each time trigger launched, it plays vect
    
    
    
    input("Press Enter to continue...")  
    vpu.Stop()
    
## Test with analog mode  
    
if is_lens_connected and analog_test_bool: 
    
    # Set analog mode
    icc4c_lens_channel.Analog.SetAsInput()
    icc4c_lens_channel.Analog.GetUnit()
    
    
   
    min_volt_set = 0
    max_volt_set = 1
    #Volt_max =  icc4c_lens_channel.Analog.SetMaximum(max_volt_set) # in Volt?
    Volt_min = icc4c_lens_channel.Analog.SetMinimum(min_volt_set) # in Volt?
    
    #print(f"Minimum voltage is {Volt_min} V, maximum voltage is {Volt_max} V")

    min_curr_set = 0
    max_curr_set = 10
    #Curr_max = icc4c_lens_channel.Analog.SetMappingMaximum(max_curr_set) # in A?
    Curr_min =icc4c_lens_channel.Analog.SetMappingMinimum(min_curr_set) # in A?
    
    #print(f"Minimum current is {Curr_min} mA, maximum current is {Curr_max} mA")
    
    Volt_max =  icc4c_lens_channel.Analog.GetMaximum() # in Volt?
    Volt_min = icc4c_lens_channel.Analog.GetMinimum() # in Volt?
    
    print(f"Minimum voltage is {Volt_min} V, maximum voltage is {Volt_max} V")

    
    Curr_max = icc4c_lens_channel.Analog.GetMappingMaximum() # in A?
    Curr_min =icc4c_lens_channel.Analog.GetMappingMinimum() # in A?
    print(f"Minimum current is {Curr_min} mA, maximum current is {Curr_max} mA")
    
    input("Press Enter to continue...")  
    
    
## Disconnect 

icc4c.disconnect()
print("Disconnection succesful!")