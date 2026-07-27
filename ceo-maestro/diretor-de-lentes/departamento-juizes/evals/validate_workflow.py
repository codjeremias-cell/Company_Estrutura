"""Validador determinístico do Departamento de Juízes.

Verifica o pacote (arquivos, metadata, links), o schema interno, os artefatos
internos e — como regressão de fronteira — que os envelopes produzidos pelo
Departamento são aceitos pelos schemas do `diretor-de-lentes` e do `ceo-maestro`.

Uso: python validate_workflow.py
"""

from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = PACKAGE_ROOT / "SKILL.md"
CONTRACT_PATH = PACKAGE_ROOT / "CONTRATO-DE-COMPROMISSO.md"
OPENAI_PATH = PACKAGE_ROOT / "agents" / "openai.yaml"
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-juizes.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
AGENTS_ROOT = PACKAGE_ROOT / "agentes"

DIRECTOR_ROOT = PACKAGE_ROOT.parent
CEO_ROOT = DIRECTOR_ROOT.parent
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(CEO_ROOT.parent))
).resolve()
DIRECTOR_SCHEMA_PATH = DIRECTOR_ROOT / "schemas" / "diretor-de-lentes.schema.json"
CEO_SCHEMA_PATH = CEO_ROOT / "schemas" / "ceo-maestro.schema.json"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"

AGENT_NAMES = [
    "agente-julgar-fidelidade-e-contrato",
    "agente-julgar-robustez-e-evidencia",
    "agente-julgar-experiencia-e-risco",
]
AGENT_LENS = {
    "agente-julgar-fidelidade-e-contrato": "fidelidade-e-contrato",
    "agente-julgar-robustez-e-evidencia": "robustez-e-evidencia",
    "agente-julgar-experiencia-e-risco": "experiencia-e-risco",
}
RULES_LINK_DEPARTMENT = "../../../regras-de-ouro/REGRAS-DE-OURO.md"
RULES_LINK_AGENT = "../../../../../regras-de-ouro/REGRAS-DE-OURO.md"

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        digest,
        find_const,
        json_pointer,
        sha256_file,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_adr_series,
        validate_agents_folder,
        validate_frontmatter,
        validate_links,
        validate_openai_yaml,
        validate_required_files,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print(
        "[FAIL] motor compartilhado ausente em "
        f"{STRUCTURE_ROOT}/_compartilhado: {exc}"
    )
    raise SystemExit(1)




# --------------------------------------------------------------------------
# Fixtures do Departamento
# --------------------------------------------------------------------------

CANDIDATE = digest("a")
CONTRACT = digest("0")
PRODUCER = digest("1")

CRITERIA = [
    ("criterio-01", "fidelidade-e-contrato", "O DONE declarado está coberto item a item."),
    ("criterio-02", "fidelidade-e-contrato", "Nenhum requisito foi descartado em silêncio."),
    ("criterio-03", "robustez-e-evidencia", "Toda alegação resolve em prova executada."),
    ("criterio-04", "experiencia-e-risco", "A falha é barulhenta e localizada para quem opera."),
]
SECONDARY = {"criterio-04": "robustez-e-evidencia"}


def causal(candidate: str = CANDIDATE, round_number: int = 1) -> dict[str, Any]:
    return {
        "work_item_id": "work-001",
        "front_id": "front-technical",
        "handoff_id": "handoff-001",
        "message_id": "message-juizes-001",
        "causation_message_ids": ["message-diretor-001"],
        "contract_id": "contract-001",
        "contract_version": 1,
        "contract_digest": CONTRACT,
        "candidate_digest": candidate,
        "round": 1 if round_number < 1 else round_number,
        "attempt": 1,
        "producer": "departamento-juizes",
        "producer_version": "1.0.0",
        "producer_digest": PRODUCER,
        "created_at": "2026-07-26T18:00:00-03:00",
    }


def contract_excerpt() -> dict[str, Any]:
    return {
        "intent": "Entregar o comportamento autorizado pelo contrato técnico.",
        "done": ["Testes aplicáveis executados sem falha."],
        "scope_in": ["Implementação do comportamento autorizado."],
        "scope_out": ["Alteração de esquema de dados."],
        "constraints": ["Sem dependência nova sem ADR."],
        "decisions": ["ADR-014 persistência relacional: aceita"],
        "not_applicable": [],
    }


def criteria_matrix(uncovered: list[str] | None = None) -> dict[str, Any]:
    return {
        "artifact_type": "CRITERIA_MATRIX",
        "criteria_matrix_id": "criteria-matrix-001",
        "causal": causal(),
        "judgment_request_ref": "judgment-request-001",
        "mode": "VALIDACAO",
        "items": [
            {
                "criterion_id": criterion_id,
                "criterion_text": text,
                "owner_lens": lens,
                "owner_reason": f"O texto literal do critério mede {lens}.",
                "secondary_lens": SECONDARY.get(criterion_id, "n/a"),
            }
            for criterion_id, lens, text in CRITERIA
        ],
        "uncovered": uncovered or [],
        "created_at": "2026-07-26T18:05:00-03:00",
    }


def assignment_criteria(judge: str) -> list[dict[str, Any]]:
    lens = AGENT_LENS[judge]
    items = [
        {"criterion_id": cid, "criterion_text": text, "role": "owner"}
        for cid, owner, text in CRITERIA
        if owner == lens
    ]
    items += [
        {"criterion_id": cid, "criterion_text": text, "role": "secondary"}
        for cid, _owner, text in CRITERIA
        if SECONDARY.get(cid) == lens
    ]
    return items


def judge_assignment(judge: str = "agente-julgar-fidelidade-e-contrato") -> dict[str, Any]:
    return {
        "artifact_type": "JUDGE_ASSIGNMENT",
        "assignment_id": f"assignment-{judge}",
        "causal": causal(),
        "judge_id": judge,
        "lens": AGENT_LENS[judge],
        "mode": "VALIDACAO",
        "candidate_digest": CANDIDATE,
        "anonymized_candidate": f"julgamento/assignment-{judge}/candidato.zip",
        "criteria": assignment_criteria(judge),
        "rubric_ref": "rubrica-corte-v1",
        "contract_excerpt": contract_excerpt(),
        "evidence_index": ["evidence/test-report.json"],
        "forbidden_context": [
            "autoria e departamento produtor",
            "pareceres dos outros agentes",
            "nota desejada, veredito esperado ou preferência da gerente",
            "rodada anterior e histórico de retrabalho",
        ],
        "return_to": "departamento-juizes",
        "issued_at": "2026-07-26T18:10:00-03:00",
    }


def judge_opinion(
    judge: str = "agente-julgar-fidelidade-e-contrato",
    scores: dict[str, Any] | None = None,
    critical: bool = False,
    status: str = "COMPLETED",
) -> dict[str, Any]:
    lens = AGENT_LENS[judge]
    default = {item["criterion_id"]: 10 for item in assignment_criteria(judge)}
    values = default if scores is None else scores
    opinion: dict[str, Any] = {
        "artifact_type": "JUDGE_OPINION",
        "assignment_id": f"assignment-{judge}",
        "judge_id": judge,
        "lens": lens,
        "candidate_digest": CANDIDATE,
        "contract_digest": CONTRACT,
        "scores": [
            {
                "criterion_id": criterion_id,
                "score": score,
                "banda": banda_for(score),
                "razao": f"Observado no artefato para {criterion_id}.",
                "evidence_ref": f"evidence-{criterion_id}",
                "artifact_ref": f"evidence/{criterion_id}.json",
            }
            for criterion_id, score in values.items()
        ],
        "critical_findings": (
            [
                {
                    "criterion_id": "criterio-03",
                    "tipo": "seguranca",
                    "descricao": "Falha explorável observada na rota autenticada.",
                    "evidence_ref": "evidence-critico",
                    "artifact_ref": "evidence/security-finding.json",
                }
            ]
            if critical
            else []
        ),
        "required_changes": [],
        "confidence": "alta",
        "status": status,
        "return_to": "departamento-juizes",
        "issued_at": "2026-07-26T18:30:00-03:00",
    }
    below = [c for c, s in values.items() if isinstance(s, int) and s < 10]
    if below or critical:
        opinion["required_changes"] = [
            f"Corrigir o defeito observado em {criterion_id}." for criterion_id in below
        ] or ["Corrigir a falha crítica observada."]
    if status == "BLOCKED":
        opinion["scores"] = []
        opinion["abstencao"] = {"motivo": "Evidência ausente para a ótica atribuída."}
    return opinion


def banda_for(score: Any) -> str:
    if isinstance(score, str):
        return "n/a"
    if score <= 3:
        return "quebrado"
    if score <= 6:
        return "cru"
    if score <= 8:
        return "polido"
    return "excelente"


def capability_gap(judge: str = "agente-julgar-experiencia-e-risco") -> dict[str, Any]:
    return {
        "artifact_type": "JUDGE_CAPABILITY_GAP",
        "capability": "Risco ao operador sem ótica de experiência nesta rodada.",
        "judge_id": judge,
        "criterion_ids": ["criterio-04"],
        "expected_contract": "Ótica de experiência e risco pontuando o criterio-04 com evidência.",
        "discovery_evidence": "SEM_RETORNO observado na atribuição assignment-experiencia.",
        "impact": "O criterio-04 fica sem nota e o veredito não pode ser VALIDATED.",
        "status": "OPEN",
        "owner": "diretor-de-lentes",
    }


def scorecard_lines(scores: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    lines = []
    for criterion_id, per_judge in scores.items():
        for judge, score in per_judge.items():
            lens = AGENT_LENS[judge]
            role = "secondary" if SECONDARY.get(criterion_id) == lens else "owner"
            lines.append(
                {
                    "criterion_id": criterion_id,
                    "judge_id": judge,
                    "lens": lens,
                    "role": role,
                    "score": score,
                    "razao": f"Observado no artefato para {criterion_id}.",
                    "evidence_ref": f"evidence-{criterion_id}-{lens}",
                    "artifact_ref": f"evidence/{criterion_id}.json",
                }
            )
    return lines


def default_scores() -> dict[str, dict[str, Any]]:
    return {
        "criterio-01": {"agente-julgar-fidelidade-e-contrato": 10},
        "criterio-02": {"agente-julgar-fidelidade-e-contrato": 10},
        "criterio-03": {"agente-julgar-robustez-e-evidencia": 10},
        "criterio-04": {
            "agente-julgar-experiencia-e-risco": 10,
            "agente-julgar-robustez-e-evidencia": 10,
        },
    }


def aggregate(scorecard: list[dict[str, Any]]) -> dict[str, Any]:
    """Nota do critério = MENOR nota entre os avaliadores. Nunca a média."""
    per_criterion: dict[str, list[Any]] = {}
    for line in scorecard:
        per_criterion.setdefault(line["criterion_id"], []).append(line["score"])
    result: dict[str, Any] = {}
    for criterion_id, values in per_criterion.items():
        numeric = [v for v in values if not isinstance(v, str)]
        result[criterion_id] = min(numeric) if numeric else "n/a"
    return result


def computed_minimum(scorecard: list[dict[str, Any]]) -> Any:
    numeric = [v for v in aggregate(scorecard).values() if not isinstance(v, str)]
    return min(numeric) if numeric else "n/a"


def panel_record(
    scores: dict[str, dict[str, Any]] | None = None,
    verdict: str = "VALIDATED",
    critical_fail: bool = False,
    gaps: list[dict[str, Any]] | None = None,
    uncovered: list[str] | None = None,
    with_assignments: bool = True,
) -> dict[str, Any]:
    values = default_scores() if scores is None else scores
    card = scorecard_lines(values)
    judges = sorted({line["judge_id"] for line in card})
    reproved = verdict != "VALIDATED"
    return {
        "artifact_type": "PANEL_RECORD",
        "panel_record_id": "panel-record-001",
        "causal": causal(),
        "judgment_request_ref": "judgment-request-001",
        "mode": "VALIDACAO",
        "criteria_matrix": criteria_matrix(uncovered),
        "assignments": (
            [
                {
                    "assignment_id": f"assignment-{judge}",
                    "judge_id": judge,
                    "lens": AGENT_LENS[judge],
                    "issued_at": "2026-07-26T18:10:00-03:00",
                    "destination": f"julgamento/assignment-{judge}/",
                }
                for judge in judges
            ]
            if with_assignments
            else []
        ),
        "panel": [
            {
                "judge_id": judge,
                "lens": AGENT_LENS[judge],
                "status": "COMPLETED",
                "confidence": "alta",
                "substrate": "desconhecido",
                "tier": "desconhecido",
            }
            for judge in judges
        ],
        "scorecard": card,
        "minimum_score": computed_minimum(card),
        "verdict": verdict,
        "critical_fail": critical_fail,
        "blocking_pending_refs": [],
        "criticisms": (
            ["O criterio-04 ficou abaixo do corte pela ótica de experiência."]
            if reproved
            else []
        ),
        "required_changes": (
            ["Tornar a falha observável para quem opera, no criterio-04."]
            if reproved
            else []
        ),
        "capability_gaps": gaps or [],
        "evidence_refs": ["evidence/test-report.json"],
        "rubric_ref": "rubrica-corte-v1",
        "pending": [
            "R6 — a existência do painel não é verificável pelo runtime; registro de emissão anexado."
        ],
        "return_to": "diretor-de-lentes",
        "recorded_at": "2026-07-26T19:00:00-03:00",
    }


def panel_handoff(
    decision_mode: str = "CONSENSO_UNANIME",
    leadership_reason: str = "n/a",
    status: str = "COMPLETED",
) -> dict[str, Any]:
    return {
        "artifact_type": "PANEL_HANDOFF",
        "panel_handoff_id": "panel-handoff-001",
        "causal": causal(),
        "judgment_request_ref": "judgment-request-002",
        "resumo": {
            "recomendacao": "O painel recomenda manter o campeão vigente.",
            "razao_mais_forte": "A prova de borda do campeão resolve; a do desafiante não abre.",
            "divergencia": "nenhuma",
            "enxertos": "nenhum",
        },
        "rubric_ref": "rubrica-corte-v1",
        "status": status,
        "decision_mode": decision_mode,
        "leadership_reason": leadership_reason,
        "winner": "candidato-campeao",
        "champion_kept": True,
        "panel": [
            {
                "judge_id": judge,
                "lens": AGENT_LENS[judge],
                "status": "COMPLETED",
                "confidence": "alta",
                "substrate": "desconhecido",
                "tier": "desconhecido",
            }
            for judge in AGENT_NAMES
        ],
        "score_matrix": [
            {
                "judge_id": judge,
                "label": label,
                "candidate_ref": candidate,
                "criterion_id": "criterio-01",
                "score": score,
            }
            for judge in AGENT_NAMES
            for label, candidate, score in [
                ("A", "candidato-campeao", 9),
                ("B", "candidato-desafiante", 7),
            ]
        ],
        "divergences": [],
        "enxertos": [],
        "evidence_refs": ["evidence/test-report.json"],
        "label_map_ref": "auditoria/label-map-001.json",
        "capability_gaps": [],
        "valid_opinions": 3,
        "pending": [
            "R6 — a existência do painel não é verificável pelo runtime; registro de emissão anexado."
        ],
        "recommended_next_step": "O Diretor decide se mantém o campeão ou reabre a disputa.",
        "return_to": "diretor-de-lentes",
        "issued_at": "2026-07-26T19:10:00-03:00",
    }


def independent_verification(verdict: str = "VERIFIED_IMPOSSIBILITY") -> dict[str, Any]:
    verified = verdict == "VERIFIED_IMPOSSIBILITY"
    return {
        "artifact_type": "INDEPENDENT_VERIFICATION",
        "verification_id": "verification-001",
        "causal": causal(),
        "limitation_report_ref": "limitation-report-001",
        "candidate_digest": CANDIDATE,
        "score_snapshot_digest": digest("b"),
        "checks": {
            "correlation_verified": True,
            "all_below_cutoff_criteria_covered": verified,
            "attempts_executed": True,
            "alternatives_discarded": True,
            "best_attainable_consistent": True,
            "nonwaivable_gates_intact": True,
        },
        "verdict": verdict,
        "independence_confirmed": True,
        "all_below_cutoff_criteria_covered": verified,
        "evidence_refs": ["evidence/limitation-evidence.json"],
        "dissent_refs": [],
        "return_to": "diretor-de-lentes",
        "issued_at": "2026-07-26T19:20:00-03:00",
    }


# --------------------------------------------------------------------------
# Derivação para os envelopes de fronteira
# --------------------------------------------------------------------------

def derive_department_judge_report(record: dict[str, Any]) -> dict[str, Any]:
    """Converte o PANEL_RECORD interno no envelope que o Diretor consome."""
    scores = aggregate(record["scorecard"])
    return {
        "artifact_type": "DEPARTMENT_JUDGE_REPORT",
        "report_id": "department-judge-report-001",
        "causal": copy.deepcopy(record["causal"]),
        "judgment_request_ref": record["judgment_request_ref"],
        "candidate_digest": record["causal"]["candidate_digest"],
        "contract_digest": record["causal"]["contract_digest"],
        "round": record["causal"]["round"],
        "scorecard": [
            {
                "criterion_id": criterion_id,
                "score": score,
                "evidence_refs": [f"evidence/{criterion_id}.json"],
            }
            for criterion_id, score in sorted(scores.items())
            if not isinstance(score, str)
        ],
        "minimum_score": record["minimum_score"],
        "verdict": record["verdict"],
        "critical_fail": record["critical_fail"],
        "blocking_pending_refs": record["blocking_pending_refs"],
        "evidence_refs": record["evidence_refs"],
        "criticisms": record["criticisms"],
        "required_changes": record["required_changes"],
        "issued_at": "2026-07-26T19:00:00-03:00",
        "expires_at": "2026-07-27T19:00:00-03:00",
    }


def derive_judge_report(record: dict[str, Any]) -> dict[str, Any]:
    """Converte o PANEL_RECORD interno no envelope que o CEO consome."""
    scores = aggregate(record["scorecard"])
    return {
        "artifact_type": "JUDGE_REPORT",
        "report_id": "judge-report-001",
        "causal": copy.deepcopy(record["causal"]),
        "candidate_digest": record["causal"]["candidate_digest"],
        "judge_capability_ref": "departamento-juizes",
        "judge_capability_digest": PRODUCER,
        "scorecard": [
            {
                "criterion_id": criterion_id,
                "applicable": True,
                "score": score,
                "evidence_refs": [f"evidence/{criterion_id}.json"],
            }
            for criterion_id, score in sorted(scores.items())
            if not isinstance(score, str)
        ],
        "minimum_score": record["minimum_score"],
        "verdict": record["verdict"],
        "critical_fail": record["critical_fail"],
        "blocking_pending_refs": record["blocking_pending_refs"],
        "evidence_refs": record["evidence_refs"],
        "issued_at": "2026-07-26T19:00:00-03:00",
        "expires_at": "2026-07-27T19:00:00-03:00",
    }


# --------------------------------------------------------------------------
# Regras comportamentais (recalculáveis por terceiro)
# --------------------------------------------------------------------------

def decide_verdict(
    scorecard: list[dict[str, Any]],
    *,
    lenses_returned: int = 3,
    lenses_expected: int = 3,
    uncovered: list[str] | None = None,
    critical_fail: bool = False,
    blocking_pending: bool = False,
    assignments_registered: bool = True,
) -> str:
    if uncovered:
        return "REPROVED"
    if lenses_returned < lenses_expected:
        return "REPROVED"
    if critical_fail or blocking_pending or not assignments_registered:
        return "REPROVED"
    minimum = computed_minimum(scorecard)
    if isinstance(minimum, str):
        return "REPROVED"
    return "VALIDATED" if minimum >= 9.5 else "REPROVED"


# --------------------------------------------------------------------------
# Verificações de pacote
# --------------------------------------------------------------------------

def validate_structure() -> list[str]:
    errors: list[str] = []
    required_local = [
        SKILL_PATH,
        CONTRACT_PATH,
        OPENAI_PATH,
        SCHEMA_PATH,
        EVALS_PATH,
        PACKAGE_ROOT / "evals" / "PLACAR.md",
        PACKAGE_ROOT / "references" / "protocolo-de-julgamento.md",
        PACKAGE_ROOT / "references" / "rubrica-e-corte.md",
        PACKAGE_ROOT / "references" / "modo-disputa-cega.md",
        PACKAGE_ROOT / "references" / "origem-migracao.md",
        PACKAGE_ROOT / "references" / "adr-002-nota-absoluta-e-modo-duplo.md",
    ]
    errors.extend(validate_required_files(required_local, "arquivo local"))

    required_external = [
        DIRECTOR_SCHEMA_PATH,
        CEO_SCHEMA_PATH,
        RULES_PATH,
        DIRECTOR_ROOT / "SKILL.md",
        STRUCTURE_ROOT / "ORGANOGRAMA.md",
        STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
    ]
    errors.extend(validate_required_files(required_external, "vínculo externo"))
    errors.extend(validate_agents_folder(AGENTS_ROOT, AGENT_NAMES))
    return errors


def validate_metadata() -> list[str]:
    errors = validate_frontmatter(SKILL_PATH, "departamento-juizes")
    errors.extend(
        validate_openai_yaml(OPENAI_PATH, "Departamento de Juízes", "$departamento-juizes")
    )
    displays = {
        "agente-julgar-fidelidade-e-contrato": "Juiz de Fidelidade e Contrato",
        "agente-julgar-robustez-e-evidencia": "Juiz de Robustez e Evidência",
        "agente-julgar-experiencia-e-risco": "Juiz de Experiência e Risco",
    }
    for name in AGENT_NAMES:
        root = AGENTS_ROOT / name
        errors.extend(validate_frontmatter(root / "SKILL.md", name))
        errors.extend(
            validate_openai_yaml(root / "agents" / "openai.yaml", displays[name], f"${name}")
        )
    return errors


def validate_normative_source() -> list[str]:
    errors: list[str] = []
    skill = SKILL_PATH.read_text(encoding="utf-8")
    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    if RULES_LINK_DEPARTMENT not in skill:
        errors.append("SKILL.md do Departamento sem a fonte normativa única")
    if RULES_LINK_DEPARTMENT not in contract:
        errors.append("contrato do Departamento sem a fonte normativa única")
    required_tokens = [
        "diretor-de-lentes",
        "JUDGE_ASSIGNMENT",
        "JUDGE_OPINION",
        "DEPARTMENT_JUDGE_REPORT",
        "JUDGE_REPORT",
        "minimum_score",
        "9,49",
        "Jeremias",
    ]
    for token in required_tokens:
        if token not in skill:
            errors.append(f"SKILL.md sem contrato obrigatório: {token}")
    for name in AGENT_NAMES:
        root = AGENTS_ROOT / name
        agent_skill = (root / "SKILL.md").read_text(encoding="utf-8")
        agent_contract = (root / "CONTRATO-DE-COMPROMISSO.md").read_text(encoding="utf-8")
        if RULES_LINK_AGENT not in agent_skill:
            errors.append(f"{name}: SKILL.md sem a fonte normativa única")
        if RULES_LINK_AGENT not in agent_contract:
            errors.append(f"{name}: contrato sem a fonte normativa única")
        if "BLOCKED_BYPASS_ATTEMPT" not in agent_skill:
            errors.append(f"{name}: SKILL.md sem a trava anti-bypass")
        if "departamento-juizes" not in agent_skill:
            errors.append(f"{name}: SKILL.md sem o superior declarado")
    return errors


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "criteriaMatrix",
        "judgeAssignment",
        "judgeOpinion",
        "judgeCapabilityGap",
        "panelRecord",
        "panelHandoff",
        "independentVerificationRecord",
    }
    missing = expected.difference(schema.get("$defs", {}))
    if missing:
        errors.append(f"schema sem defs: {sorted(missing)}")
    judge_enum = schema.get("$defs", {}).get("judgeId", {}).get("enum", [])
    if sorted(judge_enum) != sorted(AGENT_NAMES):
        errors.append(f"judgeId do schema divergente das pastas de agentes/: {judge_enum}")

    refs: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "$ref" in node:
                refs.append(node["$ref"])
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(schema)
    for ref in refs:
        try:
            json_pointer(schema, ref)
        except (KeyError, ValueError) as exc:
            errors.append(f"$ref não resolve: {ref}: {exc}")
    return errors


def validate_inherited_authority() -> list[str]:
    errors: list[str] = []
    if not CEO_SCHEMA_PATH.is_file() or not DIRECTOR_SCHEMA_PATH.is_file():
        return ["schema de fronteira ausente"]
    ceo = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8")).get("$defs", {})
    director = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8")).get("$defs", {})
    checks = [
        (ceo, "judgeReport", "producer", "departamento-juizes",
         "JUDGE_REPORT deve ser autoria dos Juízes"),
        (ceo, "judgeReport", "judge_capability_ref", "departamento-juizes",
         "JUDGE_REPORT deve declarar a capacidade dos Juízes"),
        (ceo, "independentVerification", "reviewer", "departamento-juizes",
         "a verificação independente deve ser dos Juízes"),
        (ceo, "exceptionAuthorization", "authorized_by", "jeremias",
         "só Jeremias autoriza exceção"),
        (director, "departmentJudgeReport", "producer", "departamento-juizes",
         "o parecer departamental deve ser autoria dos Juízes"),
        (director, "judgmentRequest", "producer", "diretor-de-lentes",
         "o pedido de julgamento deve ser autoria do Diretor"),
        (director, "judgmentRequest", "return_to", "diretor-de-lentes",
         "o pedido de julgamento deve retornar ao Diretor"),
    ]
    for definitions, name, prop, expected, message in checks:
        if name not in definitions:
            errors.append(f"schema de fronteira sem $defs/{name}")
        elif not find_const(definitions[name], prop, expected):
            errors.append(message)
    return errors


def validate_evals() -> list[str]:
    errors: list[str] = []
    evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    if evals.get("skill") != "departamento-juizes":
        errors.append("evals: skill incorreta")
    cases = evals.get("cases", [])
    if len(cases) < 12:
        errors.append(f"evals: necessários ao menos 12 casos, há {len(cases)}")
    if not any(case.get("origem") == "real" for case in cases):
        errors.append("evals: falta caso de origem real")
    identifiers = [case["id"] for case in cases]
    if len(identifiers) != len(set(identifiers)):
        errors.append("evals: id duplicado")
    for case in cases:
        if "$departamento-juizes" in case["prompt"]:
            errors.append(f"evals: {case['id']} nomeia a skill no prompt")
        if len(case.get("assertions", [])) < 3:
            errors.append(f"evals: {case['id']} com menos de 3 assertions")
    return errors


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

def run() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    director_schema = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))
    ceo_schema = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))

    cases: list[tuple[str, bool, list[str]]] = []

    cases.append(("pacote, agentes e vínculos externos", True, validate_structure()))
    cases.append(("metadata da gerente e dos três agentes", True, validate_metadata()))
    cases.append(("fonte normativa única e tokens de contrato", True, validate_normative_source()))
    cases.append(("links internos do pacote resolvem", True, validate_links(PACKAGE_ROOT)))
    cases.append(("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT)))
    cases.append(("schema interno e referências locais", True, validate_schema_shape(schema)))
    cases.append(("autoridades herdadas dos schemas de fronteira", True, validate_inherited_authority()))
    cases.append(("catálogo de evals", True, validate_evals()))

    fixtures = [
        ("CRITERIA_MATRIX", criteria_matrix()),
        ("JUDGE_ASSIGNMENT", judge_assignment()),
        ("JUDGE_ASSIGNMENT de robustez", judge_assignment("agente-julgar-robustez-e-evidencia")),
        ("JUDGE_OPINION", judge_opinion()),
        ("JUDGE_CAPABILITY_GAP", capability_gap()),
        ("PANEL_RECORD", panel_record()),
        ("PANEL_HANDOFF", panel_handoff()),
        ("INDEPENDENT_VERIFICATION", independent_verification()),
    ]
    for label, fixture in fixtures:
        cases.append((f"schema aceita {label}", True, validate_schema(fixture, schema, schema)))

    # --- cegueira, fronteira e trava ---------------------------------------

    wrong_lens = judge_assignment()
    wrong_lens["lens"] = "robustez-e-evidencia"
    cases.append(
        ("atribuição rejeita ótica trocada para o agente", False,
         validate_schema(wrong_lens, schema, schema))
    )

    wrong_return = judge_assignment()
    wrong_return["return_to"] = "diretor-de-lentes"
    cases.append(
        ("atribuição rejeita retorno fora da gerente", False,
         validate_schema(wrong_return, schema, schema))
    )

    leaky = judge_assignment()
    leaky["forbidden_context"] = [
        "pareceres dos outros agentes",
        "nota desejada",
        "rodada anterior",
    ]
    cases.append(
        ("atribuição exige proibição explícita de autoria", False,
         validate_schema(leaky, schema, schema))
    )

    foreign_judge = judge_assignment()
    foreign_judge["judge_id"] = "lente-juizes"
    cases.append(
        ("atribuição rejeita juiz de fora de agentes/", False,
         validate_schema(foreign_judge, schema, schema))
    )

    # --- rubrica e escala --------------------------------------------------

    fractional = judge_opinion(scores={"criterio-01": 9.5, "criterio-02": 10})
    cases.append(
        ("parecer rejeita nota fracionária", False,
         validate_schema(fractional, schema, schema))
    )

    out_of_range = judge_opinion(scores={"criterio-01": 11, "criterio-02": 10})
    cases.append(
        ("parecer rejeita nota fora de 0..10", False,
         validate_schema(out_of_range, schema, schema))
    )

    na_declared = judge_opinion(
        scores={"criterio-01": "n/a:criterio nao se aplica a este candidato", "criterio-02": 10}
    )
    cases.append(
        ("parecer aceita n/a com motivo verificável", True,
         validate_schema(na_declared, schema, schema))
    )

    na_empty = judge_opinion(scores={"criterio-01": "n/a:", "criterio-02": 10})
    cases.append(
        ("parecer rejeita n/a sem motivo", False,
         validate_schema(na_empty, schema, schema))
    )

    blocked = judge_opinion(status="BLOCKED")
    cases.append(
        ("parecer BLOCKED com abstenção é válido", True,
         validate_schema(blocked, schema, schema))
    )

    blocked_no_reason = judge_opinion(status="BLOCKED")
    blocked_no_reason.pop("abstencao")
    cases.append(
        ("parecer BLOCKED exige abstenção declarada", False,
         validate_schema(blocked_no_reason, schema, schema))
    )

    empty_opinion = judge_opinion()
    empty_opinion["scores"] = []
    cases.append(
        ("parecer COMPLETED exige ao menos uma nota", False,
         validate_schema(empty_opinion, schema, schema))
    )

    # --- consolidação e veredito -------------------------------------------

    below_cut = panel_record(
        scores={
            "criterio-01": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-02": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-03": {"agente-julgar-robustez-e-evidencia": 10},
            "criterio-04": {
                "agente-julgar-experiencia-e-risco": 9,
                "agente-julgar-robustez-e-evidencia": 10,
            },
        },
        verdict="VALIDATED",
    )
    cases.append(
        ("registro rejeita VALIDATED com menor nota 9", False,
         validate_schema(below_cut, schema, schema))
    )

    reproved = copy.deepcopy(below_cut)
    reproved["verdict"] = "REPROVED"
    reproved["criticisms"] = ["O criterio-04 ficou em 9 pela ótica de experiência."]
    reproved["required_changes"] = ["Tornar a falha observável para quem opera."]
    cases.append(
        ("registro aceita REPROVED com menor nota 9", True,
         validate_schema(reproved, schema, schema))
    )

    silent_reproval = copy.deepcopy(reproved)
    silent_reproval["criticisms"] = []
    silent_reproval["required_changes"] = []
    cases.append(
        ("reprovação sem crítica e mudança é rejeitada", False,
         validate_schema(silent_reproval, schema, schema))
    )

    with_gap = panel_record(gaps=[capability_gap()], verdict="VALIDATED")
    cases.append(
        ("registro rejeita VALIDATED com lacuna aberta", False,
         validate_schema(with_gap, schema, schema))
    )

    uncovered_record = panel_record(uncovered=["criterio-05"], verdict="VALIDATED")
    cases.append(
        ("registro rejeita VALIDATED com critério sem dona", False,
         validate_schema(uncovered_record, schema, schema))
    )

    no_assignments = panel_record(with_assignments=False, verdict="VALIDATED")
    cases.append(
        ("registro rejeita VALIDATED sem registro de emissão (R6)", False,
         validate_schema(no_assignments, schema, schema))
    )

    no_r6 = panel_record()
    no_r6["pending"] = ["fingerprint estilístico residual anotado"]
    cases.append(
        ("registro exige R6 nomeado em pending", False,
         validate_schema(no_r6, schema, schema))
    )

    critical = panel_record(verdict="VALIDATED", critical_fail=True)
    cases.append(
        ("registro rejeita VALIDATED com falha crítica", False,
         validate_schema(critical, schema, schema))
    )

    to_director = panel_record()
    to_director["return_to"] = "ceo-maestro"
    cases.append(
        ("registro rejeita retorno fora do Diretor", False,
         validate_schema(to_director, schema, schema))
    )

    # --- modo DISPUTA -------------------------------------------------------

    consensus_with_reason = panel_handoff(
        decision_mode="CONSENSO_UNANIME", leadership_reason="SEM_CONSENSO"
    )
    cases.append(
        ("handoff rejeita consenso com motivo de liderança", False,
         validate_schema(consensus_with_reason, schema, schema))
    )

    leadership = panel_handoff(
        decision_mode="DECISAO_DE_LIDERANCA",
        leadership_reason="SEM_CONSENSO",
        status="PARTIAL",
    )
    cases.append(
        ("handoff aceita decisão de liderança com motivo", True,
         validate_schema(leadership, schema, schema))
    )

    leadership_without_reason = panel_handoff(
        decision_mode="DECISAO_DE_LIDERANCA", leadership_reason="n/a", status="PARTIAL"
    )
    cases.append(
        ("handoff rejeita liderança sem motivo declarado", False,
         validate_schema(leadership_without_reason, schema, schema))
    )

    completed_with_gap = panel_handoff()
    completed_with_gap["capability_gaps"] = [capability_gap()]
    cases.append(
        ("handoff rejeita COMPLETED com lacuna aberta", False,
         validate_schema(completed_with_gap, schema, schema))
    )

    single_opinion = panel_handoff()
    single_opinion["valid_opinions"] = 1
    cases.append(
        ("handoff rejeita COMPLETED com menos de 2 pareceres", False,
         validate_schema(single_opinion, schema, schema))
    )

    # --- verificação de limitação ------------------------------------------

    partial_verification = independent_verification()
    partial_verification["checks"]["attempts_executed"] = False
    cases.append(
        ("verificação rejeita impossibilidade sem tentativa executada", False,
         validate_schema(partial_verification, schema, schema))
    )

    cases.append(
        ("verificação aceita NOT_VERIFIED com conferência parcial", True,
         validate_schema(independent_verification("NOT_VERIFIED"), schema, schema))
    )

    # --- fronteira: os envelopes produzidos servem aos consumidores ---------

    validated_record = panel_record()
    cases.append(
        ("Diretor aceita o DEPARTMENT_JUDGE_REPORT produzido", True,
         validate_schema(
             derive_department_judge_report(validated_record),
             director_schema,
             director_schema,
         ))
    )
    cases.append(
        ("CEO aceita o JUDGE_REPORT produzido", True,
         validate_schema(derive_judge_report(validated_record), ceo_schema, ceo_schema))
    )

    forged = derive_department_judge_report(validated_record)
    forged["minimum_score"] = 9.49
    cases.append(
        ("Diretor rejeita VALIDATED com 9,49", False,
         validate_schema(forged, director_schema, director_schema))
    )

    forged_ceo = derive_judge_report(validated_record)
    forged_ceo["minimum_score"] = 9.49
    cases.append(
        ("CEO rejeita VALIDATED com 9,49", False,
         validate_schema(forged_ceo, ceo_schema, ceo_schema))
    )

    spoofed = derive_department_judge_report(validated_record)
    spoofed["causal"]["producer"] = "departamento-desenvolvimento"
    cases.append(
        ("Diretor rejeita parecer forjado por outro Departamento", False,
         validate_schema(spoofed, director_schema, director_schema))
    )

    reproved_report = derive_department_judge_report(reproved)
    cases.append(
        ("Diretor aceita reprovação com crítica e mudança", True,
         validate_schema(reproved_report, director_schema, director_schema))
    )

    mute_reproval = copy.deepcopy(reproved_report)
    mute_reproval["criticisms"] = []
    mute_reproval["required_changes"] = []
    cases.append(
        ("Diretor rejeita reprovação muda", False,
         validate_schema(mute_reproval, director_schema, director_schema))
    )

    # --- aritmética da consolidação, recalculável por terceiro ---------------

    card_ten = scorecard_lines(default_scores())
    card_nine = scorecard_lines(
        {
            "criterio-01": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-02": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-03": {"agente-julgar-robustez-e-evidencia": 10},
            "criterio-04": {
                "agente-julgar-experiencia-e-risco": 9,
                "agente-julgar-robustez-e-evidencia": 10,
            },
        }
    )
    card_six = scorecard_lines(
        {
            "criterio-01": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-02": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-03": {"agente-julgar-robustez-e-evidencia": 6},
            "criterio-04": {"agente-julgar-experiencia-e-risco": 10},
        }
    )
    card_na = scorecard_lines(
        {
            "criterio-01": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-02": {
                "agente-julgar-fidelidade-e-contrato": "n/a:sem interface publica neste candidato"
            },
            "criterio-03": {"agente-julgar-robustez-e-evidencia": 10},
            "criterio-04": {"agente-julgar-experiencia-e-risco": 10},
        }
    )

    checks = [
        ("dois avaliadores no mesmo critério: vale a menor",
         aggregate(card_nine)["criterio-04"] == 9),
        ("minimum_score é o mínimo do scorecard",
         computed_minimum(card_nine) == 9),
        ("média alta não substitui a menor nota",
         computed_minimum(card_six) == 6 and sum([10, 10, 6, 10]) / 4 == 9.0),
        ("n/a declarado não entra no mínimo",
         computed_minimum(card_na) == 10),
        ("10 em tudo valida",
         decide_verdict(card_ten) == "VALIDATED"),
        ("9 em um critério reprova",
         decide_verdict(card_nine) == "REPROVED"),
        ("critério sem dona reprova mesmo com 10 em tudo",
         decide_verdict(card_ten, uncovered=["criterio-05"]) == "REPROVED"),
        ("ótica ausente reprova mesmo com 10 em tudo",
         decide_verdict(card_ten, lenses_returned=2) == "REPROVED"),
        ("falha crítica reprova mesmo com 10 em tudo",
         decide_verdict(card_ten, critical_fail=True) == "REPROVED"),
        ("pendência bloqueante reprova mesmo com 10 em tudo",
         decide_verdict(card_ten, blocking_pending=True) == "REPROVED"),
        ("sem registro de emissão não há VALIDATED (R6)",
         decide_verdict(card_ten, assignments_registered=False) == "REPROVED"),
        ("digest das regras é verificável",
         RULES_PATH.is_file() and sha256_file(RULES_PATH).startswith("sha256:")),
    ]
    for name, passed in checks:
        cases.append((name, True, [] if passed else ["condição comportamental falhou"]))

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
