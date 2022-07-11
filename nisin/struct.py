from __future__ import annotations
from typing import Dict, Any, Union, List
import json

RawValue = Union[str, int]


class StructData:
    def __init__(
        self,
        value: Union[RawValue, List[StructData], Dict[str, StructData]],
        fmt: str = None,
        labels: Dict[RawValue, str] = None,
    ) -> None:
        self.value = value
        if fmt is None:
            if isinstance(value, int):
                self.fmt = "#x"
            else:
                self.fmt = ""
        else:
            self.fmt = fmt
        self.labels = {} if labels is None else labels

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if isinstance(self.value, dict):
            for k, v in self.value.items():
                d[k] = v._to_dict()
        return d

    def _to_dict(self) -> Union[RawValue, List[StructData], Dict[str, StructData]]:
        if isinstance(self.value, dict):
            d: Any = {}
            for k, v in self.value.items():
                d[k] = v._to_dict()
            return d
        elif isinstance(self.value, list):
            d = []
            for v in self.value:
                d.append(v._to_dict())
        else:
            d = self.value
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def show(
        self,
        *,
        indent: int = 0,
        step: int = 2,
        name: str = None,
    ) -> str:
        idt = " " * indent * step
        nm = "" if name is None else f"{name}: "

        if isinstance(self.value, dict):
            ss = [f"{idt}{nm}" + "{"]
            for n, v in self.value.items():
                ss.append(v.show(indent=indent + 1, step=step, name=n))
            ss.append(idt + "}")
            return "\n".join(ss)
        elif isinstance(self.value, list):
            ss = [f"{idt}{nm}" + "["]
            for v in self.value:
                ss.append(v.show(indent=indent + 1, step=step))
            ss.append(idt + "]")
            return "\n".join(ss)
        else:
            if self.value in self.labels:
                return f"{idt}{nm}{self.labels[self.value]},"
            else:
                return f"{idt}{nm}{self.value:{self.fmt}},"
