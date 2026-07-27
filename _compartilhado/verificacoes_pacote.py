"""Verificações estruturais comuns a todo pacote da Estrutura Final de Skills.

Implementa, uma vez só, os itens mecânicos do checklist de aceite da
`GUIA-DE-EXPANSAO-E-MIGRACAO.md`: frontmatter, limites de tamanho, interface do
runtime, arquivos obrigatórios, pasta de agentes e links internos.

Cada função devolve uma **lista de erros**; lista vazia significa conforme. Elas
não decidem o que é obrigatório — quem decide é o validador de cada pacote, que
passa os nomes, caminhos e limites.
"""

from __future__ import annotations

import re
from pathlib import Path

__all__ = [
    "read_frontmatter",
    "validate_frontmatter",
    "validate_openai_yaml",
    "validate_required_files",
    "validate_agents_folder",
    "validate_links",
    "validate_adr_series",
    "ADR_FILE_PATTERN",
    "ADR_HISTORICAL_EXCEPTIONS",
]

AGENT_REQUIRED_FILES = ("SKILL.md", "CONTRATO-DE-COMPROMISSO.md", "agents/openai.yaml")

ADR_FILE_PATTERN = re.compile(r"^adr-(\d+)-.+\.md$")

# Os três `ADR-001` que a `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 4, declara
# históricos: nasceram em camadas distintas antes da convenção da série global e
# "permanecem intactos como proveniência e **não** autorizam reuso". A isenção é
# por CAMINHO EXATO, não por número: um quarto `adr-001` em qualquer outro lugar
# quebra o grupo inteiro e é reprovado.
ADR_HISTORICAL_EXCEPTIONS = (
    "ceo-maestro/references/adr-001-hierarquia-executiva.md",
    "ceo-maestro/diretor-de-lentes/references/adr-001-diretoria-e-camada-de-juizes.md",
    "ceo-maestro/departamento-negocios/references/adr-001-rota-vigente-aos-juizes.md",
)


def read_frontmatter(path: Path) -> tuple[str, list[str]]:
    """Devolve (bloco do frontmatter, chaves na ordem em que aparecem)."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, flags=re.DOTALL)
    if not match:
        return "", []
    block = match.group(1)
    keys = [line.split(":", 1)[0].strip() for line in block.splitlines() if ":" in line]
    return block, keys


def validate_frontmatter(
    path: Path,
    expected_name: str,
    *,
    max_lines: int = 500,
    max_description: int = 1024,
) -> list[str]:
    """Frontmatter só com name/description, nome canônico e limites de tamanho."""
    if not path.is_file():
        return [f"{expected_name}: SKILL.md ausente em {path}"]
    block, keys = read_frontmatter(path)
    if not block:
        return [f"{expected_name}: SKILL.md sem frontmatter válido"]

    errors: list[str] = []
    if keys != ["name", "description"]:
        errors.append(
            f"{expected_name}: frontmatter deve ter só name/description, recebeu {keys}"
        )
    if f"name: {expected_name}" not in block:
        errors.append(f"{expected_name}: name divergente do nome canônico")

    description = re.search(
        r'^description:\s*"(.*)"$', block, flags=re.MULTILINE | re.DOTALL
    )
    if not description:
        errors.append(f"{expected_name}: description deve ser string entre aspas")
    elif len(description.group(1)) > max_description:
        errors.append(
            f"{expected_name}: description excede {max_description} caracteres "
            f"({len(description.group(1))})"
        )

    line_count = len(path.read_text(encoding="utf-8").splitlines())
    if line_count > max_lines:
        errors.append(
            f"{expected_name}: SKILL.md excede {max_lines} linhas ({line_count})"
        )
    return errors


def validate_openai_yaml(
    path: Path,
    display_name: str,
    token: str,
    *,
    expected_short: str | None = None,
    min_length: int = 25,
    max_length: int = 64,
) -> list[str]:
    """Interface do runtime: display_name, short_description e token no prompt."""
    label = path.parent.parent.name
    if not path.is_file():
        return [f"{label}: agents/openai.yaml ausente"]

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if f'display_name: "{display_name}"' not in text:
        errors.append(f"{label}: display_name divergente")
    if token not in text:
        errors.append(f"{label}: default_prompt sem {token}")

    match = re.search(r'short_description:\s*"([^"]+)"', text)
    if not match:
        errors.append(f"{label}: sem short_description")
        return errors

    short = match.group(1)
    if not min_length <= len(short) <= max_length:
        errors.append(
            f"{label}: short_description fora de {min_length}–{max_length} "
            f"({len(short)})"
        )
    if expected_short is not None and short != expected_short:
        errors.append(f"{label}: short_description divergente do contrato")
    return errors


def validate_required_files(paths: list[Path], label: str = "arquivo") -> list[str]:
    return [f"{label} ausente: {path}" for path in paths if not path.is_file()]


def validate_agents_folder(
    agents_root: Path,
    expected_names: list[str],
    *,
    required_files: tuple[str, ...] = AGENT_REQUIRED_FILES,
) -> list[str]:
    """A pasta de agentes contém exatamente os nomes canônicos, cada um completo."""
    if not agents_root.is_dir():
        return [f"pasta {agents_root.name}/ ausente"]

    errors: list[str] = []
    found = sorted(item.name for item in agents_root.iterdir() if item.is_dir())
    if found != sorted(expected_names):
        errors.append(
            f"{agents_root.name}/ deve conter exatamente {sorted(expected_names)}, "
            f"contém {found}"
        )
    for name in expected_names:
        root = agents_root / name
        for required in required_files:
            if not (root / required).is_file():
                errors.append(f"agente {name} sem {required}")
    return errors


def validate_adr_series(
    structure_root: Path,
    *,
    historical_exceptions: tuple[str, ...] = ADR_HISTORICAL_EXCEPTIONS,
) -> list[str]:
    """A série `adr-<NNN>` é global e única em TODA a estrutura.

    O passo 4 do guia manda cunhar o próximo número livre olhando todos os
    `adr-*.md` da árvore, porque o arquivo mora na pasta do dono da decisão mas o
    número é da estrutura inteira. O aviso em prosa já falhou uma vez (dois
    `adr-005`, em Registros e em QA), então a regra vale aqui, mecanicamente.

    Roda sobre a estrutura inteira e não sobre o pacote: é isso que faz a trava
    valer com frentes paralelas — qualquer validador pega a colisão do vizinho,
    mesmo que o pacote do vizinho ainda não tenha validador próprio.

    `historical_exceptions` são caminhos relativos a `structure_root`, com `/`.
    Um número só é perdoado quando **todos** os arquivos dele estão na lista; um
    arquivo novo entrando no grupo reprova o grupo inteiro.
    """
    if not structure_root.is_dir():
        return [f"série de ADR: raiz da estrutura ausente em {structure_root}"]

    root = structure_root.resolve()
    exempt = set(historical_exceptions)
    by_number: dict[int, list[str]] = {}
    for path in root.rglob("adr-*.md"):
        if not path.is_file():
            continue
        match = ADR_FILE_PATTERN.match(path.name)
        if not match:
            continue
        relative = path.resolve().relative_to(root).as_posix()
        by_number.setdefault(int(match.group(1)), []).append(relative)

    errors: list[str] = []
    for number in sorted(by_number):
        paths = sorted(by_number[number])
        if len(paths) < 2 or set(paths) <= exempt:
            continue
        errors.append(
            f"série de ADR: número {number:03d} duplicado em "
            + " e ".join(paths)
        )
    return errors


def validate_links(
    package_root: Path,
    *,
    exclude: list[Path] | None = None,
) -> list[str]:
    """Todo link markdown interno do pacote resolve em arquivo existente.

    `exclude` pula subárvores que são pacotes próprios, com validador próprio —
    assim um Departamento filho quebrado não reprova o pacote do superior.
    """
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    skipped = [item.resolve() for item in (exclude or [])]
    errors: list[str] = []
    for path in sorted(package_root.rglob("*.md")):
        if any(path.resolve().is_relative_to(item) for item in skipped):
            continue
        text = path.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                errors.append(f"link quebrado em {path.name}: {target}")
    return errors
