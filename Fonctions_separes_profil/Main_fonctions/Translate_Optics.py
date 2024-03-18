# Translate Optics
# > Position to focal length

import json
import numpy as np

# Lecture du fichier JSON
with open('/Users/gauthierrey/Desktop/STAGE/Déplacement/Soft_atoms_displacement/Soft_atom_disp_E17/Fonctions_separes_profil/Parameters/parameters.json', 'r') as f:
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


def load_constants_from_file(file_path):
    """
    Loads constants from a JSON file.

    Args:
        file_path (str): Path of the file from which to load the constants.

    Returns:
        dict: Dictionary containing the loaded constants.
    """
    with open(file_path, 'r') as f:
        constants = json.load(f)
    return constants

# Load constants
constants_file_path = '/Users/gauthierrey/Desktop/STAGE/Déplacement/Soft_atoms_displacement/Soft_atom_disp_E17/Fonctions_separes_profil/Parameters/optical_setup_constants.json'
constants = load_constants_from_file(constants_file_path)
pos_to_foc_arr_constants = constants['pos_to_foc_arr_constants']
pos_to_foc_opt_setup_constants = constants['pos_to_foc_opt_setup_constants']

def save_json(F0_list, F1_list, file_path):
    # Création d'un dictionnaire pour la sérialisation JSON
    # Conversion des tableaux Numpy en listes
    F0_list = F0_list.tolist()
    F1_list = F1_list.tolist()

    data = {"F0": F0_list, "F1": F1_list}

    # Sérialisation et sauvegarde dans un fichier JSON
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)
        
def compute_foc_opt_setup(w0i, z0i, w0f, z0f):
    """ Takes input/output beam parameters, the waist position and size,
    for our optical setup and returns the corresponding optotune focal length.
        
    Input: 
        - w0i: waist of input beam
        - z0i: waist position (positive, wrt lens center)
        - w0f: waist of output beam
        - z0f: waist position ouf output beam (wrt last lens)
        
        
    Output:
        - fopt: focal length of optotune required 
            
        
    """ 
    
    ## Setup parameters focal length/dist
    
    f1 = pos_to_foc_opt_setup_constants['f1']
    D1 = pos_to_foc_opt_setup_constants['D1']
    fopt = pos_to_foc_opt_setup_constants['fopt']
    D2 = pos_to_foc_opt_setup_constants['D2']
    f2 = pos_to_foc_opt_setup_constants['f2']
    D3 = pos_to_foc_opt_setup_constants['D3']
    f3 = pos_to_foc_opt_setup_constants['f3']
    D4 = pos_to_foc_opt_setup_constants['D4']
    f4 = pos_to_foc_opt_setup_constants['f4']
    
    ## Computation forward direction 
    
    
    w0i, z0i = lens_gaussian_effect(w0i, z0i, f1)
    
    z0i = D1 - z0i
    
    
    ## Computation backward direction 
    
    
    w0f, z0f = lens_gaussian_effect(w0f, z0f, f4)
    
    z0f = D4 - z0f
    
    w0f, z0f = lens_gaussian_effect(w0f, z0f, f3)
    
    z0f = D3 - z0f
    
    w0f, z0f = lens_gaussian_effect(w0f, z0f, f2)
    
    z0f = D2 - z0f
    
    ## Compute f for optotune 
    
    
    fopt = foc_guess_gaussian_effect(w0i, z0i, w0f, z0f)   
    
    
    return fopt

def pos_to_foc_arr(tmp_arr_pos_time):
    """
    Takes as input an array of positions at each step, returns array of 
    associated focal power for each lens (0 and 1). Note that lens 0 is on
    the MOT side (focal center 10 cm at pos z = 7mm, positive direction) and 
    lens 1 is on the capa side (focal center 10 cm at z = 7 mm, negative direction).
    
    Args:
        tmp_arr_pos_time (np.ndarray): Array of positions and times, 
                                       where each element is [zi, ti], z in m, t in s.
    
    Returns:
        np.ndarray: Array of focal lengths and times for lens 0.
        np.ndarray: Array of focal lengths and times for lens 1.
    """
    # Using loaded constants
    global w0i
    w0i = pos_to_foc_arr_constants['input_beam_waist']
    z0i = pos_to_foc_arr_constants['input_beam_pos']
    w0f = pos_to_foc_arr_constants['trap_waist']
    central_pos = pos_to_foc_arr_constants['central_pos']  # Focal center 10 cm
    shift_MOT = pos_to_foc_arr_constants['shift_MOT']     # Shift MOT

    time_arr = tmp_arr_pos_time[:, 1]
    tmp_arr_pos = tmp_arr_pos_time[:, 0]

    arr_foc_0, arr_foc_1 = [], []

    for z in tmp_arr_pos:
        z0f_0 = central_pos + (z - shift_MOT)  # central position + (z - shift MOT)
        z0f_1 = central_pos - (z - shift_MOT)  # central position - (z - shift MOT)

        tmp_f0 = compute_foc_opt_setup(w0i, z0i, w0f, z0f_0)
        tmp_f1 = compute_foc_opt_setup(w0i, z0i, w0f, z0f_1)

        arr_foc_0.append(tmp_f0)
        arr_foc_1.append(tmp_f1)

    out_arr_val_foc_0 = np.stack((arr_foc_0, time_arr), axis=-1)
    out_arr_val_foc_1 = np.stack((arr_foc_1, time_arr), axis=-1)

    return out_arr_val_foc_0, out_arr_val_foc_1

def pos_to_foc_opt_setup(w0i, z0i, lens_gaussian_effect):
    """
    Revised function using constants loaded from a JSON file.
    """
    f1 = pos_to_foc_opt_setup_constants['f1']
    D1 = pos_to_foc_opt_setup_constants['D1']
    fopt = pos_to_foc_opt_setup_constants['fopt']
    D2 = pos_to_foc_opt_setup_constants['D2']
    f2 = pos_to_foc_opt_setup_constants['f2']
    D3 = pos_to_foc_opt_setup_constants['D3']
    f3 = pos_to_foc_opt_setup_constants['f3']
    D4 = pos_to_foc_opt_setup_constants['D4']
    f4 = pos_to_foc_opt_setup_constants['f4']
    
    ## Computation
    
    
    w0, z0 = lens_gaussian_effect(w0i, z0i, f1)
    
    z0 = D1 - z0
    
    
    w0, z0 = lens_gaussian_effect(w0, z0, fopt)
    
    z0 = D2 - z0
    
    w0, z0 = lens_gaussian_effect(w0, z0, f2)
    
    z0 = D3 - z0
    
    w0, z0 = lens_gaussian_effect(w0, z0, f3)
    
    z0 = D4 - z0
    
    w0f, z0f = lens_gaussian_effect(w0, z0, f4)
    
    
    return w0f, z0f

def lens_gaussian_effect(w0i, z0i, f, tmp_lambda = lambda_laser):
    """ Function which computes the effect of a lens of focal length f, on 
    a beam with parameters w0i/z0i (waist / waist position) and output the 
    output parameters w0f / z0f.
    
    Input: 
        - w0i: waist of input beam
        - z0i: waist position (positive, wrt lens center)
        - f: lens focal length
        - tmp_lambda: wavelength of the laser
        
    Output:
        - w0f: waist of output beam
        - z0f: waist position ouf output beam (wrt lens center)
            
    
    """
    
    # Compute param in
    Zr = np.pi * w0i**2 / lambda_laser # propagation in air, n=1
    if z0i != f:
        
        Mr = np.abs(f / (f-z0i))
        r = Zr /(z0i - f)
        
        M = Mr / np.sqrt(1+r**2)
        
    else: 
    
        M =  f/Zr
   
    # Compute param out
    
    w0f = w0i * M
    z0f = M**2 * (z0i-f) +f
    
    return w0f, z0f

def foc_guess_gaussian_effect(w0i, z0i, w0f, z0f, tmp_lambda = lambda_laser):
    """ Function which computes focel length f needed for a lens to get an 
    output beam of waist w0f with an input beam of waist w0i at a distance z0i.
    
    Input: 
        - w0i: waist of input beam
        - z0i: waist position (positive, wrt lens center)
        - w0f: waist of output beam
        - tmp_lambda: wavelength of the laser
        
    Output:
        - f: lens focal length
        
    NB: z0f not needed here (maybe check that the maths work, might allow to
    distinguish between f<0 and f<0 but we want f>0 here).      
    
    """
    
    # Compute in parameter 
    M = w0f / w0i
    Zr = np.pi * w0i**2 / lambda_laser # propagation in air, n=1
    
 

    # Comput out param
    if (z0i-z0f)*(w0f**2 - w0i**2) < 0 : # condition from abs value
        f = M * (z0i + Zr) / (1+M)
        
    else:
        
        f = -M * (z0i + Zr) / (1-M)
    
    return f



# Lire les données depuis le fichier JSON
with open('/Users/gauthierrey/Desktop/STAGE/Déplacement/Soft_atoms_displacement/Soft_atom_disp_E17/Fonctions_separes_profil/Parameters/Profil_position.json', 'r') as fichier_json:
    Z_opt_json = json.load(fichier_json)

# Convertir la liste en array NumPy
Z_opt = np.array(Z_opt_json)

F0, F1 = pos_to_foc_arr(Z_opt)

save_json(F0, F1, '/Users/gauthierrey/Desktop/STAGE/Déplacement/Soft_atoms_displacement/Soft_atom_disp_E17/Fonctions_separes_profil/Parameters/Profil_foc.json')
#%%
translate_Keysight_path = "Translate_Keysight.py"
with open(translate_Keysight_path) as file:
    script = file.read()
exec(script)

