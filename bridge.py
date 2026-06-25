"""
WebSocket Bridge Module.

Acts as a middleware bridging the Vue.js web frontend (via WebSocket)
to the underlying raw TCP/SSL SmartServer.
"""

import asyncio
import json
from typing import Any, Dict

import websockets
from websockets.server import ServerConnection

from client import SecureClientBackend
from logger import setup_logger

logger = setup_logger("BRIDGE")


class ClientBridge:
    """
    Manages the bidirectional communication between the web frontend
    and the secure TCP backend.
    """

    def __init__(self, websocket: ServerConnection) -> None:
        """Initialize the bridge with an active WebSocket connection."""
        self.websocket = websocket
        self.client_backend: SecureClientBackend | None = None
        self.is_running = True

    async def _listen_to_tcp(self) -> None:
        """
        Continuously listen for incoming messages from the TCP server
        and forward them to the WebSocket client.
        """
        loop = asyncio.get_running_loop()
        while (
            self.is_running
            and self.client_backend
            and self.client_backend.active_socket
        ):
            try:
                reply = await loop.run_in_executor(
                    None, self.client_backend.receive_message
                )
                if reply:
                    response_payload = {
                        "type": "message",
                        "sender": "Server",
                        "text": reply,
                    }
                    await self.websocket.send(json.dumps(response_payload))
            except Exception as e:
                logger.warning(f"TCP Listener stopped: {e}")
                self.is_running = False
                break

    def _initialize_backend(self, config: Dict[str, Any]) -> None:
        """
        Initialize and connect the secure TCP client backend based on the
        provided configuration from the frontend.
        """
        logger.info(f"Connecting to Backend with config: {config}")
        self.client_backend = SecureClientBackend(
            host=config["host"].strip(),
            port=int(config["port"]),
            mode=config["mode"],
            username=config["username"].strip(),
            key=config.get("key", "NETWORK").strip(),
        )
        self.client_backend.connect()

    async def _process_client_messages(self) -> None:
        """
        Process incoming WebSocket messages from the Vue.js frontend
        and forward them to the TCP server.
        """
        async for message in self.websocket:
            data = json.loads(message)

            if data.get("type") == "send_chat":
                raw_payload = self.client_backend.send_message(data["text"])

                sniffer_payload = {
                    "type": "sniffer",
                    "raw_payload": str(raw_payload),
                }
                await self.websocket.send(json.dumps(sniffer_payload))

    async def handle_communication(self) -> None:
        """
        Main handler orchestrating the setup, connection, and message loops.
        """
        try:
            config_msg = await self.websocket.recv()
            config = json.loads(config_msg)

            self._initialize_backend(config)
            await self.websocket.send(
                json.dumps({"type": "status", "msg": "connected"})
            )

            asyncio.create_task(self._listen_to_tcp())
            await self._process_client_messages()

        except websockets.exceptions.ConnectionClosed:
            logger.info("Browser disconnected from bridge.")
        except Exception as e:
            logger.error(f"Bridge Error: {e}")
            await self.websocket.send(json.dumps({"type": "error", "msg": str(e)}))
        finally:
            self.is_running = False
            if self.client_backend:
                self.client_backend.disconnect()


async def bridge_handler(websocket: ServerConnection) -> None:
    """
    Entry point handler for new WebSocket connections.
    """
    bridge = ClientBridge(websocket)
    await bridge.handle_communication()


async def main() -> None:
    """
    Initialize and run the WebSocket server bridge.
    """
    logger.info("Starting WebSocket Bridge on ws://localhost:8765")
    async with websockets.serve(bridge_handler, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
