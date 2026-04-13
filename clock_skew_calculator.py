import sys

def calculate_clock_skew(nominal_freq_hz, measured_freq_hz, elapsed_seconds):
    """
    Calculate clock skew in parts per million (ppm) and total time drift.

    Args:
        nominal_freq_hz (float): Nominal oscillator frequency in Hz.
        measured_freq_hz (float): Measured oscillator frequency in Hz.
        elapsed_seconds (float): Elapsed time in seconds.

    Returns:
        tuple: (skew_ppm, drift_seconds)
    """
    if nominal_freq_hz <= 0 or measured_freq_hz <= 0 or elapsed_seconds < 0:
        raise ValueError("Frequencies must be > 0 and elapsed time >= 0.")

    # Calculate skew in ppm
    skew_ppm = ((measured_freq_hz - nominal_freq_hz) / nominal_freq_hz) * 1_000_000

    # Calculate total drift over elapsed time
    drift_seconds = (skew_ppm / 1_000_000) * elapsed_seconds

    return skew_ppm, drift_seconds


if __name__ == "__main__":
    crystal_frequency = 32768

    try:
        # Example input (this would be data from the wireshark capture)
        measured = float(input("Enter measured frequency (Hz): ").strip())
        elapsed = float(input("Enter elapsed time (seconds): ").strip())

        skew_ppm, drift_sec = calculate_clock_skew(crystal_frequency, measured, elapsed)

        print(f"\nClock Skew: {skew_ppm:.3f} ppm")
        # print(f"Total Drift over {elapsed} seconds: {drift_sec:.6f} seconds")

    except ValueError as e:
        print(f"Input error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
