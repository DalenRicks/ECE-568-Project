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

Because network delay is always positive, observed points are always shifted downward from their true position. A standard least-squares regression would average across these delays and underestimate the slope.

Instead, Kohno uses a **linear program to find the upper-bounding line** — the tightest line that sits above all observed points. This line represents the zero-delay case and its slope is therefore the true measured frequency of the ESP32's TSopt clock.

The LP minimizes the average vertical distance from the line to all points, subject to the constraint that the line must upper-bound every point:

```
minimize:   (1/|T|) * Σ (α·x_i + β - y_i)
subject to: α·x_i + β ≥ y_i   for all i
```

The solution gives slope `α` — the measured tick rate in ticks/second.

### 5. Converting Slope to Clock Skew (ppm)

With the measured tick rate `α` and the known nominal frequency `Hz[C_tcp]`:

```
skew_ppm = (α / Hz[C_tcp] - 1) × 1,000,000
```

This value is the clock skew in parts per million. It represents how much faster or slower the ESP32's clock runs relative to its intended frequency, and serves as the device fingerprint.

