import importlib
import sys


def run_tests(workspace_root: str) -> dict:
    failures = []
    sys.path.insert(0, workspace_root)
    try:
        logic = importlib.import_module("pkg.logic")
        reporting = importlib.import_module("pkg.reporting")

        alpha = logic.transform("  Mixed Name  ", "alpha")
        beta = logic.transform("Beta User", "beta")

        if alpha != {"name": "mixed_name", "kind": "alpha", "tag": "mixed_name-A"}:
            failures.append(f"alpha transform mismatch: {alpha!r}")
        if beta != {"name": "beta_user", "kind": "beta", "tag": "beta_user-B"}:
            failures.append(f"beta transform mismatch: {beta!r}")

        rendered = reporting.render_record(alpha)
        if rendered != "mixed_name|alpha|mixed_name-A":
            failures.append(f"reporting contract mismatch: {rendered!r}")
    finally:
        if sys.path and sys.path[0] == workspace_root:
            sys.path.pop(0)
        for module_name in ["pkg", "pkg.logic", "pkg.helpers", "pkg.reporting"]:
            sys.modules.pop(module_name, None)

    return {
        "passed": not failures,
        "details": failures or ["workspace-mode task passed"],
    }
