# ESP32 Fingerprintee

ESP32 firmware that connects to a WiFi network and sends periodic TCP packets to a server. Designed as the fingerprintee side of a TCP clock skew-based device fingerprinting experiment.

## Requirements

- [ESP-IDF v6.0](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/index.html)
- ESP32 board

## Setup

1. Clone the repo and navigate to this folder:
   ```bash
   cd station
   ```

2. Set up the ESP-IDF environment:
   ```bash
   source "~/.espressif/tools/activate_idf_<version>.sh"
   ```
   Or open the folder in VS Code using the ESP-IDF extension terminal.

3. Set the target:
   ```bash
   idf.py set-target esp32
   ```

4. Configure credentials and server:
   ```bash
   idf.py menuconfig
   ```
   Under **Example Configuration**, set:
   - WiFi SSID
   - WiFi Password
   - Server IP Address
   - Server Port

5. Flash and monitor:
   ```bash
   idf.py -p /dev/ttyACM0 flash monitor
   ```
   Replace `/dev/ttyACM0` with your actual port.
