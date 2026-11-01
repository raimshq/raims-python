from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from decimal import Decimal, DecimalException
from importlib.resources import files
from typing import Any

from ._errors import UnexpectedResponseError
from ._resource import ApiResource
from ._response import LastResponse

CONTRACT: dict[str, Any] = json.loads(
    files("raims").joinpath("_generated/contract.json").read_text(encoding="utf-8")
)
_MAX_NESTING = 100


def _decimal(value: str) -> int | Decimal:
    number = Decimal(value)
    if number == number.to_integral_value():
        if number.adjusted() > 4300:
            raise ValueError("JSON integer exceeds the supported size.")
        return int(number)
    return number


def _invalid_constant(value: str) -> Any:
    raise ValueError("JSON numbers must be finite.")


def parse_json(payload: bytes) -> Any:
    try:
        return json.loads(
            payload.decode("utf-8", errors="strict"),
            parse_float=_decimal,
            parse_constant=_invalid_constant,
        )
    except DecimalException:
        raise ValueError("The JSON number cannot be represented.") from None


def resolve(schema: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in schema:
        return CONTRACT["schemas"][schema["$ref"].rsplit("/", 1)[-1]]
    return schema


def validate_response(
    value: Any, schema: dict[str, Any], response: LastResponse | None, depth: int = 0
) -> None:
    def fail() -> Any:
        raise UnexpectedResponseError(
            "The API response does not match the published structure.", last_response=response
        )

    if depth > _MAX_NESTING:
        fail()
    if "$ref" in schema:
        return validate_response(value, resolve(schema), response, depth + 1)
    if "anyOf" in schema or "oneOf" in schema:
        for variant in schema.get("anyOf", schema.get("oneOf", [])):
            try:
                validate_response(value, variant, response, depth + 1)
                return
            except UnexpectedResponseError:
                continue
        fail()
    for part in schema.get("allOf", []):
        validate_response(value, part, response, depth + 1)
    kinds = schema.get("type", [])
    if isinstance(kinds, str):
        kinds = [kinds]
    if value is None:
        if not kinds or "null" in kinds or schema.get("nullable"):
            return
        fail()
    kind = next((t for t in kinds if t != "null"), None)
    if kind == "object" or "properties" in schema:
        if not isinstance(value, dict):
            fail()
        if any(key not in value for key in schema.get("required", [])):
            fail()
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties")
        for key, child in value.items():
            child_schema = properties.get(key, additional if isinstance(additional, dict) else {})
            validate_response(child, child_schema, response, depth + 1)
    elif kind == "array":
        if not isinstance(value, list):
            fail()
        for item in value:
            validate_response(item, schema.get("items", {}), response, depth + 1)
    else:
        match kind:
            case "integer":
                if type(value) is not int:
                    fail()
            case "number":
                if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
                    fail()
            case "boolean":
                if type(value) is not bool:
                    fail()
            case "string":
                if not isinstance(value, str):
                    fail()
            case "null":
                fail()


def _check_json_depth(value: Any, response: LastResponse | None) -> None:
    pending: list[tuple[Iterator[Any], int]] = [(iter((value,)), 0)]
    while pending:
        iterator, depth = pending[-1]
        try:
            current = next(iterator)
        except StopIteration:
            pending.pop()
            continue
        if depth > _MAX_NESTING:
            raise UnexpectedResponseError(
                "The API response nesting exceeds the supported depth.", last_response=response
            )
        if isinstance(current, dict):
            pending.append((iter(current.values()), depth + 1))
        elif isinstance(current, list):
            pending.append((iter(current), depth + 1))


def hydrate(
    value: Any,
    schema: dict[str, Any] | None = None,
    response: LastResponse | None = None,
    *,
    _depth: int = 0,
) -> Any:
    if _depth == 0:
        _check_json_depth(value, response)
    schema = schema or {}
    model_name = schema.get("$ref", "").rsplit("/", 1)[-1]
    schema = resolve(schema)
    if "anyOf" in schema or "oneOf" in schema:
        for variant in schema.get("anyOf", schema.get("oneOf", [])):
            try:
                validate_response(value, variant, response)
                return hydrate(value, variant, response, _depth=_depth + 1)
            except UnexpectedResponseError:
                continue
    if isinstance(value, dict):
        from . import models

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", {})
        data = {
            key: hydrate(
                item,
                properties.get(key, additional if isinstance(additional, dict) else {}),
                _depth=_depth + 1,
            )
            for key, item in value.items()
        }
        model = getattr(models, model_name, ApiResource) if model_name else ApiResource
        if not isinstance(model, type) or not issubclass(model, ApiResource):
            model = ApiResource
        return model(data, last_response=response)
    if isinstance(value, list):
        return tuple(hydrate(item, schema.get("items", {}), _depth=_depth + 1) for item in value)
    return value


def serialize_params(value: Mapping[str, Any]) -> bytes:
    def visit(item: Any, seen: set[int], depth: int) -> Any:
        if depth > _MAX_NESTING:
            raise ValueError("Request parameters are nested too deeply.")
        if item is None or type(item) in (str, int, float, bool):
            return item
        if not isinstance(item, (Mapping, list, tuple)):
            raise TypeError("Request parameters must contain only JSON values.")
        if id(item) in seen:
            raise ValueError("Request parameters cannot contain cycles.")
        seen.add(id(item))
        try:
            if isinstance(item, Mapping):
                if any(not isinstance(key, str) for key in item):
                    raise ValueError("JSON object keys must be strings.")
                return {key: visit(child, seen, depth + 1) for key, child in item.items()}
            return [visit(child, seen, depth + 1) for child in item]
        finally:
            seen.remove(id(item))

    try:
        return json.dumps(
            visit(value, set(), 0), ensure_ascii=False, allow_nan=False, separators=(",", ":")
        ).encode("utf-8")
    except (ValueError, OverflowError, UnicodeError, RecursionError):
        raise ValueError("Request parameters must contain valid finite JSON values.") from None
