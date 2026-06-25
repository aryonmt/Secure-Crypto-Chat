"""
Cryptographic module implementing the Strategy Design Pattern.

This module provides an extensible architecture for various classical
encryption algorithms, supporting both English and Persian alphabets.
"""

from abc import ABC, abstractmethod


class BaseCipher(ABC):
    """
    Abstract base class defining the standard interface for all cryptographic ciphers.
    Includes built-in support for English and Persian character sets.
    """

    ENGLISH_ALPHABET_LOWER = "abcdefghijklmnopqrstuvwxyz"
    ENGLISH_ALPHABET_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    PERSIAN_ALPHABET = "ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"

    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        """Encrypt the given plaintext."""
        pass

    @abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt the given ciphertext."""
        pass

    @classmethod
    def _is_supported_char(cls, char: str) -> bool:
        """
        Check if the character belongs to the supported alphabets.
        """
        return (
            char in cls.ENGLISH_ALPHABET_LOWER
            or char in cls.ENGLISH_ALPHABET_UPPER
            or char in cls.PERSIAN_ALPHABET
        )

    @classmethod
    def _shift_character(cls, char: str, shift_amount: int) -> str:
        """
        Core helper method to shift a character by a specified amount.
        Detects the alphabet (English or Persian) and applies the correct modulo.
        Unsupported characters are returned unchanged.
        """
        if char in cls.ENGLISH_ALPHABET_LOWER:
            idx = cls.ENGLISH_ALPHABET_LOWER.index(char)
            return cls.ENGLISH_ALPHABET_LOWER[(idx + shift_amount) % 26]

        if char in cls.ENGLISH_ALPHABET_UPPER:
            idx = cls.ENGLISH_ALPHABET_UPPER.index(char)
            return cls.ENGLISH_ALPHABET_UPPER[(idx + shift_amount) % 26]

        if char in cls.PERSIAN_ALPHABET:
            idx = cls.PERSIAN_ALPHABET.index(char)
            return cls.PERSIAN_ALPHABET[(idx + shift_amount) % 32]

        return char


class CaesarCipher(BaseCipher):
    """
    Implementation of the Caesar Cipher algorithm.
    Shifts characters by a fixed integer amount.
    """

    def __init__(self, shift: int = 3) -> None:
        """Initialize the Caesar cipher with a specific shift value."""
        self.shift = shift

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext using the fixed shift."""
        return "".join(self._shift_character(char, self.shift) for char in plaintext)

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext using the inverse of the fixed shift."""
        return "".join(self._shift_character(char, -self.shift) for char in ciphertext)


class VigenereCipher(BaseCipher):
    """
    Implementation of the Vigenère Cipher algorithm.
    Shifts characters dynamically based on a repeating keyword.
    """

    def __init__(self, key: str = "NETWORK") -> None:
        """Initialize the Vigenère cipher with a specific keyword."""
        self.key = key.upper()

    def _process_text(self, text: str, is_decrypting: bool = False) -> str:
        """
        Unified logic for both encrypting and decrypting text.
        Iterates through the text and applies the appropriate keyword shift.
        """
        result = []
        key_length = len(self.key)
        key_index = 0

        for char in text:
            if self._is_supported_char(char):
                key_char = self.key[key_index % key_length]
                # Fallback to 0 shift if key_char is not a standard English letter
                shift = ord(key_char) - ord("A") if "A" <= key_char <= "Z" else 0

                if is_decrypting:
                    shift = -shift

                result.append(self._shift_character(char, shift))
                key_index += 1
            else:
                result.append(char)

        return "".join(result)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext using the repeating keyword."""
        return self._process_text(plaintext, is_decrypting=False)

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext using the repeating keyword."""
        return self._process_text(ciphertext, is_decrypting=True)
