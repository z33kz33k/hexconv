#!/usr/bin/env python3

import argparse
from sys import exit


class Base(object):
    """Base for notation"""
    BASES = {
        2: ("binary", 4),
        3: ("ternary", 4),
        4: ("quaternary", 4),
        5: ("quinary", 4),
        6: ("senary", 4),
        7: ("septenary", 4),
        8: ("octal", 3),
        9: ("nonary", 3),
        10: ("decimal", 3),
        11: ("undecimal", 3),
        12: ("duodecimal", 3),
        13: ("tridecimal", 3),
        14: ("tetradecimal", 3),
        15: ("pentadecimal", 3),
        16: ("hexadecimal", 2),
        32: ("duotrigesimal", 2)
    }

    def __init__(self, value):
        super(Base, self).__init__()
        self.value = value
        self.name = self.BASES[self.value][0]
        self.span = self.BASES[self.value][1]


class Hexadecimal(object):
    """
    Hexadecimal number. Knows how to convert itself to other notations (any with a base in Base.BASES)
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
        """Checks if the argument is a valid hexadecimal string"""
        for char in str_to_check:
            if char not in cls.HEX2DEC.keys():
                return False
        return True

    def __init__(self, hx, base, pretty, verbosity):
        super(Hexadecimal, self).__init__()
        self.hx = hx  # string
        self.dec = self.to_dec(self.hx)  # number
        self.base = Base(base)
        self.pretty = pretty
        self.verbosity = verbosity

    def to_dec(self, hx):
        """Converts a hexadecimal string to a decimal number"""
        if hx is None:  # needed when input is IPv6 address (child sends None)
            return None
        dec = 0
        for i, char in enumerate(hx[::-1]):
            dec += self.HEX2DEC[char] * (16**i)
        return dec

    def to_base(self, dec):
        """Converts a decimal number to a string in other notation"""
        ceiling = 0
        while True:
            maxpower = self.base.value ** ceiling
            if maxpower > dec:
                break
            ceiling += 1

        rmdr = dec
        multiplrs = []
        for exp in range(ceiling - 1, -1, -1):
            power = self.base.value ** exp
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
                if self.base.value == 32:
                    conv.append(self.DEC2CFD_BASE32[m])
                else:
                    conv.append(self.DEC2HEX[m])
            conv = "".join(conv)
        else:
            conv = "0"

        return conv

    def segment(self, numstring):
        segments = []
        segment = []
        for i in range(len(numstring)):
            segment.append(numstring[i])
            if (i + 1) % self.base.span == 0:
                segment = "".join(segment)
                segments.append(segment)
                segment = []
        numstring = " ".join(segments)

        return numstring

    def prettify(self, numstring):
        """Renders a number string in human readable format"""

        # padding with zeroes
        zeroes_count = self.base.span - len(numstring) % self.base.span
        if zeroes_count == self.base.span:
            zeroes_count = 0
        numstring = numstring.zfill(len(numstring) + zeroes_count)
        # dividing into self.base.span-long segments
        numstring = self.segment(numstring)

        return numstring

    def get_output(self):
        """Creates and returns the output string"""
        output = self.to_base(self.dec)

        if self.pretty:
            output = self.prettify(output)

        if self.verbosity:
            output = "'{}' in {} notation: {}".format(self.hx, self.base.name, output)

        return output


class IPv6Address(Hexadecimal):
    """
    IPv6 address. Knows how to convert itself to other notations (any with a base in Base.BASES)
    """

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
        for char in str_to_check:
            if char not in chars:  # all chars are hex or colon condition
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

    def __init__(self, address, base, pretty, verbosity):
        super(IPv6Address, self).__init__(None, base, pretty, verbosity)
        self.raw_address = address
        self.address = self.expand(address)
        self.hexes = self.address.split(":")  # list of strings
        self.decimals = [super(IPv6Address, self).to_dec(hx) for hx in self.hexes]  # list of numbers

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

    @staticmethod
    def compress(address):  # this was a lot harder than expected
        """Supresses zeroes in an address (as per RFC 5952)"""
        parts = address.split(":")

        # mapping consecutive zeroes in 'parts'
        indexes = []  # list of lists of indexes mapping to consecutive zeroes
        current_seq = []
        zeroes_count = 0
        for i, part in enumerate(parts):

            if zeroes_count == 1 and part != "0":  # only at least 2 consecutive zeroes count
                zeroes_count = 0

            if zeroes_count > 1 and part != "0":
                for z in range(zeroes_count):
                    current_seq.append(i - (z + 1))
                indexes.append(current_seq[::-1])
                current_seq = []  # flush
                zeroes_count = 0
            elif zeroes_count > 0 and part == "0" and i == len(parts) - 1:  # case of zeroes' sequence at the end
                for z in range(zeroes_count + 1):
                    current_seq.append(i - z)
                indexes.append(current_seq[::-1])
                break

            if part == "0":
                zeroes_count += 1

        # removing mapped parts & adding colons
        if len(indexes) > 0:  # if there were zeroes
            indexes = indexes[::-1]  # reversing order so the next step selects the right sequence (the left-most as per 'parts')
            indexes = sorted(indexes, key=lambda item: len(item))
            seq = indexes.pop()
            # adding colons
            if len(seq) == 8:
                return "::"
            if 0 in seq:
                parts[seq[len(seq) - 1] + 1] = "::" + parts[seq[len(seq) - 1] + 1]
            elif len(parts) - 1 in seq:
                parts[seq[0] - 1] = parts[seq[0] - 1] + "::"
            else:
                parts[seq[0] - 1] = parts[seq[0] - 1] + ":"
            # removing parts
            for index in seq[::-1]:  # deleting items of a list being looped over - indexes NEED to be reversed!
                parts.pop(index)

        return ":".join(parts)

    def to_base(self):
        """Translates IPv6 address expressed in decimals to other notation"""
        based = []
        for decimal in self.decimals:
            based.append(super().to_base(int(decimal)))
        based = ":".join(based)

        return based

    def prettify(self, address):
        """Renders an address in human readable format"""
        parts = address.split(":")

        # prettifying non-zero parts
        new_parts = []
        for part in parts:
            if part != "0":
                new_parts.append(super().prettify(part))
            else:
                new_parts.append("0")

        # prettifying zero parts
        new_parts_lens = [len(new_part) for new_part in new_parts]
        newer_parts = []
        for new_part in new_parts:
            if new_part != "0":
                newer_parts.append(new_part)
            else:
                zeroes = "0" * max(new_parts_lens)
                newer_parts.append(super().segment(zeroes))

        new_address = ":".join(newer_parts)

        return new_address

    def get_output(self):
        """Creates and returns the output string"""
        output = self.to_base()

        if self.pretty:
            output = self.prettify(output)
        else:
            output = self.compress(output)

        if self.verbosity:
            output = "'{}' in {} notation: {}".format(self.raw_address, self.base.name, output)

        return output


def get_argsparser():
    """Creates and returns a command line arguments parser"""
    parser = argparse.ArgumentParser(description="Convert a hexadecimal/IPv6 address to other notations")
    parser.add_argument("hex_or_ipv6", help="either a hexadecimal number or a valid (RFC 5952 compliant) IPv6 address")
    parser.add_argument("-b", "--base", type=int, choices=sorted(Base.BASES.keys()), default=10, help="base for notation, 32 is Crockford's variety,  defaults to 10")
    parser.add_argument("-p", "--prettify", action="store_true", help="prettify output to human readable format (most useful for lower bases)")
    parser.add_argument("-v", "--verbosity", action="store_true", help="increase output verbosity")
    return parser


def main():
    """Runs the script"""
    parser = get_argsparser()
    args = parser.parse_args()

    if Hexadecimal.is_valid(args.hex_or_ipv6):
        h = (Hexadecimal(args.hex_or_ipv6, args.base, args.prettify, args.verbosity))
        print(h.get_output())
    elif IPv6Address.is_valid(args.hex_or_ipv6):
        ip = IPv6Address(args.hex_or_ipv6, args.base, args.prettify, args.verbosity)
        print(ip.get_output())
    else:
        parser.print_usage()
        exit("{}: error: unrecognized argument: {}".format(parser.prog, args.hex_or_ipv6))


if __name__ == "__main__":
    main()
