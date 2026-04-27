import numpy as np
import pandas as pd # for reading csv
import matplotlib.pyplot as plt # for plotting
from scipy.optimize import linprog    # for step 4 of readme linear programming part
import argparse

# Known standard TSopt clock frequencies in Hz (from Kohno Table 2)
STANDARD_HZ = [2, 10, 100, 512, 1000]

#read csv, get values
def load_data(path):
    df = pd.read_csv(path)
    return df   ### TODO: check csv column names

#read me mentioned to shift time stamp so this makes the fitting part easier
def to_relative(t, T):
    return t - t[0], T - T[0]

def to_relative_df(data_frame: pd.DataFrame):
    try:
        # Create columns for the relative arrival time and relative tsval
        data_frame['rel_arrival_time'] = data_frame['arrival_time'] - data_frame['arrival_time'].iloc[0]
        data_frame['rel_tsval'] = (data_frame['tsval'] - data_frame['tsval'].iloc[0])
    except Exception as e:
        print(f"Error calculating the relative time - {e}")

def infer_hz(rel_arrival_time: np.ndarray, rel_tsval: np.ndarray) -> int:
    """
    Infer the TSopt clock frequency by computing the slope of raw
    (rel_arrival_time, rel_tsval) points, then rounding to the nearest
    standard value from Kohno Table 2.
    """
    slope, _ = np.polyfit(rel_arrival_time, rel_tsval, 1)
    nearest = min(STANDARD_HZ, key=lambda hz: abs(hz - slope))
    print(f"Inferred TSopt clock: raw slope = {slope:.2f} ticks/s -> nearest standard = {nearest} Hz")
    return nearest

#step 4 of readme - linear programming slope estimation
def solve_upper_bound_fit(x, y) -> tuple:
    n = len(x)
    c = np.array([x.sum(), n])
    A = np.column_stack((-x, -np.ones(n)))
    b = -y
    
    #this line was chatgpt
    res = linprog(c, A_ub=A, b_ub=b, bounds=[(None, None), (None, None)], method="highs")
    alpha = res.x[0]
    beta = res.x[1]
    return alpha, beta

#step 5 of readme
#use tick rate to get clk skew
def skew_ppm(alpha, nominal_hz):
    return (alpha / nominal_hz - 1.0) * 1000000

#step 4 plotting part of readme
#plotting with upper bound fit
def plot_fit(x, y, alpha, beta, nominal_hz, ppm):
    # convert tsval ticks to seconds then compute offset (Kohno Fig 1)
    y_offset = (y / nominal_hz - x) * 1000  # milliseconds

    xs = np.linspace(0, x.max(), 100)
    fit_line = (alpha * xs + beta) / nominal_hz * 1000 - xs * 1000

    plt.scatter(x, y_offset, s=10, label="data")
    plt.plot(xs, fit_line, label=f"upper bound ({ppm:.4f} ppm)")
    # least squares (mentioned in the readme)
    m, b = np.polyfit(x, y_offset, 1)
    plt.plot(xs, m * xs + b, "--", label="least squares")
    plt.xlabel("time (s)")
    plt.ylabel("observed offset (ms)")
    plt.title("Clock skew estimate")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='Calculates the clock skew of a timestamp file.')
    # Add arguments
    parser.add_argument('input_path', metavar='input_path', type=str, help='The filepath of the csv file')
    parser.add_argument('--hz', type=int, default=None, help='TSopt clock frequency in Hz. If not provided, inferred from data.')
    # Parse the arguments
    args = parser.parse_args()
    
    # Get the data frame from the CSV
    ts_df = load_data(args.input_path)
    # Calculate the relative times
    to_relative_df(ts_df)

    # Infer or use provided Hz
    nominal_hz = args.hz if args.hz is not None else infer_hz(
        ts_df['rel_arrival_time'].to_numpy(),
        ts_df['rel_tsval'].to_numpy()
    )

    # Scale the tsval values to seconds
    ts_df['rel_tsval'] = ts_df['rel_tsval']
    alpha, beta = solve_upper_bound_fit(ts_df['rel_arrival_time'], ts_df['rel_tsval'])
    
    # Calculate the ppm
    ppm = skew_ppm(alpha, nominal_hz)
    print(f"The calcualted clock skew is {ppm}ppm")
    plot_fit(ts_df['rel_arrival_time'], ts_df['rel_tsval'], alpha, beta, nominal_hz, ppm)