"""
Configuration module for network and security settings.

This module dynamically defines the network parameters, encoding standards,
and file paths required for SSL/TLS certificates across the entire application.
"""

import socket

# Dynamically resolve the host IP address based on the local machine's hostname
HOST: str = socket.gethostbyname(socket.gethostname())

# Network communication constants
PORT: int = 5050
BUFFER_SIZE: int = 1024
ENCODING: str = "utf-8"

# Cryptographic asset paths for TLS connections
CERT_FILE: str = "cert.pem"
KEY_FILE: str = "key.pem"
