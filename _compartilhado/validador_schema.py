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
    "DigestDeFixtureRecusado",
    "digest",
    "sha256_file",
    "sha256_texto_normalizado",
    "digest_declarado",
    "conferir_digest_declarado",
    "conferir_digest_das_regras",
    "conferir_marcacao_da_proveniencia",
    "MARCADOR_HISTORICO",
    "MARCADOR_DIGEST_DECLARADO",
    "RECEITA_DIGEST_NORMALIZADO",
    "json_pointer",
    "is_type",
    "validate_schema",
    "find_const",
    "collect_property_names",
]


class DigestDeFixtureRecusado(ValueError):
    """`digest()` recebeu algo que não é UM caractere.

    Classe própria, e não um `ValueError` genérico, por uma razão já medida
    nesta casa: **mutante que morre por exceção qualquer é mutante creditado
    errado** — 7 de 11 saíram assim numa medição. Com classe própria, o caso
    que prova a recusa afirma ESTA classe, e uma explosão vinda de qualquer
    outro ponto do código não consegue se passar pela trava.
    """


def digest(char: str) -> str:
    """Digest sintético para fixtures: `digest("a")` → `sha256:aaaa…`.

    **RECUSA** entrada que não seja exatamente um caractere.

    Isto nunca foi um digest: é um gerador de valor de teste com a forma que os
    schemas exigem. Três validadores canônicos passaram o **schema inteiro**
    aqui dentro e publicaram o resultado como «digest do próprio schema é
    verificável» — e `digest(<qualquer coisa>).startswith("sha256:")` é
    verdadeiro por construção, logo a linha não podia ficar vermelha.

    A trava está aqui, no código, e não num aviso em prosa: esta casa já
    documentou armadilha em texto e viu a mesma repetir quatro vezes.

    Para digerir um arquivo real: `sha256_file()`.
    Para digerir texto sem depender do fim de linha: `sha256_texto_normalizado()`.
    """
    if not isinstance(char, str) or len(char) != 1:
        recebido = (
            f"str de {len(char)} caractere(s)"
            if isinstance(char, str)
            else f"{type(char).__name__}"
        )
        raise DigestDeFixtureRecusado(
            "digest() é gerador de fixture e aceita UM caractere; recebeu "
            f"{recebido}.\n"
            "  · escrevendo um validador VIGENTE: para digerir um arquivo use "
            "sha256_file(); para digerir texto use sha256_texto_normalizado().\n"
            "  · reexecutando EVIDÊNCIA CONGELADA de campanha encerrada "
            "(evals/<campanha>/...): NÃO reescreva o arquivo. Ele foi escrito "
            "contra o motor do commit dele; alterá-lo para ficar verde "
            "falsifica registro. Rode-o contra o _compartilhado daquele commit."
        )
    return "sha256:" + char * 64


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


# --- digest declarado × digest recomputado ---------------------------------
#
# `sha256_file` mede os BYTES DO CHECKOUT. O mesmo conteúdo em CRLF e em LF dá
# dois valores — a lição `digest-de-arquivo-nao-e-identidade` desta casa. Uma
# conferência de conteúdo que use bytes crus fica vermelha num clone sem que
# um caractere tenha mudado, e vermelho que mente é tão inútil quanto verde que
# mente. Por isso a conferência de CONTEÚDO normaliza; a de BYTES continua
# existindo, com outro nome, para quem precisa dela.

RECEITA_DIGEST_NORMALIZADO = (
    "sha256 sobre os bytes UTF-8 do arquivo, BOM removido e CRLF trocado por "
    "LF — _compartilhado/validador_schema.py::sha256_texto_normalizado"
)

MARCADOR_DIGEST_DECLARADO = "DIGEST-NORMATIVO:"

_RE_DIGEST_DECLARADO = re.compile(
    MARCADOR_DIGEST_DECLARADO + r"\s*`?(sha256:[0-9a-f]{64})`?"
)
_RE_SHA256 = re.compile(r"sha256:[0-9a-f]{64}")


def sha256_texto_normalizado(path: Path) -> str:
    """SHA-256 do CONTEÚDO: BOM fora, `CRLF` vira `LF`, bytes UTF-8.

    Para `regras-de-ouro/REGRAS-DE-OURO.md` este valor é idêntico ao do blob
    que o git guarda, porque o git também guarda em LF. Medido em 2026-08-04.
    """
    dados = path.read_bytes()
    if dados.startswith(b"\xef\xbb\xbf"):
        dados = dados[3:]
    return "sha256:" + hashlib.sha256(dados.replace(b"\r\n", b"\n")).hexdigest()


def digest_declarado(path: Path) -> tuple[str | None, str]:
    """Lê o valor DECLARADO num arquivo de proveniência.

    Devolve `(valor, estado)`. Quando não há valor, `valor` é `None` e `estado`
    é o **nome da ausência** — ausência nunca vira `True` por omissão.
    """
    if not path.is_file():
        return None, f"AUSENTE_ARQUIVO_DE_PROVENIENCIA: {path}"
    achados = _RE_DIGEST_DECLARADO.findall(path.read_text(encoding="utf-8"))
    if not achados:
        return None, (
            f"AUSENTE_DIGEST_DECLARADO: {path} não traz nenhuma linha "
            f"'{MARCADOR_DIGEST_DECLARADO} sha256:<64 hex minúsculos>'"
        )
    distintos = sorted(set(achados))
    if len(distintos) > 1:
        return None, (
            f"DIGEST_DECLARADO_AMBIGUO: {path} declara {len(distintos)} valores "
            f"diferentes ({', '.join(distintos)}); um artefato tem uma identidade"
        )
    return distintos[0], "DECLARADO"


def conferir_digest_declarado(
    path: Path,
    declarado: str | None,
    rotulo: str,
) -> list[str]:
    """Recomputa e COMPARA. Lista vazia significa que confere.

    Devolve lista — nunca levanta — porque o chamador é um caso de eval: a
    morte precisa ser **pela trava**, aparecendo como caso vermelho, e não por
    exceção que derruba o validador inteiro e não diz qual condição falhou.
    """
    if not path.is_file():
        return [f"AUSENTE_ARTEFATO: {rotulo} não existe em {path}"]
    if not isinstance(declarado, str) or not _RE_SHA256.fullmatch(declarado):
        return [
            f"AUSENTE_DIGEST_DECLARADO: {rotulo} sem valor declarado utilizável "
            f"({declarado!r}); sem valor declarado não há o que conferir"
        ]
    recomputado = sha256_texto_normalizado(path)
    if recomputado != declarado:
        return [
            f"DIGEST_DIVERGENTE: {rotulo} em {path} — declarado {declarado}, "
            f"recomputado {recomputado}; receita: {RECEITA_DIGEST_NORMALIZADO}"
        ]
    return []


def conferir_digest_das_regras(
    rules_path: Path,
    origem_path: Path | None = None,
) -> list[str]:
    """A fonte normativa confere com o valor declarado na sua proveniência.

    O valor declarado mora em `regras-de-ouro/ORIGEM.md`, irmão do arquivo
    normativo — **um artefato, uma identidade, um lugar**. Replicar o valor no
    contrato de cada pacote criaria 10 declarações do mesmo objeto, sem árbitro
    para a primeira divergência, e faria cada pacote autenticar contra a própria
    cópia a norma que ele deve obedecer.
    """
    origem = origem_path if origem_path is not None else rules_path.with_name("ORIGEM.md")
    if not rules_path.is_file():
        return [f"AUSENTE_FONTE_NORMATIVA: {rules_path}"]
    erros = conferir_marcacao_da_proveniencia(origem)
    valor, estado = digest_declarado(origem)
    if valor is None:
        return erros + [estado]
    return erros + conferir_digest_declarado(
        rules_path, valor, "fonte normativa REGRAS-DE-OURO.md"
    )



# --- valor com forma de digest solto no arquivo de proveniência -------------
#
# `ORIGEM.md` é, por definição, o arquivo que guarda a história — e história de
# digest é uma lista de SHA-256. Isso colide com a regra de máquina «exatamente
# um marcador vigente», e a colisão já produziu dano medido: o valor
# `197736D2…`, escrito em MAIÚSCULAS e sem prefixo na posição de autoridade do
# arquivo (linha 6), não corresponde a nenhuma versão do arquivo em nenhum
# commit — e `_RE_DIGEST_DECLARADO` não o enxerga, porque só casa 64 hex
# minúsculos precedidos do marcador. Um editor futuro que atualizasse a linha 6
# criaria uma segunda verdade que nenhuma trava veria.
#
# A regra, então, não é sobre o marcador: é sobre a FORMA. Todo valor com cara
# de SHA-256 dentro do arquivo de proveniência declara se está em vigor ou não.
# Quem não declara vira erro nomeado. Isso deixa o histórico possível — basta
# marcá-lo — e torna impossível o valor órfão silencioso.

MARCADOR_HISTORICO = "HISTORICO-NAO-VIGENTE:"

_RE_QUALQUER_SHA256 = re.compile(r"\b[0-9a-fA-F]{64}\b")


def conferir_marcacao_da_proveniencia(origem_path: Path) -> list[str]:
    """Nenhum valor com forma de SHA-256 fica sem dizer se está em vigor."""
    if not origem_path.is_file():
        return [f"AUSENTE_ARQUIVO_DE_PROVENIENCIA: {origem_path}"]
    erros: list[str] = []
    for numero, linha in enumerate(
        origem_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not _RE_QUALQUER_SHA256.search(linha):
            continue
        if MARCADOR_DIGEST_DECLARADO in linha or MARCADOR_HISTORICO in linha:
            continue
        erros.append(
            f"DIGEST_SEM_MARCACAO: {origem_path}:{numero} traz um valor com "
            f"forma de SHA-256 e não diz se vale: use "
            f"'{MARCADOR_DIGEST_DECLARADO}' para o vigente ou "
            f"'{MARCADOR_HISTORICO}' para o que já não vale. Valor sem marca "
            "vira segunda verdade que nenhuma trava enxerga"
        )
    return erros

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
