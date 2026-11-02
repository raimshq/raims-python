#!/usr/bin/env python3
"""Check the Python library surface independently from the HTTP contract."""
from __future__ import annotations

import argparse
import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
FORMAT_VERSION = 2
TYPED_DICTS = {"typing.TypedDict", "typing_extensions.TypedDict"}
REQUIRED = {"typing.Required", "typing_extensions.Required"}
NOT_REQUIRED = {"typing.NotRequired", "typing_extensions.NotRequired"}
DATACLASS_DEFAULTS = {
    "init": True, "repr": True, "eq": True, "order": False,
    "unsafe_hash": False, "frozen": False, "match_args": True,
    "kw_only": False, "slots": False, "weakref_slot": False,
}
BUILTINS = {"object", "dict", "str", "int", "float", "bool", "tuple", "list", "set",
            "Exception", "BaseException", "RuntimeError", "ValueError", "TypeError",
            "property", "staticmethod", "classmethod"}


def expression(node: ast.AST | None) -> str | None:
    return ast.unparse(node) if node is not None else None


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef, binding: str) -> dict[str, Any]:
    positional = node.args.posonlyargs + node.args.args
    defaults = [None] * (len(positional) - len(node.args.defaults)) + node.args.defaults
    parameters = []
    for index, (argument, default) in enumerate(zip(positional, defaults)):
        if index == 0 and binding in {"instance", "class"}:
            continue
        parameters.append({
            "name": argument.arg,
            "kind": "positional_only" if index < len(node.args.posonlyargs) else "positional_or_keyword",
            "annotation": expression(argument.annotation), "default": expression(default),
        })
    if node.args.vararg:
        parameters.append({"name": node.args.vararg.arg, "kind": "varargs", "annotation": expression(node.args.vararg.annotation)})
    for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        parameters.append({"name": argument.arg, "kind": "keyword_only", "annotation": expression(argument.annotation), "default": expression(default)})
    if node.args.kwarg:
        parameters.append({"name": node.args.kwarg.arg, "kind": "kwargs", "annotation": expression(node.args.kwarg.annotation)})
    return {"kind": "async_method" if isinstance(node, ast.AsyncFunctionDef) else "method",
            "binding": binding, "parameters": parameters, "return": expression(node.returns)}


def public(name: str) -> bool:
    return not name.startswith("_") or name in {
        "__init__", "__enter__", "__exit__", "__aenter__", "__aexit__",
        "__iter__", "__len__", "__getitem__",
    }


class Surface:
    def __init__(self, root: Path) -> None:
        package = root / "src/raims"
        self.trees = {"raims" if path.stem == "__init__" else "raims." + path.stem:
                      ast.parse(path.read_text(encoding="utf-8")) for path in sorted(package.glob("*.py"))}
        self.aliases: dict[str, str] = {}
        self.values: dict[str, ast.AST] = {}
        self.classes: dict[str, ast.ClassDef] = {}
        for module, tree in self.trees.items():
            for node in tree.body:
                if isinstance(node, ast.ImportFrom):
                    package_parts = module.split(".") if module == "raims" else module.split(".")[:-1]
                    parent = ".".join(package_parts[:len(package_parts) - node.level + 1]) if node.level else ""
                    origin = ".".join(part for part in (parent, node.module) if part) if node.level else node.module or ""
                    for alias in node.names:
                        if alias.name == "*":
                            raise ValueError("Wildcard imports cannot define the reviewed public surface.")
                        self.aliases[module + "." + (alias.asname or alias.name)] = origin + "." + alias.name
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.aliases[module + "." + (alias.asname or alias.name.split(".")[0])] = alias.name if alias.asname else alias.name.split(".")[0]
                elif isinstance(node, ast.ClassDef):
                    self.classes[module + "." + node.name] = node
                elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for target in targets:
                        if isinstance(target, ast.Name) and node.value is not None:
                            self.values[module + "." + target.id] = node.value
        self._typed: dict[str, bool] = {}

    def follow(self, name: str, visited: frozenset[str] = frozenset()) -> str:
        if name in visited:
            raise ValueError("Cyclic import or type alias in the public surface.")
        visited = visited | {name}
        if name in self.aliases:
            return self.follow(self.aliases[name], visited)
        value = self.values.get(name)
        if isinstance(value, (ast.Name, ast.Attribute)):
            return self.reference(name.rsplit(".", 1)[0], value, visited)
        return name

    def reference(self, module: str, node: ast.AST, visited: frozenset[str] = frozenset()) -> str:
        if isinstance(node, ast.Subscript):
            return self.reference(module, node.value, visited)
        if isinstance(node, ast.Name):
            local = module + "." + node.id
            if local in self.classes or local in self.aliases or local in self.values:
                return self.follow(local, visited)
            return ("builtins." if node.id in BUILTINS else module + ".") + node.id
        if isinstance(node, ast.Attribute):
            return self.follow(self.reference(module, node.value, visited) + "." + node.attr, visited)
        raise ValueError("An inheritance or decorator reference cannot be represented.")

    def bases(self, name: str) -> list[str]:
        module = name.rsplit(".", 1)[0]
        return [self.reference(module, base) for base in self.classes[name].bases]

    def typed_dict(self, name: str, visited: frozenset[str] = frozenset()) -> bool:
        if name in self._typed:
            return self._typed[name]
        if name in visited:
            raise ValueError("Cyclic class inheritance in the public surface.")
        result = any(base in TYPED_DICTS or base in self.classes and self.typed_dict(base, visited | {name}) for base in self.bases(name))
        self._typed[name] = result
        return result

    def literal_bool(self, node: ast.AST, module: str) -> bool:
        if isinstance(node, (ast.Name, ast.Attribute)):
            target = self.reference(module, node)
            if target in self.values:
                node = self.values[target]
        value = ast.literal_eval(node)
        if type(value) is not bool:
            raise ValueError("Class semantic flags must be literal booleans.")
        return value

    def decorators(self, module: str, nodes: list[ast.expr]) -> list[str]:
        result = []
        for node in nodes:
            if isinstance(node, ast.Call):
                result.append(self.reference(module, node.func) + "(" + ", ".join(
                    [expression(arg) or "" for arg in node.args] +
                    [(keyword.arg or "**") + "=" + (expression(keyword.value) or "") for keyword in node.keywords]
                ) + ")")
            else:
                result.append(self.reference(module, node))
        return result

    def class_definition(self, name: str) -> dict[str, Any]:
        node = self.classes[name]
        module = name.rsplit(".", 1)[0]
        result: dict[str, Any] = {"kind": "class", "bases": self.bases(name),
                                  "keywords": {keyword.arg or "**": expression(keyword.value) for keyword in node.keywords}}
        decorators = []
        for decorator in node.decorator_list:
            call = decorator if isinstance(decorator, ast.Call) else None
            target = self.reference(module, call.func if call else decorator)
            if target == "dataclasses.dataclass":
                if call and call.args:
                    raise ValueError("Positional dataclass options cannot define the reviewed surface.")
                options = dict(DATACLASS_DEFAULTS)
                for keyword in call.keywords if call else []:
                    if keyword.arg not in options:
                        raise ValueError("Unsupported dataclass semantic option.")
                    options[keyword.arg] = self.literal_bool(keyword.value, module)
                result["dataclass"] = options
            else:
                decorators.extend(self.decorators(module, [decorator]))
        result["decorators"] = decorators
        if self.typed_dict(name):
            total_node = next((keyword.value for keyword in node.keywords if keyword.arg == "total"), ast.Constant(True))
            result["typed_dict"] = {"total": self.literal_bool(total_node, module)}
            result["keywords"].pop("total", None)
        return result

    def field(self, name: str, member: ast.AnnAssign) -> dict[str, Any]:
        definition: dict[str, Any] = {"kind": "field", "annotation": expression(member.annotation), "default": expression(member.value)}
        if self.typed_dict(name):
            module = name.rsplit(".", 1)[0]
            annotation = member.annotation
            required = self.class_definition(name)["typed_dict"]["total"]
            if isinstance(annotation, ast.Subscript):
                wrapper = self.reference(module, annotation.value)
                if wrapper in REQUIRED | NOT_REQUIRED:
                    required = wrapper in REQUIRED
                    annotation = annotation.slice
            definition.update(annotation=expression(annotation), required=required)
        return definition

    def members(self, name: str, visited: frozenset[str] = frozenset()) -> dict[str, Any]:
        if name in visited:
            raise ValueError("Cyclic class inheritance in the public surface.")
        node = self.classes[name]
        module = name.rsplit(".", 1)[0]
        result: dict[str, Any] = {}
        for base in self.bases(name):
            if base in self.classes:
                result.update(copy.deepcopy(self.members(base, visited | {name})))
        for member in node.body:
            if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and public(member.name):
                decorators = self.decorators(module, member.decorator_list)
                binding = "static" if "builtins.staticmethod" in decorators else "class" if "builtins.classmethod" in decorators else "instance"
                definition = signature(member, binding)
                definition["decorators"] = decorators
                accessor = next((decorator.attr for decorator in member.decorator_list if isinstance(decorator, ast.Attribute) and decorator.attr in {"getter", "setter", "deleter"}), None)
                if "builtins.property" in decorators or accessor:
                    property_definition = result.get(member.name)
                    if not isinstance(property_definition, dict) or property_definition.get("kind") != "property":
                        property_definition = {"kind": "property", "getter": None, "setter": None, "deleter": None}
                    definition["decorators"] = []
                    property_definition[accessor or "getter"] = definition
                    property_definition["readonly"] = property_definition["setter"] is None
                    result[member.name] = property_definition
                else:
                    result[member.name] = definition
                if member.name == "__init__":
                    for assignment in ast.walk(member):
                        if isinstance(assignment, ast.Assign):
                            for target in assignment.targets:
                                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self" and public(target.attr):
                                    value = assignment.value.func if isinstance(assignment.value, ast.Call) else assignment.value
                                    result[target.attr] = {"kind": "attribute", "type_source": expression(value)}
            elif isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name) and public(member.target.id):
                result[member.target.id] = self.field(name, member)
            elif isinstance(member, ast.Assign):
                for target in member.targets:
                    if isinstance(target, ast.Name) and public(target.id):
                        result[target.id] = {"kind": "class_attribute", "value": expression(member.value)}
        return result


def snapshot(root: Path = ROOT) -> dict[str, Any]:
    surface = Surface(root)
    exports = []
    for node in surface.trees["raims"].body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            exports = ast.literal_eval(node.value)
    if not exports or any(not isinstance(name, str) for name in exports):
        raise ValueError("The package must declare its public exports.")
    symbols: dict[str, Any] = {}
    owners: dict[str, str] = {}
    for name in sorted(exports):
        target = surface.follow("raims." + name)
        definition: dict[str, Any] = {"kind": "export", "target": target}
        if name == "__version__":
            value = surface.values.get(target)
            if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
                raise ValueError("The public library version must remain a string.")
            definition = {"kind": "version", "type": "str"}
        symbols["raims." + name] = definition
        if target in surface.classes:
            owners["raims." + name] = target
    for module, tree in surface.trees.items():
        module_public = module in {"raims.models", "raims.types", "raims.services", "raims.enum_values"}
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and public(node.name):
                target = module + "." + node.name
                if module_public:
                    owners[target] = target
                elif module == "raims._client" and node.name in {"Simulations", "AsyncSimulations"}:
                    owners["raims." + node.name] = target
            elif module_public and isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name) and public(target.id):
                        definition = {"kind": "constant_or_alias", "value": expression(node.value)}
                        if isinstance(node, ast.AnnAssign):
                            definition["annotation"] = expression(node.annotation)
                        symbols[module + "." + target.id] = definition
    for owner, target in sorted(owners.items()):
        symbols[owner] = surface.class_definition(target)
        for member, definition in surface.members(target).items():
            symbols[owner + "." + member] = definition
    return {"format_version": FORMAT_VERSION, "symbols": dict(sorted(symbols.items()))}


def incompatible_symbols(expected: dict[str, Any], current: dict[str, Any]) -> list[str]:
    if expected.get("format_version") != FORMAT_VERSION or not isinstance(expected.get("symbols"), dict):
        raise ValueError("The public Python baseline format is unsupported; update it deliberately after reviewing the semantic snapshot.")
    return [name for name, value in expected["symbols"].items() if current["symbols"].get(name) != value]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Deliberately replace the reviewed compatibility baseline.")
    args = parser.parse_args()
    current = snapshot()
    baseline = ROOT / "contracts/python-api.json"
    if args.write:
        baseline.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"Wrote {len(current['symbols'])} public symbols in format {FORMAT_VERSION}. Review the baseline diff.")
        return 0
    if not baseline.is_file():
        raise ValueError("The public Python baseline is missing. Initialize it deliberately with --write and review the diff.")
    expected = json.loads(baseline.read_text(encoding="utf-8"))
    incompatible = incompatible_symbols(expected, current)
    if incompatible:
        print("Public Python compatibility changed: " + ", ".join(incompatible), file=sys.stderr)
        return 1
    print(f"Checked {len(expected['symbols'])} baseline public symbols; additions are allowed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, TypeError) as error:
        print("Compatibility check failed: " + str(error), file=sys.stderr)
        raise SystemExit(1)
