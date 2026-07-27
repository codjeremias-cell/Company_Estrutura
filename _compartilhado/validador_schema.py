"""Motor de validação de JSON Schema (subconjunto draft 2020-12).

Fonte única do que era copiado em cada `evals/validate_workflow.py`. Usa somente
a biblioteca padrão do Python: nenhum pacote de rede, nenhuma dependência nova.

Palavras-chave suportadas
-------------------------
`$ref` (só ponteiro local `#/...`), `oneOf`, `allOf`, `if`/`then`/`else`, `not`,
`type`, `const`, `enum`, `minLength`, `maxLength`, `pattern`, `format: date-time`,
`minimum`, `maximum`, `exclusiveMaximum`, `minItems`, `maxItems`, `uniqueItems`,
`items`, `contains` (+ `minContains`/`maxContains`), `required`, `properties` e
`additionalProperties: false`.

**Não** suportadas — se um schema passar a usá-las, elas são ignoradas em
silêncio, e é preciso implementá-las aqui antes de confiar na validação:
`anyOf`, `exclusiveMinimum`, `multipleOf`, `patternProperties`,
`propertyNames`, `dependentSchemas`, `prefixItems`, `$defs` remotos e
`format` diferente de `date-time`.

Ao mexer neste arquivo, rodar `python _compartilhado/teste_validador_schema.py`
e depois os validadores de todos os pacotes: um erro aqui afeta a estrutura
inteira de uma vez.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

__all__ = [
    "digest",
    "sha256_file",
    "json_pointer",
    "is_type",
    "validate_schema",
    "find_const",
    "collect_property_names",
]


def digest(char: str) -> str:
    """Digest sintético para fixtures: `digest("a")` → `sha256:aaaa…`."""
    return "sha256:" + char * 64


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def json_pointer(root: dict[str, Any], ref: str) -> Any:
    if not ref.startswith("#/"):
        raise ValueError(f"referência externa não suportada: {ref}")
    value: Any = root
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[token]
    return value


def is_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def validate_schema(
    value: Any,
    schema: dict[str, Any],
    root: dict[str, Any],
    path: str = "$",
) -> list[str]:
    """Devolve a lista de erros. Lista vazia significa válido."""
    if "$ref" in schema:
        try:
            target = json_pointer(root, schema["$ref"])
        except (KeyError, ValueError) as exc:
            return [f"{path}: $ref inválido {schema['$ref']}: {exc}"]
        return validate_schema(value, target, root, path)

    errors: list[str] = []

    if "oneOf" in schema:
        matches = [
            not validate_schema(value, candidate, root, path)
            for candidate in schema["oneOf"]
        ]
        if sum(matches) != 1:
            errors.append(f"{path}: oneOf esperava 1 alternativa, obteve {sum(matches)}")
            return errors

    for child in schema.get("allOf", []):
        errors.extend(validate_schema(value, child, root, path))

    if "if" in schema and not validate_schema(value, schema["if"], root, path):
        if "then" in schema:
            errors.extend(validate_schema(value, schema["then"], root, path))
    elif "else" in schema:
        errors.extend(validate_schema(value, schema["else"], root, path))

    if "not" in schema and not validate_schema(value, schema["not"], root, path):
        errors.append(f"{path}: valor proibido por not")

    expected_type = schema.get("type")
    if expected_type and not is_type(value, expected_type):
        return [f"{path}: tipo {type(value).__name__}, esperado {expected_type}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: {value!r} difere de const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} fora do enum")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string curta")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: string longa")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: não corresponde ao pattern")
        if schema.get("format") == "date-time":
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{path}: data/hora inválida")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: abaixo do mínimo")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: acima do máximo")
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            errors.append(f"{path}: no ou acima do máximo exclusivo")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: poucos itens")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: itens demais")
        if schema.get("uniqueItems"):
            canonical = [json.dumps(item, sort_keys=True) for item in value]
            if len(canonical) != len(set(canonical)):
                errors.append(f"{path}: itens duplicados")
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(
                    validate_schema(item, schema["items"], root, f"{path}[{index}]")
                )
        if "contains" in schema:
            matches = sum(
                not validate_schema(item, schema["contains"], root, f"{path}[{index}]")
                for index, item in enumerate(value)
            )
            minimum = schema.get("minContains", 1)
            maximum = schema.get("maxContains")
            if matches < minimum:
                errors.append(f"{path}: contains encontrou {matches}, mínimo {minimum}")
            if maximum is not None and matches > maximum:
                errors.append(f"{path}: contains encontrou {matches}, máximo {maximum}")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: chave obrigatória ausente: {key}")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                errors.extend(
                    validate_schema(item, properties[key], root, f"{path}.{key}")
                )
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: chave extra: {key}")

    return errors


def find_const(node: Any, property_name: str, expected: Any) -> bool:
    """Procura, em qualquer profundidade, `properties.<nome>.const == esperado`.

    Usado para provar que um schema de fronteira continua atribuindo a autoria de
    um envelope a quem o contrato manda.
    """
    if isinstance(node, dict):
        candidate = node.get(property_name)
        if isinstance(candidate, dict) and candidate.get("const") == expected:
            return True
        return any(find_const(child, property_name, expected) for child in node.values())
    if isinstance(node, list):
        return any(find_const(child, property_name, expected) for child in node)
    return False


def collect_property_names(node: Any, found: set[str]) -> None:
    """Coleta todo nome declarado em `properties`, em qualquer profundidade.

    Usado para provar a **ausência** de um campo proibido por ADR — por exemplo,
    campo de nota no Departamento de Auditoria (ADR-003).
    """
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict):
            found.update(properties.keys())
        for child in node.values():
            collect_property_names(child, found)
    elif isinstance(node, list):
        for child in node:
            collect_property_names(child, found)
