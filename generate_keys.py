"""
Module to generate self-signed RSA certificates and private keys.

This script handles the creation of cryptographic assets required
for establishing secure SSL/TLS connections within the network.
"""

import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from config import CERT_FILE, KEY_FILE
from logger import setup_logger

logger = setup_logger("KEY_GENERATOR")


def _generate_rsa_private_key() -> rsa.RSAPrivateKey:
    """
    Generate a secure RSA private key (2048-bit).
    """
    logger.info("Generating 2048-bit RSA private key...")
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


def _build_certificate(private_key: rsa.RSAPrivateKey) -> x509.Certificate:
    """
    Build and sign a self-signed x509 certificate using the provided private key.
    """
    logger.info("Building self-signed x509 certificate...")

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "University Crypto Project"),
            x509.NameAttribute(NameOID.COMMON_NAME, "127.0.0.1"),
        ]
    )

    valid_from = datetime.datetime.utcnow()
    valid_to = valid_from + datetime.timedelta(days=365)

    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(valid_from)
        .not_valid_after(valid_to)
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )


def _save_private_key(private_key: rsa.RSAPrivateKey, file_path: str) -> None:
    """
    Serialize and save the RSA private key to the disk in PEM format.
    """
    with open(file_path, "wb") as key_file:
        key_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    logger.debug(f"Private key securely saved to '{file_path}'.")


def _save_certificate(cert: x509.Certificate, file_path: str) -> None:
    """
    Serialize and save the x509 certificate to the disk in PEM format.
    """
    with open(file_path, "wb") as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
    logger.debug(f"Certificate securely saved to '{file_path}'.")


def generate_self_signed_cert() -> None:
    """
    Main orchestration function to generate and save the private key and certificate.
    """
    try:
        private_key = _generate_rsa_private_key()
        certificate = _build_certificate(private_key)

        _save_private_key(private_key, KEY_FILE)
        _save_certificate(certificate, CERT_FILE)

        logger.info(
            f"Successfully generated cryptographic assets: '{KEY_FILE}' and '{CERT_FILE}'."
        )
    except Exception as error:
        logger.error(f"Failed to generate cryptographic keys: {error}")


if __name__ == "__main__":
    generate_self_signed_cert()
