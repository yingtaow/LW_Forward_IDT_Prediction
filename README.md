# IC8H18 Ignition Delay Time Prediction

A Python implementation for predicting ignition delay times (IDT) of fuels using the Livengood-Wu (L-W) forward integral method.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Directory Structure](#directory-structure)
- [Parameters](#parameters)
- [Example](#example)
- [License](#license)

## Introduction

This program predicts the ignition delay time (IDT) of fuels/air mixtures in rapid compression machines (RCM) or any other combustion systems with transient non-reactive thermal trajectories using the Livengood-Wu integral approach. The Livengood-Wu integral is a widely used method for predicting ignition delay in engines and combustion systems.

The model considers both first-stage and total ignition delays, accounting for the chemical kinetics of fuel combustion under various thermodynamic conditions.   

## Features

- **Livengood-Wu Integral Method**: Implements the forward integral approach for ignition delay prediction
- **Two-Stage Ignition Model**: Predicts both first-stage and total ignition delays
- **Non-reactive Compression Data**: Processes experimental pressure-temperature traces from non-reactive tests
- **Parameter Conversion**: Supports both 11-parameter and 17-parameter input formats
- **Visualization**: Generates comparison plots between predicted and experimental IDTs
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.8 or higher
- The following Python packages:
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `pyyaml`

### Install Dependencies

```bash
pip install numpy pandas matplotlib pyyaml
```

## Usage

### Running the Program

```bash
python main_nonreac_L-W_integral_V1.py
```

### Configuration

The program uses a YAML configuration file (`Pre_config.yaml`) to specify input parameters. See the [Configuration](#configuration) section for details.

## Configuration

The `Pre_config.yaml` file contains the following settings:

```yaml
# Directory settings
data_dir: "UoG/UoG_F10_20bar_inputfile"       # Input data directory
results_dir: "UoG/Pre_results_F10_20bar"       # Output results directory

# Input File patterns
csv_pattern: "*.csv"                           # Pattern for matching CSV files
exp_data_file: "UoG/exp_data_F10_20bar.csv"    # Experimental data filename

# Parameters file
param_path: "fit_results_IC8H18-all.txt"       # Path to correlation parameters file

# Mixture information (required for 17-parameter TXT files)
equivalence_ratio: 1.0                         # Equivalence ratio (phi)
fuel_molar_fraction: 0.01163                   # Fuel molar fraction [F]

# EOC Time settings
t_shift: 0.0                                   # EOC time shift (ms)
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `data_dir` | Directory containing input CSV files | - |
| `results_dir` | Directory for saving output results | - |
| `csv_pattern` | Glob pattern for matching input CSV files | `"*.csv"` |
| `exp_data_file` | Path to experimental IDT data CSV | - |
| `param_path` | Path to parameter file (.csv or .txt) | - |
| `equivalence_ratio` | Equivalence ratio (phi) | 1.0 |
| `fuel_molar_fraction` | Fuel molar fraction [F] | 0.0 |
| `t_shift` | EOC time shift in milliseconds | 0.0 |

## Directory Structure

```
.
├── main_nonreac_L-W_integral_V1.py    # Main program entry
├── idt_calculator_nonreac.py          # IDT calculation module
├── plotting_utils_forward.py          # Plotting utilities
├── Pre_config.yaml                    # Configuration file
├── fit_results_*.txt                  # Parameter fitting results
├── *_optimized_parameters.csv         # Optimized parameters
├── UoG/                               # University of Glasgow data
│   ├── *_inputfile/                   # Input files
│   ├── Pre_results_*/                 # Prediction results
│   └── exp_data_*.csv                 # Experimental data
└── README.md                          # This file
```

## Parameters

The program supports two parameter input formats:

### 11-Parameter Format (CSV)

| Parameter | Description | Units |
|-----------|-------------|-------|
| A1 | Pre-exponential factor (first stage) | - |
| n1 | Pressure exponent (first stage) | - |
| E1 | Activation energy (first stage) | K |
| Ah | Pre-exponential factor (high-T) | - |
| nh | Pressure exponent (high-T) | - |
| Eh | Activation energy (high-T) | K |
| Teq | Equilibrium temperature | K |
| k | Pressure exponent for Teq | - |
| w | Temperature coefficient | - |
| C0 | Constant for cross-term | - |
| xf | Temperature fraction | - |

### 17-Parameter Format (TXT)

The 17-parameter format includes additional parameters for mixture-dependent corrections:

| Additional Parameter | Description |
|---------------------|-------------|
| b1 | Phi exponent for A1 |
| c1 | F exponent for A1 |
| bh | Phi exponent for Ah |
| ch | F exponent for Ah |
| u | Phi exponent for Teq |
| s | F exponent for Teq |

These parameters are automatically converted to 11 parameters using the specified equivalence ratio (`phi`) and fuel molar fraction (`F`).

## Example

### Running with Default Configuration

1. Configure `Pre_config.yaml` with your input data:
   ```yaml
   data_dir: "UoG/UoG_F10_20bar_inputfile"
   results_dir: "UoG/Pre_results_F10_20bar"
   csv_pattern: "*.csv"
   exp_data_file: "UoG/exp_data_F10_20bar.csv"
   param_path: "fit_results_IC8H18-all.txt"
   equivalence_ratio: 1.0
   fuel_molar_fraction: 0.01163
   ```

2. Run the program:
   ```bash
   python main_nonreac_L-W_integral_V1.py
   ```

3. Check the results in the specified `results_dir`:
   - `IDT_comparison.png`: Plot comparing predicted vs experimental IDTs
   - `IDT_predicted.csv`: CSV file with predicted IDT values

### Output Files

The program generates the following output files in the `results_dir`:

- **IDT_comparison.png**: A semi-logarithmic plot showing predicted first-stage and total IDTs compared with experimental data
- **IDT_predicted.csv**: CSV file containing:
  - `1000 K/T`: Inverse temperature (K⁻¹)
  - `Tc (K)`: Temperature at EOC
  - `Pc (bar)`: Pressure at EOC
  - `Predicted_1st_IDTs (ms)`: Predicted first-stage ignition delay
  - `Predicted_Total_IDTs (ms)`: Predicted total ignition delay
  - `Dp_at_1st_ignition (bar)`: Pressure rise at first-stage ignition

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📖 Reference

If you use this code in your research, please cite our paper:

> Yingtao Wu, Zhonghao Zhao, Yuxin Fang, Pengzhi Wang, Song Cheng, Chenglong Tang, Zuohua Huang, Henry Curran.  
> "A Multi-Stage Inverse Integral Method for Deriving Ignition Delay Correlation from Transient Autoignition Experimental Measurements."  
> (submitted)