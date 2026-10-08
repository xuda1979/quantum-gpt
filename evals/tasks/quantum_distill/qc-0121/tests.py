# Auto-generated from distillation reference (row qc-0121).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '0 t= 0.0000 <sigma_z>= 1.000000\n1 t= 0.2020 <sigma_z>= 0.788581\n2 t= 0.4040 <sigma_z>= 0.497188\n3 t= 0.6061 <sigma_z>= 0.171890\n4 t= 0.8081 <sigma_z>=-0.142045\n5 t= 1.0101 <sigma_z>=-0.405829\n6 t= 1.2121 <sigma_z>=-0.591389\n7 t= 1.4141 <sigma_z>=-0.683749\n8 t= 1.6162 <sigma_z>=-0.681490\n9 t= 1.8182 <sigma_z>=-0.595422\n10 t= 2.0202 <sigma_z>=-0.445845\n11 t= 2.2222 <sigma_z>=-0.258901\n12 t= 2.4242 <sigma_z>=-0.062595\n13 t= 2.6263 <sigma_z>= 0.116987\n14 t= 2.8283 <sigma_z>= 0.258797\n15 t= 3.0303 <sigma_z>= 0.348942\n16 t= 3.2323 <sigma_z>= 0.381668\n17 t= 3.4343 <sigma_z>= 0.359185\n18 t= 3.6364 <sigma_z>= 0.290499\n19 t= 3.8384 <sigma_z>= 0.189511\n20 t= 4.0404 <sigma_z>= 0.072696\n21 t= 4.2424 <sigma_z>=-0.043283\n22 t= 4.4444 <sigma_z>=-0.143724\n23 t= 4.6465 <sigma_z>=-0.217541\n24 t= 4.8485 <sigma_z>=-0.258277\n25 t= 5.0505 <sigma_z>=-0.264413\n26 t= 5.2525 <sigma_z>=-0.239015\n27 t= 5.4545 <sigma_z>=-0.188828\n28 t= 5.6566 <sigma_z>=-0.123013\n29 t= 5.8586 <sigma_z>=-0.051702\n30 t= 6.0606 <sigma_z>= 0.015395\n31 t= 6.2626 <sigma_z>= 0.070187\n32 t= 6.4646 <sigma_z>= 0.107053\n33 t= 6.6667 <sigma_z>= 0.123283\n34 t= 6.8687 <sigma_z>= 0.119100\n35 t= 7.0707 <sigma_z>= 0.097309\n36 t= 7.2727 <sigma_z>= 0.062647\n37 t= 7.4747 <sigma_z>= 0.020967\n38 t= 7.6768 <sigma_z>=-0.021633\n39 t= 7.8788 <sigma_z>=-0.059615\n40 t= 8.0808 <sigma_z>=-0.088649\n41 t= 8.2828 <sigma_z>=-0.106025\n42 t= 8.4848 <sigma_z>=-0.110822\n43 t= 8.6869 <sigma_z>=-0.103828\n44 t= 8.8889 <sigma_z>=-0.087245\n45 t= 9.0909 <sigma_z>=-0.064256\n46 t= 9.2929 <sigma_z>=-0.038506\n47 t= 9.4949 <sigma_z>=-0.013586\n48 t= 9.6970 <sigma_z>= 0.007416\n49 t= 9.8990 <sigma_z>= 0.022257\n50 t= 10.1010 <sigma_z>= 0.029728\n51 t= 10.3030 <sigma_z>= 0.029697\n52 t= 10.5051 <sigma_z>= 0.023000\n53 t= 10.7071 <sigma_z>= 0.011234\n54 t= 10.9091 <sigma_z>=-0.003536\n55 t= 11.1111 <sigma_z>=-0.019093\n56 t= 11.3131 <sigma_z>=-0.033364\n57 t= 11.5152 <sigma_z>=-0.044671\n58 t= 11.7172 <sigma_z>=-0.051902\n59 t= 11.9192 <sigma_z>=-0.054588\n60 t= 12.1212 <sigma_z>=-0.052890\n61 t= 12.3232 <sigma_z>=-0.047514\n62 t= 12.5253 <sigma_z>=-0.039554\n63 t= 12.7273 <sigma_z>=-0.030313\n64 t= 12.9293 <sigma_z>=-0.021112\n65 t= 13.1313 <sigma_z>=-0.013120\n66 t= 13.3333 <sigma_z>=-0.007223\n67 t= 13.5354 <sigma_z>=-0.003941\n68 t= 13.7374 <sigma_z>=-0.003400\n69 t= 13.9394 <sigma_z>=-0.005365\n70 t= 14.1414 <sigma_z>=-0.009308\n71 t= 14.3434 <sigma_z>=-0.014504\n72 t= 14.5455 <sigma_z>=-0.020152\n73 t= 14.7475 <sigma_z>=-0.025481\n74 t= 14.9495 <sigma_z>=-0.029846\n75 t= 15.1515 <sigma_z>=-0.032798\n76 t= 15.3535 <sigma_z>=-0.034118\n77 t= 15.5556 <sigma_z>=-0.033818\n78 t= 15.7576 <sigma_z>=-0.032116\n79 t= 15.9596 <sigma_z>=-0.029387\n80 t= 16.1616 <sigma_z>=-0.026092\n81 t= 16.3636 <sigma_z>=-0.022714\n82 t= 16.5657 <sigma_z>=-0.019694\n83 t= 16.7677 <sigma_z>=-0.017377\n84 t= 16.9697 <sigma_z>=-0.015981\n85 t= 17.1717 <sigma_z>=-0.015581\n86 t= 17.3737 <sigma_z>=-0.016118\n87 t= 17.5758 <sigma_z>=-0.017418\n88 t= 17.7778 <sigma_z>=-0.019231\n89 t= 17.9798 <sigma_z>=-0.021270\n90 t= 18.1818 <sigma_z>=-0.023247\n91 t= 18.3838 <sigma_z>=-0.024919\n92 t= 18.5859 <sigma_z>=-0.026106\n93 t= 18.7879 <sigma_z>=-0.026710\n94 t= 18.9899 <sigma_z>=-0.026719\n95 t= 19.1919 <sigma_z>=-0.026198\n96 t= 19.3939 <sigma_z>=-0.025273\n97 t= 19.5960 <sigma_z>=-0.024106\n98 t= 19.7980 <sigma_z>=-0.022873\n99 t= 20.0000 <sigma_z>=-0.021740'


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
