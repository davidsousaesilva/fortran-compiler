from dataclasses import dataclass, field
from typing import Optional, List


class SemanticError(Exception):
    pass


@dataclass
class Symbol:
    name: str
    type: str
    kind: str = "variable"
    initialized: bool = False

    # Para arrays
    size: Optional[int] = None

    # Para funções/subrotinas
    params: List[str] = field(default_factory=list)
    return_type: Optional[str] = None

    # Para codegen
    index: Optional[int] = None

    def __repr__(self):
        return (
            f"Symbol("
            f"name={self.name!r}, "
            f"type={self.type!r}, "
            f"kind={self.kind!r}, "
            f"initialized={self.initialized}, "
            f"size={self.size}, "
            f"params={self.params}, "
            f"return_type={self.return_type}, "
            f"index={self.index}"
            f")"
        )


class Scope:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.symbols = {}
        self.next_index = 0

    def declare(
        self,
        name,
        type_,
        kind="variable",
        initialized=False,
        size=None,
        params=None,
        return_type=None,
    ):
        key = name.upper()

        if key in self.symbols:
            raise SemanticError(
                f"Identifier '{name}' already declared in scope '{self.name}'"
            )

        symbol = Symbol(
            name=key,
            type=type_,
            kind=kind,
            initialized=initialized,
            size=size,
            params=params or [],
            return_type=return_type,
            index=self.next_index,
        )

        self.symbols[key] = symbol

        if kind == "array":
            self.next_index += size
        else:
            self.next_index += 1

        return symbol

    def lookup(self, name):
        key = name.upper()

        if key in self.symbols:
            return self.symbols[key]

        if self.parent is not None:
            return self.parent.lookup(key)

        raise SemanticError(f"Identifier '{name}' was not declared")

    def exists_local(self, name):
        return name.upper() in self.symbols

    def initialize(self, name):
        symbol = self.lookup(name)
        symbol.initialized = True
        return symbol

    def all_symbols(self):
        return list(self.symbols.values())

    def __repr__(self):
        lines = [f"Scope({self.name})"]
        for name, symbol in self.symbols.items():
            lines.append(f"  {name}: {symbol}")
        return "\n".join(lines)