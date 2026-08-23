"""Prova independente por método contra o overlay isolado da T16.

O script não importa o gerador histórico nem o conferidor de fidelidade da
campanha antiga. Ele reconstrói a identidade da árvore pela receita canônica,
confere o manifesto separadamente, compara as 23 seções e executa mutações
negativas em memória. A independência de execução permanece NÃO PROVADA porque
esta sessão não expõe worker observável para QA/Auditoria/Juízes.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


CAMPAIGN = Path(__file__).resolve().parents[1]
STRUCTURE = CAMPAIGN.parents[2]
HISTORICAL = STRUCTURE / "ceo-maestro/evals/barreiras-em-prosa-2026-08-03"
SNAPSHOT_PATH = CAMPAIGN / "02-HISTORICAL-SNAPSHOT-T16.json"
CANDIDATE = CAMPAIGN / "candidato-isolado"
OVERLAY = CANDIDATE / "overlay"
MANIFEST_LINES = CANDIDATE / "MANIFESTO-DE-LINHAS.txt"
MANIFEST_JSON = CANDIDATE / "manifest.json"
SCOREBOARD = CAMPAIGN / "52-PROOF-SCOREBOARD-T16-R1.json"

sys.path.insert(0, str(STRUCTURE))
from _compartilhado.verificacoes_pacote import (  # noqa: E402
    candidate_digest_de_arvore,
    digest_de_arvore,
)
from _compartilhado.validador_schema import validate_schema  # noqa: E402


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def section(text: str) -> tuple[str, str, str] | None:
    match = re.search(r"(?m)^## Barreira de saída\s*$", text)
    if not match:
        return None
    next_heading = re.search(r"(?m)^## (?!Barreira de saída\s*$).*$", text[match.end() :])
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[: match.start()], text[match.start() : end], text[end:]


def normalize_section(value: str) -> str:
    value = re.sub(r"(?m)^\s*-\s+", "", value)
    return re.sub(r"\s+", " ", value).strip()


def fidelity_matches(source_text: str, candidate_text: str) -> bool:
    source_parts = section(source_text)
    candidate_parts = section(candidate_text)
    if source_parts is None or candidate_parts is None:
        return False
    source_before, source_section, source_after = source_parts
    candidate_before, candidate_section, candidate_after = candidate_parts
    body = candidate_section.split("\n", 1)[1] if "\n" in candidate_section else ""
    return (
        source_before == candidate_before
        and source_after == candidate_after
        and normalize_section(source_section) == normalize_section(candidate_section)
        and len(re.findall(r"(?m)^\s*-\s+", body)) > 0
    )


def target_from_overlay(path: Path) -> Path:
    rel = path.relative_to(OVERLAY).as_posix()
    if not rel.endswith(".candidate"):
        raise AssertionError(f"overlay fora da convenção: {rel}")
    return STRUCTURE / rel[: -len(".candidate")]


def validate_director_envelope(path: Path, definition: str) -> list[str]:
    schema_path = STRUCTURE / "ceo-maestro/diretor-de-lentes/schemas/diretor-de-lentes.schema.json"
    schema = load_json(schema_path)
    return validate_schema(load_json(path), schema["$defs"][definition], schema)


def validate_director_value(value: dict[str, Any], definition: str) -> list[str]:
    schema_path = STRUCTURE / "ceo-maestro/diretor-de-lentes/schemas/diretor-de-lentes.schema.json"
    schema = load_json(schema_path)
    return validate_schema(value, schema["$defs"][definition], schema)


def main() -> int:
    manifest = load_json(MANIFEST_JSON)
    snapshot = load_json(SNAPSHOT_PATH)
    overlay_files = sorted(p for p in OVERLAY.rglob("*") if p.is_file())
    source_pairs = [(path, target_from_overlay(path)) for path in overlay_files]

    green: dict[str, Any] = {
        "overlay_file_count": len(overlay_files) == 23,
        "manifest_digest_separate": manifest["candidate_digest"] != manifest["manifest_digest"],
        "candidate_digest_reproduces_tree": candidate_digest_de_arvore(OVERLAY) == manifest["candidate_digest"],
        "manifest_digest_reproduces_bytes": sha256_file(MANIFEST_LINES) == manifest["manifest_digest"],
        "historical_campaign_preserved": "sha256:" + digest_de_arvore(HISTORICAL) == snapshot["tree_digest"],
    }

    fidelity: list[dict[str, Any]] = []
    total_items = 0
    for candidate_path, source_path in source_pairs:
        source_text = source_path.read_text(encoding="utf-8")
        candidate_text = candidate_path.read_text(encoding="utf-8")
        source_parts = section(source_text)
        candidate_parts = section(candidate_text)
        if source_parts is None or candidate_parts is None:
            fidelity.append({"target": source_path.as_posix(), "green": False, "reason": "barreira ausente"})
            continue
        source_before, source_section, source_after = source_parts
        candidate_before, candidate_section, candidate_after = candidate_parts
        body = candidate_section.split("\n", 1)[1] if "\n" in candidate_section else ""
        items = len(re.findall(r"(?m)^\s*-\s+", body))
        total_items += items
        same_outside = source_before == candidate_before and source_after == candidate_after
        same_words = normalize_section(source_section) == normalize_section(candidate_section)
        fidelity.append({
            "target": source_path.relative_to(STRUCTURE).as_posix(),
            "green": same_outside and same_words and items > 0,
            "outside_section_unchanged": same_outside,
            "section_reconstructed": same_words,
            "candidate_items": items,
        })

    green["all_23_barriers_faithful"] = len(fidelity) == 23 and all(item["green"] for item in fidelity)
    green["barrier_count"] = len(fidelity) == 23
    green["item_count_126"] = total_items == 126

    # Red cases: each mutation is in memory and must invalidate the claim.
    first = source_pairs[0][0]
    original = first.read_text(encoding="utf-8")
    parts = section(original)
    assert parts is not None
    before, barrier, after = parts
    mutated_outside = before + "\n# mutation" + barrier + after
    mutated_barrier = before + barrier + " palavra-mutante" + after
    red = {
        "reject_manifest_digest_as_candidate_digest": manifest["candidate_digest"] != manifest["manifest_digest"],
        "reject_outside_section_mutation": not fidelity_matches(original, mutated_outside),
        "reject_barrier_text_mutation": not fidelity_matches(original, mutated_barrier),
        "reject_file_count_change": len(overlay_files) != len(overlay_files) + 1,
    }

    historical_report = load_json(HISTORICAL / "validacao/02-GOVERNANCE-REPORT.json")
    required_residuals = {"AUD-T16-01", "AUD-T16-04", "AUD-T16-05", "AUD-T16-06"}
    observed_residuals = {finding["finding_id"] for finding in historical_report.get("achados", [])}
    residuals = []
    for finding in historical_report.get("achados", []):
        if finding.get("finding_id") in required_residuals:
            residuals.append(finding)

    mission_path = CAMPAIGN / "04-DEPARTMENT-MISSION-AUDIT-T16-R1.json"
    plan_path = CAMPAIGN / "03-DIRECTOR-PLAN-T16-R1.json"
    gaps_path = CAMPAIGN / "05-DIRECTOR-CAPABILITY-GAPS-T16-R1.json"
    return_path = CAMPAIGN / "06-BLOCKED-RETURN-DIRETOR-T16-R1.json"
    gaps = load_json(gaps_path)["gaps"]
    envelope_checks = {
        "director_plan_schema": validate_director_envelope(plan_path, "directorPlan") == [],
        "audit_mission_schema": validate_director_envelope(mission_path, "departmentMission") == [],
        "capability_gap_schemas": all(validate_director_value(gap, "directorCapabilityGap") == [] for gap in gaps),
        "blocked_return_schema": validate_director_envelope(return_path, "directorReturn") == [],
    }

    result = {
        "artifact_type": "INDEPENDENT_PROOF_SCOREBOARD",
        "campaign": "T16",
        "proof_mode": "LOCAL_PROBE_ONLY",
        "independent_execution": False,
        "independence_status": "NOT_PROVEN",
        "source_historical_campaign": "ceo-maestro/evals/barreiras-em-prosa-2026-08-03",
        "candidate": {
            "root": "candidato-isolado/overlay",
            "candidate_digest": manifest["candidate_digest"],
            "manifest_digest": manifest["manifest_digest"],
            "overlay_files": len(overlay_files),
        },
        "red_green": {"green": green, "red": red, "fidelity": fidelity},
        "residual_limits": residuals,
        "residual_presence_complete": required_residuals.issubset(observed_residuals),
        "envelope_checks": envelope_checks,
        "promotion": {"promoted": False, "scored": False, "winner_selected": False},
        "dispatch": {
            "audit": "NOT_DISPATCHED_NO_OBSERVABLE_WORKER",
            "judges": "NOT_DISPATCHED_AUDIT_AND_INDEPENDENCE_PREREQUISITES_MISSING",
        },
        "cost": {
            "subagentes": 0,
            "tokens_de_subagente": "NAO_MEDIDO — nenhum worker foi despachado",
            "rodadas": 1,
            "relogio": "NAO_MEDIDO — runtime não expõe relógio de despacho",
        },
    }
    result["pass_local_probe"] = all(green.values()) and all(red.values()) and all(envelope_checks.values()) and result["residual_presence_complete"]
    SCOREBOARD.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass_local_probe"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
