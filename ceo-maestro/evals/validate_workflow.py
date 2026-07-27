#!/usr/bin/env python3
"""Validador determinístico e autocontido dos invariantes do CEO Maestro."""

from __future__ import annotations

import copy
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "ceo-maestro.schema.json"
EVALS_PATH = ROOT / "evals" / "evals.json"
RULES_PATH = ROOT.parent / "regras-de-ouro" / "REGRAS-DE-OURO.md"

sys.path.insert(0, str(ROOT.parent))
try:
    from _compartilhado.validador_schema import digest, sha256_file  # noqa: E402
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_adr_series,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print(
        "[FAIL] motor compartilhado ausente em "
        f"{ROOT.parent}/_compartilhado: {exc}"
    )
    raise SystemExit(1)
CUTOFF = 9.5
DIRECT_EXECUTIVES = {"diretor-de-lentes", "departamento-negocios"}
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


def applicable_minimum(report: dict[str, Any], errors: list[str]) -> float | None:
    scorecard = required_list(report, "scorecard", errors)
    scores: list[float] = []
    for index, item in enumerate(scorecard):
        if not isinstance(item, dict):
            errors.append(f"scorecard[{index}]: objeto obrigatório")
            continue
        if item.get("applicable") is True:
            score = item.get("score")
            if not isinstance(score, (int, float)) or isinstance(score, bool):
                errors.append(f"scorecard[{index}].score: número obrigatório")
            elif not 0 <= float(score) <= 10:
                errors.append(f"scorecard[{index}].score: fora de 0..10")
            else:
                scores.append(float(score))
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
    calculated = applicable_minimum(report, errors)
    declared = report.get("minimum_score")
    if calculated is not None:
        add_if(
            errors,
            not isinstance(declared, (int, float))
            or isinstance(declared, bool)
            or not math.isclose(float(declared), calculated, abs_tol=1e-12),
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
    eligible = (
        calculated is not None
        and calculated >= CUTOFF
        and critical is False
        and blockers == []
    )
    add_if(
        errors,
        verdict != ("VALIDATED" if eligible else "REPROVED"),
        "judge_report.verdict: incompatível com menor nota, falha crítica ou bloqueios",
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
    add_if(
        errors,
        not isinstance(current, (int, float))
        or isinstance(current, bool)
        or not 0 <= float(current) < CUTOFF,
        "limitation_report.current_minimum_score: deve ser menor que 9,5",
    )
    add_if(
        errors,
        not isinstance(best, (int, float))
        or isinstance(best, bool)
        or not 0 <= float(best) < CUTOFF,
        "limitation_report.best_attainable_score: deve ser menor que 9,5",
    )
    if isinstance(current, (int, float)) and isinstance(best, (int, float)):
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
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not 0 <= float(score) < CUTOFF,
            f"below_cutoff_evaluations[{index}].score: deve ser menor que 9,5",
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
            and isinstance(item.get("score"), (int, float))
            and item.get("score") < CUTOFF
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
        request.get("cutoff_score") != CUTOFF,
        "exception_request.cutoff_score: deve ser 9,5",
    )
    add_if(
        errors,
        request.get("actual_minimum_score") != judge_report.get("minimum_score"),
        "exception_request: nota diverge do JUDGE_REPORT",
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
        "mission: CEO tentou chamar capacidade fora de Diretor/Negócios",
    )
    add_if(
        errors,
        mission.get("return_to") != "ceo-maestro",
        "mission.return_to: inválido",
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
    return errors


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
    required_list(report, "evidence_refs", errors)
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
        "submission: autor não é Diretor nem Negócios",
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
        add_if(
            errors,
            submission.get("candidate_digest") != judge.get("candidate_digest"),
            "submission: candidato diverge do JUDGE_REPORT",
        )
        minimum = judge.get("minimum_score")
        if isinstance(minimum, (int, float)) and minimum < CUTOFF:
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
    if state == "VALIDATED":
        add_if(
            errors,
            not isinstance(minimum, (int, float)) or minimum < CUTOFF,
            "decision: VALIDATED exige nota mínima 9,5",
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
    elif state == "AWAITING_HUMAN_EXCEPTION":
        add_if(
            errors,
            not isinstance(minimum, (int, float)) or minimum >= CUTOFF,
            "decision: espera de exceção exige nota abaixo de 9,5",
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
            not isinstance(minimum, (int, float)) or minimum >= CUTOFF,
            "decision: exceção deve preservar nota real abaixo de 9,5",
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
        "created_at": "2026-07-26T11:00:00-03:00",
    }


def score_item(identifier: str, score: float) -> dict[str, Any]:
    return {
        "criterion_id": identifier,
        "applicable": True,
        "score": score,
        "evidence_refs": [f"evidence/{identifier}.json"],
    }


def judge_report(
    scores: list[float], critical: bool = False, blockers: list[str] | None = None
) -> dict[str, Any]:
    blockers = [] if blockers is None else blockers
    minimum = min(scores)
    eligible = minimum >= CUTOFF and not critical and not blockers
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
        "verdict": "VALIDATED" if eligible else "REPROVED",
        "critical_fail": critical,
        "blocking_pending_refs": blockers,
        "evidence_refs": ["evidence/judges.json"],
        "issued_at": "2026-07-26T12:00:00-03:00",
        "expires_at": "2026-07-27T12:00:00-03:00",
    }


def limitation_report(judge: dict[str, Any]) -> dict[str, Any]:
    minimum = judge["minimum_score"]
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
        "best_attainable_score": 9.4,
        "below_cutoff_evaluations": [
            item for item in judge["scorecard"] if item["score"] < CUTOFF
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
        "cutoff_score": CUTOFF,
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
        "executive_mission": mission(),
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
            "violations": [],
            "evidence_refs": ["evidence/rules-audit.json"],
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


def mission() -> dict[str, Any]:
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
        "scope_in": ["Produto, viabilidade e implementação."],
        "scope_out": [],
        "constraints": [],
        "decisions_binding": [],
        "dependencies": [],
        "acceptance_criteria": ["Menor nota aplicável maior ou igual a 9,5."],
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

    normal_judge = judge_report([9.5, 9.7, 10.0])
    below_judge = judge_report([9.3, 10.0, 10.0])
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
    cases.append(("schema e refs locais", True, schema_errors))
    cases.append(("série global de ADR é única em toda a estrutura", True, validate_adr_series(ROOT.parent)))
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

    cases.append(
        (
            "corte exato 9,5",
            True,
            validate_decision_packet(
                valid_normal_submission,
                decision(normal_judge, "VALIDATED", "quality_gate"),
            ),
        )
    )

    rounded_judge = judge_report([9.49, 10.0, 10.0])
    rounded_submission = submission(
        rounded_judge, limitation_report(rounded_judge), None
    )
    cases.append(
        (
            "9,49 não arredonda",
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

    multi_below_judge = judge_report([9.2, 9.3, 10.0])
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

    critical_judge = judge_report([9.3, 10.0], critical=True)
    critical_limit = limitation_report(critical_judge)
    critical_request = exception_request(critical_judge, critical_limit)
    critical_auth = authorization(critical_request)
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

    expired_judge = judge_report([9.5, 9.8])
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

    forged_judge = judge_report([9.2, 9.8])
    forged_judge["minimum_score"] = 9.8
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
    sys.exit(run())
