#!/usr/bin/env python3

from sys import argv
from sys import exit

HEX2DEX = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "a": 10,
    "A": 10,
    "b": 11,
    "B": 11,
    "c": 12,
    "C": 12,
    "d": 13,
    "D": 13,
    "e": 14,
    "E": 14,
    "f": 15,
    "F": 15
}

DEX2HEX = {
    0: "0",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "a",
    11: "b",
    12: "c",
    13: "d",
    14: "e",
    15: "f"
}


CFD_BASE32 = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "a": 10,
    "A": 10,
    "b": 11,
    "B": 11,
    "c": 12,
    "C": 12,
    "d": 13,
    "D": 13,
    "e": 14,
    "E": 14,
    "f": 15,
    "F": 15,
    "g": 16,
    "G": 16,
    "h": 17,
    "H": 17,
    "j": 18,
    "J": 18,
    "k": 19,
    "K": 19,
    "m": 20,
    "M": 20,
    "n": 21,
    "N": 22,
    "p": 23,
    "P": 23,
    "q": 24,
    "Q": 24,
    "r": 25,
    "R": 25,
    "s": 26,
    "S": 26,
    "t": 27,
    "T": 27,
    "v": 28,
    "V": 28,
    "w": 29,
    "W": 29,
    "x": 30,
    "X": 30,
    "y": 31,
    "Y": 31,
    "z": 32,
    "Z": 33
}


def is_hex(str_to_check):
    """Checks if the argument is hexadecimal"""
    for lit in str_to_check:
        if lit not in HEX2DEX.keys():
            return False
    return True


def is_ipv6(str_to_check):
    """Checks if the argument is a valid (RFC 5952 compliant) IPv6 address"""
    if len(str_to_check) > 39:  # max 39 chars condition
        return False
    if ":" not in str_to_check:  # colon condition
        return False
    chars = list(HEX2DEX)
    chars.append(":")
    for lit in str_to_check:
        if lit not in chars:  # all chars are hex or colon condition
            return False
    parts = str_to_check.split(":")
    if len(parts) > 8:  # max 8 parts condition
        return False
    for part in parts:
        if len(part) > 4:  # max 4 chars per part condition
            return False
        if len(part) > 1 and part.startswith("0"):  # suppress leading 0s condition
            return False
    if len(str_to_check.split("::")) > 2:  # max 1 double-colon condition
        return False
    if ":::" in str_to_check:  # no ":::" condition
        return False
    if "::" in str_to_check and len(parts) == 8:  # "::" used to shorten sequence longer than single 0 field condition
        return False
    if "::" not in str_to_check and "0:0" in str_to_check:  # "::" used when needed condition
        return False

    return True


class HexConverter(object):
    """Converts hexadecimal numbers"""

    def __init__(self, user_input):
        super(HexConverter, self).__init__()
        self.hx = None
        self.ipv6 = None
        if is_hex(user_input):
            self.hx = user_input
        elif is_ipv6(user_input):
            self.ipv6 = user_input

    @staticmethod
    def hex2dec(hx):
        """Converts hexadecimal to decimal numbers"""
        dec = 0
        for i, lit in enumerate(hx[::-1]):
            dec += HEX2DEX[lit] * (16**i)
        return dec

    def expand_ipv6(self):
        """Expands compressed IPv6 addresses"""
        parts = self.ipv6.split(":")
        if "::" in self.ipv6:
            zeroes = []
            supp_0000_count = 8 - len(parts) + 1
            while supp_0000_count > 0:
                zeroes.append("0000")
                supp_0000_count -= 1
            unsupressed = ":" + ":".join(zeroes) + ":"
            self.ipv6 = self.ipv6.replace("::", unsupressed)

        parts = self.ipv6.split(":")
        new_parts = []
        for part in parts:
            new_parts.append(part.zfill(4))
        self.ipv6 = ":".join(new_parts)

    def ipv6_to_dec(self):
        """
        Converts IPv6 addresses to decimal format

        RFC 5952 recommendations for IPv6 representation as text are:

            Leading zeros in each 16-bit field are suppressed. For example, 2001:0db8::0001 is rendered as 2001:db8::1, though any all-zero field that is explicitly presented is rendered as 0.

            "::" is not used to shorten just a single 0 field. For example, 2001:db8:0:0:0:0:2:1 is shortened to 2001:db8::2:1, but 2001:db8:0000:1:1:1:1:1 is rendered as 2001:db8:0:1:1:1:1:1.

            Representations are shortened as much as possible. The longest sequence of consecutive all-zero fields is replaced by double-colon. If there are multiple longest runs of all-zero fields, then it is the leftmost that is compressed. E.g., 2001:db8:0:0:1:0:0:1 is rendered as 2001:db8::1:0:0:1 rather than as 2001:db8:0:0:1::1.

            Hexadecimal digits are expressed as lower-case letters. For example, 2001:db8::1 is preferred over 2001:DB8::1.
        """
        self.expand_ipv6()
        parts = self.ipv6.split(":")
        print(parts)
        dec = []
        for part in parts:
            dec.append(str(self.hex2dec(part)))
        return ":".join(dec)

    @staticmethod
    def dec2base32(dec):
        """Converts decimals do base32"""
        count = 0
        while True:
            power32 = 32 ** count
            if dec > power32:
                count += 1
            else:
                break

    @staticmethod
    def dec2hex(dec):
        """Converts decimals do hexadecimals"""
        ceiling = 0
        while True:
            power16 = 16 ** ceiling
            if dec < power16:
                break
            ceiling += 1

        rmdr = dec
        multiplrs = []
        for i in range(ceiling - 1, -1, -1):
            power = 16 ** i
            if rmdr >= power:
                md = rmdr % power
                multipl = int((rmdr - md) / power)
                delta = power * multipl
                rmdr -= delta
                multiplrs.append(multipl)
            else:
                multiplrs.append(0)

        if len(multiplrs) > 0:
            hx = []
            for m in multiplrs:
                hx.append(DEX2HEX[m])
            hx = "".join(hx)
        else:
            hx = "0"

        return hx


def main():
    """
    Runs the script
    """
    if len(argv) == 2:
        h2d = HexConverter(argv[1])
        if h2d.hx is not None:
            print(h2d.hex2dec(h2d.hx))
        elif h2d.ipv6 is not None:
            print(h2d.ipv6_to_dec())
        else:
            exit("Input in wrong format. Exiting")

    elif len(argv) == 1:
        exit("No parameter entered. Exiting")
    else:
        exit("To many parameters entered. Exiting")


if __name__ == "__main__":
    main()
