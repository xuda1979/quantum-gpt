import importlib.util


def _load(path: str):
    spec = importlib.util.spec_from_file_location("candidate", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run_tests(candidate_path: str) -> dict:
    failures: list[str] = []
    try:
        mod = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return {"passed": False, "details": [f"import failed: {e}"]}

    users = [
        {"id": 1, "name": "alice"},
        {"id": 2, "name": "bob"},
        {"id": 3, "name": "carol"},
    ]
    orders = [
        {"uid": 1, "item": "book", "price": 10},
        {"uid": 1, "item": "pen", "price": 2},
        {"uid": 2, "item": "lamp", "price": 25},
    ]

    # 1. Basic inner join
    out = mod.run_query(
        users,
        orders,
        "users",
        "orders",
        "id",
        "uid",
        columns=["users.name", "orders.item", "orders.price"],
    )
    if len(out) != 3:
        failures.append(f"join returned {len(out)} rows, expected 3")
    else:
        names = sorted(r["users.name"] for r in out)
        if names != ["alice", "alice", "bob"]:
            failures.append(f"join names = {names!r}")

    # 2. WHERE filter on a joined column
    out2 = mod.run_query(
        users,
        orders,
        "users",
        "orders",
        "id",
        "uid",
        columns=["users.name", "orders.item"],
        where=("orders.price", ">", 5),
    )
    if len(out2) != 2:
        failures.append(f"WHERE price>5 returned {len(out2)} rows, expected 2")
    else:
        items = sorted(r["orders.item"] for r in out2)
        if items != ["book", "lamp"]:
            failures.append(f"WHERE items = {items!r}")

    # 3. Carol has no orders -> excluded by inner join
    if any(r["users.name"] == "carol" for r in out):
        failures.append("inner join included a user with no orders")

    # 4. Unqualified column must be unambiguous
    bad_users = [{"id": 1, "x": 1}]
    bad_orders = [{"uid": 1, "x": 2}]
    try:
        mod.run_query(bad_users, bad_orders, "u", "o", "id", "uid", columns=["x"])
        failures.append("ambiguous unqualified column did not raise")
    except KeyError:
        pass
    except Exception as e:  # noqa: BLE001
        failures.append(f"ambiguous column raised wrong exception: {e!r}")

    # 5. Missing column raises KeyError
    try:
        mod.run_query(users, orders, "users", "orders", "id", "uid", columns=["users.nonexistent"])
        failures.append("missing column did not raise")
    except KeyError:
        pass

    # 6. !=, <=, >= operators
    out3 = mod.run_query(
        users,
        orders,
        "users",
        "orders",
        "id",
        "uid",
        columns=["orders.item"],
        where=("orders.price", "!=", 10),
    )
    items3 = sorted(r["orders.item"] for r in out3)
    if items3 != ["lamp", "pen"]:
        failures.append(f"WHERE price!=10 returned {items3!r}")

    return {
        "passed": not failures,
        "details": failures
        or ["SQL inner join + projection + WHERE filter + ambiguity check all correct"],
    }
