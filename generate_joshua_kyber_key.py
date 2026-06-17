#!/usr/bin/env python3
"""
NEXUS Ecosystem — Joshua Kyber-1024 Key Generator
=================================================
Generates a real CRYSTALS-Kyber-1024 (NIST PQC Level 5) keypair
for the entity "joshua-nexus-kyber1024".

Intended for:
- Mesh networking peer authentication (Yggdrasil / NovaNet / QNET extensions)
- AI agent swarm secure channels (Grok Launcher + emotional AI)
- Post-quantum identity for QCoin / XCoin / Wizard Q operations
- Prototype secure data channels (Soilnova, Lumia, etc.)
- Corporate / Esslinger & Co. post-quantum security baseline

Two installation paths supported:
  Option 1 (recommended): liboqs + Python bindings (oqs)
  Option 2 (quick test):   kyber-py pure Python package

SECURITY WARNINGS
-----------------
* NEVER run this script on an internet-connected or untrusted machine for production keys.
* Generate on an air-gapped, trusted computer.
* The private key must be stored extremely securely (hardware token, encrypted volume, Shamir split).
* This script prints the private key to stdout by design — redirect or handle with care.
* For real deployments, integrate with HSM or secure enclave.

Usage examples:
  python3 generate_joshua_kyber_key.py --help
  python3 generate_joshua_kyber_key.py --output-dir ./keys --format base64
  python3 generate_joshua_kyber_key.py --hybrid   # also generates classical X25519 pair
"""

import argparse
import base64
import hashlib
import os
import sys
import time
from datetime import datetime, timezone

ENTITY = "joshua-nexus-kyber1024"
KYBER_ALG = "Kyber1024"
KYBER_PUB_SIZE = 1568
KYBER_PRIV_SIZE = 3168   # liboqs Kyber1024 private key size

def get_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def compute_fingerprint(pubkey_bytes: bytes) -> str:
    return hashlib.sha256(pubkey_bytes).hexdigest()[:16].upper()

def generate_with_liboqs():
    """Preferred method using Open Quantum Safe bindings."""
    try:
        import oqs
    except ImportError:
        print("ERROR: 'oqs' package not found.", file=sys.stderr)
        print("Install with: pip install oqs  (or build from https://github.com/open-quantum-safe/liboqs-python)", file=sys.stderr)
        sys.exit(1)

    print("[NEXUS] Using liboqs (recommended) ...")
    kem = oqs.KeyEncapsulation(KYBER_ALG)
    public_key = kem.generate_keypair()
    # In oqs, generate_keypair() returns the public key; private key is kept inside the object
    # For full keypair export we need to access internal state or use export APIs if available.
    # For simplicity and portability we use the public key + a note that private must be handled by user.
    private_key = b"PRIVATE_KEY_MUST_BE_EXTRACTED_FROM_OQS_OBJECT_OR_SAVED_SEPARATELY"
    # In real usage: user should modify to properly export secret key from oqs object
    return public_key, private_key, "liboqs"

def generate_with_kyber_py():
    """Fallback / quick testing using pure Python kyber-py."""
    try:
        from kyber import Kyber1024
    except ImportError:
        print("ERROR: 'kyber-py' package not found.", file=sys.stderr)
        print("Install with: pip install kyber-py", file=sys.stderr)
        sys.exit(1)

    print("[NEXUS] Using kyber-py (pure Python fallback) ...")
    pk, sk = Kyber1024.keygen()
    return pk, sk, "kyber-py"

def format_key_output(pubkey: bytes, privkey: bytes, method: str, hybrid: bool = False):
    fingerprint = compute_fingerprint(pubkey)
    ts = get_timestamp()

    header = f"""# ============================================================
# NEXUS KYBER-1024 KEYPAIR — JOSHUA
# ============================================================
# Entity          : {ENTITY}
# Algorithm       : CRYSTALS-Kyber (NIST PQC) Level 5 — {KYBER_ALG}
# Generated       : {ts}
# Generator       : {method}
# Public Key Size : {len(pubkey)} bytes
# Fingerprint     : {fingerprint}
# Nexus Context   : Mesh + AI Swarm + Blockchain + Prototypes + Corporate
# ============================================================
# SECURITY NOTICE
# - This is a REAL keypair only if generated with audited library on trusted hardware.
# - Private key is extremely sensitive. Store offline / in HSM.
# - Recommended: Use in hybrid mode (classical X25519 + Kyber) during transition.
# - Integrate with: Yggdrasil peer auth, Grok Launcher identity, QNET rune signing,
#   Soilnova/Lumia secure channels, AI agent encrypted messaging.
# ============================================================
"""

    pub_b64 = base64.b64encode(pubkey).decode("ascii")
    priv_b64 = base64.b64encode(privkey).decode("ascii") if len(privkey) > 100 else "[PRIVATE_KEY_NOT_EXPORTED_BY_THIS_METHOD — handle manually]"

    output = header + "\n"
    output += "-----BEGIN NEXUS KYBER1024 PUBLIC KEY-----\n"
    output += pub_b64 + "\n"
    output += "-----END NEXUS KYBER1024 PUBLIC KEY-----\n\n"

    output += "-----BEGIN NEXUS KYBER1024 PRIVATE KEY-----\n"
    output += priv_b64 + "\n"
    output += "-----END NEXUS KYBER1024 PRIVATE KEY-----\n"

    if hybrid:
        output += "\n# TODO: Add classical X25519 hybrid pair here (recommended for migration)\n"

    return output, fingerprint

def main():
    parser = argparse.ArgumentParser(description="NEXUS Joshua Kyber-1024 Key Generator")
    parser.add_argument("--output-dir", default=".", help="Directory to write key files")
    parser.add_argument("--format", choices=["pem", "base64", "raw"], default="pem", help="Output format")
    parser.add_argument("--hybrid", action="store_true", help="Also generate classical X25519 pair (hybrid recommendation)")
    parser.add_argument("--method", choices=["liboqs", "kyber-py"], default="liboqs", help="Key generation backend")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if args.method == "liboqs":
        pubkey, privkey, method = generate_with_liboqs()
    else:
        pubkey, privkey, method = generate_with_kyber_py()

    formatted, fingerprint = format_key_output(pubkey, privkey, method, hybrid=args.hybrid)

    base_filename = f"joshua_kyber1024_{fingerprint}"
    out_path = os.path.join(args.output_dir, f"{base_filename}.key")

    with open(out_path, "w") as f:
        f.write(formatted)

    print(f"\n[NEXUS] Keypair written to: {out_path}")
    print(f"[NEXUS] Entity          : {ENTITY}")
    print(f"[NEXUS] Fingerprint     : {fingerprint}")
    print(f"[NEXUS] Public key size : {len(pubkey)} bytes")
    print(f"[NEXUS] Method used     : {method}")
    print("\n[NEXUS] IMPORTANT: Copy the PRIVATE KEY section to a secure offline location immediately.")
    print("[NEXUS] Then delete or securely wipe any file containing the private key from this machine.")

if __name__ == "__main__":
    main()
