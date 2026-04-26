# Fingerprinter (Server Side)

This component runs on the server and estimates the clock skew of a remote device (the ESP32 fingerprintee) by passively observing TCP timestamps in incoming packets. The technique is based on Kohno et al., *Remote Physical Device Fingerprinting* (IEEE TDSC, 2005).

---

## How It Works

### 1. TCP Timestamps as a Clock Signal

When the ESP32 sends a TCP packet, each packet's header contains a TCP timestamp option value. This value is not wall clock time — it is a raw tick counter incremented by the ESP32's internal hardware timer at a fixed rate (`Hz[C_tcp]`). Due to imperfections in the crystal oscillator, this rate is never exactly the nominal frequency. The deviation is the **clock skew**, and it is unique and stable per device — making it a hardware fingerprint.

### 2. Collecting Observations

For every incoming TCP packet from the ESP32, the server records a pair:

```
(t_i, T_i)
```

- `t_i` — server's local arrival time (wall clock, in seconds)
- `T_i` — TCP timestamp value extracted from the packet header

After collecting many packets over time, these pairs form the dataset for skew estimation.

### 3. Computing the Offset-Set

Rather than working with raw values, both axes are shifted relative to the first packet:

```
x_i = t_i - t_1   (real elapsed time in seconds, by server clock)
y_i = T_i - T_1   (elapsed ticks, by ESP32 clock)
```

If the ESP32 clock ran at exactly its nominal frequency with zero network delay, plotting `y_i` vs `x_i` would produce a perfect straight line with slope equal to the nominal frequency. In practice, two sources of noise appear:

- **Clock skew** causes the slope to differ slightly from nominal
- **Network delay** shifts points downward (packets always arrive late, never early)

### 4. Estimating the Slope via Linear Programming

Plotting `y_i` (ticks) vs `x_i` (seconds) should produce points that follow a straight line, where the slope is the ESP32's tick rate. However, network delay distorts this picture.

Each packet experiences some positive delay between when the ESP32 sent it and when the server received it. This delay adds extra time to `t_i`, making `x_i` larger than it would be in a zero-delay scenario. Since `y_i` (the tick count) is unaffected by network delay, each observed point ends up shifted to the right of its true position on the graph. The result is that every point lies to the right of where it would be without delay — meaning every point falls **below** the true line rather than on it.

Because of this one-sided distortion, standard least-squares regression underestimates the slope — it fits a line through the middle of the shifted points rather than recovering the true underlying relationship.

Kohno addresses this by using **linear programming to find the minimum-slope upper-bounding line** — the line with the smallest possible slope that still remains above every observed point. Since all points are shifted below the true line due to delay, the upper-bounding line recovers the true slope. Formally, the LP solves for slope `α` and intercept `β`:

```
minimize:   (1/|T|) * Σ (α·x_i + β - y_i)
subject to: α·x_i + β ≥ y_i   for all i
```

The constraint ensures the line stays above all points. The objective minimizes how far above the points the line sits, making it as tight as possible. The resulting slope `α` is the measured tick rate in ticks/second.

### 5. Converting Slope to Clock Skew (ppm)

With the measured tick rate `α` and the known nominal frequency `Hz[C_tcp]`:

```
skew_ppm = (α / Hz[C_tcp] - 1) × 1,000,000
```

This value is the clock skew in parts per million. It represents how much faster or slower the ESP32's clock runs relative to its intended frequency, and serves as the device fingerprint.

---

## Scripts

### `setup.py`

Run once before anything else. Creates a Python virtual environment at `~/fingerprinter-env` and installs `scapy` into it.

```bash
python3 setup.py
```

> **Windows:** Run as Administrator. **Linux:** Run as your regular user.

---

### `server.py`

Starts a TCP server that accepts a connection from the ESP32 and keeps it open. The ESP32 needs something to connect to before any packets flow.

```bash
python3 server.py [--host HOST] [--port PORT]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--host` | `0.0.0.0` | Interface to listen on. `0.0.0.0` accepts on all interfaces. |
| `--port` | `12345` | Port to listen on. Must match the port set in the ESP32 menuconfig. |

---

### `run.py`

The main entry point for capturing packets. Internally calls `capture.py` using the virtual environment Python. At least one of `--duration` or `--count` must be specified — if both are provided, capture stops at whichever condition is met first.

```bash
python3 run.py --src-ip <ESP32_IP> [--output FILE] [--duration SECONDS] [--count N]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--src-ip` | required | IP address of the ESP32 to filter on |
| `--output` | `timestamps.csv` | Output CSV file path |
| `--duration` | — | Stop after this many seconds |
| `--count` | — | Stop after this many packets |

> **Linux:** Automatically runs with `sudo` since raw packet capture requires root privileges. Also fixes CSV file ownership after capture so the file is accessible without sudo. **Windows:** Run the terminal as Administrator instead.

---

### `capture.py`

Called internally by `run.py` — you do not need to run this directly. It sniffs incoming TCP packets from the ESP32, extracts the TCP timestamp value from each packet header, and saves the collected `(arrival_time, tsval)` pairs to a CSV file.

---

## Usage Order

1. Run `python3 setup.py` (first time only)
2. Run `python3 server.py` in one terminal
3. Run `python3 run.py --src-ip <ESP32_IP> --duration <seconds>` in another terminal
4. Flash and run the ESP32 — it will connect to the server and begin sending packets
5. After capture completes, the CSV file contains the timestamp pairs for skew estimation


---

### `clock_skew_calculator.py`

Called after collecting data to calculate the clock skew. Will display the plot of the collected data and print the calculated clock skew in the terminal.

```bash
python3 clock_skew_calculator.py [file_path]
```
---


