"""Validador determinístico do Departamento de Juízes.

Verifica o pacote (arquivos, metadata, links), o schema interno, os artefatos
internos e — como regressão de fronteira — que os envelopes produzidos pelo
Departamento são aceitos pelos schemas do `diretor-de-lentes` e do `ceo-maestro`.

Uso: python validate_workflow.py
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
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
        conferir_digest_das_regras,
        digest,
        find_const,
        json_pointer,
        sha256_file,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_agents_folder,
    validate_contract_sections,
    validate_skill_tokens,
    SECOES_CONTRATO_AGENTE,
    TOKENS_SKILL_AGENTE,
        validate_frontmatter,
        validate_links,
        validate_openai_yaml,
        validate_required_files,
    )
    from _compartilhado.verificacoes_estrutura import (  # noqa: E402
        recusar_execucao_fora_da_fonte,
        validate_adr_series,
        validate_cobertura_de_validadores,
        validate_fonte_normativa_conferida,
        validate_placar_nao_declara_cadeia,
        validate_contagem_ligada_ao_instrumento,
        validate_travas_compartilhadas_com_efeito,
        validate_pendencia_tem_dono,
        validate_sem_check_tautologico,
        validate_trava_de_digest,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print(
        "[FAIL] motor compartilhado ausente em "
        f"{STRUCTURE_ROOT}/_compartilhado: {exc}"
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
        # RODADA 8 — a receita ao lado do numero, exigida pelo schema do CEO.
        "producer_digest_recipe": (
            "_compartilhado/validador_schema.py::sha256_file sobre o SKILL.md do produtor"
        ),
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


def assignment_id_for(judge: str, instance: int = 1) -> str:
    return f"assignment-{judge}" if instance == 1 else f"assignment-{judge}-i{instance}"


def write_path_for(assignment_id: str, handoff: str = "handoff-001", attempt: int = 1) -> str:
    """ADR-016, trava 1: o caminho carrega handoff, attempt e assignment_id."""
    return f"julgamento/{handoff}/a{attempt}/{assignment_id}/"


def custody_copy_for(
    assignment_id: str, taken_at: str = "2026-07-26T18:09:00-03:00"
) -> dict[str, Any]:
    """ADR-016, trava 3: cópia de custódia com digest, tomada antes do despacho."""
    return {
        "path": f"custodia/{assignment_id}/emissao.json",
        "sha256": digest("c"),
        "bytes": 4096,
        "taken_at": taken_at,
    }


def no_return_evidence(
    runtime_signal: str = "NENHUM",
    assignment_id: str = "assignment-agente-julgar-experiencia-e-risco",
) -> dict[str, Any]:
    """ADR-016, trava 2: a conferência em disco que todo estado de não-entrega carrega."""
    caminho = write_path_for(assignment_id)
    return {
        "checked_paths": [caminho],
        "checks": [
            {"at": "2026-07-26T18:25:00-03:00", "path": caminho, "exists": False},
            {"at": "2026-07-26T18:41:00-03:00", "path": caminho, "exists": False},
        ],
        "runtime_signal": runtime_signal,
        "waited_seconds": 960,
    }


def judge_assignment(
    judge: str = "agente-julgar-fidelidade-e-contrato", instance: int = 1
) -> dict[str, Any]:
    assignment_id = assignment_id_for(judge, instance)
    return {
        "artifact_type": "JUDGE_ASSIGNMENT",
        "assignment_id": assignment_id,
        "causal": causal(),
        "judge_id": judge,
        "lens": AGENT_LENS[judge],
        "instance": instance,
        "write_path": write_path_for(assignment_id),
        "custody_copy": custody_copy_for(assignment_id),
        "mode": "VALIDACAO",
        "candidate_digest": CANDIDATE,
        "anonymized_candidate": f"julgamento/assignment-{judge}/candidato.zip",
        "criteria": assignment_criteria(judge),
        "rubric_ref": "rubrica-corte-v2",
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


def aggregation_rule(
    method: str = "MENOR", declared_at: str = "2026-07-26T18:05:00-03:00"
) -> dict[str, Any]:
    """ADR-016: a regra de combinação entre instâncias da mesma lente.

    `declared_at` precede o `issued_at` de toda emissão da rodada (18:10) e, por
    consequência, o de todo parecer. Regra escolhida depois de ver as notas não é
    regra: é seleção de resultado.
    """
    return {
        "method": method,
        "declared_at": declared_at,
        "rationale": "Fixada pelo Diretor no pedido, antes de qualquer parecer existir.",
    }


def panel_record(
    scores: dict[str, dict[str, Any]] | None = None,
    verdict: str = "VALIDATED",
    required_level: str = "PRODUCAO",
    critical_fail: bool = False,
    blocking_pending_refs: list[str] | None = None,
    gaps: list[dict[str, Any]] | None = None,
    uncovered: list[str] | None = None,
    with_assignments: bool = True,
    instances_per_lens: int = 1,
    score_range: tuple[int, int] | None = None,
    rule: dict[str, Any] | None = None,
) -> dict[str, Any]:
    values = default_scores() if scores is None else scores
    card = scorecard_lines(values)
    judges = sorted({line["judge_id"] for line in card})
    reproved = verdict != "VALIDATED"
    minimum = computed_minimum(card)
    if score_range is None:
        ponto = 0 if isinstance(minimum, str) else minimum
        score_range = (ponto, ponto)
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
                    "assignment_id": assignment_id_for(judge, instancia),
                    "judge_id": judge,
                    "lens": AGENT_LENS[judge],
                    "instance": instancia,
                    "issued_at": "2026-07-26T18:10:00-03:00",
                    "destination": write_path_for(assignment_id_for(judge, instancia)),
                    "custody_copy": custody_copy_for(assignment_id_for(judge, instancia)),
                }
                for judge in judges
                for instancia in range(1, instances_per_lens + 1)
            ]
            if with_assignments
            else []
        ),
        "panel": [
            {
                "judge_id": judge,
                "lens": AGENT_LENS[judge],
                "instance": instancia,
                "status": "COMPLETED",
                "confidence": "alta",
                "substrate": "desconhecido",
                "tier": "desconhecido",
            }
            for judge in judges
            for instancia in range(1, instances_per_lens + 1)
        ],
        "instances_per_lens": instances_per_lens,
        "aggregation_rule": rule or aggregation_rule(),
        "scorecard": card,
        "minimum_score": minimum,
        "minimum_score_range": {"lo": score_range[0], "hi": score_range[1]},
        "verdict": verdict,
        "required_level": required_level,
        "critical_fail": critical_fail,
        "blocking_pending_refs": blocking_pending_refs or [],
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
        "rubric_ref": "rubrica-corte-v2",
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
        "rubric_ref": "rubrica-corte-v2",
        "status": status,
        "decision_mode": decision_mode,
        "leadership_reason": leadership_reason,
        "winner": "candidato-campeao",
        "champion_kept": True,
        "panel": [
            {
                "judge_id": judge,
                "lens": AGENT_LENS[judge],
                "instance": 1,
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
        # RODADA 8, LIMITE DECLARADO — o schema do Diretor ainda não
        # conhece `producer_digest_recipe`. O campo sai AQUI, com o motivo
        # escrito, em vez de o alcance ser apresentado como se fosse total.
        "artifact_type": "DEPARTMENT_JUDGE_REPORT",
        "report_id": "department-judge-report-001",
        "causal": {
            chave: valor
            for chave, valor in copy.deepcopy(record["causal"]).items()
            if chave != "producer_digest_recipe"
        },
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
        "minimum_score_range": copy.deepcopy(record["minimum_score_range"]),
        "instances_per_lens": record["instances_per_lens"],
        "aggregation_rule": copy.deepcopy(record["aggregation_rule"]),
        "verdict": record["verdict"],
        "required_level": record["required_level"],
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
        "minimum_score_range": copy.deepcopy(record["minimum_score_range"]),
        "instances_per_lens": record["instances_per_lens"],
        "aggregation_rule": copy.deepcopy(record["aggregation_rule"]),
        "verdict": record["verdict"],
        "required_level": record["required_level"],
        "critical_fail": record["critical_fail"],
        "blocking_pending_refs": record["blocking_pending_refs"],
        "evidence_refs": record["evidence_refs"],
        "issued_at": "2026-07-26T19:00:00-03:00",
        "expires_at": "2026-07-27T19:00:00-03:00",
    }


# --------------------------------------------------------------------------
# Regras comportamentais (recalculáveis por terceiro)
# --------------------------------------------------------------------------

def banda_do_ponto(nota: int) -> str:
    """ADR-014: a faixa fixa, lida como função de um ponto."""
    if nota >= 10:
        return "VALIDATED"
    if nota >= 7:
        return "ACEITO_USO_INTERNO"
    return "REPROVED"


def atravessa_o_corte(lo: int, hi: int) -> bool:
    """ADR-016: a faixa atravessa um corte quando as pontas caem em bandas diferentes."""
    return banda_do_ponto(lo) != banda_do_ponto(hi)


def decide_verdict(
    scorecard: list[dict[str, Any]],
    *,
    lenses_returned: int = 3,
    lenses_expected: int = 3,
    uncovered: list[str] | None = None,
    critical_fail: bool = False,
    blocking_pending: bool = False,
    assignments_registered: bool = True,
    instance_minimums: list[int] | None = None,
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
    # ADR-016: com mais de uma instância por lente o dado é a FAIXA, não o ponto.
    # Faixa que atravessa um corte do ADR-014 não vira veredito: sai como
    # NAO_DISCRIMINADO, que não autoriza produção, publicação nem uso interno.
    # Os gates acima já reprovaram falha crítica, lacuna e pendência bloqueante —
    # quem falhou gate está reprovado, não indiscriminado.
    if instance_minimums and len(instance_minimums) >= 2:
        lo, hi = min(instance_minimums), max(instance_minimums)
        if atravessa_o_corte(lo, hi):
            return "NAO_DISCRIMINADO"
        return banda_do_ponto(lo)
    # ADR-014: faixa fixa, sem discricionariedade. Só 10 atravessa para
    # VALIDATED; 7–9 é ACEITO_USO_INTERNO; 6 ou menos reprova. A régua não se
    # move com o pedinte — quem varia é o `required_level` de quem pede.
    return banda_do_ponto(minimum)


def verdict_reaches_required_level(verdict: str, required_level: str) -> bool:
    # ADR-016: NAO_DISCRIMINADO não alcança nenhum nível. Não é reprovação nem
    # aceite, e não autoriza produção, publicação, exposição a terceiro nem uso
    # interno.
    if required_level == "PRODUCAO":
        return verdict == "VALIDATED"
    if required_level == "INTERNO":
        return verdict in {"VALIDATED", "ACEITO_USO_INTERNO"}
    return False


# --------------------------------------------------------------------------
# ADR-016 — as três travas de orquestração, em código e não em prosa
#
# Cada uma tem caso negativo próprio no `run()` e foi provada por mutação
# executada: a própria trava desligada, e o validador ficando vermelho. Trava
# declarada e não provada não conta.
# --------------------------------------------------------------------------

METODOS_DE_AGREGACAO = ("MENOR", "MEDIANA", "EMPATE_DECLARADO")
CAMINHO_DE_ESCRITA = re.compile(
    r"^julgamento/(?P<handoff>[A-Za-z0-9._-]+)/a(?P<attempt>\d+)/(?P<slug>[A-Za-z0-9._-]+)/$"
)
SINAIS_DE_RUNTIME_TERMINAIS = ("EXECUTOR_ERROR", "TIMEOUT_DECLARADO")
ESTADOS_TERMINAIS_DE_EXECUTOR = ("SEM_RETORNO", "FALHO")


def trava_caminho_exclusivo(
    emissoes: list[dict[str, Any]],
    *,
    handoff_id: str = "handoff-001",
    attempt: int = 1,
) -> list[str]:
    """TRAVA 1 — caminho de escrita exclusivo por emissão.

    Duas emissões nunca compartilham arquivo. Em 2026-07-31 duas instâncias da
    mesma ótica escreveram no caminho canônico; uma foi descartada por
    proveniência, e não por mérito, e três de oito vereditos passaram a depender
    de qual sobreviveu à colisão.
    """
    errors: list[str] = []
    vistos: dict[str, str] = {}
    for emissao in emissoes:
        identificador = emissao.get("assignment_id", "<sem assignment_id>")
        caminho = emissao.get("write_path") or emissao.get("destination")
        if not isinstance(caminho, str) or not caminho:
            errors.append(f"{identificador}: emissão sem caminho de escrita")
            continue
        casado = CAMINHO_DE_ESCRITA.match(caminho)
        if casado is None:
            errors.append(
                f"{identificador}: caminho de escrita fora do formato "
                f"julgamento/<handoff>/a<attempt>/<assignment_id>/: {caminho}"
            )
            continue
        if casado.group("slug") != identificador:
            errors.append(
                f"{identificador}: caminho de escrita não deriva do assignment_id: {caminho}"
            )
        if casado.group("handoff") != handoff_id:
            errors.append(
                f"{identificador}: caminho de escrita não deriva do handoff da rodada: {caminho}"
            )
        if casado.group("attempt") != str(attempt):
            errors.append(
                f"{identificador}: caminho de escrita não deriva do attempt da rodada: {caminho}"
            )
        if caminho in vistos:
            errors.append(
                f"caminho de escrita compartilhado por {vistos[caminho]} e "
                f"{identificador}: {caminho}"
            )
        else:
            vistos[caminho] = identificador
    return errors


def trava_ausencia_nao_prova_morte(
    panel: list[dict[str, Any]], emissoes: list[dict[str, Any]] | None = None
) -> list[str]:
    """TRAVA 2 — proibição de concluir morte de executor por ausência de arquivo.

    Sem sinal de runtime, o único estado admissível é `AGUARDANDO`, e não há
    redespacho. Em 2026-07-31 a conclusão contrária foi tirada três vezes na
    mesma rodada, e cada redespacho criou a segunda instância que colidiu.
    """
    errors: list[str] = []
    for item in panel:
        status = item.get("status")
        identificador = f"{item.get('judge_id')}#{item.get('instance')}"
        if status not in ESTADOS_TERMINAIS_DE_EXECUTOR + ("AGUARDANDO",):
            continue
        evidencia = item.get("no_return_evidence")
        if not isinstance(evidencia, dict):
            errors.append(f"{identificador}: {status} sem no_return_evidence")
            continue
        conferencias = evidencia.get("checks")
        if not isinstance(conferencias, list) or len(conferencias) < 2:
            errors.append(
                f"{identificador}: {status} com menos de duas conferências em disco"
            )
        if not evidencia.get("checked_paths"):
            errors.append(f"{identificador}: {status} sem caminho conferido")
        sinal = evidencia.get("runtime_signal")
        if status in ESTADOS_TERMINAIS_DE_EXECUTOR and sinal not in SINAIS_DE_RUNTIME_TERMINAIS:
            errors.append(
                f"{identificador}: {status} declarado com runtime_signal {sinal!r} — "
                "ausência de arquivo não prova morte de executor"
            )
    if emissoes:
        chaves: dict[tuple[Any, Any], str] = {}
        for emissao in emissoes:
            chave = (emissao.get("judge_id"), emissao.get("instance"))
            identificador = emissao.get("assignment_id", "<sem assignment_id>")
            if chave in chaves:
                errors.append(
                    f"redespacho: segunda emissão para {chave[0]} instância {chave[1]} "
                    f"({chaves[chave]} e {identificador}) no mesmo handoff e attempt"
                )
            else:
                chaves[chave] = identificador
    return errors


def trava_custodia_antes_do_despacho(emissoes: list[dict[str, Any]]) -> list[str]:
    """TRAVA 3 — cópia de custódia obrigatória, com digest, antes do despacho.

    Onde houve custódia em 2026-07-31, a perda de bytes virou incidente contido;
    onde não houve, virou parecer irrecuperável.
    """
    errors: list[str] = []
    for emissao in emissoes:
        identificador = emissao.get("assignment_id", "<sem assignment_id>")
        custodia = emissao.get("custody_copy")
        if not isinstance(custodia, dict):
            errors.append(f"{identificador}: despacho sem cópia de custódia")
            continue
        for campo in ("path", "sha256", "bytes", "taken_at"):
            if not custodia.get(campo):
                errors.append(f"{identificador}: cópia de custódia sem {campo}")
        assinatura = custodia.get("sha256")
        if not isinstance(assinatura, str) or not assinatura.startswith("sha256:"):
            errors.append(f"{identificador}: cópia de custódia sem digest sha256")
        tamanho = custodia.get("bytes")
        if not isinstance(tamanho, int) or tamanho <= 0:
            errors.append(f"{identificador}: cópia de custódia sem bytes verificáveis")
        tomada_em = custodia.get("taken_at")
        despachada_em = emissao.get("issued_at")
        if isinstance(tomada_em, str) and isinstance(despachada_em, str):
            if tomada_em >= despachada_em:
                errors.append(
                    f"{identificador}: cópia de custódia tomada em {tomada_em}, "
                    f"não anterior ao despacho em {despachada_em}"
                )
    return errors


def trava_regra_declarada_antes_das_notas(
    rule: Any, opinion_times: list[str]
) -> list[str]:
    """A regra de agregação é fixada antes de qualquer parecer existir.

    Regra escolhida depois de ver as notas não é regra: é seleção de resultado.
    """
    errors: list[str] = []
    if not isinstance(rule, dict):
        errors.append("rodada sem aggregation_rule declarada")
        return errors
    metodo = rule.get("method")
    if metodo not in METODOS_DE_AGREGACAO:
        errors.append(f"método de agregação fora do enum: {metodo!r}")
    declarada_em = rule.get("declared_at")
    if not isinstance(declarada_em, str) or not declarada_em:
        errors.append("aggregation_rule sem declared_at")
        return errors
    for emitido_em in opinion_times:
        if declarada_em >= emitido_em:
            errors.append(
                f"aggregation_rule declarada em {declarada_em}, não anterior ao "
                f"parecer emitido em {emitido_em}"
            )
    return errors


def trava_evidencia_simetrica(
    rule: Any, emissoes: list[dict[str, Any]]
) -> list[str]:
    """ADR-023 — toda instância da rodada julga a MESMA evidência executada.

    A medição de 2026-08-04 (nove departamentos, 6 instâncias, 54 pareceres)
    devolveu divergência em 60% dos 40 pares e **7 `NAO_DISCRIMINADO` de 9**. A
    causa não era discordância: era **evidência assimétrica** — uma instância
    rodou um experimento que a outra não rodou, e por isso enxergou um defeito
    que a outra não podia ver.

    Isso quebra o remédio do ADR-016 pelo meio: acrescentar instâncias sobre
    evidência desigual não mede melhor, só produz mais indeterminação — e
    `NAO_DISCRIMINADO` não alcança nenhum `required_level`, então a rodada custa
    o dobro e não autoriza nada.

    A trava exige o que a declaração promete: se a regra declara simetria, a
    bateria rodou UMA vez antes do despacho e **o mesmo digest viaja em toda
    emissão**. Divergência de digest entre emissões da mesma rodada é evidência
    assimétrica em flagrante, não detalhe de transporte.
    """
    errors: list[str] = []
    if not isinstance(rule, dict):
        return errors
    simetria = rule.get("evidence_symmetry")
    if simetria is None:
        # Rodada que não declara simetria segue sob o ADR-016 puro. Silêncio
        # aqui é deliberado: as rodadas congeladas não a declaram, e exigir
        # delas obrigaria a reescrever registro passado para ficar verde.
        return errors
    if not isinstance(simetria, dict):
        errors.append("evidence_symmetry declarada mas não é objeto")
        return errors

    declarado = simetria.get("evidence_digest")
    if not isinstance(declarado, str) or not declarado:
        errors.append("evidence_symmetry sem evidence_digest")
        return errors
    bateria = simetria.get("battery")
    if not isinstance(bateria, list) or not bateria:
        errors.append("evidence_symmetry sem battery declarada")

    declarada_em = simetria.get("declared_at")
    for emissao in emissoes:
        alvo = emissao.get("assignment_id", "<sem id>")
        carregado = emissao.get("evidence_digest")
        if carregado is None:
            errors.append(
                f"emissão {alvo}: rodada declara evidence_symmetry e a emissão "
                "não carrega evidence_digest — o juiz receberia a regra sem a "
                "evidência que ela promete"
            )
            continue
        if carregado != declarado:
            errors.append(
                f"emissão {alvo}: evidence_digest {carregado} diverge do "
                f"declarado {declarado} — instâncias da mesma rodada julgariam "
                "evidências diferentes"
            )
        emitido_em = emissao.get("issued_at")
        if (isinstance(declarada_em, str) and isinstance(emitido_em, str)
                and declarada_em >= emitido_em):
            errors.append(
                f"emissão {alvo}: evidência declarada em {declarada_em}, não "
                f"anterior à emissão em {emitido_em} — bateria que roda depois "
                "do despacho não é evidência comum, é evidência de uma só"
            )
    return errors


def _dentro_de(caminho: str, raiz: str) -> bool:
    """`caminho` está sob `raiz`? Compara por segmento, não por prefixo de
    texto — `a/b2` começa com `a/b` e não está dentro dele."""
    a = [p for p in raiz.replace("\\", "/").strip("/").split("/") if p]
    b = [p for p in caminho.replace("\\", "/").strip("/").split("/") if p]
    return len(b) >= len(a) and b[: len(a)] == a


def trava_isolamento_por_runtime(emissoes: list[dict[str, Any]]) -> list[str]:
    """ADR-024 — instâncias que precisam ser independentes vão em raízes disjuntas.

    Em 2026-08-04 seis instâncias foram despachadas em pasta compartilhada, e
    uma delas declarou no próprio parecer:

        "O diretório temporário é compartilhado com a instância 2: encontrei um
        gerador de parecer dela e **não o abri**. A independência dependeu da
        minha recusa, não de isolamento do runtime."

    A trava T3 do ADR-016 já exige `write_path` exclusivo — e ela impede
    **colisão de escrita**, não **leitura**. O que foi medido foi leitura: o
    arquivo da outra instância estava alcançável, e a independência daquela
    rodada apoiou-se na honestidade do agente.

    Independência que depende de recusa é a mesma família de
    `aviso-em-prosa-nao-previne-erro`: a regra existe, e nada a faz valer.
    """
    errors: list[str] = []
    declaram = [e for e in emissoes if e.get("isolation") is not None]
    if not declaram:
        # Rodada que não declara isolamento segue sob o ADR-016 puro. O silêncio
        # é deliberado: as congeladas não declaram, e exigir delas obrigaria a
        # reescrever registro passado.
        return errors
    if len(declaram) != len(emissoes):
        errors.append(
            f"{len(declaram)} de {len(emissoes)} emissões declaram isolamento — "
            "rodada isola ou não isola; parcial não é isolamento, é a pasta "
            "compartilhada de volta com nome melhor"
        )

    raizes: list[tuple[str, str]] = []
    for emissao in declaram:
        alvo = emissao.get("assignment_id", "<sem id>")
        iso = emissao["isolation"]
        if not isinstance(iso, dict):
            errors.append(f"emissão {alvo}: isolation não é objeto")
            continue
        raiz = iso.get("root")
        if not isinstance(raiz, str) or not raiz:
            errors.append(f"emissão {alvo}: isolation sem root")
            continue
        if iso.get("mode") == "pasta-compartilhada":
            errors.append(
                f"emissão {alvo}: isolation declara pasta-compartilhada — "
                "declarar a ausência é auditável e continua não sendo "
                "isolamento; a instância alcança o rascunho da outra"
            )
        caminho = emissao.get("write_path")
        if isinstance(caminho, str) and caminho and not _dentro_de(caminho, raiz):
            errors.append(
                f"emissão {alvo}: write_path {caminho!r} fora da própria raiz "
                f"{raiz!r} — escrever fora do isolamento o desfaz"
            )
        for outro_alvo, outra in raizes:
            if _dentro_de(raiz, outra) or _dentro_de(outra, raiz):
                errors.append(
                    f"emissões {outro_alvo} e {alvo}: raízes {outra!r} e "
                    f"{raiz!r} não são disjuntas — uma instância enxerga a "
                    "pasta da outra"
                )
        raizes.append((alvo, raiz))
    return errors


def trava_forma_do_painel(
    panel: list[dict[str, Any]], instances_per_lens: int
) -> list[str]:
    """O que substituiu o antigo `maxItems: 3` do painel, e é mais apertado.

    No máximo três lentes distintas, e cada lente com exatamente
    `instances_per_lens` entradas, numeradas 1..N sem repetir. `maxItems: 3`
    aceitava duas linhas da mesma lente e nenhuma da terceira.
    """
    errors: list[str] = []
    por_lente: dict[Any, list[Any]] = {}
    for item in panel:
        por_lente.setdefault(item.get("lens"), []).append(item.get("instance"))
    if len(por_lente) > 3:
        errors.append(f"painel com {len(por_lente)} lentes distintas; o teto é 3")
    for lente, instancias in por_lente.items():
        esperado = list(range(1, instances_per_lens + 1))
        if sorted(i for i in instancias if isinstance(i, int)) != esperado:
            errors.append(
                f"lente {lente}: instâncias {sorted(instancias, key=str)} não são "
                f"exatamente {esperado}"
            )
    return errors


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
        PACKAGE_ROOT / "references" / "adr-014-dois-niveis-de-veredito.md",
        PACKAGE_ROOT / "references" / "adr-016-agregacao-entre-instancias.md",
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
    # --- Estrutura normativa dos contratos e SKILL de agente ---------------
    # GUIA, passos 7 e 8. Ate 2026-07-27 nenhum validador olhava heading de
    # contrato de agente, e o resultado medido foi 15 de 66 conformes, com a
    # trava anti-bypass ausente em 30. A conferencia mora no _compartilhado; a
    # lista do que e obrigatorio continua sendo decisao deste pacote.
    for _agente in sorted(p for p in AGENTS_ROOT.iterdir() if p.is_dir()):
        errors.extend(
            validate_contract_sections(
                _agente / "CONTRATO-DE-COMPROMISSO.md",
                SECOES_CONTRATO_AGENTE,
                _agente.name,
            )
        )
        errors.extend(
            validate_skill_tokens(
                _agente / "SKILL.md", TOKENS_SKILL_AGENTE, _agente.name
            )
        )
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
        "required_level",
        "ACEITO_USO_INTERNO",
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


def validate_adr014_normative_consistency() -> list[str]:
    """Trava as regras operacionais que não podem divergir do schema do ADR-014."""
    errors: list[str] = []
    skill = SKILL_PATH.read_text(encoding="utf-8")
    adr = (
        PACKAGE_ROOT / "references" / "adr-014-dois-niveis-de-veredito.md"
    ).read_text(encoding="utf-8")
    rubric = (
        PACKAGE_ROOT / "references" / "rubrica-e-corte.md"
    ).read_text(encoding="utf-8")
    dispute = (
        PACKAGE_ROOT / "references" / "modo-disputa-cega.md"
    ).read_text(encoding="utf-8")

    for text, label in ((adr, "ADR-014"), (rubric, "rubrica v2")):
        if "`required_level` **não é inferido**" not in text:
            errors.append(f"{label} permite inferir required_level ausente")
        if "recusada antes do julgamento" not in text:
            errors.append(f"{label} não recusa missão sem required_level")
    if 'rubric_ref: "rubrica-corte-v2"' not in dispute:
        errors.append("modo de disputa não emite rubric_ref v2")
    if 'rubric_ref: "rubrica-corte-v1"' in dispute:
        errors.append("modo de disputa ainda emite rubric_ref v1")
    if skill.count("qualquer veredito positivo") < 2:
        errors.append(
            "SKILL não bloqueia VALIDATED e ACEITO_USO_INTERNO em todas as lacunas"
        )
    if "`ACEITO_USO_INTERNO` ou `REPROVED`" not in skill:
        errors.append("SKILL não exige crítica e mudança nos dois vereditos não finais")
    return errors


def validate_adr016_agreement() -> list[str]:
    """A regra de agregação tem de CONCORDAR entre schema, protocolo e rubrica.

    Aceite mecânico da frente do método (2026-07-31): não basta que cada arquivo
    diga algo sobre agregação — os três têm de dizer a MESMA coisa, e a
    conferência é derivada dos artefatos, não de uma lista escrita à mão aqui.
    O conjunto de métodos e o enum de veredito saem dos schemas e são cobrados
    nos documentos.
    """
    errors: list[str] = []
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if not DIRECTOR_SCHEMA_PATH.is_file() or not CEO_SCHEMA_PATH.is_file():
        return ["schema de fronteira ausente para conferir a regra de agregação"]
    director = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))
    ceo = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))

    protocolo = (
        PACKAGE_ROOT / "references" / "protocolo-de-julgamento.md"
    ).read_text(encoding="utf-8")
    rubrica = (
        PACKAGE_ROOT / "references" / "rubrica-e-corte.md"
    ).read_text(encoding="utf-8")
    adr = (
        PACKAGE_ROOT / "references" / "adr-016-agregacao-entre-instancias.md"
    ).read_text(encoding="utf-8")
    skill = SKILL_PATH.read_text(encoding="utf-8")

    # 1. Os três schemas declaram o MESMO conjunto de métodos de agregação.
    metodos: dict[str, list[str]] = {}
    for rotulo, documento in (
        ("juízes", schema),
        ("diretor", director),
        ("CEO", ceo),
    ):
        enum = documento.get("$defs", {}).get("aggregationMethod", {}).get("enum")
        if not enum:
            errors.append(f"schema do {rotulo} sem aggregationMethod")
        else:
            metodos[rotulo] = enum
    if metodos and len({tuple(v) for v in metodos.values()}) != 1:
        errors.append(f"métodos de agregação divergem entre schemas: {metodos}")
    if metodos and sorted(next(iter(metodos.values()))) != sorted(METODOS_DE_AGREGACAO):
        errors.append(
            "schema e validador discordam do conjunto de métodos de agregação: "
            f"{sorted(next(iter(metodos.values())))} != {sorted(METODOS_DE_AGREGACAO)}"
        )

    # 2. Os três schemas declaram o MESMO enum de veredito, com NAO_DISCRIMINADO.
    vereditos = {
        "juízes": schema["$defs"]["panelRecord"]["properties"]["verdict"].get("enum", []),
        "diretor": director["$defs"]["departmentJudgeReport"]["properties"]["verdict"].get(
            "enum", []
        ),
        "CEO": ceo["$defs"]["judgeReport"]["properties"]["verdict"].get("enum", []),
    }
    if len({tuple(sorted(v)) for v in vereditos.values()}) != 1:
        errors.append(f"enum de veredito diverge entre schemas: {vereditos}")
    for rotulo, enum in vereditos.items():
        if "NAO_DISCRIMINADO" not in enum:
            errors.append(f"schema do {rotulo} sem NAO_DISCRIMINADO no enum de veredito")

    # 3. Protocolo e rubrica falam dos MESMOS métodos que o schema declara.
    for metodo in metodos.get("juízes", METODOS_DE_AGREGACAO):
        if metodo not in protocolo:
            errors.append(f"protocolo não declara o método de agregação {metodo}")
        if metodo not in rubrica:
            errors.append(f"rubrica não declara o método de agregação {metodo}")

    # 4. O pedido fixa a regra ANTES de qualquer parecer, e os três documentos dizem isso.
    pedido = director["$defs"]["judgmentRequest"]
    for campo in ("instances_per_lens", "aggregation_rule"):
        if campo not in pedido.get("required", []):
            errors.append(f"JUDGMENT_REQUEST não exige {campo}")
    if "antes de qualquer parecer existir" not in protocolo:
        errors.append("protocolo não fixa a regra antes de qualquer parecer existir")
    if "antes de qualquer parecer existir" not in rubrica:
        errors.append("rubrica não fixa a regra antes de qualquer parecer existir")
    if "antes de qualquer parecer existir" not in adr:
        errors.append("ADR-016 não fixa a regra antes de qualquer parecer existir")

    # 5. NAO_DISCRIMINADO não autoriza nada — declarado nos três documentos.
    for texto, rotulo in (
        (protocolo, "protocolo"),
        (rubrica, "rubrica"),
        (adr, "ADR-016"),
        (skill, "SKILL"),
    ):
        if "NAO_DISCRIMINADO" not in texto:
            errors.append(f"{rotulo} não declara NAO_DISCRIMINADO")
        if "não autoriza" not in texto:
            errors.append(f"{rotulo} não declara que NAO_DISCRIMINADO não autoriza nada")

    # 6. As três travas de orquestração aparecem nomeadas no protocolo e na SKILL.
    for token in ("write_path", "custody_copy", "no_return_evidence", "AGUARDANDO"):
        if token not in protocolo:
            errors.append(f"protocolo não declara a trava {token}")
    for token in ("write_path", "custody_copy", "AGUARDANDO"):
        if token not in skill:
            errors.append(f"SKILL não declara a trava {token}")

    # 7. O schema interno carrega as travas onde elas valem.
    atribuicao = schema["$defs"]["judgeAssignment"].get("required", [])
    for campo in ("instance", "write_path", "custody_copy"):
        if campo not in atribuicao:
            errors.append(f"JUDGE_ASSIGNMENT não exige {campo}")
    registro = schema["$defs"]["panelRecord"].get("required", [])
    for campo in ("instances_per_lens", "aggregation_rule", "minimum_score_range"):
        if campo not in registro:
            errors.append(f"PANEL_RECORD não exige {campo}")
    if "AGUARDANDO" not in schema["$defs"]["judgeStatus"].get("enum", []):
        errors.append("judgeStatus sem AGUARDANDO")

    # 8. A regra 4 da §3 continua proibindo média e mediana ENTRE CRITÉRIOS.
    #    A regra nova combina instâncias da MESMA lente; se a proibição antiga
    #    sumir, a agregação vira porta de entrada para a média que o ADR-002 baniu.
    if "**Proibido** média, mediana" not in protocolo:
        errors.append("protocolo deixou de proibir média e mediana entre critérios")
    if "Proibido:** média, mediana" not in rubrica:
        errors.append("rubrica deixou de proibir média e mediana entre critérios")
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
    required_level_contracts = [
        (director, "judgmentRequest", "JUDGMENT_REQUEST do Diretor"),
        (director, "departmentJudgeReport", "DEPARTMENT_JUDGE_REPORT do Diretor"),
        (ceo, "judgeReport", "JUDGE_REPORT do CEO"),
    ]
    for definitions, name, label in required_level_contracts:
        if name in definitions and "required_level" not in definitions[name].get(
            "required", []
        ):
            errors.append(f"{label} não exige required_level")
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

    # --- Trava do instrumento (frente 2, 2026-07-27) -----------------------
    # `tipo` separa o que o caso mede: PORTAO e pedido cru — mede recusa e
    # roteamento; OPERACAO traz o envelope no prompt — mede o que a skill faz
    # depois de autorizada. Sem essa separacao o catalogo mede a recusa com
    # precisao e a execucao por hipotese, e assercoes pos-portao ficam
    # inalcancaveis por construcao. Caso irrodavel e APOSENTADO com motivo e
    # sai do denominador.
    validos = [c for c in cases if c.get("status") != "APOSENTADO"]
    for case in cases:
        tipo = case.get("tipo")
        if tipo not in {"PORTAO", "OPERACAO"}:
            errors.append(f"evals: {case.get('id')} sem tipo PORTAO/OPERACAO")
        if case.get("status") == "APOSENTADO" and not case.get("motivo"):
            errors.append(f"evals: {case.get('id')} aposentado sem motivo")
    if len(validos) < 12:
        errors.append(
            f"evals: apenas {len(validos)} casos validos (aposentados nao contam)"
        )

    return errors


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# TAREFA 42 — a receita do `custody_copy`, executável
# ---------------------------------------------------------------------------
#
# Até 2026-08-08 a receita não existia em lugar nenhum: nem no schema, nem na
# designação, nem no contrato, nem no protocolo §1.3. O custo foi medido —
# **três juízes reproduziram o digest em 16, 438 e 1440 tentativas, e um não
# conseguiu**. É o mesmo esqueleto do `producer_digest_recipe` do CEO, onde
# receita só em prosa produziu uma acusação de forjadura plausível e falsa.
#
# Publicar em prosa não bastaria: `aviso-em-prosa-nao-previne-erro` já se
# repetiu cinco vezes nesta casa. A receita mora aqui, em código, e é
# **exercitada contra as instâncias reais em disco** — se ela deixar de
# reproduzir, o pacote fica vermelho.
#
# AS DUAS ARMADILHAS, medidas e nomeadas:
#
#   1. `bytes` e `sha256` medem OBJETOS DIFERENTES no caso diretório. O hash
#      inclui os nomes dos arquivos; o `bytes` conta só os conteúdos. Quem
#      confere o tamanho contra o blob hasheado acha divergência sem que nada
#      esteja errado — foi o que consumiu as 1440 tentativas.
#
#   2. O conteúdo é lido em **LF**. A instância de arquivo reproduz
#      `83782d15…` com 2453 bytes normalizados e devolve outro número com os
#      2522 bytes CRLF do checkout Windows. Quem tinha `autocrlf` ligado não
#      conseguia reproduzir por motivo nenhum ligado a conteúdo — e essa é a
#      explicação mais provável para o juiz que não conseguiu. Normalizar
#      dentro da receita torna o digest independente de checkout, que é o que
#      `digest-de-arquivo-nao-e-identidade` manda fazer.
CUSTODY_DIGEST_RECIPE = (
    "departamento-juizes/evals/validate_workflow.py::custody_digest sobre "
    "conteudo normalizado em LF; arquivo hasheia o conteudo, diretorio hasheia "
    "a concatenacao de (caminho relativo POSIX + conteudo) ordenada por caminho"
)


def _conteudo_em_lf(caminho: Path) -> bytes:
    return caminho.read_bytes().replace(b"\r\n", b"\n")


def custody_digest(alvo: Path) -> tuple[str, int]:
    """Devolve `(sha256, bytes)` de uma cópia de custódia, pela receita canônica.

    `bytes` é sempre a soma dos CONTEÚDOS — no caso diretório ele não é o
    tamanho do blob hasheado, e essa diferença é a armadilha 1 do bloco acima.
    """
    if alvo.is_file():
        conteudo = _conteudo_em_lf(alvo)
        return hashlib.sha256(conteudo).hexdigest(), len(conteudo)

    # A receita é a mesma de sempre: sha256 da concatenação, ordenada por caminho
    # relativo POSIX, de (caminho + conteúdo em LF). O que mudou é COMO ela é
    # construída, e o motivo é medido:
    #   - `blob += ...` em bytes é O(n²) — cada volta copiava o acumulado inteiro.
    #     Perfilado em 2026-08-19: 417 s de `tottime` nesta função, 80% dos 523 s
    #     da execução completa. `hash.update()` incremental dá o MESMO digest,
    #     porque hashear a concatenação e concatenar no hash são a mesma operação.
    #   - `relative_to` era calculado duas vezes por arquivo (uma na chave da
    #     ordenação, outra no corpo): 423.613 chamadas. Agora é uma só, guardada
    #     no par que também serve de chave.
    pares = sorted(
        ((p.relative_to(alvo).as_posix(), p) for p in alvo.rglob("*") if p.is_file()),
        key=lambda par: par[0],
    )
    acumulador = hashlib.sha256()
    soma = 0
    for relativo, p in pares:
        conteudo = _conteudo_em_lf(p)
        acumulador.update(relativo.encode("utf-8"))
        acumulador.update(conteudo)
        soma += len(conteudo)
    return acumulador.hexdigest(), soma


def _custodias_em_disco() -> list[tuple[Path, dict]]:
    """Toda `custody_copy` real, com o arquivo que a declara."""
    achadas: list[tuple[Path, dict]] = []

    def anda(obj: Any):
        if isinstance(obj, dict):
            alvo = obj.get("custody_copy")
            if isinstance(alvo, dict) and isinstance(alvo.get("sha256"), str):
                yield alvo
            for v in obj.values():
                yield from anda(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from anda(v)

    for caminho in CEO_ROOT.rglob("*.json"):
        if "__pycache__" in caminho.parts:
            continue
        try:
            texto = caminho.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "custody_copy" not in texto:
            continue
        try:
            doc = json.loads(texto)
        except json.JSONDecodeError:
            continue
        for c in anda(doc):
            achadas.append((caminho, c))
    return achadas


def _resolver_alvo_da_custodia(origem: Path, relativo: str) -> Path | None:
    """Onde o `path` da custódia aterrissa — porque a BASE não é publicada.

    Achado colateral da tarefa 42, medido em 2026-08-08: o `path` é relativo a
    bases DIFERENTES conforme o envelope. Numa `JUDGMENT_REQUEST` de campanha
    ele parte da raiz do `ceo-maestro` (`evals/<campanha>/saida-crua`); num
    `JUDGE_REPORT` de outra campanha ele parte da pasta da própria campanha
    (`evidence/QAM-….json`). O `$defs/artifactRef` não diz qual é, e nenhum
    documento normativo diz também — é a mesma família de omissão que fez três
    juízes gastarem 16, 438 e 1440 tentativas com a receita do digest.

    Enquanto a base não for declarada, resolver é uma busca honesta: tenta a
    pasta do declarante, depois cada ancestral até a raiz do CEO, e devolve a
    primeira que existir. Fica registrado aqui para quem for publicar a base
    saber que ela hoje é ambígua *na prática*, não só no papel.
    """
    base = origem.parent
    while True:
        alvo = (base / relativo)
        if alvo.exists():
            return alvo.resolve()
        if base == CEO_ROOT or CEO_ROOT not in base.parents:
            return None
        base = base.parent


def validate_receita_de_custodia() -> list[str]:
    """A receita publicada reproduz as custódias que ainda existem em disco.

    Custódia cujo alvo sumiu é ignorada de propósito: cópia de custódia é
    registro de um instante, e o alvo pode ter sido movido depois sem que a
    receita esteja errada. O que não pode é o alvo existir e não reproduzir.
    """
    erros: list[str] = []
    conferidas = 0
    for origem, custodia in _custodias_em_disco():
        alvo = _resolver_alvo_da_custodia(origem, custodia["path"])
        if alvo is None:
            continue
        esperado = custodia["sha256"].split(":", 1)[-1]
        obtido, tamanho = custody_digest(alvo)
        conferidas += 1
        if obtido != esperado:
            erros.append(
                f"a receita publicada NÃO reproduz a custódia de "
                f"{custodia['path']} declarada em {origem.name}: esperado "
                f"{esperado[:16]}…, obtido {obtido[:16]}…"
            )
        elif tamanho != custodia.get("bytes"):
            erros.append(
                f"custódia de {custodia['path']} em {origem.name}: o digest "
                f"reproduz mas `bytes` diverge — declarado "
                f"{custodia.get('bytes')}, recomputado {tamanho}"
            )
    if not conferidas:
        erros.append(
            "nenhuma custódia com alvo existente foi conferida — uma receita "
            "que não roda contra nada é prosa com endereço de código"
        )
    return erros


def _autoteste_da_receita_de_custodia() -> list[str]:
    """A receita sabe reprovar, e sabe não reprovar quem cumpriu."""
    import tempfile

    erros = []
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        (raiz / "sub").mkdir()
        (raiz / "b.txt").write_bytes(b"BB\n")
        (raiz / "sub" / "a.txt").write_bytes(b"A\n")

        # ordem por caminho relativo POSIX: "b.txt" < "sub/a.txt"
        esperado = hashlib.sha256(b"b.txt" + b"BB\n" + b"sub/a.txt" + b"A\n").hexdigest()
        obtido, tamanho = custody_digest(raiz)
        if obtido != esperado:
            erros.append("autoteste da custódia: a ordem ou a forma da "
                         "concatenação do caso diretório mudou")
        # "BB\n" = 3 bytes e "A\n" = 2 bytes; a soma dos CONTEÚDOS é 5. O blob
        # hasheado tem 5 + len("b.txt") + len("sub/a.txt") = 19 — e é essa
        # diferença que a armadilha 1 nomeia.
        if tamanho != 5:
            erros.append(f"autoteste da custódia: `bytes` deve somar só os "
                         f"conteúdos (5), veio {tamanho}")
        if tamanho == len(b"b.txt" + b"BB\n" + b"sub/a.txt" + b"A\n"):
            erros.append("autoteste da custódia: `bytes` passou a contar o "
                         "blob hasheado — os nomes não entram nessa conta")

        # A ORDEM tem de ser load-bearing, e provar isso exige uma árvore em
        # que a ordem do `rglob` DIFIRA da lexical. Medido em 2026-08-08: na
        # maioria das formas as duas coincidem, e por isso a primeira prova de
        # mutação desta trava passou verde ao remover o `sorted()` — a ordem
        # existia no código e não era exercitada por nada. A forma que
        # discrimina é um arquivo de raiz que ordena DEPOIS do conteúdo de um
        # subdiretório: `rglob` devolve `["z.txt", "a/b.txt"]` e o lexical é
        # `["a/b.txt", "z.txt"]`.
        with tempfile.TemporaryDirectory() as tmp2:
            fora_de_ordem = Path(tmp2)
            (fora_de_ordem / "a").mkdir()
            (fora_de_ordem / "a" / "b.txt").write_bytes(b"AB\n")
            (fora_de_ordem / "z.txt").write_bytes(b"Z\n")
            por_caminho = hashlib.sha256(
                b"a/b.txt" + b"AB\n" + b"z.txt" + b"Z\n").hexdigest()
            por_varredura = hashlib.sha256(
                b"z.txt" + b"Z\n" + b"a/b.txt" + b"AB\n").hexdigest()
            obtido_ordem, _ = custody_digest(fora_de_ordem)
            if obtido_ordem == por_varredura:
                erros.append(
                    "autoteste da custódia: a concatenação seguiu a ordem da "
                    "varredura do sistema de arquivos, não a ordem do caminho "
                    "— o digest deixa de reproduzir em outra máquina")
            elif obtido_ordem != por_caminho:
                erros.append("autoteste da custódia: a ordem por caminho "
                             "relativo não reproduz o digest esperado")

        # CRLF e LF do mesmo conteúdo têm de dar o MESMO digest — é o que
        # torna a receita independente de checkout.
        crlf = raiz / "c.txt"
        crlf.write_bytes(b"X\r\nY\r\n")
        d_crlf, _ = custody_digest(crlf)
        crlf.write_bytes(b"X\nY\n")
        d_lf, _ = custody_digest(crlf)
        if d_crlf != d_lf:
            erros.append("autoteste da custódia: CRLF e LF do mesmo conteúdo "
                         "dão digests diferentes — a receita voltou a depender "
                         "do checkout, que é o que impediu um juiz de reproduzir")
    return erros


# ---------------------------------------------------------------------------
# TAREFA 66 — a receita existe no schema e falta no ENVELOPE
# ---------------------------------------------------------------------------
#
# A tarefa 42 canonizou a receita no schema, e **no dia seguinte** um juiz real
# gastou OITO tentativas adivinhando o digest de uma designação — porque o
# envelope que ele recebeu não a trazia. É o degrau que
# `aviso-em-prosa-nao-previne-erro` não cobria: a receita estava normativa,
# acessível e **ausente de onde importava**. Quem lê o envelope não lê o schema.
#
# POR QUE NÃO `required` NO SCHEMA, que era a hipótese registrada em 2026-08-08
# ("provavelmente uma trava no emissor, não no schema"): medido por experimento
# em 2026-08-22, pôr `digest_recipe` em `$defs/custodyCopy.required` derruba
# DEZESSEIS casos — catorze aqui e dois no CEO — e **nenhum deles é registro
# congelado**: são todos FIXTURES de envelope válido. Os 52 `custody_copy`
# reais em disco não são validados por schema nenhum hoje. A rota do schema
# custava dezesseis casos e não alcançava o artefato que o juiz efetivamente
# lê. Esta trava varre o DISCO, que é onde o envelope mora.
#
# A DÍVIDA HISTÓRICA VIAJA NOMEADA, no molde da tarefa 94: cada arquivo com a
# sua contagem, o teto DERIVADO da soma, e catraca nos DOIS sentidos —
# ocorrência nova reprova, e dívida que encolheu reprova pedindo para baixar o
# número no mesmo ato. Reescrever os 52 seria falsificar registro; escondê-los
# atrás de um inteiro solto seria a `chave de limites regressível` que a tarefa
# 100 existe para consertar.
#
# LIMITE DECLARADO: a trava alcança envelope GRAVADO. Envelope construído em
# memória e entregue sem passar pelo disco não passa por aqui — e o schema,
# que alcançaria esse caso, foi medido acima como caro e cego ao caso real.
DIVIDA_HISTORICA_SEM_RECEITA: dict[str, int] = {
    # Campanhas de 2026-08-07 e 2026-08-08, TODAS anteriores à descoberta do
    # defeito. Nenhuma ocorrência nasceu depois — e é isso que torna o teto
    # uma dívida fechada, não um orçamento.
    "evals/despacho-real-2026-08-08/01-JUDGE-ASSIGNMENT.json": 1,
    "evals/nucleo-de-comando-r2-2026-08-07/01-JUDGMENT-REQUEST.json": 1,
    "evals/nucleo-de-comando-r2-2026-08-07/03-JUDGE-ASSIGNMENTS/ASSIGN-NUCLEO-R2-EXP-I1.json": 1,
    "evals/nucleo-de-comando-r2-2026-08-07/03-JUDGE-ASSIGNMENTS/ASSIGN-NUCLEO-R2-EXP-I2.json": 1,
    "evals/nucleo-de-comando-r2-2026-08-07/03-JUDGE-ASSIGNMENTS/ASSIGN-NUCLEO-R2-FID-I1.json": 1,
    "evals/nucleo-de-comando-r2-2026-08-07/03-JUDGE-ASSIGNMENTS/ASSIGN-NUCLEO-R2-FID-I2.json": 1,
    "evals/nucleo-de-comando-r2-2026-08-07/03-JUDGE-ASSIGNMENTS/ASSIGN-NUCLEO-R2-PAINEL-I1.json": 1,
    "evals/nucleo-de-comando-r2-2026-08-07/03-JUDGE-ASSIGNMENTS/ASSIGN-NUCLEO-R2-PAINEL-I2.json": 1,
    "evals/nucleo-de-comando-r2-2026-08-07/03-JUDGE-ASSIGNMENTS/ASSIGN-NUCLEO-R2-ROB-I1.json": 1,
    "evals/nucleo-de-comando-r2-2026-08-07/03-JUDGE-ASSIGNMENTS/ASSIGN-NUCLEO-R2-ROB-I2.json": 1,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-04a01f278fe34021a8611f75ad3215c0.panel_record.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-04a01f278fe34021a8611f75ad3215c0.stdout.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-11567ee1a3cd48f0b86f929f79a2d94e.panel_record.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-11567ee1a3cd48f0b86f929f79a2d94e.stdout.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-1fadba774e5346a38a02be38fc7961e8.panel_record.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-1fadba774e5346a38a02be38fc7961e8.stdout.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-37ff47fb8b5f4e48b0500283968eb0fb.panel_record.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-37ff47fb8b5f4e48b0500283968eb0fb.stdout.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-66aad2033bbf46cabd215c5c6de13bcb.panel_record.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-66aad2033bbf46cabd215c5c6de13bcb.stdout.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-8b025aa052c54fc1bbc560c0ec11921a.panel_record.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-8b025aa052c54fc1bbc560c0ec11921a.stdout.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-fdc9771dbe584dd3a6df05357c95edf4.panel_record.json": 3,
    "evals/runtime-worker-observavel-2026-08-07/evidence/R6-JUDGE-fdc9771dbe584dd3a6df05357c95edf4.stdout.json": 3,
}

# DERIVADO, nunca digitado. Digitar o total permite que ele e a lista andem
# separados — e um teto que não sabe de onde veio é um teto que ninguém audita.
TETO_CUSTODIA_SEM_RECEITA = sum(DIVIDA_HISTORICA_SEM_RECEITA.values())


def _comparar_com_divida(encontradas: dict[str, int]) -> list[str]:
    """Catraca nos dois sentidos. PURA — é o que o autoteste exercita.

    Extraída antes de escrever o autoteste, e não depois: escrever o autoteste
    primeiro fez esta casa REIMPLEMENTAR a comparação três vezes num só dia, e
    mutar a função de produção deixava a bateria verde.
    """
    erros: list[str] = []
    for caminho in sorted(set(encontradas) | set(DIVIDA_HISTORICA_SEM_RECEITA)):
        achadas = encontradas.get(caminho, 0)
        prevista = DIVIDA_HISTORICA_SEM_RECEITA.get(caminho, 0)
        if achadas > prevista:
            erros.append(
                f"ENVELOPE NOVO SEM RECEITA: {caminho} tem {achadas} "
                f"`custody_copy` sem `digest_recipe` e a dívida declarada é "
                f"{prevista}. Quem receber este envelope vai adivinhar o "
                f"digest — foi o que custou 8 tentativas a um juiz real em "
                f"2026-08-08, e 16, 438 e 1440 a três outros na véspera. "
                f"Acrescente `custody_copy.digest_recipe` na emissão."
            )
        elif achadas < prevista:
            erros.append(
                f"DÍVIDA ENCOLHEU E O NÚMERO NÃO: {caminho} tem {achadas} "
                f"ocorrência(s) sem receita contra {prevista} declaradas. "
                f"Baixe a entrada em DIVIDA_HISTORICA_SEM_RECEITA no MESMO "
                f"ato — teto que sobra vira orçamento para reincidir."
            )
    return erros


def _custodias_sem_receita_em_disco() -> dict[str, int]:
    """Caminho relativo ao CEO → quantas `custody_copy` sem `digest_recipe`."""
    achadas: dict[str, int] = {}
    for origem, custodia in _custodias_em_disco():
        if "digest_recipe" in custodia:
            continue
        chave = origem.relative_to(CEO_ROOT).as_posix()
        achadas[chave] = achadas.get(chave, 0) + 1
    return achadas


def validate_receita_declarada_no_envelope() -> list[str]:
    """Todo `custody_copy` gravado carrega a receita, salvo dívida nomeada."""
    return _comparar_com_divida(_custodias_sem_receita_em_disco())


def _autoteste_da_receita_no_envelope() -> list[str]:
    """As amostras isolam UMA regra cada — senão um mutante sobrevive porque a
    outra regra pega o caso, que foi exatamente o que aconteceu na tarefa 55.

    As amostras são SINTÉTICAS de propósito: a árvore real está em dia com a
    dívida, logo ela não contém nem o caso "nasceu uma nova" nem o caso "a
    dívida encolheu". Mutante que só a árvore real exercita sobrevive — o
    padrão já custou quatro rodadas nesta casa.
    """
    erros: list[str] = []
    if TETO_CUSTODIA_SEM_RECEITA != sum(DIVIDA_HISTORICA_SEM_RECEITA.values()):
        erros.append("o teto deixou de ser derivado da lista nomeada")

    exemplo = next(iter(sorted(DIVIDA_HISTORICA_SEM_RECEITA)))
    previsto = DIVIDA_HISTORICA_SEM_RECEITA[exemplo]

    # 1. exatamente a dívida declarada — silêncio.
    if _comparar_com_divida(dict(DIVIDA_HISTORICA_SEM_RECEITA)):
        erros.append("autoteste: a dívida declarada, intacta, acusou — a "
                     "trava passaria a reprovar o registro congelado que ela "
                     "existe para preservar")

    # 2. UMA ocorrência nova num arquivo já devedor — reprova.
    cresceu = dict(DIVIDA_HISTORICA_SEM_RECEITA)
    cresceu[exemplo] = previsto + 1
    if not any("ENVELOPE NOVO SEM RECEITA" in e for e in _comparar_com_divida(cresceu)):
        erros.append("autoteste: ocorrência NOVA dentro de arquivo já devedor "
                     "passou — é a rota mais barata para reincidir sem que a "
                     "lista de caminhos mude")

    # 3. arquivo INTEIRAMENTE novo — reprova.
    inedito = dict(DIVIDA_HISTORICA_SEM_RECEITA)
    inedito["evals/campanha-que-nao-existe/99-JUDGE-ASSIGNMENT.json"] = 1
    if not any("ENVELOPE NOVO SEM RECEITA" in e for e in _comparar_com_divida(inedito)):
        erros.append("autoteste: envelope novo, em arquivo novo, sem receita, "
                     "passou — é o defeito de 2026-08-08 podendo repetir")

    # 4. dívida QUITADA sem baixar o número — reprova (a catraca ao contrário).
    quitou = dict(DIVIDA_HISTORICA_SEM_RECEITA)
    quitou.pop(exemplo)
    if not any("DÍVIDA ENCOLHEU" in e for e in _comparar_com_divida(quitou)):
        erros.append("autoteste: consertar um arquivo sem baixar o teto "
                     "passou — o saldo sobrando vira orçamento para reincidir")

    # 5. a árvore VAZIA não é sucesso: seria o detector cego se passando por
    #    conformidade, que já me fez errar a mesma medição três vezes.
    if not _comparar_com_divida({}):
        erros.append("autoteste: nenhuma custódia encontrada foi lida como "
                     "conformidade — zero de detector é suspeita, não aprovação")
    return erros


def run() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    director_schema = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))
    ceo_schema = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))

    cases: list[tuple[str, bool, list[str]]] = []

    cases.append(("pacote, agentes e vínculos externos", True, validate_structure()))
    # T42: a receita do custody_copy, conferida por execucao contra o disco.
    cases.append(("a receita publicada do custody_copy reproduz as custódias em disco", True, validate_receita_de_custodia()))
    cases.append(("a receita do custody_copy sabe reprovar (fixture nos dois sentidos)", True, _autoteste_da_receita_de_custodia()))
    # T66: a receita CHEGA a quem lê o envelope, e a dívida histórica viaja nomeada.
    cases.append(("todo custody_copy gravado carrega a receita (dívida histórica nomeada)", True, validate_receita_declarada_no_envelope()))
    cases.append(("a catraca da dívida de receita sabe reprovar nos dois sentidos", True, _autoteste_da_receita_no_envelope()))
    cases.append(("metadata da gerente e dos três agentes", True, validate_metadata()))
    cases.append(("fonte normativa única e tokens de contrato", True, validate_normative_source()))
    cases.append(("ADR-014, rubrica, exemplos e SKILL são coerentes", True, validate_adr014_normative_consistency()))
    cases.append(("ADR-016: regra de agregação concorda entre schema, protocolo e rubrica", True, validate_adr016_agreement()))
    cases.append(("links internos do pacote resolvem", True, validate_links(PACKAGE_ROOT)))
    cases.append(("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT)))
    cases.append(("todo pacote gerente tem validador que roda a trava global", True, validate_cobertura_de_validadores(STRUCTURE_ROOT)))
    cases.append(("a recusa de digest() dispara e ninguém tem cópia privada do motor", True, validate_trava_de_digest(STRUCTURE_ROOT)))
    cases.append(("nenhuma asserção é verdadeira por construção sobre valor produzido", True, validate_sem_check_tautologico(STRUCTURE_ROOT)))
    cases.append(("nenhum placar de pacote declara total de cadeia como estado corrente", True, validate_placar_nao_declara_cadeia(STRUCTURE_ROOT)))
    cases.append(("a contagem publicada aponta para o digest do instrumento vigente", True, validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)))
    cases.append(("as travas do modulo compartilhado nao estao neutralizadas", True, validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT)))
    cases.append(("toda pendencia declarada nomeia quem responde por ela", True, validate_pendencia_tem_dono(STRUCTURE_ROOT)))
    cases.append(("a fonte normativa confere com o valor declarado em ORIGEM.md", True, validate_fonte_normativa_conferida(STRUCTURE_ROOT)))
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

    assignment_v1 = judge_assignment()
    assignment_v1["rubric_ref"] = "rubrica-corte-v1"
    cases.append(
        (
            "atribuição rejeita rubrica v1",
            False,
            validate_schema(assignment_v1, schema, schema),
        )
    )

    panel_without_level = panel_record()
    panel_without_level.pop("required_level")
    cases.append(
        (
            "PANEL_RECORD exige required_level",
            False,
            validate_schema(panel_without_level, schema, schema),
        )
    )

    fractional_panel = panel_record()
    fractional_panel["minimum_score"] = 9.5
    cases.append(
        (
            "PANEL_RECORD rejeita minimum_score fracionário",
            False,
            validate_schema(fractional_panel, schema, schema),
        )
    )

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

    # ADR-014. Antes da v2 da rubrica, `9` reprovava e este caso era positivo.
    # Agora a faixa 7–9 tem veredito próprio: chamar de REPROVED o que a faixa
    # não reprova é tão fora do contrato quanto chamar de VALIDATED o que ela
    # não valida. Os dois lados da faixa ficam travados.
    reproved = copy.deepcopy(below_cut)
    reproved["verdict"] = "REPROVED"
    reproved["criticisms"] = ["O criterio-04 ficou em 9 pela ótica de experiência."]
    reproved["required_changes"] = ["Tornar a falha observável para quem opera."]
    cases.append(
        ("registro rejeita REPROVED com menor nota 9 (faixa é ACEITO_USO_INTERNO)", False,
         validate_schema(reproved, schema, schema))
    )

    # ACEITO_USO_INTERNO cai no ramo `else` do primeiro allOf, junto com
    # REPROVED: quem não é VALIDATED explica o porquê. É o correto — na faixa
    # 7–9 sempre sobra um risco nomeado, e ele tem de estar escrito.
    aceito_interno = copy.deepcopy(below_cut)
    aceito_interno["verdict"] = "ACEITO_USO_INTERNO"
    aceito_interno["criticisms"] = ["O criterio-04 ficou em 9: sobra risco menor nomeado."]
    aceito_interno["required_changes"] = ["Fechar o risco do criterio-04 para atravessar a 10."]
    cases.append(
        ("registro aceita ACEITO_USO_INTERNO com menor nota 9", True,
         validate_schema(aceito_interno, schema, schema))
    )
    sem_critica = copy.deepcopy(aceito_interno)
    sem_critica["criticisms"] = []
    sem_critica["required_changes"] = []
    cases.append(
        ("registro rejeita ACEITO_USO_INTERNO sem crítica nem mudança pedida", False,
         validate_schema(sem_critica, schema, schema))
    )

    aceito_polido = copy.deepcopy(aceito_interno)
    aceito_polido["scorecard"] = [
        dict(linha, score=7) if linha.get("criterion_id") == "criterio-04" else linha
        for linha in aceito_polido["scorecard"]
    ]
    aceito_polido["minimum_score"] = 7
    cases.append(
        ("registro aceita ACEITO_USO_INTERNO com menor nota 7 (piso da faixa)", True,
         validate_schema(aceito_polido, schema, schema))
    )

    aceito_abaixo = copy.deepcopy(aceito_polido)
    aceito_abaixo["scorecard"] = [
        dict(linha, score=6) if linha.get("criterion_id") == "criterio-04" else linha
        for linha in aceito_abaixo["scorecard"]
    ]
    aceito_abaixo["minimum_score"] = 6
    cases.append(
        ("registro rejeita ACEITO_USO_INTERNO com menor nota 6", False,
         validate_schema(aceito_abaixo, schema, schema))
    )

    aceito_dez = copy.deepcopy(aceito_interno)
    aceito_dez["scorecard"] = [
        dict(linha, score=10) for linha in aceito_dez["scorecard"]
    ]
    aceito_dez["minimum_score"] = 10
    cases.append(
        ("registro rejeita ACEITO_USO_INTERNO com menor nota 10 (é VALIDATED)", False,
         validate_schema(aceito_dez, schema, schema))
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

    gap_reproved = panel_record(
        gaps=[capability_gap()],
        verdict="REPROVED",
    )
    cases.append(
        (
            "lacuna força REPROVED mesmo com mínimo 10",
            True,
            validate_schema(gap_reproved, schema, schema),
        )
    )

    uncovered_record = panel_record(uncovered=["criterio-05"], verdict="VALIDATED")
    cases.append(
        ("registro rejeita VALIDATED com critério sem dona", False,
         validate_schema(uncovered_record, schema, schema))
    )

    uncovered_reproved = panel_record(
        uncovered=["criterio-05"],
        verdict="REPROVED",
    )
    cases.append(
        (
            "critério sem dona força REPROVED mesmo com mínimo 10",
            True,
            validate_schema(uncovered_reproved, schema, schema),
        )
    )

    no_assignments = panel_record(with_assignments=False, verdict="VALIDATED")
    cases.append(
        ("registro rejeita VALIDATED sem registro de emissão (R6)", False,
         validate_schema(no_assignments, schema, schema))
    )

    no_assignments_reproved = panel_record(
        with_assignments=False,
        verdict="REPROVED",
    )
    cases.append(
        (
            "ausência de emissão força REPROVED mesmo com mínimo 10",
            True,
            validate_schema(no_assignments_reproved, schema, schema),
        )
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

    critical_reproved = panel_record(verdict="REPROVED", critical_fail=True)
    cases.append(
        (
            "falha crítica força REPROVED mesmo com mínimo 10",
            True,
            validate_schema(critical_reproved, schema, schema),
        )
    )

    pending_reproved = panel_record(
        verdict="REPROVED",
        blocking_pending_refs=["pending/blocking-001"],
    )
    cases.append(
        (
            "pendência bloqueante força REPROVED mesmo com mínimo 10",
            True,
            validate_schema(pending_reproved, schema, schema),
        )
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

    internal_record = copy.deepcopy(aceito_interno)
    internal_record["required_level"] = "INTERNO"
    cases.append(
        (
            "Diretor aceita DEPARTMENT_JUDGE_REPORT interno com mínimo 9",
            True,
            validate_schema(
                derive_department_judge_report(internal_record),
                director_schema,
                director_schema,
            ),
        )
    )
    cases.append(
        (
            "CEO aceita JUDGE_REPORT interno com mínimo 9",
            True,
            validate_schema(
                derive_judge_report(internal_record),
                ceo_schema,
                ceo_schema,
            ),
        )
    )

    department_report_without_level = derive_department_judge_report(validated_record)
    department_report_without_level.pop("required_level")
    cases.append(
        (
            "Diretor rejeita DEPARTMENT_JUDGE_REPORT sem required_level",
            False,
            validate_schema(
                department_report_without_level,
                director_schema,
                director_schema,
            ),
        )
    )

    judge_report_without_level = derive_judge_report(validated_record)
    judge_report_without_level.pop("required_level")
    cases.append(
        (
            "CEO rejeita JUDGE_REPORT sem required_level",
            False,
            validate_schema(judge_report_without_level, ceo_schema, ceo_schema),
        )
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

    reproved_six = panel_record(
        scores={
            "criterio-01": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-02": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-03": {"agente-julgar-robustez-e-evidencia": 6},
            "criterio-04": {"agente-julgar-experiencia-e-risco": 10},
        },
        verdict="REPROVED",
    )
    reproved_report = derive_department_judge_report(reproved_six)
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
    card_seven = scorecard_lines(
        {
            "criterio-01": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-02": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-03": {"agente-julgar-robustez-e-evidencia": 7},
            "criterio-04": {"agente-julgar-experiencia-e-risco": 10},
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
        # ADR-014: 9 não valida e não reprova — tem faixa própria.
        ("9 em um critério não atravessa para VALIDATED",
         decide_verdict(card_nine) != "VALIDATED"),
        ("9 em um critério cai em ACEITO_USO_INTERNO",
         decide_verdict(card_nine) == "ACEITO_USO_INTERNO"),
        ("7 em um critério cai em ACEITO_USO_INTERNO",
         decide_verdict(card_seven) == "ACEITO_USO_INTERNO"),
        ("6 em um critério reprova",
         decide_verdict(card_six) == "REPROVED"),
        ("PRODUCAO passa somente com VALIDATED",
         verdict_reaches_required_level(decide_verdict(card_ten), "PRODUCAO")
         and not verdict_reaches_required_level(
             decide_verdict(card_nine), "PRODUCAO"
         )),
        ("INTERNO passa com mínimo 9",
         verdict_reaches_required_level(decide_verdict(card_nine), "INTERNO")),
        ("INTERNO passa com mínimo 7",
         verdict_reaches_required_level(decide_verdict(card_seven), "INTERNO")),
        ("INTERNO não passa com mínimo 6",
         not verdict_reaches_required_level(decide_verdict(card_six), "INTERNO")),
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
    ]
    for name, passed in checks:
        cases.append((name, True, [] if passed else ["condição comportamental falhou"]))

    # --- C04 — a fonte normativa confere contra o valor DECLARADO ------------
    # Fora da lista de booleanos de propósito: quando isto reprova, quem lê
    # precisa do valor declarado, do recomputado e da receita. A lista acima só
    # sabe dizer "condição comportamental falhou", e número sem receita é
    # exatamente o que o C04 proíbe.
    cases.append((
        "digest da fonte normativa confere com o declarado em ORIGEM.md",
        True,
        conferir_digest_das_regras(RULES_PATH),
    ))

    # ======================================================================
    # ADR-016 — casos da regra de agregação, do NAO_DISCRIMINADO e das travas
    #
    # Cada trava tem um caso POSITIVO (o artefato conforme é aceito) e um caso
    # NEGATIVO (a violação é rejeitada). O caso negativo é o que sobrevive à
    # mutação: desligar a trava faz o negativo passar, e o validador fica
    # vermelho. Verde no positivo não prova trava nenhuma.
    # ======================================================================

    emissoes_conformes = [
        {
            "assignment_id": assignment_id_for(judge),
            "judge_id": judge,
            "instance": 1,
            "write_path": write_path_for(assignment_id_for(judge)),
            "custody_copy": custody_copy_for(assignment_id_for(judge)),
            "issued_at": "2026-07-26T18:10:00-03:00",
        }
        for judge in AGENT_NAMES
    ]

    # --- ADR-023: evidência simétrica entre instâncias ----------------------
    #
    # Quatro casos, porque a trava tem quatro modos de falhar e o positivo
    # sozinho não prova nenhum deles.

    EVID = "sha256:" + digest("e")
    regra_simetrica = {
        "method": "MENOR",
        "declared_at": "2026-07-26T18:00:00-03:00",
        "rationale": "regra fixada antes de qualquer parecer desta rodada",
        "evidence_symmetry": {
            "battery": ["python evals/validate_workflow.py"],
            "evidence_digest": EVID,
            "declared_at": "2026-07-26T18:00:00-03:00",
        },
    }
    emissoes_simetricas = [
        dict(e, evidence_digest=EVID) for e in emissoes_conformes
    ]

    cases.append(
        ("ADR-023 aceita rodada em que toda emissão carrega o mesmo digest "
         "de evidência", True,
         trava_evidencia_simetrica(regra_simetrica, emissoes_simetricas))
    )
    cases.append(
        ("ADR-023 rejeita emissão sem evidence_digest quando a rodada declara "
         "simetria", False,
         trava_evidencia_simetrica(regra_simetrica, emissoes_conformes))
    )
    cases.append(
        ("ADR-023 rejeita digest divergente entre emissões da mesma rodada",
         False,
         trava_evidencia_simetrica(
             regra_simetrica,
             [emissoes_simetricas[0]]
             + [dict(e, evidence_digest="sha256:" + digest("x"))
                for e in emissoes_simetricas[1:]]))
    )
    cases.append(
        ("ADR-023 rejeita bateria que roda depois do despacho", False,
         trava_evidencia_simetrica(
             dict(regra_simetrica,
                  evidence_symmetry=dict(
                      regra_simetrica["evidence_symmetry"],
                      declared_at="2026-07-26T23:59:00-03:00")),
             emissoes_simetricas))
    )
    cases.append(
        ("ADR-023 não exige nada de rodada que não declara simetria — as "
         "congeladas não declaram", True,
         trava_evidencia_simetrica(
             {"method": "MENOR", "declared_at": "2026-07-26T18:00:00-03:00",
              "rationale": "rodada anterior ao ADR-023"},
             emissoes_conformes))
    )

    # --- ADR-024: isolamento por runtime, não por recusa do agente ----------
    #
    # A trava 1 (write_path exclusivo) e esta parecem a mesma coisa e não são:
    # aquela impede COLISÃO DE ESCRITA, esta impede LEITURA. O caso negativo
    # `raízes aninhadas` é o que separa as duas — ali os write_path continuam
    # exclusivos e a trava 1 passa.

    def com_isolamento(emissao, raiz):
        return dict(emissao, isolation={"mode": "worktree", "root": raiz},
                    write_path=raiz + "/" + emissao["assignment_id"] + "/")

    emissoes_isoladas = [
        com_isolamento(e, "arena/i%d" % n)
        for n, e in enumerate(emissoes_conformes, start=1)
    ]

    cases.append(
        ("ADR-024 aceita rodada com raízes disjuntas e write_path dentro da "
         "própria raiz", True,
         trava_isolamento_por_runtime(emissoes_isoladas))
    )
    cases.append(
        ("ADR-024 rejeita raízes aninhadas — a trava 1 passa e esta pega", False,
         trava_isolamento_por_runtime(
             [emissoes_isoladas[0]]
             + [com_isolamento(e, "arena/i1/dentro%d" % n)
                for n, e in enumerate(emissoes_conformes[1:], start=2)]))
    )
    cases.append(
        ("ADR-024 rejeita write_path fora da própria raiz", False,
         trava_isolamento_por_runtime(
             [dict(emissoes_isoladas[0], write_path="arena/i9/fora/")]
             + emissoes_isoladas[1:]))
    )
    cases.append(
        ("ADR-024 rejeita pasta-compartilhada declarada — declarar a ausência "
         "é auditável e continua não isolando", False,
         trava_isolamento_por_runtime(
             [dict(emissoes_isoladas[0],
                   isolation={"mode": "pasta-compartilhada", "root": "arena/i1"})]
             + emissoes_isoladas[1:]))
    )
    cases.append(
        ("ADR-024 rejeita isolamento parcial na mesma rodada", False,
         trava_isolamento_por_runtime(
             emissoes_isoladas[:-1] + [emissoes_conformes[-1]]))
    )
    cases.append(
        ("ADR-024 não exige nada de rodada que não declara isolamento — as "
         "congeladas não declaram", True,
         trava_isolamento_por_runtime(emissoes_conformes))
    )
    cases.append(
        ("ADR-024 não confunde prefixo de texto com pasta: arena/i1 não contém "
         "arena/i12", True,
         trava_isolamento_por_runtime(
             [com_isolamento(emissoes_conformes[0], "arena/i1"),
              com_isolamento(emissoes_conformes[1], "arena/i12")]))
    )

    # --- TRAVA 1: caminho de escrita exclusivo por emissão ------------------

    cases.append(
        ("trava 1 aceita emissões com caminho exclusivo por emissão", True,
         trava_caminho_exclusivo(emissoes_conformes))
    )

    # A colisão real de 2026-07-31 não foi um caminho malformado: foi o
    # REDESPACHO reusando o mesmo assignment_id e, com ele, o mesmo caminho
    # canônico. Por isso a emissão duplicada aqui é byte a byte igual à
    # primeira: todas as outras checagens da trava passam, e só a de
    # exclusividade pode reprovar. Um fixture com caminho malformado ficaria
    # verde sob a mutação — foi assim que a primeira versão deste caso passou
    # pela razão errada, e a mutação pegou.
    colisao = copy.deepcopy(emissoes_conformes)
    colisao.append(copy.deepcopy(colisao[0]))
    cases.append(
        ("trava 1 rejeita duas emissões no mesmo caminho de escrita", False,
         trava_caminho_exclusivo(colisao))
    )

    caminho_sem_emissao = copy.deepcopy(emissoes_conformes)
    caminho_sem_emissao[0]["write_path"] = "julgamento/handoff-001/a1/canonico/"
    cases.append(
        ("trava 1 rejeita caminho que não deriva do assignment_id", False,
         trava_caminho_exclusivo(caminho_sem_emissao))
    )

    caminho_de_outro_attempt = copy.deepcopy(emissoes_conformes)
    caminho_de_outro_attempt[2]["write_path"] = write_path_for(
        assignment_id_for(AGENT_NAMES[2]), attempt=2
    )
    cases.append(
        ("trava 1 rejeita caminho de outro attempt", False,
         trava_caminho_exclusivo(caminho_de_outro_attempt))
    )

    sem_caminho = copy.deepcopy(emissoes_conformes)
    sem_caminho[0].pop("write_path")
    cases.append(
        ("trava 1 rejeita emissão sem caminho de escrita", False,
         trava_caminho_exclusivo(sem_caminho))
    )

    registro_multi = panel_record(instances_per_lens=2, score_range=(10, 10))
    cases.append(
        ("trava 1 aceita duas instâncias por lente com caminhos distintos", True,
         trava_caminho_exclusivo(registro_multi["assignments"]))
    )

    # --- TRAVA 2: ausência de arquivo não prova morte de executor -----------

    painel_aguardando = [
        {
            "judge_id": "agente-julgar-experiencia-e-risco",
            "lens": "experiencia-e-risco",
            "instance": 1,
            "status": "AGUARDANDO",
            "confidence": "n/a",
            "substrate": "desconhecido",
            "tier": "desconhecido",
            "no_return_evidence": no_return_evidence("NENHUM"),
        }
    ]
    cases.append(
        ("trava 2 aceita AGUARDANDO com arquivo ausente e sem sinal de runtime", True,
         trava_ausencia_nao_prova_morte(painel_aguardando))
    )

    painel_morte_presumida = copy.deepcopy(painel_aguardando)
    painel_morte_presumida[0]["status"] = "SEM_RETORNO"
    cases.append(
        ("trava 2 rejeita SEM_RETORNO concluído só por ausência de arquivo", False,
         trava_ausencia_nao_prova_morte(painel_morte_presumida))
    )

    painel_falho_presumido = copy.deepcopy(painel_aguardando)
    painel_falho_presumido[0]["status"] = "FALHO"
    cases.append(
        ("trava 2 rejeita FALHO concluído só por ausência de arquivo", False,
         trava_ausencia_nao_prova_morte(painel_falho_presumido))
    )

    painel_com_sinal = copy.deepcopy(painel_aguardando)
    painel_com_sinal[0]["status"] = "SEM_RETORNO"
    painel_com_sinal[0]["no_return_evidence"] = no_return_evidence("EXECUTOR_ERROR")
    cases.append(
        ("trava 2 aceita SEM_RETORNO com sinal de runtime observado", True,
         trava_ausencia_nao_prova_morte(painel_com_sinal))
    )

    painel_sem_evidencia = copy.deepcopy(painel_aguardando)
    painel_sem_evidencia[0].pop("no_return_evidence")
    cases.append(
        ("trava 2 rejeita não-entrega sem conferência em disco", False,
         trava_ausencia_nao_prova_morte(painel_sem_evidencia))
    )

    painel_uma_conferencia = copy.deepcopy(painel_aguardando)
    painel_uma_conferencia[0]["no_return_evidence"]["checks"] = [
        painel_uma_conferencia[0]["no_return_evidence"]["checks"][0]
    ]
    cases.append(
        ("trava 2 rejeita não-entrega com uma só conferência", False,
         trava_ausencia_nao_prova_morte(painel_uma_conferencia))
    )

    redespacho = copy.deepcopy(emissoes_conformes)
    redespacho.append(
        {
            "assignment_id": "assignment-agente-julgar-robustez-e-evidencia-reenvio",
            "judge_id": "agente-julgar-robustez-e-evidencia",
            "instance": 1,
            "write_path": "julgamento/handoff-001/a1/assignment-agente-julgar-robustez-e-evidencia-reenvio/",
            "custody_copy": custody_copy_for(
                "assignment-agente-julgar-robustez-e-evidencia-reenvio"
            ),
            "issued_at": "2026-07-26T18:40:00-03:00",
        }
    )
    cases.append(
        ("trava 2 rejeita redespacho da mesma ótica e instância no mesmo attempt", False,
         trava_ausencia_nao_prova_morte([], redespacho))
    )

    # --- TRAVA 3: cópia de custódia com digest antes do despacho ------------

    cases.append(
        ("trava 3 aceita despacho com custódia anterior e digest", True,
         trava_custodia_antes_do_despacho(emissoes_conformes))
    )

    sem_custodia = copy.deepcopy(emissoes_conformes)
    sem_custodia[0].pop("custody_copy")
    cases.append(
        ("trava 3 rejeita despacho sem cópia de custódia", False,
         trava_custodia_antes_do_despacho(sem_custodia))
    )

    custodia_tardia = copy.deepcopy(emissoes_conformes)
    custodia_tardia[1]["custody_copy"]["taken_at"] = "2026-07-26T18:30:00-03:00"
    cases.append(
        ("trava 3 rejeita custódia tomada depois do despacho", False,
         trava_custodia_antes_do_despacho(custodia_tardia))
    )

    custodia_sem_digest = copy.deepcopy(emissoes_conformes)
    custodia_sem_digest[2]["custody_copy"]["sha256"] = "md5:0123456789abcdef"
    cases.append(
        ("trava 3 rejeita custódia sem digest sha256", False,
         trava_custodia_antes_do_despacho(custodia_sem_digest))
    )

    custodia_vazia = copy.deepcopy(emissoes_conformes)
    custodia_vazia[0]["custody_copy"]["bytes"] = 0
    cases.append(
        ("trava 3 rejeita custódia sem bytes verificáveis", False,
         trava_custodia_antes_do_despacho(custodia_vazia))
    )

    # --- A regra de agregação é declarada antes das notas -------------------

    pareceres_em = ["2026-07-26T18:40:00-03:00", "2026-07-26T18:55:00-03:00"]
    cases.append(
        ("regra de agregação declarada antes de todo parecer é aceita", True,
         trava_regra_declarada_antes_das_notas(aggregation_rule(), pareceres_em))
    )
    cases.append(
        ("regra declarada depois do primeiro parecer é rejeitada", False,
         trava_regra_declarada_antes_das_notas(
             aggregation_rule(declared_at="2026-07-26T18:45:00-03:00"), pareceres_em
         ))
    )
    cases.append(
        ("regra com método fora do enum é rejeitada", False,
         trava_regra_declarada_antes_das_notas(
             aggregation_rule(method="MEDIA"), pareceres_em
         ))
    )
    cases.append(
        ("rodada sem regra de agregação é rejeitada", False,
         trava_regra_declarada_antes_das_notas(None, pareceres_em))
    )
    for metodo in METODOS_DE_AGREGACAO:
        cases.append(
            (f"método de agregação {metodo} é declarável", True,
             trava_regra_declarada_antes_das_notas(
                 aggregation_rule(method=metodo), pareceres_em
             ))
        )

    # --- Forma do painel: o que substituiu o antigo maxItems 3 --------------

    cases.append(
        ("painel de 3 lentes × 2 instâncias tem forma válida", True,
         trava_forma_do_painel(registro_multi["panel"], 2))
    )
    painel_torto = copy.deepcopy(registro_multi["panel"])
    painel_torto[1]["instance"] = 1
    cases.append(
        ("painel com instância repetida na mesma lente é rejeitado", False,
         trava_forma_do_painel(painel_torto, 2))
    )
    painel_incompleto = [
        item for item in registro_multi["panel"] if item["instance"] == 1
    ]
    cases.append(
        ("painel sem a segunda instância declarada é rejeitado", False,
         trava_forma_do_painel(painel_incompleto, 2))
    )

    # --- NAO_DISCRIMINADO: veredito legítimo, e caso negativo próprio -------

    faixa_atravessa = decide_verdict(card_six, instance_minimums=[6, 8])
    cases.append(
        ("faixa 6–8 entre instâncias sai como NAO_DISCRIMINADO",
         True, [] if faixa_atravessa == "NAO_DISCRIMINADO" else [f"saiu {faixa_atravessa}"])
    )
    faixa_9_10 = decide_verdict(card_ten, instance_minimums=[9, 10])
    cases.append(
        ("faixa 9–10 entre instâncias também atravessa o corte",
         True, [] if faixa_9_10 == "NAO_DISCRIMINADO" else [f"saiu {faixa_9_10}"])
    )
    faixa_estavel = decide_verdict(card_seven, instance_minimums=[7, 8])
    cases.append(
        ("faixa 7–8, que não atravessa, continua ACEITO_USO_INTERNO",
         True, [] if faixa_estavel == "ACEITO_USO_INTERNO" else [f"saiu {faixa_estavel}"])
    )
    faixa_baixa = decide_verdict(card_six, instance_minimums=[5, 6])
    cases.append(
        ("faixa 5–6, que não atravessa, continua REPROVED",
         True, [] if faixa_baixa == "REPROVED" else [f"saiu {faixa_baixa}"])
    )
    uma_instancia = decide_verdict(card_six, instance_minimums=[6])
    cases.append(
        ("uma instância só nunca produz NAO_DISCRIMINADO",
         True, [] if uma_instancia == "REPROVED" else [f"saiu {uma_instancia}"])
    )
    faixa_com_falha = decide_verdict(
        card_six, instance_minimums=[6, 8], critical_fail=True
    )
    cases.append(
        ("falha crítica manda REPROVED, não empate técnico",
         True, [] if faixa_com_falha == "REPROVED" else [f"saiu {faixa_com_falha}"])
    )
    faixa_com_lacuna = decide_verdict(
        card_six, instance_minimums=[6, 8], uncovered=["criterio-05"]
    )
    cases.append(
        ("lacuna de cobertura manda REPROVED, não empate técnico",
         True, [] if faixa_com_lacuna == "REPROVED" else [f"saiu {faixa_com_lacuna}"])
    )
    cases.append(
        ("NAO_DISCRIMINADO não alcança PRODUCAO", True,
         [] if not verdict_reaches_required_level("NAO_DISCRIMINADO", "PRODUCAO")
         else ["NAO_DISCRIMINADO autorizou produção"])
    )
    cases.append(
        ("NAO_DISCRIMINADO não alcança INTERNO", True,
         [] if not verdict_reaches_required_level("NAO_DISCRIMINADO", "INTERNO")
         else ["NAO_DISCRIMINADO autorizou uso interno"])
    )

    nao_discriminado = panel_record(
        scores={
            "criterio-01": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-02": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-03": {"agente-julgar-robustez-e-evidencia": 6},
            "criterio-04": {"agente-julgar-experiencia-e-risco": 10},
        },
        verdict="NAO_DISCRIMINADO",
        required_level="INTERNO",
        instances_per_lens=2,
        score_range=(6, 8),
    )
    cases.append(
        ("schema aceita PANEL_RECORD NAO_DISCRIMINADO com faixa que atravessa", True,
         validate_schema(nao_discriminado, schema, schema))
    )

    faixa_que_nao_atravessa = copy.deepcopy(nao_discriminado)
    faixa_que_nao_atravessa["minimum_score_range"] = {"lo": 7, "hi": 8}
    cases.append(
        ("schema rejeita NAO_DISCRIMINADO com faixa que não atravessa o corte", False,
         validate_schema(faixa_que_nao_atravessa, schema, schema))
    )

    nao_discriminado_solo = copy.deepcopy(nao_discriminado)
    nao_discriminado_solo["instances_per_lens"] = 1
    nao_discriminado_solo["assignments"] = [
        a for a in nao_discriminado_solo["assignments"] if a["instance"] == 1
    ]
    nao_discriminado_solo["panel"] = [
        p for p in nao_discriminado_solo["panel"] if p["instance"] == 1
    ]
    cases.append(
        ("schema rejeita NAO_DISCRIMINADO com uma instância por lente", False,
         validate_schema(nao_discriminado_solo, schema, schema))
    )

    nao_discriminado_mudo = copy.deepcopy(nao_discriminado)
    nao_discriminado_mudo["criticisms"] = []
    nao_discriminado_mudo["required_changes"] = []
    cases.append(
        ("schema rejeita NAO_DISCRIMINADO mudo", False,
         validate_schema(nao_discriminado_mudo, schema, schema))
    )

    nao_discriminado_com_falha = copy.deepcopy(nao_discriminado)
    nao_discriminado_com_falha["critical_fail"] = True
    cases.append(
        ("schema rejeita NAO_DISCRIMINADO com falha crítica", False,
         validate_schema(nao_discriminado_com_falha, schema, schema))
    )

    aceite_com_faixa_que_atravessa = panel_record(
        scores={
            "criterio-01": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-02": {"agente-julgar-fidelidade-e-contrato": 10},
            "criterio-03": {"agente-julgar-robustez-e-evidencia": 7},
            "criterio-04": {"agente-julgar-experiencia-e-risco": 10},
        },
        verdict="ACEITO_USO_INTERNO",
        required_level="INTERNO",
        instances_per_lens=2,
        score_range=(6, 7),
    )
    cases.append(
        ("schema rejeita ACEITO_USO_INTERNO com faixa que atravessa o corte", False,
         validate_schema(aceite_com_faixa_que_atravessa, schema, schema))
    )

    validado_com_faixa_que_atravessa = panel_record(
        instances_per_lens=2, score_range=(9, 10)
    )
    cases.append(
        ("schema rejeita VALIDATED com faixa 9–10", False,
         validate_schema(validado_com_faixa_que_atravessa, schema, schema))
    )

    sem_faixa = panel_record()
    sem_faixa.pop("minimum_score_range")
    cases.append(
        ("PANEL_RECORD exige minimum_score_range", False,
         validate_schema(sem_faixa, schema, schema))
    )

    sem_regra = panel_record()
    sem_regra.pop("aggregation_rule")
    cases.append(
        ("PANEL_RECORD exige aggregation_rule", False,
         validate_schema(sem_regra, schema, schema))
    )

    regra_invalida = panel_record()
    regra_invalida["aggregation_rule"]["method"] = "MEDIA"
    cases.append(
        ("PANEL_RECORD rejeita método de agregação fora do enum", False,
         validate_schema(regra_invalida, schema, schema))
    )

    atribuicao_sem_caminho = judge_assignment()
    atribuicao_sem_caminho.pop("write_path")
    cases.append(
        ("JUDGE_ASSIGNMENT exige write_path", False,
         validate_schema(atribuicao_sem_caminho, schema, schema))
    )

    atribuicao_sem_custodia = judge_assignment()
    atribuicao_sem_custodia.pop("custody_copy")
    cases.append(
        ("JUDGE_ASSIGNMENT exige custody_copy", False,
         validate_schema(atribuicao_sem_custodia, schema, schema))
    )

    atribuicao_caminho_livre = judge_assignment()
    atribuicao_caminho_livre["write_path"] = "julgamento/canonico/"
    cases.append(
        ("JUDGE_ASSIGNMENT rejeita caminho fora do formato da emissão", False,
         validate_schema(atribuicao_caminho_livre, schema, schema))
    )

    cases.append(
        ("schema aceita JUDGE_ASSIGNMENT de segunda instância", True,
         validate_schema(
             judge_assignment("agente-julgar-robustez-e-evidencia", instance=2),
             schema,
             schema,
         ))
    )

    # Ótica que não devolveu abre lacuna, e lacuna reprova: os três fixtures
    # abaixo diferem SOMENTE no estado e no sinal de runtime, para que o
    # aceite/rejeição prove a trava e não outra condição do envelope.
    def painel_de_nao_entrega(status: str, sinal: str | None) -> dict[str, Any]:
        registro = panel_record(verdict="REPROVED", gaps=[capability_gap()])
        registro["panel"][0]["status"] = status
        if sinal is not None:
            registro["panel"][0]["no_return_evidence"] = no_return_evidence(sinal)
        return registro

    cases.append(
        ("schema aceita AGUARDANDO com runtime_signal NENHUM", True,
         validate_schema(painel_de_nao_entrega("AGUARDANDO", "NENHUM"), schema, schema))
    )
    cases.append(
        ("schema rejeita SEM_RETORNO com runtime_signal NENHUM", False,
         validate_schema(painel_de_nao_entrega("SEM_RETORNO", "NENHUM"), schema, schema))
    )
    cases.append(
        ("schema rejeita FALHO com runtime_signal NENHUM", False,
         validate_schema(painel_de_nao_entrega("FALHO", "NENHUM"), schema, schema))
    )
    cases.append(
        ("schema aceita SEM_RETORNO com EXECUTOR_ERROR observado", True,
         validate_schema(
             painel_de_nao_entrega("SEM_RETORNO", "EXECUTOR_ERROR"), schema, schema
         ))
    )
    cases.append(
        ("schema aceita FALHO com TIMEOUT_DECLARADO observado", True,
         validate_schema(
             painel_de_nao_entrega("FALHO", "TIMEOUT_DECLARADO"), schema, schema
         ))
    )
    cases.append(
        ("schema rejeita AGUARDANDO sem no_return_evidence", False,
         validate_schema(painel_de_nao_entrega("AGUARDANDO", None), schema, schema))
    )
    cases.append(
        ("schema rejeita SEM_RETORNO sem no_return_evidence", False,
         validate_schema(painel_de_nao_entrega("SEM_RETORNO", None), schema, schema))
    )

    # --- fronteira: os envelopes com NAO_DISCRIMINADO servem aos consumidores

    cases.append(
        ("Diretor aceita DEPARTMENT_JUDGE_REPORT NAO_DISCRIMINADO", True,
         validate_schema(
             derive_department_judge_report(nao_discriminado),
             director_schema,
             director_schema,
         ))
    )
    cases.append(
        ("CEO aceita JUDGE_REPORT NAO_DISCRIMINADO", True,
         validate_schema(
             derive_judge_report(nao_discriminado), ceo_schema, ceo_schema
         ))
    )

    relatorio_forjado = derive_department_judge_report(nao_discriminado)
    relatorio_forjado["verdict"] = "ACEITO_USO_INTERNO"
    relatorio_forjado["minimum_score"] = 7
    cases.append(
        ("Diretor rejeita faixa que atravessa carimbada como aceite interno", False,
         validate_schema(relatorio_forjado, director_schema, director_schema))
    )

    relatorio_forjado_ceo = derive_judge_report(nao_discriminado)
    relatorio_forjado_ceo["verdict"] = "ACEITO_USO_INTERNO"
    relatorio_forjado_ceo["minimum_score"] = 7
    cases.append(
        ("CEO rejeita faixa que atravessa carimbada como aceite interno", False,
         validate_schema(relatorio_forjado_ceo, ceo_schema, ceo_schema))
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
    recusar_execucao_fora_da_fonte(STRUCTURE_ROOT)
    sys.exit(run())
