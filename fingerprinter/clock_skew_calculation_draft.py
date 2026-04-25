import numpy as np
import pandas as pd # for reading csv
import matplotlib.pyplot as plt # for plotting
from scipy.optimize import linprog    # for step 4 of readme linear programming part


#read csv, get values
def load_data(path):
    df = pd.read_csv(path)
    return    ### TODO: check csv column names


#read me mentioned to shift time stamp so this makes the fitting part easier
def to_relative(t, T):
    return t - t[0], T - T[0]


#step 4 of readme - linear programming slope estimation
def solve_upper_bound_fit(x, y):
    n = len(x)

    c = np.array([x.sum(), n])

    A = np.column_stack((-x, -np.ones(n)))
    b = -y
    
    #this line was chatgpt
    res = linprog(c, A_ub=A, b_ub=b, bounds=[(None, None), (None, None)], method="highs")

    return res.x

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
    # to do
