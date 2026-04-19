import socket
import argparse


def start_server(host, port):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)
    print(f"Server listening on {host}:{port}")

    conn, addr = server_sock.accept()
    print(f"Connected: {addr}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print("Client disconnected.")
                break
            print(f"Received: {data.decode().strip()}")
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        conn.close()
        server_sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple TCP server for ESP32 fingerprinting")
    parser.add_argument('--host', default='0.0.0.0', help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument('--port', type=int, default=12345, help="Port to listen on (default: 12345)")
    args = parser.parse_args()

    start_server(args.host, args.port)
