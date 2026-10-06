from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from urllib import error, request
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
        self.peers: dict[str, dict[str, Any]] = {}
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

    def register_peer(
        self,
        name: str,
        chain: list[dict[str, Any]] | None = None,
        base_url: str | None = None,
    ) -> dict[str, Any]:
        if not name:
            raise ValueError("Peer name is required.")

        if base_url:
            normalized_url = base_url.rstrip("/")
            self.peers[name] = {
                "name": name,
                "type": "url",
                "base_url": normalized_url,
                "chain": None,
            }
            return {
                "name": name,
                "type": "url",
                "base_url": normalized_url,
                "chain_length": None,
                "status": "registered",
            }

        snapshot = [self.chain[0]] if chain is None else chain
        self.peers[name] = {
            "name": name,
            "type": "snapshot",
            "base_url": None,
            "chain": deepcopy(snapshot),
        }
        return {
            "name": name,
            "type": "snapshot",
            "base_url": None,
            "chain_length": len(snapshot),
            "status": "registered",
        }

    def _fetch_chain_from_url(self, base_url: str) -> list[dict[str, Any]]:
        endpoint = f"{base_url}/blockchain"
        with request.urlopen(endpoint, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        if not isinstance(payload, dict) or not isinstance(payload.get("blocks"), list):
            raise ValueError("Peer blockchain response must contain a blocks list.")

        return payload["blocks"]

    def _resolve_peer_chain(self, peer_name: str) -> list[dict[str, Any]]:
        peer = self.peers.get(peer_name)
        if peer is None:
            raise KeyError(f"Peer {peer_name} not found.")

        peer_type = peer.get("type")
        if peer_type == "url":
            base_url = peer.get("base_url")
            if not isinstance(base_url, str) or not base_url:
                raise ValueError("Peer URL is not configured.")

            return self._fetch_chain_from_url(base_url)

        chain = peer.get("chain")
        if not isinstance(chain, list):
            raise ValueError("Peer snapshot chain is unavailable.")

        return deepcopy(chain)

    def list_peers(self) -> list[dict[str, Any]]:
        peers: list[dict[str, Any]] = []
        for peer_name, peer in self.peers.items():
            chain = peer.get("chain")
            chain_length = len(chain) if isinstance(chain, list) else None
            peers.append(
                {
                    "name": peer_name,
                    "type": peer.get("type", "snapshot"),
                    "base_url": peer.get("base_url"),
                    "chain_length": chain_length,
                }
            )
        return peers

    def sync_with_peer(self, peer_name: str) -> dict[str, Any]:
        try:
            peer_chain = self._resolve_peer_chain(peer_name)
        except (error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            return {"peer": peer_name, "adopted": False, "reason": f"Failed to fetch peer chain: {exc}"}

        peer_validation = self.validate_chain(peer_chain)
        if not peer_validation["valid"]:
            return {"peer": peer_name, "adopted": False, "reason": "Peer chain is invalid."}

        if len(peer_chain) <= len(self.chain):
            return {"peer": peer_name, "adopted": False, "reason": "Peer chain is not longer than the local chain."}

        self.chain = deepcopy(peer_chain)
        return {"peer": peer_name, "adopted": True, "chain_length": len(self.chain), "message": "Local chain replaced with valid peer chain."}

    def reconcile_with_peers(self) -> dict[str, Any]:
        if not self.peers:
            raise ValueError("No peers registered.")

        local_validation = self.validate_chain()
        local_is_valid = local_validation["valid"]

        best_peer_name: str | None = None
        best_peer_chain: list[dict[str, Any]] | None = None

        for peer_name in self.peers:
            try:
                peer_chain = self._resolve_peer_chain(peer_name)
            except (error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
                continue

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

            self.chain = deepcopy(best_peer_chain)
            return {
                "reconciled": True,
                "adopted": True,
                "peer": best_peer_name,
                "chain_length": len(self.chain),
                "message": "Local chain replaced with the longest valid peer chain.",
            }

        self.chain = deepcopy(best_peer_chain)
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
