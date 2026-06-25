"""
UI-Ready Client Module.

Separates Network and Cryptographic logic (Backend) from User Input (Frontend/CLI).
Designed to be easily imported and utilized by GUI frameworks like PyQt or Tkinter.
"""

import argparse
import socket
import ssl
from typing import Any, Optional

from cipher import CaesarCipher, VigenereCipher
from config import BUFFER_SIZE, ENCODING, HOST, PORT
from logger import setup_logger

logger = setup_logger("CLIENT")


class SecureClientBackend:
    """
    Core client logic class managing connections, encryptions, and data transmission.
    """

    def __init__(
        self, host: str, port: int, mode: str, username: str, key: str = "NETWORK"
    ) -> None:
        """
        Initialize the client configuration and select the appropriate cipher mechanism.
        """
        self.host = host
        self.port = port
        self.mode = mode.lower()
        self.username = username
        self.active_socket: Optional[socket.socket] = None
        self.cipher: Optional[Any] = self._initialize_cipher(key)

    def _initialize_cipher(self, key: str) -> Optional[Any]:
        """
        Instantiate the corresponding cryptographic class based on the selected mode.
        """
        if self.mode == "caesar":
            return CaesarCipher()
        if self.mode == "vigenere":
            return VigenereCipher(key=key)
        return None

    def _establish_tls_connection(self, raw_socket: socket.socket) -> None:
        """
        Upgrade the raw socket to a secure TLS connection.
        """
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        self.active_socket = context.wrap_socket(raw_socket, server_hostname=self.host)
        self.active_socket.connect((self.host, self.port))
        logger.info("TLS Connection established.")

    def _establish_classical_connection(self, raw_socket: socket.socket) -> None:
        """
        Establish a raw TCP connection and transmit the protocol identification header.
        """
        self.active_socket = raw_socket
        self.active_socket.connect((self.host, self.port))
        logger.info(
            f"Raw Connection established. Sending '{self.mode}' protocol header."
        )

        header = b"\x01" if self.mode == "caesar" else b"\x02"
        self.active_socket.sendall(header)

    def connect(self) -> None:
        """
        Initiate the connection process based on the selected security mode.
        """
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.mode == "ssl":
            self._establish_tls_connection(raw_socket)
        else:
            self._establish_classical_connection(raw_socket)

    def send_message(self, message: str) -> str:
        """
        Format, encrypt (if applicable), and transmit a message to the server.
        """
        if not self.active_socket:
            raise ConnectionError("Cannot send message: Socket is not connected.")

        formatted_message = f"[{self.username}] says: {message}"

        if self.cipher:
            payload = self.cipher.encrypt(formatted_message)
        else:
            payload = formatted_message

        self.active_socket.sendall(payload.encode(ENCODING))
        logger.debug(f"Payload sent: {payload}")
        return payload

    def receive_message(self) -> str:
        """
        Receive and decrypt (if applicable) an incoming message from the server.
        """
        if not self.active_socket:
            raise ConnectionError("Cannot receive message: Socket is not connected.")

        raw_response = self.active_socket.recv(BUFFER_SIZE).decode(ENCODING)

        if self.cipher:
            return self.cipher.decrypt(raw_response)

        return raw_response

    def disconnect(self) -> None:
        """
        Safely terminate the active socket connection.
        """
        if self.active_socket:
            self.active_socket.close()
            self.active_socket = None
            logger.info("Disconnected from server.")


# ==============================================================================
# Command Line Interface (CLI) Execution Block
# This section is isolated and only runs when the script is executed directly.
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Secure Chat Client CLI")
    parser.add_argument("--host", default=HOST, help="Target Server IP Address")
    parser.add_argument("--port", type=int, default=PORT, help="Target Server Port")
    parser.add_argument(
        "--mode",
        choices=["caesar", "vigenere", "ssl"],
        required=True,
        help="Encryption Protocol Mode",
    )
    parser.add_argument("--user", required=True, help="Display Username")
    parser.add_argument(
        "--key", default="NETWORK", help="Keyword for Vigenère Cipher (Optional)"
    )

    args = parser.parse_args()
    client = SecureClientBackend(args.host, args.port, args.mode, args.user, args.key)

    try:
        client.connect()
        while True:
            user_input = input(f"[{args.user}] Message: ")
            if user_input.lower() == "quit":
                break

            client.send_message(user_input)
            server_reply = client.receive_message()
            logger.info(f"Server reply: {server_reply}")

    except KeyboardInterrupt:
        logger.warning("Session terminated manually by user.")
    except ConnectionRefusedError:
        logger.error("Connection failed. Ensure the server is currently running.")
    except Exception as e:
        logger.error(f"An unexpected runtime error occurred: {e}")
    finally:
        client.disconnect()
