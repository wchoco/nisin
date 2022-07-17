import struct
from typing import Any, Optional, List, Dict, Type, Union, Tuple
import re
from enum import Enum, Flag, EnumMeta

import yaml

from nisin.struct import StructData
from .primitive import Char, NisinType, Padding, Pointer, primitive

StructField = Dict[str, Union[str, Dict[str, Union[str, int]]]]
StructDefs = Dict[str, Union[str, List[StructField]]]


class BinaryParser:
    def __init__(
        self,
        type_name: str,
        type: Type[NisinType] = None,
        ptr_depth: int = 0,
        dim: List[int] = None,
        children: Optional[Dict[str, "BinaryParser"]] = None,
        fmt: str = None,
    ) -> None:
        self.type_name = type_name
        self.type = type
        self.ptr_depth = ptr_depth
        self.dim = [] if dim is None else dim
        self.children = children

        self._fmt = fmt
        self._equates: Optional[EnumMeta] = None

    def set_equates(
        self, labels: Dict[Union[str, int], str] = None, is_flag=False
    ) -> None:
        if labels is None:
            return
        if is_flag:
            self._equates = Flag("equates", {v: k for k, v in labels.items()})  # type: ignore
        else:
            self._equates = Enum("equates", {v: k for k, v in labels.items()})  # type: ignore

    def get_format(self, bit=64) -> Tuple[str, int]:
        fmts = []
        if self.ptr_depth > 0:
            fmts.append(Pointer.get_format(bit))
        elif self.type is not None:
            fmts.append(self.type.get_format(bit))
        elif self.children is not None:
            for c in self.children.values():
                fmts.append(c.get_format(bit)[0])

        dim = 1
        for d in self.dim:
            dim *= d

        fmt = "".join(fmts * dim)
        return fmt, struct.calcsize(fmt)

    def parse(
        self, buf: bytes, bit: int = 64, endian: str = "little", offset: int = 0
    ) -> StructData:
        fmt, size = self.get_format(bit)
        if endian == "little":
            fmt = "<" + fmt
        elif endian == "big":
            fmt = ">" + fmt
        else:
            raise ValueError(f"unexpected endian: {endian}")

        data = list(struct.unpack_from(fmt, buf, offset))[::-1]
        return self.asign_data(data)

    def asign_data(self, data: List[Any], *, dim: List[int] = None) -> StructData:
        if dim is None:
            dim = self.dim

        if len(dim) != 0:  # array
            d: Any = []
            for i in range(dim[0]):
                d.append(self.asign_data(data, dim=dim[1:]))
            if self.type == Char and len(dim) == 1:
                d = b"".join(x.value for x in d).decode()
        elif self.ptr_depth > 0:  # pointer
            d = data.pop()
        elif self.type is not None:  # primitive
            d = data.pop()
        elif self.children is not None:  # struct
            d = {}
            for field_name, c in self.children.items():
                if c.type == Padding:
                    continue
                d[field_name] = c.asign_data(data)
        else:
            raise ValueError
        return StructData(d, self._fmt, self._equates)

    def show(
        self,
        *,
        use_short: bool = True,
        indent: int = 0,
        step: int = 2,
        name: Optional[str] = None,
    ) -> str:
        idt = " " * indent * step
        if self.type is None:
            type_name = self.type_name
        elif use_short:
            type_name = self.type.get_short_name()
        else:
            type_name = self.type.get_name()

        s = f"{idt}{type_name} "
        if self.ptr_depth > 0:
            s += f"{'*'*self.ptr_depth}"
        if name is not None:
            s += name
        s += "".join(f"[{d}]" for d in self.dim)

        s = s.rstrip()
        if self.children is not None and self.ptr_depth == 0:
            ss = [" {"]
            for k, v in self.children.items():
                ss.append(
                    v.show(use_short=use_short, indent=indent + 1, step=step, name=k)
                )
            ss.append(idt + "}")
            s += "\n".join(ss)
        return s


class StructsDefinitions:
    array_dim_pat = re.compile(r"\[([0-9]+)\]")

    def __init__(self, structs: StructDefs) -> None:
        self.structs = structs

    @classmethod
    def from_yaml_files(cls, paths: List[str]) -> "StructsDefinitions":
        structs = {}
        for path in paths:
            with open(path) as fi:
                structs.update(yaml.load(fi, yaml.SafeLoader))
        return cls(structs)

    def build_parser(self, target: str) -> BinaryParser:
        if target not in self.structs:
            raise KeyError(f"cannot find selected struct: {target}")

        t = self.structs[target]
        while isinstance(t, str):
            if t in primitive:
                return BinaryParser(t, type=primitive[t])
            t = self.structs[target]

        children = {}
        for field in t:
            if len(field) != 1:
                raise ValueError(
                    f"struct fields must have one entry: {', '.join(field.keys())}"
                )
            field_name, entry = field.popitem()
            if isinstance(entry, str):
                children[field_name] = self.convert_type(entry)
            else:
                bp = self.convert_type(entry["type"])  # type: ignore
                bp._fmt = entry.get("format")  # type: ignore

                if "labels" in entry:
                    bp.set_equates(entry.get("labels"))  # type: ignore
                elif "flags" in entry:
                    bp.set_equates(entry.get("flags"), is_flag=True)  # type: ignore

                children[field_name] = bp

        return BinaryParser(target, children=children)

    def convert_type(self, ty: str) -> BinaryParser:
        dim = [int(m.group(1)) for m in re.finditer(self.array_dim_pat, ty)]
        # array
        if len(dim) > 0:
            ty = ty.split("[")[0]

        # pointer
        if "*" in ty:
            ptr_depth = ty.count("*")
            bp = BinaryParser(ty.strip("* "), ptr_depth=ptr_depth, dim=dim)
        # primitive
        elif ty in primitive:
            bp = BinaryParser(ty, dim=dim, type=primitive[ty])
        # struct
        else:
            bp = self.build_parser(ty)

        return bp
