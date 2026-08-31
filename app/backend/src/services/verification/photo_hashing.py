"""Image hashing for uploaded fire reports"""

import hashlib


def hash_photo(file_bytes: bytes) -> str:
    """Computes SHA-256 hex of raw image bytes"""
    return hashlib.sha256(file_bytes).hexdigest()
