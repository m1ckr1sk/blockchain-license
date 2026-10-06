from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash_block(block: dict[str, Any]) -> str:
    payload = json.dumps(block, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class BlockchainService:
    """Minimal blockchain ledger with chain integrity validation."""

    def __init__(self) -> None:
        self.chain: list[dict[str, Any]] = []
        self.peers: dict[str, list[dict[str, Any]]] = {}
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        genesis = {
            "index": 0,
            "timestamp": _utc_timestamp(),
            "previous_hash": "",
            "event": {"type": "GENESIS", "details": "Initial ledger state"},
        }
        genesis["hash"] = _hash_block(genesis)
        self.chain.append(genesis)

    def add_block(self, event: dict[str, Any]) -> dict[str, Any]:
        previous_hash = self.chain[-1]["hash"]
        block = {
            "index": len(self.chain),
            "timestamp": _utc_timestamp(),
            "previous_hash": previous_hash,
            "event": event,
        }
        block["hash"] = _hash_block(block)
        self.chain.append(block)
        return block

    def tamper_chain(self) -> dict[str, Any]:
        """Intentionally mutate a block to demonstrate tamper detection in the demo."""
        if not self.chain:
            return {"valid": False, "block_count": 0, "blocks": [], "message": "Chain is empty."}

        target = self.chain[1] if len(self.chain) > 1 else self.chain[0]
        target["event"] = {**target.get("event", {}), "type": "TAMPERED_EVENT", "details": "Intentional tampering demonstration"}
        return self.validate_chain()

    def register_peer(self, name: str, chain: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        if not name:
            raise ValueError("Peer name is required.")

        if chain is None:
            chain = [self.chain[0]]

        self.peers[name] = list(chain)
        return {"name": name, "chain_length": len(self.peers[name]), "status": "registered"}

    def sync_with_peer(self, peer_name: str) -> dict[str, Any]:
        peer_chain = self.peers.get(peer_name)
        if peer_chain is None:
            raise KeyError(f"Peer {peer_name} not found.")

        peer_validation = self.validate_chain(peer_chain)
        if not peer_validation["valid"]:
            return {"peer": peer_name, "adopted": False, "reason": "Peer chain is invalid."}

        if len(peer_chain) <= len(self.chain):
            return {"peer": peer_name, "adopted": False, "reason": "Peer chain is not longer than the local chain."}

        self.chain = list(peer_chain)
        return {"peer": peer_name, "adopted": True, "chain_length": len(self.chain), "message": "Local chain replaced with valid peer chain."}

    def reconcile_with_peers(self) -> dict[str, Any]:
        if not self.peers:
            raise ValueError("No peers registered.")

        local_validation = self.validate_chain()
        local_is_valid = local_validation["valid"]

        best_peer_name: str | None = None
        best_peer_chain: list[dict[str, Any]] | None = None

        for peer_name, peer_chain in self.peers.items():
            if not self.validate_chain(peer_chain)["valid"]:
                continue

            if best_peer_chain is None or len(peer_chain) > len(best_peer_chain):
                best_peer_name = peer_name
                best_peer_chain = peer_chain

        if best_peer_chain is None:
            return {
                "reconciled": False,
                "adopted": False,
                "peer": None,
                "chain_length": len(self.chain),
                "message": "No valid peer chains available for reconciliation.",
            }

        if local_is_valid:
            if len(best_peer_chain) <= len(self.chain):
                return {
                    "reconciled": False,
                    "adopted": False,
                    "peer": best_peer_name,
                    "chain_length": len(self.chain),
                    "reason": "Local chain is valid and no longer valid peer chain was found.",
                }

            self.chain = list(best_peer_chain)
            return {
                "reconciled": True,
                "adopted": True,
                "peer": best_peer_name,
                "chain_length": len(self.chain),
                "message": "Local chain replaced with the longest valid peer chain.",
            }

        self.chain = list(best_peer_chain)
        return {
            "reconciled": True,
            "adopted": True,
            "peer": best_peer_name,
            "chain_length": len(self.chain),
            "message": "Local chain was invalid and has been reconciled using a valid peer chain.",
        }

    def validate_chain(self, chain: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        active_chain = self.chain if chain is None else chain

        if not active_chain:
            return {"valid": False, "block_count": 0, "blocks": [], "message": "Chain is empty."}

        for index, block in enumerate(active_chain):
            expected = {
                "index": block["index"],
                "timestamp": block["timestamp"],
                "previous_hash": block["previous_hash"],
                "event": block["event"],
            }
            recalculated_hash = _hash_block(expected)
            if block.get("hash") != recalculated_hash:
                return {
                    "valid": False,
                    "block_count": len(active_chain),
                    "blocks": active_chain,
                    "message": f"Block {index} hash mismatch detected.",
                }

            if index == 0 and block["previous_hash"] != "":
                return {
                    "valid": False,
                    "block_count": len(active_chain),
                    "blocks": active_chain,
                    "message": "Genesis block previous_hash must be empty.",
                }

            if index > 0:
                previous = active_chain[index - 1]
                if block["previous_hash"] != previous["hash"]:
                    return {
                        "valid": False,
                        "block_count": len(active_chain),
                        "blocks": active_chain,
                        "message": f"Block {index} is not linked to the previous block.",
                    }

        return {"valid": True, "block_count": len(active_chain), "blocks": active_chain}

    def tamper_last_block(self) -> dict[str, Any]:
        if not self.chain:
            return {"valid": False, "block_count": 0, "blocks": [], "message": "Chain is empty."}

        last_block = self.chain[-1]
        last_block["event"] = {
            **last_block.get("event", {}),
            "type": "TAMPERED_EVENT",
            "details": "Simulated tampering for educational demonstration.",
        }
        return self.validate_chain()
