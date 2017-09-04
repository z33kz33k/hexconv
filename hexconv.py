#!/usr/bin/env python3

from sys import argv
from sys import exit

HEX2DEC = {
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

DEC2HEX = {
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

DEC2CFD_BASE32 = {  # decimals to Crockford's base32
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
    15: "f",
    16: "g",
    17: "h",
    18: "j",
    19: "k",
    20: "m",
    21: "n",
    22: "p",
    23: "q",
    24: "r",
    25: "s",
    26: "t",
    27: "v",
    28: "w",
    29: "x",
    30: "y",
    31: "z"
}

CFD_BASE32 = {  # Crockford's base32 to decimals (so far not used)
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
    "N": 21,
    "p": 22,
    "P": 22,
    "q": 23,
    "Q": 23,
    "r": 24,
    "R": 24,
    "s": 25,
    "S": 25,
    "t": 26,
    "T": 26,
    "v": 27,
    "V": 27,
    "w": 28,
    "W": 28,
    "x": 29,
    "X": 29,
    "y": 30,
    "Y": 30,
    "z": 31,
    "Z": 31
}


def is_hex(str_to_check):
    """Checks if the argument is hexadecimal"""
    for lit in str_to_check:
        if lit not in HEX2DEC.keys():
            return False
    return True


def is_ipv6(str_to_check):
    """Checks if the argument is a valid (RFC 5952 compliant) IPv6 address

    RFC 5952 recommendations for IPv6 representation as text are:

        Leading zeros in each 16-bit field are suppressed. For example, 2001:0db8::0001 is rendered as 2001:db8::1, though any all-zero field that is explicitly presented is rendered as 0.

        "::" is not used to shorten just a single 0 field. For example, 2001:db8:0:0:0:0:2:1 is shortened to 2001:db8::2:1, but 2001:db8:0000:1:1:1:1:1 is rendered as 2001:db8:0:1:1:1:1:1.

        Representations are shortened as much as possible. The longest sequence of consecutive all-zero fields is replaced by double-colon. If there are multiple longest runs of all-zero fields, then it is the leftmost that is compressed. E.g., 2001:db8:0:0:1:0:0:1 is rendered as 2001:db8::1:0:0:1 rather than as 2001:db8:0:0:1::1.

        Hexadecimal digits are expressed as lower-case letters. For example, 2001:db8::1 is preferred over 2001:DB8::1.
    """
    if len(str_to_check) > 39:  # max 39 chars condition
        return False
    if ":" not in str_to_check:  # colon condition
        return False
    chars = list(HEX2DEC)
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
    """
    Converts hexadecimal numbers/IPv6 addresses to numbers/addresses expressed with binary (or any other base <= 10) or base32 notation"
    """

    def __init__(self, user_input):
        super(HexConverter, self).__init__()
        self.hx = None
        self.hx_dec = None
        self.ipv6 = None  # ordinary IPv6 address (expressed with hexadecimals and colons)
        self.ipv6_dec = None  # IPv6 expressed with decimals and colons

        if is_hex(user_input):
            self.hx = user_input
            self.hex_dec = self.hex2dec(self.hx)
        elif is_ipv6(user_input):
            self.ipv6 = self.expand_ipv6(user_input)
            self.ipv6_dec = self.ipv6_to_dec()  # IPv6 expressed with decimals (and colons)

    @staticmethod
    def hex2dec(hx):
        """Converts a hexadecimal number (string) to a decimal one (number)"""
        if hx is None:
            return None
        else:
            dec = 0
            for i, lit in enumerate(hx[::-1]):
                dec += HEX2DEC[lit] * (16**i)
            return dec

    @staticmethod
    def expand_ipv6(ipv6):
        """Expands compressed IPv6 addresses"""
        parts = ipv6.split(":")
        if "::" in ipv6:
            zeroes = []
            supp_0000_count = 8 - len(parts) + 1
            while supp_0000_count > 0:
                zeroes.append("0000")
                supp_0000_count -= 1
            unsupressed = ":" + ":".join(zeroes) + ":"
            ipv6 = ipv6.replace("::", unsupressed)

        parts = ipv6.split(":")
        new_parts = []
        for part in parts:
            new_parts.append(part.zfill(4))
        ipv6 = ":".join(new_parts)

        return ipv6

    def ipv6_to_dec(self):
        """Converts IPv6 addresses to decimal format"""
        if self.ipv6 is not None:
            parts = self.ipv6.split(":")
        else:
            return None
        dec = []
        for part in parts:
            dec.append(str(self.hex2dec(part)))

        return ":".join(dec)

    @staticmethod
    def conv_dec(dec, base=16, pretty=False):
        """
        Converts decimals (numbers) to binaries (or any other base <= 10), hexadecimals or base32 (strings)
        """
        if base not in [i for i in range(2, 33) if i <= 10 or i == 16 or i == 32]:
            return None

        ceiling = 0
        while True:
            maxpower = base ** ceiling
            if maxpower > dec:
                break
            ceiling += 1

        rmdr = dec
        multiplrs = []
        for exp in range(ceiling - 1, -1, -1):
            power = base ** exp
            if rmdr >= power:
                md = rmdr % power
                multipl = int((rmdr - md) / power)
                delta = power * multipl
                rmdr -= delta
                multiplrs.append(multipl)
            else:
                multiplrs.append(0)

        if len(multiplrs) > 0:
            conv = []
            for m in multiplrs:
                if base == 16:
                    conv.append(DEC2HEX[m])
                elif base == 32:
                    conv.append(DEC2CFD_BASE32[m])
                else:
                    conv.append(str(m))
            conv = "".join(conv)
        else:
            conv = "0"

        if pretty:
            # padding with zeroes
            zeroes_count = 4 - len(conv) % 4
            if zeroes_count == 4:
                zeroes_count = 0
            conv = conv.zfill(len(conv) + zeroes_count)
            # dividing into 4 chars long segments
            segments = []
            segment = []
            for i in range(len(conv)):
                segment.append(conv[i])
                if (i + 1) % 4 == 0:
                    segment = "".join(segment)
                    segments.append(segment)
                    segment = []
            conv = " ".join(segments)

        return conv

    def ipv6_to_base32(self):
        """Translates IPv6 address expressed in decimals to base32 notation"""
        parts = self.ipv6_dec.split(":")
        base32 = []
        for part in parts:
            base32.append(self.conv_dec(int(part), 32))
        return ":".join(base32)


def main():
    """
    Runs the script
    """
    if len(argv) == 2:
        h2d = HexConverter(argv[1])
        if h2d.hx is not None:
            print(h2d.hex2dec(h2d.hx))
        elif h2d.ipv6 is not None:
            h2d.ipv6_to_dec()
            print(h2d.ipv6_dec)
            print(h2d.ipv6_to_base32())
        else:
            exit("Input in wrong format. Exiting")

    elif len(argv) == 1:
        exit("No parameter entered. Exiting")
    else:
        exit("To many parameters entered. Exiting")


if __name__ == "__main__":
    main()
