import socket

def start_dummy_router(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(1)
    print(f"[Router {port}] Listening on port {port}...")

    conn, addr = server_socket.accept()
    print(f"[Router {port}] Connected by {addr}")

    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"[Router {port}] Received:", data.decode())

    conn.close()
    server_socket.close()

if __name__ == "__main__":
    start_dummy_router(8002)  # or 8004, etc.
