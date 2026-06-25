"""
Concurrent Smart Server module with Logging and Dynamic Protocol Routing.

This module provides a multi-threaded server capable of handling multiple
simultaneous clients, routing them dynamically based on their requested
protocol (TLS, Caesar, or Vigenère).
"""

import socket
import ssl
import threading
from typing import Any, Optional, Tuple

from cipher import CaesarCipher, VigenereCipher
from config import BUFFER_SIZE, CERT_FILE, ENCODING, HOST, KEY_FILE, PORT
from logger import setup_logger

logger = setup_logger("SERVER")


class SmartServer:
    """
    A multi-threaded server that dynamically handles both TLS and classical
    cryptographic connections.
    """

    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        """
        Initialize the SmartServer with the specified host and port.
        """
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def _peek_first_byte(self, conn: socket.socket) -> bytes:
        """
        Peek the first byte from the socket buffer without consuming it.
        """
        first_byte = b""
        while True:
            try:
                first_byte = conn.recv(1, socket.MSG_PEEK)
                break
            except socket.timeout:
                pass
        return first_byte

    def _setup_tls_context(self, conn: socket.socket) -> ssl.SSLSocket:
        """
        Wrap the raw socket in an SSL context for TLS connections.
        """
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
        secure_conn = context.wrap_socket(conn, server_side=True)
        secure_conn.settimeout(1.0)
        return secure_conn

    def _process_tls_communication(
        self, secure_conn: ssl.SSLSocket, addr: Tuple[str, int]
    ) -> None:
        """
        Handle the continuous communication loop for a TLS encrypted client.
        """
        while True:
            try:
                data = secure_conn.recv(BUFFER_SIZE)
                if not data:
                    break
                logger.debug(f"[{addr}] Secure Payload: {data.decode(ENCODING)}")
                secure_conn.sendall("TLS verified.".encode(ENCODING))
            except socket.timeout:
                continue

    def _get_cipher_instance(
        self, header: bytes, addr: Tuple[str, int]
    ) -> Optional[Any]:
        """
        Determine and return the appropriate cipher instance based on the protocol header.
        """
        if header == b"\x01":
            logger.info(f"[{addr}] Protocol: Caesar Cipher")
            return CaesarCipher()
        elif header == b"\x02":
            logger.info(f"[{addr}] Protocol: Vigenère Cipher")
            return VigenereCipher(key="NETWORK")

        logger.error(f"[{addr}] Unknown protocol header.")
        return None

    def _process_classical_communication(
        self, conn: socket.socket, addr: Tuple[str, int], cipher: Any
    ) -> None:
        """
        Handle the continuous communication loop for a classical cipher client.
        """
        while True:
            try:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break

                encrypted_message = data.decode(ENCODING)
                logger.debug(f"[{addr}] Raw bytes (Encrypted): {encrypted_message}")
                logger.info(
                    f"[{addr}] Decrypted Message: {cipher.decrypt(encrypted_message)}"
                )

                encrypted_response = cipher.encrypt("Message Received Safely!")
                conn.sendall(encrypted_response.encode(ENCODING))
            except socket.timeout:
                continue

    def handle_client(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """
        Main entry point for handling an individual client connection in a dedicated thread.
        """
        logger.info(f"Thread started for client: {addr}")
        secure_conn = None

        try:
            conn.settimeout(1.0)
            first_byte = self._peek_first_byte(conn)

            if not first_byte:
                logger.warning(f"Client {addr} disconnected before sending header.")
                return

            if first_byte == b"\x16":
                logger.info(f"[{addr}] Protocol: SSL/TLS Handshake")
                secure_conn = self._setup_tls_context(conn)
                self._process_tls_communication(secure_conn, addr)
            else:
                protocol_header = conn.recv(1)
                cipher = self._get_cipher_instance(protocol_header, addr)

                if not cipher:
                    return

                self._process_classical_communication(conn, addr, cipher)

        except Exception as e:
            logger.error(f"[{addr}] Connection dropped: {e}")
        finally:
            if secure_conn:
                secure_conn.close()
            elif conn:
                conn.close()
            logger.info(f"[{addr}] Session closed. Thread terminating.")

    def _accept_clients_loop(self) -> None:
        """
        Continuously accept new incoming client connections and spawn handler threads.
        """
        while True:
            try:
                conn, addr = self.server_socket.accept()
            except socket.timeout:
                continue

            logger.info(f"New connection accepted from {addr}")

            client_thread = threading.Thread(
                target=self.handle_client, args=(conn, addr), daemon=True
            )
            client_thread.start()

            active_users = threading.active_count() - 1
            logger.info(f"Active clients connected: {active_users}")

    def start(self) -> None:
        """
        Bind the server socket, start listening, and initiate the connection loop.
        """
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1.0)

        logger.info(f"Server securely listening on {self.host}:{self.port}")
        logger.info("Press Ctrl+C to shut down gracefully.")

        try:
            self._accept_clients_loop()
        except KeyboardInterrupt:
            logger.warning("Shutdown signal received.")
        finally:
            self.server_socket.close()
            logger.info("Server terminated.")


if __name__ == "__main__":
    server = SmartServer()
    server.start()
