from __future__ import annotations

import json
from typing import Any


class TreeNode:
    """Simple n-ary tree node."""

    def __init__(self, value: Any, children: list[TreeNode] | None = None):
        self.value = value
        self.children = children or []


def serialize(root: TreeNode | None) -> str:
    """Serialize an n-ary tree to a JSON string.

    Format: {"v": value, "c": [child, ...]}
    None root -> "null"
    """
    if root is None:
        return "null"

    def to_dict(node: TreeNode) -> dict:
        return {
            "v": node.value,
            "c": [to_dict(ch) for ch in node.children],
        }

    return json.dumps(to_dict(root), separators=(",", ":"))


def deserialize(data: str) -> TreeNode | None:
    """Deserialize a JSON string back to an n-ary tree."""
    if data == "null":
        return None

    obj = json.loads(data)

    def from_dict(d: dict) -> TreeNode:
        return TreeNode(
            value=d["v"],
            children=[from_dict(ch) for ch in d.get("c", [])],
        )

    return from_dict(obj)


def tree_depth(root: TreeNode | None) -> int:
    """Return the depth of the tree (0 for None, 1 for a single node)."""
    if root is None:
        return 0
    if not root.children:
        return 1
    return 1 + max(tree_depth(ch) for ch in root.children)
