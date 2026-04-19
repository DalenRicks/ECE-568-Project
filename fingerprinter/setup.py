import subprocess
import sys
import os

VENV_DIR = os.path.join(os.path.expanduser("~"), "fingerprinter-env")

def main():
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)

    pip = os.path.join(VENV_DIR, "Scripts" if sys.platform == "win32" else "bin", "pip")

    print("Installing scapy...")
    subprocess.run([pip, "install", "scapy"], check=True)

    print("\nSetup complete.")
    print("Run 'python3 run.py --src-ip <ESP32_IP> --duration <seconds>' to start capturing.")

if __name__ == "__main__":
    main()
