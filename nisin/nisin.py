import struct
from typing import Any, Optional, List, Dict, Type, Union, Tuple
import re
import yaml
from .primitive import NisinType, Pointer, primitive

StructField = Dict[str, Union[str, Dict[str, Union[str, int]]]]
Structs = Dict[str, Union[str, List[StructField]]]


class BinaryParser:
    def __init__(
        self,
        type_name: str,
        type: Type[NisinType] = None,
        ptr_depth: int = 0,
        dim: List[int] = None,
        children: Optional[Dict[str, "BinaryParser"]] = None,
    ) -> None:
        self.type_name = type_name
        self.type = type
        self.ptr_depth = ptr_depth
        self.dim = [] if dim is None else dim
        self.children = children

        self._binary_data = None
        self._data = None

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
    ) -> Dict[str, Any]:
        self.clear()
        fmt, size = self.get_format(bit)
        if endian == "little":
            fmt = "<" + fmt
        elif endian == "big":
            fmt = ">" + fmt
        else:
            raise ValueError(f"unexpected endian: {endian}")

        data = list(struct.unpack_from(fmt, buf, offset))[::-1]
        return self.asign_data(data)

    def asign_data(self, data: List[Any], *, dim: List[int] = None) -> Any:
        if dim is None:
            dim = self.dim

        if len(dim) != 0:  # array
            ds = []
            for i in range(dim[0]):
                ds.append(self.asign_data(data, dim=dim[1:]))
            return ds
        elif self.ptr_depth > 0:  # pointer
            return data.pop()
        elif self.type is not None:  # primitive
            return data.pop()
        elif self.children is not None:  # struct
            d = {}
            for field_name, c in self.children.items():
                d[field_name] = c.asign_data(data)
            return d
        else:
            raise ValueError

    def show(
        self,
        *,
        use_short: bool = True,
        indent: int = 0,
        step: int = 4,
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

    def clear(self) -> None:
        self._binary_data = None
        self._data = None

        if self.children is not None:
            for c in self.children.values():
                c.clear()


class StructsDefinitions:
    array_dim_pat = re.compile(r"\[([0-9]+)\]")

    def __init__(self, structs: Structs) -> None:
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
                dim = [int(m.group(1)) for m in re.finditer(self.array_dim_pat, entry)]
                if len(dim) > 0:
                    entry = entry.split("[")[0]

                if "*" in entry:
                    ptr_depth = entry.count("*")
                    children[field_name] = BinaryParser(
                        entry.strip("* "), ptr_depth=ptr_depth, dim=dim
                    )
                elif entry in primitive:
                    children[field_name] = BinaryParser(
                        entry, dim=dim, type=primitive[entry]
                    )
                else:
                    children[field_name] = self.build_parser(entry)
            else:
                raise NotImplementedError

        return BinaryParser(target, children=children)
