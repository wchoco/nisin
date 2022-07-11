import argparse
import pprint
from typing import Optional, List
import sys

from . import nisin


def main():
    args = get_args()
    defs = nisin.StructsDefinitions.from_yaml_files(args.yaml_files)

    if args.select is None:
        pprint.pprint(defs.structs, sort_dicts=False)
        return

    bin_parser = defs.build_parser(args.select)
    if args.binary is None and not args.raw:
        print(bin_parser.show())
        fmt, size = bin_parser.get_format()
        print(f"size: {size}")
        print(f"format: {fmt}")
    else:
        if args.raw:
            data = bin_parser.parse(
                sys.stdin.buffer.read(), args.bit, args.endian, args.offset
            )
        else:
            with open(args.binary, "br") as fi:
                buf = fi.read()
                data = bin_parser.parse(buf, args.bit, args.endian, args.offset)

        if args.json:
            print(data.to_json())
        else:
            print(data.show())


def get_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--yaml-files", nargs="+", required=True)
    parser.add_argument("-s", "--select")

    parser.add_argument("-b", "--binary")
    parser.add_argument("--raw", action="store_true")

    parser.add_argument("--bit", type=int, choices=[32, 64], default=64)
    parser.add_argument("-e", "--endian", choices=["little", "big"], default="little")
    parser.add_argument("-o", "--offset", type=int, default=0)

    parser.add_argument("-j", "--json", action="store_true")

    args = parser.parse_args(argv)
    return args
