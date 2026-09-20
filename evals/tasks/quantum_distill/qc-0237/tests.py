# Auto-generated from distillation reference (row qc-0237).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Iteration | GD Energy | QNG Energy\n-------------------------------------------------------\n0 | 0.48142752 | 0.48142752\n1 | 0.09739037 | 0.31093645\n2 | -0.30039361 | 0.13426731\n3 | -0.68037354 | -0.04565247\n4 | -1.01506975 | -0.22559865\n5 | -1.28837692 | -0.40229917\n6 | -1.49746429 | -0.57269770\n7 | -1.64948598 | -0.73418384\n8 | -1.75620861 | -0.88475127\n9 | -1.82963268 | -1.02306572\n10 | -1.87975141 | -1.14844801\n11 | -1.91400904 | -1.26079345\n12 | -1.93760789 | -1.36045582\n13 | -1.95405815 | -1.44812133\n14 | -1.96568896 | -1.52469097\n15 | -1.97403814 | -1.59118149\n16 | -1.98012391 | -1.64864855\n17 | -1.98462569 | -1.69813146\n18 | -1.98800185 | -1.74061636\n19 | -1.99056573 | -1.77701417\n20 | -1.99253457 | -1.80814948\n21 | -1.99406130 | -1.83475721\n22 | -1.99525518 | -1.85748452\n23 | -1.99619548 | -1.87689582\n24 | -1.99694053 | -1.89347971\n25 | -1.99753384 | -1.90765658\n26 | -1.99800827 | -1.91978647\n27 | -1.99838894 | -1.93017661\n28 | -1.99869523 | -1.93908838\n29 | -1.99894223 | -1.94674373\n30 | -1.99914179 | -1.95333081\n31 | -1.99930325 | -1.95900893\n32 | -1.99943404 | -1.96391296\n33 | -1.99954009 | -1.96815700\n34 | -1.99962615 | -1.97183759\n35 | -1.99969602 | -1.97503647\n36 | -1.99975278 | -1.97782285\n37 | -1.99979891 | -1.98025541\n38 | -1.99983641 | -1.98238392\n39 | -1.99986691 | -1.98425065\n40 | -1.99989171 | -1.98589158\n41 | -1.99991188 | -1.98733730\n42 | -1.99992829 | -1.98861394\n43 | -1.99994164 | -1.98974379\n44 | -1.99995251 | -1.99074594\n45 | -1.99996135 | -1.99163676\n46 | -1.99996854 | -1.99243027\n47 | -1.99997440 | -1.99313857\n48 | -1.99997916 | -1.99377207\n49 | -1.99998304 | -1.99433976'


def _normalize(text):
    # collapse whitespace runs; strip trailing spaces per line
    lines = []
    for line in text.splitlines():
        lines.append(" ".join(line.split()))
    return "\n".join(lines).strip()


def run_tests(candidate_path: str) -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, candidate_path],
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "details": ["candidate timed out (> 120s)"]}
    if proc.returncode != 0:
        return {
            "passed": False,
            "details": ["exit code {r}" .format(r=proc.returncode) + ": " + proc.stderr.strip()[:500]],
        }
    actual = _normalize(proc.stdout)
    if actual == EXPECTED:
        return {"passed": True, "details": ["stdout matches reference"]}
    return {
        "passed": False,
        "details": [
            "stdout mismatch",
            "expected: " + EXPECTED[:200],
            "actual:   " + actual[:200],
        ],
    }
