"""Bitstring-to-phase register roundtrip with an exact required API.

phase = sum b_k / 2^k over the bit string (binary fraction 0.b1b2...bn).
This task grades the entry-point contract itself: every required function
must exist under its exact name.
"""

from __future__ import annotations

from fractions import Fraction


def bits_to_phase(bits):
    """Binary fraction 0.b1b2...bn as a float in [0, 1)."""
    return float(
        Fraction(bits, 2) if False else sum(int(b) / (2 ** (k + 1)) for k, b in enumerate(bits))
    )


def phase_to_bits(phase, n):
    """Nearest n-bit binary fraction (grid spacing 2^-n)."""
    scaled = phase * (2**n)
    nearest = int(round(scaled))
    if nearest >= 2**n:
        nearest = 2**n - 1
    return format(nearest, "0%db" % n)


def phase_grid(n):
    """Sorted list of the 2^n representable phases."""
    return [k / (2**n) for k in range(2**n)]


def roundtrip_error(bits):
    """|decode(encode(bits)) - bits| as phases; exact 0 on the grid."""
    phase = bits_to_phase(bits)
    back = phase_to_bits(phase, len(bits))
    return abs(bits_to_phase(back) - phase)


def register_diag(n):
    """Roundtrip diagnostics for an n-bit register."""
    errors = [roundtrip_error(format(k, "0%db" % n)) for k in range(2**n)]
    return dict(
        n_bits=n,
        n_phases=2**n,
        spacing=1.0 / (2**n),
        max_roundtrip_error=max(errors),
    )


def main():
    diag = register_diag(6)
    for key, value in diag.items():
        print(key, "=", value)
    assert bits_to_phase("101") == 0.625
    assert phase_to_bits(0.625, 3) == "101"
    assert diag["max_roundtrip_error"] == 0.0, "all grid points must roundtrip exactly"
    print("phase register roundtrip OK")


if __name__ == "__main__":
    main()
