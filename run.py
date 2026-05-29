from app import create_app
import os
import socket


def get_available_port(start_port):
    port = start_port
    while port <= start_port + 20:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
    return start_port

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    default_port = int(os.getenv('PORT', '5000'))
    if os.getenv('WERKZEUG_RUN_MAIN') == 'true':
        port = default_port
    else:
        port = get_available_port(default_port)
        if port != default_port:
            print(f"Port {default_port} is in use, falling back to {port}")
        os.environ['PORT'] = str(port)
    app.run(debug=True, host='0.0.0.0', port=port)
