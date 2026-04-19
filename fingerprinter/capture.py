import argparse
import csv
import time
from scapy.all import sniff, TCP, IP

pairs = []


def extract_timestamp(packet):
    if not packet.haslayer(TCP):
        return None

    tcp = packet[TCP]
    for option in tcp.options:
        if option[0] == 'Timestamp':
            tsval = option[1][0]
            arrival_time = time.time()
            return (arrival_time, tsval)

    return None


def handle_packet(packet):
    result = extract_timestamp(packet)
    if result:
        pairs.append(result)
        print(f"[{len(pairs)}] arrival={result[0]:.6f}  tsval={result[1]}")


def capture(src_ip, output_file, duration=None, count=None):
    filter_str = f"tcp and src host {src_ip}"
    print(f"Capturing from {src_ip} -> {output_file}")
    if duration:
        print(f"Duration: {duration}s")
    if count:
        print(f"Max packets: {count}")

    sniff(filter=filter_str, prn=handle_packet, timeout=duration, count=count or 0)

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['arrival_time', 'tsval'])
        writer.writerows(pairs)

    print(f"\nSaved {len(pairs)} pairs to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture TCP timestamps from ESP32")
    parser.add_argument('--src-ip', required=True, help="ESP32 IP address to filter on")
    parser.add_argument('--output', default='timestamps.csv', help="Output CSV file (default: timestamps.csv)")
    parser.add_argument('--duration', type=float, help="Capture duration in seconds")
    parser.add_argument('--count', type=int, help="Max number of packets to capture")
    args = parser.parse_args()

    if not args.duration and not args.count:
        parser.error("At least one of --duration or --count must be specified")

    capture(args.src_ip, args.output, duration=args.duration, count=args.count)
