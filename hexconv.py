#!/usr/bin/env python3

from sys import argv
from sys import exit


class Hexadecimal(object):
    """
    Hexadecimal number. Knows how to convert itself to other notations (any with base <= 10 and base32)
    """
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

    @classmethod
    def is_valid(cls, str_to_check):
        """Checks if the argument is a valid hexadecimal number"""
        for lit in str_to_check:
            if lit not in cls.HEX2DEC.keys():
                return False
        return True

    @classmethod
    def to_dec(cls, hx):
        """Converts a hexadecimal string to a decimal number"""
        dec = 0
        for i, lit in enumerate(hx[::-1]):
            dec += cls.HEX2DEC[lit] * (16**i)
        return dec

    @classmethod
    def dec_to_base(cls, dec, base=16, pretty=False):
        """
        Converts a decimal number to a binary (or any other base <= 10), hexadecimal or base32 string
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
                    conv.append(cls.DEC2HEX[m])
                elif base == 32:
                    conv.append(cls.DEC2CFD_BASE32[m])
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

    def __init__(self, hx):
        super(Hexadecimal, self).__init__()
        self.hx = hx  # string


class IPv6Address(Hexadecimal):
    """
    IPv6 addresss. Knows how to convert itself to other notations (any with base <= 10 and base32)"
    """

    @staticmethod
    def expand(address):
        """Expands a compressed IPv6 address"""

        # uncompressing zeroes
        parts = address.split(":")
        if "::" in address:
            zeroes = []
            compressed_count = 8 - len(parts) + 1
            while compressed_count > 0:
                zeroes.append("0000")
                compressed_count -= 1
            uncompressed = ":" + ":".join(zeroes) + ":"
            address = address.replace("::", uncompressed)
        # left-padding with zeroes
        parts = address.split(":")
        new_parts = []
        for part in parts:
            new_parts.append(part.zfill(4))
        address = ":".join(new_parts)

        return address

    @classmethod
    def is_valid(cls, str_to_check):
        """
        Checks if the argument is a valid (RFC 5952 compliant) IPv6 address

        RFC 5952 recommendations for IPv6 representation as text are:

            - Leading zeros in each 16-bit field are suppressed. For example, 2001:0db8::0001 is rendered as 2001:db8::1, though any all-zero field that is explicitly presented is rendered as 0.
            - "::" is not used to shorten just a single 0 field. For example, 2001:db8:0:0:0:0:2:1 is shortened to 2001:db8::2:1, but 2001:db8:0000:1:1:1:1:1 is rendered as 2001:db8:0:1:1:1:1:1.
            - Representations are shortened as much as possible. The longest sequence of consecutive all-zero fields is replaced by double-colon. If there are multiple longest runs of all-zero fields, then it is the leftmost that is compressed. E.g., 2001:db8:0:0:1:0:0:1 is rendered as 2001:db8::1:0:0:1 rather than as 2001:db8:0:0:1::1.
            - Hexadecimal digits are expressed as lower-case letters. For example, 2001:db8::1 is preferred over 2001:DB8::1.
        """
        if len(str_to_check) > 39:  # max 39 chars condition
            return False
        if ":" not in str_to_check:  # colon condition
            return False
        chars = list(super().HEX2DEC)
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

    def __init__(self, address):
        super(IPv6Address, self).__init__(None)
        self.address = self.expand(address)
        self.hexes = self.address.split(":")  # list of strings
        self.decimals = [super(IPv6Address, self).to_dec(hx) for hx in self.hexes]  # list of numbers

    def to_base(self, base=16):
        """Translates IPv6 address expressed in decimals to base32 notation"""
        based = []
        for decimal in self.decimals:
            based.append(super().dec_to_base(int(decimal), base))
        based = ":".join(based)

        return self.expand(based)


def main():
    """
    Runs the script
    """
    if len(argv) == 2:
        if Hexadecimal.is_valid(argv[1]):
            h = Hexadecimal(argv[1])
            dec = h.to_dec(h.hx)
            print(dec)
        elif IPv6Address.is_valid(argv[1]):
            ip = IPv6Address(argv[1])
            print(ip.to_base(8))
        else:
            exit("Input in wrong format. Exiting")

    elif len(argv) == 1:
        exit("No parameter entered. Exiting")
    else:
        exit("To many parameters entered. Exiting")


if __name__ == "__main__":
    main()
