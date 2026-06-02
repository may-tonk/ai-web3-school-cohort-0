"""Chain identifier helpers for external APIs."""

from __future__ import annotations


DEXSCREENER_CHAIN_IDS = {
    "bnb": "bsc",
    "bsc": "bsc",
}

GOPLUS_CHAIN_IDS = {
    "bnb": "56",
    "bsc": "56",
}

HONEYPOT_CHAIN_IDS = {
    "bnb": "56",
    "bsc": "56",
}

NANSEN_CHAIN_IDS = {
    "bnb": "bnb",
    "bsc": "bnb",
}


def dexscreener_chain_id(chain: str) -> str:
    key = chain.lower()
    if key not in DEXSCREENER_CHAIN_IDS:
        raise RuntimeError(f"Unsupported DexScreener chain: {chain}")
    return DEXSCREENER_CHAIN_IDS[key]


def goplus_chain_id(chain: str) -> str:
    key = chain.lower()
    if key not in GOPLUS_CHAIN_IDS:
        raise RuntimeError(f"Unsupported GoPlus chain: {chain}")
    return GOPLUS_CHAIN_IDS[key]


def honeypot_chain_id(chain: str) -> str:
    key = chain.lower()
    if key not in HONEYPOT_CHAIN_IDS:
        raise RuntimeError(f"Unsupported Honeypot.is chain: {chain}")
    return HONEYPOT_CHAIN_IDS[key]


def nansen_chain_id(chain: str) -> str:
    key = chain.lower()
    if key not in NANSEN_CHAIN_IDS:
        raise RuntimeError(f"Unsupported Nansen chain: {chain}")
    return NANSEN_CHAIN_IDS[key]
