import numpy as np
import pandas as pd # for reading csv
import matplotlib.pyplot as plt # for plotting
from scipy.optimize import linprog    # for step 4 of readme linear programming part
import argparse


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
def plot_fit(x, y, alpha, beta):
    xs = np.linspace(0, x.max(), 100)

    plt.scatter(x, y, s=10, label="data")

    plt.plot(xs, alpha * xs + beta, label="upper bound")

    # least squares (mentioned in the readme
    m, b = np.polyfit(x, y, 1)
    plt.plot(xs, m * xs + b, "--", label="least squares")

    plt.xlabel("time (s)")
    plt.ylabel("timestamp")
    plt.title("Clock skew estimate")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='Calculates the clock skew of a timestamp file.')

    # Add arguments
    parser.add_argument('input_path', metavar='input_path', type=str, help='The filepath of the csv file')

    # Parse the arguments
    args = parser.parse_args()
    
    # Get the data frame from the CSV
    ts_df = load_data(args.input_path)

    # Calculate the relative times
    to_relative_df(ts_df)

    # Scale the tsval values to seconds
    ts_df['rel_tsval'] = ts_df['rel_tsval']

    alpha, beta = solve_upper_bound_fit(ts_df['rel_arrival_time'], ts_df['rel_tsval'])
    
    # Calculate the ppm (I'm assuming the nominal frequency is 1000, not entirely sure what its supposed to be)
    ppm = skew_ppm(alpha, 1000)

    print(f"The calcualted clock skew is {ppm}ppm")

    plot_fit(ts_df['rel_arrival_time'], ts_df['rel_tsval'], alpha, beta)
