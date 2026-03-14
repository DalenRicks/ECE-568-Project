
`ESP32 devices  →  Packet collection  →  Skew analysis`

Each person can own one layer.

# Person A — ESP32 Firmware (Target Devices)

This person handles everything running on the ESP32 boards.

## Responsibilities:

- Write ESP32 firmware (C++)
- Ensure the ESP32 creates TCP connections to the measurement server
- Generate consistent traffic so timestamps can be measured

Test networking stability

## Tasks:

1) ESP32 connects to the server via TCP.
2) ESP32 periodically sends packets (ex: every 50–100 ms).
3) Confirm TCP timestamp option is enabled in lwIP.
4) Verify packets are actually being sent continuously.

They also write a short test program that confirms packets appear on the network.

## Deliverables:

- ESP32 firmware
- documentation on how to flash and run it
- confirmation that timestamps appear in packets

This person mostly writes C++.

# Person B — Packet Capture / Measurement System

This person builds the fingerprinter system that collects packets.

## Responsibilities:

- capture traffic from ESP32 devices
- extract TCP timestamps
- log packet timing data

## Tasks:

Run packet capture on the server or laptop using:

- tcpdump
- Wireshark
- libpcap

Extract these values from packets:

- arrival time
- TCP timestamp
- source IP

Store data in a file such as:

`timestamp_log.csv`

Example log:

```
receive_time, device_id, tcp_timestamp
1713044230.9123,1,12345678
1713044231.0124,1,12345788
```

## Deliverables:

- packet capture scripts
- parsing tool
- dataset used for analysis

This part can be done in Python or C++, but Python with `scapy` or `dpkt` is easiest.

# Person C — Clock Skew Estimation & Graphs

This person implements the core algorithm from Section 4 of the paper.

## Responsibilities:

- compute skew
- generate plots
- analyze results

## Tasks:

1) Load packet data.
2) Compute

$ x_i = t_i - t_1$
​
$w_i = \frac{T_i - T_1}{Hz}$
​
3) Compute offset

$y_i = w_i - x_i$

4) Plot

`offset vs time`

5) Estimate skew slope

$y = αx + β$

6) Compare slopes from different ESP32 devices.

Expected result:

```
Device A → skew +3 ppm
Device B → skew -2 ppm
Device C → skew +1 ppm
```

## Deliverables:

- skew estimation script
- graphs
- explanation of results

This part is easiest in Python with numpy + matplotlib.

# Shared Work (All Three)

The remaining work should be shared:

## Paper explanation

Each person explains one part of the paper in the report.

Example:

```
Person A → theory of clock skew
Person B → packet measurement method
Person C → experimental results
```

## Experiments

All three run the experiment with their ESP32 boards.

Example workflow:

```
ESP32 #1 → State A
ESP32 #2 → State B
ESP32 #3 → State C
```

Server collects packets from all three.

Then compare skew values.

## Final report / presentation

Split the presentation roughly like this:

- Intro & theory
- Implementation
- Results & discussion

Each person presents one section.

# Summary (Balanced Workload)

## Person A

- ESP32 firmware
- network traffic generation

## Person B

- packet capture
- timestamp extraction

## Person C

- skew estimation
- graphs & analysis

Shared:

- experiments
- report
- presentation