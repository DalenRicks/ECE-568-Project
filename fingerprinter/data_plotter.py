import os
import numpy as np
import pandas as pd # for reading csv
import matplotlib.pyplot as plt # for plotting
import tkinter as tk
from tkinter import filedialog
from clock_skew_calculator import load_data, to_relative_df, infer_hz, solve_upper_bound_fit, skew_ppm

# Defines for readability
X_AXIS = 0
Y_AXIS = 1
ALPHA = 2
BETA = 3
PPM = 4
FILE_NAME = 5

def select_files() -> list:
    try:
        # Open file dialog allowing multiple selections
        file_paths = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=[("All Files", "*.*"), ("Text Files", "*.txt"), ("Python Files", "*.py")]
        )

        # Check to make sure files were selected
        if not file_paths:
            return

        # Convert tuple to list
        selected_files = list(file_paths)

        # Return list to the user
        return selected_files
    
    except Exception as e:
        print(f"Error selecting files - {e}")

#plotting with upper bound fit
def plot_data(files: list):

    # TODO: Make sure files all start at 0 or show a warning. Maybe try to make it fit but dont worry about it if its too hard
    # TODO: Take the longest file and make the line space off that. 0 pad the files that are shorter so that they are all the same length if matplotlib doesnt like the files of different lengths

    plt.figure(figsize=(10, 5))

    for file in files:
        x = file[X_AXIS]
        y = file[Y_AXIS]
        alpha = file[ALPHA]
        beta = file[BETA]
        ppm = file[PPM]
        file_name = file[FILE_NAME]
 
        # convert tsval ticks to seconds then compute offset (Kohno Fig 1)
        y_offset = y * 1000  # already in seconds, convert to ms

        xs = np.linspace(0, x.max(), 100)
        fit_line = (alpha * xs + beta) * 1000

        plt.scatter(x, y_offset, s=10, alpha=0.3, label=file_name)
        plt.plot(xs, fit_line, label=f"{file_name} upper bound ({ppm:.4f} ppm)")
        plt.xlabel("time (s)")
        plt.ylabel("observed offset (ms)")
        plt.title("Clock skew estimate")

    plt.legend()
    plt.show() 


if __name__ == "__main__":
    files = select_files()

    # Initialze empty dataset list
    dataset = []

    if files is not None:
        print(f"Selected {len(files)} files")

        for fil in files:
            # Get the file name
            fil_name = os.path.basename(fil)

            print("--------------------------------------------------------")
            print(f"Plotting: '{fil_name}'")

            # Get the data frame from the CSV
            df = load_data(fil)
            # Calculate the relative times
            to_relative_df(df)

            # Infer or use provided Hz
            nominal_hz = infer_hz(
                df['rel_arrival_time'].to_numpy(),
                df['rel_tsval'].to_numpy()
            )

            # Scale the tsval values to seconds
            df['rel_tsval'] = df['rel_tsval']
            # compute offset-set: convert ticks to seconds then subtract arrival time
            df['offset'] = df['rel_tsval'] / nominal_hz - df['rel_arrival_time']
            alpha, beta = solve_upper_bound_fit(df['rel_arrival_time'], df['offset'])
            
            # Calculate the ppm
            ppm = skew_ppm(alpha, nominal_hz)
            print(f"The calcualted clock skew is: {ppm}ppm")
            print("--------------------------------------------------------")
            print()

            # Pack data into tuple and append to data set list
            dataset.append((df['rel_arrival_time'], df['offset'], alpha, beta, ppm, fil_name))

        plot_data(dataset) 

    