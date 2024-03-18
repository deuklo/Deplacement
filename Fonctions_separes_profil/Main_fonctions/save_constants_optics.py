import json

def save_constants_to_file(constants, file_path):
    """
    Saves given constants to a JSON file.
    
    Args:
        constants (dict): Dictionary containing constants to save.
        file_path (str): Path of the file where to save the constants.
    """
    with open(file_path, 'w') as f:
        json.dump(constants, f, indent=4)

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

# Constants
constants = {
    "pos_to_foc_arr_constants": {
        "input_beam_waist": 1e-3,
        "input_beam_pos": 700e-3 ,
        "trap_waist": 6e-6,
        "central_pos": 10e-2,
        "shift_MOT": 7e-3
    },
    "pos_to_foc_opt_setup_constants": {
        "f1": 40e-3,
        "D1": 125e-3,
        "fopt": 85e-3,
        "D2": 150e-3,
        "f2": 150e-3,
        "D3": 450e-3,
        "f3": 300e-3,
        "D4": 400e-3,
        "f4": 100e-3
    }
}

# Example usage
file_path = '/Users/gauthierrey/Desktop/STAGE/Déplacement/Soft_atoms_displacement/Soft_atom_disp_E17/Fonctions_separes_profil/Parameters/optical_setup_constants.json'

# Save the constants to a file
save_constants_to_file(constants, file_path)

# To load the constants later, you can use:
# loaded_constants = load_constants_from_file(file_path)
