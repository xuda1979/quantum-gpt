import importlib.util


def _load(candidate_path):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path):
    failures = []
    try:
        m = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return dict(passed=False, details=["candidate import failed: %s" % e])

    required = ["normalize", "lookup", "aliases", "canonicals", "register", "stats"]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s" % ", ".join(missing))
        return dict(passed=False, details=failures)

    try:
        if m.normalize("Hadamard") != "h":
            failures.append("normalize('Hadamard') must be 'h' (casefold before lookup)")
        if m.lookup("PAULI_X") != "x":
            failures.append("lookup('PAULI_X') must be 'x'")
        if m.normalize("cnot") != "cx":
            failures.append("normalize('cnot') must be 'cx'")
        try:
            m.normalize("nope")
            failures.append("normalize('nope') must raise KeyError")
        except KeyError:
            pass
        reg_before = len(m.aliases())
        m.register("sx", "x")
        if m.normalize("SX") != "x":
            failures.append("register then normalize('SX') must be 'x'")
        if len(m.aliases()) != reg_before + 1:
            failures.append("aliases() must grow by 1 after register")
        if "sx" not in m.aliases():
            failures.append("aliases() must contain the new alias")
        st = m.stats()
        if st.get("n_canonicals") != len(set(m.canonicals())):
            failures.append("stats().n_canonicals must match canonicals()")
    except Exception as e:  # noqa: BLE001
        failures.append("registry checks raised: %s" % e)

    return dict(
        passed=not failures,
        details=failures
        or [
            "Gate alias registry: casefolded lookup with runtime register; all six "
            "required entry points present and verified"
        ],
    )
