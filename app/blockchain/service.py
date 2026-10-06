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

    def validate_chain(self) -> dict[str, Any]:
        if not self.chain:
            return {"valid": False, "block_count": 0, "blocks": [], "message": "Chain is empty."}

        for index, block in enumerate(self.chain):
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
                    "block_count": len(self.chain),
                    "blocks": self.chain,
                    "message": f"Block {index} hash mismatch detected.",
                }

            if index == 0 and block["previous_hash"] != "":
                return {
                    "valid": False,
                    "block_count": len(self.chain),
                    "blocks": self.chain,
                    "message": "Genesis block previous_hash must be empty.",
                }

            if index > 0:
                previous = self.chain[index - 1]
                if block["previous_hash"] != previous["hash"]:
                    return {
                        "valid": False,
                        "block_count": len(self.chain),
                        "blocks": self.chain,
                        "message": f"Block {index} is not linked to the previous block.",
                    }

        return {"valid": True, "block_count": len(self.chain), "blocks": self.chain}

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
