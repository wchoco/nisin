import struct
from typing import Dict, Type


class NisinType:
    @staticmethod
    def get_name() -> str:
        raise NotImplementedError

    @staticmethod
    def get_short_name() -> str:
        raise NotImplementedError

    @staticmethod
    def get_format(bit: int = 64) -> str:
        raise NotImplementedError

    @classmethod
    def get_size(cls, bit: int = 64) -> int:
        return struct.calcsize(cls.get_format(bit))


class Char(NisinType):
    @staticmethod
    def get_name() -> str:
        return "char"

    @staticmethod
    def get_short_name() -> str:
        return "char"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "c"


class S8(NisinType):
    @staticmethod
    def get_name() -> str:
        return "signed char"

    @staticmethod
    def get_short_name() -> str:
        return "s8"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "b"


class U8(NisinType):
    @staticmethod
    def get_name() -> str:
        return "unsigned char"

    @staticmethod
    def get_short_name() -> str:
        return "u8"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "B"


class Bool(NisinType):
    @staticmethod
    def get_name() -> str:
        return "bool"

    @staticmethod
    def get_short_name() -> str:
        return "bool"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "?"


class S16(NisinType):
    @staticmethod
    def get_name() -> str:
        return "short"

    @staticmethod
    def get_short_name() -> str:
        return "s16"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "h"


class U16(NisinType):
    @staticmethod
    def get_name() -> str:
        return "unsigned short"

    @staticmethod
    def get_short_name() -> str:
        return "u16"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "H"


class S32(NisinType):
    @staticmethod
    def get_name() -> str:
        return "int"

    @staticmethod
    def get_short_name() -> str:
        return "s32"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "i"


class U32(NisinType):
    @staticmethod
    def get_name() -> str:
        return "unsigned int"

    @staticmethod
    def get_short_name() -> str:
        return "u32"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "I"


class S64(NisinType):
    @staticmethod
    def get_name() -> str:
        return "long long"

    @staticmethod
    def get_short_name() -> str:
        return "s64"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "q"


class U64(NisinType):
    @staticmethod
    def get_name() -> str:
        return "unsigned long long"

    @staticmethod
    def get_short_name() -> str:
        return "u64"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "Q"


class Float(NisinType):
    @staticmethod
    def get_name() -> str:
        return "float"

    @staticmethod
    def get_short_name() -> str:
        return "f32"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "f"


class Double(NisinType):
    @staticmethod
    def get_name() -> str:
        return "double"

    @staticmethod
    def get_short_name() -> str:
        return "f64"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "d"


class SSize(NisinType):
    @staticmethod
    def get_name() -> str:
        return "ssize_t"

    @staticmethod
    def get_short_name() -> str:
        return "ssize_t"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        if bit == 32:
            return "i"
        elif bit == 64:
            return "q"
        else:
            raise ValueError(f"unknown bit: {bit}")


class USize(NisinType):
    @staticmethod
    def get_name() -> str:
        return "size_t"

    @staticmethod
    def get_short_name() -> str:
        return "size_t"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        if bit == 32:
            return "I"
        elif bit == 64:
            return "Q"
        else:
            raise ValueError(f"unknown bit: {bit}")


class Pointer(NisinType):
    @staticmethod
    def get_name() -> str:
        return "void*"

    @staticmethod
    def get_short_name() -> str:
        return "void*"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        if bit == 32:
            return "I"
        elif bit == 64:
            return "Q"
        else:
            raise ValueError(f"unknown bit: {bit}")


class Padding(NisinType):
    @staticmethod
    def get_name() -> str:
        return "padding"

    @staticmethod
    def get_short_name() -> str:
        return "padding"

    @staticmethod
    def get_format(bit: int = 64) -> str:
        return "x"


primitive: Dict[str, Type[NisinType]] = {
    # default
    "char": Char,
    "signed char": S8,
    "unsigned char": U8,
    "_Bool": Bool,
    "short": S16,
    "unsigned short": U16,
    "int": S32,
    "unsigned int": U32,
    "long": S32,  # TODO
    "unsigned long": U32,  # TODO
    "long long": S64,
    "unsigned long long": U64,
    "ssize_t": SSize,
    "size_t": USize,
    "float": Float,
    "double": Double,
    # windows
    "BYTE": U8,
    "WORD": U16,
    "DWORD": U32,
    "QWORD": U64,
    "LONG": S32,
    "LONGLONG": S64,
    "ULONGLONG": U64,
    # linux
    "__s8": S8,
    "__s16": S16,
    "__s32": S32,
    "__s64": S64,
    "__u8": U8,
    "__u16": U16,
    "__u32": U32,
    "__u64": U64,
    # utils
    "bool": Bool,
    "s8": S8,
    "s16": S16,
    "s32": S32,
    "s64": S64,
    "u8": U8,
    "u16": U16,
    "u32": U32,
    "u64": U64,
    "padding": Padding,
}
