import os
import numpy as np
import matplotlib.pyplot as plt # for plotting
from tkinter import filedialog
from clock_skew_calculator import load_data, to_relative_df, infer_hz, solve_upper_bound_fit, skew_ppm
import argparse

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
def plot_data(files: list, plot_data_points: bool = True, plot_fit_line: bool = True, remove_y_intercept: bool = False, length_equal: bool = False):
    '''
    Plots the data for the list of offet-sets from the selected CSV files.

    This should be called after all data processing steps are complete.

    Args:
        - files: List of tuples containing the offet-sets, upper-bounds, ppm and file names.
        - plot_data_points: Plots the offset-set data points on the chart
        - plot_fit_line: Plots the upper-bound fit line for a given offset-set
        - remove_y_intercept: Removes the y-intercept offset from the plot.
    '''
    
    if not plot_data_points and not plot_fit_line:
        print("Please plot data points, the fit line, or both.")
        return
    
    if not plot_fit_line and length_equal:
        print("Unable to plot equal length since fit line is disabled")
        return

    plt.figure(figsize=(10, 5))

    # Initialize a longest file variable
    longest_file_entries = 0

    # Find the longest file
    if length_equal:
        for file in files:
            if file[X_AXIS].max() > longest_file_entries:
                longest_file_entries = file[X_AXIS].max()

    for file in files:
        x = file[X_AXIS]
        y = file[Y_AXIS]
        alpha = file[ALPHA]
        beta = file[BETA]
        ppm = file[PPM]
        file_name = file[FILE_NAME]

        if remove_y_intercept:
            y_offset = (y - beta) * 1000 
            beta = 0
        else:
            # convert tsval ticks to seconds then compute offset (Kohno Fig 1)
            y_offset = y * 1000  # already in seconds, convert to ms

        if length_equal:
            xs = np.linspace(0, longest_file_entries, 100)
        else:
            xs = np.linspace(0, x.max(), 100)
            
        fit_line = (alpha * xs + beta) * 1000

        if plot_data_points:
            plt.scatter(x, y_offset, s=10, alpha=0.3, label=file_name)
        
        if plot_fit_line:
            plt.plot(xs, fit_line, label=f"{file_name} upper bound ({ppm:.4f} ppm)")

        
        plt.xlabel("time (s)")
        plt.ylabel("observed offset (ms)")
        plt.title("Clock skew estimate")

    plt.legend()
    plt.show() 


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='Calculates the clock skew of a timestamp file.')
    # Add arguments
    parser.add_argument('--no_plot', action='store_true', help='Disables plotting the input file set')
    parser.add_argument('--stats', action='store_true', help='Calculate additional statistics from the input file set (not plotted)')
    parser.add_argument('--no_data_points', action='store_true', help='Does not plot data points on the graph')
    parser.add_argument('--no_fit_line', action='store_true', help='Does not plot data points on the upper-bound fit line')
    parser.add_argument('--fit_line_equal', action='store_true', help='Extends all of the fit lines to be the same length. Will be the length of the longest file.')
    parser.add_argument('--no_y_intercept', action='store_true', help='Removes the y-intercept offset from the plot.')
    parser.add_argument('--output_file', type=str, default=None, help='Specify an output file name to write the processed data to. Includes additional statistics if enabled.')
    # Parse the arguments
    args = parser.parse_args()

    # Prompt the user to select a file
    files = select_files()

    # Initialze empty dataset list
    dataset = []

    # Calculate the Clock skew of all the files
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

            if args.stats:
                # Calculate approximate runtime in minutes
                samples = len(df['rel_arrival_time']) 
                of_variance = np.var(df['offset'])
                of_std = np.std(df['offset'])

                print()
                print("-------------- Additional Statistics --------------")
                print(f"Number of samples: {samples}")
                print(f"Trace intercept point: {beta}")
                print(f"Offset Variance: {of_variance}")
                print(f"Offset Standard Deviation: {of_std}")


            print("--------------------------------------------------------")
            print()

            # Pack data into tuple and append to data set list
            dataset.append((df['rel_arrival_time'], df['offset'], alpha, beta, ppm, fil_name))

        mean = None
        std = None

        if args.stats:
            mean = np.mean([entry[PPM] for entry in dataset])
            std = np.std([entry[PPM] for entry in dataset])

            print("-------------- Global Statistics --------------")
            print(f"Clock Skew Mean: {mean}ppm")
            print(f"Clock Skew Standard Deviation: {std}")

        if not args.no_plot:
            plot_data(dataset, not args.no_data_points, not args.no_fit_line, args.no_y_intercept, args.fit_line_equal) 

    