#!/usr/bin/env python3
"""Validador determinístico e autocontido dos invariantes do CEO Maestro."""

from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "ceo-maestro.schema.json"
EVALS_PATH = ROOT / "evals" / "evals.json"
RULES_PATH = ROOT.parent / "regras-de-ouro" / "REGRAS-DE-OURO.md"
JUDGE_SCHEMA_PATH = (
    ROOT / "diretor-de-lentes" / "departamento-juizes" / "schemas"
    / "departamento-juizes.schema.json"
)
DIRECTOR_SCHEMA_PATH = (
    ROOT / "diretor-de-lentes" / "schemas" / "diretor-de-lentes.schema.json"
)

sys.path.insert(0, str(ROOT.parent))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        digest,
        sha256_file,
        sha256_texto_normalizado,
        validate_schema,
    )
    from _compartilhado.verificacoes_estrutura import (
    digests_truncados_sem_original,
    validate_exclusoes_declaradas,
    validate_tetos_no_pacote,  # noqa: E402
        recusar_execucao_fora_da_fonte,
        validate_adr_series,
        validate_cobertura_de_validadores,
        validate_contratos_de_gerente,
        validate_fonte_normativa_conferida,
        validate_placar_nao_declara_cadeia,
        validate_contagem_ligada_ao_instrumento,
        validate_travas_compartilhadas_com_efeito,
        validate_pendencia_tem_dono,
        achar_limite_sem_dono,
        validate_limite_residual_tem_dono,
        validate_sem_check_tautologico,
        validate_trava_de_digest,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print(
        "[FAIL] motor compartilhado ausente em "
        f"{ROOT.parent}/_compartilhado: {exc}"
    )
    raise SystemExit(1)
except ImportError as exc:  # pragma: no cover
    # `ModuleNotFoundError` é SUBCLASSE de `ImportError`: o handler acima não
    # captura o pai. Sem este segundo braço, aplicar os validadores sem o
    # `_compartilhado` atualizado mata o processo por traceback, sem sumário e
    # sem dizer qual condição faltou — o modo de falha que este candidato
    # existe para repudiar. Medido na rodada 1: dez validadores assim.
    print(
        "[FAIL] OVERLAY_APLICADO_PELA_METADE: _compartilhado existe mas não "
        f"expõe o que este validador importa ({exc}). Este conjunto é "
        "INDIVISÍVEL: validadores e _compartilhado/ se aplicam no mesmo ato, "
        "ou a fonte normativa fica sem conferência nenhuma."
    )
    raise SystemExit(1)
REQUIRED_LEVELS = {"PRODUCAO": 10, "INTERNO": 7}
DIRECT_EXECUTIVES = {
    "diretor-de-lentes",
    "departamento-negocios",
    "departamento-evolucao-skills",
}
REQUIRED_GATES = {
    "critical_fail_absent",
    "rules_compliant",
    "done_proved",
    "blocking_pending_absent",
    "integrity_valid",
    "authority_reconciled",
}


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def add_if(errors: list[str], condition: bool, message: str) -> None:
    if condition:
        errors.append(message)


def required_target(required_level: Any) -> int | None:
    return REQUIRED_LEVELS.get(required_level)


def band_for(score: int) -> str:
    if score == 10:
        return "VALIDATED"
    if score >= 7:
        return "ACEITO_USO_INTERNO"
    return "REPROVED"


def external_verdict(
    minimum_score: int | None,
    critical_fail: Any = False,
    blocking_pending_refs: Any = None,
    score_range: Any = None,
) -> str:
    if (
        minimum_score is None
        or critical_fail is not False
        or blocking_pending_refs != []
    ):
        return "REPROVED"
    # ADR-016: faixa que atravessa um corte não vira veredito — sai como
    # NAO_DISCRIMINADO, que não alcança nenhum required_level. Falha crítica e
    # pendência bloqueante já reprovaram acima: quem falhou gate está reprovado,
    # não indiscriminado.
    if (
        isinstance(score_range, dict)
        and band_for(score_range["lo"]) != band_for(score_range["hi"])
    ):
        return "NAO_DISCRIMINADO"
    if minimum_score <= 6:
        return "REPROVED"
    return band_for(minimum_score)


def level_reached(verdict: Any, required_level: Any) -> bool:
    # ADR-016: NAO_DISCRIMINADO não alcança nenhum nível.
    return verdict == "VALIDATED" or (
        required_level == "INTERNO" and verdict == "ACEITO_USO_INTERNO"
    )


def required_list(
    artifact: dict[str, Any], field: str, errors: list[str]
) -> list[Any]:
    value = artifact.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"{field}: lista não vazia obrigatória")
        return []
    return value


def valid_digest(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return False
    hexadecimal = value[7:]
    return len(hexadecimal) == 64 and all(c in "0123456789abcdef" for c in hexadecimal)


def resolve_local_ref(schema: dict[str, Any], ref: str) -> Any:
    if not ref.startswith("#/"):
        raise ValueError(f"referência externa não permitida: {ref}")
    current: Any = schema
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        current = current[token]
    return current


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    add_if(
        errors,
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema",
        "schema: draft esperado não declarado",
    )
    definitions = schema.get("$defs")
    add_if(errors, not isinstance(definitions, dict), "schema: $defs ausente")
    expected = {
        "executiveMission",
        "judgeReport",
        "limitationReport",
        "exceptionRequest",
        "exceptionAuthorization",
        "executiveSubmission",
        "executiveDecision",
        "capabilityGap",
    }
    if isinstance(definitions, dict):
        missing = expected - set(definitions)
        add_if(errors, bool(missing), f"schema: definições ausentes: {sorted(missing)}")
        if not missing:
            score_schema = definitions["scoreItem"]["properties"]["score"]
            add_if(
                errors,
                score_schema.get("type") != "integer",
                "schema: score externo deve ser inteiro",
            )
            for definition_name in (
                "executiveMission",
                "judgeReport",
                "exceptionRequest",
                "executiveDecision",
            ):
                definition = definitions[definition_name]
                add_if(
                    errors,
                    "required_level" not in definition.get("required", []),
                    f"schema: {definition_name}.required_level deve ser obrigatório",
                )
                level_schema = definition.get("properties", {}).get(
                    "required_level", {}
                )
                add_if(
                    errors,
                    set(level_schema.get("enum", [])) != set(REQUIRED_LEVELS),
                    f"schema: {definition_name}.required_level diverge do ADR-014",
                )
            judge_verdicts = set(
                definitions["judgeReport"]["properties"]["verdict"].get("enum", [])
            )
            add_if(
                errors,
                judge_verdicts
                != {
                    "VALIDATED",
                    "ACEITO_USO_INTERNO",
                    "REPROVED",
                    "NAO_DISCRIMINADO",
                },
                "schema: vereditos externos divergem do ADR-014 e do ADR-016",
            )
            # ADR-016: os campos que sustentam NAO_DISCRIMINADO são obrigatórios.
            for campo in (
                "minimum_score_range",
                "instances_per_lens",
                "aggregation_rule",
            ):
                add_if(
                    errors,
                    campo not in definitions["judgeReport"].get("required", []),
                    f"schema: judgeReport.{campo} deve ser obrigatório",
                )
            add_if(
                errors,
                set(definitions.get("aggregationMethod", {}).get("enum", []))
                != {"MENOR", "MEDIANA", "EMPATE_DECLARADO"},
                "schema: métodos de agregação divergem do ADR-016",
            )
            decision_states = set(
                definitions["executiveDecision"]["properties"]["decision"].get(
                    "enum", []
                )
            )
            add_if(
                errors,
                "ACEITO_USO_INTERNO" not in decision_states,
                "schema: decisão executiva não representa aceite interno",
            )
            integer_fields = {
                "judgeReport": ("minimum_score",),
                "limitationReport": (
                    "current_minimum_score",
                    "best_attainable_score",
                ),
                "exceptionRequest": ("actual_minimum_score",),
                "exceptionAuthorization": ("actual_minimum_score",),
                "executiveDecision": ("minimum_score",),
            }
            for definition_name, fields in integer_fields.items():
                properties = definitions[definition_name].get("properties", {})
                for field in fields:
                    add_if(
                        errors,
                        properties.get(field, {}).get("type") != "integer",
                        f"schema: {definition_name}.{field} deve ser inteiro",
                    )
            add_if(
                errors,
                set(
                    definitions["exceptionRequest"]["properties"]["cutoff_score"].get(
                        "enum", []
                    )
                )
                != set(REQUIRED_LEVELS.values()),
                "schema: alvos de exceção devem ser 7 e 10",
            )

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str):
                try:
                    resolve_local_ref(schema, ref)
                except (KeyError, TypeError, ValueError) as exc:
                    errors.append(f"schema: $ref inválida {ref}: {exc}")
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(schema)
    return errors


def validate_package_files(evals: dict[str, Any]) -> list[str]:
    """Cobre o DoD estrutural sem depender de PyYAML ou pacotes de rede."""
    errors: list[str] = []
    skill_path = ROOT / "SKILL.md"
    skill_text = skill_path.read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\r?\n(.*?)\r?\n---", skill_text, re.DOTALL)
    if frontmatter is None:
        errors.append("package: frontmatter de SKILL.md ausente ou inválido")
    else:
        header = frontmatter.group(1)
        name_match = re.search(r"^name:\s*([^\r\n]+)$", header, re.MULTILINE)
        description_match = re.search(
            r'^description:\s*"([^"\r\n]+)"$', header, re.MULTILINE
        )
        name = name_match.group(1).strip() if name_match else ""
        description = description_match.group(1) if description_match else ""
        add_if(
            errors,
            re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is None,
            "package: name deve ser kebab-case",
        )
        add_if(errors, name != "ceo-maestro", "package: name divergente")
        add_if(
            errors,
            not 1 <= len(description) <= 1024,
            "package: description ausente ou acima de 1024 caracteres",
        )
        add_if(
            errors,
            "Acione" not in description,
            "package: description sem frase-gatilho Acione",
        )
        add_if(
            errors,
            "NÃO" not in description,
            "package: description sem fronteira negativa",
        )
    add_if(
        errors,
        len(skill_text.splitlines()) > 500,
        "package: SKILL.md deve permanecer com no máximo 500 linhas",
    )
    add_if(
        errors,
        "## 🔗 Rede da skill" not in skill_text,
        "package: bloco Rede da skill ausente",
    )

    openai_path = ROOT / "agents" / "openai.yaml"
    if not openai_path.exists():
        errors.append("package: agents/openai.yaml ausente")
    else:
        openai_text = openai_path.read_text(encoding="utf-8")
        short_match = re.search(
            r'^\s*short_description:\s*"([^"\r\n]+)"$',
            openai_text,
            re.MULTILINE,
        )
        short = short_match.group(1) if short_match else ""
        add_if(
            errors,
            not 25 <= len(short) <= 64,
            "package: short_description deve ter 25..64 caracteres",
        )
        add_if(
            errors,
            "$ceo-maestro" not in openai_text,
            "package: default_prompt deve citar $ceo-maestro",
        )

    required_paths = [
        ROOT / "CONTRATO-DE-COMPROMISSO.md",
        ROOT / "schemas" / "ceo-maestro.schema.json",
        ROOT / "references" / "bootstrap.md",
        ROOT / "references" / "comunicacao.md",
        ROOT / "references" / "gate-qualidade-e-excecao.md",
        ROOT / "references" / "protocolo-de-handoff.md",
        ROOT / "references" / "workflow-executivo.md",
        ROOT.parent / "AGENTS.md",
        ROOT.parent / "regras-de-ouro" / "REGRAS-DE-OURO.md",
    ]
    for path in required_paths:
        add_if(errors, not path.is_file(), f"package: arquivo obrigatório ausente {path}")

    # O CEO confere os próprios arquivos e os da raiz da estrutura. Pacote aninhado
    # — Diretor, Departamentos, agentes — tem validador próprio e responde por si:
    # um filho em construção não reprova o pai (GUIA-DE-EXPANSAO-E-MIGRACAO.md, §2).
    ceo_owned = {
        ROOT,
        ROOT / "references",
        ROOT / "schemas",
        ROOT / "evals",
        ROOT / "agents",
    }
    for markdown in ROOT.parent.rglob("*.md"):
        if markdown.is_relative_to(ROOT) and markdown.parent not in ceo_owned:
            continue
        text = markdown.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            clean = target.split("#", 1)[0]
            if not clean or "://" in clean:
                continue
            resolved = (markdown.parent / clean).resolve()
            add_if(
                errors,
                not resolved.exists(),
                f"package: link quebrado em {markdown.name}: {target}",
            )

    cases = evals.get("cases")
    if not isinstance(cases, list):
        errors.append("evals: cases deve ser lista")
    else:
        for index, case in enumerate(cases):
            if not isinstance(case, dict):
                errors.append(f"evals[{index}]: objeto obrigatório")
                continue
            add_if(
                errors,
                case.get("origem") not in {"real", "sintetico"},
                f"evals[{index}].origem: inválida",
            )
            for field in ("id", "prompt", "data_geracao", "sessao_geracao"):
                add_if(
                    errors,
                    not isinstance(case.get(field), str) or not case[field].strip(),
                    f"evals[{index}].{field}: obrigatório",
                )
            required_list(case, "assertions", errors)
    return errors


def validate_schema_keys(
    schema: dict[str, Any],
    definition_name: str,
    artifact: dict[str, Any],
    label: str,
) -> list[str]:
    """Detecta deriva de nomes entre exemplos/fixtures e o contrato JSON."""
    errors: list[str] = []
    definition = schema["$defs"][definition_name]
    required = set(definition.get("required", []))
    properties = set(definition.get("properties", {}))
    missing = required - set(artifact)
    extra = set(artifact) - properties
    add_if(errors, bool(missing), f"{label}: campos obrigatórios ausentes {sorted(missing)}")
    if definition.get("additionalProperties") is False:
        add_if(errors, bool(extra), f"{label}: campos fora do schema {sorted(extra)}")
    causal = artifact.get("causal")
    if isinstance(causal, dict):
        causal_definition = schema["$defs"]["causalHeader"]
        causal_required = set(causal_definition.get("required", []))
        causal_properties = set(causal_definition.get("properties", {}))
        missing_causal = causal_required - set(causal)
        extra_causal = set(causal) - causal_properties
        add_if(
            errors,
            bool(missing_causal),
            f"{label}.causal: campos ausentes {sorted(missing_causal)}",
        )
        add_if(
            errors,
            bool(extra_causal),
            f"{label}.causal: campos fora do schema {sorted(extra_causal)}",
        )
    return errors


def validate_causal(
    causal: Any,
    expected_producers: set[str],
    errors: list[str],
    expected_candidate: str | None = None,
) -> None:
    if not isinstance(causal, dict):
        errors.append("causal: cabeçalho obrigatório")
        return
    for field in (
        "work_item_id",
        "front_id",
        "handoff_id",
        "message_id",
        "causation_message_ids",
        "contract_id",
        "contract_version",
        "contract_digest",
        "candidate_digest",
        "round",
        "attempt",
        "producer",
        "producer_version",
        "producer_digest",
        # RODADA 8 — a receita ao lado do numero. Ela so existia em prosa
        # nao normativa e alcancou 17 envelopes em 7 rodadas sem que
        # nenhum leitor conseguisse reproduzi-la.
        "producer_digest_recipe",
        "created_at",
    ):
        add_if(errors, field not in causal, f"causal.{field}: obrigatório")
    add_if(
        errors,
        causal.get("producer") not in expected_producers,
        f"causal.producer: produtor inválido {causal.get('producer')!r}",
    )
    add_if(
        errors,
        not valid_digest(causal.get("producer_digest")),
        "causal.producer_digest: SHA-256 inválido",
    )
    add_if(
        errors,
        not valid_digest(causal.get("contract_digest")),
        "causal.contract_digest: SHA-256 inválido",
    )
    candidate = causal.get("candidate_digest")
    add_if(
        errors,
        candidate != "n/a" and not valid_digest(candidate),
        "causal.candidate_digest: SHA-256 ou n/a obrigatório",
    )
    if expected_candidate is not None:
        add_if(
            errors,
            candidate != expected_candidate,
            "causal.candidate_digest: diverge do artefato",
        )
    add_if(
        errors,
        not isinstance(causal.get("causation_message_ids"), list),
        "causal.causation_message_ids: lista obrigatória",
    )
    for field in ("round", "attempt"):
        value = causal.get(field)
        add_if(
            errors,
            not isinstance(value, int) or isinstance(value, bool) or value < 1,
            f"causal.{field}: inteiro positivo obrigatório",
        )
    try:
        parse_time(causal["created_at"])
    except (KeyError, TypeError, ValueError):
        errors.append("causal.created_at: timestamp inválido")


def applicable_minimum(report: dict[str, Any], errors: list[str]) -> int | None:
    scorecard = required_list(report, "scorecard", errors)
    scores: list[int] = []
    for index, item in enumerate(scorecard):
        if not isinstance(item, dict):
            errors.append(f"scorecard[{index}]: objeto obrigatório")
            continue
        if item.get("applicable") is True:
            score = item.get("score")
            if not isinstance(score, int) or isinstance(score, bool):
                errors.append(f"scorecard[{index}].score: inteiro obrigatório")
            elif not 0 <= score <= 10:
                errors.append(f"scorecard[{index}].score: fora de 0..10")
            else:
                scores.append(score)
            required_list(item, "evidence_refs", errors)
    if not scores:
        errors.append("scorecard: ao menos uma nota aplicável")
        return None
    return min(scores)


def validate_judge_report(report: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(report, dict):
        return ["judge_report: objeto obrigatório"]
    add_if(
        errors,
        report.get("artifact_type") != "JUDGE_REPORT",
        "judge_report.artifact_type: inválido",
    )
    validate_causal(
        report.get("causal"),
        {"departamento-juizes"},
        errors,
        report.get("candidate_digest"),
    )
    add_if(
        errors,
        report.get("judge_capability_ref") != "departamento-juizes",
        "judge_report: capacidade julgadora inválida",
    )
    for field in ("candidate_digest", "judge_capability_digest"):
        add_if(
            errors,
            not valid_digest(report.get(field)),
            f"judge_report.{field}: SHA-256 inválido",
        )
    required_level = report.get("required_level")
    add_if(
        errors,
        required_target(required_level) is None,
        "judge_report.required_level: PRODUCAO ou INTERNO obrigatório",
    )
    calculated = applicable_minimum(report, errors)
    declared = report.get("minimum_score")
    if calculated is not None:
        add_if(
            errors,
            not isinstance(declared, int)
            or isinstance(declared, bool)
            or declared != calculated,
            f"judge_report.minimum_score: esperado {calculated}, recebido {declared!r}",
        )
    blockers = report.get("blocking_pending_refs")
    add_if(
        errors,
        not isinstance(blockers, list),
        "judge_report.blocking_pending_refs: lista obrigatória",
    )
    required_list(report, "evidence_refs", errors)
    critical = report.get("critical_fail")
    verdict = report.get("verdict")
    # ADR-016: a faixa é o dado; o ponto é a leitura conservadora dela.
    score_range = report.get("minimum_score_range")
    instances = report.get("instances_per_lens")
    if not isinstance(score_range, dict):
        errors.append("judge_report.minimum_score_range: objeto obrigatório")
        score_range = None
    else:
        lo, hi = score_range.get("lo"), score_range.get("hi")
        add_if(
            errors,
            not isinstance(lo, int) or not isinstance(hi, int) or lo > hi,
            "judge_report.minimum_score_range: faixa inválida ou invertida",
        )
        if calculated is not None:
            add_if(
                errors,
                lo != calculated,
                "judge_report.minimum_score_range.lo: deve ser a menor consolidação",
            )
        add_if(
            errors,
            instances == 1 and lo != hi,
            "judge_report: faixa aberta com uma única instância por lente",
        )
        add_if(
            errors,
            not isinstance(instances, int)
            or isinstance(instances, bool)
            or not 1 <= instances <= 5,
            "judge_report.instances_per_lens: inteiro de 1 a 5 obrigatório",
        )
    rule = report.get("aggregation_rule")
    if not isinstance(rule, dict):
        errors.append("judge_report.aggregation_rule: objeto obrigatório")
    else:
        add_if(
            errors,
            rule.get("method") not in {"MENOR", "MEDIANA", "EMPATE_DECLARADO"},
            "judge_report.aggregation_rule.method: fora do enum do ADR-016",
        )
        add_if(
            errors,
            not rule.get("declared_at"),
            "judge_report.aggregation_rule: sem declared_at",
        )
    expected_verdict = external_verdict(calculated, critical, blockers, score_range)
    add_if(
        errors,
        verdict != expected_verdict,
        "judge_report.verdict: incompatível com a faixa medida, falha crítica ou bloqueios",
    )
    try:
        add_if(
            errors,
            parse_time(report["expires_at"]) <= parse_time(report["issued_at"]),
            "judge_report: expires_at deve ser posterior a issued_at",
        )
    except (KeyError, TypeError, ValueError):
        errors.append("judge_report: timestamps inválidos")
    return errors


def validate_limitation_report(
    report: Any, judge_report: dict[str, Any] | None = None
) -> list[str]:
    errors: list[str] = []
    if not isinstance(report, dict):
        return ["limitation_report: objeto obrigatório"]
    add_if(
        errors,
        report.get("artifact_type") != "LIMITATION_REPORT",
        "limitation_report.artifact_type: inválido",
    )
    submitter = report.get("submitted_by")
    add_if(
        errors,
        submitter not in DIRECT_EXECUTIVES,
        "limitation_report.submitted_by: não é interlocutor direto",
    )
    validate_causal(
        report.get("causal"),
        DIRECT_EXECUTIVES,
        errors,
        report.get("candidate_digest"),
    )
    if isinstance(report.get("causal"), dict):
        add_if(
            errors,
            report["causal"].get("producer") != submitter,
            "limitation_report: produtor causal diverge do autor",
        )
    for field in ("candidate_digest", "score_snapshot_digest"):
        add_if(
            errors,
            not valid_digest(report.get(field)),
            f"limitation_report.{field}: SHA-256 inválido",
        )
    current = report.get("current_minimum_score")
    best = report.get("best_attainable_score")
    required_level = (
        judge_report.get("required_level")
        if isinstance(judge_report, dict)
        else None
    )
    target = required_target(required_level)
    add_if(
        errors,
        target is None
        or not isinstance(current, int)
        or isinstance(current, bool)
        or not 0 <= current < target,
        "limitation_report.current_minimum_score: deve ser inteiro abaixo do alvo do nível",
    )
    add_if(
        errors,
        target is None
        or not isinstance(best, int)
        or isinstance(best, bool)
        or not 0 <= best < target,
        "limitation_report.best_attainable_score: deve ser inteiro abaixo do alvo do nível",
    )
    if isinstance(current, int) and isinstance(best, int):
        add_if(
            errors,
            float(best) < float(current),
            "limitation_report: melhor nota atingível não pode ser menor que a atual",
        )
    below = required_list(report, "below_cutoff_evaluations", errors)
    for index, item in enumerate(below):
        if not isinstance(item, dict):
            errors.append(f"below_cutoff_evaluations[{index}]: objeto obrigatório")
            continue
        add_if(
            errors,
            item.get("applicable") is not True,
            f"below_cutoff_evaluations[{index}]: deve ser aplicável",
        )
        score = item.get("score")
        add_if(
            errors,
            target is None
            or not isinstance(score, int)
            or isinstance(score, bool)
            or not 0 <= score < target,
            f"below_cutoff_evaluations[{index}].score: deve ser inteiro abaixo do alvo do nível",
        )
        required_list(item, "evidence_refs", errors)
    for field in (
        "objective_factors",
        "attempted_remediations",
        "alternatives_assessed",
        "why_gap_cannot_close",
        "residual_risks",
        "mitigations",
        "requested_scope",
        "evidence_refs",
    ):
        required_list(report, field, errors)
    verification = report.get("independent_verification")
    if not isinstance(verification, dict):
        errors.append("limitation_report.independent_verification: obrigatória")
    else:
        expected = {
            "reviewer": "departamento-juizes",
            "verdict": "VERIFIED_IMPOSSIBILITY",
            "independence_confirmed": True,
            "all_below_cutoff_criteria_covered": True,
        }
        for field, value in expected.items():
            add_if(
                errors,
                verification.get(field) != value,
                f"independent_verification.{field}: esperado {value!r}",
            )
        add_if(
            errors,
            not valid_digest(verification.get("reviewer_digest")),
            "independent_verification.reviewer_digest: SHA-256 inválido",
        )
        required_list(verification, "evidence_refs", errors)
        add_if(
            errors,
            not isinstance(verification.get("dissent_refs"), list),
            "independent_verification.dissent_refs: lista obrigatória",
        )
    if judge_report is not None:
        reconcile_contracts(
            [
                ("JUDGE_REPORT", judge_report),
                ("LIMITATION_REPORT", report),
            ],
            errors,
        )
        add_if(
            errors,
            report.get("candidate_digest") != judge_report.get("candidate_digest"),
            "limitation_report: candidato diverge do JUDGE_REPORT",
        )
        add_if(
            errors,
            current != judge_report.get("minimum_score"),
            "limitation_report: nota atual diverge do JUDGE_REPORT",
        )
        expected_below = {
            item.get("criterion_id"): item.get("score")
            for item in judge_report.get("scorecard", [])
            if isinstance(item, dict)
            and item.get("applicable") is True
            and isinstance(item.get("score"), int)
            and not isinstance(item.get("score"), bool)
            and target is not None
            and item.get("score") < target
        }
        actual_below = {
            item.get("criterion_id"): item.get("score")
            for item in below
            if isinstance(item, dict)
        }
        add_if(
            errors,
            actual_below != expected_below,
            "limitation_report: avaliações abaixo do corte não cobrem exatamente o JUDGE_REPORT",
        )
    return errors


def gates_all_pass(gates: Any) -> bool:
    return (
        isinstance(gates, dict)
        and set(gates) == REQUIRED_GATES
        and all(gates.get(field) is True for field in REQUIRED_GATES)
    )


def reconcile_contracts(
    artifacts: list[tuple[str, dict[str, Any] | None]], errors: list[str]
) -> None:
    baseline_name = ""
    baseline_key: tuple[Any, ...] | None = None
    for name, artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        causal = artifact.get("causal")
        if not isinstance(causal, dict):
            continue
        key = (
            causal.get("work_item_id"),
            causal.get("contract_id"),
            causal.get("contract_version"),
            causal.get("contract_digest"),
        )
        if baseline_key is None:
            baseline_name = name
            baseline_key = key
            continue
        add_if(
            errors,
            key != baseline_key,
            f"contrato causal: {name} diverge de {baseline_name}",
        )


def validate_exception_request(
    request: Any,
    judge_report: dict[str, Any],
    limitation_report: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(request, dict):
        return ["exception_request: objeto obrigatório"]
    add_if(
        errors,
        request.get("artifact_type") != "EXCEPTION_REQUEST",
        "exception_request.artifact_type: inválido",
    )
    validate_causal(
        request.get("causal"),
        {"ceo-maestro"},
        errors,
        request.get("candidate_digest"),
    )
    add_if(
        errors,
        request.get("requested_authority") != "jeremias",
        "exception_request: autoridade deve ser Jeremias",
    )
    add_if(
        errors,
        required_target(request.get("required_level")) is None,
        "exception_request.required_level: PRODUCAO ou INTERNO obrigatório",
    )
    add_if(
        errors,
        request.get("required_level") != judge_report.get("required_level"),
        "exception_request.required_level: diverge do JUDGE_REPORT",
    )
    add_if(
        errors,
        request.get("cutoff_score")
        != required_target(request.get("required_level")),
        "exception_request.cutoff_score: diverge do alvo do nível",
    )
    add_if(
        errors,
        request.get("actual_minimum_score") != judge_report.get("minimum_score"),
        "exception_request: nota diverge do JUDGE_REPORT",
    )
    target = required_target(request.get("required_level"))
    actual = request.get("actual_minimum_score")
    add_if(
        errors,
        target is None
        or not isinstance(actual, int)
        or isinstance(actual, bool)
        or not 0 <= actual < target,
        "exception_request: nota deve ser inteira e inferior ao alvo do nível",
    )
    add_if(
        errors,
        judge_report.get("critical_fail") is not False
        or judge_report.get("blocking_pending_refs") != [],
        "exception_request: falha crítica ou bloqueio não é dispensável",
    )
    add_if(
        errors,
        request.get("judge_report_ref") != judge_report.get("report_id"),
        "exception_request.judge_report_ref: divergente",
    )
    add_if(
        errors,
        request.get("limitation_report_ref") != limitation_report.get("report_id"),
        "exception_request.limitation_report_ref: divergente",
    )
    add_if(
        errors,
        request.get("actual_minimum_score") != limitation_report.get(
            "current_minimum_score"
        ),
        "exception_request: nota diverge do LIMITATION_REPORT",
    )
    for source in (judge_report, limitation_report):
        add_if(
            errors,
            request.get("candidate_digest") != source.get("candidate_digest"),
            "exception_request: candidato divergente",
        )
    reconcile_contracts(
        [
            ("JUDGE_REPORT", judge_report),
            ("LIMITATION_REPORT", limitation_report),
            ("EXCEPTION_REQUEST", request),
        ],
        errors,
    )
    add_if(
        errors,
        request.get("score_snapshot_digest")
        != limitation_report.get("score_snapshot_digest"),
        "exception_request: snapshot divergente",
    )
    add_if(
        errors,
        not gates_all_pass(request.get("nonwaivable_gates")),
        "exception_request: todos os gates inegociáveis devem passar",
    )
    for field in ("requested_scope", "residual_risks", "mitigations"):
        required_list(request, field, errors)
    try:
        add_if(
            errors,
            parse_time(request["expires_at"]) <= parse_time(request["issued_at"]),
            "exception_request: expiração inválida",
        )
    except (KeyError, TypeError, ValueError):
        errors.append("exception_request: timestamps inválidos")
    return errors


def validate_authorization(
    authorization: Any,
    request: dict[str, Any],
    decision_time: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(authorization, dict):
        return ["exception_authorization: objeto obrigatório"]
    add_if(
        errors,
        authorization.get("artifact_type") != "EXCEPTION_AUTHORIZATION",
        "exception_authorization.artifact_type: inválido",
    )
    add_if(
        errors,
        authorization.get("authorized_by") != "jeremias",
        "exception_authorization: somente Jeremias pode autorizar",
    )
    add_if(
        errors,
        authorization.get("exception_request_id") != request.get("request_id"),
        "exception_authorization: pedido divergente",
    )
    for field in ("candidate_digest", "score_snapshot_digest"):
        add_if(
            errors,
            authorization.get(field) != request.get(field),
            f"exception_authorization.{field}: diverge do pedido",
        )
    add_if(
        errors,
        authorization.get("actual_minimum_score")
        != request.get("actual_minimum_score"),
        "exception_authorization: nota diverge do pedido",
    )
    add_if(
        errors,
        authorization.get("scope") != request.get("requested_scope"),
        "exception_authorization: escopo diverge do pedido",
    )
    add_if(
        errors,
        not isinstance(authorization.get("citation_exact"), str)
        or len(authorization["citation_exact"].strip()) < 10,
        "exception_authorization: citação explícita ausente",
    )
    add_if(
        errors,
        authorization.get("usage_policy") != "single_use",
        "exception_authorization: uso deve ser único",
    )
    if authorization.get("decision") == "APPROVED":
        add_if(
            errors,
            authorization.get("status") not in {"AUTHORIZED", "CONSUMED"},
            "exception_authorization: status incompatível com aprovação",
        )
    else:
        add_if(
            errors,
            authorization.get("status") not in {"REVOKED", "EXPIRED"},
            "exception_authorization: rejeição não pode autorizar",
        )
    try:
        issued = parse_time(authorization["issued_at"])
        expires = parse_time(authorization["expires_at"])
        request_issued = parse_time(request["issued_at"])
        request_expires = parse_time(request["expires_at"])
        add_if(errors, expires <= issued, "exception_authorization: expiração inválida")
        add_if(
            errors,
            not request_issued <= issued <= request_expires,
            "exception_authorization: emitida fora da vigência do EXCEPTION_REQUEST",
        )
        if decision_time is not None:
            decided = parse_time(decision_time)
            add_if(
                errors,
                not issued <= decided <= expires,
                "exception_authorization: não vigente no momento da decisão",
            )
            add_if(
                errors,
                decided > request_expires,
                "exception_authorization: decisão ocorreu após expirar o pedido",
            )
    except (KeyError, TypeError, ValueError):
        errors.append("exception_authorization: timestamps inválidos")
    return errors


# ===========================================================================
# T96 — uma missão não pode proibir o dono da evidência que sua própria
# barreira de saída exige.
# ---------------------------------------------------------------------------
# O QUE ISTO CONSERTA, com hora. A missão 46 (T71/C10, 2026-08-21) declarou
# `judge_gate_required: true` e dirigiu-se apenas ao `departamento-evolucao-skills`,
# proibindo em `stop_when` "qualquer tentativa de julgar" e restringindo
# `spawn_agent` aos agentes do próprio Departamento. Só que o `executiveSubmission`
# exige `judge_report` e `governance_report` NÃO NULOS, e nenhum dos dois admite
# forma de ausência declarada: `judgeReport` pede 18 campos e um `verdict` de
# enum fechado; `governanceReport` pede 14 e `COMPLIANT|NONCOMPLIANT`.
#
# Nenhuma execução podia satisfazer as duas cláusulas. O resultado foi o
# `EVOLUTION_CAPABILITY_GAP` 16 — que estava CORRETO e era INEVITÁVEL. Consertar
# a instância (reemitir a missão) deixaria o contrato capaz de gerar o mesmo
# impasse na campanha seguinte; é conserto-de-instância, não de mecanismo.
#
# PRIMEIRA TENTATIVA MINHA, DESCARTADA PELA PRÓPRIA CASA — e o registro fica porque
# a hipótese era plausível e estava errada. Tentei derivar a proibição de
# `recipients`: se a missão exige `judge_report` e não chama quem alcança os Juízes,
# seria insatisfazível. A bateria derrubou em duas linhas: o caso canônico
# `missão executiva admite Evolução de Skills` tem `judge_gate_required: true` e
# `required_level: "PRODUCAO"` com `recipients` só da Evolução, e é declarado
# VÁLIDO; e a `submissão executiva admite Evolução de Skills` volta com
# `judge_report` real. O modelo desta casa é que o parecer chega pela CADEIA DO CEO,
# não pelo destinatário — logo `recipients` não decide satisfatibilidade, e a regra
# que eu escrevi reprovaria a rota legítima.
#
# O DEFEITO REAL DA 46, relido no CAPABILITY_GAP 16: *"a missão proíbe acionar
# Diretor, Juízes ou Auditoria e proíbe julgar"*. A proibição é o fato — e ela vivia
# só em PROSA (`stop_when`, e um `allowed_tools` que restringia `spawn_agent` ao
# próprio Departamento). Caçar essa prosa seria detector cego ao formato: a próxima
# missão escreveria a mesma proibição com outras palavras e passaria.
#
# POR ISSO O CONSERTO DE MECANISMO É TORNAR A PROIBIÇÃO ESTRUTURAL. O envelope ganha
# `forbidden_actors`, opcional para não falsificar registro passado (mesma disciplina
# do `bloqueada_por` do estado), e a trava compara:
#   * QUEM produz cada relatório está `const` no schema — `judge_capability_ref` é
#     `departamento-juizes`, `auditor_ref` é `departamento-auditoria-responsabilidades`.
#     A trava LÊ do schema em vez de repetir o nome, senão vira mais uma cópia que
#     envelhece sozinha.
#   * QUEM a missão proíbe passa a ser um campo, não uma frase.
# Missão que proíbe o dono de uma evidência que sua própria barreira de saída exige
# morre na EMISSÃO, em vez de morrer seis passos adiante como CAPABILITY_GAP.
# ===========================================================================

_EVIDENCIAS_DA_BARREIRA = (
    # (campo do executiveSubmission, $defs do relatório, campo que fixa o dono)
    ("judge_report", "judgeReport", "judge_capability_ref"),
    ("governance_report", "governanceReport", "auditor_ref"),
)


@lru_cache(maxsize=1)
def _schema_do_ceo() -> dict[str, Any]:
    try:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _dono_da_evidencia(deff: str, campo: str) -> str | None:
    """O `const` que o schema fixa como emissor daquele relatório.

    Lido DO SCHEMA, de propósito: repetir o nome aqui criaria uma quarta cópia,
    que a próxima edição do schema deixaria para trás em silêncio.
    """
    try:
        propriedades = _schema_do_ceo()["$defs"][deff]["properties"]
    except (KeyError, TypeError):
        return None
    valor = propriedades.get(campo)
    if isinstance(valor, dict):
        const = valor.get("const")
        if isinstance(const, str) and const:
            return const
    return None


def _missao_nao_proibe_dono_de_evidencia(mission: dict[str, Any]) -> list[str]:
    """Nenhum ator proibido pela missão é dono de evidência que a saída dela exige.

    `governance_report` é exigido pelo `executiveSubmission` SEMPRE; `judge_report`
    entra quando a própria missão declara `judge_gate_required: true`. Proibir o dono
    de qualquer um dos dois torna a barreira de saída insatisfazível — e é melhor
    saber disso na emissão do que seis passos adiante.
    """
    errors: list[str] = []
    proibidos = mission.get("forbidden_actors")
    if proibidos is None:
        return errors  # campo opcional: envelope antigo continua válido
    if not isinstance(proibidos, list):
        return errors  # forma inválida já é acusada pelo schema; não duplicamos
    proibidos_set = {p for p in proibidos if isinstance(p, str)}
    if not proibidos_set:
        return errors

    exigidas = [_EVIDENCIAS_DA_BARREIRA[1] + ("o executiveSubmission sempre o exige",)]
    if mission.get("judge_gate_required") is True:
        exigidas.insert(0, _EVIDENCIAS_DA_BARREIRA[0] + ("judge_gate_required=true",))

    for campo, deff, chave, porque in exigidas:
        dono = _dono_da_evidencia(deff, chave)
        if dono is None:
            errors.append(
                f"BARREIRA_SEM_DONO: o schema não fixa {deff}.{chave}; sem isso a "
                f"trava não sabe quem produz {campo} e NÃO conclui nada sobre a missão"
            )
            continue
        if dono in proibidos_set:
            errors.append(
                f"MISSAO_INSATISFAZIVEL: a missão proíbe {dono} em forbidden_actors, "
                f"e só {dono} produz {campo} — que a barreira de saída exige "
                f"({porque}). Nenhuma execução satisfaz as duas cláusulas ao mesmo "
                "tempo: é o impasse que gerou o CAPABILITY_GAP 16 da missão 46. "
                "Ou o ator sai da proibição, ou a missão declara que não devolve "
                "EXECUTIVE_SUBMISSION"
            )
    return errors


# As amostras isolam UMA evidência cada, e isso não é preciosismo: com uma única
# amostra que proíbe os dois donos, remover `judge_report` ou `governance_report` da
# barreira deixaria a outra acusando sozinha — o mutante sobreviveria e a regra
# removida ficaria sem prova. É a mesma correção que a T55 precisou fazer quando o
# mutante da REGRA 1 sobreviveu porque a REGRA 2 pegava o mesmo caso.
_AMOSTRA_BARREIRA_COERENTE = {
    "forbidden_actors": ["departamento-negocios"],
    "judge_gate_required": True,
}
_AMOSTRA_SO_JUIZES = {
    "forbidden_actors": ["departamento-juizes"],
    "judge_gate_required": True,
}
_AMOSTRA_SO_AUDITORIA = {
    # sem judge_gate: só `governance_report` sustenta a acusação aqui
    "forbidden_actors": ["departamento-auditoria-responsabilidades"],
    "judge_gate_required": False,
}
_AMOSTRA_BARREIRA_INSATISFAZIVEL = {
    "forbidden_actors": [
        "departamento-juizes",
        "departamento-auditoria-responsabilidades",
    ],
    "judge_gate_required": True,
}


def _autoteste_da_barreira() -> list[str]:
    """A trava prova que enxerga — e que não grita no inocente — a cada chamada.

    Mesmo remédio de `_autoteste_da_cobertura` e `_autoteste_da_recusa`, e pelo
    mesmo motivo: detector que quebra ISENTA em silêncio, e aqui isentar significa
    voltar a emitir missões insatisfazíveis sem que nada acuse.
    """
    try:
        coerente = _missao_nao_proibe_dono_de_evidencia(_AMOSTRA_BARREIRA_COERENTE)
        so_juizes = _missao_nao_proibe_dono_de_evidencia(_AMOSTRA_SO_JUIZES)
        so_auditoria = _missao_nao_proibe_dono_de_evidencia(_AMOSTRA_SO_AUDITORIA)
        impasse = _missao_nao_proibe_dono_de_evidencia(_AMOSTRA_BARREIRA_INSATISFAZIVEL)
    except Exception as exc:  # noqa: BLE001
        return [
            "DETECTOR_DE_BARREIRA_QUEBRADO: o autoteste levantou "
            f"{exc.__class__.__name__}: {exc}"
        ]
    erros: list[str] = []
    if coerente:
        erros.append(
            "DETECTOR_DE_BARREIRA_GRITA_NO_INOCENTE: a missão que proíbe apenas um "
            f"ator SEM evidência na barreira foi acusada — {coerente}; trava que "
            "reprova proibição legítima é desligada na semana seguinte, não obedecida"
        )
    if not so_juizes:
        erros.append(
            "DETECTOR_DE_BARREIRA_CEGO: proibir SÓ os Juízes com "
            "judge_gate_required=true não foi acusado; a regra do judge_report não "
            "está sendo exercitada"
        )
    if not so_auditoria:
        erros.append(
            "DETECTOR_DE_BARREIRA_CEGO: proibir SÓ a Auditoria não foi acusado; o "
            "executiveSubmission exige governance_report SEMPRE, e a regra dele não "
            "está sendo exercitada"
        )
    if not impasse:
        erros.append(
            "DETECTOR_DE_BARREIRA_CEGO: a missão da forma da 46 (proíbe Juízes e "
            "Auditoria com judge_gate_required=true) NÃO foi acusada; detector que "
            "não vê o impasse conhecido isenta a árvore inteira em silêncio"
        )
    return erros


def validate_mission(mission: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(mission, dict):
        return ["mission: objeto obrigatório"]
    add_if(
        errors,
        mission.get("artifact_type") != "EXECUTIVE_MISSION",
        "mission.artifact_type: inválido",
    )
    validate_causal(mission.get("causal"), {"ceo-maestro"}, errors, "n/a")
    recipients = required_list(mission, "recipients", errors)
    add_if(
        errors,
        not set(recipients).issubset(DIRECT_EXECUTIVES),
        "mission: CEO tentou chamar capacidade fora dos três pares executivos",
    )
    add_if(
        errors,
        mission.get("return_to") != "ceo-maestro",
        "mission.return_to: inválido",
    )
    add_if(
        errors,
        required_target(mission.get("required_level")) is None,
        "mission.required_level: PRODUCAO ou INTERNO obrigatório",
    )
    matrix = mission.get("matrix_exchange")
    if not isinstance(matrix, dict):
        errors.append("mission.matrix_exchange: obrigatória")
    else:
        if len(recipients) == 2:
            add_if(
                errors,
                matrix.get("allowed") is not True,
                "mission: missão mista deve autorizar troca matricial",
            )
            for field in ("topics", "read_scope", "write_scope"):
                required_list(matrix, field, errors)
            add_if(
                errors,
                matrix.get("consolidation_owner") not in set(recipients),
                "mission: dono da consolidação deve ser um destinatário",
            )
        else:
            add_if(
                errors,
                matrix.get("allowed") is not False,
                "mission: troca matricial deve iniciar negada com um destinatário",
            )
            for field in ("topics", "read_scope", "write_scope"):
                add_if(
                    errors,
                    matrix.get(field) != [],
                    f"mission.matrix_exchange.{field}: deve estar vazio",
                )
            add_if(
                errors,
                matrix.get("consolidation_owner") is not None,
                "mission: missão simples não tem dono matricial",
            )
    add_if(
        errors,
        mission.get("deliverable_type") not in {"analysis", "product", "proposal"},
        "mission.deliverable_type: inválido",
    )
    if mission.get("deliverable_type") in {"product", "proposal"}:
        add_if(
            errors,
            mission.get("judge_gate_required") is not True,
            "mission: produto/proposta exige gate dos Juízes",
        )
    for field in ("scope_in", "acceptance_criteria", "required_evidence", "stop_when"):
        required_list(mission, field, errors)
    for field in ("scope_out", "constraints", "decisions_binding", "dependencies"):
        add_if(
            errors,
            not isinstance(mission.get(field), list),
            f"mission.{field}: lista obrigatória",
        )
    permissions = mission.get("permissions")
    if not isinstance(permissions, dict):
        errors.append("mission.permissions: obrigatório")
    else:
        add_if(
            errors,
            permissions.get("default_policy") != "deny",
            "mission.permissions.default_policy: deve ser deny",
        )
        for field in ("allowed_tools", "allowed_resources"):
            add_if(
                errors,
                not isinstance(permissions.get(field), list),
                f"mission.permissions.{field}: lista obrigatória",
            )
    # T96 — a missão não pode proibir o dono da evidência que sua própria
    # barreira de saída exige. O autoteste vem junto: detector que quebra ISENTA
    # em silêncio, e isentar aqui é voltar a emitir missões insatisfazíveis.
    errors.extend(_autoteste_da_barreira())
    errors.extend(_missao_nao_proibe_dono_de_evidencia(mission))
    return errors


# ---------------------------------------------------------------------------
# A ALEGAÇÃO QUE A BARREIRA LÊ — rodada 5
# ---------------------------------------------------------------------------
#
# Os dois textos são os mesmos de
# `departamento-auditoria-responsabilidades/scripts/inspecao_executada.py`, e
# os mesmos `const` do schema. Três lugares, e é de propósito: alargar a
# alegação passa a exigir três edições, e uma só derruba a barreira.
ALEGACAO_DO_COMPLIANT = (
    "COMPLIANT certifica exatamente isto: nenhum valor deste envelope foi aceito como digitado quando divergia da evidência reaberta. Toda âncora declarada foi reaberta contra a raiz auditada, cada citação foi conferida no byte, cada total foi recontado dos recibos em disco e cada estado da matriz foi rederivado dos mesmos recibos."
)
NAO_COBERTO_PELA_ALEGACAO = (
    "COMPLIANT NÃO certifica que a evidência não foi forjada. Forjar a evidência é chamar as mesmas funções que a verificam: medido por origem independente em 2026-08-02 (OI-04) a 80 linhas, 0,031 s, 1 tentativa, 4 arquivos lidos e zero conhecimento do conteúdo auditado. Atacante e verificador compartilham o código, o processo e a árvore; fechar isto exige âncora externa ao pacote, que não cabe no runtime atual."
)

# ---------------------------------------------------------------------------
# RODADA 7, OI6-01 — OS QUATRO LIMITES RESIDUAIS, POR IGUALDADE EXATA
# ---------------------------------------------------------------------------
#
# O que estava medido, e o que o proprio comentario do codigo ja dizia
# --------------------------------------------------------------------
# Dos ONZE limites que o envelope carrega, SETE (`declared_limits`) eram
# exigidos por `id` com `const`/`enum` — igualdade exata — e QUATRO (`pending`:
# R6, R9, R10, R11) por PREFIXO ABERTO. `OI6-01` mediu a assimetria: a lista
# `["R6 x", "R9 x", "R10 x", "R11 x"]` atravessava o schema E esta barreira, e
# `"R6 "` sozinho tambem.
#
# O mais duro do achado nao e o buraco: e que o comentario ao lado do proprio
# `IDS_DOS_LIMITES_DE_B`, logo acima, JA DIAGNOSTICAVA o mecanismo como quebrado
# — "sob ela o texto vigente, o texto RETIRADO e um 'R6 — qualquer coisa' eram
# indistinguiveis" (`OI5-08`) — e o mantinha vivo para os quatro. O diagnostico
# correto convivia com o defeito porque estava em PROSA e nao em codigo. E isso
# que acaba aqui.
#
# Os quatro textos abaixo sao copia byte a byte das constantes
# `TEXTO_R6`, `TEXTO_R9`, `TEXTO_R10` e `TEXTO_R11` de
# `departamento-auditoria-responsabilidades/scripts/emitir_governanca.py`, e sao
# os mesmos `const` dos dois schemas — a mesma disciplina de tres lugares que
# `ALEGACAO_DO_COMPLIANT` ja usava. Alargar um limite passa a exigir tres
# edicoes, e uma so derruba a barreira.
TEXTO_R6 = (
    'R6 — a existência do painel auditor não é verificável pelo runtime; sob porta única a inspeção é executada em papel pela gerente. A âncora NÃO impede a fabricação, e o custo dela está medido: recibos íntegros que reabrem foram forjados em 80 linhas e 0,031 s, com 1 tentativa (OI-04, 2026-08-02).'
)
TEXTO_R9 = (
    'R9 — a âncora prova que UM arquivo da raiz auditada foi reaberto na versão declarada; ela NÃO liga a dimensão ao artefato que deveria sustentá-la. Pertinência de evidência é mérito, e mérito é dos Juízes (R5). (Este limite viajava como R8 até a rodada 3, e colidia com o R8 do §7, bypass para fora.)'
)
TEXTO_R10 = (
    'R10 — nada assina este envelope. Edição do arquivo posterior à gravação é invisível ao emissor E ao validador, e o consumidor pode ler um veredito que o emissor não produziu. A defesa correspondente é o CONSUMIDOR recomputar o envelope a partir do ledger e do candidato, e ela mora fora deste pacote. Medido pela sonda S14-ENVELOPE-EDITADO.'
)
TEXTO_R11 = (
    "R11 — TETO DO MÉTODO: forjar a evidência é chamar as mesmas funções que "
    "a verificam. Derivar da evidência protege contra valor DIGITADO; não "
    "protege contra quem CHAMA o derivador, porque atacante e verificador "
    "compartilham o código, o processo e a árvore. Medido por origem "
    "independente em 2026-08-02 (OI-04): 80 linhas, 0,031 s, 1 tentativa, 4 "
    "arquivos lidos, zero conhecimento do conteúdo auditado. Fechar isto "
    "exige âncora externa ao pacote — runtime separado, assinatura fora da "
    "árvore ou terceiro que não compartilhe o processo — e não cabe no "
    "runtime atual. Este envelope NÃO carrega defesa contra isto e não obriga "
    "nenhuma: a origem independente dos casos foi retirada do envelope na "
    "rodada 8, e o limite permanece ABERTO."
)
TEXTO_DE_CADA_LIMITE = {
    "R6": TEXTO_R6,
    "R9": TEXTO_R9,
    "R10": TEXTO_R10,
    "R11": TEXTO_R11,
}



def validate_governance_report(
    report: Any, submission: dict[str, Any] | None = None
) -> list[str]:
    errors: list[str] = []
    if not isinstance(report, dict):
        return ["governance_report: objeto obrigatório"]
    add_if(
        errors,
        report.get("auditor_ref") != "departamento-auditoria-responsabilidades",
        "governance_report.auditor_ref: capacidade inválida",
    )
    add_if(
        errors,
        not valid_digest(report.get("auditor_digest")),
        "governance_report.auditor_digest: SHA-256 inválido",
    )
    if isinstance(submission, dict):
        add_if(
            errors,
            report.get("candidate_digest") != submission.get("candidate_digest"),
            "governance_report.candidate_digest: diverge da submissão",
        )
        add_if(
            errors,
            report.get("contract_digest")
            != submission.get("causal", {}).get("contract_digest"),
            "governance_report.contract_digest: diverge da submissão",
        )
    add_if(
        errors,
        report.get("rules_digest") != sha256_file(RULES_PATH),
        "governance_report.rules_digest: diverge das Regras de Ouro vigentes",
    )
    verdict = report.get("verdict")
    violations = report.get("violations")
    add_if(
        errors,
        verdict not in {"COMPLIANT", "NONCOMPLIANT"},
        "governance_report.verdict: inválido",
    )
    add_if(
        errors,
        not isinstance(violations, list),
        "governance_report.violations: lista obrigatória",
    )
    if isinstance(violations, list):
        add_if(
            errors,
            verdict == "COMPLIANT" and bool(violations),
            "governance_report: COMPLIANT não pode ocultar violações",
        )
        add_if(
            errors,
            verdict == "NONCOMPLIANT" and not violations,
            "governance_report: NONCOMPLIANT deve listar violações",
        )
    # ADR-018 — a barreira do CEO confere a identidade do candidato.
    #
    # O schema já exige `candidate_identity_status: CONFERIDO` para COMPLIANT.
    # A conferência é repetida aqui, na semântica, porque quem lê o relatório na
    # barreira é este código, e uma exigência que mora só no schema desaparece
    # para quem chama `validate_governance_report` direto. Em 2026-08-01 os
    # Juízes mediram o custo de não ter este campo: pelo caminho documentado, com
    # `candidate_digest` falso, saía `COMPLIANT` gravando `sha256:ffff…`, e nada
    # no envelope distinguia identidade conferida de identidade nunca recomputada.
    add_if(
        errors,
        verdict == "COMPLIANT"
        and report.get("candidate_identity_status") != "CONFERIDO",
        "governance_report: COMPLIANT sem candidate_identity_status CONFERIDO — a"
        " identidade do candidato não foi recomputada, e ausência de conferência"
        " não vira conferência por silêncio",
    )
    required_list(report, "evidence_refs", errors)
    # ADR-018, rodada 4 — os limites residuais chegam COM o envelope.
    #
    # A SKILL.md da Auditoria (passo 6) afirma que quem lê o envelope na barreira
    # lê R6, R9 e R10 "no próprio artefato, e não precisa lembrar deles de fora".
    # Até a rodada 3 isso era falso aqui: o `governanceReport` não tinha `pending`
    # e o schema o proibia. A exigência é repetida nesta função, e não só no
    # schema, porque quem lê o relatório na barreira é este código — exigência que
    # mora só no schema some para quem chama `validate_governance_report` direto.
    pendencias = report.get("pending")
    add_if(
        errors,
        not isinstance(pendencias, list),
        "governance_report.pending: lista obrigatória — os limites residuais"
        " viajam com o envelope",
    )
    if isinstance(pendencias, list):
        for limite in ("R6", "R9", "R10"):
            add_if(
                errors,
                not any(
                    isinstance(linha, str) and linha.startswith(f"{limite} ")
                    for linha in pendencias
                ),
                f"governance_report.pending: sem o limite {limite} — quem lê na"
                " barreira teria de lembrar dele de fora do artefato",
            )
        # RODADA 7, OI6-01 — A IGUALDADE EXATA, AO LADO DO PREFIXO.
        #
        # A exigência por prefixo, acima, NÃO sai: ela continua acusando a
        # ausência do identificador, e o piso desta rodada é zero travas
        # desligadas. O que entra é a exigência de que o texto seja o texto —
        # byte a byte igual à constante do emissor. Sob o prefixo sozinho,
        # `"R6 x"` e o texto RETIRADO da rodada 5 eram indistinguíveis da versão
        # vigente para esta barreira.
        for limite in ("R6", "R9", "R10"):
            add_if(
                errors,
                not any(
                    linha == TEXTO_DE_CADA_LIMITE[limite] for linha in pendencias
                ),
                f"governance_report.pending: o limite {limite} não é o texto"
                " vigente, byte a byte. Prefixo aberto aceitava"
                f" {limite!r} + qualquer coisa, e foi assim que a alegação"
                " retirada sobreviveu em prosa que nenhuma trava varria"
                " (OI6-01, OI5-08)",
            )
    # --- RODADA 8: A IDENTIDADE DO PACOTE, NA BARREIRA ---------------------
    #
    # Entra porque protege algo que o pacote AINDA afirma: a propria identidade.
    # `C07` da rodada 7 mediu que a arvore do candidato REPRODUZ com o manifesto
    # mentiroso dentro dela, e o instrumento padrao fica verde sobre a declaracao
    # falsa. O schema ja proibe o par COMPLIANT/DIVERGENTE; esta linha existe
    # porque quem chama a barreira direto nao passa pelo schema.
    add_if(
        errors,
        report.get("candidate_manifest_status") not in
        ("CONFERIDO", "SEM_MANIFESTO", "DIVERGENTE"),
        "governance_report.candidate_manifest_status: obrigatorio e com estado"
        " nomeado — sem ele quem decide na barreira nao distingue um pacote que"
        " se identifica de um que carrega o manifesto de outro candidato",
    )
    add_if(
        errors,
        verdict == "COMPLIANT"
        and report.get("candidate_manifest_status") == "DIVERGENTE",
        "governance_report: COMPLIANT com manifesto DIVERGENTE — o pacote"
        " entregue nao diz de si a verdade, e digest de arvore nao detecta isso"
        " porque o manifesto mentiroso e membro da arvore",
    )
    # --- RODADA 5: a alegação, NA BARREIRA --------------------------------
    #
    # A exigência é repetida aqui, e não só no schema, pelo mesmo motivo de
    # `pending`: quem chama `validate_governance_report` direto não passa pelo
    # schema, e uma exigência que mora num lugar só some para metade dos
    # consumidores.
    alegacao = report.get("compliance_claim")
    add_if(
        errors,
        not isinstance(alegacao, dict),
        "governance_report.compliance_claim: obrigatório — quem decide na"
        " barreira precisa ler o que COMPLIANT certifica, e o que ele NÃO"
        " certifica, sem reabrir artefato nenhum",
    )
    if isinstance(alegacao, dict):
        add_if(
            errors,
            alegacao.get("certifies") != ALEGACAO_DO_COMPLIANT,
            "governance_report.compliance_claim.certifies: não é a alegação"
            " vigente — alegação alargada no envelope é o defeito que a rodada"
            " 5 existe para impedir",
        )
        add_if(
            errors,
            alegacao.get("does_not_certify") != NAO_COBERTO_PELA_ALEGACAO,
            "governance_report.compliance_claim.does_not_certify: não é o teto"
            " vigente — um COMPLIANT sem o limite ao lado promete cobertura"
            " contra forja, que o mecanismo não tem",
        )
    if isinstance(pendencias, list):
        add_if(
            errors,
            not any(
                isinstance(linha, str) and linha.startswith("R11 ")
                for linha in pendencias
            ),
            "governance_report.pending: sem o TETO R11 — o limite que governa o"
            " significado do binário não chegou a quem decide",
        )
        # RODADA 7, OI6-01 — o TETO também por igualdade exata. Um `R11` cujo
        # texto não seja o texto é um teto que diz outra coisa, e o teto é o
        # limite que governa o significado do binário inteiro.
        add_if(
            errors,
            not any(linha == TEXTO_DE_CADA_LIMITE["R11"] for linha in pendencias),
            "governance_report.pending: o TETO R11 não é o texto vigente, byte a"
            " byte — 'R11 ' + qualquer coisa passava por teto",
        )
    # --- TAREFA 105: O LIMITE RESIDUAL NOMEIA DONO E CONDIÇÃO -------------
    #
    # Achado #1 da reconciliação da tarefa 47, e o painel externo de
    # 2026-08-05 já o tinha pontuado: as declarações de limite "são honestas
    # e completas, mas majoritariamente NÃO ACIONÁVEIS — ninguém está na
    # linha por elas". Os quatro limites fixos já eram cobrados por texto
    # exato acima; o que NADA cobrava era a ressalva de rodada, e são 73
    # delas nas 126 emissões reais, nenhuma com dono e nenhuma com condição.
    #
    # A conferência é repetida aqui, e não só na varredura da árvore, pelo
    # mesmo motivo de `pending` e da alegação: quem chama
    # `validate_governance_report` direto não passa pelo schema nem pela
    # varredura, e exigência que mora num lugar só some para metade dos
    # consumidores.
    if isinstance(pendencias, list):
        errors.extend(achar_limite_sem_dono(pendencias, "governance_report"))
    add_if(
        errors,
        verdict == "COMPLIANT" and report.get("candidate_digest_source") != "RECOMPUTADO",
        "governance_report: COMPLIANT publicando digest que não é o recomputado"
        " — identidade conferida cujo número não chega ao consumidor é palavra"
        " sobre um número que ninguém publicou",
    )
    try:
        parse_time(report["issued_at"])
    except (KeyError, TypeError, ValueError):
        errors.append("governance_report.issued_at: timestamp inválido")
    return errors


def validate_submission(submission: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(submission, dict):
        return ["submission: objeto obrigatório"]
    add_if(
        errors,
        submission.get("artifact_type") != "EXECUTIVE_SUBMISSION",
        "submission.artifact_type: inválido",
    )
    submitter = submission.get("submitted_by")
    add_if(
        errors,
        submitter not in DIRECT_EXECUTIVES,
        "submission: autor não é um dos três pares executivos",
    )
    validate_causal(
        submission.get("causal"),
        DIRECT_EXECUTIVES,
        errors,
        submission.get("candidate_digest"),
    )
    if isinstance(submission.get("causal"), dict):
        add_if(
            errors,
            submission["causal"].get("producer") != submitter,
            "submission: produtor causal diverge do autor",
        )
    add_if(
        errors,
        submission.get("deliverable_type") not in {"product", "proposal"},
        "submission: somente produto ou proposta",
    )
    executive_mission = submission.get("executive_mission")
    errors.extend(validate_mission(executive_mission))
    if isinstance(executive_mission, dict):
        add_if(
            errors,
            submitter not in executive_mission.get("recipients", []),
            "submission: autor não é destinatário da missão",
        )
        scope_touched = required_list(submission, "scope_touched", errors)
        scope_in = executive_mission.get("scope_in")
        add_if(
            errors,
            not isinstance(scope_in, list)
            or not set(scope_touched).issubset(set(scope_in)),
            "submission.scope_touched: extrapola o escopo autorizado",
        )
    add_if(
        errors,
        submission.get("returned_to") != "ceo-maestro",
        "submission.returned_to: inválido",
    )
    for field in ("artifact_refs", "evidence_refs", "audit_refs"):
        required_list(submission, field, errors)
    test_summary = submission.get("test_summary")
    if not isinstance(test_summary, dict):
        errors.append("submission.test_summary: objeto obrigatório")
    else:
        for field in ("pass", "fail", "skip"):
            value = test_summary.get(field)
            add_if(
                errors,
                not isinstance(value, int) or isinstance(value, bool) or value < 0,
                f"submission.test_summary.{field}: inteiro não negativo obrigatório",
            )
        skip_reasons = test_summary.get("skip_reasons")
        add_if(
            errors,
            not isinstance(skip_reasons, list),
            "submission.test_summary.skip_reasons: lista obrigatória",
        )
        if isinstance(skip_reasons, list):
            add_if(
                errors,
                test_summary.get("skip", 0) > 0 and not skip_reasons,
                "submission.test_summary: SKIP exige justificativa",
            )
            add_if(
                errors,
                test_summary.get("skip") == 0 and bool(skip_reasons),
                "submission.test_summary: motivo de SKIP sem teste pulado",
            )
        add_if(
            errors,
            not isinstance(test_summary.get("critical_fail"), bool),
            "submission.test_summary.critical_fail: booleano obrigatório",
        )
    governance_report = submission.get("governance_report")
    errors.extend(validate_governance_report(governance_report, submission))
    if isinstance(governance_report, dict):
        try:
            add_if(
                errors,
                parse_time(governance_report["issued_at"])
                > parse_time(submission["submitted_at"]),
                "governance_report: emitido após a submissão",
            )
        except (KeyError, TypeError, ValueError):
            errors.append("submission/governance_report: timestamps inválidos")
    judge = submission.get("judge_report")
    errors.extend(validate_judge_report(judge))
    if isinstance(judge, dict):
        mission_level = (
            executive_mission.get("required_level")
            if isinstance(executive_mission, dict)
            else None
        )
        add_if(
            errors,
            judge.get("required_level") != mission_level,
            "submission: required_level diverge entre missão e JUDGE_REPORT",
        )
        add_if(
            errors,
            submission.get("candidate_digest") != judge.get("candidate_digest"),
            "submission: candidato diverge do JUDGE_REPORT",
        )
        minimum = judge.get("minimum_score")
        target = required_target(judge.get("required_level"))
        if isinstance(minimum, int) and target is not None and minimum < target:
            limitation = submission.get("limitation_report")
            if limitation is not None:
                errors.extend(validate_limitation_report(limitation, judge))
            add_if(
                errors,
                submission.get("exception_authorization") is not None
                and limitation is None,
                "submission: autorização excepcional exige LIMITATION_REPORT",
            )
        else:
            add_if(
                errors,
                submission.get("limitation_report") is not None,
                "submission: gate normal não deve carregar relatório de limitação",
            )
            add_if(
                errors,
                submission.get("exception_authorization") is not None,
                "submission: gate normal não deve carregar autorização excepcional",
            )
    blockers = submission.get("blocking_pending_refs")
    add_if(
        errors,
        not isinstance(blockers, list),
        "submission.blocking_pending_refs: lista obrigatória",
    )
    limitation = submission.get("limitation_report")
    reconcile_contracts(
        [
            (
                "EXECUTIVE_MISSION",
                executive_mission if isinstance(executive_mission, dict) else None,
            ),
            ("EXECUTIVE_SUBMISSION", submission),
            ("JUDGE_REPORT", judge if isinstance(judge, dict) else None),
            (
                "LIMITATION_REPORT",
                limitation if isinstance(limitation, dict) else None,
            ),
        ],
        errors,
    )
    if isinstance(submission.get("causal"), dict):
        add_if(
            errors,
            submission.get("round") != submission["causal"].get("round"),
            "submission.round: diverge do cabeçalho causal",
        )
    return errors


def validate_capability_gap(gap: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(gap, dict):
        return ["capability_gap: objeto obrigatório"]
    add_if(
        errors,
        gap.get("artifact_type") != "CAPABILITY_GAP",
        "capability_gap.artifact_type: inválido",
    )
    validate_causal(gap.get("causal"), {"ceo-maestro"}, errors)
    add_if(
        errors,
        gap.get("required_capability")
        not in {
            "diretor-de-lentes",
            "departamento-negocios",
            "departamento-juizes",
            "departamento-evolucao-skills",
        },
        "capability_gap.required_capability: inválida",
    )
    add_if(
        errors,
        not isinstance(gap.get("expected_path"), str)
        or len(gap["expected_path"]) < 5,
        "capability_gap.expected_path: obrigatório",
    )
    add_if(
        errors,
        not isinstance(gap.get("impact"), str) or len(gap["impact"]) < 10,
        "capability_gap.impact: obrigatório",
    )
    add_if(
        errors,
        gap.get("safe_state") != "BLOCKED",
        "capability_gap.safe_state: deve ser BLOCKED",
    )
    try:
        parse_time(gap["detected_at"])
    except (KeyError, TypeError, ValueError):
        errors.append("capability_gap.detected_at: timestamp inválido")
    return errors


def validate_decision_packet(
    submission: dict[str, Any],
    decision: dict[str, Any],
    exception_request: dict[str, Any] | None = None,
) -> list[str]:
    errors = validate_submission(submission)
    validate_causal(
        decision.get("causal"),
        {"ceo-maestro"},
        errors,
        decision.get("candidate_digest"),
    )
    add_if(
        errors,
        decision.get("artifact_type") != "EXECUTIVE_DECISION",
        "decision.artifact_type: inválido",
    )
    judge = submission.get("judge_report", {})
    limitation = submission.get("limitation_report")
    authorization = submission.get("exception_authorization")
    mission = submission.get("executive_mission", {})
    required_level = decision.get("required_level")
    add_if(
        errors,
        required_target(required_level) is None,
        "decision.required_level: PRODUCAO ou INTERNO obrigatório",
    )
    add_if(
        errors,
        required_level != judge.get("required_level")
        or required_level != mission.get("required_level"),
        "decision.required_level: diverge da missão ou do JUDGE_REPORT",
    )
    reconcile_contracts(
        [
            ("EXECUTIVE_SUBMISSION", submission),
            ("JUDGE_REPORT", submission.get("judge_report")),
            (
                "LIMITATION_REPORT",
                limitation if isinstance(limitation, dict) else None,
            ),
            ("EXCEPTION_REQUEST", exception_request),
            ("EXECUTIVE_DECISION", decision),
        ],
        errors,
    )
    add_if(
        errors,
        decision.get("candidate_digest") != submission.get("candidate_digest"),
        "decision: candidato diverge da submissão",
    )
    add_if(
        errors,
        decision.get("minimum_score") != judge.get("minimum_score"),
        "decision: nota diverge dos Juízes",
    )
    add_if(
        errors,
        decision.get("submission_ref") != submission.get("submission_id"),
        "decision.submission_ref: diverge da submissão",
    )
    add_if(
        errors,
        decision.get("judge_report_ref") != judge.get("report_id"),
        "decision.judge_report_ref: diverge do JUDGE_REPORT",
    )
    if isinstance(limitation, dict):
        add_if(
            errors,
            decision.get("limitation_report_ref") != limitation.get("report_id"),
            "decision.limitation_report_ref: diverge do LIMITATION_REPORT",
        )
    else:
        add_if(
            errors,
            decision.get("limitation_report_ref") is not None,
            "decision: referência de limitação sem relatório correlacionado",
        )
    if isinstance(authorization, dict):
        add_if(
            errors,
            decision.get("exception_authorization_ref")
            != authorization.get("authorization_id"),
            "decision.exception_authorization_ref: diverge da autorização",
        )
    else:
        add_if(
            errors,
            decision.get("exception_authorization_ref") is not None,
            "decision: referência de autorização sem artefato correlacionado",
        )
    try:
        decided_at = parse_time(decision["decided_at"])
        issued_at = parse_time(judge["issued_at"])
        expires_at = parse_time(judge["expires_at"])
        add_if(
            errors,
            not issued_at <= decided_at <= expires_at,
            "decision: JUDGE_REPORT não estava vigente na decisão",
        )
    except (KeyError, TypeError, ValueError):
        errors.append("decision: timestamps do parecer ou decisão inválidos")
    required_list(decision, "evidence_refs", errors)
    state = decision.get("decision")
    gates = decision.get("nonwaivable_gates")
    minimum = decision.get("minimum_score")
    judge_blockers = judge.get("blocking_pending_refs")
    submission_blockers = submission.get("blocking_pending_refs")
    test_summary = submission.get("test_summary")
    test_critical = (
        test_summary.get("critical_fail")
        if isinstance(test_summary, dict)
        else None
    )
    test_fail = (
        test_summary.get("fail") if isinstance(test_summary, dict) else None
    )
    test_pass = (
        test_summary.get("pass") if isinstance(test_summary, dict) else None
    )
    test_skip = (
        test_summary.get("skip") if isinstance(test_summary, dict) else None
    )
    skip_reasons = (
        test_summary.get("skip_reasons")
        if isinstance(test_summary, dict)
        else None
    )
    derived_critical_absent = (
        judge.get("critical_fail") is False and test_critical is False
    )
    derived_blocking_absent = judge_blockers == [] and submission_blockers == []
    derived_done_proved = (
        isinstance(test_pass, int)
        and not isinstance(test_pass, bool)
        and test_pass > 0
        and test_fail == 0
        and isinstance(test_skip, int)
        and not isinstance(test_skip, bool)
        and (
            (test_skip == 0 and skip_reasons == [])
            or (
                test_skip > 0
                and isinstance(skip_reasons, list)
                and bool(skip_reasons)
            )
        )
        and isinstance(submission.get("artifact_refs"), list)
        and bool(submission.get("artifact_refs"))
        and isinstance(submission.get("evidence_refs"), list)
        and bool(submission.get("evidence_refs"))
    )
    governance = submission.get("governance_report")
    derived_rules_compliant = (
        isinstance(governance, dict)
        and governance.get("auditor_ref")
        == "departamento-auditoria-responsabilidades"
        and valid_digest(governance.get("auditor_digest"))
        and governance.get("candidate_digest") == submission.get("candidate_digest")
        and governance.get("contract_digest")
        == submission.get("causal", {}).get("contract_digest")
        and governance.get("rules_digest") == sha256_file(RULES_PATH)
        and governance.get("verdict") == "COMPLIANT"
        and governance.get("violations") == []
        and isinstance(governance.get("evidence_refs"), list)
        and bool(governance.get("evidence_refs"))
    )
    contract_artifacts = [
        submission.get("executive_mission"),
        submission,
        judge,
        limitation,
        exception_request,
        decision,
    ]
    contract_keys = {
        (
            artifact["causal"].get("work_item_id"),
            artifact["causal"].get("contract_id"),
            artifact["causal"].get("contract_version"),
            artifact["causal"].get("contract_digest"),
        )
        for artifact in contract_artifacts
        if isinstance(artifact, dict) and isinstance(artifact.get("causal"), dict)
    }
    candidate = submission.get("candidate_digest")
    candidate_integrity = (
        decision.get("candidate_digest") == candidate
        and judge.get("candidate_digest") == candidate
        and (
            not isinstance(limitation, dict)
            or limitation.get("candidate_digest") == candidate
        )
        and (
            not isinstance(exception_request, dict)
            or exception_request.get("candidate_digest") == candidate
        )
        and (
            not isinstance(authorization, dict)
            or authorization.get("candidate_digest") == candidate
        )
    )
    reference_integrity = (
        decision.get("submission_ref") == submission.get("submission_id")
        and decision.get("judge_report_ref") == judge.get("report_id")
        and (
            (
                isinstance(limitation, dict)
                and decision.get("limitation_report_ref")
                == limitation.get("report_id")
            )
            or (
                not isinstance(limitation, dict)
                and decision.get("limitation_report_ref") is None
            )
        )
        and (
            (
                isinstance(authorization, dict)
                and decision.get("exception_authorization_ref")
                == authorization.get("authorization_id")
            )
            or (
                not isinstance(authorization, dict)
                and decision.get("exception_authorization_ref") is None
            )
        )
    )
    mission = submission.get("executive_mission")
    scope_integrity = (
        isinstance(mission, dict)
        and isinstance(mission.get("scope_in"), list)
        and isinstance(submission.get("scope_touched"), list)
        and set(submission.get("scope_touched", [])).issubset(
            set(mission.get("scope_in", []))
        )
    )
    try:
        time_integrity = (
            parse_time(judge["issued_at"])
            <= parse_time(decision["decided_at"])
            <= parse_time(judge["expires_at"])
        )
    except (KeyError, TypeError, ValueError):
        time_integrity = False
    derived_integrity_valid = (
        len(errors) == 0
        and len(contract_keys) == 1
        and candidate_integrity
        and reference_integrity
        and scope_integrity
        and time_integrity
        and submission.get("round") == submission.get("causal", {}).get("round")
    )
    try:
        request_time_valid = (
            isinstance(exception_request, dict)
            and parse_time(exception_request["issued_at"])
            <= parse_time(decision["decided_at"])
            <= parse_time(exception_request["expires_at"])
        )
    except (KeyError, TypeError, ValueError):
        request_time_valid = False
    try:
        authorization_time_valid = (
            isinstance(authorization, dict)
            and parse_time(authorization["issued_at"])
            <= parse_time(decision["decided_at"])
            <= parse_time(authorization["expires_at"])
        )
    except (KeyError, TypeError, ValueError):
        authorization_time_valid = False
    if state == "AWAITING_HUMAN_EXCEPTION":
        derived_authority_reconciled = (
            isinstance(exception_request, dict)
            and exception_request.get("requested_authority") == "jeremias"
            and authorization is None
            and request_time_valid
        )
    elif state == "VALIDATED_BY_EXCEPTION":
        derived_authority_reconciled = (
            isinstance(exception_request, dict)
            and exception_request.get("requested_authority") == "jeremias"
            and isinstance(authorization, dict)
            and authorization.get("authorized_by") == "jeremias"
            and authorization.get("decision") == "APPROVED"
            and authorization.get("exception_request_id")
            == exception_request.get("request_id")
            and authorization.get("candidate_digest") == candidate
            and authorization.get("score_snapshot_digest")
            == exception_request.get("score_snapshot_digest")
            and request_time_valid
            and authorization_time_valid
        )
    else:
        derived_authority_reconciled = (
            submission.get("submitted_by") in DIRECT_EXECUTIVES
            and authorization is None
        )
    if isinstance(gates, dict):
        add_if(
            errors,
            gates.get("critical_fail_absent") is not derived_critical_absent,
            "decision: gate critical_fail_absent diverge dos artefatos",
        )
        add_if(
            errors,
            gates.get("blocking_pending_absent") is not derived_blocking_absent,
            "decision: gate blocking_pending_absent diverge dos artefatos",
        )
        add_if(
            errors,
            gates.get("done_proved") is not derived_done_proved,
            "decision: gate done_proved diverge de testes ou evidências",
        )
        add_if(
            errors,
            gates.get("rules_compliant") is not derived_rules_compliant,
            "decision: gate rules_compliant diverge da auditoria e das regras vigentes",
        )
        add_if(
            errors,
            gates.get("integrity_valid") is not derived_integrity_valid,
            "decision: gate integrity_valid diverge das correlações do pacote",
        )
        add_if(
            errors,
            gates.get("authority_reconciled") is not derived_authority_reconciled,
            "decision: gate authority_reconciled diverge da cadeia de autoridade",
        )
    target = required_target(required_level)
    if state == "VALIDATED":
        add_if(
            errors,
            not isinstance(minimum, int) or isinstance(minimum, bool) or minimum != 10,
            "decision: VALIDATED exige nota mínima inteira 10",
        )
        add_if(
            errors,
            judge.get("verdict") != "VALIDATED",
            "decision: VALIDATED exige parecer VALIDATED",
        )
        add_if(
            errors,
            not derived_critical_absent
            or not derived_blocking_absent
            or not derived_done_proved,
            "decision: VALIDATED rejeita falha, pendência ou conclusão sem prova",
        )
        add_if(
            errors,
            decision.get("acceptance_basis") != "quality_gate",
            "decision: base normal inválida",
        )
        add_if(
            errors,
            limitation is not None or authorization is not None,
            "decision: validação normal não usa exceção",
        )
        add_if(
            errors,
            not gates_all_pass(gates),
            "decision: VALIDATED exige todos os gates",
        )
    elif state == "ACEITO_USO_INTERNO":
        add_if(
            errors,
            required_level != "INTERNO",
            "decision: ACEITO_USO_INTERNO não alcança PRODUCAO",
        )
        add_if(
            errors,
            not isinstance(minimum, int)
            or isinstance(minimum, bool)
            or not 7 <= minimum <= 9,
            "decision: ACEITO_USO_INTERNO exige nota inteira entre 7 e 9",
        )
        add_if(
            errors,
            judge.get("verdict") != "ACEITO_USO_INTERNO",
            "decision: aceite interno exige parecer ACEITO_USO_INTERNO",
        )
        add_if(
            errors,
            not level_reached(judge.get("verdict"), required_level),
            "decision: veredito não alcança o nível exigido",
        )
        add_if(
            errors,
            not derived_critical_absent
            or not derived_blocking_absent
            or not derived_done_proved,
            "decision: aceite interno rejeita falha, pendência ou conclusão sem prova",
        )
        add_if(
            errors,
            decision.get("acceptance_basis") != "quality_gate",
            "decision: base de aceite interno inválida",
        )
        add_if(
            errors,
            limitation is not None or authorization is not None,
            "decision: aceite interno normal não usa exceção",
        )
        add_if(
            errors,
            not gates_all_pass(gates),
            "decision: ACEITO_USO_INTERNO exige todos os gates",
        )
    elif state == "AWAITING_HUMAN_EXCEPTION":
        add_if(
            errors,
            target is None
            or not isinstance(minimum, int)
            or isinstance(minimum, bool)
            or minimum >= target,
            "decision: espera de exceção exige nota inteira abaixo do alvo do nível",
        )
        add_if(errors, limitation is None, "decision: falta LIMITATION_REPORT")
        add_if(
            errors,
            authorization is not None,
            "decision: ainda não pode haver autorização consumida",
        )
        add_if(
            errors,
            exception_request is None,
            "decision: falta EXCEPTION_REQUEST",
        )
        if (
            exception_request is not None
            and isinstance(judge, dict)
            and isinstance(limitation, dict)
        ):
            errors.extend(
                validate_exception_request(exception_request, judge, limitation)
            )
        add_if(
            errors,
            decision.get("acceptance_basis") != "none",
            "decision: aguardando humano não é aceite",
        )
        add_if(
            errors,
            not gates_all_pass(gates),
            "decision: exceção inelegível por gate inegociável",
        )
    elif state == "VALIDATED_BY_EXCEPTION":
        add_if(
            errors,
            target is None
            or not isinstance(minimum, int)
            or isinstance(minimum, bool)
            or minimum >= target,
            "decision: exceção deve preservar nota inteira abaixo do alvo do nível",
        )
        add_if(errors, limitation is None, "decision: falta LIMITATION_REPORT")
        add_if(errors, authorization is None, "decision: falta autorização")
        add_if(
            errors,
            exception_request is None,
            "decision: falta EXCEPTION_REQUEST correlacionado",
        )
        if exception_request is not None and isinstance(authorization, dict):
            errors.extend(
                validate_authorization(
                    authorization, exception_request, decision.get("decided_at")
                )
            )
            add_if(
                errors,
                authorization.get("decision") != "APPROVED",
                "decision: autorização não aprovada",
            )
            add_if(
                errors,
                authorization.get("status") != "CONSUMED",
                "decision: autorização de uso único deve ser consumida",
            )
        add_if(
            errors,
            decision.get("acceptance_basis") != "jeremias_exception",
            "decision: base excepcional inválida",
        )
        add_if(
            errors,
            not gates_all_pass(gates),
            "decision: exceção não dispensa gate inegociável",
        )
        add_if(
            errors,
            not derived_critical_absent
            or not derived_blocking_absent
            or not derived_done_proved,
            "decision: exceção rejeita falha, pendência ou conclusão sem prova",
        )
    elif state in {"REWORK", "BLOCKED", "CANCELLED", "LIMIT_REACHED"}:
        add_if(
            errors,
            decision.get("acceptance_basis") != "none",
            "decision: estado sem aceite deve usar base none",
        )
    else:
        errors.append(f"decision: estado desconhecido {state!r}")
    return errors


def causal(
    producer: str,
    candidate_digest: str = "n/a",
    message_id: str = "message-001",
    round_number: int = 3,
) -> dict[str, Any]:
    return {
        "work_item_id": "work-item-001",
        "front_id": "front-001",
        "handoff_id": "handoff-001",
        "message_id": message_id,
        "causation_message_ids": [],
        "contract_id": "contract-001",
        "contract_version": 1,
        "contract_digest": digest("0"),
        "candidate_digest": candidate_digest,
        "round": round_number,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": digest("1"),
        "producer_digest_recipe": "_compartilhado/validador_schema.py::sha256_file sobre o SKILL.md do produtor",
        "created_at": "2026-07-26T11:00:00-03:00",
    }


def score_item(identifier: str, score: int) -> dict[str, Any]:
    return {
        "criterion_id": identifier,
        "applicable": True,
        "score": score,
        "evidence_refs": [f"evidence/{identifier}.json"],
    }


def aggregation_rule(
    method: str = "MENOR", declared_at: str = "2026-07-26T11:00:00-03:00"
) -> dict[str, Any]:
    """ADR-016: a regra de combinação entre instâncias da mesma lente.

    Fixada no `JUDGMENT_REQUEST` antes de qualquer parecer existir, copiada pelos
    Juízes e propagada até o CEO.
    """
    return {
        "method": method,
        "declared_at": declared_at,
        "rationale": "Fixada no pedido, antes de qualquer parecer existir.",
    }


def judge_report(
    scores: list[int],
    required_level: str = "PRODUCAO",
    critical: bool = False,
    blockers: list[str] | None = None,
    instances_per_lens: int = 1,
    score_range: tuple[int, int] | None = None,
    rule: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blockers = [] if blockers is None else blockers
    minimum = min(scores)
    # ADR-016: com uma instância, lo == hi == minimum e nada muda.
    if score_range is None:
        score_range = (minimum, minimum)
    verdict = external_verdict(
        minimum, critical, blockers, {"lo": score_range[0], "hi": score_range[1]}
    )
    return {
        "artifact_type": "JUDGE_REPORT",
        "report_id": "judge-report-001",
        "causal": causal(
            "departamento-juizes",
            digest("a"),
            "message-judge-001",
        ),
        "candidate_digest": digest("a"),
        "judge_capability_ref": "departamento-juizes",
        "judge_capability_digest": digest("b"),
        "scorecard": [
            score_item(f"criterion-{index + 1:02d}", score)
            for index, score in enumerate(scores)
        ],
        "minimum_score": minimum,
        "minimum_score_range": {"lo": score_range[0], "hi": score_range[1]},
        "instances_per_lens": instances_per_lens,
        "aggregation_rule": rule or aggregation_rule(),
        "verdict": verdict,
        "required_level": required_level,
        "critical_fail": critical,
        "blocking_pending_refs": blockers,
        "evidence_refs": ["evidence/judges.json"],
        "issued_at": "2026-07-26T12:00:00-03:00",
        "expires_at": "2026-07-27T12:00:00-03:00",
    }


def limitation_report(judge: dict[str, Any]) -> dict[str, Any]:
    minimum = judge["minimum_score"]
    target = required_target(judge["required_level"])
    assert target is not None
    return {
        "artifact_type": "LIMITATION_REPORT",
        "report_id": "limit-report-001",
        "causal": causal(
            "diretor-de-lentes",
            judge["candidate_digest"],
            "message-limit-001",
        ),
        "submitted_by": "diretor-de-lentes",
        "candidate_digest": judge["candidate_digest"],
        "score_snapshot_digest": digest("c"),
        "current_minimum_score": minimum,
        "best_attainable_score": max(minimum, target - 1),
        "below_cutoff_evaluations": [
            item for item in judge["scorecard"] if item["score"] < target
        ],
        "objective_factors": [
            "A API vinculante limita atomicidade além do controle do projeto."
        ],
        "attempted_remediations": [
            "Foram testadas transação compensatória e fila idempotente."
        ],
        "alternatives_assessed": [
            "Trocar o fornecedor foi analisado e viola restrição contratual vigente."
        ],
        "why_gap_cannot_close": [
            "O critério depende de garantia que a API não oferece no contrato atual."
        ],
        "residual_risks": [
            "Pode ocorrer atraso observável em reconciliação após falha externa."
        ],
        "mitigations": [
            "Reconciliação automática, alerta e runbook de recuperação foram provados."
        ],
        "requested_scope": [
            "Aceitar somente a versão e o fluxo representados pelo digest do candidato."
        ],
        "independent_verification": {
            "reviewer": "departamento-juizes",
            "reviewer_digest": digest("b"),
            "verdict": "VERIFIED_IMPOSSIBILITY",
            "independence_confirmed": True,
            "all_below_cutoff_criteria_covered": True,
            "evidence_refs": ["evidence/independent-review.json"],
            "dissent_refs": [],
        },
        "evidence_refs": ["evidence/platform-contract.pdf"],
        "issued_at": "2026-07-26T12:10:00-03:00",
    }


def gates(value: bool = True) -> dict[str, bool]:
    return {field: value for field in REQUIRED_GATES}


def exception_request(
    judge: dict[str, Any], limitation: dict[str, Any]
) -> dict[str, Any]:
    return {
        "artifact_type": "EXCEPTION_REQUEST",
        "request_id": "exception-request-001",
        "causal": causal(
            "ceo-maestro",
            judge["candidate_digest"],
            "message-exception-request-001",
        ),
        "candidate_digest": judge["candidate_digest"],
        "score_snapshot_digest": limitation["score_snapshot_digest"],
        "judge_report_ref": judge["report_id"],
        "limitation_report_ref": limitation["report_id"],
        "actual_minimum_score": judge["minimum_score"],
        "cutoff_score": required_target(judge["required_level"]),
        "required_level": judge["required_level"],
        "requested_scope": limitation["requested_scope"],
        "residual_risks": limitation["residual_risks"],
        "mitigations": limitation["mitigations"],
        "nonwaivable_gates": gates(),
        "requested_authority": "jeremias",
        "issued_at": "2026-07-26T12:20:00-03:00",
        "expires_at": "2026-07-26T18:20:00-03:00",
    }


def authorization(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": "EXCEPTION_AUTHORIZATION",
        "authorization_id": "exception-authorization-001",
        "exception_request_id": request["request_id"],
        "decision": "APPROVED",
        "authorized_by": "jeremias",
        "identity_evidence_ref": "conversation/turn-jeremias-001",
        "citation_exact": (
            "Eu, Jeremias, autorizo esta exceção para o candidato, escopo e riscos citados."
        ),
        "candidate_digest": request["candidate_digest"],
        "score_snapshot_digest": request["score_snapshot_digest"],
        "actual_minimum_score": request["actual_minimum_score"],
        "scope": request["requested_scope"],
        "conditions": ["Preservar mitigação e monitoramento registrados."],
        "issued_at": "2026-07-26T12:30:00-03:00",
        "expires_at": "2026-07-26T18:30:00-03:00",
        "usage_policy": "single_use",
        "status": "CONSUMED",
    }


def submission(
    judge: dict[str, Any],
    limitation: dict[str, Any] | None = None,
    auth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "artifact_type": "EXECUTIVE_SUBMISSION",
        "submission_id": "submission-001",
        "causal": causal(
            "diretor-de-lentes",
            judge["candidate_digest"],
            "message-submission-001",
        ),
        "submitted_by": "diretor-de-lentes",
        "deliverable_type": "product",
        "executive_mission": mission(judge["required_level"]),
        "scope_touched": ["Produto, viabilidade e implementação."],
        "artifact_refs": ["artifacts/product.zip"],
        "evidence_refs": ["evidence/test-report.json"],
        "candidate_digest": judge["candidate_digest"],
        "test_summary": {
            "pass": 12,
            "fail": 0,
            "skip": 0,
            "skip_reasons": [],
            "critical_fail": judge["critical_fail"],
        },
        "audit_refs": ["evidence/audit-report.md"],
        "governance_report": {
            "report_id": "governance-report-001",
            "auditor_ref": "departamento-auditoria-responsabilidades",
            "auditor_digest": digest("e"),
            "candidate_digest": judge["candidate_digest"],
            "contract_digest": digest("0"),
            "rules_digest": sha256_file(RULES_PATH),
            "verdict": "COMPLIANT",
            # ADR-018: um COMPLIANT que chega à barreira tem de declarar que a
            # identidade do candidato foi RECOMPUTADA, e não apenas copiada. Sem
            # este campo os dois casos — conferido e não conferido — chegavam
            # aqui idênticos, e o CEO não tinha como distinguir.
            "candidate_identity_status": "CONFERIDO",
            "candidate_manifest_status": "SEM_MANIFESTO",
            # T71: um COMPLIANT que chega à barreira também declara que TODO
            # inspetor do painel foi medido independente. O painel fica no
            # AUDIT_LEDGER da Auditoria — este envelope não o carrega —, então
            # o que atravessa a fronteira é o escalar derivado dele. Antes desta
            # frente o campo `panel[].independent` era preenchido e jamais lido,
            # e recibo não independente fechava COMPLIANT do mesmo jeito.
            "panel_independence_status": "INDEPENDENTE",
            # Rodada 4: o envelope declara de onde veio o digest que publica.
            # RECOMPUTADO significa que a Auditoria reabriu a árvore e refez a
            # conta; DECLARADO_NAO_CONFERIDO significa que copiou o que lhe
            # deram. Antes os dois chegavam aqui com a mesma cara.
            "candidate_digest_source": "RECOMPUTADO",
            "violations": [],
            "evidence_refs": ["evidence/rules-audit.json"],
            # Os três limites residuais viajam COM o envelope que esta barreira
            # lê. A SKILL.md da Auditoria afirmava, desde a rodada 2, que quem lê
            # aqui os lê "no próprio artefato" — e o artefato não tinha `pending`.
            # Duas óticas independentes dos Juízes acusaram a contradição na
            # rodada 3.
            "pending": [
                # RODADA 6 — TEXTO CORRIGIDO, E A CORREÇÃO É UMA RETIRADA.
                #
                # Até o cand-E esta fixture publicava o R6 ANTIGO: "a âncora
                # encarece a fabricação sem impedi-la". Era a alegação que o
                # emissor declara retirada desde a rodada 5, e que o
                # `68-EVOLUTION-LEDGER-R5` diz "retirada por ser desmentida pela
                # medição" — viva aqui, numa fixture canônica de envelope VÁLIDO,
                # com casos asseverando PASS sobre ela. `OI5-08` (a2) mediu isto:
                # o pacote entregue continha um teste executado que certificava
                # que um envelope publicando a alegação retirada era ACEITO na
                # barreira. O texto passa a ser o vigente, com o número no lugar
                # do advérbio.
                TEXTO_R6,
                TEXTO_R9,
                TEXTO_R10,
                # RODADA 5 — o TETO. R6, R9 e R10 limitam o alcance de travas
                # que existem; R11 limita o método inteiro, e é a razão de a
                # alegação ter sido reduzida.
                TEXTO_R11,
            ],
            # RODADA 5 — A ALEGAÇÃO VIAJA NO ENVELOPE.
            #
            # Reduzir a alegação só serve se ela chegar a quem decide. Este é o
            # artefato que a barreira lê, e o campo é obrigatório: um envelope
            # que não diga o que COMPLIANT certifica, e o que ele NÃO certifica,
            # não passa aqui nem no schema.
            "compliance_claim": {
                "certifies": ALEGACAO_DO_COMPLIANT,
                "does_not_certify": NAO_COBERTO_PELA_ALEGACAO,
                "ceiling_ref": "R11",
                "source": "scripts/inspecao_executada.py::ALEGACAO_DO_COMPLIANT",
            },
            "issued_at": "2026-07-26T12:35:00-03:00",
        },
        "judge_report": judge,
        "limitation_report": limitation,
        "exception_authorization": auth,
        "blocking_pending_refs": [],
        "round": 3,
        "returned_to": "ceo-maestro",
        "submitted_at": "2026-07-26T12:40:00-03:00",
    }


def decision(
    judge: dict[str, Any],
    state: str,
    basis: str,
    gate_values: dict[str, bool] | None = None,
) -> dict[str, Any]:
    is_exception = state == "VALIDATED_BY_EXCEPTION"
    has_limitation = state in {"AWAITING_HUMAN_EXCEPTION", "VALIDATED_BY_EXCEPTION"}
    return {
        "artifact_type": "EXECUTIVE_DECISION",
        "decision_id": "decision-001",
        "causal": causal(
            "ceo-maestro",
            judge["candidate_digest"],
            "message-decision-001",
        ),
        "submission_ref": "submission-001",
        "candidate_digest": judge["candidate_digest"],
        "minimum_score": judge["minimum_score"],
        "required_level": judge["required_level"],
        "judge_report_ref": judge["report_id"],
        "limitation_report_ref": "limit-report-001" if has_limitation else None,
        "exception_authorization_ref": (
            "exception-authorization-001" if is_exception else None
        ),
        "decision": state,
        "acceptance_basis": basis,
        "nonwaivable_gates": gates() if gate_values is None else gate_values,
        "evidence_refs": ["evidence/executive-decision.json"],
        "decided_at": "2026-07-26T12:45:00-03:00",
    }


def capability_gap() -> dict[str, Any]:
    return {
        "artifact_type": "CAPABILITY_GAP",
        "gap_id": "capability-gap-001",
        "causal": causal(
            "ceo-maestro",
            "n/a",
            "message-capability-gap-001",
            round_number=1,
        ),
        "required_capability": "diretor-de-lentes",
        "expected_path": "ceo-maestro/diretor-de-lentes/SKILL.md",
        "impact": "A frente técnica não pode ser roteada nem validada.",
        "safe_state": "BLOCKED",
        "detected_at": "2026-07-26T11:05:00-03:00",
    }


def mission(required_level: str = "PRODUCAO") -> dict[str, Any]:
    return {
        "artifact_type": "EXECUTIVE_MISSION",
        "mission_id": "mission-001",
        "causal": causal(
            "ceo-maestro",
            "n/a",
            "message-mission-001",
            round_number=1,
        ),
        "recipients": ["diretor-de-lentes", "departamento-negocios"],
        "objective": "Criar e validar um novo produto digital.",
        "deliverable_type": "product",
        "required_level": required_level,
        "scope_in": ["Produto, viabilidade e implementação."],
        "scope_out": [],
        "constraints": [],
        "decisions_binding": [],
        "dependencies": [],
        "acceptance_criteria": [
            f"Veredito externo deve alcançar required_level {required_level}."
        ],
        "required_evidence": ["Testes, auditoria e parecer dos Juízes."],
        "matrix_exchange": {
            "allowed": True,
            "topics": ["Valor de negócio e viabilidade técnica."],
            "read_scope": ["Contrato e evidências compartilhadas."],
            "write_scope": ["Recomendação correlacionada, sem ampliar autoridade."],
            "consolidation_owner": "diretor-de-lentes",
        },
        "permissions": {
            "default_policy": "deny",
            "allowed_tools": [],
            "allowed_resources": [],
            "expires_at": "2026-07-27T11:00:00-03:00",
        },
        "stop_when": ["Bloqueio material ou critério de pronto satisfeito."],
        "judge_gate_required": True,
        "return_to": "ceo-maestro",
        "issued_at": "2026-07-26T11:00:00-03:00",
    }


# ---------------------------------------------------------------------------
# Trava de despacho de julgamento (T32)
#
# O `protocolo-de-julgamento.md` §5 diz que rodada sem `JUDGE_ASSIGNMENT` é
# `BLOCKED_BYPASS_ATTEMPT` "mesmo vindo do CEO ou de Jeremias" — e a própria
# linha 502 declara o limite: "auditável só a posteriori; o runtime não oferece
# controle de acesso por chamador". A trava era CONTRATUAL, isto é, prosa. Ela
# falhou dos dois lados: o CEO despachou fora do protocolo dez vezes, e os
# agentes que deviam recusar julgaram assim mesmo.
#
# Aqui ela vira derivada do disco. Três armadilhas que esta implementação
# atravessou, todas medidas em 2026-08-06 e todas defeito do instrumento:
#
#   1. `grep "JUDGE_ASSIGNMENT"` daria VERDE à rodada que mais furou o
#      protocolo — ela cita a palavra 14 vezes, todas denunciando a ausência.
#      Por isso: só objeto JSON parseado conta. Markdown não parseia.
#   2. `EXECUTIVE_MISSION` tem `handoff_id` e foi aceita como prova numa
#      primeira versão. É envelope de CEO→executivo, não de gerente→juiz.
#      Crédito à trava errada.
#   3. O par `assignment_id`+`write_path` veio do EXEMPLO do protocolo, não da
#      forma real do artefato — a `JUDGE_ASSIGNMENT` de verdade não tem
#      `write_path`. Exigi-lo reprovava rodadas conformes.
#
# O discriminador que sobrou é `artifact_type == "JUDGE_ASSIGNMENT"`, e ele
# separa o caso mais afiado: um parecer que CITA `assignment_id` não prova
# designação nenhuma. Citar a designação não é ter sido designado.
#
# LIMITE DECLARADO: forjar um JSON com esse `artifact_type` é trivial. Esta
# trava não torna o bypass impossível — torna-o VISÍVEL e DELIBERADO. É o mesmo
# teto `OI-04` já nomeado nesta casa: forjar a evidência é chamar as mesmas
# funções que a verificam.
# ---------------------------------------------------------------------------

PASTAS_FORA_DA_RODADA = {
    "candidatos", "instrumentos", "lab", "fontes", "saida-crua", "backup",
}

# EXCEÇÃO HISTÓRICA DATADA, não permissão. Rodada nova que aparecer em bypass
# reprova, porque não está aqui.
#
# **A regra "só encolhe" não se autoexigia, e a lista quase dobrou — medido em
# 2026-08-08 (tarefa 53).** Ela nasceu com **7** entradas no commit `d302724`
# (T32, 06/ago) sob este mesmo comentário, e chegou a **13** no commit `1162772`
# (07/ago). Cinco das seis que entraram não trazem justificativa escrita, e o
# comentário continuou dizendo "As 7 rodadas medidas em 2026-08-06" enquanto o
# dado ao lado dizia 13 — o texto normativo e o dado discordando dentro do
# mesmo bloco.
#
# **As seis entradas eram legítimas**, e isso importa para não acusar ninguém de
# fraude: conferido em 2026-08-08, as 13 correspondem exatamente às 13 rodadas
# hoje em bypass — zero peso morto, zero violação fora da lista. Cinco são
# campanhas ANTIGAS que a detecção passou a enxergar quando melhorou, e uma é
# campanha nova de 07/ago. O defeito não é o conteúdo: é que **a lista só sabia
# subir**. Detecção melhor produz mais entradas, e nada obrigava a descer.
#
# Por isso agora ela se autoexige de duas formas, e as duas estão em
# `validar_trava_de_despacho`:
#   1. **Teto declarado.** Crescer exige mudar `TETO_BYPASS_HISTORICO`, que é um
#      número — a menor unidade de mudança que um revisor não deixa passar.
#      Linha a mais numa lista de nomes parece inofensiva no diff; número não.
#   2. **Catraca.** Entrada que deixou de ser bypass — porque a rodada ganhou
#      sua `JUDGE_ASSIGNMENT` — vira erro pedindo a REMOÇÃO. É o "só encolhe"
#      deixando de ser promessa em prosa e virando exigência executável.
TETO_BYPASS_HISTORICO = 13

BYPASS_HISTORICO_2026_08_06 = {
    "digest-que-nao-reprova-2026-08-04",
    "julgamento-nove-departamentos-2026-08-04",
    "julgamento-pacotes-2026-07-29",
    "metodo-agregacao-2026-07-31",
    "nucleo-de-comando-2026-08-05",
    "recoleta-c03-c05-c06-2026-08-05",
    "rejulgamento-rodada2-2026-07-31",
    # T38: evidencia congelada da rodada que revelou as 98 violacoes de
    # schema. Continua observavel por `rodadas_em_bypass`; esta excecao apenas
    # impede que uma campanha historica conhecida derrube o inventario inteiro.
    "nucleo-de-comando-r2-2026-08-07",
    "barreiras-em-prosa-2026-08-03",
    "compliant-porta-unica-2026-08-01",
    "contrato-analysis-2026-07-31",
    "forward-test-julgamento-rodada2",
    "remedicao-dos-sete-2026-08-03",
}


def _objetos_json(texto: str, ndjson: bool) -> list[Any]:
    """Objetos JSON de um arquivo. Texto que não parseia devolve nada — é o que
    impede prosa de markdown de ser lida como envelope."""
    saida: list[Any] = []
    if ndjson:
        for linha in texto.splitlines():
            if linha.strip():
                try:
                    saida.append(json.loads(linha))
                except json.JSONDecodeError:
                    pass
        return saida
    try:
        saida.append(json.loads(texto))
    except json.JSONDecodeError:
        pass
    return saida


def _percorre(obj: Any) -> Any:
    if isinstance(obj, dict):
        yield obj
        for valor in obj.values():
            yield from _percorre(valor)
    elif isinstance(obj, list):
        for valor in obj:
            yield from _percorre(valor)


_CANONICAL_ENVELOPE_SCHEMAS = {
    "JUDGE_ASSIGNMENT": (JUDGE_SCHEMA_PATH, "judgeAssignment"),
    "CRITERIA_MATRIX": (JUDGE_SCHEMA_PATH, "criteriaMatrix"),
    "JUDGMENT_REQUEST": (DIRECTOR_SCHEMA_PATH, "judgmentRequest"),
}


@lru_cache(maxsize=None)
def _carregar_schema_canonico(path: Path) -> dict[str, Any]:
    """Carrega um schema normativo uma vez, sem criar copia local dele."""
    return json.loads(path.read_text(encoding="utf-8"))


def validar_envelope_canonico(
    envelope: Any,
    artifact_type: str | None = None,
) -> list[str]:
    """Valida um envelope contra o `$defs` do seu consumidor canonico.

    O motor compartilhado e usado como uma unica implementacao de JSON Schema
    da estrutura. Ausencia, schema desconhecido ou erro de leitura falham
    fechado e aparecem como erro nomeado; nenhum desses estados vira True por
    rotulo.
    """
    if not isinstance(envelope, dict):
        return [f"envelope: esperado objeto, recebido {type(envelope).__name__}"]

    kind = artifact_type or envelope.get("artifact_type")
    target = _CANONICAL_ENVELOPE_SCHEMAS.get(kind)
    if target is None:
        return [f"envelope: artifact_type sem schema canonico: {kind!r}"]

    schema_path, definition_name = target
    try:
        schema = _carregar_schema_canonico(schema_path)
        definition = schema["$defs"][definition_name]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        return [
            "schema canonico indisponivel: "
            f"{schema_path}#$defs/{definition_name}: {exc}"
        ]
    return validate_schema(envelope, definition, schema)


def tem_judge_assignment(arquivos: list[tuple[str, str]]) -> bool:
    """Classificador PURO: recebe [(nome, conteúdo)] e não toca em disco.

    É puro de propósito — assim a prova de mutação abaixo é barata e real, em
    vez de depender de fixture em disco que ninguém reexecuta.
    """
    for nome, conteudo in arquivos:
        if not nome.endswith((".json", ".ndjson")):
            continue
        for raiz in _objetos_json(conteudo, nome.endswith(".ndjson")):
            for obj in _percorre(raiz):
                if obj.get("artifact_type") != "JUDGE_ASSIGNMENT":
                    continue
                if not validar_envelope_canonico(obj, "JUDGE_ASSIGNMENT"):
                    return True
    return False


def _arquivos_da_rodada(pasta: Path) -> list[tuple[str, str]]:
    arquivos = []
    for caminho in pasta.rglob("*"):
        if PASTAS_FORA_DA_RODADA & set(caminho.parts):
            continue
        if not caminho.is_file() or caminho.suffix not in (".json", ".ndjson"):
            continue
        try:
            arquivos.append(
                (caminho.name, caminho.read_text(encoding="utf-8", errors="replace"))
            )
        except OSError:
            pass
    return arquivos


def _houve_julgamento(pasta: Path) -> bool:
    """Evidência EM DISCO de que se julgou: parecer, veredito ou opinião."""
    for caminho in pasta.rglob("*"):
        if PASTAS_FORA_DA_RODADA & set(caminho.parts):
            continue
        nome = caminho.name.upper()
        if nome.startswith("PARECER") or "VEREDITO" in nome or "JUDGE-OPINION" in nome:
            return True
        partes = {parte.upper() for parte in caminho.parts}
        if (
            "JUDGE-ASSIGNMENTS" in partes
            or "JUDGE_ASSIGNMENTS" in partes
            or "JUDGE-ASSIGNMENT" in nome
            or "JUDGE_ASSIGNMENT" in nome
        ):
            return True
    return False


def rodadas_em_bypass(raiz_evals: Path) -> list[str]:
    """Rodadas que julgaram sem nenhuma `JUDGE_ASSIGNMENT` estruturada."""
    bypass = []
    if not raiz_evals.is_dir():
        return bypass
    for pasta in sorted(raiz_evals.iterdir()):
        if not pasta.is_dir() or pasta.name in PASTAS_FORA_DA_RODADA:
            continue
        if not _houve_julgamento(pasta):
            continue
        if not tem_judge_assignment(_arquivos_da_rodada(pasta)):
            bypass.append(pasta.name)
    return bypass


def validar_trava_de_despacho(raiz_evals: Path) -> list[str]:
    erros = []
    bypass = set(rodadas_em_bypass(raiz_evals))

    novas = sorted(bypass - BYPASS_HISTORICO_2026_08_06)
    for nome in novas:
        erros.append(
            f"rodada de julgamento sem JUDGE_ASSIGNMENT e fora da exceção "
            f"histórica: {nome} — protocolo-de-julgamento.md §5 chama isso de "
            f"BLOCKED_BYPASS_ATTEMPT"
        )

    # A lista pinada não pode citar rodada que não existe: entrada fantasma
    # transformaria a exceção em permissão genérica.
    existentes = {
        p.name for p in raiz_evals.iterdir() if p.is_dir()
    } if raiz_evals.is_dir() else set()
    for nome in sorted(BYPASS_HISTORICO_2026_08_06 - existentes):
        erros.append(
            f"exceção histórica cita rodada inexistente: {nome} — "
            f"remova a entrada em vez de deixá-la cobrindo o vazio"
        )

    # T53, autoexigência 1 — TETO. Sem isto a lista cresce em silêncio: foi
    # assim que ela foi de 7 para 13 sob um comentário que dizia "só encolhe".
    if len(BYPASS_HISTORICO_2026_08_06) > TETO_BYPASS_HISTORICO:
        erros.append(
            f"a exceção histórica tem {len(BYPASS_HISTORICO_2026_08_06)} "
            f"entradas e o teto declarado é {TETO_BYPASS_HISTORICO} — se a "
            f"lista precisa crescer, o teto muda junto, à vista, com a razão "
            f"de cada entrada nova escrita ao lado"
        )

    # T53, autoexigência 2 — CATRACA. Entrada que deixou de ser bypass tem de
    # sair. É o "só encolhe" virando exigência executável em vez de promessa:
    # quando uma rodada ganha sua JUDGE_ASSIGNMENT, a exceção que a cobria
    # perde objeto e passaria a cobrir qualquer regressão futura no mesmo nome.
    for nome in sorted((BYPASS_HISTORICO_2026_08_06 & existentes) - bypass):
        erros.append(
            f"exceção histórica obsoleta: {nome} não está mais em bypass — "
            f"remova a entrada e baixe TETO_BYPASS_HISTORICO para "
            f"{len(BYPASS_HISTORICO_2026_08_06) - 1}. Exceção que perdeu "
            f"objeto vira permissão para a próxima regressão com o mesmo nome"
        )
    return erros


def _fixture_judge_assignment_canonica() -> dict[str, Any]:
    """Fixture positiva minima, montada a partir do schema do consumidor."""
    digest_fixture = "sha256:" + "a" * 64
    timestamp = "2026-08-06T10:00:00-03:00"
    return {
        "artifact_type": "JUDGE_ASSIGNMENT",
        "assignment_id": "ASSIGN-T38-I1",
        "causal": {
            "work_item_id": "TASK-T38",
            "front_id": "FRONT-T38",
            "handoff_id": "HANDOFF-T38",
            "message_id": "MSG-T38",
            "causation_message_ids": ["MSG-T38-CEO"],
            "contract_id": "CTR-T38",
            "contract_version": 1,
            "contract_digest": digest_fixture,
            "candidate_digest": digest_fixture,
            "round": 1,
            "attempt": 1,
            "producer": "departamento-juizes",
            "producer_version": "1",
            "producer_digest": digest_fixture,
            "producer_digest_recipe": (
                "ceo-maestro/evals/validate_workflow.py::validate sobre schema canonico"
            ),
            "created_at": timestamp,
        },
        "judge_id": "agente-julgar-robustez-e-evidencia",
        "lens": "robustez-e-evidencia",
        "mode": "VALIDACAO",
        "candidate_digest": digest_fixture,
        "anonymized_candidate": "custody/candidate-redacted",
        "criteria": [
            {
                "criterion_id": "CRIT-01",
                "criterion_text": "Criterio canonico de controle.",
                "role": "owner",
            }
        ],
        "rubric_ref": "rubrica-corte-v2",
        "contract_excerpt": {
            "intent": "Provar a forma do envelope.",
            "done": [],
            "scope_in": [],
            "scope_out": [],
            "constraints": [],
            "decisions": [],
            "not_applicable": [],
        },
        "evidence_index": [],
        "forbidden_context": [
            "autoria do candidato",
            "nota desejada",
            "parecer de outra otica",
            "preferencia da gerente",
        ],
        "instance": 1,
        "write_path": "julgamento/HANDOFF-T38/a1/ASSIGN-T38-I1/",
        "custody_copy": {
            "path": "custody/assignment.json",
            "sha256": digest_fixture,
            "bytes": 1,
            "taken_at": timestamp,
        },
        "return_to": "departamento-juizes",
        "issued_at": timestamp,
    }



# --------------------------------------------------------------------------
# T109 — a trava da T96 esta certa e nao alcanca ninguem
#
# `_missao_nao_proibe_dono_de_evidencia` so entra quando a missao declara
# `forbidden_actors`. Medido em 2026-08-24: das **161 EXECUTIVE_MISSION reais**
# da arvore (253 no total, 92 sao fixture, overlay, isolamento ou backup),
# **ZERO** declaram o campo. A trava dispara em 0 de 161 — passa nas proprias
# amostras sinteticas, que setam o campo, e e inerte na casa.
#
# NAO E DEFEITO DELA. O campo nasceu OPCIONAL de proposito, para nao falsificar
# envelope ja emitido — mesma disciplina do `bloqueada_por`. O que falta e o
# outro lado: nada obriga uma emissao NOVA a declarar. A missao 46 proibiu
# atores em PROSA (`stop_when` e um `allowed_tools` restringindo `spawn_agent`),
# e prosa a T96 recusou cacar, com razao: a proxima escreveria com outras
# palavras.
#
# O QUE NAO FAZER, e esta e a parte cara: NAO derivar a proibicao de
# `recipients`. Ja foi tentado na T96 e a propria bateria derrubou em duas
# linhas — o caso canonico `missao executiva admite Evolucao de Skills` tem
# `judge_gate_required: true` com `recipients` so da Evolucao e e VALIDO,
# porque nesta casa o parecer chega pela CADEIA DO CEO, nao pelo destinatario.
# A T109 nasceu pedindo exatamente essa derivacao; o pedido estava errado.
#
# ENTAO O CONSERTO E TORNAR A DECLARACAO OBRIGATORIA DAQUI PARA A FRENTE:
# ausencia deixa de ser silencio e vira declaracao. `[]` diz "esta missao nao
# proibe ninguem"; campo faltando nao diz nada. As anteriores ao corte sao
# divida, contada e com catraca dos dois lados.
# --------------------------------------------------------------------------

CORTE_DECLARACAO_DE_PROIBICAO = "2026-08-25"

# Divida MEDIDA em 2026-08-24 sobre as missoes reais da arvore, nao estimada.
# Derivada de contagem e nao escrita ao lado dela seria melhor; aqui a lista
# nomeada teria 161 ids e afogaria o arquivo, entao o numero fica com a receita
# colada: e `missoes_sem_declaracao_de_proibicao(...)[1]` sobre a arvore real.
TETO_MISSOES_SEM_DECLARACAO = 161


def missoes_sem_declaracao_de_proibicao(
    missoes: list[dict[str, Any]], corte: str = CORTE_DECLARACAO_DE_PROIBICAO
) -> tuple[list[str], list[str]]:
    """Separa quem OMITE `forbidden_actors` em pos-corte (falta) e pre-corte (divida).

    Recebe as missoes ja lidas, e nao o caminho: trava que so sabe ler o disco
    nao tem como provar que fica vermelha. Mesma disciplina de
    `retornos_sem_gate`, no `diretor-de-lentes`.
    """
    pos: list[str] = []
    pre: list[str] = []
    for m in missoes:
        if not isinstance(m, dict) or m.get("artifact_type") != "EXECUTIVE_MISSION":
            continue
        if isinstance(m.get("forbidden_actors"), list):
            continue  # declarou, ainda que vazio — que e o ponto
        ident = str(m.get("mission_id") or "SEM-MISSION-ID")
        quando = str(
            m.get("issued_at")
            or m.get("created_at")
            or (m.get("causal") or {}).get("created_at")
            or ""
        )
        if not quando:
            pos.append(ident + " (SEM DATA — conta como pos-corte: ausencia nao isenta)")
        elif quando[:10] >= corte:
            pos.append(ident)
        else:
            pre.append(ident)
    return pos, pre


def validate_declaracao_de_proibicao(missoes: list[dict[str, Any]]) -> list[str]:
    """Emissao nova declara `forbidden_actors`; a divida antiga so encolhe."""
    errors: list[str] = []
    pos, pre = missoes_sem_declaracao_de_proibicao(missoes)
    if pos:
        errors.append(
            "MISSAO_SEM_DECLARACAO_DE_PROIBICAO: emitida em "
            f"{CORTE_DECLARACAO_DE_PROIBICAO} ou depois e sem `forbidden_actors`, "
            f"nem vazio: {sorted(pos)[:5]}{'...' if len(pos) > 5 else ''} "
            f"({len(pos)} no total). Campo faltando nao diz nada; `[]` diz que a "
            "missao nao proibe ninguem, e e o que torna a trava da T96 alcancavel."
        )
    if len(pre) > TETO_MISSOES_SEM_DECLARACAO:
        errors.append(
            f"DIVIDA_CRESCEU: {len(pre)} missoes anteriores ao corte sem declaracao, "
            f"contra teto de {TETO_MISSOES_SEM_DECLARACAO}. A divida so encolhe."
        )
    if len(pre) < TETO_MISSOES_SEM_DECLARACAO:
        errors.append(
            f"TETO_DESATUALIZADO: a divida caiu para {len(pre)} e o teto ainda diz "
            f"{TETO_MISSOES_SEM_DECLARACAO}. Baixe o teto no mesmo ato — catraca que "
            "so aperta de um lado deixa folga silenciosa."
        )
    return errors


# Pastas que NAO sao emissao real: fixture, candidato, overlay, isolamento e
# backup. Contar copia como original ja inflou uma cadeia de 16 para 101 nesta
# casa; o corte e estrutural, e os descartados sao CONTADOS, nunca omitidos.
_FORA_DA_EMISSAO_REAL = frozenset({
    "fixtures", "candidatos", "candidatos-r2", "candidatos-r3", "candidatos-r4",
    "lab", "overlay", "instrumentos", "fontes", "custodia", "isolamento",
    "isolamento-r2", "isolamento-r3", "isolamento-r4", "__pycache__",
    "backup-pre-canonizacao-t19",
})


def missoes_reais_em_disco(raiz: Path) -> tuple[list[dict[str, Any]], int]:
    """As EXECUTIVE_MISSION que sao emissao de verdade, e quantas foram descartadas."""
    reais: list[dict[str, Any]] = []
    descartadas = 0
    for caminho in raiz.rglob("*.json"):
        try:
            obj = json.loads(caminho.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(obj, dict) or obj.get("artifact_type") != "EXECUTIVE_MISSION":
            continue
        if _FORA_DA_EMISSAO_REAL & set(caminho.parts):
            descartadas += 1
            continue
        reais.append(obj)
    return reais, descartadas


# --------------------------------------------------------------------------
# T111 — o digest publicado no despacho tem de REPRODUZIR
#
# Ate 2026-08-25 os registros de despacho publicavam o sha256 CRU do arquivo da
# missao. Cru NAO E IDENTIDADE: a raiz do cofre guarda CRLF, todo worktree
# guarda LF (`.gitattributes` fixa `eol=lf`), e o mesmo conteudo da dois
# numeros. A barreira que o executor recebia FALHAVA POR CONSTRUCAO em checkout
# limpo — e falhar por EOL e indistinguivel de falhar por adulteracao para quem
# so compara strings: a trava contra troca de missao virava alarme falso
# exatamente onde deveria dar seguranca.
#
# Quem apontou foi a ORIGEM INDEPENDENTE da R4, medindo `10bbbb4b` na raiz
# contra `ac83e39f` no worktree dela. Tres modos de falha coexistiam nos quatro
# registros reais: digest AUSENTE (o 11, de 2026-08-08), digest CRU que nao
# reproduz normalizado (o 20), e digest TRUNCADO por defeito do meu script de
# emissao (o 26, que publicava `4d0b9f3c...`).
#
# A regra nao e "use a funcao certa" — isso e verificavel por leitura e portanto
# fraco. A regra e que o numero publicado RECOMPUTE a partir do arquivo, pela
# receita nomeada ao lado dele. Digest que nao reproduz nao e identidade,
# qualquer que seja a funcao que o gerou.
# --------------------------------------------------------------------------

# Divida MEDIDA em 2026-08-25: as entradas de despacho anteriores a esta trava
# que nao publicaram digest nenhum. Nao se retro-carimba registro congelado —
# faze-lo diria que aquele despacho publicou o que nao publicou.
DIVIDA_DESPACHO_SEM_DIGEST = (
    "11-DESPACHO-R3.json::08-EXECUTIVE-MISSION-R3.json",
    "11-DESPACHO-R3.json::09-EXECUTIVE-MISSION-ORIGEM-INDEPENDENTE-R3.json",
)
TETO_DESPACHOS_SEM_DIGEST = len(DIVIDA_DESPACHO_SEM_DIGEST)


def digests_de_despacho(
    registros: list[tuple[str, dict[str, Any]]], resolver
) -> tuple[list[str], list[str]]:
    """Separa as entradas de despacho em (nao reproduzem, sem digest).

    `registros` chega ja lido e `resolver` devolve o caminho da missao a partir
    do `mission_ref` — as duas coisas para que a trava possa ser exercitada com
    amostra. Trava que so sabe ler o disco nao consegue provar que fica vermelha;
    e a mesma disciplina de `retornos_sem_gate`, no `diretor-de-lentes`.
    """
    nao_reproduzem: list[str] = []
    sem_digest: list[str] = []
    for nome, reg in registros:
        if not isinstance(reg, dict):
            continue
        for entrada in reg.get("despachos") or []:
            if not isinstance(entrada, dict):
                continue
            ref = entrada.get("mission_ref")
            chave = f"{nome}::{ref}"
            publicado = entrada.get("mission_digest")
            if not isinstance(publicado, str) or not publicado.startswith("sha256:"):
                sem_digest.append(chave)
                continue
            caminho = resolver(nome, ref)
            if caminho is None or not Path(caminho).is_file():
                nao_reproduzem.append(chave + " (missao nao encontrada para recomputar)")
                continue
            recomputado = sha256_texto_normalizado(Path(caminho))
            if recomputado != publicado:
                nao_reproduzem.append(
                    f"{chave}: publicado {publicado[:22]}... recomputado {recomputado[:22]}..."
                )
    return nao_reproduzem, sem_digest


def validate_digest_de_despacho_reproduz(
    registros: list[tuple[str, dict[str, Any]]], resolver
) -> list[str]:
    """Digest publicado que nao recompute nao e identidade — e alarme falso."""
    errors: list[str] = []
    nao_reproduzem, sem_digest = digests_de_despacho(registros, resolver)
    if nao_reproduzem:
        errors.append(
            "DIGEST_DE_DESPACHO_NAO_REPRODUZ: o numero publicado nao recomputa a "
            f"partir do arquivo pela receita nomeada: {sorted(nao_reproduzem)[:3]}"
            f"{'...' if len(nao_reproduzem) > 3 else ''} ({len(nao_reproduzem)} no "
            "total). Quem confere em worktree limpo nao distingue isso de troca de missao."
        )
    if len(sem_digest) > TETO_DESPACHOS_SEM_DIGEST:
        errors.append(
            f"DIVIDA_CRESCEU: {len(sem_digest)} entradas de despacho sem digest, contra "
            f"teto de {TETO_DESPACHOS_SEM_DIGEST}. Despacho novo publica digest que reproduz."
        )
    if len(sem_digest) < TETO_DESPACHOS_SEM_DIGEST:
        errors.append(
            f"TETO_DESATUALIZADO: a divida caiu para {len(sem_digest)} e o teto ainda diz "
            f"{TETO_DESPACHOS_SEM_DIGEST}. Baixe o teto no mesmo ato."
        )
    return errors


def registros_de_despacho_em_disco(raiz: Path):
    """Os DISPATCH_RECORD que sao registro real, e o resolver do `mission_ref`."""
    achados: list[tuple[str, dict[str, Any]]] = []
    onde: dict[str, Path] = {}
    for caminho in raiz.rglob("*.json"):
        if _FORA_DA_EMISSAO_REAL & set(caminho.parts):
            continue
        try:
            obj = json.loads(caminho.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(obj, dict) and obj.get("artifact_type") == "DISPATCH_RECORD":
            achados.append((caminho.name, obj))
            onde[caminho.name] = caminho.parent

    def resolver(nome_registro: str, ref: object):
        pasta = onde.get(nome_registro)
        if pasta is None or not isinstance(ref, str) or not ref:
            return None
        return pasta / ref

    return achados, resolver

def run() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    schema_errors = validate_schema_shape(schema)
    schema_errors.extend(validate_package_files(evals))
    add_if(
        schema_errors,
        len(evals.get("cases", [])) < 8,
        "evals: são necessários ao menos oito casos",
    )

    normal_judge = judge_report([10, 10, 10], "PRODUCAO")
    below_judge = judge_report([9, 10, 10], "PRODUCAO")
    limit = limitation_report(below_judge)
    request = exception_request(below_judge, limit)
    auth = authorization(request)

    valid_normal_submission = submission(normal_judge)
    valid_exception_submission = submission(below_judge, limit, auth)
    waiting_submission = submission(below_judge, limit, None)
    normal_decision = decision(normal_judge, "VALIDATED", "quality_gate")

    fixture_contract_errors: list[str] = []
    fixtures = [
        ("executiveMission", mission(), "EXECUTIVE_MISSION"),
        ("judgeReport", normal_judge, "JUDGE_REPORT"),
        ("limitationReport", limit, "LIMITATION_REPORT"),
        ("exceptionRequest", request, "EXCEPTION_REQUEST"),
        ("exceptionAuthorization", auth, "EXCEPTION_AUTHORIZATION"),
        ("executiveSubmission", valid_normal_submission, "EXECUTIVE_SUBMISSION"),
        ("executiveDecision", normal_decision, "EXECUTIVE_DECISION"),
        ("capabilityGap", capability_gap(), "CAPABILITY_GAP"),
    ]
    for definition_name, artifact, label in fixtures:
        fixture_contract_errors.extend(
            validate_schema_keys(schema, definition_name, artifact, label)
        )

    cases: list[tuple[str, bool, list[str]]] = []

    # T38: pares vermelho/verde derivados do schema, incluindo os 10 envelopes
    # observados na rodada do nucleo. Os arquivos da campanha sao evidencia
    # congelada: nao sao reescritos; cada caso apenas os le e espera rejeicao.
    rotulo_isolado = {"artifact_type": "JUDGE_ASSIGNMENT"}
    rotulo_errors = validar_envelope_canonico(rotulo_isolado, "JUDGE_ASSIGNMENT")
    cases.append(
        (
            "T38 vermelho: rotulo JUDGE_ASSIGNMENT sem envelope e rejeitado pelo schema",
            False,
            rotulo_errors or ["rotulo isolado atravessou o schema canonico"],
        )
    )
    cases.append(
        (
            "T38 verde: envelope JUDGE_ASSIGNMENT completo passa no schema canonico",
            True,
            validar_envelope_canonico(
                _fixture_judge_assignment_canonica(), "JUDGE_ASSIGNMENT"
            ),
        )
    )

    for required_field in (
        "causal",
        "candidate_digest",
        "anonymized_candidate",
        "contract_excerpt",
        "evidence_index",
        "forbidden_context",
    ):
        invalid = _fixture_judge_assignment_canonica()
        invalid.pop(required_field)
        errors = validar_envelope_canonico(invalid, "JUDGE_ASSIGNMENT")
        cases.append(
            (
                f"T38 vermelho: required ausente ({required_field})",
                False,
                errors or [f"schema aceitou required ausente: {required_field}"],
            )
        )

    for extra_field in (
        "contract_id",
        "contract_version",
        "contract_digest",
        "required_level",
        "pacotes",
        "issued_by",
    ):
        invalid = _fixture_judge_assignment_canonica()
        invalid[extra_field] = "extra"
        errors = validar_envelope_canonico(invalid, "JUDGE_ASSIGNMENT")
        cases.append(
            (
                f"T38 vermelho: propriedade extra ({extra_field})",
                False,
                errors or [f"schema aceitou propriedade extra: {extra_field}"],
            )
        )

    invalid_custody = _fixture_judge_assignment_canonica()
    invalid_custody["custody_copy"]["arquivos"] = 1
    custody_errors = validar_envelope_canonico(invalid_custody, "JUDGE_ASSIGNMENT")
    cases.append(
        (
            "T38 vermelho: custody_copy.arquivos proibido pelo schema",
            False,
            custody_errors or ["schema aceitou custody_copy.arquivos"],
        )
    )

    invalid_write_path = _fixture_judge_assignment_canonica()
    invalid_write_path["write_path"] = "pareceres/robustez-e-evidencia/i2/"
    write_path_errors = validar_envelope_canonico(
        invalid_write_path, "JUDGE_ASSIGNMENT"
    )
    cases.append(
        (
            "T38 vermelho: write_path fora da trava ADR-016",
            False,
            write_path_errors or ["schema aceitou write_path fora do pattern"],
        )
    )

    campanha_t38 = ROOT / "evals" / "nucleo-de-comando-r2-2026-08-07"
    envelopes_observados = [
        ("JUDGMENT_REQUEST", campanha_t38 / "01-JUDGMENT-REQUEST.json"),
        ("CRITERIA_MATRIX", campanha_t38 / "02-CRITERIA-MATRIX.json"),
    ]
    envelopes_observados.extend(
        ("JUDGE_ASSIGNMENT", caminho)
        for caminho in sorted((campanha_t38 / "03-JUDGE-ASSIGNMENTS").glob("*.json"))
    )
    for envelope_kind, caminho in envelopes_observados:
        if not caminho.is_file():
            continue
        observado = json.loads(caminho.read_text(encoding="utf-8"))
        errors = validar_envelope_canonico(observado, envelope_kind)
        cases.append(
            (
                f"T38 vermelho: {caminho.name} rejeitado pelo schema canonico",
                False,
                errors or [f"envelope observado passou sem prova: {caminho}"],
            )
        )
    cases.append(
        (
            "T38: rodada com JUDGE-ASSIGNMENTS e selada mesmo sem marcador de parecer",
            True,
            []
            if _houve_julgamento(campanha_t38)
            else ["a footprint JUDGE-ASSIGNMENTS foi ignorada"],
        )
    )

    cases.append(("schema e refs locais", True, schema_errors))

    # --- T32: a trava de despacho, e as três armadilhas que ela atravessou ---
    #
    # Cada fixture abaixo é uma versão do classificador que JÁ EXISTIU e estava
    # errada. Elas não são hipóteses: são os três erros medidos em 2026-08-06,
    # congelados para não voltarem.
    cases.append(
        (
            "nenhuma rodada de julgamento nova sem JUDGE_ASSIGNMENT",
            True,
            validar_trava_de_despacho(ROOT / "evals"),
        )
    )

    prosa_denunciando_a_ausencia = [
        (
            "RELATORIO.md",
            "Estou operando em BLOCKED_BYPASS_ATTEMPT e julguei assim mesmo — "
            'sem JUDGE_ASSIGNMENT, minha própria SKILL.md:24-26 manda recusar. '
            '{"artifact_type": "JUDGE_ASSIGNMENT"}',
        ),
        (
            "PARECER.json",
            json.dumps(
                {
                    "artifact_type": "JUDGE_OPINION",
                    "razao": "a rodada correu sem assignment_id e sem "
                    "JUDGE_ASSIGNMENT; o CEO despachou direto às lentes",
                }
            ),
        ),
    ]
    cases.append(
        (
            "armadilha 1 — citar JUDGE_ASSIGNMENT em prosa não é ter sido designado",
            True,
            []
            if not tem_judge_assignment(prosa_denunciando_a_ausencia)
            else [
                "a menção em texto foi aceita como envelope: é exatamente o "
                "verde que a rodada mais irregular da casa receberia"
            ],
        )
    )

    envelope_da_fronteira_errada = [
        (
            "01-EXECUTIVE-MISSION.json",
            json.dumps(
                {
                    "artifact_type": "EXECUTIVE_MISSION",
                    "handoff_id": "HANDOFF-1",
                    "return_to": "ceo-maestro",
                }
            ),
        )
    ]
    cases.append(
        (
            "armadilha 2 — EXECUTIVE_MISSION não substitui JUDGE_ASSIGNMENT",
            True,
            []
            if not tem_judge_assignment(envelope_da_fronteira_errada)
            else [
                "envelope de CEO→executivo creditado como designação de juiz: "
                "crédito à trava errada"
            ],
        )
    )

    parecer_que_so_cita_a_designacao = [
        (
            "PARECER.json",
            json.dumps(
                {"artifact_type": "JUDGE_OPINION", "assignment_id": "ASSIGN-1"}
            ),
        )
    ]
    cases.append(
        (
            "armadilha 3 — citar assignment_id não prova designação",
            True,
            []
            if not tem_judge_assignment(parecer_que_so_cita_a_designacao)
            else [
                "parecer que referencia um assignment_id foi lido como o "
                "próprio artefato de designação"
            ],
        )
    )

    designacao_de_verdade = [
        ("ASSIGN-T38-I1.json", json.dumps(_fixture_judge_assignment_canonica()))
    ]
    cases.append(
        (
            "designação real é reconhecida (a trava não reprova quem cumpriu)",
            True,
            []
            if tem_judge_assignment(designacao_de_verdade)
            else ["JUDGE_ASSIGNMENT legítima foi recusada — a trava reprovaria "
                  "as quatro rodadas que seguiram o protocolo"],
        )
    )

    # --- T57: o manifesto se exercita, para não apodrecer no repositório ---
    #
    # O PORTÃO do manifesto contra a árvore real mora no CI (matriz de três
    # sistemas), e não aqui de propósito: exigir manifesto regenerado a cada
    # edição local trava o trabalho sem acrescentar segurança que o CI não dê.
    # O que mora aqui é o AUTOTESTE da ferramenta — sem ele, `manifesto.py` é
    # código que ninguém executa até o dia em que precisa dele.
    try:
        sys.path.insert(0, str(ROOT.parent))
        from _compartilhado.manifesto import comparar, gerar, verificar
    except ImportError as erro:  # pragma: no cover
        cases.append(("manifesto da Estrutura é importável", True, [str(erro)]))
    else:
        _erros_man: list[str] = []
        with tempfile.TemporaryDirectory() as _tmp:
            _raiz = Path(_tmp)
            (_raiz / "a.md").write_bytes(b"linha\r\nlinha 2\r\n")
            (_raiz / "sub").mkdir()
            (_raiz / "sub" / "b.py").write_bytes(b"x = 1\n")

            import _compartilhado.manifesto as _mod
            _antes_raiz = _mod.RAIZ
            try:
                _mod.RAIZ = _raiz
                _m = gerar(_raiz, "2026-01-01T00:00:00-03:00", None)
                if _m["total_de_arquivos"] != 2:
                    _erros_man.append(
                        f"manifesto contou {_m['total_de_arquivos']} de 2 arquivos")
                if verificar(_raiz, _m):
                    _erros_man.append("manifesto recém-gerado não confere consigo")

                # O ponto inteiro: o MESMO conteúdo com o outro fim de linha tem
                # de continuar conferindo, senão o manifesto não sobrevive a um
                # checkout noutro sistema e o CI multi-SO vira ruído.
                (_raiz / "a.md").write_bytes(b"linha\nlinha 2\n")
                if verificar(_raiz, _m):
                    _erros_man.append(
                        "CRLF trocado por LF quebrou o manifesto — ele voltou a "
                        "depender do checkout e não serve para CI de três sistemas")

                # E tem de saber recusar: conteúdo de verdade, remoção, acréscimo.
                (_raiz / "a.md").write_bytes(b"outro conteudo\n")
                if not verificar(_raiz, _m):
                    _erros_man.append("conteúdo alterado passou despercebido")
                (_raiz / "a.md").unlink()
                if not verificar(_raiz, _m):
                    _erros_man.append("arquivo removido passou despercebido")
                (_raiz / "a.md").write_bytes(b"linha\nlinha 2\n")
                (_raiz / "intruso.txt").write_bytes(b"i\n")
                if not verificar(_raiz, _m):
                    _erros_man.append("arquivo acrescentado passou despercebido")

                _d = comparar({"x": "sha256:1", "some": "sha256:2"},
                              {"x": "sha256:9", "novo": "sha256:3"})
                if (_d["alterados"], _d["removidos"], _d["acrescentados"]) != (
                        ["x"], ["some"], ["novo"]):
                    _erros_man.append(f"comparar() erra os três sentidos: {_d}")
            finally:
                _mod.RAIZ = _antes_raiz
        cases.append(
            ("manifesto da Estrutura: sobrevive a EOL e recusa mudança real",
             True, _erros_man))

    # --- T33: o INSTRUMENTO de medição entra na suíte de regressão ---
    #
    # Em 2026-08-06 o CEO publicou a oito juízes uma evidência com quatro
    # defeitos, todos do coletor e nenhum do objeto medido. Prova de mutação em
    # script solto apodrece; aqui o coletor é reexecutado a cada rodada.
    sys.path.insert(0, str(ROOT / "evals"))
    try:
        import coletar_saida_crua as _coletor  # noqa: E402
        from coletar_saida_crua import (  # noqa: E402
            SUBORDINADOS_ESPERADOS,
            acentos_intactos,
            coerencia,
            coletar,
            conferir_expectativa,
            subordinados_diretos,
            sumario_proprio,
        )
    except ImportError as erro:  # pragma: no cover
        cases.append(("coletor de saída crua é importável", True, [str(erro)]))
    else:
        # Imita o `departamento-negocios`: sumário próprio em caixa alta e eco
        # da cauda do vizinho no fim. A receita antiga colhia a última linha.
        saida_com_eco_do_vizinho = (
            "[FAIL] a\n[FAIL] b\n[FAIL] c\n"
            "RESULTADO: 230/233 PASS; 3 FAIL; 0 WARN\n"
            "   detalhe do vizinho:\n"
            "Resultado: 99/100 casos passaram.\n"
        )
        colhido = sumario_proprio(saida_com_eco_do_vizinho)
        cases.append(
            (
                "coletor colhe o sumário PRÓPRIO, não o do vizinho ecoado",
                True,
                []
                if (colhido.get("passou"), colhido.get("total")) == (230, 233)
                else [
                    f"colheu {colhido} — a receita 'último da saída' publicou o "
                    f"99/100 do Diretor como sendo de Negócios"
                ],
            )
        )
        cases.append(
            (
                "coerência interna é gate: 3 FAIL não convive com 99/100",
                True,
                []
                if coerencia(saida_com_eco_do_vizinho,
                             {"passou": 99, "total": 100, "token": "x"})
                else ["a autocontradição publicada em 00-RESUMO.json passaria de novo"],
            )
        )
        cases.append(
            (
                "coerência interna não acusa número correto",
                True,
                coerencia(saida_com_eco_do_vizinho,
                          {"passou": 230, "total": 233, "token": "x"}),
            )
        )
        cases.append(
            (
                "ambiguidade de sumário vira estado nomeado, nunca palpite",
                True,
                []
                if sumario_proprio(
                    "Resultado: 10/10 casos passaram.\n"
                    "Resultado: 20/20 casos passaram.\n"
                ).get("estado") == "AMBIGUO"
                else ["o coletor adivinhou qual dos dois sumários era o próprio"],
            )
        )
        cases.append(
            (
                "mojibake na saída capturada é detectado",
                True,
                []
                if acentos_intactos("único é ação")
                and not acentos_intactos("troca sem dono Ãºnico Ã© negada")
                else ["a decodificação errada que corrompeu as quatro saídas "
                      "publicadas passaria despercebida"],
            )
        )
        # Defeito 10: maiúscula normal de PT-BR fechava o gate. As três
        # palavras abaixo são as que apareceram de verdade nas saídas de
        # `ceo-maestro` e `departamento-desenvolvimento` e as bloquearam.
        _pt_br_legitimo = [
            "gate fechado NÃO deixa 00-RESUMO.json",
            "ramo da DECLARAÇÃO acusa sozinho",
            "SUPOSIÇÃO sem dizer por quê",
            "AÇÃO, ORGANIZAÇÃO, PADRÃO, IRMÃOS",
        ]
        cases.append(
            (
                "maiúscula acentuada de PT-BR não é confundida com mojibake",
                True,
                [f"{s!r} acusado como mojibake — o gate bloquearia evidência boa"
                 for s in _pt_br_legitimo if not acentos_intactos(s)],
            )
        )

        # --- T40/T41: a rodada 2 julgou o conserto acima e achou cinco furos ---
        #
        # Os cinco casos anteriores passavam TODOS no mesmo fixture, em que os
        # dois ramos de `coerencia()` disparam juntos. Medido em 2026-08-07:
        # matando `RE_FAIL_DECL` a função ainda devolvia 1 erro e os cinco
        # seguiam verdes. Cada ramo ganha aqui um fixture em que SÓ ele acusa.
        so_a_declaracao = (
            "[FAIL] a\n[FAIL] b\n[FAIL] c\n"
            "RESULTADO: 230/233 PASS; 5 FAIL; 0 WARN\n"
        )
        _so_decl = coerencia(so_a_declaracao,
                             {"passou": 230, "total": 233, "token": "x"})
        cases.append(
            (
                "ramo da DECLARAÇÃO acusa sozinho (contagem bate, declaração não)",
                True,
                []
                if len(_so_decl) == 1 and "declara 5 FAIL" in _so_decl[0]
                else [f"matar RE_FAIL_DECL não avermelharia nada — devolveu {_so_decl}"],
            )
        )
        so_a_contagem = "[FAIL] a\nRESULTADO: 230/233 PASS; 3 FAIL; 0 WARN\n"
        _so_cont = coerencia(so_a_contagem,
                             {"passou": 230, "total": 233, "token": "x"})
        cases.append(
            (
                "ramo da CONTAGEM acusa sozinho (declaração bate, contagem não)",
                True,
                []
                if len(_so_cont) == 1 and "[FAIL]" in _so_cont[0]
                else [f"a contagem de linhas [FAIL] não é exercitada — devolveu {_so_cont}"],
            )
        )

        # Defeito 5: o gate ficava ABERTO justamente nos dois estados que o
        # defeito 1 produz — `coerencia()` devolvia [] e a evidência saía com
        # `problemas_do_coletor: []` sem o coletor saber o resultado do pacote.
        for _estado in ("SEM_SUMARIO", "AMBIGUO"):
            cases.append(
                (
                    f"sumário {_estado} é PROBLEMA, não silêncio",
                    True,
                    []
                    if coerencia(so_a_contagem, {"estado": _estado, "motivo": "m"})
                    else [f"{_estado} devolve [] e o gate fica aberto sem o "
                          f"coletor saber o resultado do pacote"],
                )
            )
        cases.append(
            (
                "sem sumário e exit≠0 acusa validador morto, não medição limpa",
                True,
                []
                if len(coerencia("", {"estado": "SEM_SUMARIO"}, 1)) == 2
                else ["validador que morre sairia publicado como medição limpa"],
            )
        )

        # Defeito 6: `"exit": proc.returncode` era gravado e o returncode nunca
        # comparado (medido: zero ocorrências no arquivo). O validador faz
        # `return 1 if failures else 0`, então exit é codificação redundante do
        # sumário e divergir dele é contradição.
        cases.append(
            (
                "exit=1 com sumário sem falha é contradição",
                True,
                []
                if coerencia("RESULTADO: 10/10 PASS; 0 FAIL; 0 WARN\n",
                             {"passou": 10, "total": 10, "token": "x"}, 1)
                else ["o exit gravado continua sem ser lido"],
            )
        )
        cases.append(
            (
                "exit=0 com sumário com falha é contradição",
                True,
                []
                if coerencia("[FAIL] x\nRESULTADO: 9/10 PASS; 1 FAIL; 0 WARN\n",
                             {"passou": 9, "total": 10, "token": "x"}, 0)
                else ["o exit gravado continua sem ser lido"],
            )
        )
        cases.append(
            (
                "exit coerente com o sumário não acusa nada",
                True,
                coerencia("[FAIL] x\nRESULTADO: 9/10 PASS; 1 FAIL; 0 WARN\n",
                          {"passou": 9, "total": 10, "token": "x"}, 1),
            )
        )

        # Defeito 9: a tabela tinha UMA chave de quinze e 13 pacotes publicavam
        # `subordinados_diretos: []` — lista vazia com cara de medida.
        # A exclusão por nome de pasta (`candidatos`, `lab`, …) não alcançava
        # `custodia/` nem `isolamento/`, e por isso quatro FIXTURES de campanha —
        # `C07-lf`, `C07-lf-baseline`, `c02-vivo`, `candidato` — eram cobradas como
        # se fossem pacotes desta estrutura (medido em 2026-08-20).
        #
        # O corte é pelo caminho do PACOTE, não pelo do arquivo: aqui não serve
        # `"evals" in p.parts`, porque **todo pacote real tem `evals/` no caminho do
        # próprio validador**. Um pacote real tem `evals/` como FILHO; uma cópia de
        # campanha tem `evals/` como ANCESTRAL. `p.parents[1]` é o pacote, e é nele
        # que a distinção aparece.
        _com_validador = {
            p.parents[1].name
            for p in (ROOT.parent).rglob("evals/validate_workflow.py")
            if not {"candidatos", "instrumentos", "lab", "fontes"} & set(p.parts)
            and "backup-" not in str(p)
            and "evals" not in p.parents[1].parts
        }
        _sem_expectativa = sorted(_com_validador - set(SUBORDINADOS_ESPERADOS))
        cases.append(
            (
                "todo pacote com validador tem expectativa declarada",
                True,
                []
                if not _sem_expectativa
                else [f"sem expectativa: {_sem_expectativa} — a tabela nasce "
                      f"com todas as chaves ou o campo não é publicável"],
            )
        )

        # A busca de um nível só enxergava a primeira das três formas de
        # subordinação. Os dois números abaixo são os que a evidência publicou
        # errado: Diretor com 1 onde tem 11, Negócios com 0 onde tem 3.
        _diretor = subordinados_diretos(ROOT / "diretor-de-lentes")
        _negocios = subordinados_diretos(ROOT / "departamento-negocios")
        cases.append(
            (
                "busca segue as três formas de subordinação (irmão, agentes/, "
                "departamentos-operacionais/)",
                True,
                []
                if len(_diretor) == 11 and len(_negocios) == 3
                and "departamento-juizes" in _diretor
                else [f"Diretor={len(_diretor)} (esperado 11), "
                      f"Negócios={len(_negocios)} (esperado 3)"],
            )
        )

        # Expectativa órfã é pior que ausente: parece conferida e não está mais
        # ligada a nada. Aqui a âncora é adulterada e a conferência tem de acusar.
        _guardado = dict(SUBORDINADOS_ESPERADOS["departamento-negocios"])
        try:
            SUBORDINADOS_ESPERADOS["departamento-negocios"] = dict(
                _guardado, ancora="LINHA QUE NÃO EXISTE EM CONTRATO NENHUM"
            )
            _orfa = conferir_expectativa(
                "departamento-negocios", ROOT / "departamento-negocios",
                subordinados_diretos(ROOT / "departamento-negocios"),
            )
        finally:
            SUBORDINADOS_ESPERADOS["departamento-negocios"] = _guardado
        cases.append(
            (
                "expectativa cuja âncora sumiu do contrato é acusada como ÓRFÃ",
                True,
                []
                if _orfa.get("estado") == "ANCORA_ORFA" and _orfa["problemas"]
                else ["a expectativa continuaria 'conferida' contra um contrato "
                      "que mudou"],
            )
        )

        # Defeito 7: a não-publicação era promessa em prosa — o 00-RESUMO.json
        # já estava no diretório de publicação quando o gate fechava. Aqui os
        # dois sentidos são exercidos de ponta a ponta, num pacote de mentira.
        def _pacote_de_mentira(base: Path, saida: str) -> Path:
            pkg = base / "pacote-de-mentira"
            (pkg / "evals").mkdir(parents=True, exist_ok=True)
            (pkg / "CONTRATO-DE-COMPROMISSO.md").write_text(
                "- **Subordinados diretos:** nenhum.\n", encoding="utf-8")
            (pkg / "evals" / "validate_workflow.py").write_text(
                "import sys\n"
                f"sys.stdout.write({saida!r})\n"
                "sys.exit(0)\n",
                encoding="utf-8")
            return pkg

        _erros_pub = []
        with tempfile.TemporaryDirectory() as _tmp:
            _base = Path(_tmp)
            SUBORDINADOS_ESPERADOS["pacote-de-mentira"] = {
                "quantidade": 0, "fonte": "CONTRATO-DE-COMPROMISSO.md",
                "ancora": "- **Subordinados diretos:** nenhum.",
            }
            try:
                _limpo = _pacote_de_mentira(
                    _base / "a", "RESULTADO: 2/2 PASS; 0 FAIL; 0 WARN\n")
                _dest_ok = _base / "pub-ok"
                _rc = coletar({"pacote-de-mentira": _limpo}, _dest_ok)
                if _rc != 0 or not (_dest_ok / "00-RESUMO.json").is_file():
                    _erros_pub.append("gate aberto não publicou o 00-RESUMO.json")
                if (_dest_ok / "00-BLOQUEADO.json").exists():
                    _erros_pub.append("gate aberto escreveu 00-BLOQUEADO.json")

                # O pacote sujo bloqueia por DOIS motivos independentes — duas
                # linhas [FAIL] para um sumário que implica uma, e exit=0 onde
                # o sumário pede 1. Um motivo só faria este caso depender de
                # outra trava: medido, matar a regra do exit derrubava ESTE
                # caso junto, e um teste de publicação tem de falar só sobre
                # publicação.
                _sujo = _pacote_de_mentira(
                    _base / "b",
                    "[FAIL] x\n[FAIL] y\nRESULTADO: 1/2 PASS; 1 FAIL; 0 WARN\n")
                _dest_bad = _base / "pub-bloqueada"
                _rc2 = coletar({"pacote-de-mentira": _sujo}, _dest_bad)
                if _rc2 == 0:
                    _erros_pub.append("gate fechado devolveu sucesso")
                if (_dest_bad / "00-RESUMO.json").exists():
                    _erros_pub.append(
                        "GATE FECHADO E O 00-RESUMO.json EXISTE — a "
                        "não-publicação continua sendo promessa em prosa")
                if not (_dest_bad / "00-BLOQUEADO.json").is_file():
                    _erros_pub.append("gate fechado não nomeou o bloqueio")
            finally:
                SUBORDINADOS_ESPERADOS.pop("pacote-de-mentira", None)
        cases.append(
            ("gate fechado NÃO deixa 00-RESUMO.json no diretório de publicação",
             True, _erros_pub)
        )

    # --- tarefa 27: a conferência de contagem não pode sumir do coletor -------
    #
    # A prova de mutação da T27 mediu isto e não escondeu: com a chamada de
    # `_selo_confere_com_execucao` removida do coletor, um `PLACAR.md` declarando
    # `999/999` com o digest certo volta a passar em silêncio. A conferência é a
    # ÚNICA coisa que pega o número — e trava que ninguém exige erode, que é o
    # `gate-que-nao-se-autoexige-erode` desta casa.
    #
    # Conferência ESTRUTURAL (AST), não textual: menção em comentário ou docstring
    # não é chamada, e validador de string aceitaria as duas.
    _erros_conferencia = []
    try:
        _fonte_coletor = (ROOT / "evals" / "coletar_saida_crua.py").read_text(
            encoding="utf-8"
        )
        import ast as _ast
        _chama = any(
            isinstance(_no, _ast.Call)
            and (getattr(_no.func, "id", None) or getattr(_no.func, "attr", None))
            == "_selo_confere_com_execucao"
            and _no.args
            for _no in _ast.walk(_ast.parse(_fonte_coletor))
        )
        if not _chama:
            _erros_conferencia.append(
                "CONFERENCIA_DE_CONTAGEM_AUSENTE: o coletor não chama "
                "_selo_confere_com_execucao(), então a contagem publicada volta a "
                "não ser comparada com a execução — e um PLACAR com o número errado "
                "e o digest certo passa em silêncio (tarefa 27)"
            )
    except (OSError, SyntaxError) as _exc:
        _erros_conferencia.append(
            f"CONFERENCIA_DE_CONTAGEM_NAO_AVALIADA: o coletor não pôde ser lido ou "
            f"parseado ({_exc.__class__.__name__}); ausência de conferência não é "
            "conformidade"
        )
    cases.append(
        ("o coletor confere a contagem publicada contra a execução",
         True, _erros_conferencia)
    )

    # --- tarefa 66: a trava da receita no envelope não pode sair do fluxo ----
    #
    # Medido em 2026-08-22, mutante M7: removida a chamada de
    # `validate_receita_declarada_no_envelope()` do `run()` dos Juízes, o pacote
    # devolve 172/173 com ZERO FAIL fora do selo — nada nomeia a trava ausente,
    # e só a contagem se move. É `gate-que-nao-se-autoexige-erode` pela terceira
    # vez nesta semana (T55, T27, e agora esta).
    #
    # A conferência mora AQUI, e não no próprio validador dos Juízes, por uma
    # razão medida: `mute-a-trava-alheia-nao-a-sua` — vigia que vive no mesmo
    # arquivo que vigia sai junto na mesma edição. Daqui, apagar a trava passa a
    # exigir editar DOIS pacotes e saber que o segundo existe.
    _erros_receita_no_envelope = []
    try:
        _fonte_juizes = (
            ROOT / "diretor-de-lentes" / "departamento-juizes" / "evals"
            / "validate_workflow.py"
        ).read_text(encoding="utf-8")
        import ast as _ast2
        _chama_receita = any(
            isinstance(_no, _ast2.Call)
            and (getattr(_no.func, "id", None) or getattr(_no.func, "attr", None))
            == "validate_receita_declarada_no_envelope"
            for _no in _ast2.walk(_ast2.parse(_fonte_juizes))
        )
        if not _chama_receita:
            _erros_receita_no_envelope.append(
                "RECEITA_NO_ENVELOPE_AUSENTE: o validador dos Juízes não chama "
                "validate_receita_declarada_no_envelope(), então um envelope novo "
                "sem `custody_copy.digest_recipe` volta a chegar ao juiz — que foi "
                "o que custou 8 tentativas em 2026-08-08, e 16, 438 e 1440 a três "
                "juízes na véspera (tarefa 66)"
            )
    except (OSError, SyntaxError) as _exc2:
        _erros_receita_no_envelope.append(
            f"RECEITA_NO_ENVELOPE_NAO_AVALIADA: o validador dos Juízes não pôde "
            f"ser lido ou parseado ({_exc2.__class__.__name__}); ausência de "
            "conferência não é conformidade"
        )
    cases.append(
        ("os Juízes exigem a receita do digest no envelope gravado",
         True, _erros_receita_no_envelope)
    )

    # --- tarefas 103 e 104: o motor não pode parar de exercitar um detector --
    #
    # ESTE VIGIA ERA TRÊS. As tarefas 27, 66 e 103 instalaram, cada uma, um bloco
    # de AST quase idêntico ao lado do outro — conserto de instância repetido,
    # que é o defeito que esta casa nomeia como
    # `conserto-de-instancia-nao-e-conserto-de-mecanismo`. A tarefa 104 seria a
    # quarta cópia; virou lista.
    #
    # POR QUE AQUI e não no próprio motor: `mute-a-trava-alheia-nao-a-sua` —
    # vigia que mora no arquivo que vigia sai junto na mesma edição. Daqui,
    # apagar um detector exige editar DOIS pacotes.
    #
    # Medido em 2026-08-22, mutante M7 da tarefa 103: sem a chamada, o motor
    # imprime `76/76 casos passaram` — verde perfeito com nove casos a menos, e
    # nada percebe. O da 104 some do mesmo jeito.
    DETECTORES_EXERCITADOS_PELO_MOTOR = {
        "digest_de_arvore_results":
            "a receita do digest de árvore deixa de ser exercitada, e um digest "
            "que não reproduz volta a passar por identidade",
        "adr_series_results":
            "a unicidade da série de ADR deixa de ser exercitada, e um número "
            "duplicado reprova os quinze pacotes de uma vez sem aviso",
        "frontmatter_allowlist_results":
            "a allowlist do frontmatter deixa de ser exercitada, e AFROUXAR o "
            "ADR-025 volta a ser indetectável (tarefa 86)",
        "base_do_candidato_results":
            "a base declarada de um candidato volta a não ser conferida, e um "
            "overlay de dezenove dias promove por cima de travas novas (tarefa 103)",
        "sondas_e_evidencias_results":
            "sonda duplicada e evidência que não discrimina voltam a passar, e o "
            "denominador da suíte volta a contar casos que medem a mesma coisa "
            "(tarefa 104)",
    }
    _erros_detectores = []
    try:
        _fonte_motor = (
            ROOT.parent / "_compartilhado" / "teste_validador_schema.py"
        ).read_text(encoding="utf-8")
        import ast as _ast3
        _arvore_motor = _ast3.parse(_fonte_motor)
        _definidos = {
            _no.name for _no in _ast3.walk(_arvore_motor)
            if isinstance(_no, (_ast3.FunctionDef, _ast3.AsyncFunctionDef))
            and _no.name.endswith("_results")
        }
        _chamados = {
            (getattr(_no.func, "id", None) or getattr(_no.func, "attr", None))
            for _no in _ast3.walk(_arvore_motor) if isinstance(_no, _ast3.Call)
        }
        for _nome_det in sorted(_definidos):
            if _nome_det not in _chamados:
                _erros_detectores.append(
                    f"DETECTOR_NAO_EXERCITADO: o motor define {_nome_det}() e não "
                    f"o chama — "
                    + DETECTORES_EXERCITADOS_PELO_MOTOR.get(
                        _nome_det, "detector não declarado nesta lista")
                )
            if _nome_det not in DETECTORES_EXERCITADOS_PELO_MOTOR:
                _erros_detectores.append(
                    f"DETECTOR_NAO_DECLARADO: o motor define {_nome_det}() e ele "
                    "não está em DETECTORES_EXERCITADOS_PELO_MOTOR. A lista existe "
                    "para dizer O QUE QUEBRA quando o detector some; entrada que "
                    "falta é vigia que parou de vigiar sem ninguém notar"
                )
        for _nome_det in sorted(DETECTORES_EXERCITADOS_PELO_MOTOR):
            if _nome_det not in _definidos:
                _erros_detectores.append(
                    f"DETECTOR_DECLARADO_INEXISTENTE: {_nome_det}() está na lista "
                    "e o motor não o define — lista que aponta para o vazio dá "
                    "sensação de cobertura sem cobrir nada"
                )
    except (OSError, SyntaxError) as _exc3:
        _erros_detectores.append(
            f"DETECTORES_NAO_AVALIADOS: o motor compartilhado não pôde ser lido "
            f"ou parseado ({_exc3.__class__.__name__}); ausência de conferência "
            "não é conformidade"
        )
    cases.append(
        ("o motor exercita todos os detectores compartilhados declarados",
         True, _erros_detectores)
    )

    # --- tarefa 98: autoteste definido e nunca chamado é decoração ----------
    #
    # Achado da própria tarefa 98, e ele é sobre trabalho MEU: varrendo o
    # conjunto vivo, 14 de 15 `_autoteste_*` de `_compartilhado` eram
    # alcançados e UM não — `_autoteste_da_contagem`, escrito na manhã do mesmo
    # dia pela tarefa 27. Definido, correto, e chamado por ninguém.
    #
    # É a forma mais silenciosa de `verificar-presenca-nao-e-verificar-efeito`:
    # o autoteste EXISTE, passa quando executado à mão, e não protege nada.
    # A varredura é por ALCANCE no conjunto vivo, não por "chamado no próprio
    # módulo" — os autotestes das tarefas 103 e 104 moram em
    # `verificacoes_pacote.py` e quem os chama é o motor, e acusá-los seria
    # `gate-que-barra-evidencia-boa`.
    _erros_orfaos = []
    try:
        import ast as _ast4
        _vivos = [
            ROOT.parent / "_compartilhado" / "verificacoes_estrutura.py",
            ROOT.parent / "_compartilhado" / "verificacoes_pacote.py",
            ROOT.parent / "_compartilhado" / "validador_schema.py",
            ROOT.parent / "_compartilhado" / "teste_validador_schema.py",
            ROOT.parent / "_compartilhado" / "manifesto.py",
            ROOT.parent / "_compartilhado" / "selar_contagem.py",
            ROOT / "evals" / "coletar_saida_crua.py",
            # TAREFA 100 — o proprio validador do CEO faltava aqui, e a
            # ausencia produziu uma ACUSACAO FALSA que a linha de baixo
            # desmentia: `validate_tetos_no_pacote` era acusada de nao ser
            # chamada enquanto o caso seguinte passava por chama-la. E vários
            # call sites de producao moram aqui; conjunto vivo incompleto e
            # detector cego com outra roupa.
            ROOT / "evals" / "validate_workflow.py",
        ]
        _definidos: dict[str, str] = {}
        _alcancados: set[str] = set()
        # ALCANCE DE PRODUÇÃO — chamada de dentro de um `_autoteste_*` NÃO conta.
        #
        # Achado do mutante M7 da tarefa 99, e ele derrubou a PRIMEIRA versão
        # desta trava: `travas_sombreadas` é chamada pelo autoteste dela mesma,
        # então remover a chamada de PRODUÇÃO deixava a do teste e a trava se
        # dava por satisfeita. Ser exercitado por um teste não é estar ligado
        # ao fluxo — é a mesma confusão que esta casa persegue desde o primeiro
        # degrau, cometida dentro da trava que existe para persegui-la.
        _alcancados_em_producao: set[str] = set()
        for _arq in _vivos:
            if not _arq.is_file():
                continue
            _arvore = _ast4.parse(_arq.read_text(encoding="utf-8"))
            _dentro_de_autoteste: set[int] = set()
            for _no in _ast4.walk(_arvore):
                if (isinstance(_no, (_ast4.FunctionDef, _ast4.AsyncFunctionDef))
                        and _no.name.startswith("_autoteste")):
                    _definidos[_no.name] = _arq.name
                    for _filho in _ast4.walk(_no):
                        _dentro_de_autoteste.add(id(_filho))
            for _no in _ast4.walk(_arvore):
                if isinstance(_no, _ast4.Call):
                    _nm = getattr(_no.func, "id", None) or getattr(_no.func, "attr", None)
                    if _nm:
                        _alcancados.add(_nm)
                        if id(_no) not in _dentro_de_autoteste:
                            _alcancados_em_producao.add(_nm)
                if isinstance(_no, _ast4.ImportFrom):
                    for _a in _no.names:
                        _alcancados.add(_a.name)
        if not _definidos:
            _erros_orfaos.append(
                "VARREDURA_DE_AUTOTESTE_CEGA: a varredura não encontrou "
                "autoteste NENHUM no conjunto vivo, e a casa tem quinze. Zero "
                "de detector é suspeita, não conformidade — sem isto, cegar a "
                "varredura seria a rota mais barata para desligar esta trava"
            )
        # TAREFA 99 — a mesma varredura serve para trava que NÃO é autoteste.
        #
        # Medido: removida a chamada de `travas_sombreadas` de
        # `validate_cobertura_de_validadores`, a casa fecha 157/157 e nada
        # acusa. A trava continua definida, correta, e deixa de proteger — a
        # mesma forma do autoteste órfão, num objeto que não começa com
        # `_autoteste`. Por isso a lista abaixo é NOMEADA: ela diz quais travas
        # não podem sair do fluxo, com o que se perde quando saem.
        TRAVAS_QUE_PRECISAM_SER_ALCANCADAS = {
            "validate_exclusoes_declaradas":
                "um gate volta a poder consultar constante de exclusao sem "
                "publicar o que deixa de fora -- ponto cego nao declarado "
                "(tarefa 60)",
            "remocoes_nao_declaradas":
                "arquivo que some entre dois manifestos volta a nao deixar "
                "rastro: regenerar depois de apagar faz `verificar` passar, "
                "porque a arvore nova e descrita com perfeicao (tarefa 57)",
            "digests_truncados_sem_original":
                "um digest volta a poder ser publicado só truncado numa linha de "
                "placar marcada como executada, sem que ninguém consiga "
                "conferi-lo (tarefa 102)",
            "validate_tetos_no_pacote":
                "o teto declarado de um mecanismo volta a poder apontar para "
                "fora do pacote e a encolher em silêncio (tarefa 100)",
            "travas_sombreadas":
                "o nome de uma trava pode ser reatribuído a um stub e a chamada "
                "continua sendo RECONHECIDA — resolver apelido sem esta guarda "
                "troca um falso positivo por um falso NEGATIVO (tarefa 99)",
        }
        for _nome_tr, _perda in sorted(TRAVAS_QUE_PRECISAM_SER_ALCANCADAS.items()):
            if _nome_tr not in _alcancados_em_producao:
                _erros_orfaos.append(
                    f"TRAVA_NAO_ALCANCADA: {_nome_tr}() está declarada como "
                    f"obrigatória e não é chamada em lugar nenhum do conjunto "
                    f"vivo. Consequência: {_perda}"
                )
        for _nome_at in sorted(set(_definidos) - _alcancados):
            _erros_orfaos.append(
                f"AUTOTESTE_ORFAO: {_nome_at}() está definido em "
                f"{_definidos[_nome_at]} e não é chamado em lugar nenhum do "
                "conjunto vivo. Autoteste que ninguém executa passa quando "
                "rodado à mão e não protege nada — e faz o registro da rodada "
                "afirmar que um mutante morreu por ele (tarefa 98)"
            )
    except (OSError, SyntaxError) as _exc4:
        _erros_orfaos.append(
            f"AUTOTESTES_NAO_AVALIADOS: o conjunto vivo não pôde ser lido ou "
            f"parseado ({_exc4.__class__.__name__}); ausência de conferência "
            "não é conformidade"
        )
    cases.append(
        ("nenhum autoteste compartilhado está órfão", True, _erros_orfaos)
    )

    # --- tarefa 100: o teto declarado mora no PACOTE, e não numa fixture -----
    #
    # Duas funções de `verificacoes_estrutura.py` declaravam o próprio teto
    # apontando para `manifest.json::o_que_este_mecanismo_NAO_pega` — chave que
    # **não existe em artefato de pacote nenhum**, só em manifestos de candidato
    # dentro de `evals/`. Quem lia a docstring não tinha onde chegar.
    #
    # E o teto encolhia sem vermelho: a rodada 2 daquela campanha removeu itens
    # da chave e só foi apanhada por leitura humana.
    _erros_tetos = []
    try:
        _fonte_estrutura = (
            ROOT.parent / "_compartilhado" / "verificacoes_estrutura.py"
        ).read_text(encoding="utf-8")
        _erros_tetos = validate_tetos_no_pacote(_fonte_estrutura)
    except OSError as _exc5:
        _erros_tetos = [
            f"TETOS_NAO_AVALIADOS: o módulo compartilhado não pôde ser lido "
            f"({_exc5.__class__.__name__}); ausência de conferência não é "
            "conformidade"
        ]
    cases.append(
        ("todo teto declarado mora no pacote, e a lista não encolheu",
         True, _erros_tetos)
    )

    # --- tarefa 60: gate que exclui em silêncio não é gate calibrado --------
    #
    # A pepita veio do `/cso` do gstack, que publica 17 exclusões e um corte de
    # confiança. Aqui os gates são BINÁRIOS — e declarar isso é a resposta que a
    # forma admite ("ou declara que não tem nenhum"). O que passa a ser
    # obrigatório é publicar O QUE cada gate deixa de fora.
    cases.append(
        ("todo gate que exclui publica o que deixa de fora", True,
         validate_exclusoes_declaradas(_fonte_estrutura))
    )

    # --- tarefa 46, fatia 2: o ANALYSIS_RETURN passa a ser exercitado --------
    #
    # A fatia 1 pôs `$defs/analysisReturn` no schema e a cadeia seguiu 160/160 —
    # prova de que ninguém o exercitava. Definição sem caso é o primeiro degrau
    # da progressão desta casa.
    #
    # POR QUE ISTO NÃO É O OVERLAY DO `cand-A2`: aquele overlay é +714 −1528
    # contra a árvore viva e APAGARIA oito travas nascidas depois de
    # 2026-08-03. Medido com o instrumento da tarefa 103, a base declarada dele
    # bate em ZERO de NOVE alvos. O que entrou foi a CONTRIBUIÇÃO isolada — um
    # `$defs` e a fiação —, e o que ele reverteria (`aggregationRule`,
    # `aggregationMethod`, `scoreRange`) ficou onde estava.
    _analysis_def = schema["$defs"]["analysisReturn"]
    _missao_analise = mission()
    _missao_analise["deliverable_type"] = "analysis"
    _retorno_analise = {
        "artifact_type": "ANALYSIS_RETURN",
        "return_id": "analysis-return-001",
        "causal": causal("departamento-evolucao-skills", "n/a",
                         "message-analysis-001", round_number=1),
        "submitted_by": "departamento-evolucao-skills",
        "content_type": "analysis",
        "executive_mission": _missao_analise,
        "scope_touched": ["Contrato de `analysis` entre Evolução e CEO."],
        "findings": ["A cadeia não distingue retorno informativo de entrega."],
        "artifact_refs": ["evals/contrato-analysis-2026-07-31/00-ANALISE-E-OPCOES.md"],
        "evidence_refs": ["evals/contrato-analysis-2026-07-31/02-PROVA-DE-MUTACAO.md"],
        "open_questions": ["Qual contrato cede quando os dois se contradizem?"],
        "recommended_next_step": "Levar a análise ao CEO sem passar pelo gate de qualidade.",
        "blocking_pending_refs": [],
        "round": 1,
        "returned_to": "ceo-maestro",
        "returned_at": "2026-08-22T12:00:00-03:00",
    }
    cases.append(
        ("schema aceita ANALYSIS_RETURN bem formado", True,
         validate_schema(_retorno_analise, _analysis_def, schema))
    )

    # A FIACAO TEM DE SER LOAD-BEARING. O mutante M5 desta fatia removeu
    # `analysisReturn` do `oneOf` da RAIZ deixando o `$defs` intacto, e a casa
    # seguia VERDE: os casos acima validam contra o `$defs` DIRETO e nao passam
    # pela raiz. Definicao cuja alcancabilidade ninguem exige e o primeiro
    # degrau desta casa em forma de schema. Este caso valida pela RAIZ, e por
    # isso a fiacao passa a morder.
    cases.append(
        ("ANALYSIS_RETURN é alcançável pela RAIZ do schema, não só pelo $defs",
         True, validate_schema(_retorno_analise, schema, schema))
    )

    # As QUATRO travas que o ADR-019 nomeia, uma negativa cada. Sem elas o bloco
    # seria uma definição verde por não ser exercitada.
    _sem_analysis = json.loads(json.dumps(_retorno_analise))
    _sem_analysis["content_type"] = "product"
    cases.append(
        ("ANALYSIS_RETURN rejeita content_type que não é `analysis`", False,
         validate_schema(_sem_analysis, _analysis_def, schema))
    )

    _com_veredito = json.loads(json.dumps(_retorno_analise))
    _com_veredito["judge_report"] = {"verdict": "APPROVED"}
    cases.append(
        ("ANALYSIS_RETURN rejeita judge_report — análise não carrega veredito",
         False, validate_schema(_com_veredito, _analysis_def, schema))
    )

    _com_candidato = json.loads(json.dumps(_retorno_analise))
    _com_candidato["causal"]["candidate_digest"] = "sha256:" + "a" * 64
    cases.append(
        ("ANALYSIS_RETURN exige candidate_digest `n/a` — análise não tem candidato",
         False, validate_schema(_com_candidato, _analysis_def, schema))
    )

    _missao_de_produto = json.loads(json.dumps(_retorno_analise))
    _missao_de_produto["executive_mission"]["deliverable_type"] = "product"
    cases.append(
        ("ANALYSIS_RETURN exige missão que pediu `analysis` — a porta dos fundos "
         "fecha na origem", False,
         validate_schema(_missao_de_produto, _analysis_def, schema))
    )

    # --- tarefa 102: digest publicado como alegação corrente é conferível ---
    #
    # `departamento-seguranca` publicava um digest **só truncado** numa linha de
    # tabela marcada `executado: sim`, e o valor inteiro não existia no arquivo.
    # O objeto da alegação nem estava no pacote — os arquivos legados vivem fora
    # da Estrutura. Reexecutado, o número estava CERTO; o defeito era não poder
    # conferi-lo.
    #
    # A varredura é sobre os PLACARes dos pacotes REAIS, pelo critério estrutural
    # da tarefa 96: `evals/` como FILHO, nunca como ancestral.
    _erros_digest = []
    try:
        for _pac in sorted(ROOT.parent.rglob("evals/PLACAR*.md")):
            _dono = _pac.parent.parent
            if "backup-pre-canonizacao" in _pac.as_posix():
                continue
            if not ((_dono / "SKILL.md").is_file()
                    and (_dono / "CONTRATO-DE-COMPROMISSO.md").is_file()):
                continue
            if "evals" in [_q.name for _q in _dono.parents]:
                continue
            for _erro in digests_truncados_sem_original(
                    _pac.read_text(encoding="utf-8")):
                _erros_digest.append(f"{_dono.name}/{_pac.name}: {_erro}")
    except OSError as _exc6:
        _erros_digest.append(
            f"DIGESTS_NAO_AVALIADOS: um PLACAR não pôde ser lido "
            f"({_exc6.__class__.__name__}); ausência de conferência não é "
            "conformidade"
        )
    cases.append(
        ("nenhum digest é publicado truncado como alegação corrente",
         True, _erros_digest)
    )

    # --- rodada 4: o envelope da barreira, validado contra o próprio schema ---
    #
    # `validate_schema_keys` só olha o nível de cima e o `causal`. O
    # `governance_report` viajava aninhado e NUNCA era validado contra
    # `$defs/governanceReport` — foi por isso que a ausência de `pending` pôde
    # atravessar três rodadas sem nada acusar. Aqui ele passa a ser validado.
    envelope_da_barreira = valid_normal_submission["governance_report"]
    governance_def = schema["$defs"]["governanceReport"]
    cases.append(
        ("o envelope da barreira valida contra $defs/governanceReport", True,
         validate_schema(envelope_da_barreira, governance_def, schema))
    )
    cases.append(
        ("o envelope da barreira passa na leitura semântica da barreira", True,
         validate_governance_report(envelope_da_barreira, valid_normal_submission))
    )
    for _limite in ("R6", "R9", "R10", "R11"):
        _sem_limite = copy.deepcopy(envelope_da_barreira)
        _sem_limite["pending"] = [
            linha for linha in _sem_limite["pending"]
            if not linha.startswith(f"{_limite} ")
        ]
        cases.append(
            (f"envelope sem o limite {_limite} é rejeitado pelo schema", False,
             validate_schema(_sem_limite, governance_def, schema))
        )
        cases.append(
            (f"envelope sem o limite {_limite} é rejeitado na barreira", False,
             validate_governance_report(_sem_limite, valid_normal_submission))
        )
    _sem_pending = copy.deepcopy(envelope_da_barreira)
    _sem_pending.pop("pending")
    cases.append(
        ("envelope sem pending nenhum é rejeitado pelo schema", False,
         validate_schema(_sem_pending, governance_def, schema))
    )
    # --- RODADA 7, OI6-01: O ATAQUE DE PREFIXO, EXECUTADO ------------------
    #
    # `["R6 x", "R9 x", "R10 x", "R11 x"]` foi o ataque que `OI6-01` executou, e
    # ele atravessava schema E barreira: os quatro limites eram decididos por
    # prefixo aberto na MESMA função que decide sete por `const`. Os dois casos
    # abaixo são o par que faltava.
    _prefixo_aberto = copy.deepcopy(envelope_da_barreira)
    _prefixo_aberto["pending"] = ["R6 x", "R9 x", "R10 x", "R11 x"]
    cases.append(
        ("os quatro limites por prefixo com texto qualquer são rejeitados pelo schema",
         False, validate_schema(_prefixo_aberto, governance_def, schema))
    )
    cases.append(
        ("os quatro limites por prefixo com texto qualquer são rejeitados na barreira",
         False, validate_governance_report(_prefixo_aberto, valid_normal_submission))
    )
    # UM CASO POR LIMITE. Caso que viola quatro condições de uma vez continua
    # vermelho quando três são neutralizadas, e a mutação sai verde.
    for _limite_exato in ("R6", "R9", "R10", "R11"):
        _texto_trocado = copy.deepcopy(envelope_da_barreira)
        _texto_trocado["pending"] = [
            f"{_limite_exato} — respeita o prefixo e não é o texto do emissor"
            if linha.startswith(f"{_limite_exato} ")
            else linha
            for linha in _texto_trocado["pending"]
        ]
        cases.append(
            (f"{_limite_exato} que respeita o prefixo mas não é o texto é rejeitado pelo schema",
             False, validate_schema(_texto_trocado, governance_def, schema))
        )
        cases.append(
            (f"{_limite_exato} que respeita o prefixo mas não é o texto é rejeitado na barreira",
             False, validate_governance_report(_texto_trocado, valid_normal_submission))
        )

    _sem_recorte = copy.deepcopy(envelope_da_barreira)

    # A origem dos limites é `const` no schema e conferida na barreira: uma
    # segunda fonte digitada divergiria da constante do emissor em silêncio, que
    # é o defeito que a rodada 4 corrigiu no `pending` e a 5 na alegação.
    _recorte_de_outra_fonte = copy.deepcopy(envelope_da_barreira)

    # --- RODADA 5: a alegação e a origem independente, na barreira ---------
    #
    # Cada caso mata UMA condição, e os dois controles já passaram acima. Os
    # pares schema/barreira existem porque quem chama
    # `validate_governance_report` direto não passa pelo schema: exigência que
    # mora num lugar só some para metade dos consumidores.
    _sem_alegacao = copy.deepcopy(envelope_da_barreira)
    _sem_alegacao.pop("compliance_claim")
    cases.append(
        ("envelope sem compliance_claim é rejeitado pelo schema", False,
         validate_schema(_sem_alegacao, governance_def, schema))
    )
    cases.append(
        ("envelope sem compliance_claim é rejeitado na barreira", False,
         validate_governance_report(_sem_alegacao, valid_normal_submission))
    )

    _alegacao_alargada = copy.deepcopy(envelope_da_barreira)
    _alegacao_alargada["compliance_claim"]["does_not_certify"] = (
        "nenhum limite: este envelope certifica que a evidência não foi forjada"
    )
    cases.append(
        ("alegação alargada no envelope é rejeitada pelo schema", False,
         validate_schema(_alegacao_alargada, governance_def, schema))
    )
    cases.append(
        ("alegação alargada no envelope é rejeitada na barreira", False,
         validate_governance_report(_alegacao_alargada, valid_normal_submission))
    )


    _digest_copiado = copy.deepcopy(envelope_da_barreira)
    _digest_copiado["candidate_digest_source"] = "DECLARADO_NAO_CONFERIDO"
    cases.append(
        ("COMPLIANT com digest apenas declarado é rejeitado pelo schema", False,
         validate_schema(_digest_copiado, governance_def, schema))
    )
    cases.append(
        ("COMPLIANT com digest apenas declarado é rejeitado na barreira", False,
         validate_governance_report(_digest_copiado, valid_normal_submission))
    )


    cases.append(("série global de ADR é única em toda a estrutura", True, validate_adr_series(ROOT.parent)))
    cases.append(("todo pacote gerente tem validador que roda a trava global", True, validate_cobertura_de_validadores(ROOT.parent)))
    cases.append(("a recusa de digest() dispara e ninguém tem cópia privada do motor", True, validate_trava_de_digest(ROOT.parent)))
    cases.append(("nenhuma asserção é verdadeira por construção sobre valor produzido", True, validate_sem_check_tautologico(ROOT.parent)))
    cases.append(("nenhum placar de pacote declara total de cadeia como estado corrente", True, validate_placar_nao_declara_cadeia(ROOT.parent)))
    cases.append(("a contagem publicada aponta para o digest do instrumento vigente", True, validate_contagem_ligada_ao_instrumento(ROOT.parent)))
    cases.append(("as travas do modulo compartilhado nao estao neutralizadas", True, validate_travas_compartilhadas_com_efeito(ROOT.parent)))
    cases.append(("toda pendencia declarada nomeia quem responde por ela", True, validate_pendencia_tem_dono(ROOT.parent)))
    # --- TAREFA 105 ------------------------------------------------------
    cases.append(
        ("todo limite residual do envelope nomeia dono e condicao de fechamento",
         True, validate_limite_residual_tem_dono(ROOT.parent))
    )
    # UM CASO POR FORMA PROIBIDA. Caso que viola duas condições de uma vez
    # continua vermelho quando uma é neutralizada, e a mutação sai verde.
    _sem_dono_nem_condicao = copy.deepcopy(envelope_da_barreira)
    _sem_dono_nem_condicao["pending"] = list(envelope_da_barreira["pending"]) + [
        "Ressalva em AUTH: fechar o achado e reexecutar a inspecao"
    ]
    cases.append(
        ("ressalva nova sem dono e sem condicao e rejeitada na barreira",
         False, validate_governance_report(_sem_dono_nem_condicao,
                                           valid_normal_submission))
    )
    _so_dono = copy.deepcopy(envelope_da_barreira)
    _so_dono["pending"] = list(envelope_da_barreira["pending"]) + [
        "Ressalva em AUTH: fechar o achado. dono: ceo-maestro"
    ]
    cases.append(
        ("ressalva nova COM dono e SEM condicao de fechamento e rejeitada",
         False, validate_governance_report(_so_dono, valid_normal_submission))
    )
    _so_condicao = copy.deepcopy(envelope_da_barreira)
    _so_condicao["pending"] = list(envelope_da_barreira["pending"]) + [
        "Ressalva em AUTH: fecha quando: a inspecao for reexecutada"
    ]
    cases.append(
        ("ressalva nova COM condicao e SEM dono e rejeitada", False,
         validate_governance_report(_so_condicao, valid_normal_submission))
    )
    # A forma satisfeita sem ninguem nomeado: `dono:` seguido de pontuacao.
    # Foi o buraco da primeira versao da trava, pego por execucao.
    _dono_de_mentira = copy.deepcopy(envelope_da_barreira)
    _dono_de_mentira["pending"] = list(envelope_da_barreira["pending"]) + [
        "Ressalva em AUTH: x. dono: . fecha quando: reabrir a dimensao"
    ]
    cases.append(
        ("ressalva com `dono:` so de pontuacao e rejeitada", False,
         validate_governance_report(_dono_de_mentira, valid_normal_submission))
    )
    # E o par que impede a trava de virar parede: a forma COMPLETA passa.
    _ressalva_completa = copy.deepcopy(envelope_da_barreira)
    _ressalva_completa["pending"] = list(envelope_da_barreira["pending"]) + [
        "Ressalva em AUTH: o achado segue aberto."
        " dono: departamento-auditoria-responsabilidades."
        " fecha quando: a inspecao for reexecutada contra a identidade vigente"
    ]
    cases.append(
        ("ressalva nova COMPLETA passa na barreira", True,
         validate_governance_report(_ressalva_completa, valid_normal_submission))
    )
    cases.append(("a fonte normativa confere com o valor declarado em ORIGEM.md", True, validate_fonte_normativa_conferida(ROOT.parent)))
    # GUIA, passo 7: as 12 secoes do contrato de gerente. Estrutura-inteira pelo
    # mesmo motivo da serie de ADR -- em 2026-07-27 a medicao achou 8 de 15
    # conformes, e os dois nos de topo estavam entre os que faltavam.
    cases.append(("contratos de gerente na anatomia canônica", True, validate_contratos_de_gerente(ROOT.parent)))
    cases.append(
        (
            "fixtures seguem chaves do schema",
            True,
            fixture_contract_errors,
        )
    )
    cases.append(
        (
            "capacidade ausente falha fechada",
            True,
            validate_capability_gap(capability_gap()),
        )
    )
    evolution_gap = capability_gap()
    evolution_gap["required_capability"] = "departamento-evolucao-skills"
    evolution_gap["expected_path"] = (
        "ceo-maestro/departamento-evolucao-skills/SKILL.md"
    )
    evolution_gap["impact"] = (
        "A frente de evolução não pode ser autorizada nem retomada."
    )
    cases.append(
        (
            "CAPABILITY_GAP admite Evolução de Skills",
            True,
            validate_capability_gap(evolution_gap),
        )
    )
    gap_without_causal = capability_gap()
    gap_without_causal.pop("causal")
    cases.append(
        (
            "CAPABILITY_GAP exige causalidade",
            False,
            validate_capability_gap(gap_without_causal),
        )
    )
    cases.append(("missão executiva válida", True, validate_mission(mission())))

    evolution_mission = mission()
    evolution_mission["recipients"] = ["departamento-evolucao-skills"]
    evolution_mission["deliverable_type"] = "proposal"
    evolution_mission["matrix_exchange"] = {
        "allowed": False,
        "topics": [],
        "read_scope": [],
        "write_scope": [],
        "consolidation_owner": None,
    }
    cases.append(
        (
            "missão executiva admite Evolução de Skills",
            True,
            validate_mission(evolution_mission),
        )
    )

    single_mission = mission()
    single_mission["recipients"] = ["diretor-de-lentes"]
    single_mission["matrix_exchange"] = {
        "allowed": False,
        "topics": [],
        "read_scope": [],
        "write_scope": [],
        "consolidation_owner": None,
    }
    cases.append(
        (
            "missão simples inicia troca matricial negada",
            True,
            validate_mission(single_mission),
        )
    )

    bypass = mission()
    bypass["recipients"] = ["dev-senior"]
    bypass["matrix_exchange"]["allowed"] = False
    cases.append(("bypass direto ao executor", False, validate_mission(bypass)))

    # T96 — a forma da missão 46: proíbe os donos das evidências que a própria
    # barreira de saída exige. Na 46 a proibição vivia em prosa (`stop_when` e um
    # `allowed_tools` que restringia `spawn_agent` ao próprio Departamento); agora
    # ela é campo, e o impasse morre na emissão em vez de virar CAPABILITY_GAP.
    barreira_insatisfazivel = mission()
    barreira_insatisfazivel["forbidden_actors"] = [
        "departamento-juizes",
        "departamento-auditoria-responsabilidades",
    ]
    cases.append(
        (
            "missão que proíbe o dono da evidência que sua saída exige é insatisfazível",
            False,
            validate_mission(barreira_insatisfazivel),
        )
    )

    # O contrapeso, no mesmo ato: proibição LEGÍTIMA não pode ser acusada. Trava que
    # reprova o caminho certo é desligada na semana seguinte, não obedecida — e sem
    # este caso a trava passaria a proibir toda `forbidden_actors`, que é o oposto
    # do que ela existe para fazer.
    barreira_coerente = mission()
    barreira_coerente["forbidden_actors"] = ["departamento-negocios"]
    cases.append(
        (
            "missão pode proibir ator que não é dono de evidência da saída",
            True,
            validate_mission(barreira_coerente),
        )
    )

    evolution_submission = submission(normal_judge)
    evolution_submission["submitted_by"] = "departamento-evolucao-skills"
    evolution_submission["causal"]["producer"] = "departamento-evolucao-skills"
    evolution_submission["deliverable_type"] = "proposal"
    evolution_submission["executive_mission"] = copy.deepcopy(evolution_mission)
    cases.append(
        (
            "submissão executiva admite Evolução de Skills",
            True,
            validate_submission(evolution_submission),
        )
    )

    verdict_oracle = {
        6: "REPROVED",
        7: "ACEITO_USO_INTERNO",
        9: "ACEITO_USO_INTERNO",
        10: "VALIDATED",
    }
    for required_level in ("INTERNO", "PRODUCAO"):
        for score, expected_verdict in verdict_oracle.items():
            boundary_judge = judge_report([score, 10], required_level)
            boundary_errors = validate_judge_report(boundary_judge)
            add_if(
                boundary_errors,
                boundary_judge.get("verdict") != expected_verdict,
                "oráculo ADR-014: veredito da fronteira divergente",
            )
            if score == 10:
                boundary_state = "VALIDATED"
                boundary_basis = "quality_gate"
            elif required_level == "INTERNO" and score >= 7:
                boundary_state = "ACEITO_USO_INTERNO"
                boundary_basis = "quality_gate"
            else:
                boundary_state = "REWORK"
                boundary_basis = "none"
            boundary_errors.extend(
                validate_decision_packet(
                    submission(boundary_judge),
                    decision(boundary_judge, boundary_state, boundary_basis),
                )
            )
            cases.append(
                (
                    f"matriz ADR-014 nível {required_level} nota {score}",
                    True,
                    boundary_errors,
                )
            )

    # --- ADR-016: a faixa entre instâncias e o quarto veredito -------------

    undiscriminated = judge_report(
        [6, 10], "INTERNO", instances_per_lens=2, score_range=(6, 8)
    )
    cases.append(
        (
            "ADR-016: faixa 6–8 entre instâncias sai como NAO_DISCRIMINADO",
            True,
            (
                []
                if undiscriminated["verdict"] == "NAO_DISCRIMINADO"
                else [f"saiu {undiscriminated['verdict']}"]
            )
            + validate_judge_report(undiscriminated)
            + validate_schema_keys(schema, "judgeReport", undiscriminated, "JUDGE_REPORT"),
        )
    )
    cases.append(
        (
            "ADR-016: NAO_DISCRIMINADO não alcança PRODUCAO nem INTERNO",
            True,
            []
            if not level_reached("NAO_DISCRIMINADO", "PRODUCAO")
            and not level_reached("NAO_DISCRIMINADO", "INTERNO")
            else ["NAO_DISCRIMINADO alcançou um required_level"],
        )
    )

    undiscriminated_forged = copy.deepcopy(undiscriminated)
    undiscriminated_forged["verdict"] = "ACEITO_USO_INTERNO"
    cases.append(
        (
            "ADR-016: faixa que atravessa carimbada como aceite interno é rejeitada",
            False,
            validate_judge_report(undiscriminated_forged),
        )
    )

    undiscriminated_solo = copy.deepcopy(undiscriminated)
    undiscriminated_solo["instances_per_lens"] = 1
    cases.append(
        (
            "ADR-016: faixa aberta com uma única instância é rejeitada",
            False,
            validate_judge_report(undiscriminated_solo),
        )
    )

    range_forged = judge_report([10, 10], "PRODUCAO")
    range_forged["minimum_score_range"] = {"lo": 6, "hi": 10}
    cases.append(
        (
            "ADR-016: faixa que não bate com a menor nota é rejeitada",
            False,
            validate_judge_report(range_forged),
        )
    )

    judge_without_range = judge_report([10, 10], "PRODUCAO")
    judge_without_range.pop("minimum_score_range")
    cases.append(
        (
            "ADR-016: JUDGE_REPORT exige minimum_score_range",
            False,
            validate_schema_keys(
                schema, "judgeReport", judge_without_range, "JUDGE_REPORT"
            ),
        )
    )

    judge_without_rule = judge_report([10, 10], "PRODUCAO")
    judge_without_rule.pop("aggregation_rule")
    cases.append(
        (
            "ADR-016: JUDGE_REPORT exige aggregation_rule",
            False,
            validate_schema_keys(
                schema, "judgeReport", judge_without_rule, "JUDGE_REPORT"
            ),
        )
    )

    judge_unknown_method = judge_report([10, 10], "PRODUCAO")
    judge_unknown_method["aggregation_rule"]["method"] = "MEDIA"
    cases.append(
        (
            "ADR-016: JUDGE_REPORT rejeita método de agregação fora do enum",
            False,
            validate_judge_report(judge_unknown_method),
        )
    )

    undiscriminated_submission = submission(undiscriminated)
    cases.append(
        (
            "ADR-016: EXECUTIVE_SUBMISSION com NAO_DISCRIMINADO não fecha o gate",
            False,
            validate_decision_packet(
                undiscriminated_submission,
                decision(undiscriminated, "ACEITO_USO_INTERNO", "quality_gate"),
            ),
        )
    )

    mission_without_level = mission()
    mission_without_level.pop("required_level")
    cases.append(
        (
            "required_level ausente na missão",
            False,
            validate_mission(mission_without_level),
        )
    )
    judge_without_level = judge_report([10])
    judge_without_level.pop("required_level")
    cases.append(
        (
            "required_level ausente no parecer",
            False,
            validate_judge_report(judge_without_level),
        )
    )
    decision_without_level = decision(normal_judge, "VALIDATED", "quality_gate")
    decision_without_level.pop("required_level")
    cases.append(
        (
            "required_level ausente na decisão",
            False,
            validate_decision_packet(
                valid_normal_submission,
                decision_without_level,
            ),
        )
    )
    divergent_submission = submission(judge_report([9, 10], "PRODUCAO"))
    divergent_submission["executive_mission"]["required_level"] = "INTERNO"
    cases.append(
        (
            "required_level divergente missão e parecer",
            False,
            validate_submission(divergent_submission),
        )
    )
    divergent_decision = decision(normal_judge, "VALIDATED", "quality_gate")
    divergent_decision["required_level"] = "INTERNO"
    cases.append(
        (
            "required_level divergente na decisão",
            False,
            validate_decision_packet(
                valid_normal_submission,
                divergent_decision,
            ),
        )
    )
    internal_as_production = judge_report([9, 10], "PRODUCAO")
    cases.append(
        (
            "aceite interno não alcança produção",
            False,
            validate_decision_packet(
                submission(internal_as_production),
                decision(
                    internal_as_production,
                    "ACEITO_USO_INTERNO",
                    "quality_gate",
                ),
            ),
        )
    )

    cases.append(
        (
            "produção exige nota 10",
            True,
            validate_decision_packet(
                valid_normal_submission,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    rounded_judge = judge_report([9.49, 10, 10])
    rounded_submission = submission(
        rounded_judge, limitation_report(rounded_judge), None
    )
    cases.append(
        (
            "nota externa decimal é rejeitada",
            False,
            validate_decision_packet(
                rounded_submission,
                decision(rounded_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    vague_limit = copy.deepcopy(limit)
    vague_limit["attempted_remediations"] = []
    vague_limit["evidence_refs"] = []
    cases.append(
        (
            "relatório vago não prova impossibilidade",
            False,
            validate_limitation_report(vague_limit, below_judge),
        )
    )

    multi_below_judge = judge_report([8, 9, 10])
    incomplete_limit = limitation_report(multi_below_judge)
    incomplete_limit["below_cutoff_evaluations"].pop()
    cases.append(
        (
            "relatório deve cobrir todo critério abaixo do corte",
            False,
            validate_limitation_report(incomplete_limit, multi_below_judge),
        )
    )

    cases.append(
        (
            "limite verificado aguarda Jeremias",
            True,
            validate_decision_packet(
                waiting_submission,
                decision(below_judge, "AWAITING_HUMAN_EXCEPTION", "none"),
                request,
            ),
        )
    )

    wrong_request_ref = copy.deepcopy(request)
    wrong_request_ref["judge_report_ref"] = "judge-report-outro"
    cases.append(
        (
            "pedido de exceção exige refs exatas",
            False,
            validate_exception_request(wrong_request_ref, below_judge, limit),
        )
    )

    cases.append(
        (
            "exceção autorizada por Jeremias",
            True,
            validate_decision_packet(
                valid_exception_submission,
                decision(
                    below_judge,
                    "VALIDATED_BY_EXCEPTION",
                    "jeremias_exception",
                ),
                request,
            ),
        )
    )

    wrong_authority = copy.deepcopy(auth)
    wrong_authority["authorized_by"] = "departamento-negocios"
    cases.append(
        (
            "autoridade errada não aprova",
            False,
            validate_decision_packet(
                submission(below_judge, limit, wrong_authority),
                decision(
                    below_judge,
                    "VALIDATED_BY_EXCEPTION",
                    "jeremias_exception",
                ),
                request,
            ),
        )
    )

    stale_authorization = copy.deepcopy(auth)
    stale_authorization["candidate_digest"] = digest("d")
    cases.append(
        (
            "autorização obsoleta não aprova",
            False,
            validate_decision_packet(
                submission(below_judge, limit, stale_authorization),
                decision(
                    below_judge,
                    "VALIDATED_BY_EXCEPTION",
                    "jeremias_exception",
                ),
                request,
            ),
        )
    )

    critical_judge = judge_report([9, 10], critical=True)
    critical_limit = limitation_report(critical_judge)
    critical_request = exception_request(critical_judge, critical_limit)
    critical_auth = authorization(critical_request)
    cases.append(
        (
            "falha crítica força REPROVED",
            True,
            validate_judge_report(critical_judge),
        )
    )
    blocked_judge = judge_report(
        [10, 10],
        "PRODUCAO",
        blockers=["pending/security-review"],
    )
    cases.append(
        (
            "pendência bloqueante força REPROVED",
            True,
            validate_judge_report(blocked_judge),
        )
    )
    forged_critical_verdict = copy.deepcopy(critical_judge)
    forged_critical_verdict["verdict"] = "ACEITO_USO_INTERNO"
    cases.append(
        (
            "falha crítica não aceita veredito positivo",
            False,
            validate_judge_report(forged_critical_verdict),
        )
    )
    cases.append(
        (
            "gate autoafirmado não esconde falha crítica",
            False,
            validate_decision_packet(
                submission(critical_judge, critical_limit, critical_auth),
                decision(
                    critical_judge,
                    "VALIDATED_BY_EXCEPTION",
                    "jeremias_exception",
                    gates(),
                ),
                critical_request,
            ),
        )
    )

    blocked_submission = submission(normal_judge)
    blocked_submission["blocking_pending_refs"] = ["pending/security-review"]
    cases.append(
        (
            "pendência bloqueante impede validação normal",
            False,
            validate_decision_packet(
                blocked_submission,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    failed_test_submission = submission(normal_judge)
    failed_test_submission["test_summary"]["fail"] = 1
    cases.append(
        (
            "teste falho impede validação normal",
            False,
            validate_decision_packet(
                failed_test_submission,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    zero_test_submission = submission(normal_judge)
    zero_test_submission["test_summary"]["pass"] = 0
    cases.append(
        (
            "zero testes aprovados não prova conclusão",
            False,
            validate_decision_packet(
                zero_test_submission,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    unjustified_skip_submission = submission(normal_judge)
    unjustified_skip_submission["test_summary"]["skip"] = 1
    cases.append(
        (
            "SKIP sem justificativa não prova conclusão",
            False,
            validate_decision_packet(
                unjustified_skip_submission,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    out_of_scope_submission = submission(normal_judge)
    out_of_scope_submission["scope_touched"].append("Escopo não autorizado.")
    cases.append(
        (
            "escopo tocado deve caber na missão",
            False,
            validate_decision_packet(
                out_of_scope_submission,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    forged_rules_submission = submission(normal_judge)
    forged_rules_submission["governance_report"]["rules_digest"] = digest("f")
    cases.append(
        (
            "digest de regras autoafirmado é rejeitado",
            False,
            validate_decision_packet(
                forged_rules_submission,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    replayed_audit_submission = submission(normal_judge)
    replayed_audit_submission["governance_report"]["candidate_digest"] = digest("d")
    cases.append(
        (
            "auditoria de outro candidato é rejeitada",
            False,
            validate_decision_packet(
                replayed_audit_submission,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    # ADR-018 — os dois casos que a rodada 1 da tarefa 15 não conseguia separar.
    #
    # O primeiro é o achado A1 em forma de fixture: relatório COMPLIANT cuja
    # identidade nunca foi recomputada. O segundo é o mesmo envelope sem o campo,
    # que é como o produtor antigo o emitia — e é o que a barreira aceitava em
    # silêncio.
    identidade_nao_conferida = submission(normal_judge)
    identidade_nao_conferida["governance_report"]["candidate_identity_status"] = (
        "NAO_CONFERIDO"
    )
    cases.append(
        (
            "COMPLIANT com identidade do candidato não conferida é rejeitado",
            False,
            validate_decision_packet(
                identidade_nao_conferida,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    identidade_ausente = submission(normal_judge)
    identidade_ausente["governance_report"].pop("candidate_identity_status")
    cases.append(
        (
            "COMPLIANT sem declarar o estado da identidade é rejeitado",
            False,
            validate_decision_packet(
                identidade_ausente,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    noncompliant_submission = submission(normal_judge)
    noncompliant_submission["governance_report"]["verdict"] = "NONCOMPLIANT"
    noncompliant_submission["governance_report"]["violations"] = [
        "RI-04 sem evidência suficiente."
    ]
    cases.append(
        (
            "violação de regra impede validação",
            False,
            validate_decision_packet(
                noncompliant_submission,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    expired_judge = judge_report([10, 10])
    expired_judge["issued_at"] = "2026-07-25T10:00:00-03:00"
    expired_judge["expires_at"] = "2026-07-25T11:00:00-03:00"
    cases.append(
        (
            "parecer vencido não sustenta decisão",
            False,
            validate_decision_packet(
                submission(expired_judge),
                decision(expired_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    mismatched_refs = decision(normal_judge, "VALIDATED", "quality_gate")
    mismatched_refs["submission_ref"] = "submission-outra"
    mismatched_refs["judge_report_ref"] = "judge-report-outro"
    cases.append(
        (
            "referências causais divergentes são rejeitadas",
            False,
            validate_decision_packet(valid_normal_submission, mismatched_refs),
        )
    )

    mismatched_contract = copy.deepcopy(valid_normal_submission)
    mismatched_contract["judge_report"]["causal"]["contract_id"] = "contract-outro"
    cases.append(
        (
            "contrato causal divergente é rejeitado",
            False,
            validate_decision_packet(
                mismatched_contract,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    cases.append(
        (
            "retrabalho abaixo do corte não exige exceção",
            True,
            validate_decision_packet(
                submission(below_judge),
                decision(below_judge, "REWORK", "none"),
            ),
        )
    )

    forged_judge = judge_report([8, 9])
    forged_judge["minimum_score"] = 9
    forged_judge["verdict"] = "VALIDATED"
    cases.append(
        (
            "placar forjado é detectado",
            False,
            validate_judge_report(forged_judge),
        )
    )

    expired = copy.deepcopy(auth)
    expired["issued_at"] = "2026-07-25T10:00:00-03:00"
    expired["expires_at"] = "2026-07-25T12:00:00-03:00"
    # --- T111: o digest do despacho recomputa? ARVORE REAL ------------------
    _regs, _resolver = registros_de_despacho_em_disco(ROOT.parent)
    cases.append(
        (
            "T111 a arvore tem registro de despacho para medir",
            True,
            [] if _regs else ["nenhum DISPATCH_RECORD real encontrado; zero de "
                              "varredura e suspeita, nao conformidade"],
        )
    )
    cases.append(
        (
            "T111 todo digest de despacho publicado RECOMPUTA (ARVORE REAL)",
            True,
            validate_digest_de_despacho_reproduz(_regs, _resolver),
        )
    )
    _amostra_ruim = [("amostra.json", {
        "artifact_type": "DISPATCH_RECORD",
        "despachos": [{"mission_ref": "x.json", "mission_digest": "sha256:" + "0" * 64}],
    })]
    _resolver_amostra = lambda _n, _r: ROOT / "evals" / "producao-honesta-2026-08-04" / (
        "14-EXECUTIVE-MISSION-R3-POS-DECISAO-T17.json")
    cases.append(
        (
            "T111 digest que nao recomputa e acusado",
            False,
            digests_de_despacho(_amostra_ruim, _resolver_amostra)[0] and ["acusado"] or [],
        )
    )
    _amostra_sem_arquivo = [("amostra.json", {
        "artifact_type": "DISPATCH_RECORD",
        "despachos": [{"mission_ref": "nao-existe.json", "mission_digest": "sha256:" + "0" * 64}],
    })]
    cases.append(
        (
            "T111 missao que nao existe para recomputar nao e isentada",
            False,
            digests_de_despacho(_amostra_sem_arquivo, lambda _n, _r: None)[0] and ["acusado"] or [],
        )
    )
    _amostra_cru = [("amostra.json", {
        "artifact_type": "DISPATCH_RECORD",
        "despachos": [{"mission_ref": "x.json", "mission_digest": "d246dbc8" + "0" * 56}],
    })]
    cases.append(
        (
            "T111 digest sem o prefixo da receita nao e aceito como publicado",
            False,
            digests_de_despacho(_amostra_cru, _resolver_amostra)[1] and ["contado como sem digest"] or [],
        )
    )

    # --- T109: a declaracao de proibicao, medida em MISSAO REAL ------------
    _missoes_reais, _descartadas = missoes_reais_em_disco(ROOT.parent)
    _pos, _pre = missoes_sem_declaracao_de_proibicao(_missoes_reais)
    cases.append(
        (
            "T109 a arvore tem missao real para medir",
            True,
            [] if _missoes_reais else ["nenhuma EXECUTIVE_MISSION real encontrada; "
                                       "zero de varredura e suspeita, nao conformidade"],
        )
    )
    cases.append(
        (
            "T109 nenhuma missao pos-corte omite forbidden_actors (ARVORE REAL)",
            True,
            validate_declaracao_de_proibicao(_missoes_reais),
        )
    )
    # Negativos com amostra, porque hoje NAO existe missao pos-corte na arvore:
    # a limitacao fica declarada em vez de disfarcada de cobertura.
    _amostra_pos = {
        "artifact_type": "EXECUTIVE_MISSION",
        "mission_id": "AMOSTRA-T109-POS-CORTE",
        "issued_at": CORTE_DECLARACAO_DE_PROIBICAO + "T00:00:00-03:00",
    }
    cases.append(
        (
            "T109 missao pos-corte sem o campo e acusada",
            False,
            missoes_sem_declaracao_de_proibicao([_amostra_pos])[0] and ["acusada"] or [],
        )
    )
    _amostra_sem_data = {
        "artifact_type": "EXECUTIVE_MISSION",
        "mission_id": "AMOSTRA-T109-SEM-DATA",
    }
    cases.append(
        (
            "T109 missao sem data nao e isentada",
            False,
            missoes_sem_declaracao_de_proibicao([_amostra_sem_data])[0] and ["acusada"] or [],
        )
    )
    _amostra_declarada = {
        "artifact_type": "EXECUTIVE_MISSION",
        "mission_id": "AMOSTRA-T109-DECLARADA",
        "issued_at": CORTE_DECLARACAO_DE_PROIBICAO + "T00:00:00-03:00",
        "forbidden_actors": [],
    }
    cases.append(
        (
            "T109 declarar lista VAZIA satisfaz a regra",
            True,
            missoes_sem_declaracao_de_proibicao([_amostra_declarada])[0] and ["acusada"] or [],
        )
    )
    cases.append(
        (
            "T109 a divida medida bate o teto declarado (ARVORE REAL)",
            True,
            (
                []
                if len(_pre) == TETO_MISSOES_SEM_DECLARACAO
                else [
                    f"divida medida {len(_pre)} contra teto "
                    f"{TETO_MISSOES_SEM_DECLARACAO}; {_descartadas} descartadas por "
                    "nao serem emissao real"
                ]
            ),
        )
    )

    cases.append(
        (
            "autorização expirada não aprova",
            False,
            validate_decision_packet(
                submission(below_judge, limit, expired),
                decision(
                    below_judge,
                    "VALIDATED_BY_EXCEPTION",
                    "jeremias_exception",
                ),
                request,
            ),
        )
    )

    expired_request = copy.deepcopy(request)
    expired_request["issued_at"] = "2026-07-25T10:00:00-03:00"
    expired_request["expires_at"] = "2026-07-25T12:00:00-03:00"
    cases.append(
        (
            "pedido de exceção vencido não autoriza",
            False,
            validate_decision_packet(
                valid_exception_submission,
                decision(
                    below_judge,
                    "VALIDATED_BY_EXCEPTION",
                    "jeremias_exception",
                ),
                expired_request,
            ),
        )
    )

    failures = 0
    for name, expected_valid, errors in cases:
        actual_valid = not errors
        passed = actual_valid == expected_valid
        marker = "PASS" if passed else "FAIL"
        expectation = "válido" if expected_valid else "rejeitado"
        print(f"[{marker}] {name} — esperado {expectation}")
        if not passed:
            failures += 1
            if errors:
                for error in errors:
                    print(f"       {error}")
            else:
                print("       caso inválido foi aceito sem erro")
    print(f"\nResultado: {len(cases) - failures}/{len(cases)} casos passaram.")
    return 1 if failures else 0


if __name__ == "__main__":
    # T55: recusa medir a Estrutura a partir do runtime, onde a raiz
    # resolve para .claude/skills e as skills do Catalogo viram pacotes.
    recusar_execucao_fora_da_fonte(ROOT.parent)
    sys.exit(run())
