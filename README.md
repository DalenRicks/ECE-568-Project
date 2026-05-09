# Hardware-Based Identity Verification for Embedded Systems
Spring 2026 Purdue ECE 56800

### Michael Antabian, Husam Chekfa, (Lead) Dalen Ricks

This project aims to identify devices connected to a Wi-Fi network by measuring the device's clock skew. This is an implementation of a research paper that was used as a reference for the WSN clock skew identification paper that we read for reading 2. The project will use an ESP32 to listen to packets on a Wi-Fi network and calculate the clock skew by looking a the TCP packet header. Once the clock skew is calculated, it will save the value with the reported MAC address, which can later be used to compare against incoming packets. The goal of the project is to have a low-power, low-cost network monitor that can raise an alarm when bad actors attempt to impersonate an authenticated device.