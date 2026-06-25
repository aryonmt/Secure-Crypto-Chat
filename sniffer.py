"""
Advanced Sniffer module optimized for Windows Loopback capture.

This module utilizes Daemon Threading to monitor network traffic
on a specified port without blocking the main execution thread,
ensuring graceful termination via keyboard interrupts.
"""

import threading
import time

from scapy.all import IP, TCP, conf, sniff
from scapy.packet import Packet

from config import ENCODING, PORT
from logger import setup_logger

logger = setup_logger("SNIFFER")


def _extract_ip_addresses(packet: Packet) -> tuple[str, str]:
    """
    Extract source and destination IP addresses from a given packet.
    Returns 'Local' if the IP layer is absent.
    """
    src_ip = packet[IP].src if packet.haslayer(IP) else "Local"
    dst_ip = packet[IP].dst if packet.haslayer(IP) else "Local"
    return src_ip, dst_ip


def _decode_payload(raw_payload: bytes) -> str:
    """
    Attempt to decode raw payload bytes into a human-readable string.
    Returns a warning string if the payload is encrypted or binary data.
    """
    try:
        return raw_payload.decode(ENCODING)
    except UnicodeDecodeError:
        return "<Encrypted/Binary TLS Data - Unreadable>"


def packet_callback(packet: Packet) -> None:
    """
    Callback function triggered for each intercepted packet.
    Filters packets by port, extracts the payload, and displays the content.
    """
    if not (packet.haslayer(TCP) and packet.haslayer("Raw")):
        return

    if packet[TCP].sport != PORT and packet[TCP].dport != PORT:
        return

    raw_payload = packet["Raw"].load
    src_ip, dst_ip = _extract_ip_addresses(packet)
    decoded_text = _decode_payload(raw_payload)

    logger.warning(f"Intercepted Packet: {src_ip} -> {dst_ip}")
    logger.debug(f"Raw Bytes: {raw_payload}")
    logger.info(f"Decoded Text: {decoded_text}")


def run_sniffer_in_background() -> None:
    """
    Background worker function executing the packet capture loop.
    Captures loopback traffic specifically for local testing environments.
    """
    try:
        loopback_interface = conf.loopback_name
        sniff(
            iface=loopback_interface,
            filter=f"tcp port {PORT}",
            prn=packet_callback,
            store=0,
        )
    except OSError:
        logger.error(
            "OS Error: WinPcap/Npcap is not configured to capture loopback traffic."
        )
    except Exception as e:
        logger.error(f"Sniffer runtime error: {e}")


def start_sniffing() -> None:
    """
    Initialize and launch the sniffer thread, keeping the main thread
    alive to handle user interrupts gracefully.
    """
    logger.info(f"Starting Sniffer on Port {PORT}...")

    try:
        logger.info(f"Forcing capture on interface: {conf.loopback_name}")
    except Exception:
        logger.warning("Could not auto-detect loopback. Using default interfaces.")

    logger.info("Press Ctrl+C to stop.")

    sniffer_thread = threading.Thread(target=run_sniffer_in_background, daemon=True)
    sniffer_thread.start()

    try:
        while sniffer_thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.warning("Sniffer stopped instantly by user (Ctrl+C).")


if __name__ == "__main__":
    start_sniffing()
