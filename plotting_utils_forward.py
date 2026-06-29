import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from idt_calculator_nonreac import integrate_idt

def plot_predicted_idts(dfs, original_idts_1st, original_idts_total, t_com_list, calculator, results_dir, exp_temps=None):
    # Default column names
    DEFAULT_TIME_COL = 'Time(msec)'
    DEFAULT_TEMP_COL = 'Temperature(K)'
    DEFAULT_PRES_COL = 'Pressure(bar)'
    
    # get column names from the first dataframe (CSV file)
    if dfs and len(dfs) > 0:
        df_columns = dfs[0].columns.tolist()
        time_col = df_columns[0] if len(df_columns) > 0 else DEFAULT_TIME_COL
        temp_col = df_columns[1] if len(df_columns) > 1 else DEFAULT_TEMP_COL
        pres_col = df_columns[2] if len(df_columns) > 2 else DEFAULT_PRES_COL
    else:
        time_col, temp_col, pres_col = DEFAULT_TIME_COL, DEFAULT_TEMP_COL, DEFAULT_PRES_COL
    
    predicted_idts_1st = []
    predicted_idts_total = []
    Dp_values = []  # Store Dp at 1st stage ignition

    # Process all dataframes for both 1st and total IDT calculations
    for i, df in enumerate(dfs):
        time = df[time_col].values
        pressure = df[pres_col].values
        temperature = df[temp_col].values
        
        # Get corresponding t_com for this file
        t_com = t_com_list[i] if i < len(t_com_list) else t_com_list[0]
        
        # Calculate 1st IDT
        idt_1st = calculator.calculate_idt_1st(pressure, temperature)
        integral_1st = integrate_idt(time, idt_1st)
        
        # Find index when integral_1st reaches 1.0
        idx_1st = np.argmin(np.abs(integral_1st - 1.0))
        idt_1st_pred = time[idx_1st] - t_com
        if idt_1st_pred < 0:  
            predicted_idt_1st = np.nan
        else:
            predicted_idt_1st = idt_1st_pred
        predicted_idts_1st.append(predicted_idt_1st)
        
        # Calculate Dp at 1st stage ignition
        p_at_1st = pressure[idx_1st]
        T_at_1st = temperature[idx_1st]
        Dp = calculator.calculate_Dp(p_at_1st, T_at_1st)
        Dp_values.append(Dp)
        
        # Calculate total IDT
        idt_hi = calculator.calculate_idt_hi(pressure, temperature)
        integral_hi = integrate_idt(time, idt_hi)
        idt_cf = calculator.calculate_idt_cf(pressure, temperature)
        # Calculate D_Tcf
        D_Tcf = calculator.calculate_DT(pressure, temperature)
        # Define the array Ti
        Ti = np.zeros_like(time)
        # Calculate Tcf
        Tcf = calculator.calculate_Tcf(temperature, D_Tcf)
        #  Calculate pcf
        pcf = calculator.calculate_pcf(pressure, temperature, D_Tcf)
        # Adjust idt_cf
        mask = (time > time[idx_1st]) & (D_Tcf > D_Tcf[idx_1st])
        pcf[mask] = calculator.calculate_pcf(pressure[mask], temperature[mask], D_Tcf[idx_1st])
        Tcf[mask] = calculator.calculate_Tcf(temperature[mask], D_Tcf[idx_1st])
        Ti[mask] = calculator.calculate_Ti(Tcf[mask], temperature[mask])
        idt_cf[mask] = calculator.calculate_idt_hi(pcf[mask], Ti[mask])
        integral_cf = integrate_idt(time, idt_cf)
        # Find the index at total ignition 
        integral_cf_total = 1 + integral_cf[idx_1st] - integral_hi[idx_1st]
        idx_total = np.argmin(np.abs(integral_cf - integral_cf_total))

        idt_total_pred = time[idx_total] - t_com
        if idt_total_pred < 0:  
            predicted_idt_total = np.nan
        else:
            predicted_idt_total = idt_total_pred
        predicted_idts_total.append(predicted_idt_total)
    
    # Calculate inv_T_total for total IDT comparison
    T_total = []
    P_total = []
    for i, df in enumerate(dfs):
        # Get corresponding t_com for this file
        t_com_i = t_com_list[i] if i < len(t_com_list) else t_com_list[0]
        
        # get temperature and pressure at t_com
        idx = (np.abs(df[time_col] - t_com_i)).idxmin()
        T_at_tcom = df.loc[idx, temp_col]
        P_at_tcom = df.loc[idx, pres_col]
        T_total.append(T_at_tcom)
        P_total.append(P_at_tcom)
    
    inv_T_total = [1000/x for x in T_total]
    
    # Sort the data in order to plot a smooth curve.
    # Sort all data together based on inv_T_total
    sorted_data = sorted(zip(inv_T_total, T_total, P_total, predicted_idts_1st, predicted_idts_total, Dp_values), key=lambda x: x[0])
    sorted_inv_T_total = [x[0] for x in sorted_data]
    sorted_T_total = [x[1] for x in sorted_data]
    sorted_P_total = [x[2] for x in sorted_data]
    sorted_predicted_idts_1st = [x[3] for x in sorted_data]
    sorted_predicted_idts_total = [x[4] for x in sorted_data]
    sorted_Dp_values = [x[5] for x in sorted_data]
    
    # Draw a comparative chart combining 1st IDTs and Total IDTs
    plt.figure(figsize=(10, 6))
    
    # Plot predicted curves first (always plotted)
    plt.semilogy(sorted_inv_T_total, sorted_predicted_idts_1st, 'y-', label='Predicted 1st IDTs')
    plt.semilogy(sorted_inv_T_total, sorted_predicted_idts_total, 'b-', label='Predicted Total IDTs')
    
    # Plot original data if available
    if original_idts_1st and exp_temps:
        # Use experimental temperatures for original data
        inv_T_exp_1st = [1000/T for T in exp_temps[:len(original_idts_1st)]]
        # Filter out NaN values
        valid_data_1st = [(inv_T, idt) for inv_T, idt in zip(inv_T_exp_1st, original_idts_1st) if not np.isnan(idt)]
        if valid_data_1st:
            sorted_exp_1st = sorted(valid_data_1st, key=lambda x: x[0])
            sorted_inv_T_exp_1st = [x[0] for x in sorted_exp_1st]
            sorted_original_idts_1st = [x[1] for x in sorted_exp_1st]
            plt.semilogy(sorted_inv_T_exp_1st, sorted_original_idts_1st, 'gs', label='Original 1st IDTs')
    
    if original_idts_total and exp_temps:
        # Use experimental temperatures for original data
        inv_T_exp_total = [1000/T for T in exp_temps]
        # Filter out NaN values
        valid_data_total = [(inv_T, idt) for inv_T, idt in zip(inv_T_exp_total, original_idts_total) if not np.isnan(idt)]
        if valid_data_total:
            sorted_exp_total = sorted(valid_data_total, key=lambda x: x[0])
            sorted_inv_T_exp_total = [x[0] for x in sorted_exp_total]
            sorted_original_idts_total = [x[1] for x in sorted_exp_total]
            plt.semilogy(sorted_inv_T_exp_total, sorted_original_idts_total, 'ro', label='Original Total IDTs')
    
    plt.xlabel('1000/T (K⁻¹)')
    plt.ylabel('IDT (ms)')
    plt.title('Comparison of Original and Predicted IDTs')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(results_dir, 'IDT_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()    
    print(f"IDT comparison plot saved to {results_dir}")
    
    # Save predicted IDT data to CSV with temperature and pressure at t_com
    csv_data_predicted = pd.DataFrame({
        '1000 K/T': sorted_inv_T_total,
        'Tc (K)': sorted_T_total,
        'Pc (bar)': sorted_P_total,
        'Predicted_1st_IDTs (ms)': sorted_predicted_idts_1st,
        'Predicted_Total_IDTs (ms)': sorted_predicted_idts_total,
        'Dp_at_1st_ignition (bar)': sorted_Dp_values
    })
    csv_data_predicted.to_csv(os.path.join(results_dir, 'IDT_predicted.csv'), index=False)
    print(f"Predicted IDT data saved to {results_dir}")


    
