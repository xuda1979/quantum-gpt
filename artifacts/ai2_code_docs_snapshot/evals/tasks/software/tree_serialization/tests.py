import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []
    TreeNode = module.TreeNode

    # Test 1: None round-trip
    s = module.serialize(None)
    if s != "null":
        failures.append(f"serialize(None) -> {s!r}, expected 'null'")
    r = module.deserialize("null")
    if r is not None:
        failures.append("deserialize('null') should return None")

    # Test 2: single node
    node = TreeNode("root")
    s = module.serialize(node)
    restored = module.deserialize(s)
    if restored is None or restored.value != "root" or restored.children != []:
        failures.append(f"Single node round-trip failed: {s}")

    # Test 3: tree with children
    #       1
    #      /|\
    #     2  3  4
    #    /
    #   5
    tree = TreeNode(1, [
        TreeNode(2, [TreeNode(5)]),
        TreeNode(3),
        TreeNode(4),
    ])
    s = module.serialize(tree)
    restored = module.deserialize(s)
    if restored is None:
        failures.append("Deserialized tree is None")
    else:
        if restored.value != 1:
            failures.append(f"Root value={restored.value}, expected 1")
        if len(restored.children) != 3:
            failures.append(f"Root has {len(restored.children)} children, expected 3")
        else:
            if restored.children[0].value != 2:
                failures.append("First child should be 2")
            if len(restored.children[0].children) != 1:
                failures.append("Node 2 should have 1 child")
            elif restored.children[0].children[0].value != 5:
                failures.append("Node 2's child should be 5")
            if restored.children[1].value != 3:
                failures.append("Second child should be 3")
            if restored.children[2].value != 4:
                failures.append("Third child should be 4")

    # Test 4: tree_depth
    if module.tree_depth(None) != 0:
        failures.append("tree_depth(None) should be 0")
    if module.tree_depth(TreeNode("x")) != 1:
        failures.append("tree_depth(single) should be 1")
    if module.tree_depth(tree) != 3:
        failures.append(f"tree_depth(tree) = {module.tree_depth(tree)}, expected 3")

    # Test 5: string values
    str_tree = TreeNode("hello", [TreeNode("world"), TreeNode("foo", [TreeNode("bar")])])
    s = module.serialize(str_tree)
    r = module.deserialize(s)
    if r is None or r.value != "hello":
        failures.append("String tree round-trip failed at root")
    elif len(r.children) != 2 or r.children[1].children[0].value != "bar":
        failures.append("String tree round-trip failed at nested node")

    # Test 6: serialize is valid JSON
    import json
    try:
        json.loads(module.serialize(tree))
    except json.JSONDecodeError:
        failures.append("serialize output is not valid JSON")

    return {
        "passed": not failures,
        "details": failures or ["Tree serialization handles all cases correctly"],
    }
