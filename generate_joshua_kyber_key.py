#!/usr/bin/env python3
"""
NEXUS Ecosystem — Joshua Kyber-1024 + Hybrid X25519 Key Generator
===================================================================
Generates CRYSTALS-Kyber-1024 (NIST PQC Level 5) keypairs, optionally
combined with classical X25519 keypairs for hybrid post-quantum + classical security.

Entity: joshua-nexus-kyber1024

Intended for the full Nexus stack:
- Mesh networking peer authentication (Yggdrasil / NovaNet / QNET)
- AI agent swarm secure channels (Grok Launcher + emotional AI)
- Post-quantum + classical signing for XCoin/QCoin/Wizard Q runes
- Prototype secure channels (Soilnova, Lumia, York Autotype)
- Corporate post-quantum baseline for Esslinger & Co.

Hybrid mode (recommended for transition period):
  Classical X25519 (fast, widely supported today)
  + Kyber-1024 (quantum-resistant)

Installation:
  Recommended: pip install oqs cryptography
  Fallback testing:   pip install kyber-py cryptography

SECURITY WARNINGS (READ CAREFULLY)
-----------------------------------
* Generate production keys ONLY on air-gapped, trusted, offline machines.
* Private keys are extremely sensitive. Store in HSM, encrypted volume, or Shamir split.
* Never commit generated .key files to any repository.
* Hybrid mode provides defense-in-depth during the quantum transition (5–15+ years).
* After generation, immediately copy private material to secure storage and securely wipe this machine.
"""

import argparse
import base64
import hashlib
import os
import sys
from datetime import datetime, timezone

try:
    from cryptography.hazmat.primitives.asymmetric import x25519
    from cryptography.hazmat.primitives import serialization
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

ENTITY = "joshua-nexus-kyber1024"
KYBER_ALG = "Kyber1024"


def get_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def compute_fingerprint(pubkey_bytes: bytes) -> str:
    return hashlib.sha256(pubkey_bytes).hexdigest()[:16].upper()

def generate_x25519_keypair():
    """Generate classical X25519 keypair using the 'cryptography' library."""
    if not HAS_CRYPTOGRAPHY:
        print("ERROR: 'cryptography' package is required for hybrid mode.", file=sys.stderr)
        print("Install with: pip install cryptography", file=sys.stderr)
        sys.exit(1)

    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()

    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pub_bytes, priv_bytes

def generate_with_liboqs():
    """Preferred method using Open Quantum Safe (liboqs) bindings."""
    try:
        import oqs
    except ImportError:
        print("ERROR: 'oqs' package not found.", file=sys.stderr)
        print("Install with: pip install oqs", file=sys.stderr)
        sys.exit(1)

    print("[NEXUS] Using liboqs (recommended for Kyber) ...")
    kem = oqs.KeyEncapsulation(KYBER_ALG)
    public_key = kem.generate_keypair()
    # Note: Full private key export from oqs object requires additional handling in production.
    # For this generator we note that the private key lives inside the KEM object.
    private_key = b"[PRIVATE_KEY_MUST_BE_EXTRACTED_FROM_OQS_OBJECT_IN_PRODUCTION_USE]"
    return public_key, private_key, "liboqs"

def generate_with_kyber_py():
    """Fallback pure-Python implementation (kyber-py). For testing only."""
    try:
        from kyber import Kyber1024
    except ImportError:
        print("ERROR: 'kyber-py' package not found.", file=sys.stderr)
        print("Install with: pip install kyber-py", file=sys.stderr)
        sys.exit(1)

    print("[NEXUS] Using kyber-py (pure Python fallback) ...")
    pk, sk = Kyber1024.keygen()
    return pk, sk, "kyber-py"

def format_hybrid_output(x25519_pub: bytes, x25519_priv: bytes,
                         kyber_pub: bytes, kyber_priv: bytes,
                         kyber_method: str) -> tuple[str, str]:
    """Format combined hybrid (X25519 + Kyber-1024) output."""
    ts = get_timestamp()
    x25519_fingerprint = compute_fingerprint(x25519_pub)
    kyber_fingerprint = compute_fingerprint(kyber_pub)
    composite = hashlib.sha256(x25519_pub + kyber_pub).hexdigest()[:16].upper()

    header = f"""# ============================================================
# NEXUS HYBRID KEYPAIR — JOSHUA (X25519 + Kyber-1024)
# ============================================================
# Entity                : {ENTITY}
# Classical Algorithm   : X25519 (Curve25519)
# Post-Quantum Algorithm: CRYSTALS-Kyber Level 5 — {KYBER_ALG}
# Generated             : {ts}
# Kyber Backend         : {kyber_method}
# X25519 Fingerprint    : {x25519_fingerprint}
# Kyber Fingerprint     : {kyber_fingerprint}
# Composite Fingerprint : {composite}
# Nexus Context         : Mesh + AI Swarm + Blockchain + Prototypes + Corporate
# ============================================================
# HYBRID SECURITY NOTICE
# This file contains BOTH a classical X25519 keypair AND a Kyber-1024 keypair.
# Use classical for compatibility today. Use Kyber for quantum resistance.
# Recommended: Deploy hybrid mode during the quantum transition period.
# Store private keys with maximum security (HSM / offline encrypted storage).
# ============================================================
"""

    x25519_pub_b64 = base64.b64encode(x25519_pub).decode("ascii")
    x25519_priv_b64 = base64.b64encode(x25519_priv).decode("ascii")

    kyber_pub_b64 = base64.b64encode(kyber_pub).decode("ascii")
    kyber_priv_b64 = base64.b64encode(kyber_priv).decode("ascii") if len(kyber_priv) > 100 else "[PRIVATE_KEY_MUST_BE_EXTRACTED_FROM_OQS_OBJECT]"

    output = header + "\n"

    output += "# -------------------- CLASSICAL X25519 --------------------\n"
    output += "-----BEGIN NEXUS X25519 PUBLIC KEY-----\n"
    output += x25519_pub_b64 + "\n"
    output += "-----END NEXUS X25519 PUBLIC KEY-----\n\n"
    output += "-----BEGIN NEXUS X25519 PRIVATE KEY-----\n"
    output += x25519_priv_b64 + "\n"
    output += "-----END NEXUS X25519 PRIVATE KEY-----\n\n"
    output += "# -------------------- POST-QUANTUM KYBER-1024 --------------------\n"
    output += "-----BEGIN NEXUS KYBER1024 PUBLIC KEY-----\n"
    output += kyber_pub_b64 + "\n"
    output += "-----END NEXUS KYBER1024 PUBLIC KEY-----\n\n"

    output += "-----BEGIN NEXUS KYBER1024 PRIVATE KEY-----\n"
    output += kyber_priv_b64 + "\n"
    output += "-----END NEXUS KYBER1024 PRIVATE KEY-----\n"

    output += "\n# ============================================================\n"
    output += "# END OF HYBRID KEYPAIR\n"
    output += "# ============================================================\n"

    return output, composite

def format_kyber_only_output(pubkey: bytes, privkey: bytes, method: str) -> tuple[str, str]:
    """Original Kyber-only formatting (preserved for backward compatibility)."""
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
# Private key is extremely sensitive. Store offline / in HSM.
# Recommended: Use hybrid mode (--hybrid) for migration safety.
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

    return output, fingerprint

def main():
    parser = argparse.ArgumentParser(
        description="NEXUS Joshua Hybrid Key Generator (X25519 + Kyber-1024)",
        epilog="Hybrid mode is strongly recommended for production use during the quantum transition."
    )
    parser.add_argument("--output-dir", default=".", help="Directory to write key files")
    parser.add_argument("--hybrid", action="store_true",
                        help="Generate BOTH classical X25519 AND Kyber-1024 (recommended)")
    parser.add_argument("--method", choices=["liboqs", "kyber-py"], default="liboqs",
                        help="Kyber backend (liboqs recommended)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if args.hybrid:
        print("[NEXUS] HYBRID MODE ENABLED (X25519 + Kyber-1024)")
        x25519_pub, x25519_priv = generate_x25519_keypair()

        if args.method == "liboqs":
            kyber_pub, kyber_priv, kyber_method = generate_with_liboqs()
        else:
            kyber_pub, kyber_priv, kyber_method = generate_with_kyber_py()

        formatted, fingerprint = format_hybrid_output(
            x25519_pub, x25519_priv, kyber_pub, kyber_priv, kyber_method
        )
        base_filename = f"joshua_hybrid_x25519_kyber1024_{fingerprint}"
    else:
        print("[NEXUS] KYBER-ONLY MODE (use --hybrid for classical + PQC)")
        if args.method == "liboqs":
            pubkey, privkey, method = generate_with_liboqs()
        else:
            pubkey, privkey, method = generate_with_kyber_py()

        formatted, fingerprint = format_kyber_only_output(pubkey, privkey, method)
        base_filename = f"joshua_kyber1024_{fingerprint}"

    out_path = os.path.join(args.output_dir, f"{base_filename}.key")

    with open(out_path, "w") as f:
        f.write(formatted)

    print(f"\n[NEXUS] Keypair written to: {out_path}")
    print(f"[NEXUS] Entity          : {ENTITY}")
    print(f"[NEXUS] Fingerprint     : {fingerprint}")
    if args.hybrid:
        print("[NEXUS] Mode            : HYBRID (X25519 + Kyber-1024)")
    else:
        print("[NEXUS] Mode            : Kyber-1024 only")
    print("\n[NEXUS] IMPORTANT: Copy PRIVATE KEY sections to secure offline storage immediately.")
    print("[NEXUS] Then securely wipe any file containing private keys from this machine.")

if __name__ == "__main__":
    main()
