#    Copyright 2026 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import annotations

import base64
import secrets

from cryptography.hazmat.primitives.ciphers import aead

KEY_SIZE = 32
NONCE_SIZE = 12


def _validate_key_and_nonce(key: bytes, nonce: bytes) -> None:
    if len(key) != KEY_SIZE:
        raise ValueError(f"Invalid key length {len(key)}. Expected {KEY_SIZE}.")

    if len(nonce) != NONCE_SIZE:
        raise ValueError(f"Invalid nonce length {len(nonce)}. Expected {NONCE_SIZE}.")


def generate_key() -> bytes:
    return secrets.token_bytes(KEY_SIZE)


def generate_nonce() -> bytes:
    return secrets.token_bytes(NONCE_SIZE)


def generate_key_base64() -> tuple[bytes, str]:
    key = generate_key()
    return key, base64.b64encode(key).decode()


def generate_nonce_base64() -> tuple[bytes, str]:
    nonce = generate_nonce()
    return nonce, base64.b64encode(nonce).decode()


def encrypt_chacha20_poly1305(
    key: bytes,
    plaintext: bytes,
    nonce: bytes,
    associated_data: bytes | None = None,
) -> bytes:
    _validate_key_and_nonce(key, nonce)

    cipher = aead.ChaCha20Poly1305(key)
    return cipher.encrypt(nonce, plaintext, associated_data)


def decrypt_chacha20_poly1305(
    key: bytes,
    nonce: bytes,
    ciphertext: bytes,
    associated_data: bytes | None = None,
) -> bytes:
    _validate_key_and_nonce(key, nonce)

    cipher = aead.ChaCha20Poly1305(key)
    return cipher.decrypt(nonce, ciphertext, associated_data)
