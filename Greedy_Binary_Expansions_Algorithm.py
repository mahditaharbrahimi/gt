#!/usr/bin/env python3
import sys
import math
from fractions import Fraction
from typing import List, Tuple, Union

# Safe names for eval’ing expressions like "pi/4" or "e-2"
_ALLOWED_NAMES = {
    'pi': math.pi,
    'e':  math.e
}

def parse_x(raw_x: str) -> Fraction:
    """
    Parse raw_x as one of:
      - "a/b"           (Fraction)
      - float literal  (e.g. "0.625")
      - math expression (e.g. "pi/4", "e-2")
    Return its Fraction in (0,1), reducing to the fractional part if ≥1.
    """
    try:
        x = Fraction(raw_x)
    except ValueError:
        try:
            val = eval(raw_x, {"__builtins__": None}, _ALLOWED_NAMES)
            x = Fraction(val).limit_denominator()
        except Exception:
            raise ValueError(f"could not parse x = {raw_x!r}")
    if x >= 1:
        x -= x.numerator // x.denominator
    if not (0 < x < 1):
        raise ValueError("x must lie strictly between 0 and 1 after fractional part")
    return x

def binary_exponents(x: Fraction, n: int) -> List[int]:
    """
    Compute up to n greedy-binary exponents m_k for x.
    Stops early if the remainder becomes zero.
    """
    if n < 1:
        raise ValueError("n must be at least 1")

    exps: List[int] = []
    rem = x

    for _ in range(n):
        if rem == 0:
            break
        inv = Fraction(1, 1) / rem
        p, q = inv.numerator, inv.denominator

        # floor(log2(inv)) via bit lengths
        bits_p, bits_q = p.bit_length(), q.bit_length()
        candidate = bits_p - bits_q
        floor_log2 = candidate - 1 if p < (q << candidate) else candidate

        # ceil(log2(inv))
        m = floor_log2 if p == (q << floor_log2) else floor_log2 + 1

        rem = rem * (1 << m) - 1
        exps.append(m)

    return exps

def partial_binary_sum(exps: List[int]) -> Fraction:
    """
    Given exponents [m1, m2, …], compute
      sum_{k=1..len(exps)} 2^{-(m1+…+mk)}.
    """
    total, cum = Fraction(0), 0
    for m in exps:
        cum += m
        total += Fraction(1, 1 << cum)
    return total

def exps_to_bitstring(exps: List[int]) -> str:
    """
    Build the binary bitstring (after "0.") by placing a '1'
    then (m_k–1) zeros for each exponent m_k.
    """
    bits: List[str] = []
    for m in exps:
        bits.append('1')
        bits.extend('0' * (m - 1))
    return ''.join(bits)

def prompt_inputs() -> Tuple[Fraction, int]:
    print("This program calculates the greedy binary expansion of x ∈ (0,1).")
    raw_x = input("Enter x (e.g. 0.625, 5/8, pi/4): ").strip()
    raw_n = input("Enter n (positive integer): ").strip()
    x = parse_x(raw_x)
    try:
        n = int(raw_n)
    except ValueError:
        raise ValueError(f"n must be an integer (you gave {raw_n!r})")
    return x, n

def main():
    if len(sys.argv) == 3:
        raw_x, raw_n = sys.argv[1], sys.argv[2]
        try:
            x = parse_x(raw_x)
            n = int(raw_n)
        except Exception as e:
            print("Error:", e)
            sys.exit(1)
    else:
        try:
            x, n = prompt_inputs()
        except Exception as e:
            print("Error:", e)
            sys.exit(1)

    exps = binary_exponents(x, n)
    if len(exps) < n:
        print(f"\nnote: exact binary expansion terminated after {len(exps)} "
              f"term{'s' if len(exps) != 1 else ''}.")

    approx = partial_binary_sum(exps)
    bitstr = exps_to_bitstring(exps)

    print()
    print(f"Input x = {x}   n = {n}")
    print(f"The first {len(exps)} exponents are: {exps}")
    print(f"Binary approximation = {approx}   (≈ {float(approx)})")
    print(f"Exact bits   = 0.{bitstr}")

if __name__ == "__main__":
    main()
