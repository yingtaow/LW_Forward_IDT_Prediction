import os
import glob
import pandas as pd
import yaml


# Import necessary modules
from plotting_utils_forward import plot_predicted_idts
from idt_calculator_nonreac import IDTCalculator

def load_config(config_path='Pre_config.yaml'):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def convert_17params_to_11params(param_dict, phi, F):
    """
    Convert 17 parameters to 11 parameters
    
    Parameters:
    -----------
    param_dict : dict
        Dictionary containing 17 parameters
    phi : float
        Equivalence ratio
    F : float
        Fuel molar fraction
    
    Returns:
    --------
    tuple
        11 converted parameters: A1_new, n1, E1, Ah_new, nh, Eh, Teq_new, k, w, C0, xf
    """
    # Extract original parameters
    A1 = param_dict['A1']
    b1 = param_dict['b1']
    c1 = param_dict['c1']
    n1 = param_dict['n1']
    E1 = param_dict['E1']
    Ah = param_dict['Ah']
    bh = param_dict['bh']
    ch = param_dict['ch']
    nh = param_dict['nh']
    Eh = param_dict['Eh']
    Teq = param_dict['Teq']
    k = param_dict['k']
    w = param_dict['w']
    C0 = param_dict['C0']
    xf = param_dict['xf']
    
    # Convert parameters
    A1_new = A1 * (phi ** b1) * (F ** c1)
    Ah_new = Ah * (phi ** bh) * (F ** ch)
    Teq_new = Teq * (phi ** param_dict.get('u', 0.0)) * (F ** param_dict.get('s', 0.0))
    
    print(f"Parameter conversion (17 -> 11):")
    print(f"  phi = {phi}, [F] = {F}")
    print(f"  A1: {A1:.6e} -> {A1_new:.6e}")
    print(f"  Ah: {Ah:.6e} -> {Ah_new:.6e}")
    print(f"  Teq: {Teq:.6f} -> {Teq_new:.6f}")
    
    return A1_new, n1, E1, Ah_new, nh, Eh, Teq_new, k, w, C0, xf

def load_parameters(param_path, phi, F):
    """
    Load parameters from either CSV (11 params) or TXT (17 params) file
    
    Parameters:
    -----------
    param_path : str
        Path to the parameter file
    phi : float
        Equivalence ratio
    F : float
        Fuel molar fraction
    
    Returns:
    --------
    tuple
        11 parameters for IDT calculation
    """
    file_ext = os.path.splitext(param_path)[1].lower()
    
    if file_ext == '.csv':
        # Load 11-parameter CSV file
        print(f"Loading 11-parameter CSV file: {param_path}")
        dfs_param = pd.read_csv(param_path)
        A1, n1, E1, Ah, nh, Eh, Teq, k, w, C0, xf = dfs_param['Value'].values
        return A1, n1, E1, Ah, nh, Eh, Teq, k, w, C0, xf
    
    elif file_ext == '.txt':
        # Load 17-parameter TXT file
        print(f"Loading 17-parameter TXT file: {param_path}")
        param_dict = {}
        
        with open(param_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#') and not line.startswith('WARNING'):
                    try:
                        key, value = line.split('=')
                        key = key.strip()
                        value = float(value.strip())
                        param_dict[key] = value
                    except (ValueError, IndexError):
                        continue
        
        # Check if we have all 17 parameters
        required_params = ['A1', 'b1', 'c1', 'n1', 'E1', 'Ah', 'bh', 'ch', 'nh', 'Eh', 
                          'Teq', 'k', 'w', 'u', 's', 'C0', 'xf']
        missing_params = [p for p in required_params if p not in param_dict]
        
        if missing_params:
            raise ValueError(f"Missing parameters in TXT file: {missing_params}")
        
        # Convert 17 parameters to 11 parameters
        return convert_17params_to_11params(param_dict, phi, F)
    
    else:
        raise ValueError(f"Unsupported parameter file format: {file_ext}. Use .csv or .txt")

def main():
    # Load configuration
    config = load_config()
    
    # Create results directory
    results_dir = config['results_dir']
    os.makedirs(results_dir, exist_ok=True)

    # Read csv files from data directory
    data_dir = config['data_dir']
    csv_pattern = os.path.join(data_dir, config['csv_pattern'])
    csv_files = sorted(glob.glob(csv_pattern))
    
    # Read ignition timing data from exp_data.csv
    exp_data_path = config['exp_data_file']
    idts_1st = []
    idts_combined = []
    exp_temps = []  # Store experimental temperatures
    
    if os.path.exists(exp_data_path):
        exp_data = pd.read_csv(exp_data_path)
        # Read temperature if available
        if 'T/K' in exp_data.columns:
            exp_temps = exp_data['T/K'].tolist()
        if 'IDT_1st' in exp_data.columns:
            idts_1st = exp_data['IDT_1st'].tolist()
        if 'IDT_total' in exp_data.columns:
            idts_combined = exp_data['IDT_total'].tolist()
    
    # Load input files
    # Load thermodynamic process file
    dfs = []
    for csv_file in csv_files:
        dfs.append(pd.read_csv(csv_file))
    
    # Calculate t_com for each CSV file
    # t_com = time at max pressure + t_shift
    t_shift = config.get('t_shift', 0.0)
    t_com_list = []
    
    if dfs and len(dfs) > 0:
        # Get column names from the first dataframe
        df_first = dfs[0]
        df_columns = df_first.columns.tolist()
        time_col = df_columns[0] if len(df_columns) > 0 else 'Time(msec)'
        pres_col = df_columns[2] if len(df_columns) > 2 else 'Pressure(bar)'        
        # Calculate t_com for each CSV file
        for i, df in enumerate(dfs):
            # Find index of maximum pressure
            max_pressure_idx = df[pres_col].idxmax()
            time_at_max_pressure = df.loc[max_pressure_idx, time_col]
            t_com = time_at_max_pressure + t_shift
            t_com_list.append(t_com)
            print(f"File {i+1}: t_com = {t_com:.2f} ms (time at max pressure: {time_at_max_pressure:.2f} ms, t_shift: {t_shift:.2f} ms)")
    else:
        raise ValueError("No CSV files found to calculate t_com")
    
    # Load optimization parameters file (supports both CSV and TXT formats)
    param_path = config['param_path']
    phi = config.get('equivalence_ratio', 1.0)
    F = config.get('fuel_molar_fraction', 0.0)    
    A1, n1, E1, Ah, nh, Eh, Teq, k, w, C0, xf = load_parameters(param_path, phi, F)
    final_calculator = IDTCalculator(A1, n1, E1, Ah, nh, Eh, Teq, k, w, C0, xf)
    
    # plot the predicted 1st IDT (the time integral_1st = 1 - t_com) with original 1st IDTs using the final calculator;
    # plot the predicted total IDT (the time integral_total = 1 - t_com) with original total IDTs using the final calculator;
    if os.path.exists(exp_data_path):
        plot_predicted_idts(dfs, idts_1st, idts_combined, t_com_list, final_calculator, results_dir, exp_temps)
        print("IDTs with experimental data plotted successfully.")
    else:
        plot_predicted_idts(dfs, None, None, t_com_list, final_calculator, results_dir, None)  
        print("IDTs without experimental data plotted successfully.")

if __name__ == "__main__":
    main()
