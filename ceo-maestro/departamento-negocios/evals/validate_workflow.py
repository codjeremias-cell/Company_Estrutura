"""Validador determinístico do Departamento de Negócios.

Verifica estrutura, links, metadata, schema, artefatos, fronteiras de autoridade,
score interno, time exato, matriz com o Diretor e regressões do CEO/Diretor.

Uso:
    python validate_workflow.py

No staging, informe:
    CEO_MAESTRO_ROOT=<.../ceo-maestro>
    SKILL_STRUCTURE_ROOT=<.../Estrutura Final de Skills>
"""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = PACKAGE_ROOT / "SKILL.md"
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-negocios.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
AGENTS_ROOT = PACKAGE_ROOT / "agentes"

CEO_ROOT = Path(os.environ.get("CEO_MAESTRO_ROOT", str(PACKAGE_ROOT.parent))).resolve()
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(CEO_ROOT.parent))
).resolve()
CANONICAL_PACKAGE = CEO_ROOT / "departamento-negocios"
DIRECTOR_ROOT = CEO_ROOT / "diretor-de-lentes"
DIRECTOR_SCHEMA_PATH = DIRECTOR_ROOT / "schemas" / "diretor-de-lentes.schema.json"
CEO_SCHEMA_PATH = CEO_ROOT / "schemas" / "ceo-maestro.schema.json"
DIRECTOR_VALIDATOR_PATH = DIRECTOR_ROOT / "evals" / "validate_workflow.py"
CEO_VALIDATOR_PATH = CEO_ROOT / "evals" / "validate_workflow.py"
ADR014_PATH = (
    DIRECTOR_ROOT
    / "departamento-juizes"
    / "references"
    / "adr-014-dois-niveis-de-veredito.md"
)
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        digest,
        is_type,
        json_pointer,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_contract_sections,
        validate_skill_tokens,
        SECOES_CONTRATO_AGENTE,
        TOKENS_SKILL_AGENTE,
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

AGENTS = [
    "agente-estrategia-de-produto",
    "agente-mercado-e-cliente",
    "agente-viabilidade-e-monetizacao",
]
CRITERIA = [f"BIZ-{number:02d}" for number in range(1, 9)]
REQUIRED_LEVELS = {"PRODUCAO", "INTERNO"}
# ADR-016: NAO_DISCRIMINADO e veredito valido do lado externo. Nao alcanca
# nenhum required_level -- entra aqui para que o gate o recuse pelo motivo certo
# ("nao alcanca o nivel") em vez de rejeita-lo como veredito desconhecido.
EXTERNAL_VERDICTS = {
    "VALIDATED",
    "ACEITO_USO_INTERNO",
    "REPROVED",
    "NAO_DISCRIMINADO",
}
CRITERION_OWNER = {
    "BIZ-01": AGENTS[1],
    "BIZ-02": AGENTS[0],
    "BIZ-03": AGENTS[0],
    "BIZ-04": AGENTS[1],
    "BIZ-05": AGENTS[1],
    "BIZ-06": AGENTS[2],
    "BIZ-07": AGENTS[2],
    "BIZ-08": AGENTS[2],
}
MISSION_IDS = {
    AGENTS[0]: "mission-strategy-001",
    AGENTS[1]: "mission-market-001",
    AGENTS[2]: "mission-viability-001",
}
REPORT_IDS = {
    AGENTS[0]: "report-strategy-001",
    AGENTS[1]: "report-market-001",
    AGENTS[2]: "report-viability-001",
}
MISSION_MESSAGES = {
    AGENTS[0]: "message-mission-strategy-001",
    AGENTS[1]: "message-mission-market-001",
    AGENTS[2]: "message-mission-viability-001",
}
REPORT_MESSAGES = {
    AGENTS[0]: "message-report-strategy-001",
    AGENTS[1]: "message-report-market-001",
    AGENTS[2]: "message-report-viability-001",
}




def causal(
    producer: str = "departamento-negocios",
    attempt: int = 1,
    candidate_digest: str = digest("a"),
    message_id: str | None = None,
    causation_message_ids: list[str] | None = None,
    round_number: int = 1,
) -> dict[str, Any]:
    if message_id is None:
        message_id = f"message-{producer}-{attempt}"
    if causation_message_ids is None:
        causation_message_ids = ["message-ceo-001"]
    return {
        "work_item_id": "work-001",
        "front_id": "front-business-001",
        "handoff_id": "handoff-001",
        "message_id": message_id,
        "causation_message_ids": causation_message_ids,
        "contract_id": "contract-business-001",
        "contract_version": 1,
        "contract_digest": digest("c"),
        "candidate_digest": candidate_digest,
        "round": round_number,
        "attempt": attempt,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": digest("d"),
        "created_at": "2026-07-26T12:00:00Z",
    }


def plan_fixture() -> dict[str, Any]:
    assignments = [
        {
            "agent": AGENTS[0],
            "mission_ref": MISSION_IDS[AGENTS[0]],
            "criterion_ids": ["BIZ-02", "BIZ-03"],
            "purpose": "Estratégia, escopo e validação.",
        },
        {
            "agent": AGENTS[1],
            "mission_ref": MISSION_IDS[AGENTS[1]],
            "criterion_ids": ["BIZ-01", "BIZ-04", "BIZ-05"],
            "purpose": "Mercado, clientes e canais.",
        },
        {
            "agent": AGENTS[2],
            "mission_ref": MISSION_IDS[AGENTS[2]],
            "criterion_ids": ["BIZ-06", "BIZ-07", "BIZ-08"],
            "purpose": "Monetização, números e riscos.",
        },
    ]
    return {
        "artifact_type": "BUSINESS_EVALUATION_PLAN",
        "plan_id": "plan-001",
        "causal": causal(
            message_id="message-plan-001",
            causation_message_ids=["message-intake-001"],
        ),
        "executive_mission_ref": "executive-mission-001",
        "intake_ref": "intake-001",
        "team": AGENTS.copy(),
        "assignments": assignments,
        "decision_questions": ["A proposta resolve um problema comprovado?"],
        "required_evidence": ["Dados e fontes rastreáveis por critério."],
        "dependencies": [],
        "risks": ["Dados sensíveis ao tempo podem mudar."],
        "completion_criteria": ["Três relatórios íntegros e score recalculável."],
        "state": "B_PLANNED",
    }


def mission_fixture(agent: str) -> dict[str, Any]:
    assignment = next(item for item in plan_fixture()["assignments"] if item["agent"] == agent)
    return {
        "artifact_type": "BUSINESS_AGENT_MISSION",
        "agent_mission_id": MISSION_IDS[agent],
        "causal": causal(
            message_id=MISSION_MESSAGES[agent],
            causation_message_ids=["message-plan-001"],
        ),
        "plan_ref": "plan-001",
        "assigned_agent": agent,
        "objective": assignment["purpose"],
        "in_scope": ["Critérios atribuídos no plano."],
        "out_of_scope": ["Autoridade dos outros agentes e decisão final."],
        "questions": ["Qual evidência sustenta a conclusão?"],
        "criterion_ids": assignment["criterion_ids"],
        "input_refs": ["candidate-001"],
        "required_evidence": ["Fonte e artefato rastreáveis."],
        "constraints": ["Não inventar dados nem ampliar autoridade."],
        "permissions": {
            "default_policy": "deny",
            "allowed_tools": [],
            "allowed_resources": [],
            "expires_at": "2026-07-27T11:00:00Z",
        },
        "return_to": "departamento-negocios",
    }


def report_fixture(agent: str) -> dict[str, Any]:
    criteria = mission_fixture(agent)["criterion_ids"]
    return {
        "artifact_type": "BUSINESS_AGENT_REPORT",
        "agent_report_id": REPORT_IDS[agent],
        "causal": causal(
            agent,
            message_id=REPORT_MESSAGES[agent],
            causation_message_ids=[MISSION_MESSAGES[agent]],
        ),
        "assignment_ref": MISSION_IDS[agent],
        "agent": agent,
        "status": "COMPLETE",
        "findings": [
            {
                "criterion_id": criterion,
                "classification": "fact",
                "conclusion": "Conclusão sustentada pela evidência indicada.",
                "evidence_refs": [f"evidence-{agent}-{criterion.lower()}"],
            }
            for criterion in criteria
        ],
        "recommended_scores": [
            {
                "criterion_id": criterion,
                "score": 9.5,
                "justification": "Evidência atende ao critério sem lacuna material.",
                "evidence_refs": [f"evidence-{agent}-{criterion.lower()}"],
            }
            for criterion in criteria
        ],
        "assumptions": [],
        "gaps": [],
        "limitations": [],
        "risks": [],
        "dissents": [],
        "confidence": 0.95,
        "return_to": "departamento-negocios",
    }


def scorecard_fixture(score: float = 9.5) -> dict[str, Any]:
    entries = []
    for criterion in CRITERIA:
        owner = CRITERION_OWNER[criterion]
        entry: dict[str, Any] = {
            "criterion_id": criterion,
            "applicable": True,
            "score": score,
            "justification": "Conclusão integrada e rastreável.",
            "evidence_refs": [f"evidence-{owner}-{criterion.lower()}"],
            "source_report_refs": [REPORT_IDS[owner]],
        }
        if score < 9.5:
            entry.update({
                "cause": "Evidência ainda insuficiente.",
                "impact": "Decisão não é segura.",
                "required_change": "Adicionar a evidência faltante.",
                "treatment_owner": AGENTS[0],
                "retest_criterion": "Reexecutar o critério com a nova evidência.",
            })
        entries.append(entry)
    return {
        "artifact_type": "BUSINESS_SCORECARD",
        "scorecard_id": "scorecard-001",
        "causal": causal(
            message_id="message-scorecard-001",
            causation_message_ids=["message-consolidation-001"],
        ),
        "consolidation_ref": "consolidation-001",
        "criteria": entries,
        "calculation_method": "MIN_APPLICABLE_NO_ROUNDING",
        "business_internal_minimum_score": score,
        "limiting_criterion_ids": CRITERIA.copy(),
        "state": "B_READY_FOR_JUDGMENT" if score >= 9.5 else "B_INTERNAL_REWORK",
    }


def fixtures() -> list[dict[str, Any]]:
    reports = [report_fixture(agent) for agent in AGENTS]
    integrated_findings = [
        copy.deepcopy(finding)
        for report in reports
        for finding in report["findings"]
    ]
    consolidated_evidence_refs = sorted({
        evidence_ref
        for report in reports
        for finding in report["findings"]
        for evidence_ref in finding["evidence_refs"]
    })
    intake = {
        "artifact_type": "BUSINESS_INTAKE",
        "intake_id": "intake-001",
        "causal": causal(
            message_id="message-intake-001",
            causation_message_ids=["message-ceo-001"],
        ),
        "executive_mission_ref": "executive-mission-001",
        "proposal_ref": "candidate-001",
        "classifications": [{
            "field": "problem",
            "status": "confirmed",
            "statement": "Problema sustentado por pesquisa.",
            "evidence_refs": ["evidence-problem"],
        }],
        "decision": "PLAN",
        "state": "B_TRIAGED",
    }
    consolidation = {
        "artifact_type": "BUSINESS_CONSOLIDATION",
        "consolidation_id": "consolidation-001",
        "causal": causal(
            message_id="message-consolidation-001",
            causation_message_ids=[REPORT_MESSAGES[agent] for agent in AGENTS],
        ),
        "plan_ref": "plan-001",
        "team": AGENTS.copy(),
        "report_refs": [REPORT_IDS[agent] for agent in AGENTS],
        "integrated_findings": integrated_findings,
        "dependencies": [],
        "dissents": [],
        "evidence_refs": consolidated_evidence_refs,
        "state": "B_CONSOLIDATING",
    }
    gap = {
        "artifact_type": "BUSINESS_GAP_REPORT",
        "gap_report_id": "gap-001",
        "causal": causal(
            message_id="message-gap-001",
            causation_message_ids=["message-scorecard-001"],
        ),
        "scorecard_ref": "scorecard-001",
        "category": "INTERNAL",
        "criterion_ids": ["BIZ-02"],
        "cause": "Evidência incompleta.",
        "impact": "Critério abaixo do corte.",
        "evidence_refs": ["evidence-gap-001"],
        "required_change": "Completar a evidência.",
        "treatment_owner": AGENTS[0],
        "retest_criterion": "Reaplicar BIZ-02.",
        "route": "INTERNAL_REWORK",
    }
    rework = {
        "artifact_type": "BUSINESS_REWORK_ORDER",
        "rework_order_id": "rework-001",
        "causal": causal(
            attempt=2,
            message_id="message-rework-002",
            causation_message_ids=["message-gap-001"],
        ),
        "gap_report_ref": "gap-001",
        "target_agent": AGENTS[0],
        "criterion_ids": ["BIZ-02"],
        "required_changes": ["Completar a evidência."],
        "retest_criteria": ["Reaplicar BIZ-02."],
        "attempt": 2,
        "return_to": "departamento-negocios",
    }
    capability = {
        "artifact_type": "BUSINESS_CAPABILITY_GAP",
        "capability_gap_id": "capability-gap-001",
        "causal": causal(
            message_id="message-capability-gap-001",
            causation_message_ids=["message-intake-001"],
        ),
        "missing_capability": "especialista-fiscal",
        "evidence_refs": ["evidence-capability-001"],
        "impact": "Análise fiscal não pode ser concluída.",
        "fallback_used": False,
        "recovery_condition": "CEO designar capacidade fiscal competente.",
        "return_to": "ceo-maestro",
    }
    judgment = {
        "artifact_type": "BUSINESS_JUDGMENT_PACKAGE",
        "judgment_package_id": "judgment-package-001",
        "causal": causal(
            message_id="message-judgment-package-001",
            causation_message_ids=["message-scorecard-001"],
        ),
        "executive_mission_ref": "executive-mission-001",
        "candidate_ref": "candidate-001",
        "plan_ref": "plan-001",
        "report_refs": [REPORT_IDS[agent] for agent in AGENTS],
        "consolidation_ref": "consolidation-001",
        "scorecard_ref": "scorecard-001",
        "purpose": "STANDARD_JUDGMENT",
        "required_level": "INTERNO",
        "business_internal_minimum_score": 9.5,
        "evidence_refs": consolidated_evidence_refs,
        "dissents": [],
        "risks": [],
        "return_to": "diretor-de-lentes",
        "state": "B_READY_FOR_JUDGMENT",
    }
    matrix = {
        "artifact_type": "MATRIX_EXCHANGE_MESSAGE",
        "matrix_message_id": "matrix-message-001",
        "causal": causal(
            candidate_digest="n/a",
            message_id="message-matrix-001",
            causation_message_ids=["message-judgment-package-001"],
        ),
        "executive_mission_ref": "executive-mission-001",
        "required_level": "INTERNO",
        "sender": "departamento-negocios",
        "recipient": "diretor-de-lentes",
        "topic": "gate-de-julgamento",
        "read_scope": ["candidate-001", "judgment-package-001"],
        "write_scope": ["judgment-request", "judge-report-return"],
        "consolidation_owner": "departamento-negocios",
        "decision_requested": "Abrir o julgamento e devolver o veredito correlacionado.",
        "evidence_refs": ["judgment-package-001"],
        "sent_at": "2026-07-26T12:00:00Z",
    }
    business_return = {
        "artifact_type": "BUSINESS_RETURN",
        "business_return_id": "business-return-001",
        "causal": causal(
            message_id="message-return-001",
            causation_message_ids=["message-intake-001"],
        ),
        "required_level": "INTERNO",
        "state": "B_BLOCKED",
        "reason": "Matriz necessária não autorizada.",
        "evidence_refs": ["executive-mission-001"],
        "next_action": "CEO revisar a missão e incluir o Diretor.",
        "recovery_condition": "Missão válida com matriz autorizada.",
        "return_to": "ceo-maestro",
    }
    return [
        intake,
        plan_fixture(),
        *[mission_fixture(agent) for agent in AGENTS],
        *reports,
        consolidation,
        scorecard_fixture(),
        gap,
        rework,
        capability,
        judgment,
        matrix,
        business_return,
    ]


def scorecard_integrity(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    applicable = [item for item in card["criteria"] if item["applicable"]]
    ids = [item["criterion_id"] for item in card["criteria"]]
    if len(ids) != len(set(ids)):
        errors.append("criterion_id duplicado")
    if len(ids) != 8 or set(ids) != set(CRITERIA):
        errors.append("scorecard não cobre exatamente BIZ-01..BIZ-08")
    for item in card["criteria"]:
        if not item.get("source_report_refs"):
            errors.append(f"{item['criterion_id']}: falta relatório-fonte")
    if not applicable:
        errors.append("nenhum critério aplicável")
        return errors
    actual = min(Decimal(str(item["score"])) for item in applicable)
    declared = Decimal(str(card["business_internal_minimum_score"]))
    if actual != declared:
        errors.append(f"mínimo declarado {declared} difere de {actual}")
    limiting = {
        item["criterion_id"]
        for item in applicable
        if Decimal(str(item["score"])) == actual
    }
    if set(card["limiting_criterion_ids"]) != limiting:
        errors.append("critérios limitantes divergentes")
    ready = card["state"] == "B_READY_FOR_JUDGMENT"
    if ready != (actual >= Decimal("9.5")):
        errors.append("estado não corresponde ao corte")
    return errors


def external_band_for(score: int) -> str:
    if score == 10:
        return "VALIDATED"
    if score >= 7:
        return "ACEITO_USO_INTERNO"
    return "REPROVED"


def external_verdict_for(
    minimum_score: Any,
    *,
    critical_fail: bool = False,
    blocking_pending_refs: list[Any] | None = None,
    minimum_score_range: dict[str, Any] | None = None,
) -> str | None:
    """Mapeia a escala inteira externa ao veredito fixo do ADR-014/ADR-016."""
    if (
        not isinstance(minimum_score, int)
        or isinstance(minimum_score, bool)
        or not 0 <= minimum_score <= 10
    ):
        return None
    if critical_fail or blocking_pending_refs:
        return "REPROVED"
    # ADR-016: faixa que atravessa um corte nao vira veredito -- sai como
    # NAO_DISCRIMINADO, que nao autoriza producao nem uso interno.
    if isinstance(minimum_score_range, dict):
        lo, hi = minimum_score_range.get("lo"), minimum_score_range.get("hi")
        if isinstance(lo, int) and isinstance(hi, int):
            if external_band_for(lo) != external_band_for(hi):
                return "NAO_DISCRIMINADO"
    return external_band_for(minimum_score)


def external_level_reached(verdict: str, required_level: str) -> bool:
    """Aplica a exigência do pedinte sem reutilizar a nota decimal interna."""
    if required_level == "PRODUCAO":
        return verdict == "VALIDATED"
    if required_level == "INTERNO":
        return verdict in {"VALIDATED", "ACEITO_USO_INTERNO"}
    return False


def external_required_target(required_level: str) -> int | None:
    if required_level == "PRODUCAO":
        return 10
    if required_level == "INTERNO":
        return 7
    return None


def external_judgment_gate(
    judge_report: dict[str, Any],
    expected_required_level: str,
) -> list[str]:
    errors: list[str] = []
    if judge_report.get("artifact_type") != "JUDGE_REPORT":
        return ["gate externo exige JUDGE_REPORT"]
    if expected_required_level not in REQUIRED_LEVELS:
        errors.append("required_level executivo ausente ou inválido")
    if judge_report.get("required_level") != expected_required_level:
        errors.append("required_level do parecer diverge da missão")
    verdict = judge_report.get("verdict")
    if verdict not in EXTERNAL_VERDICTS:
        errors.append("veredito externo ausente ou inválido")
    minimum_score = judge_report.get("minimum_score")
    expected_verdict = external_verdict_for(
        minimum_score,
        critical_fail=judge_report.get("critical_fail") is True,
        blocking_pending_refs=judge_report.get("blocking_pending_refs", []),
        minimum_score_range=judge_report.get("minimum_score_range"),
    )
    if expected_verdict is None:
        errors.append("nota externa deve ser inteira entre 0 e 10")
    elif verdict != expected_verdict:
        errors.append("veredito não corresponde à faixa fixa do ADR-014")
    return errors


def external_judge_fixture(
    minimum_score: int,
    required_level: str,
    *,
    critical_fail: bool = False,
    blocking_pending_refs: list[str] | None = None,
    minimum_score_range: dict[str, int] | None = None,
) -> dict[str, Any]:
    pending = [] if blocking_pending_refs is None else blocking_pending_refs
    faixa = (
        {"lo": minimum_score, "hi": minimum_score}
        if minimum_score_range is None
        else minimum_score_range
    )
    return {
        "artifact_type": "JUDGE_REPORT",
        "minimum_score": minimum_score,
        "minimum_score_range": faixa,
        "verdict": external_verdict_for(
            minimum_score,
            critical_fail=critical_fail,
            blocking_pending_refs=pending,
            minimum_score_range=faixa,
        ),
        "required_level": required_level,
        "critical_fail": critical_fail,
        "blocking_pending_refs": pending,
    }


def bundle_integrity(
    intake: dict[str, Any],
    plan: dict[str, Any],
    missions: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    consolidation: dict[str, Any],
    scorecard: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if plan["intake_ref"] != intake["intake_id"]:
        errors.append("plano não referencia o intake real")
    if plan["executive_mission_ref"] != intake["executive_mission_ref"]:
        errors.append("plano diverge da missão executiva do intake")
    if consolidation["plan_ref"] != plan["plan_id"]:
        errors.append("consolidation does not reference the real plan")
    if scorecard is not None and scorecard["consolidation_ref"] != consolidation["consolidation_id"]:
        errors.append("scorecard does not reference the real consolidation")
    if set(plan["team"]) != set(AGENTS) or len(plan["team"]) != 3:
        errors.append("time diferente dos três agentes canônicos")
    if (
        {item["agent"] for item in plan["assignments"]} != set(AGENTS)
        or len(plan["assignments"]) != 3
    ):
        errors.append("atribuições não cobrem os três agentes")
    assigned_criteria = [
        criterion
        for assignment in plan["assignments"]
        for criterion in assignment["criterion_ids"]
    ]
    if len(assigned_criteria) != 8 or set(assigned_criteria) != set(CRITERIA):
        errors.append("atribuições não cobrem BIZ-01..BIZ-08 exatamente uma vez")
    if {item["assigned_agent"] for item in missions} != set(AGENTS) or len(missions) != 3:
        errors.append("missões não cobrem os três agentes")
    if {item["agent"] for item in reports} != set(AGENTS) or len(reports) != 3:
        errors.append("relatórios não cobrem os três agentes")
    mission_by_agent = {item["assigned_agent"]: item for item in missions}
    assignment_by_agent = {item["agent"]: item for item in plan["assignments"]}
    mission_ids = [item["agent_mission_id"] for item in missions]
    if len(mission_ids) != len(set(mission_ids)):
        errors.append("agent_mission_id colidido")
    for agent, mission in mission_by_agent.items():
        if mission["causal"]["producer"] != "departamento-negocios":
            errors.append(f"missao nao produzida por Negocios para {agent}")
        if set(mission["criterion_ids"]) != set(assignment_by_agent[agent]["criterion_ids"]):
            errors.append(f"missão diverge da atribuição para {agent}")
        if assignment_by_agent[agent]["mission_ref"] != mission["agent_mission_id"]:
            errors.append(f"mission_ref do plano diverge para {agent}")
        if mission["plan_ref"] != plan["plan_id"]:
            errors.append(f"plan_ref da missão diverge para {agent}")
        if intake["proposal_ref"] not in mission["input_refs"]:
            errors.append(f"missao nao referencia a proposta real para {agent}")
    report_ids = [item["agent_report_id"] for item in reports]
    if len(report_ids) != len(set(report_ids)):
        errors.append("agent_report_id colidido")
    for report in reports:
        agent = report["agent"]
        if report["assignment_ref"] != mission_by_agent.get(agent, {}).get("agent_mission_id"):
            errors.append(f"assignment_ref divergente para {agent}")
        if report["causal"]["producer"] != agent:
            errors.append(f"produtor divergente para {agent}")
        if report["status"] != "COMPLETE":
            errors.append(f"relatório incompleto para {agent}")
        if report["causal"]["attempt"] != mission_by_agent.get(agent, {}).get("causal", {}).get("attempt"):
            errors.append(f"relatorio obsoleto ou de outra tentativa para {agent}")
        expected_criteria = set(mission_by_agent.get(agent, {}).get("criterion_ids", []))
        finding_criteria = {item["criterion_id"] for item in report["findings"]}
        score_criteria = {item["criterion_id"] for item in report["recommended_scores"]}
        if finding_criteria != expected_criteria or len(report["findings"]) != len(expected_criteria):
            errors.append(f"findings não cobrem a missão de {agent}")
        if score_criteria != expected_criteria or len(report["recommended_scores"]) != len(expected_criteria):
            errors.append(f"scores sugeridos não cobrem a missão de {agent}")
        finding_evidence = {
            item["criterion_id"]: set(item["evidence_refs"])
            for item in report["findings"]
        }
        for recommendation in report["recommended_scores"]:
            criterion_id = recommendation["criterion_id"]
            if not set(recommendation["evidence_refs"]).issubset(
                finding_evidence.get(criterion_id, set())
            ):
                errors.append(
                    f"score sugerido sem evidencia do finding para {agent}/{criterion_id}"
                )
    if (
        set(consolidation["report_refs"])
        != {item["agent_report_id"] for item in reports}
        or len(consolidation["report_refs"]) != 3
    ):
        errors.append("consolidação não referencia exatamente os três relatórios")
    if set(consolidation["team"]) != set(AGENTS) or len(consolidation["team"]) != 3:
        errors.append("consolidacao nao preserva o time canonico")
    if consolidation["causal"]["producer"] != "departamento-negocios":
        errors.append("consolidacao nao produzida por Negocios")
    integrated_ids = [
        item["criterion_id"]
        for item in consolidation["integrated_findings"]
    ]
    if len(integrated_ids) != 8 or set(integrated_ids) != set(CRITERIA):
        errors.append("consolidacao nao integra exatamente BIZ-01..BIZ-08")
    report_evidence_by_criterion: dict[str, set[str]] = {}
    for report in reports:
        for finding in report["findings"]:
            report_evidence_by_criterion.setdefault(
                finding["criterion_id"], set()
            ).update(finding["evidence_refs"])
        for recommendation in report["recommended_scores"]:
            report_evidence_by_criterion.setdefault(
                recommendation["criterion_id"], set()
            ).update(recommendation["evidence_refs"])
    for finding in consolidation["integrated_findings"]:
        criterion_id = finding["criterion_id"]
        if not set(finding["evidence_refs"]).issubset(
            report_evidence_by_criterion.get(criterion_id, set())
        ):
            errors.append(f"finding consolidado sem origem real para {criterion_id}")
    all_report_evidence = set().union(*report_evidence_by_criterion.values())
    if not set(consolidation["evidence_refs"]).issubset(all_report_evidence):
        errors.append("consolidacao contem evidencia sem origem nos relatorios")
    if scorecard is not None:
        errors.extend(scorecard_integrity(scorecard))
        report_by_agent = {item["agent"]: item["agent_report_id"] for item in reports}
        for entry in scorecard["criteria"]:
            expected_report = report_by_agent[CRITERION_OWNER[entry["criterion_id"]]]
            if (
                set(entry["source_report_refs"]) != {expected_report}
                or len(entry["source_report_refs"]) != 1
            ):
                errors.append(f"relatório-fonte divergente para {entry['criterion_id']}")
            if not set(entry["evidence_refs"]).issubset(
                report_evidence_by_criterion.get(entry["criterion_id"], set())
            ):
                errors.append(
                    f"scorecard usa evidencia sem origem para {entry['criterion_id']}"
                )
    keys = [
        "work_item_id",
        "front_id",
        "handoff_id",
        "contract_id",
        "contract_version",
        "contract_digest",
        "candidate_digest",
        "round",
        "attempt",
    ]
    base = tuple(intake["causal"][key] for key in keys)
    correlated = [plan, *missions, *reports, consolidation]
    if scorecard is not None:
        correlated.append(scorecard)
    for artifact in correlated:
        if tuple(artifact["causal"][key] for key in keys) != base:
            errors.append("identidade causal divergente")
    artifacts = [intake, *correlated]
    message_ids = [artifact["causal"]["message_id"] for artifact in artifacts]
    if len(message_ids) != len(set(message_ids)):
        errors.append("message_id causal reutilizado")
    if intake["causal"]["producer"] != "departamento-negocios":
        errors.append("intake nao produzido por Negocios")
    if plan["causal"]["producer"] != "departamento-negocios":
        errors.append("plano nao produzido por Negocios")
    if scorecard is not None and scorecard["causal"]["producer"] != "departamento-negocios":
        errors.append("scorecard nao produzido por Negocios")
    if intake["causal"]["message_id"] not in plan["causal"]["causation_message_ids"]:
        errors.append("plano nao deriva causalmente do intake")
    for agent, mission in mission_by_agent.items():
        if plan["causal"]["message_id"] not in mission["causal"]["causation_message_ids"]:
            errors.append(f"missao nao deriva causalmente do plano para {agent}")
    for report in reports:
        mission_message_id = mission_by_agent[report["agent"]]["causal"]["message_id"]
        if mission_message_id not in report["causal"]["causation_message_ids"]:
            errors.append(
                f"relatorio nao deriva causalmente da missao para {report['agent']}"
            )
    report_message_ids = {
        report["causal"]["message_id"]
        for report in reports
    }
    if not report_message_ids.issubset(
        set(consolidation["causal"]["causation_message_ids"])
    ):
        errors.append("consolidacao nao deriva dos tres relatorios")
    if scorecard is not None and consolidation["causal"]["message_id"] not in (
        scorecard["causal"]["causation_message_ids"]
    ):
        errors.append("scorecard nao deriva causalmente da consolidacao")
    return errors


def judgment_integrity(
    package: dict[str, Any],
    executive_mission: dict[str, Any],
    intake: dict[str, Any],
    plan: dict[str, Any],
    missions: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    consolidation: dict[str, Any],
    scorecard: dict[str, Any],
) -> list[str]:
    errors = bundle_integrity(intake, plan, missions, reports, consolidation, scorecard)
    required_level = executive_mission.get("required_level")
    if required_level not in REQUIRED_LEVELS:
        errors.append("missão executiva sem required_level válido")
    if package.get("required_level") != required_level:
        errors.append("required_level do pacote diverge da missão")
    if package["executive_mission_ref"] != intake["executive_mission_ref"]:
        errors.append("pacote diverge da missão do intake")
    if package["executive_mission_ref"] != plan["executive_mission_ref"]:
        errors.append("pacote diverge da missão do plano")
    if package["candidate_ref"] != intake["proposal_ref"]:
        errors.append("candidate_ref não corresponde ao intake")
    if package["plan_ref"] != plan["plan_id"]:
        errors.append("plan_ref forjado")
    if (
        set(package["report_refs"]) != {item["agent_report_id"] for item in reports}
        or len(package["report_refs"]) != 3
    ):
        errors.append("report_refs não correspondem aos relatórios reais")
    if package["consolidation_ref"] != consolidation["consolidation_id"]:
        errors.append("consolidation_ref forjado")
    if package["scorecard_ref"] != scorecard["scorecard_id"]:
        errors.append("scorecard_ref forjado")
    if Decimal(str(package["business_internal_minimum_score"])) != Decimal(
        str(scorecard["business_internal_minimum_score"])
    ):
        errors.append("score interno do pacote diverge do scorecard")
    if not set(consolidation["evidence_refs"]).issubset(set(package["evidence_refs"])):
        errors.append("pacote não preserva evidências consolidadas")
    keys = [
        "work_item_id",
        "front_id",
        "handoff_id",
        "contract_id",
        "contract_version",
        "contract_digest",
        "candidate_digest",
        "round",
        "attempt",
    ]
    base = tuple(plan["causal"][key] for key in keys)
    if tuple(package["causal"][key] for key in keys) != base:
        errors.append("identidade causal do pacote divergente")
    if package["causal"]["producer"] != "departamento-negocios":
        errors.append("pacote nao produzido por Negocios")
    chain_message_ids = {
        artifact["causal"]["message_id"]
        for artifact in [intake, plan, *missions, *reports, consolidation, scorecard]
    }
    if package["causal"]["message_id"] in chain_message_ids:
        errors.append("message_id do pacote colide com a cadeia")
    if scorecard["causal"]["message_id"] not in package["causal"]["causation_message_ids"]:
        errors.append("pacote nao deriva causalmente do scorecard")
    score = Decimal(str(package["business_internal_minimum_score"]))
    if package["purpose"] == "STANDARD_JUDGMENT":
        if score < Decimal("9.5") or package["state"] != "B_READY_FOR_JUDGMENT":
            errors.append("julgamento padrão não atende ao corte")
    elif package["purpose"] == "LIMITATION_VERIFICATION":
        if score >= Decimal("9.5") or package["state"] != "B_LIMITATION_REVIEW":
            errors.append("revisão de limitação incompatível com score/estado")
        if not package.get("limitation_basis_refs") or not package.get("attempted_remediation_refs"):
            errors.append("revisão de limitação sem base ou remediações")
    else:
        errors.append("finalidade de julgamento desconhecida")
    return errors


def executive_chain_integrity(
    executive_mission: dict[str, Any],
    intake: dict[str, Any],
    plan: dict[str, Any],
    missions: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    mission_id = executive_mission.get("mission_id")
    if intake.get("executive_mission_ref") != mission_id:
        errors.append("intake nao referencia a missao executiva real")
    if plan.get("executive_mission_ref") != mission_id:
        errors.append("plano nao referencia a missao executiva real")
    mission_causal = executive_mission.get("causal", {})
    if mission_causal.get("producer") != "ceo-maestro":
        errors.append("missao executiva nao foi produzida pelo CEO")
    if mission_causal.get("candidate_digest") != "n/a":
        errors.append("missao executiva deve preservar candidate_digest n/a")
    if executive_mission.get("required_level") not in REQUIRED_LEVELS:
        errors.append("missao executiva sem required_level valido")
    if "departamento-negocios" not in executive_mission.get("recipients", []):
        errors.append("Negocios nao e destinatario da missao executiva")
    executive_keys = [
        "work_item_id",
        "front_id",
        "handoff_id",
        "contract_id",
        "contract_version",
        "contract_digest",
        "round",
    ]
    expected = tuple(mission_causal.get(key) for key in executive_keys)
    for artifact in [intake, plan, *missions]:
        if tuple(artifact["causal"].get(key) for key in executive_keys) != expected:
            errors.append("cadeia de Negocios diverge da identidade executiva")
    if mission_causal.get("message_id") not in intake["causal"]["causation_message_ids"]:
        errors.append("intake nao deriva causalmente da missao executiva")
    downstream_message_ids = {
        artifact["causal"]["message_id"]
        for artifact in [intake, plan, *missions]
    }
    if mission_causal.get("message_id") in downstream_message_ids:
        errors.append("message_id executivo reutilizado na cadeia de Negocios")
    return errors


def matrix_authorization(
    message: dict[str, Any],
    mission: dict[str, Any],
    expected_parent_message_id: str | None = None,
) -> list[str]:
    errors: list[str] = []
    matrix = mission.get("matrix_exchange", {})
    mission_causal = mission.get("causal", {})
    if mission_causal.get("producer") != "ceo-maestro":
        errors.append("missão não produzida pelo CEO")
    if message.get("sender") != message.get("causal", {}).get("producer"):
        errors.append("sender diverge do produtor causal")
    if {
        message.get("sender"),
        message.get("recipient"),
    } != {"departamento-negocios", "diretor-de-lentes"}:
        errors.append("remetente e destinatario nao formam os pares da matriz")
    if set(mission.get("recipients", [])) != {"departamento-negocios", "diretor-de-lentes"}:
        errors.append("destinatários não contêm exatamente os pares")
    if matrix.get("allowed") is not True:
        errors.append("matriz não autorizada")
    if message["topic"] not in matrix.get("topics", []):
        errors.append("tópico fora do escopo")
    if not set(message["read_scope"]).issubset(set(matrix.get("read_scope", []))):
        errors.append("leitura fora do escopo")
    if not set(message["write_scope"]).issubset(set(matrix.get("write_scope", []))):
        errors.append("escrita fora do escopo")
    if message["consolidation_owner"] != matrix.get("consolidation_owner"):
        errors.append("dono da consolidação alterado")
    if message["executive_mission_ref"] != mission.get("mission_id"):
        errors.append("referência da missão divergente")
    if message.get("required_level") != mission.get("required_level"):
        errors.append("required_level matricial diverge da missão")
    for key in [
        "work_item_id",
        "front_id",
        "handoff_id",
        "contract_id",
        "contract_version",
        "contract_digest",
        "candidate_digest",
        "round",
        "attempt",
    ]:
        if message["causal"].get(key) != mission_causal.get(key):
            errors.append(f"{key} causal divergente")
    if message["causal"].get("message_id") == mission_causal.get("message_id"):
        errors.append("message_id matricial reutiliza o da missao executiva")
    if (
        expected_parent_message_id is not None
        and expected_parent_message_id
        not in message["causal"].get("causation_message_ids", [])
    ):
        errors.append("mensagem matricial nao deriva do artefato esperado")
    return errors


def business_return_integrity(
    business_return: dict[str, Any],
    executive_mission: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if business_return.get("return_to") != "ceo-maestro":
        errors.append("BUSINESS_RETURN não retorna ao CEO")
    if business_return.get("causal", {}).get("producer") != "departamento-negocios":
        errors.append("BUSINESS_RETURN não foi produzido por Negócios")
    required_level = executive_mission.get("required_level")
    if required_level not in REQUIRED_LEVELS:
        errors.append("missão executiva sem required_level válido")
    if business_return.get("required_level") != required_level:
        errors.append("required_level do BUSINESS_RETURN diverge da missão")
    return errors


def below_cutoff_routing(
    scorecard: dict[str, Any],
    gap_report: dict[str, Any],
    matrix_message: dict[str, Any] | None,
    executive_mission: dict[str, Any],
) -> list[str]:
    errors = scorecard_integrity(scorecard)
    score = Decimal(str(scorecard["business_internal_minimum_score"]))
    if score >= Decimal("9.5"):
        return errors
    if scorecard["state"] != "B_NEEDS_CTO":
        errors.append("score abaixo do corte deve entrar em B_NEEDS_CTO")
    if gap_report.get("scorecard_ref") != scorecard.get("scorecard_id"):
        errors.append("gap não referencia o scorecard")
    if scorecard["causal"]["producer"] != "departamento-negocios":
        errors.append("scorecard abaixo do corte nao produzido por Negocios")
    if gap_report.get("causal", {}).get("producer") != "departamento-negocios":
        errors.append("gap abaixo do corte nao produzido por Negocios")
    gap_keys = [
        "work_item_id",
        "front_id",
        "handoff_id",
        "contract_id",
        "contract_version",
        "contract_digest",
        "candidate_digest",
        "round",
        "attempt",
    ]
    if any(
        gap_report.get("causal", {}).get(key) != scorecard["causal"].get(key)
        for key in gap_keys
    ):
        errors.append("gap diverge da identidade causal do scorecard")
    if scorecard["causal"]["message_id"] not in gap_report.get("causal", {}).get(
        "causation_message_ids", []
    ):
        errors.append("gap nao deriva causalmente do scorecard")
    if gap_report.get("causal", {}).get("message_id") == scorecard["causal"].get("message_id"):
        errors.append("gap reutiliza message_id do scorecard")
    below_ids = {
        item["criterion_id"]
        for item in scorecard["criteria"]
        if item["applicable"] and Decimal(str(item["score"])) < Decimal("9.5")
    }
    if (
        set(gap_report.get("criterion_ids", [])) != below_ids
        or len(gap_report.get("criterion_ids", [])) != len(below_ids)
    ):
        errors.append("gap não cobre todos os critérios abaixo do corte")
    if gap_report.get("route") != "AUTHORIZED_MATRIX":
        errors.append("gap abaixo do corte não foi roteado à matriz")
    if matrix_message is None:
        errors.append("falta mensagem matricial ao Diretor")
        return errors
    errors.extend(
        matrix_authorization(
            matrix_message,
            executive_mission,
            gap_report["causal"]["message_id"],
        )
    )
    required_refs = {gap_report["gap_report_id"], scorecard["scorecard_id"]}
    if not required_refs.issubset(set(matrix_message["evidence_refs"])):
        errors.append("mensagem ao Diretor não carrega gap e scorecard")
    return errors


def rework_integrity(
    rework: dict[str, Any],
    gap_report: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if rework.get("gap_report_ref") != gap_report.get("gap_report_id"):
        errors.append("retrabalho nao referencia o gap real")
    treatment_owner = gap_report.get("treatment_owner")
    if (
        rework.get("target_agent") != treatment_owner
        or treatment_owner not in AGENTS
    ):
        errors.append("agente de retrabalho diverge do dono do tratamento")
    gap_criteria = gap_report.get("criterion_ids", [])
    rework_criteria = rework.get("criterion_ids", [])
    if (
        set(rework_criteria) != set(gap_criteria)
        or len(rework_criteria) != len(gap_criteria)
    ):
        errors.append("criterios de retrabalho divergem do gap")
    if gap_report.get("required_change") not in rework.get("required_changes", []):
        errors.append("retrabalho nao preserva a mudanca exigida pelo gap")
    if gap_report.get("retest_criterion") not in rework.get("retest_criteria", []):
        errors.append("retrabalho nao preserva o criterio de reteste do gap")
    rework_causal = rework.get("causal", {})
    gap_causal = gap_report.get("causal", {})
    if rework.get("attempt") != rework_causal.get("attempt"):
        errors.append("attempt do retrabalho diverge do envelope causal")
    if rework_causal.get("attempt") != gap_causal.get("attempt", 0) + 1:
        errors.append("retrabalho nao avanca exatamente uma tentativa")
    causal_keys = [
        "work_item_id",
        "front_id",
        "handoff_id",
        "contract_id",
        "contract_version",
        "contract_digest",
        "candidate_digest",
        "round",
    ]
    if any(
        rework_causal.get(key) != gap_causal.get(key)
        for key in causal_keys
    ):
        errors.append("retrabalho diverge da identidade causal do gap")
    if rework_causal.get("producer") != "departamento-negocios":
        errors.append("retrabalho nao produzido por Negocios")
    if gap_causal.get("message_id") not in rework_causal.get(
        "causation_message_ids", []
    ):
        errors.append("retrabalho nao deriva causalmente do gap")
    if rework_causal.get("message_id") == gap_causal.get("message_id"):
        errors.append("retrabalho reutiliza message_id do gap")
    return errors


def delegation_authorization(
    missions: list[dict[str, Any]],
    executive_mission: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    executive_permissions = executive_mission.get("permissions", {})
    allowed_scope = set(executive_mission.get("scope_in", []))
    allowed_tools = set(executive_permissions.get("allowed_tools", []))
    allowed_resources = set(executive_permissions.get("allowed_resources", []))
    try:
        executive_expiry = datetime.fromisoformat(
            executive_permissions["expires_at"].replace("Z", "+00:00")
        )
    except (KeyError, TypeError, ValueError):
        return ["permissões executivas inválidas"]
    for mission in missions:
        agent = mission["assigned_agent"]
        permissions = mission.get("permissions", {})
        if permissions.get("default_policy") != "deny":
            errors.append(f"{agent}: política não é deny-by-default")
        if not set(mission.get("in_scope", [])).issubset(allowed_scope):
            errors.append(f"{agent}: escopo ampliado")
        if not set(permissions.get("allowed_tools", [])).issubset(allowed_tools):
            errors.append(f"{agent}: ferramenta não autorizada")
        if not set(permissions.get("allowed_resources", [])).issubset(allowed_resources):
            errors.append(f"{agent}: recurso não autorizado")
        try:
            agent_expiry = datetime.fromisoformat(
                permissions["expires_at"].replace("Z", "+00:00")
            )
            if agent_expiry > executive_expiry:
                errors.append(f"{agent}: permissão vence depois da missão executiva")
        except (KeyError, TypeError, ValueError):
            errors.append(f"{agent}: vencimento inválido")
    return errors


def business_limitation_gate(
    report: dict[str, Any],
    judge_report: dict[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    if judge_report is None or judge_report.get("artifact_type") != "JUDGE_REPORT":
        return ["LIMITATION_REPORT exige JUDGE_REPORT independente"]
    required_level = judge_report.get("required_level")
    errors.extend(external_judgment_gate(judge_report, required_level))
    if external_level_reached(judge_report.get("verdict", ""), required_level):
        errors.append("limitação exige parecer que não alcance o required_level")
    judge_minimum = judge_report.get("minimum_score")
    target = external_required_target(required_level)
    if (
        not isinstance(judge_minimum, int)
        or isinstance(judge_minimum, bool)
        or target is None
        or not 0 <= judge_minimum < target
    ):
        errors.append("limitação exige nota externa inteira abaixo do alvo do nível")
    if report.get("submitted_by") != "departamento-negocios":
        errors.append("limitação de Negócios exige submitted_by canônico")
    causal_header = report.get("causal", {})
    if causal_header.get("producer") != "departamento-negocios":
        errors.append("produtor causal da limitação diverge")
    if report.get("candidate_digest") != judge_report.get("candidate_digest"):
        errors.append("candidato da limitação diverge dos Juízes")
    if report.get("current_minimum_score") != judge_minimum:
        errors.append("nota da limitação não é a nota dos Juízes")
    keys = ["contract_id", "contract_version", "contract_digest", "candidate_digest", "round"]
    if any(causal_header.get(key) != judge_report.get("causal", {}).get(key) for key in keys):
        errors.append("contrato causal da limitação diverge dos Juízes")
    expected_below = {
        item.get("criterion_id"): item.get("score")
        for item in judge_report.get("scorecard", [])
        if item.get("applicable") is True
        and isinstance(item.get("score"), int)
        and not isinstance(item.get("score"), bool)
        and target is not None
        and item["score"] < target
    }
    below_evaluations = report.get("below_cutoff_evaluations", [])
    actual_below = {
        item.get("criterion_id"): item.get("score")
        for item in below_evaluations
    }
    if len(below_evaluations) != len(actual_below):
        errors.append("limitacao contem criterio abaixo do corte duplicado")
    if actual_below != expected_below:
        errors.append("limitação não cobre exatamente os critérios abaixo do corte")
    verification = report.get("independent_verification", {})
    expected_verification = {
        "reviewer": "departamento-juizes",
        "verdict": "VERIFIED_IMPOSSIBILITY",
        "independence_confirmed": True,
        "all_below_cutoff_criteria_covered": True,
    }
    for key, expected in expected_verification.items():
        if verification.get(key) != expected:
            errors.append(f"verificação independente inválida: {key}")
    return errors


def executive_submission_boundary(submission: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if submission.get("submitted_by") != "departamento-negocios":
        errors.append("submissão não é produzida por Negócios")
    if submission.get("causal", {}).get("producer") != "departamento-negocios":
        errors.append("produtor causal da submissão diverge")
    mission = submission.get("executive_mission", {})
    if "departamento-negocios" not in mission.get("recipients", []):
        errors.append("Negócios não é destinatário da missão")
    judge = submission.get("judge_report", {})
    required_level = mission.get("required_level")
    errors.extend(external_judgment_gate(judge, required_level))
    if not external_level_reached(judge.get("verdict", ""), required_level):
        errors.append("veredito não alcança o required_level da missão")
    if submission.get("candidate_digest") != judge.get("candidate_digest"):
        errors.append("candidato diverge do parecer")
    try:
        submitted_at = datetime.fromisoformat(submission["submitted_at"].replace("Z", "+00:00"))
        expires_at = datetime.fromisoformat(judge["expires_at"].replace("Z", "+00:00"))
        if expires_at < submitted_at:
            errors.append("parecer dos Juízes vencido")
    except (KeyError, TypeError, ValueError):
        errors.append("timestamps da submissão/parecer inválidos")
    if submission.get("returned_to") != "ceo-maestro":
        errors.append("submissão não retorna ao CEO")
    return errors


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def resolve_link(source: Path, target: str) -> Path:
    clean = target.split("#", 1)[0]
    local = (source.parent / clean).resolve()
    if local.exists():
        return local
    relative_source = source.relative_to(PACKAGE_ROOT)
    canonical_source = CANONICAL_PACKAGE / relative_source
    return (canonical_source.parent / clean).resolve()


class Results:
    def __init__(self) -> None:
        self.pass_count = 0
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        if condition:
            self.pass_count += 1
            print(f"[PASS] {name}")
        else:
            message = f"{name}: {detail}" if detail else name
            self.failures.append(message)
            print(f"[FAIL] {message}")

    def warn(self, name: str, detail: str) -> None:
        message = f"{name}: {detail}"
        self.warnings.append(message)
        print(f"[WARN] {message}")


def main() -> int:
    results = Results()

    required_files = [
        SKILL_PATH,
        PACKAGE_ROOT / "CONTRATO-DE-COMPROMISSO.md",
        PACKAGE_ROOT / "agents" / "openai.yaml",
        SCHEMA_PATH,
        EVALS_PATH,
        PACKAGE_ROOT / "references" / "workflow-avaliacao-proposta.md",
        PACKAGE_ROOT / "references" / "protocolo-de-handoff.md",
        PACKAGE_ROOT / "references" / "regua-de-avaliacao.md",
        PACKAGE_ROOT / "references" / "comunicacao-matricial-cto.md",
        PACKAGE_ROOT / "references" / "bootstrap.md",
        PACKAGE_ROOT / "references" / "adr-001-rota-vigente-aos-juizes.md",
        PACKAGE_ROOT / "references" / "origem-sintese.md",
        ADR014_PATH,
    ]
    for path in required_files:
        try:
            relative_path = path.relative_to(PACKAGE_ROOT)
        except ValueError:
            relative_path = path.relative_to(CEO_ROOT)
        results.check(f"arquivo existe: {relative_path}", path.is_file())

    actual_agents = sorted(path.name for path in AGENTS_ROOT.iterdir() if path.is_dir())
    results.check("exatamente três diretórios de agentes", actual_agents == sorted(AGENTS), str(actual_agents))
    for agent in AGENTS:
        root = AGENTS_ROOT / agent
        for relative in ["SKILL.md", "CONTRATO-DE-COMPROMISSO.md", "agents/openai.yaml"]:
            results.check(f"{agent}/{relative}", (root / relative).is_file())

    # --- Estrutura normativa dos contratos e SKILL de agente ------------------
    # GUIA, passos 7 e 8. Até 2026-07-27 este validador conferia a existência do
    # arquivo, não a sua anatomia: os três agentes deste pacote usavam uma quarta
    # variante, com zero dos seis tokens e sem a trava anti-bypass declarada. A
    # conferência mora no _compartilhado; a lista do que é obrigatório continua
    # sendo decisão deste pacote.
    for agent in AGENTS:
        root = AGENTS_ROOT / agent
        errors = validate_contract_sections(
            root / "CONTRATO-DE-COMPROMISSO.md", SECOES_CONTRATO_AGENTE, agent)
        results.check(f"{agent}: contrato na anatomia canônica",
                      not errors, " | ".join(errors))
        errors = validate_skill_tokens(
            root / "SKILL.md", TOKENS_SKILL_AGENTE, agent)
        results.check(f"{agent}: SKILL.md com os tokens normativos",
                      not errors, " | ".join(errors))

    for skill_path, expected_name in [
        (SKILL_PATH, "departamento-negocios"),
        *[(AGENTS_ROOT / agent / "SKILL.md", agent) for agent in AGENTS],
    ]:
        frontmatter = read_frontmatter(skill_path)
        results.check(f"frontmatter name: {expected_name}", frontmatter.get("name") == expected_name)
        description = frontmatter.get("description", "")
        results.check(f"description acionável: {expected_name}", len(description) >= 80 and "TODO" not in description)
        metadata = skill_path.parent / "agents" / "openai.yaml"
        metadata_text = metadata.read_text(encoding="utf-8")
        results.check(f"metadata cita ${expected_name}", f"${expected_name}" in metadata_text)

    adr_errors = validate_adr_series(STRUCTURE_ROOT)
    results.check(
        "série global de ADR é única em toda a estrutura",
        not adr_errors,
        " | ".join(adr_errors),
    )
    cobertura_errors = validate_cobertura_de_validadores(STRUCTURE_ROOT)
    results.check(
        "todo pacote gerente tem validador que roda a trava global",
        not cobertura_errors,
        " | ".join(cobertura_errors),
    )
    cobertura_errors = validate_trava_de_digest(STRUCTURE_ROOT)
    results.check(
        "a recusa de digest() dispara e ninguém tem cópia privada do motor",
        not cobertura_errors,
        " | ".join(cobertura_errors),
    )
    cadeia_errors = validate_placar_nao_declara_cadeia(STRUCTURE_ROOT)
    results.check(
        "nenhum placar de pacote declara total de cadeia como estado corrente",
        not cadeia_errors,
        " | ".join(cadeia_errors),
    )
    selo_errors = validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)
    results.check(
        "a contagem publicada aponta para o digest do instrumento vigente",
        not selo_errors,
        " | ".join(selo_errors),
    )
    travas_errors = validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT)
    results.check(
        "as travas do modulo compartilhado nao estao neutralizadas",
        not travas_errors,
        " | ".join(travas_errors),
    )
    dono_errors = validate_pendencia_tem_dono(STRUCTURE_ROOT)
    results.check(
        "toda pendencia declarada nomeia quem responde por ela",
        not dono_errors,
        " | ".join(dono_errors),
    )
    cobertura_errors = validate_sem_check_tautologico(STRUCTURE_ROOT)
    results.check(
        "nenhuma asserção é verdadeira por construção sobre valor produzido",
        not cobertura_errors,
        " | ".join(cobertura_errors),
    )
    cobertura_errors = validate_fonte_normativa_conferida(STRUCTURE_ROOT)
    results.check(
        "a fonte normativa confere com o valor declarado em ORIGEM.md",
        not cobertura_errors,
        " | ".join(cobertura_errors),
    )

    markdown_files = list(PACKAGE_ROOT.rglob("*.md"))
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        results.check(f"sem placeholder: {path.relative_to(PACKAGE_ROOT)}", "TODO" not in text)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#")):
                continue
            resolved = resolve_link(path, target)
            results.check(
                f"link resolve: {path.relative_to(PACKAGE_ROOT)} -> {target}",
                resolved.exists(),
                str(resolved),
            )

    results.check("Regras de Ouro disponíveis", RULES_PATH.is_file(), str(RULES_PATH))
    evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    results.check("15 evals pré-definidos", len(evals.get("cases", [])) == 15)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    results.check("schema draft 2020-12", schema.get("$schema", "").endswith("2020-12/schema"))

    valid_fixtures = fixtures()
    for artifact in valid_fixtures:
        errors = validate_schema(artifact, schema, schema)
        results.check(f"schema aceita {artifact['artifact_type']}", not errors, "; ".join(errors[:3]))

    plan = plan_fixture()
    reports = [report_fixture(agent) for agent in AGENTS]
    missions = [mission_fixture(agent) for agent in AGENTS]
    intake = next(item for item in valid_fixtures if item["artifact_type"] == "BUSINESS_INTAKE")
    consolidation = next(item for item in valid_fixtures if item["artifact_type"] == "BUSINESS_CONSOLIDATION")
    scorecard = scorecard_fixture()
    judgment = next(item for item in valid_fixtures if item["artifact_type"] == "BUSINESS_JUDGMENT_PACKAGE")
    matrix = next(item for item in valid_fixtures if item["artifact_type"] == "MATRIX_EXCHANGE_MESSAGE")
    gap = next(
        item
        for item in valid_fixtures
        if item["artifact_type"] == "BUSINESS_GAP_REPORT"
    )
    rework = next(
        item
        for item in valid_fixtures
        if item["artifact_type"] == "BUSINESS_REWORK_ORDER"
    )
    business_return = next(
        item
        for item in valid_fixtures
        if item["artifact_type"] == "BUSINESS_RETURN"
    )
    executive_mission = {
        "mission_id": "executive-mission-001",
        "causal": causal(
            "ceo-maestro",
            candidate_digest="n/a",
            message_id="message-ceo-001",
            causation_message_ids=["message-user-001"],
        ),
        "required_level": "INTERNO",
        "recipients": ["departamento-negocios", "diretor-de-lentes"],
        "scope_in": ["Critérios atribuídos no plano."],
        "permissions": {
            "default_policy": "deny",
            "allowed_tools": [],
            "allowed_resources": [],
            "expires_at": "2026-07-27T12:00:00Z",
        },
        "matrix_exchange": {
            "allowed": True,
            "topics": ["gate-de-julgamento", "viabilidade-tecnica"],
            "read_scope": ["candidate-001", "judgment-package-001"],
            "write_scope": ["judgment-request", "judge-report-return"],
            "consolidation_owner": "departamento-negocios",
        },
    }

    invalid_cases: list[tuple[str, dict[str, Any]]] = []
    two_agents = copy.deepcopy(plan)
    two_agents["team"].pop()
    invalid_cases.append(("rejeita dois agentes", two_agents))
    four_agents = copy.deepcopy(plan)
    four_agents["team"].append("agente-inventado")
    invalid_cases.append(("rejeita quarto agente", four_agents))
    duplicated = copy.deepcopy(plan)
    duplicated["team"][2] = duplicated["team"][0]
    invalid_cases.append(("rejeita agente duplicado", duplicated))
    uncovered_plan = copy.deepcopy(plan)
    for assignment in uncovered_plan["assignments"]:
        assignment["criterion_ids"] = ["BIZ-01"]
    invalid_cases.append(("rejeita plano sem cobertura BIZ-01..08", uncovered_plan))
    wrong_mission_producer = mission_fixture(AGENTS[0])
    wrong_mission_producer["causal"]["producer"] = "ceo-maestro"
    invalid_cases.append(("rejeita missão de agente produzida pelo CEO", wrong_mission_producer))
    wrong_report_producer = report_fixture(AGENTS[0])
    wrong_report_producer["causal"]["producer"] = "departamento-negocios"
    invalid_cases.append(("rejeita gerente fabricando relatório", wrong_report_producer))
    incomplete_consolidation = copy.deepcopy(consolidation)
    incomplete_consolidation["report_refs"].pop()
    invalid_cases.append(("rejeita consolidação com dois relatórios", incomplete_consolidation))
    partial_scorecard = scorecard_fixture()
    partial_scorecard["criteria"] = partial_scorecard["criteria"][:1]
    partial_scorecard["limiting_criterion_ids"] = ["BIZ-01"]
    invalid_cases.append(("rejeita scorecard sem os oito critérios", partial_scorecard))
    rounded = scorecard_fixture(9.49)
    rounded["state"] = "B_READY_FOR_JUDGMENT"
    invalid_cases.append(("rejeita 9,49 como pronto", rounded))
    missing_treatment = scorecard_fixture(9.49)
    for key in ["cause", "impact", "required_change", "treatment_owner", "retest_criterion"]:
        missing_treatment["criteria"][0].pop(key)
    invalid_cases.append(("rejeita nota baixa sem tratamento", missing_treatment))
    judgment_below = copy.deepcopy(judgment)
    judgment_below["business_internal_minimum_score"] = 9.49
    invalid_cases.append(("rejeita pacote aos Juízes abaixo do corte", judgment_below))
    judgment_without_level = copy.deepcopy(judgment)
    judgment_without_level.pop("required_level")
    invalid_cases.append(
        ("rejeita pacote de julgamento sem required_level", judgment_without_level)
    )
    bad_matrix = copy.deepcopy(matrix)
    bad_matrix["causal"]["producer"] = "diretor-de-lentes"
    invalid_cases.append(("rejeita remetente diferente do produtor", bad_matrix))
    matrix_without_level = copy.deepcopy(matrix)
    matrix_without_level.pop("required_level")
    invalid_cases.append(
        ("rejeita mensagem matricial sem required_level", matrix_without_level)
    )
    same_party = copy.deepcopy(matrix)
    same_party["recipient"] = "departamento-negocios"
    invalid_cases.append(("rejeita matriz para si próprio", same_party))
    cap_fallback = next(item for item in valid_fixtures if item["artifact_type"] == "BUSINESS_CAPABILITY_GAP")
    cap_fallback = copy.deepcopy(cap_fallback)
    cap_fallback["fallback_used"] = True
    invalid_cases.append(("rejeita fallback de capacidade", cap_fallback))
    return_without_level = copy.deepcopy(business_return)
    return_without_level.pop("required_level")
    invalid_cases.append(
        ("rejeita BUSINESS_RETURN sem required_level", return_without_level)
    )
    forbidden = {"artifact_type": "JUDGE_REPORT"}
    invalid_cases.append(("rejeita JUDGE_REPORT produzido localmente", forbidden))
    forbidden = {"artifact_type": "EXECUTIVE_DECISION"}
    invalid_cases.append(("rejeita EXECUTIVE_DECISION produzido localmente", forbidden))
    forbidden = {"artifact_type": "EXCEPTION_REQUEST"}
    invalid_cases.append(("rejeita EXCEPTION_REQUEST produzido localmente", forbidden))

    for name, artifact in invalid_cases:
        errors = validate_schema(artifact, schema, schema)
        results.check(name, bool(errors), "artefato inválido foi aceito")

    results.check("scorecard íntegro", not scorecard_integrity(scorecard))
    score_mismatch = scorecard_fixture()
    score_mismatch["business_internal_minimum_score"] = 9.7
    results.check("rejeita mínimo interno divergente", bool(scorecard_integrity(score_mismatch)))
    duplicate_criterion = scorecard_fixture()
    duplicate_criterion["criteria"][1]["criterion_id"] = "BIZ-01"
    results.check("rejeita critério duplicado", bool(scorecard_integrity(duplicate_criterion)))
    partial_integrity = scorecard_fixture()
    partial_integrity["criteria"] = partial_integrity["criteria"][:1]
    partial_integrity["limiting_criterion_ids"] = ["BIZ-01"]
    results.check("integridade rejeita cobertura parcial", bool(scorecard_integrity(partial_integrity)))

    results.check(
        "bundle íntegro com três agentes",
        not bundle_integrity(intake, plan, missions, reports, consolidation, scorecard),
    )
    wrong_bundle = copy.deepcopy(reports)
    wrong_bundle[0]["assignment_ref"] = MISSION_IDS[AGENTS[1]]
    results.check(
        "rejeita relatório ligado à missão errada",
        bool(bundle_integrity(intake, plan, missions, wrong_bundle, consolidation, scorecard)),
    )
    changed_candidate = copy.deepcopy(reports)
    changed_candidate[0]["causal"]["candidate_digest"] = digest("f")
    results.check(
        "rejeita digest divergente",
        bool(bundle_integrity(intake, plan, missions, changed_candidate, consolidation, scorecard)),
    )
    wrong_mission_scope = copy.deepcopy(missions)
    wrong_mission_scope[0]["criterion_ids"] = ["BIZ-01"]
    results.check(
        "rejeita missão divergente da atribuição",
        bool(bundle_integrity(intake, plan, wrong_mission_scope, reports, consolidation, scorecard)),
    )
    partial_report = copy.deepcopy(reports)
    partial_report[1]["findings"] = partial_report[1]["findings"][:1]
    partial_report[1]["recommended_scores"] = partial_report[1]["recommended_scores"][:1]
    results.check(
        "rejeita relatório sem cobertura da missão",
        bool(bundle_integrity(intake, plan, missions, partial_report, consolidation, scorecard)),
    )
    forged_score_source = copy.deepcopy(scorecard)
    forged_score_source["criteria"][0]["source_report_refs"] = ["report-forged-001"]
    results.check(
        "rejeita score sem relatório-fonte real",
        bool(bundle_integrity(intake, plan, missions, reports, consolidation, forged_score_source)),
    )
    results.check(
        "pacote padrão correlacionado",
        not judgment_integrity(
            judgment,
            executive_mission,
            intake,
            plan,
            missions,
            reports,
            consolidation,
            scorecard,
        ),
    )
    colliding_plan = copy.deepcopy(plan)
    colliding_missions = copy.deepcopy(missions)
    colliding_reports = copy.deepcopy(reports)
    collision_id = colliding_missions[0]["agent_mission_id"]
    colliding_missions[1]["agent_mission_id"] = collision_id
    colliding_plan["assignments"][1]["mission_ref"] = collision_id
    colliding_reports[1]["assignment_ref"] = collision_id
    results.check(
        "rejeita colisao de agent_mission_id mesmo com refs coordenadas",
        bool(
            bundle_integrity(
                intake,
                colliding_plan,
                colliding_missions,
                colliding_reports,
                consolidation,
                scorecard,
            )
        ),
    )
    forged_lineage_plan = copy.deepcopy(plan)
    forged_lineage_plan["intake_ref"] = "intake-forged-001"
    forged_lineage_plan["assignments"][0]["mission_ref"] = "mission-forged-001"
    forged_lineage_missions = copy.deepcopy(missions)
    forged_lineage_missions[0]["plan_ref"] = "plan-forged-001"
    results.check(
        "rejeita refs forjadas entre intake plano atribuicao e missao",
        bool(
            bundle_integrity(
                intake,
                forged_lineage_plan,
                forged_lineage_missions,
                reports,
                consolidation,
                scorecard,
            )
        ),
    )
    duplicate_finding_report = report_fixture(AGENTS[0])
    duplicate_finding_report["findings"][1] = copy.deepcopy(
        duplicate_finding_report["findings"][0]
    )
    results.check(
        "schema rejeita findings duplicados ou conflitantes",
        bool(validate_schema(duplicate_finding_report, schema, schema)),
    )
    duplicate_score_report = report_fixture(AGENTS[0])
    duplicate_score_report["recommended_scores"][1] = copy.deepcopy(
        duplicate_score_report["recommended_scores"][0]
    )
    duplicate_score_report["recommended_scores"][1]["score"] = 0.0
    results.check(
        "schema rejeita recommended_scores duplicados ou conflitantes",
        bool(validate_schema(duplicate_score_report, schema, schema)),
    )
    forged_consolidation = copy.deepcopy(consolidation)
    forged_consolidation["plan_ref"] = "plan-forged-001"
    results.check(
        "rejeita consolidation.plan_ref forjado",
        bool(
            bundle_integrity(
                intake,
                plan,
                missions,
                reports,
                forged_consolidation,
                scorecard,
            )
        ),
    )
    forged_consolidation_ref = copy.deepcopy(scorecard)
    forged_consolidation_ref["consolidation_ref"] = "consolidation-forged-001"
    results.check(
        "rejeita scorecard.consolidation_ref forjado",
        bool(
            bundle_integrity(
                intake,
                plan,
                missions,
                reports,
                consolidation,
                forged_consolidation_ref,
            )
        ),
    )
    divergent_intake = copy.deepcopy(intake)
    divergent_intake["causal"]["contract_id"] = "contract-forged-001"
    divergent_intake["causal"]["candidate_digest"] = digest("f")
    divergent_intake["causal"]["round"] = 2
    results.check(
        "rejeita identidade causal divergente desde o intake",
        bool(
            bundle_integrity(
                divergent_intake,
                plan,
                missions,
                reports,
                consolidation,
                scorecard,
            )
        ),
    )
    invented_evidence_scorecard = copy.deepcopy(scorecard)
    invented_evidence_scorecard["criteria"][0]["evidence_refs"] = [
        "evidence-invented-001"
    ]
    results.check(
        "rejeita evidencia de scorecard ausente dos relatorios",
        bool(
            bundle_integrity(
                intake,
                plan,
                missions,
                reports,
                consolidation,
                invented_evidence_scorecard,
            )
        ),
    )
    stale_report = copy.deepcopy(reports)
    stale_report[0]["causal"]["attempt"] = 2
    results.check(
        "rejeita relatorio de tentativa divergente",
        bool(
            bundle_integrity(
                intake,
                plan,
                missions,
                stale_report,
                consolidation,
                scorecard,
            )
        ),
    )
    causal_collision_plan = copy.deepcopy(plan)
    causal_collision_plan["causal"]["message_id"] = intake["causal"]["message_id"]
    results.check(
        "rejeita message_id causal reutilizado",
        bool(
            bundle_integrity(
                intake,
                causal_collision_plan,
                missions,
                reports,
                consolidation,
                scorecard,
            )
        ),
    )
    forged_judgment = copy.deepcopy(judgment)
    forged_judgment["report_refs"] = ["forged-1", "forged-2", "forged-3"]
    forged_judgment["consolidation_ref"] = "forged-consolidation"
    forged_judgment["scorecard_ref"] = "forged-scorecard"
    forged_judgment["candidate_ref"] = "forged-candidate"
    results.check(
        "rejeita pacote de julgamento com referências forjadas",
        bool(
            judgment_integrity(
                forged_judgment,
                executive_mission,
                intake,
                plan,
                missions,
                reports,
                consolidation,
                scorecard,
            )
        ),
    )
    uncaused_judgment = copy.deepcopy(judgment)
    uncaused_judgment["causal"]["causation_message_ids"] = [
        "message-unrelated-001"
    ]
    results.check(
        "rejeita pacote de julgamento sem causalidade do scorecard",
        bool(
            judgment_integrity(
                uncaused_judgment,
                executive_mission,
                intake,
                plan,
                missions,
                reports,
                consolidation,
                scorecard,
            )
        ),
    )
    limitation_scorecard = scorecard_fixture(9.3)
    limitation_package = copy.deepcopy(judgment)
    limitation_package["purpose"] = "LIMITATION_VERIFICATION"
    limitation_package["state"] = "B_LIMITATION_REVIEW"
    limitation_package["business_internal_minimum_score"] = 9.3
    limitation_package["limitation_basis_refs"] = ["evidence-objective-limit-001"]
    limitation_package["attempted_remediation_refs"] = ["evidence-remediation-001"]
    limitation_schema_errors = validate_schema(limitation_package, schema, schema)
    results.check(
        "schema aceita pacote de verificação abaixo do corte",
        not limitation_schema_errors,
        "; ".join(limitation_schema_errors[:3]),
    )
    results.check(
        "pacote de limitação correlacionado",
        not judgment_integrity(
            limitation_package,
            executive_mission,
            intake,
            plan,
            missions,
            reports,
            consolidation,
            limitation_scorecard,
        ),
    )

    results.check(
        "delegações preservam escopo e permissões do CEO",
        not delegation_authorization(missions, executive_mission),
    )
    results.check(
        "cadeia de Negocios preserva contrato e rodada do CEO",
        not executive_chain_integrity(
            executive_mission,
            intake,
            plan,
            missions,
        ),
    )
    missing_level_mission = copy.deepcopy(executive_mission)
    missing_level_mission.pop("required_level")
    results.check(
        "rejeita EXECUTIVE_MISSION sem required_level",
        bool(
            executive_chain_integrity(
                missing_level_mission,
                intake,
                plan,
                missions,
            )
        ),
    )
    reset_round_intake = copy.deepcopy(intake)
    reset_round_plan = copy.deepcopy(plan)
    reset_round_missions = copy.deepcopy(missions)
    reset_round_intake["causal"]["round"] = 1
    reset_round_plan["causal"]["round"] = 1
    for agent_mission in reset_round_missions:
        agent_mission["causal"]["round"] = 1
    executive_round_two = copy.deepcopy(executive_mission)
    executive_round_two["causal"]["round"] = 2
    results.check(
        "rejeita reinicio da rodada global do CEO",
        bool(
            executive_chain_integrity(
                executive_round_two,
                reset_round_intake,
                reset_round_plan,
                reset_round_missions,
            )
        ),
    )
    widened_permissions = copy.deepcopy(missions)
    widened_permissions[0]["permissions"]["allowed_tools"] = ["external-publisher"]
    results.check(
        "rejeita ferramenta ou efeito externo não autorizado",
        bool(delegation_authorization(widened_permissions, executive_mission)),
    )
    widened_scope = copy.deepcopy(missions)
    widened_scope[0]["in_scope"] = ["Alterar orçamento vinculante."]
    results.check(
        "rejeita ampliação de escopo na delegação",
        bool(delegation_authorization(widened_scope, executive_mission)),
    )
    results.check("matriz autorizada aceita", not matrix_authorization(matrix, executive_mission))
    results.check(
        "BUSINESS_RETURN preserva required_level",
        not business_return_integrity(business_return, executive_mission),
    )
    divergent_return_level = copy.deepcopy(business_return)
    divergent_return_level["required_level"] = "PRODUCAO"
    results.check(
        "rejeita BUSINESS_RETURN com required_level divergente",
        bool(business_return_integrity(divergent_return_level, executive_mission)),
    )
    divergent_package_level = copy.deepcopy(judgment)
    divergent_package_level["required_level"] = "PRODUCAO"
    results.check(
        "rejeita pacote com required_level divergente",
        bool(
            judgment_integrity(
                divergent_package_level,
                executive_mission,
                intake,
                plan,
                missions,
                reports,
                consolidation,
                scorecard,
            )
        ),
    )
    divergent_matrix_level = copy.deepcopy(matrix)
    divergent_matrix_level["required_level"] = "PRODUCAO"
    results.check(
        "rejeita matriz com required_level divergente",
        bool(matrix_authorization(divergent_matrix_level, executive_mission)),
    )
    no_matrix = copy.deepcopy(executive_mission)
    no_matrix["matrix_exchange"]["allowed"] = False
    results.check("matriz fechada bloqueia", bool(matrix_authorization(matrix, no_matrix)))
    one_recipient = copy.deepcopy(executive_mission)
    one_recipient["recipients"] = ["departamento-negocios"]
    results.check("um destinatário bloqueia matriz", bool(matrix_authorization(matrix, one_recipient)))
    wrong_topic = copy.deepcopy(matrix)
    wrong_topic["topic"] = "arquitetura-nao-autorizada"
    results.check("tópico fora da missão bloqueia", bool(matrix_authorization(wrong_topic, executive_mission)))
    wrong_owner = copy.deepcopy(matrix)
    wrong_owner["consolidation_owner"] = "diretor-de-lentes"
    results.check("mudança do consolidador bloqueia", bool(matrix_authorization(wrong_owner, executive_mission)))

    boundary_expectations = [
        (6, "INTERNO", False),
        (6, "PRODUCAO", False),
        (7, "INTERNO", True),
        (7, "PRODUCAO", False),
        (9, "INTERNO", True),
        (9, "PRODUCAO", False),
        (10, "INTERNO", True),
        (10, "PRODUCAO", True),
    ]
    for external_score, required_level, should_pass in boundary_expectations:
        judge_report = external_judge_fixture(external_score, required_level)
        label = f"{external_score}/{required_level}"
        results.check(
            f"ADR-014 aceita parecer coerente na borda {label}",
            not external_judgment_gate(judge_report, required_level),
        )
        results.check(
            f"ADR-014 aplica o nível exigido na borda {label}",
            external_level_reached(judge_report["verdict"], required_level)
            is should_pass,
        )

    fractional_external = external_judge_fixture(9, "INTERNO")
    fractional_external["minimum_score"] = 9.5
    results.check(
        "rejeita nota fracionária no gate externo",
        bool(external_judgment_gate(fractional_external, "INTERNO")),
    )
    missing_external_level = external_judge_fixture(9, "INTERNO")
    missing_external_level.pop("required_level")
    results.check(
        "rejeita parecer sem required_level",
        bool(external_judgment_gate(missing_external_level, "INTERNO")),
    )
    divergent_external_level = external_judge_fixture(9, "INTERNO")
    results.check(
        "rejeita parecer com required_level divergente",
        bool(external_judgment_gate(divergent_external_level, "PRODUCAO")),
    )
    invalid_external_verdict = external_judge_fixture(7, "INTERNO")
    invalid_external_verdict["verdict"] = "VALIDATED"
    results.check(
        "rejeita veredito incompatível com a faixa externa",
        bool(external_judgment_gate(invalid_external_verdict, "INTERNO")),
    )
    critical_external = external_judge_fixture(10, "INTERNO", critical_fail=True)
    results.check(
        "falha crítica força REPROVED",
        not external_judgment_gate(critical_external, "INTERNO")
        and not external_level_reached(
            critical_external["verdict"],
            critical_external["required_level"],
        ),
    )
    pending_external = external_judge_fixture(
        10,
        "INTERNO",
        blocking_pending_refs=["pending-001"],
    )
    results.check(
        "pendência bloqueante força REPROVED",
        not external_judgment_gate(pending_external, "INTERNO")
        and not external_level_reached(
            pending_external["verdict"],
            pending_external["required_level"],
        ),
    )

    # --- ADR-016: NAO_DISCRIMINADO chega coerente e nao autoriza nada -------
    undiscriminated_external = external_judge_fixture(
        6, "INTERNO", minimum_score_range={"lo": 6, "hi": 8}
    )
    results.check(
        "ADR-016 aceita parecer NAO_DISCRIMINADO coerente com a faixa medida",
        undiscriminated_external["verdict"] == "NAO_DISCRIMINADO"
        and not external_judgment_gate(undiscriminated_external, "INTERNO"),
    )
    results.check(
        "ADR-016 nega uso interno e producao ao NAO_DISCRIMINADO",
        not external_level_reached(
            undiscriminated_external["verdict"], "INTERNO"
        )
        and not external_level_reached(
            undiscriminated_external["verdict"], "PRODUCAO"
        ),
    )
    forged_undiscriminated = external_judge_fixture(
        7, "INTERNO", minimum_score_range={"lo": 6, "hi": 7}
    )
    forged_undiscriminated["verdict"] = "ACEITO_USO_INTERNO"
    results.check(
        "ADR-016 rejeita faixa que atravessa carimbada como aceite interno",
        bool(external_judgment_gate(forged_undiscriminated, "INTERNO")),
    )
    stable_external = external_judge_fixture(
        7, "INTERNO", minimum_score_range={"lo": 7, "hi": 9}
    )
    results.check(
        "ADR-016 preserva o aceite interno quando a faixa nao atravessa",
        stable_external["verdict"] == "ACEITO_USO_INTERNO"
        and not external_judgment_gate(stable_external, "INTERNO")
        and external_level_reached(stable_external["verdict"], "INTERNO"),
    )

    below_scorecard = scorecard_fixture(9.2)
    below_scorecard["state"] = "B_NEEDS_CTO"
    routed_gap = copy.deepcopy(
        next(item for item in valid_fixtures if item["artifact_type"] == "BUSINESS_GAP_REPORT")
    )
    routed_gap["criterion_ids"] = CRITERIA.copy()
    routed_gap["route"] = "AUTHORIZED_MATRIX"
    routed_matrix = copy.deepcopy(matrix)
    routed_matrix["topic"] = "viabilidade-tecnica"
    routed_matrix["evidence_refs"] = ["gap-001", "scorecard-001"]
    routed_matrix["causal"]["causation_message_ids"] = ["message-gap-001"]
    results.check(
        "todo score abaixo do corte é repassado ao Diretor",
        not below_cutoff_routing(
            below_scorecard,
            routed_gap,
            routed_matrix,
            executive_mission,
        ),
    )
    results.check(
        "score abaixo do corte bloqueia sem matriz",
        bool(
            below_cutoff_routing(
                below_scorecard,
                routed_gap,
                None,
                executive_mission,
            )
        ),
    )

    results.check(
        "retrabalho preserva gap agente criterios tentativa e contrato",
        not rework_integrity(rework, gap),
    )
    rework_forged_gap_ref = copy.deepcopy(rework)
    rework_forged_gap_ref["gap_report_ref"] = "gap-forged-001"
    results.check(
        "rejeita retrabalho com gap_report_ref forjado",
        bool(rework_integrity(rework_forged_gap_ref, gap)),
    )
    rework_wrong_agent = copy.deepcopy(rework)
    rework_wrong_agent["target_agent"] = AGENTS[1]
    results.check(
        "rejeita retrabalho com agente incompatível",
        bool(rework_integrity(rework_wrong_agent, gap)),
    )
    rework_wrong_criteria = copy.deepcopy(rework)
    rework_wrong_criteria["criterion_ids"] = ["BIZ-01"]
    results.check(
        "rejeita retrabalho com critérios incompatíveis",
        bool(rework_integrity(rework_wrong_criteria, gap)),
    )
    rework_wrong_attempt = copy.deepcopy(rework)
    rework_wrong_attempt["attempt"] = 3
    results.check(
        "rejeita attempt divergente do causal no retrabalho",
        bool(rework_integrity(rework_wrong_attempt, gap)),
    )
    rework_wrong_contract = copy.deepcopy(rework)
    rework_wrong_contract["causal"]["contract_digest"] = digest("f")
    results.check(
        "rejeita retrabalho com contrato divergente do gap",
        bool(rework_integrity(rework_wrong_contract, gap)),
    )
    rework_wrong_parent = copy.deepcopy(rework)
    rework_wrong_parent["causal"]["causation_message_ids"] = [
        "message-unrelated-001"
    ]
    results.check(
        "rejeita retrabalho sem causalidade do gap",
        bool(rework_integrity(rework_wrong_parent, gap)),
    )
    rework_wrong_change = copy.deepcopy(rework)
    rework_wrong_change["required_changes"] = ["Mudança não relacionada."]
    results.check(
        "rejeita retrabalho sem mudança exigida pelo gap",
        bool(rework_integrity(rework_wrong_change, gap)),
    )
    rework_wrong_retest = copy.deepcopy(rework)
    rework_wrong_retest["retest_criteria"] = ["Reteste não relacionado."]
    results.check(
        "rejeita retrabalho sem reteste exigido pelo gap",
        bool(rework_integrity(rework_wrong_retest, gap)),
    )

    divergent_gap = copy.deepcopy(routed_gap)
    divergent_gap["causal"]["candidate_digest"] = digest("f")
    results.check(
        "rejeita gap de outro candidato antes de rotear ao Diretor",
        bool(
            below_cutoff_routing(
                below_scorecard,
                divergent_gap,
                routed_matrix,
                executive_mission,
            )
        ),
    )
    matrix_wrong_parent = copy.deepcopy(routed_matrix)
    matrix_wrong_parent["causal"]["causation_message_ids"] = [
        "message-unrelated-001"
    ]
    results.check(
        "rejeita mensagem ao Diretor sem causalidade do gap",
        bool(
            below_cutoff_routing(
                below_scorecard,
                routed_gap,
                matrix_wrong_parent,
                executive_mission,
            )
        ),
    )

    if DIRECTOR_SCHEMA_PATH.is_file():
        director_schema = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))
        director_errors = validate_schema(matrix, director_schema, director_schema)
        results.check("MATRIX_EXCHANGE_MESSAGE aceita pelo schema do Diretor", not director_errors, "; ".join(director_errors[:3]))
        if DIRECTOR_VALIDATOR_PATH.is_file():
            spec = importlib.util.spec_from_file_location(
                "director_validator_for_business",
                DIRECTOR_VALIDATOR_PATH,
            )
            if spec is None or spec.loader is None:
                results.check("validador semântico do Diretor carregável", False)
            else:
                director_validator = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(director_validator)
                semantic_errors = director_validator.validate_matrix_exchange_message(
                    matrix,
                    executive_mission,
                    director_schema,
                )
                results.check(
                    "MATRIX_EXCHANGE_MESSAGE aceita pela semântica do Diretor",
                    not semantic_errors,
                    "; ".join(semantic_errors[:3]),
                )
        else:
            results.check("validador semântico do Diretor disponível", False, str(DIRECTOR_VALIDATOR_PATH))
    else:
        results.check("schema do Diretor disponível", False, str(DIRECTOR_SCHEMA_PATH))

    if CEO_SCHEMA_PATH.is_file():
        ceo_schema = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))
        if CEO_VALIDATOR_PATH.is_file():
            ceo_spec = importlib.util.spec_from_file_location(
                "ceo_validator_for_business",
                CEO_VALIDATOR_PATH,
            )
            if ceo_spec is None or ceo_spec.loader is None:
                results.check("validador semântico do CEO carregável", False)
            else:
                ceo_validator = importlib.util.module_from_spec(ceo_spec)
                ceo_spec.loader.exec_module(ceo_validator)

                # ADR-014: o judge_report e dos JUIZES, e VALIDATED passou a
                # exigir 10 em tudo. A regua INTERNA de Negocios (9,5) e outra
                # e nao foi tocada -- ver ADR-014, "nao decidido aqui".
                normal_judge = ceo_validator.judge_report([10, 10, 10])
                business_submission = ceo_validator.submission(normal_judge)
                business_submission["submitted_by"] = "departamento-negocios"
                business_submission["causal"]["producer"] = "departamento-negocios"
                submission_schema_errors = validate_schema(
                    business_submission,
                    ceo_schema,
                    ceo_schema,
                )
                submission_semantic_errors = ceo_validator.validate_submission(
                    business_submission
                )
                submission_boundary_errors = executive_submission_boundary(
                    business_submission
                )
                results.check(
                    "EXECUTIVE_SUBMISSION de Negócios aceita pelo schema do CEO",
                    not submission_schema_errors,
                    "; ".join(submission_schema_errors[:3]),
                )
                results.check(
                    "EXECUTIVE_SUBMISSION de Negócios aceita pela semântica do CEO",
                    not submission_semantic_errors and not submission_boundary_errors,
                    "; ".join((submission_semantic_errors + submission_boundary_errors)[:3]),
                )

                unauthorized_submission = copy.deepcopy(business_submission)
                unauthorized_submission["executive_mission"]["recipients"] = [
                    "diretor-de-lentes"
                ]
                results.check(
                    "rejeita submissão quando Negócios não é destinatário",
                    bool(
                        ceo_validator.validate_submission(unauthorized_submission)
                        + executive_submission_boundary(unauthorized_submission)
                    ),
                )
                expired_submission = copy.deepcopy(business_submission)
                expired_submission["judge_report"]["expires_at"] = (
                    "2026-07-26T12:36:00-03:00"
                )
                results.check(
                    "rejeita submissão com parecer vencido",
                    bool(executive_submission_boundary(expired_submission)),
                )
                divergent_submission = copy.deepcopy(business_submission)
                divergent_submission["candidate_digest"] = digest("f")
                results.check(
                    "rejeita submissão de outro candidato",
                    bool(
                        ceo_validator.validate_submission(divergent_submission)
                        + executive_submission_boundary(divergent_submission)
                    ),
                )

                below_judge = ceo_validator.judge_report([9, 10, 10], "PRODUCAO")
                business_limitation = ceo_validator.limitation_report(below_judge)
                business_limitation["submitted_by"] = "departamento-negocios"
                business_limitation["causal"]["producer"] = "departamento-negocios"
                limitation_schema_errors = validate_schema(
                    business_limitation,
                    ceo_schema,
                    ceo_schema,
                )
                limitation_semantic_errors = ceo_validator.validate_limitation_report(
                    business_limitation,
                    below_judge,
                )
                limitation_gate_errors = business_limitation_gate(
                    business_limitation,
                    below_judge,
                )
                results.check(
                    "LIMITATION_REPORT de Negócios aceita pelo schema do CEO",
                    not limitation_schema_errors,
                    "; ".join(limitation_schema_errors[:3]),
                )
                results.check(
                    "LIMITATION_REPORT de Negócios aceita pela semântica do CEO",
                    not limitation_semantic_errors and not limitation_gate_errors,
                    "; ".join((limitation_semantic_errors + limitation_gate_errors)[:3]),
                )
                results.check(
                    "score interno isolado não abre LIMITATION_REPORT",
                    bool(business_limitation_gate(business_limitation, None)),
                )
                duplicated_limitation = copy.deepcopy(business_limitation)
                duplicated_limitation["below_cutoff_evaluations"].append(
                    copy.deepcopy(
                        duplicated_limitation["below_cutoff_evaluations"][0]
                    )
                )
                results.check(
                    "rejeita criterio duplicado no LIMITATION_REPORT",
                    bool(
                        business_limitation_gate(
                            duplicated_limitation,
                            below_judge,
                        )
                    ),
                )
                mismatched_limitation = copy.deepcopy(business_limitation)
                mismatched_limitation["current_minimum_score"] = 8
                results.check(
                    "rejeita limitação divergente do JUDGE_REPORT",
                    bool(
                        ceo_validator.validate_limitation_report(
                            mismatched_limitation,
                            below_judge,
                        )
                        + business_limitation_gate(
                            mismatched_limitation,
                            below_judge,
                        )
                    ),
                )
        else:
            results.check("validador semântico do CEO disponível", False, str(CEO_VALIDATOR_PATH))
    else:
        results.check("schema do CEO disponível", False, str(CEO_SCHEMA_PATH))

    regression_scripts = [
        CEO_ROOT / "evals" / "validate_workflow.py",
        DIRECTOR_ROOT / "evals" / "validate_workflow.py",
    ]
    for script in regression_scripts:
        if not script.is_file():
            results.check(f"regressão disponível: {script}", False)
            continue
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(script.parent),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            check=False,
        )
        combined = completed.stdout + completed.stderr
        if completed.returncode == 0:
            results.check(f"regressão passa: {script.parent.parent.name}", True)
        elif (
            script == CEO_ROOT / "evals" / "validate_workflow.py"
            and "adr-003-conformidade-sem-nota.md" in combined
            and "departamento-negocios" not in combined
            and "Resultado: 31/32 casos passaram." in combined
        ):
            results.warn(
                "baseline externo do CEO permanece 31/32",
                "links preexistentes de adr-003-conformidade-sem-nota.md; "
                "não pertencem ao pacote de Negócios",
            )
        else:
            # Excerto cortado em limite de LINHA, nunca de caractere.
            # `combined[-500:]` cortava no meio de uma palavra, e a primeira
            # linha do excerto saía sem sentido — medido em 2026-08-19, o
            # detalhe deste mesmo caso chegava ao placar como
            # `[FAIL] regressão passa: ceo-maestro: tado`, onde `tado` era o
            # rabo de uma palavra qualquer. Quem lê o FAIL precisa do fim da
            # saída do subprocesso, e o fim de uma saída são linhas inteiras:
            # é lá que moram o `Resultado: N/M` e as linhas de erro.
            results.check(
                f"regressão passa: {script.parent.parent.name}",
                False,
                "\n".join(combined.rstrip().splitlines()[-12:]),
            )

    total = results.pass_count + len(results.failures)
    print(
        f"\nRESULTADO: {results.pass_count}/{total} PASS; "
        f"{len(results.failures)} FAIL; {len(results.warnings)} WARN"
    )
    for warning in results.warnings:
        print(f" ! {warning}")
    if results.failures:
        for failure in results.failures:
            print(f" - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    # T55: recusa medir a Estrutura a partir do runtime, onde a raiz
    # resolve para .claude/skills e as skills do Catalogo viram pacotes.
    recusar_execucao_fora_da_fonte(STRUCTURE_ROOT)
    raise SystemExit(main())
