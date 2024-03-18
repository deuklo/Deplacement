import numpy as np
import json 

# Optotune 
from optoKummenberg import UnitType
from optoICC import connect, DeviceModel# , WaveformType #Pas sûr de ce package, je crois qu'il n'existe pas 
import optoICC

def setup_analog_FP(lens_channel, param = None, name = "Lens"):
    """ Function that setup the lens channel in the analog mode with focal power
    unit. Defaults values are 0-10 V for the voltage and max / min diopter for
    the focal power, but this can be tuned if param is given. Name is just for 
    the return message.
    
    Input: 
        
        - lens channel : name of the lens channel 
        
        - param = [dmin, dmax, Vmin, Vmax] minimal focal length, maximal
        
        - name: Str used to give a name to the function call.
        
    Return: 
        
        - Feedback message: name + " is correctly set up in analog mode."

    """
    
    
    # Parameters init
    
    if param != None:
        
        dmin = param[0] # min_diopter
        dmax = param[1] # max_diopter
        
        Vmin = param[2]
        Vmax = param[3]
        
       
        
    else:
        
        dmax = lens_channel.LensCompensation.GetMaxDiopter()
        dmin = lens_channel.LensCompensation.GetMinDiopter()
        
        Vmin = 0
        Vmax = 10
       
    #  Set analog in focal power mode 
    lens_channel.Analog.SetUnitType_LUT(UnitType.FP)
    
    
    # Set volate and focal power ranges 
    
    lens_channel.Analog.SetVoltages_LUT([Vmin, Vmax])
    lens_channel.Analog.SetValues_LUT([dmin, dmax])
    
    #  Set analog up 
    
    lens_channel.Analog.SetAsInput()
    
    return print(name + " is correctly set up in analog mode FP, with"+...
    +" dmin ="+str(dmin)
    +" , dmax ="+str(dmax)
    +" , Vmin ="+str(Vmin)
    +" , Vmax ="+str(Vmax))

def prepare_optotune_control(param_0, param_1):
    """ Functions that prepares the optotune lens 0 and 1 in the analog control
    mode with right parameters.
    
    Input: 
        - param_0 = [fmin, fmax, Vmin, Vmax] minimal focal length, maximal
        focal length, maximal voltage and minimal voltage for lens 0.
       
        - param_1 = [fmin, fmax, Vmin, Vmax] minimal focal length, maximal
        focal length, maximal voltage and minimal voltage for lens 1.
        
    Output:
        
        -print check message "Lenses correctly set up"
    """ 
    ## Parameters compute 
    
    
    ## Initialise lens 
    
    # Connect lens
    icc4c = connect() #Connecting to board. Port can be specified like connect(port='COM12')
    print()
    print("Board info")
    
    #Getting board info
    serial_number = icc4c.BoardEEPROM.getSerialNumber()[0].decode('UTF-8')
    fw_version = f"{icc4c.Status.GetFirmwareVersionMajor()[0]}.{icc4c.Status.GetFirmwareVersionMinor()[0]}.{icc4c.Status.GetFirmwareVersionRevision()[0]}"

    print(f"Board serial number: {serial_number}")
    print(f"Board firmware version: {fw_version}")

    # Connection check

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
        return("No lens connected")
        
    else:
        
        
        is_lens_connected = True 
        print("Lens connected !")
        
    ## Set lens channel 0
    
    icc4c_lens_channel_0= icc4c.channel[0]
    
    setup_analog_FP(icc4c_lens_channel_0, param_0, "Lens 0")
    
    ## Set lens channel 1
    
    icc4c_lens_channel_1= icc4c.channel[1]
    
    setup_analog_FP(icc4c_lens_channel_1, param_1, "Lens 1")
    

        
    return print("Lenses correctly set up")
