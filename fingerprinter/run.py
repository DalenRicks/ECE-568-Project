import subprocess
import sys
import os
import argparse

VENV_DIR = os.path.join(os.path.expanduser("~"), "fingerprinter-env")

def main():
    parser = argparse.ArgumentParser(description="Run the fingerprinter capture script")
    parser.add_argument('--src-ip', required=True, help="ESP32 IP address to filter on")
    parser.add_argument('--output', default='timestamps.csv', help="Output CSV file (default: timestamps.csv)")
    parser.add_argument('--duration', type=float, help="Capture duration in seconds")
    parser.add_argument('--count', type=int, help="Max number of packets to capture")
    args = parser.parse_args()

    if not args.duration and not args.count:
        parser.error("At least one of --duration or --count must be specified")

    if sys.platform == "win32":
        python = os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        python = os.path.join(VENV_DIR, "bin", "python3")

    if not os.path.exists(python):
        print("Virtual environment not found. Run 'python3 setup.py' first.")
        sys.exit(1)

    capture_script = os.path.join(os.path.dirname(__file__), "capture.py")

    cmd = [python, capture_script]
    cmd += ["--src-ip", args.src_ip]
    cmd += ["--output", args.output]
    if args.duration:
        cmd += ["--duration", str(args.duration)]
    if args.count:
        cmd += ["--count", str(args.count)]

    if sys.platform != "win32":
        cmd = ["sudo"] + cmd

    subprocess.run(cmd)

    if sys.platform != "win32":
        subprocess.run(["sudo", "chown", os.environ["USER"], args.output])

if __name__ == "__main__":
    main()
