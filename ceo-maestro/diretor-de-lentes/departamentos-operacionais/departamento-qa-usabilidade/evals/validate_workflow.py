"""Validador determinístico do Departamento de QA e Usabilidade.

Valida estrutura, metadata, links, schema, fixtures positivas/negativas,
propriedade exclusiva, consolidação, proveniência do legado e a fronteira real
com o schema do Diretor de Lentes.

Uso:
  python evals/validate_workflow.py

Em staging, definir SKILL_STRUCTURE_ROOT para a Estrutura Final canônica.
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
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-qa-usabilidade.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
ORIGIN_PATH = PACKAGE_ROOT / "references" / "origem-migracao.md"
AGENTS_ROOT = PACKAGE_ROOT / "agentes"

OPERATIONS_ROOT = PACKAGE_ROOT.parent
DIRECTOR_ROOT_LOCAL = OPERATIONS_ROOT.parent
CEO_ROOT_LOCAL = DIRECTOR_ROOT_LOCAL.parent
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(CEO_ROOT_LOCAL.parent))
).resolve()
CANONICAL_PACKAGE_ROOT = (
    STRUCTURE_ROOT
    / "ceo-maestro"
    / "diretor-de-lentes"
    / "departamentos-operacionais"
    / "departamento-qa-usabilidade"
)
DIRECTOR_SCHEMA_PATH = (
    STRUCTURE_ROOT
    / "ceo-maestro"
    / "diretor-de-lentes"
    / "schemas"
    / "diretor-de-lentes.schema.json"
)
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"
LEGACY_ROOT = (
    STRUCTURE_ROOT.parent
    / "SKILL - Nova formula"
    / "maestro"
    / "comite-de-lentes"
    / "lente-qa-usabilidade"
)

DEPARTMENT = "departamento-qa-usabilidade"
AGENTS = [
    "agente-testes-funcionais",
    "agente-testes-nao-funcionais",
    "agente-usabilidade-e-acessibilidade",
]
CAPABILITY = {
    "agente-testes-funcionais": "FUNCTIONAL",
    "agente-testes-nao-funcionais": "NON_FUNCTIONAL",
    "agente-usabilidade-e-acessibilidade": "USABILITY_A11Y",
}
RULES_LINK_DEPARTMENT = "../../../../regras-de-ouro/REGRAS-DE-OURO.md"
RULES_LINK_AGENT = "../../../../../../regras-de-ouro/REGRAS-DE-OURO.md"
FORBIDDEN_RESULT_KEYS = {
    "score",
    "nota",
    "notas",
    "minimum_score",
    "scorecard",
    "cut_score",
    "validated",
    "exception_request",
}
EDGE_DIMENSIONS = {
    "happy-path",
    "validation",
    "permissions",
    "state",
    "scale",
    "failure",
    "data",
    "ux",
    "recovery",
    "concurrency",
    "security",
    "integration",
}

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        collect_property_names,
        digest,
        json_pointer,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_agents_folder,
        validate_contract_sections,
        validate_frontmatter,
        validate_openai_yaml,
        validate_required_files,
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


LOCAL_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
DIRECTOR_SCHEMA = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))
CANDIDATE = digest("a")
CONTRACT = digest("b")
PRODUCER = digest("c")
POLICY = digest("d")
NOW = "2026-07-26T20:00:00-03:00"


# ---------------------------------------------------------------------------
# Regras recalculadas
# ---------------------------------------------------------------------------

def derive_state(
    *,
    mode: str,
    passed: int,
    failed: int,
    skipped: int,
    unverified: int,
    missing: int,
    blocked: bool = False,
) -> tuple[str, str]:
    """Deriva estado e recomendação; nunca lê um campo autoafirmado."""
    if blocked:
        return "BLOCKED", "BLOCKED"
    if failed > 0:
        return "FAILED", "REWORK_REQUIRED"
    if mode == "CONSULTA" or skipped + unverified + missing > 0 or passed == 0:
        return "PARTIAL", "NOT_PROVEN"
    return "PROVED", "READY_FOR_JUDGMENT"


def owner_for(property_kind: str) -> str:
    owners = {
        "functional": "agente-testes-funcionais",
        "non_functional": "agente-testes-nao-funcionais",
        "usability_a11y": "agente-usabilidade-e-acessibilidade",
    }
    return owners[property_kind]


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [item["status"] for item in results]
    return {
        "pass": statuses.count("PASS"),
        "fail": statuses.count("FAIL"),
        "skip": statuses.count("SKIP"),
        "unverified": statuses.count("UNVERIFIED"),
        "critical_fail": any(
            item["status"] == "FAIL" and item["severity"] == "critical"
            for item in results
        ),
    }


def artifact_digest(value: Any) -> str:
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def authenticated_artifact_ref(value: dict[str, Any], id_field: str) -> str:
    """Cria referência conteúdo-endereçada sem ampliar o schema consumidor."""
    return f"{value[id_field]}@{artifact_digest(value)}"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def causal(
    producer: str = DEPARTMENT,
    *,
    message: str = "message-qa-001",
    handoff: str = "handoff-qa-001",
    causes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "work_item_id": "work-001",
        "department_mission_id": "mission-qa-001",
        "handoff_id": handoff,
        "message_id": message,
        "causation_message_ids": causes or ["message-director-001"],
        "contract_id": "contract-qa-001",
        "contract_version": 1,
        "contract_digest": CONTRACT,
        "candidate_digest": CANDIDATE,
        "round": 1,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": PRODUCER,
        "created_at": NOW,
    }


def execution_policy(active: bool = False) -> dict[str, Any]:
    if active:
        return {
            "active_testing_allowed": True,
            "authorization_ref": "authorization-001",
            "authorized_by": "owner-test-environment",
            "issued_at": NOW,
            "expires_at": "2026-07-27T20:00:00-03:00",
            "status": "active",
            "targets": ["candidate-a"],
            "environments": ["isolated-test"],
            "window": "2026-07-26T20:00:00-03:00/2026-07-27T00:00:00-03:00",
            "allowed_tools": ["test-runner"],
            "allowed_actions": ["execute-listed-cases"],
            "prohibited_actions": ["production", "real-notification"],
            "rate_volume_concurrency_limits": ["max-concurrency=2"],
            "data_classes_allowed": ["synthetic"],
            "test_accounts": ["qa-auto-001"],
            "evidence_handling": ["redact-secrets"],
            "cleanup_plan_ref": "cleanup-plan-001",
            "recovery_plan_ref": "recovery-plan-001",
            "stop_conditions": ["authorization-revoked", "unexpected-effect"],
            "emergency_contact": "owner-test-environment",
            "recheck_interval": "PT15M",
        }
    return {
        "active_testing_allowed": False,
        "authorization_ref": "n/a",
        "authorized_by": "n/a",
        "issued_at": "n/a",
        "expires_at": "n/a",
        "status": "not_required",
        "targets": [],
        "environments": [],
        "window": "n/a",
        "allowed_tools": [],
        "allowed_actions": [],
        "prohibited_actions": ["active-testing"],
        "rate_volume_concurrency_limits": [],
        "data_classes_allowed": [],
        "test_accounts": [],
        "evidence_handling": ["read-only-analysis"],
        "cleanup_plan_ref": "n/a",
        "recovery_plan_ref": "n/a",
        "stop_conditions": ["active-action-requested"],
        "emergency_contact": "n/a",
        "recheck_interval": "n/a",
    }


def plan(mode: str = "ATUA") -> dict[str, Any]:
    criteria = [
        {
            "criterion_id": "criterion-values",
            "observable": "Totais do dashboard reconciliam com a fonte.",
            "priority": "critical",
            "profiles": ["DASHBOARD_VISUALIZATION", "DATA_DATABASE"],
            "risk_ids": ["risk-wrong-values"],
            "applicable": True,
            "owner_agent": "agente-testes-funcionais",
            "method": "Executar consulta fonte e reconciliar totais.",
            "evidence_required": ["Consulta e resultado bruto com digest."],
            "not_applicable_reason": "n/a",
        },
        {
            "criterion_id": "criterion-latency",
            "observable": "Primeira carga p95 permanece em até 2 segundos.",
            "priority": "high",
            "profiles": ["DESKTOP", "DASHBOARD_VISUALIZATION"],
            "risk_ids": ["risk-slow-load"],
            "applicable": True,
            "owner_agent": "agente-testes-nao-funcionais",
            "method": "Medir dez cargas após aquecimento no ambiente isolado.",
            "evidence_required": ["Série bruta, p95 e ambiente."],
            "not_applicable_reason": "n/a",
        },
        {
            "criterion_id": "criterion-task",
            "observable": "Operador identifica o KPI crítico por teclado em 5 segundos.",
            "priority": "high",
            "profiles": ["DESKTOP", "DASHBOARD_VISUALIZATION"],
            "risk_ids": ["risk-hidden-alert"],
            "applicable": True,
            "owner_agent": "agente-usabilidade-e-acessibilidade",
            "method": "Executar tarefa de cinco segundos e navegação por teclado.",
            "evidence_required": ["Registro de tarefa, foco e tempo humano."],
            "not_applicable_reason": "n/a",
        },
    ]
    risks = [
        {
            "risk_id": "risk-wrong-values",
            "failure": "Dashboard exibe total incorreto.",
            "impact": "Decisão operacional errada.",
            "severity": "critical",
            "criterion_ids": ["criterion-values"],
        },
        {
            "risk_id": "risk-slow-load",
            "failure": "Dashboard demora para carregar.",
            "impact": "Operador perde janela de decisão.",
            "severity": "high",
            "criterion_ids": ["criterion-latency"],
        },
        {
            "risk_id": "risk-hidden-alert",
            "failure": "Alerta não é percebido ou acessível.",
            "impact": "Evento crítico fica sem ação.",
            "severity": "high",
            "criterion_ids": ["criterion-task"],
        },
    ]
    return {
        "artifact_type": "QA_TEST_PLAN",
        "plan_id": "plan-qa-001",
        "causal": causal(),
        "department_mission_ref": "mission-qa-001",
        "mode": mode,
        "target_ref": "artifact/dashboard-v1",
        "objective": "Provar correção, latência e uso acessível do dashboard.",
        "risks": risks,
        "criteria": criteria,
        "edge_dimensions": {
            "covered": [
                "happy-path",
                "validation",
                "permissions",
                "state",
                "scale",
                "failure",
                "data",
                "ux",
                "recovery",
            ],
            "not_applicable": [
                "concurrency:not-required-for-read-only-dashboard",
                "security:owned-by-security-department",
                "integration:no-external-provider",
            ],
            "total": 12,
        },
        "profiles": [
            "DESKTOP",
            "DATA_DATABASE",
            "DASHBOARD_VISUALIZATION",
        ],
        "waves": [
            "contract",
            "functional-and-usability",
            "non-functional",
            "integration",
        ],
        "execution_policy": execution_policy(active=True),
        "saturation_ref": "ro15-saturation-record-001",
        "capability_gap_refs": [],
        "pending": [],
        "state": "PLANNED",
        "created_at": NOW,
    }


def assignment(agent: str) -> dict[str, Any]:
    mapping = {
        "agente-testes-funcionais": (
            ["criterion-values"],
            ["DASHBOARD_VISUALIZATION", "DATA_DATABASE"],
        ),
        "agente-testes-nao-funcionais": (
            ["criterion-latency"],
            ["DESKTOP", "DASHBOARD_VISUALIZATION"],
        ),
        "agente-usabilidade-e-acessibilidade": (
            ["criterion-task"],
            ["DESKTOP", "DASHBOARD_VISUALIZATION"],
        ),
    }
    criterion_ids, profiles = mapping[agent]
    return {
        "artifact_type": "QA_ASSIGNMENT",
        "assignment_id": f"assignment-{agent}",
        "causal": causal(message=f"message-{agent}-assignment"),
        "department_mission_ref": "mission-qa-001",
        "plan_ref": "plan-qa-001",
        "recipient": agent,
        "capability": CAPABILITY[agent],
        "objective": "Executar somente os critérios atribuídos.",
        "profiles": profiles,
        "criterion_ids": criterion_ids,
        "scope_in": ["Critérios atribuídos no plano QA."],
        "scope_out": ["Critérios das duas capacidades irmãs."],
        "target_ref": "artifact/dashboard-v1",
        "candidate_digest": CANDIDATE,
        "inputs": ["plan-qa-001", "artifact/dashboard-v1"],
        "deliverables": ["QA_AGENT_RETURN com prova reproduzível."],
        "done": ["Todos os critérios atribuídos possuem estado válido."],
        "required_evidence": ["Saída bruta, ambiente, data e executor."],
        "depends_on": [],
        "permissions": {
            "default_policy": "deny",
            "allowed_tools": ["test-runner"],
            "allowed_resources": ["isolated-test", "artifact/dashboard-v1"],
            "expires_at": "2026-07-27T20:00:00-03:00",
        },
        "execution_policy": execution_policy(active=True),
        "test_data": ["synthetic-dashboard-fixture-001"],
        "stop_when": ["authorization-revoked", "unexpected-effect"],
        "return_to": DEPARTMENT,
        "issued_at": NOW,
    }


def result_for(agent: str, status: str = "PASS") -> dict[str, Any]:
    mapping = {
        "agente-testes-funcionais": (
            "case-values",
            "criterion-values",
            "DATA_DATABASE",
            "Totais reconciliam com a consulta fonte.",
            "Totais reconciliaram: 42 = 42.",
        ),
        "agente-testes-nao-funcionais": (
            "case-latency",
            "criterion-latency",
            "DASHBOARD_VISUALIZATION",
            "Primeira carga p95 <= 2 s.",
            "p95 medido em 1,74 s.",
        ),
        "agente-usabilidade-e-acessibilidade": (
            "case-task",
            "criterion-task",
            "DASHBOARD_VISUALIZATION",
            "Operador identifica o KPI por teclado em 5 s.",
            "Tarefa concluída em 4,2 s com foco visível.",
        ),
    }
    case_id, criterion_id, profile, expected, observed = mapping[agent]
    evidence_id = f"evidence-{case_id}"
    item = {
        "case_id": case_id,
        "criterion_id": criterion_id,
        "profile": profile,
        "status": status,
        "severity": "none" if status == "PASS" else "high",
        "expected": expected,
        "observed": observed if status == "PASS" else "Resultado divergente.",
        "method": "Método fixado antes da execução.",
        "environment": "isolated-test",
        "executed_at": NOW,
        "evidence_refs": [evidence_id],
        "skip_detail": None,
    }
    if status == "SKIP":
        item.update(
            {
                "severity": "none",
                "observed": "Caso não executado.",
                "executed_at": None,
                "evidence_refs": [],
                "skip_detail": {
                    "reason": "Ambiente indisponível.",
                    "impact": "Critério permanece não comprovado.",
                    "owner": "owner-test-environment",
                    "resume_when": "Ambiente isolado disponível.",
                },
            }
        )
    if status == "UNVERIFIED":
        item.update(
            {
                "severity": "none",
                "observed": "Saída insuficiente para concluir.",
                "executed_at": None,
                "evidence_refs": [],
            }
        )
    return item


def evidence_for(agent: str, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": result["evidence_refs"][0],
        "case_id": result["case_id"],
        "criterion_id": result["criterion_id"],
        "type": "test_output",
        "origin": "isolated-test/test-runner",
        "tool_and_version": "test-runner 1.0",
        "target_ref": "artifact/dashboard-v1",
        "candidate_digest": CANDIDATE,
        "environment": "isolated-test",
        "collected_at": NOW,
        "collected_by": agent,
        "raw_output_ref": f"evidence/{result['case_id']}.txt",
        "integrity_check": digest("e"),
        "redaction": "none-required-synthetic-data",
        "limits": [],
    }


def pending_for(label: str, owner: str) -> dict[str, Any]:
    return {
        "pending_id": f"pending-{label}",
        "obligation": f"Resolver e comprovar {label}.",
        "owner": owner,
        "impact": "Critério permanece bloqueante até nova evidência.",
        "resume_when": f"Nova evidência correlacionada para {label}.",
        "causal_ref": label,
        "blocking": True,
    }


def defect_for(agent: str, result: dict[str, Any]) -> dict[str, Any]:
    risk_by_criterion = {
        "criterion-values": "risk-wrong-values",
        "criterion-latency": "risk-slow-load",
        "criterion-task": "risk-hidden-alert",
    }
    return {
        "defect_id": f"defect-{result['case_id']}",
        "risk_ids": [risk_by_criterion[result["criterion_id"]]],
        "case_id": result["case_id"],
        "evidence_refs": result["evidence_refs"],
        "candidate_digest": CANDIDATE,
        "environment": result["environment"],
        "severity": result["severity"],
        "title": f"Desvio comprovado em {result['case_id']}.",
        "preconditions": ["Candidato e ambiente do assignment disponíveis."],
        "reproduction_steps": ["Executar novamente o método registrado."],
        "expected": result["expected"],
        "observed": result["observed"],
        "impact": "Critério contratado não foi atendido.",
        "reproducibility": "always",
        "status": "open",
        "owner": "departamento-desenvolvimento",
        "retest_evidence_ref": "n/a",
    }


def agent_return(agent: str, status: str = "PASS") -> dict[str, Any]:
    assigned = assignment(agent)
    result = result_for(agent, status)
    evidence = [] if not result["evidence_refs"] else [evidence_for(agent, result)]
    defects = [defect_for(agent, result)] if status == "FAIL" else []
    pending = (
        [pending_for(result["case_id"], agent)]
        if status in {"FAIL", "SKIP", "UNVERIFIED"}
        else []
    )
    return {
        "artifact_type": "QA_AGENT_RETURN",
        "agent_return_id": f"return-{agent}",
        "causal": causal(
            agent,
            message=f"message-{agent}-return",
            handoff="handoff-qa-001",
            causes=[assigned["causal"]["message_id"]],
        ),
        "department_mission_ref": "mission-qa-001",
        "plan_ref": "plan-qa-001",
        "assignment_ref": f"assignment-{agent}",
        "assignment_digest": artifact_digest(assigned),
        "execution_policy_digest": artifact_digest(assigned["execution_policy"]),
        "agent_id": agent,
        "capability": CAPABILITY[agent],
        "status": "completed" if status == "PASS" else "partial",
        "candidate_digest": CANDIDATE,
        "profiles": assigned["profiles"],
        "results": [result],
        "evidence": evidence,
        "defects": defects,
        "pending": pending,
        "dissent_refs": [],
        "authorization_check": {
            "checked_at": NOW,
            "status_seen": "active",
            "decision": "allowed",
            "policy_digest": POLICY,
            "evidence_ref": "authorization-check-001",
            "revocation_ref": "n/a",
        },
        "cleanup": {
            "status": "PROVED",
            "cleaned_by": agent,
            "cleaned_at": NOW,
            "scope_cleaned": ["synthetic-dashboard-fixture-001"],
            "residuals": [],
            "evidence_refs": ["cleanup-evidence-001"],
            "recovery_status": "NOT_APPLICABLE",
            "recovery_evidence_refs": [],
            "pending_ref": "n/a",
        },
        "recommended_next_step": {
            "action": "CONSOLIDATE",
            "owner": DEPARTMENT,
            "reason_refs": [result["case_id"]],
        },
        "returned_to": DEPARTMENT,
        "returned_at": NOW,
    }


def consolidated(
    *,
    mode: str = "ATUA",
    passed: int = 3,
    failed: int = 0,
    skipped: int = 0,
    unverified: int = 0,
    missing: int = 0,
    recommendation: str = "READY_FOR_JUDGMENT",
) -> dict[str, Any]:
    quality_state = {
        "READY_FOR_JUDGMENT": "PROVED",
        "REWORK_REQUIRED": "FAILED",
        "NOT_PROVEN": "PARTIAL",
        "BLOCKED": "BLOCKED",
    }[recommendation]
    known_evidence_ids = [
        "evidence-case-values",
        "evidence-case-latency",
        "evidence-case-task",
    ]
    known_case_ids = ["case-values", "case-latency", "case-task"]
    evidence_total = passed + failed
    evidence_ids = known_evidence_ids[:evidence_total]
    evidence_ids.extend(
        f"evidence-extra-{index}"
        for index in range(
            1,
            max(0, evidence_total - len(known_evidence_ids)) + 1,
        )
    )
    failed_cases = known_case_ids[:failed]
    defect_refs = [f"defect-{case_id}" for case_id in failed_cases]
    defect_refs.extend(
        f"defect-extra-{index}"
        for index in range(
            1,
            max(0, failed - len(known_case_ids)) + 1,
        )
    )
    pending = [
        pending_for(case_id, DEPARTMENT)
        for case_id in failed_cases
    ]
    unresolved = skipped + unverified + missing
    pending.extend(
        pending_for(f"report-open-{index}", DEPARTMENT)
        for index in range(1, unresolved + 1)
    )
    if recommendation == "BLOCKED" and not pending:
        pending = [pending_for("report-blocked", DEPARTMENT)]
    if recommendation == "NOT_PROVEN" and not pending:
        pending = [pending_for("report-consulta", DEPARTMENT)]
    return {
        "artifact_type": "QA_CONSOLIDATED_REPORT",
        "report_id": "report-qa-001",
        "causal": causal(
            message="message-report-001",
            causes=[
                "message-director-001",
                *[f"message-{agent}-return" for agent in AGENTS],
            ],
        ),
        "department_mission_ref": "mission-qa-001",
        "plan_ref": "plan-qa-001",
        "candidate_digest": CANDIDATE,
        "mode": mode,
        "assignment_refs": [f"assignment-{agent}" for agent in AGENTS],
        "agent_return_refs": [f"return-{agent}" for agent in AGENTS],
        "coverage_summary": {
            "applicable": passed + failed + skipped + unverified + missing,
            "evaluated": passed + failed + skipped + unverified,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "unverified": unverified,
            "missing": missing,
        },
        "test_summary": {
            "pass": passed,
            "fail": failed,
            "skip": skipped,
            "skip_reasons": (
                ["Ambiente indisponível; retomar com ambiente isolado."]
                if skipped
                else []
            ),
            "critical_fail": False,
        },
        "evidence_refs": evidence_ids,
        "defect_refs": defect_refs,
        "pending": pending,
        "dissent_refs": [],
        "confidence": "HIGH" if recommendation == "READY_FOR_JUDGMENT" else "MEDIUM",
        "quality_state": quality_state,
        "recommendation": recommendation,
        "judge_required": True,
        "returned_to": "diretor-de-lentes",
        "returned_at": NOW,
    }


def route_rejection() -> dict[str, Any]:
    return {
        "artifact_type": "QA_ROUTE_REJECTION",
        "rejection_id": "rejection-qa-001",
        "causal": causal(message="message-rejection-001"),
        "result_code": "INVALID_DEPARTMENT_ROUTE",
        "failed_checks": ["Origem não é diretor-de-lentes."],
        "evidence_refs": [],
        "impact": "Nenhuma ação de QA foi autorizada.",
        "resume_when": "Diretor emitir DEPARTMENT_MISSION íntegra.",
        "action_started": False,
        "returned_to": "diretor-de-lentes",
        "returned_at": NOW,
    }


def capability_gap() -> dict[str, Any]:
    return {
        "artifact_type": "QA_CAPABILITY_GAP",
        "gap_id": "gap-qa-001",
        "causal": causal(message="message-gap-001"),
        "required_capability": "USABILITY_A11Y",
        "required_profiles": ["REPORT_DOCUMENT_PDF"],
        "discovery_method": "Enumerar agentes e validar metadata/contrato/digest.",
        "discovery_evidence": ["Agente de usabilidade ausente no inventário."],
        "result": "Capacidade necessária indisponível.",
        "blocked_criterion_ids": ["criterion-pdf-visual"],
        "impact": "Aparência do PDF permanece não comprovada.",
        "reversible_planning_allowed": True,
        "safe_state": "Q_BLOCKED",
        "owner": "diretor-de-lentes",
        "recovery_condition": "Restaurar agente válido ou reduzir escopo por autoridade.",
        "status": "open",
        "returned_to": "diretor-de-lentes",
        "detected_at": NOW,
    }


def director_causal(producer: str) -> dict[str, Any]:
    return {
        "work_item_id": "work-001",
        "front_id": "front-qa",
        "handoff_id": "handoff-qa-001",
        "message_id": "message-director-001",
        "causation_message_ids": ["message-director-root-001"],
        "contract_id": "contract-qa-001",
        "contract_version": 1,
        "contract_digest": CONTRACT,
        "candidate_digest": CANDIDATE,
        "round": 1,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": PRODUCER,
        "created_at": NOW,
    }


def director_mission() -> dict[str, Any]:
    return {
        "artifact_type": "DEPARTMENT_MISSION",
        "department_mission_id": "mission-qa-001",
        "causal": director_causal("diretor-de-lentes"),
        "recipient": DEPARTMENT,
        "mode": "ATUA",
        "objective": "Provar qualidade do dashboard.",
        "scope_in": ["Dashboard v1 e banco sintético."],
        "scope_out": ["Produção e dados reais."],
        "inputs": ["artifact/dashboard-v1"],
        "deliverables": ["Relatório consolidado e evidências."],
        "done": ["Critérios aplicáveis possuem resultado e prova."],
        "required_evidence": ["Saídas datadas e reproduzíveis."],
        "depends_on": [],
        "handoff_to": ["diretor-de-lentes"],
        "decision_authority": ["Estratégia e execução de QA no escopo."],
        "permissions": {
            "default_policy": "deny",
            "allowed_tools": ["test-runner"],
            "allowed_resources": ["isolated-test", "artifact/dashboard-v1"],
            "expires_at": "2026-07-27T20:00:00-03:00",
        },
        "stop_when": ["authorization-revoked", "unexpected-effect"],
        "return_to": "diretor-de-lentes",
        "issued_at": NOW,
    }


def to_department_return(
    report: dict[str, Any],
    mission: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Converte o relatório local sem reautorar causalidade nem incerteza."""
    mission = mission or director_mission()
    report_causal = report["causal"]
    mission_causal = mission["causal"]
    boundary_summary = copy.deepcopy(report["test_summary"])
    coverage = report["coverage_summary"]
    unverified = coverage["unverified"]
    missing = coverage["missing"]
    if unverified:
        boundary_summary["skip"] += unverified
        boundary_summary["skip_reasons"].append(
            f"UNVERIFIED:{unverified}; ver {report['report_id']}"
        )
    if missing:
        boundary_summary["skip"] += missing
        boundary_summary["skip_reasons"].append(
            f"MISSING:{missing}; ver {report['report_id']}"
        )
    boundary_causal = {
        "work_item_id": report_causal["work_item_id"],
        "front_id": mission_causal["front_id"],
        "handoff_id": report_causal["handoff_id"],
        "message_id": f"message-department-return-{report['report_id']}",
        "causation_message_ids": [report_causal["message_id"]],
        "contract_id": report_causal["contract_id"],
        "contract_version": report_causal["contract_version"],
        "contract_digest": report_causal["contract_digest"],
        "candidate_digest": report_causal["candidate_digest"],
        "round": report_causal["round"],
        "attempt": report_causal["attempt"],
        "producer": DEPARTMENT,
        "producer_version": report_causal["producer_version"],
        "producer_digest": report_causal["producer_digest"],
        "created_at": report["returned_at"],
    }
    return {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "department-return-qa-001",
        "causal": boundary_causal,
        "department_mission_ref": report["department_mission_ref"],
        "returned_by": DEPARTMENT,
        "state": "RETURNED",
        "scope_touched": copy.deepcopy(mission["scope_in"]),
        "artifact_refs": [
            authenticated_artifact_ref(report, "report_id"),
            report["plan_ref"],
        ],
        "evidence_refs": report["evidence_refs"],
        "candidate_digest": report["candidate_digest"],
        "test_summary": boundary_summary,
        "pending_refs": [p["pending_id"] for p in report["pending"]],
        "dissent_refs": report["dissent_refs"],
        "returned_to": "diretor-de-lentes",
        "returned_at": report["returned_at"],
    }


def department_bridge_errors(
    report: dict[str, Any],
    boundary: dict[str, Any],
    mission: dict[str, Any] | None = None,
) -> list[str]:
    """Reconcilia fonte e envelope; validar só o schema externo é insuficiente."""
    mission = mission or director_mission()
    errors: list[str] = []
    local_errors = validate_schema(report, LOCAL_SCHEMA, LOCAL_SCHEMA)
    errors.extend(f"fonte local: {item}" for item in local_errors)
    director_errors = validate_schema(
        boundary,
        DIRECTOR_SCHEMA["$defs"]["departmentReturn"],
        DIRECTOR_SCHEMA,
    )
    errors.extend(f"schema consumidor: {item}" for item in director_errors)

    report_causal = report["causal"]
    mission_causal = mission["causal"]
    mission_id = mission["department_mission_id"]
    if report["department_mission_ref"] != mission_id:
        errors.append("ponte: relatório referencia missão divergente")
    if report_causal["department_mission_id"] != mission_id:
        errors.append("ponte: causal local referencia missão divergente")
    inherited_fields = (
        "work_item_id",
        "handoff_id",
        "contract_id",
        "contract_version",
        "contract_digest",
        "candidate_digest",
        "round",
        "attempt",
    )
    for field in inherited_fields:
        if report_causal[field] != mission_causal[field]:
            errors.append(f"ponte: fonte não herdou {field} da missão")
    if mission_causal["message_id"] not in report_causal["causation_message_ids"]:
        errors.append("ponte: relatório não é causado pela missão do Diretor")

    expected = to_department_return(report, mission)
    for field, expected_value in expected.items():
        if boundary.get(field) != expected_value:
            errors.append(f"ponte: {field} diverge da conversão recalculada")
    extra_fields = set(boundary) - set(expected)
    if extra_fields:
        errors.append(
            "ponte: campos externos inesperados " + ", ".join(sorted(extra_fields))
        )
    authenticated_ref = authenticated_artifact_ref(report, "report_id")
    if authenticated_ref not in boundary.get("artifact_refs", []):
        errors.append("ponte: referência autenticada do relatório ausente")
    return errors


def edge_dimension_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    edge = value["edge_dimensions"]
    covered = edge["covered"]
    raw_not_applicable = edge["not_applicable"]
    not_applicable = [item.split(":", 1)[0] for item in raw_not_applicable]
    combined = covered + not_applicable
    if len(combined) != len(set(combined)):
        errors.append("dimensão repetida ou sobreposta")
    if set(combined) != EDGE_DIMENSIONS:
        missing = sorted(EDGE_DIMENSIONS - set(combined))
        extra = sorted(set(combined) - EDGE_DIMENSIONS)
        errors.append(f"partição divergente; missing={missing}; extra={extra}")
    if edge["total"] != len(EDGE_DIMENSIONS):
        errors.append("total não corresponde ao conjunto canônico")
    return errors


def artifact_graph_errors(
    test_plan: dict[str, Any],
    assignments: list[dict[str, Any]],
    returns: list[dict[str, Any]],
    report: dict[str, Any],
) -> list[str]:
    """Recalcula correlações e contagens que JSON Schema não compara."""
    errors: list[str] = []
    candidate = test_plan["causal"]["candidate_digest"]
    mission = test_plan["department_mission_ref"]
    plan_id = test_plan["plan_id"]
    criteria = {
        item["criterion_id"]: item
        for item in test_plan["criteria"]
        if item["applicable"]
    }

    assignments_by_id = {item["assignment_id"]: item for item in assignments}
    if len(assignments_by_id) != len(assignments):
        errors.append("assignment_id duplicado")
    assigned: dict[str, list[str]] = {criterion_id: [] for criterion_id in criteria}
    for item in assignments:
        if item["department_mission_ref"] != mission:
            errors.append(f"{item['assignment_id']}: missão divergente")
        if item["plan_ref"] != plan_id:
            errors.append(f"{item['assignment_id']}: plano divergente")
        if item["candidate_digest"] != candidate:
            errors.append(f"{item['assignment_id']}: candidato divergente")
        if item["capability"] != CAPABILITY[item["recipient"]]:
            errors.append(f"{item['assignment_id']}: capacidade divergente")
        for criterion_id in item["criterion_ids"]:
            if criterion_id not in criteria:
                errors.append(f"{item['assignment_id']}: critério desconhecido")
                continue
            assigned[criterion_id].append(item["recipient"])
            if criteria[criterion_id]["owner_agent"] != item["recipient"]:
                errors.append(f"{criterion_id}: assignment não pertence à dona")
    for criterion_id, recipients in assigned.items():
        if recipients != [criteria[criterion_id]["owner_agent"]]:
            errors.append(f"{criterion_id}: não possui exatamente uma assignment")

    returns_by_id = {item["agent_return_id"]: item for item in returns}
    if len(returns_by_id) != len(returns):
        errors.append("agent_return_id duplicado")
    all_results: list[dict[str, Any]] = []
    evidence_ids: set[str] = set()
    defect_ids: set[str] = set()
    returned_pending_ids: set[str] = set()
    returned_pending_by_id: dict[str, dict[str, Any]] = {}
    for item in returns:
        assignment_item = assignments_by_id.get(item["assignment_ref"])
        if assignment_item is None:
            errors.append(f"{item['agent_return_id']}: assignment ausente")
            continue
        if item["department_mission_ref"] != assignment_item["department_mission_ref"]:
            errors.append(f"{item['agent_return_id']}: missão divergente")
        if item["plan_ref"] != assignment_item["plan_ref"]:
            errors.append(f"{item['agent_return_id']}: plano divergente")
        if item["agent_id"] != assignment_item["recipient"]:
            errors.append(f"{item['agent_return_id']}: agente divergente")
        if item["capability"] != assignment_item["capability"]:
            errors.append(f"{item['agent_return_id']}: capacidade divergente")
        if item["candidate_digest"] != assignment_item["candidate_digest"]:
            errors.append(f"{item['agent_return_id']}: candidato divergente")
        causal_fields = (
            "work_item_id",
            "department_mission_id",
            "handoff_id",
            "contract_id",
            "contract_version",
            "contract_digest",
            "candidate_digest",
            "round",
            "attempt",
        )
        for field in causal_fields:
            if item["causal"][field] != assignment_item["causal"][field]:
                errors.append(
                    f"{item['agent_return_id']}: causal {field} divergente"
                )
        if assignment_item["causal"]["message_id"] not in item["causal"][
            "causation_message_ids"
        ]:
            errors.append(
                f"{item['agent_return_id']}: mensagem da assignment não causa retorno"
            )
        if item["assignment_digest"] != artifact_digest(assignment_item):
            errors.append(f"{item['agent_return_id']}: digest da assignment divergente")
        if item["execution_policy_digest"] != artifact_digest(
            assignment_item["execution_policy"]
        ):
            errors.append(
                f"{item['agent_return_id']}: digest da política divergente"
            )
        if assignment_item["execution_policy"]["active_testing_allowed"]:
            authorization = item["authorization_check"]
            if (
                authorization["status_seen"] != "active"
                or authorization["decision"] != "allowed"
            ):
                errors.append(
                    f"{item['agent_return_id']}: autorização ativa não comprovada"
                )
            cleanup = item["cleanup"]
            if cleanup["status"] != "PROVED":
                errors.append(
                    f"{item['agent_return_id']}: limpeza ativa não comprovada"
                )
            if cleanup["status"] == "PROVED" and not cleanup["evidence_refs"]:
                errors.append(
                    f"{item['agent_return_id']}: limpeza sem evidência"
                )
        evidence_by_id = {
            evidence["evidence_id"]: evidence
            for evidence in item["evidence"]
        }
        evidence_ids.update(evidence_by_id)
        defect_ids.update(defect["defect_id"] for defect in item["defects"])
        returned_pending_ids.update(
            pending["pending_id"] for pending in item["pending"]
        )
        returned_pending_by_id.update(
            {pending["pending_id"]: pending for pending in item["pending"]}
        )
        for result in item["results"]:
            all_results.append(result)
            if result["criterion_id"] not in assignment_item["criterion_ids"]:
                errors.append(
                    f"{item['agent_return_id']}: resultado fora da assignment"
                )
            if result["profile"] not in assignment_item["profiles"]:
                errors.append(
                    f"{item['agent_return_id']}: perfil fora da assignment"
                )
            for evidence_ref in result["evidence_refs"]:
                evidence = evidence_by_id.get(evidence_ref)
                if evidence is None:
                    errors.append(
                        f"{item['agent_return_id']}: evidência não resolvida"
                    )
                    continue
                if (
                    evidence["case_id"] != result["case_id"]
                    or evidence["criterion_id"] != result["criterion_id"]
                    or evidence["candidate_digest"] != candidate
                    or evidence["collected_by"] != item["agent_id"]
                ):
                    errors.append(
                        f"{item['agent_return_id']}: evidência não correlacionada"
                    )
            if result["status"] == "FAIL":
                matching_defects = [
                    defect
                    for defect in item["defects"]
                    if defect["case_id"] == result["case_id"]
                    and defect["candidate_digest"] == candidate
                    and defect["environment"] == result["environment"]
                    and set(result["evidence_refs"]).issubset(
                        set(defect["evidence_refs"])
                    )
                ]
                if not matching_defects:
                    errors.append(
                        f"{item['agent_return_id']}: FAIL sem defeito correlacionado"
                    )
                allowed_pending_causes = {result["case_id"]} | {
                    defect["defect_id"] for defect in matching_defects
                }
                if not any(
                    pending["causal_ref"] in allowed_pending_causes
                    for pending in item["pending"]
                ):
                    errors.append(
                        f"{item['agent_return_id']}: FAIL sem pendência correlacionada"
                    )
        fail_case_ids = {
            result["case_id"]
            for result in item["results"]
            if result["status"] == "FAIL"
        }
        if any(
            defect["case_id"] not in fail_case_ids
            for defect in item["defects"]
        ):
            errors.append(f"{item['agent_return_id']}: defeito órfão de FAIL")
        allowed_reason_refs = {
            result["case_id"] for result in item["results"]
        } | set(evidence_by_id) | {
            defect["defect_id"] for defect in item["defects"]
        } | {
            pending["pending_id"] for pending in item["pending"]
        }
        if not set(
            item["recommended_next_step"]["reason_refs"]
        ).issubset(allowed_reason_refs):
            errors.append(
                f"{item['agent_return_id']}: próximo passo sem razão resolvida"
            )

    if set(report["assignment_refs"]) != set(assignments_by_id):
        errors.append("relatório não referencia todas e somente as assignments")
    if set(report["agent_return_refs"]) != set(returns_by_id):
        errors.append("relatório não referencia todos e somente os retornos")
    if report["department_mission_ref"] != mission:
        errors.append("relatório aponta missão divergente")
    if report["plan_ref"] != plan_id:
        errors.append("relatório aponta plano divergente")
    if report["candidate_digest"] != candidate:
        errors.append("relatório aponta candidato divergente")
    report_causal_fields = (
        "work_item_id",
        "department_mission_id",
        "handoff_id",
        "contract_id",
        "contract_version",
        "contract_digest",
        "candidate_digest",
        "round",
        "attempt",
    )
    for field in report_causal_fields:
        if report["causal"][field] != test_plan["causal"][field]:
            errors.append(f"relatório possui causal {field} divergente")
    return_messages = {
        item["causal"]["message_id"] for item in returns
    }
    if not return_messages.issubset(
        set(report["causal"]["causation_message_ids"])
    ):
        errors.append("relatório não é causado por todos os retornos")
    if set(report["evidence_refs"]) != evidence_ids:
        errors.append("relatório não reconcilia evidências")
    if set(report["defect_refs"]) != defect_ids:
        errors.append("relatório não reconcilia defeitos")
    report_pending_by_id = {
        item["pending_id"]: item for item in report["pending"]
    }
    if not returned_pending_ids.issubset(report_pending_by_id):
        errors.append("relatório não preserva pendências dos agentes")
    for pending_id, pending in returned_pending_by_id.items():
        if report_pending_by_id.get(pending_id) != pending:
            errors.append(f"relatório reautora pendência {pending_id}")

    raw_summary = summarize(all_results)
    expected_test_summary = {
        "pass": raw_summary["pass"],
        "fail": raw_summary["fail"],
        "skip": raw_summary["skip"],
        "skip_reasons": [
            item["skip_detail"]["reason"]
            for item in all_results
            if item["status"] == "SKIP"
        ],
        "critical_fail": raw_summary["critical_fail"],
    }
    if report["test_summary"] != expected_test_summary:
        errors.append("test_summary não foi recalculado dos casos")

    results_by_criterion: dict[str, list[str]] = {
        criterion_id: [] for criterion_id in criteria
    }
    for result in all_results:
        if result["criterion_id"] in results_by_criterion:
            results_by_criterion[result["criterion_id"]].append(result["status"])
    coverage = {
        "applicable": len(criteria),
        "evaluated": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "unverified": 0,
        "missing": 0,
    }
    for statuses in results_by_criterion.values():
        if not statuses:
            coverage["missing"] += 1
            continue
        coverage["evaluated"] += 1
        if "FAIL" in statuses:
            coverage["failed"] += 1
        elif "SKIP" in statuses:
            coverage["skipped"] += 1
        elif "UNVERIFIED" in statuses:
            coverage["unverified"] += 1
        else:
            coverage["passed"] += 1
    if report["coverage_summary"] != coverage:
        errors.append("coverage_summary não foi recalculado dos critérios")

    expected_state = derive_state(
        mode=report["mode"],
        passed=raw_summary["pass"],
        failed=raw_summary["fail"],
        skipped=raw_summary["skip"],
        unverified=coverage["unverified"],
        missing=coverage["missing"],
    )
    if (report["quality_state"], report["recommendation"]) != expected_state:
        errors.append("estado/recomendação não derivam dos resultados")
    return errors


# ---------------------------------------------------------------------------
# Infra de verificação
# ---------------------------------------------------------------------------

PASSED = 0
FAILED = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"[PASS] {label}")
    else:
        FAILED += 1
        suffix = f": {detail}" if detail else ""
        print(f"[FAIL] {label}{suffix}")


def valid_local(value: dict[str, Any]) -> list[str]:
    return validate_schema(value, LOCAL_SCHEMA, LOCAL_SCHEMA)


def valid_director(value: dict[str, Any], def_name: str) -> list[str]:
    return validate_schema(
        value,
        DIRECTOR_SCHEMA["$defs"][def_name],
        DIRECTOR_SCHEMA,
    )


def validate_links_with_context() -> list[str]:
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    errors: list[str] = []
    for path in sorted(PACKAGE_ROOT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_file = target.split("#", 1)[0]
            if not target_file:
                continue
            local = (path.parent / target_file).resolve()
            if local.exists():
                continue
            mirror = CANONICAL_PACKAGE_ROOT / path.relative_to(PACKAGE_ROOT)
            canonical = (mirror.parent / target_file).resolve()
            if not canonical.exists():
                errors.append(f"link quebrado em {path.name}: {target}")
    return errors


def validate_structure() -> None:
    required = [
        SKILL_PATH,
        CONTRACT_PATH,
        OPENAI_PATH,
        SCHEMA_PATH,
        EVALS_PATH,
        PACKAGE_ROOT / "evals" / "validate_workflow.py",
        PACKAGE_ROOT / "evals" / "PLACAR.md",
        PACKAGE_ROOT / "evals" / "FORWARD-TEST.md",
        PACKAGE_ROOT / "references" / "protocolo-qa-usabilidade.md",
        PACKAGE_ROOT / "references" / "perfis-e-matriz-de-cobertura.md",
        PACKAGE_ROOT / "references" / "fontes-canonicas-e-fronteiras.md",
        PACKAGE_ROOT / "references" / "origem-migracao.md",
        PACKAGE_ROOT / "references" / "bootstrap.md",
        PACKAGE_ROOT / "references" / "adr-011-qa-executa-sem-julgar.md",
        DIRECTOR_SCHEMA_PATH,
        RULES_PATH,
        STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
        STRUCTURE_ROOT / "_compartilhado" / "verificacoes_pacote.py",
    ]
    errors = validate_required_files(required, "arquivo obrigatório")
    check("arquivos obrigatórios", not errors, " | ".join(errors))
    errors = validate_agents_folder(AGENTS_ROOT, AGENTS)
    check("três agentes canônicos e completos", not errors, " | ".join(errors))

    # Estrutura normativa dos contratos e SKILL de agente — GUIA, passos 7 e 8.
    # Até 2026-07-27 nenhum validador olhava heading de contrato de agente, e o
    # resultado medido foi 15 de 66 conformes, com a trava anti-bypass ausente
    # em 30. A conferência mora no `_compartilhado`; a lista do que é
    # obrigatório continua sendo decisão deste pacote.
    errors = []
    for agente in sorted(p for p in AGENTS_ROOT.iterdir() if p.is_dir()):
        errors.extend(
            validate_contract_sections(
                agente / "CONTRATO-DE-COMPROMISSO.md",
                SECOES_CONTRATO_AGENTE,
                agente.name,
            )
        )
        errors.extend(
            validate_skill_tokens(agente / "SKILL.md", TOKENS_SKILL_AGENTE, agente.name)
        )
    check(
        "contratos e SKILL dos agentes seguem a estrutura normativa",
        not errors,
        " | ".join(errors),
    )


def validate_metadata() -> None:
    errors = validate_frontmatter(SKILL_PATH, DEPARTMENT)
    check("frontmatter e tamanho do Departamento", not errors, " | ".join(errors))
    errors = validate_openai_yaml(
        OPENAI_PATH,
        "Departamento de QA e Usabilidade",
        "$departamento-qa-usabilidade",
        expected_short="Orquestra qualidade, usabilidade e evidências",
    )
    check("metadata do Departamento", not errors, " | ".join(errors))

    metadata = {
        "agente-testes-funcionais": (
            "Agente de Testes Funcionais",
            "Executa fluxos e valida objetivos funcionais",
        ),
        "agente-testes-nao-funcionais": (
            "Agente de Testes Não Funcionais",
            "Mede desempenho, confiabilidade e compatibilidade",
        ),
        "agente-usabilidade-e-acessibilidade": (
            "Agente de Usabilidade e Acessibilidade",
            "Valida tarefas, experiência e acessibilidade",
        ),
    }
    for agent in AGENTS:
        root = AGENTS_ROOT / agent
        errors = validate_frontmatter(root / "SKILL.md", agent)
        check(f"frontmatter e tamanho de {agent}", not errors, " | ".join(errors))
        display, short = metadata[agent]
        errors = validate_openai_yaml(
            root / "agents" / "openai.yaml",
            display,
            f"${agent}",
            expected_short=short,
        )
        check(f"metadata de {agent}", not errors, " | ".join(errors))


def validate_normative_source() -> None:
    manager = SKILL_PATH.read_text(encoding="utf-8")
    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    check(
        "caminho normativo correto no Departamento",
        RULES_LINK_DEPARTMENT in manager and RULES_LINK_DEPARTMENT in contract,
    )
    check(
        "Departamento declara orquestrar e não executar",
        "não executar testes" in manager.lower()
        and "não executa testes" in contract.lower(),
    )
    check(
        "Departamento preserva gate dos Juízes",
        "departamento-juizes" in manager and "não atribui nota" in contract.lower(),
    )
    for agent in AGENTS:
        root = AGENTS_ROOT / agent
        text = (root / "SKILL.md").read_text(encoding="utf-8")
        own_contract = (root / "CONTRATO-DE-COMPROMISSO.md").read_text(
            encoding="utf-8"
        )
        check(
            f"fonte normativa correta em {agent}",
            RULES_LINK_AGENT in text and RULES_LINK_AGENT in own_contract,
        )
        check(
            f"anti-bypass explícito em {agent}",
            "BLOCKED_BYPASS_ATTEMPT" in text and "QA_ASSIGNMENT" in own_contract,
        )
        check(
            f"{agent} é folha da árvore",
            "Não aciona:** ninguém" in text,
        )


def validate_links_and_evals() -> None:
    errors = validate_links_with_context()
    check("todos os links markdown resolvem", not errors, " | ".join(errors))
    errors = validate_adr_series(STRUCTURE_ROOT)
    check(
        "série global de ADR é única em toda a estrutura",
        not errors,
        " | ".join(errors),
    )
    errors = validate_cobertura_de_validadores(STRUCTURE_ROOT)
    check(
        "todo pacote gerente tem validador que roda a trava global",
        not errors,
        " | ".join(errors),
    )
    errors = validate_trava_de_digest(STRUCTURE_ROOT)
    check(
        "a recusa de digest() dispara e ninguém tem cópia privada do motor",
        not errors,
        " | ".join(errors),
    )
    cadeia_errors = validate_placar_nao_declara_cadeia(STRUCTURE_ROOT)
    check(
        "nenhum placar de pacote declara total de cadeia como estado corrente",
        not cadeia_errors,
        " | ".join(cadeia_errors),
    )
    selo_errors = validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)
    check(
        "a contagem publicada aponta para o digest do instrumento vigente",
        not selo_errors,
        " | ".join(selo_errors),
    )
    travas_errors = validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT)
    check(
        "as travas do modulo compartilhado nao estao neutralizadas",
        not travas_errors,
        " | ".join(travas_errors),
    )
    dono_errors = validate_pendencia_tem_dono(STRUCTURE_ROOT)
    check(
        "toda pendencia declarada nomeia quem responde por ela",
        not dono_errors,
        " | ".join(dono_errors),
    )
    errors = validate_sem_check_tautologico(STRUCTURE_ROOT)
    check(
        "nenhuma asserção é verdadeira por construção sobre valor produzido",
        not errors,
        " | ".join(errors),
    )
    errors = validate_fonte_normativa_conferida(STRUCTURE_ROOT)
    check(
        "a fonte normativa confere com o valor declarado em ORIGEM.md",
        not errors,
        " | ".join(errors),
    )
    data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    check("evals contém ao menos 12 casos", len(cases) >= 12, str(len(cases)))
    check(
        "evals contém caso de origem real",
        any(case.get("origem") == "real" for case in cases),
    )
    check(
        "cada eval possui ao menos 3 assertions",
        all(len(case.get("assertions", [])) >= 3 for case in cases),
    )
    check(
        "prompts não nomeiam a skill nem usam token",
        all(
            DEPARTMENT not in case.get("prompt", "")
            and f"${DEPARTMENT}" not in case.get("prompt", "")
            for case in cases
        ),
    )
    ids = [case.get("id") for case in cases]
    check("ids dos evals são únicos", len(ids) == len(set(ids)))


def validate_schema_shape() -> None:
    expected = {
        "qaTestPlan",
        "qaAssignment",
        "qaAgentReturn",
        "qaRouteRejection",
        "qaCapabilityGap",
        "qaConsolidatedReport",
    }
    check(
        "schema possui os seis artefatos",
        expected.issubset(LOCAL_SCHEMA["$defs"]),
    )
    refs: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "$ref" in node:
                refs.append(node["$ref"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(LOCAL_SCHEMA)
    broken: list[str] = []
    for ref in refs:
        try:
            json_pointer(LOCAL_SCHEMA, ref)
        except (KeyError, ValueError) as exc:
            broken.append(f"{ref}: {exc}")
    check("todos os $refs locais resolvem", not broken, " | ".join(broken))
    enum_agents = set(LOCAL_SCHEMA["$defs"]["agentId"]["enum"])
    folders = {item.name for item in AGENTS_ROOT.iterdir() if item.is_dir()}
    check("enum de agentes coincide com pastas reais", enum_agents == folders)

    properties: set[str] = set()
    collect_property_names(LOCAL_SCHEMA, properties)
    collision = properties & FORBIDDEN_RESULT_KEYS
    check(
        "schema não materializa nota ou validação",
        not collision,
        ", ".join(sorted(collision)),
    )

    missing_closed: list[str] = []

    def inspect_objects(node: Any, path: str = "$") -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and node.get("additionalProperties") is not False:
                missing_closed.append(path)
            for key, value in node.items():
                inspect_objects(value, f"{path}/{key}")
        elif isinstance(node, list):
            for index, item in enumerate(node):
                inspect_objects(item, f"{path}/{index}")

    inspect_objects(LOCAL_SCHEMA)
    check(
        "todo objeto do schema é fechado",
        not missing_closed,
        ", ".join(missing_closed[:5]),
    )


def validate_positive_fixtures() -> None:
    fixtures = [
        ("QA_TEST_PLAN", plan()),
        ("QA_ASSIGNMENT funcional", assignment(AGENTS[0])),
        ("QA_ASSIGNMENT não funcional", assignment(AGENTS[1])),
        ("QA_ASSIGNMENT usabilidade", assignment(AGENTS[2])),
        ("QA_AGENT_RETURN funcional", agent_return(AGENTS[0])),
        ("QA_AGENT_RETURN não funcional", agent_return(AGENTS[1])),
        ("QA_AGENT_RETURN usabilidade", agent_return(AGENTS[2])),
        ("QA_AGENT_RETURN com FAIL materializado", agent_return(AGENTS[0], "FAIL")),
        ("QA_ROUTE_REJECTION", route_rejection()),
        ("QA_CAPABILITY_GAP", capability_gap()),
        ("QA_CONSOLIDATED_REPORT", consolidated()),
    ]
    for label, value in fixtures:
        errors = valid_local(value)
        check(f"fixture positiva {label}", not errors, " | ".join(errors[:3]))


def validate_negative_fixtures() -> None:
    mutations: list[tuple[str, dict[str, Any]]] = []

    bad = plan()
    bad["causal"]["producer"] = AGENTS[0]
    mutations.append(("plano com produtor forjado", bad))

    bad = plan()
    bad["criteria"][0]["owner_agent"] = None
    mutations.append(("critério aplicável sem dona", bad))

    bad = plan()
    bad["criteria"][0]["not_applicable_reason"] = "sem motivo"
    mutations.append(("critério aplicável com N/A divergente", bad))

    bad = plan()
    bad["unexpected"] = True
    mutations.append(("campo extra no plano", bad))

    bad = plan()
    bad["edge_dimensions"]["covered"][0] = "dimensão-inventada"
    mutations.append(("plano inventa dimensão de borda", bad))

    bad = assignment(AGENTS[0])
    bad["capability"] = "NON_FUNCTIONAL"
    mutations.append(("assignment com capacidade da irmã", bad))

    bad = assignment(AGENTS[0])
    bad["return_to"] = "diretor-de-lentes"
    mutations.append(("assignment salta a gerente", bad))

    bad = assignment(AGENTS[0])
    bad["permissions"]["default_policy"] = "allow"
    mutations.append(("permissão não é default-deny", bad))

    bad = assignment(AGENTS[0])
    bad["execution_policy"]["authorization_ref"] = "n/a"
    mutations.append(("ação ativa sem autorização", bad))

    bad = assignment(AGENTS[0])
    bad["execution_policy"]["rate_volume_concurrency_limits"] = []
    mutations.append(("ação ativa sem limites operacionais", bad))

    bad = assignment(AGENTS[0])
    bad["execution_policy"]["test_accounts"] = ["n/a"]
    mutations.append(("ação ativa esconde conta de teste como N/A", bad))

    bad = assignment(AGENTS[0])
    bad["execution_policy"]["cleanup_plan_ref"] = " N/A "
    mutations.append(("ação ativa mascara cleanup como N/A com espaços", bad))

    bad = assignment(AGENTS[0])
    bad["execution_policy"]["issued_at"] = "hoje"
    mutations.append(("ação ativa com timestamp inválido", bad))

    bad = agent_return(AGENTS[0])
    bad["causal"]["producer"] = AGENTS[1]
    mutations.append(("retorno com produtor de outra agente", bad))

    bad = agent_return(AGENTS[0])
    bad["capability"] = "USABILITY_A11Y"
    mutations.append(("retorno assume fronteira da irmã", bad))

    bad = agent_return(AGENTS[0])
    bad["results"][0]["evidence_refs"] = []
    mutations.append(("PASS sem evidência", bad))

    bad = agent_return(AGENTS[0], "SKIP")
    bad["results"][0]["skip_detail"] = None
    mutations.append(("SKIP sem detalhe", bad))

    bad = agent_return(AGENTS[0], "SKIP")
    bad["status"] = "completed"
    mutations.append(("retorno concluído promove SKIP", bad))

    bad = agent_return(AGENTS[0], "FAIL")
    bad["defects"] = []
    bad["pending"] = []
    mutations.append(("FAIL sem defeito nem pendência", bad))

    bad = agent_return(AGENTS[0])
    bad["recommended_next_step"] = "APROVADO com nota 10"
    mutations.append(("agente embute julgamento em texto livre", bad))

    bad = agent_return(AGENTS[0])
    bad["recommended_next_step"]["owner"] = "APROVADO com nota 10"
    mutations.append(("agente embute julgamento no owner do próximo passo", bad))

    bad = agent_return(AGENTS[0])
    bad["returned_to"] = "diretor-de-lentes"
    mutations.append(("agente salta a gerente no retorno", bad))

    bad = route_rejection()
    bad["action_started"] = True
    mutations.append(("rejeição depois de iniciar ação", bad))

    bad = capability_gap()
    bad["owner"] = DEPARTMENT
    mutations.append(("gap esconde decisão do Diretor", bad))

    bad = consolidated()
    bad["test_summary"]["fail"] = 1
    mutations.append(("READY com falha", bad))

    bad = consolidated(mode="CONSULTA")
    mutations.append(("CONSULTA declarada PROVED", bad))

    bad = consolidated()
    bad["score"] = 9.5
    mutations.append(("relatório inclui nota", bad))

    bad = consolidated()
    bad["assignment_refs"] = []
    bad["agent_return_refs"] = []
    bad["evidence_refs"] = []
    mutations.append(("READY sem cadeia probatória", bad))

    bad = consolidated()
    bad["coverage_summary"]["applicable"] = 0
    bad["coverage_summary"]["evaluated"] = 0
    bad["coverage_summary"]["passed"] = 0
    mutations.append(("READY sem cobertura positiva", bad))

    bad = consolidated()
    bad["pending"] = [pending_for("ready-aberto", DEPARTMENT)]
    mutations.append(("READY com pendência aberta", bad))

    bad = consolidated(
        passed=2,
        skipped=1,
        recommendation="READY_FOR_JUDGMENT",
    )
    mutations.append(("READY promove SKIP", bad))

    bad = consolidated(
        passed=2,
        failed=1,
        recommendation="REWORK_REQUIRED",
    )
    bad["quality_state"] = "PROVED"
    mutations.append(("falha com estado PROVED", bad))

    for label, value in mutations:
        errors = valid_local(value)
        check(f"fixture negativa rejeita {label}", bool(errors))


def validate_behavioral_rules() -> None:
    check(
        "derivação positiva exige prova total",
        derive_state(
            mode="ATUA",
            passed=3,
            failed=0,
            skipped=0,
            unverified=0,
            missing=0,
        )
        == ("PROVED", "READY_FOR_JUDGMENT"),
    )
    check(
        "uma falha força retrabalho",
        derive_state(
            mode="ATUA",
            passed=99,
            failed=1,
            skipped=0,
            unverified=0,
            missing=0,
        )
        == ("FAILED", "REWORK_REQUIRED"),
    )
    check(
        "um SKIP impede PROVED",
        derive_state(
            mode="ATUA",
            passed=9,
            failed=0,
            skipped=1,
            unverified=0,
            missing=0,
        )
        == ("PARTIAL", "NOT_PROVEN"),
    )
    check(
        "CONSULTA nunca vira PROVED",
        derive_state(
            mode="CONSULTA",
            passed=3,
            failed=0,
            skipped=0,
            unverified=0,
            missing=0,
        )
        == ("PARTIAL", "NOT_PROVEN"),
    )
    check(
        "propriedade funcional tem dona única",
        owner_for("functional") == AGENTS[0],
    )
    check(
        "propriedade não funcional tem dona única",
        owner_for("non_functional") == AGENTS[1],
    )
    check(
        "propriedade humana tem dona única",
        owner_for("usability_a11y") == AGENTS[2],
    )
    results = [
        result_for(AGENTS[0], "PASS"),
        result_for(AGENTS[1], "FAIL"),
        result_for(AGENTS[2], "SKIP"),
    ]
    summary = summarize(results)
    check(
        "resumo é recalculado dos casos",
        summary
        == {
            "pass": 1,
            "fail": 1,
            "skip": 1,
            "unverified": 0,
            "critical_fail": False,
        },
    )

    base_plan = plan()
    base_assignments = [assignment(agent) for agent in AGENTS]
    base_returns = [agent_return(agent) for agent in AGENTS]
    base_report = consolidated()
    errors = edge_dimension_errors(base_plan)
    check(
        "as 12 dimensões formam partição canônica",
        not errors,
        " | ".join(errors),
    )
    errors = artifact_graph_errors(
        base_plan,
        base_assignments,
        base_returns,
        base_report,
    )
    check(
        "grafo assignment-retorno-relatório fecha",
        not errors,
        " | ".join(errors),
    )

    bad_plan = copy.deepcopy(base_plan)
    bad_plan["edge_dimensions"]["not_applicable"].pop()
    check(
        "partição incompleta das 12 dimensões é detectada",
        bool(edge_dimension_errors(bad_plan)),
    )

    bad_returns = copy.deepcopy(base_returns)
    bad_returns[0]["assignment_ref"] = base_assignments[1]["assignment_id"]
    check(
        "retorno correlacionado à assignment errada é detectado",
        bool(
            artifact_graph_errors(
                base_plan,
                base_assignments,
                bad_returns,
                base_report,
            )
        ),
    )

    bad_report = copy.deepcopy(base_report)
    bad_report["coverage_summary"]["applicable"] = 99
    check(
        "cobertura aritmeticamente incoerente é detectada",
        bool(
            artifact_graph_errors(
                base_plan,
                base_assignments,
                base_returns,
                bad_report,
            )
        ),
    )

    bad_returns = copy.deepcopy(base_returns)
    bad_returns[0]["assignment_digest"] = digest("f")
    check(
        "digest divergente da assignment é detectado",
        bool(
            artifact_graph_errors(
                base_plan,
                base_assignments,
                bad_returns,
                base_report,
            )
        ),
    )

    bad_returns = copy.deepcopy(base_returns)
    bad_returns[0]["cleanup"]["status"] = "UNVERIFIED"
    bad_returns[0]["cleanup"]["pending_ref"] = "pending-cleanup-001"
    check(
        "execução ativa com limpeza não comprovada é detectada",
        bool(
            artifact_graph_errors(
                base_plan,
                base_assignments,
                bad_returns,
                base_report,
            )
        ),
    )

    bad_returns = copy.deepcopy(base_returns)
    bad_returns[0]["cleanup"]["status"] = "PARTIAL"
    bad_returns[0]["cleanup"]["pending_ref"] = "pending-cleanup-001"
    check(
        "execução ativa com limpeza parcial impede READY",
        bool(
            artifact_graph_errors(
                base_plan,
                base_assignments,
                bad_returns,
                base_report,
            )
        ),
    )

    bad_returns = copy.deepcopy(base_returns)
    bad_returns[0]["causal"]["handoff_id"] = "handoff-forjado-001"
    check(
        "handoff causal divergente é detectado",
        bool(
            artifact_graph_errors(
                base_plan,
                base_assignments,
                bad_returns,
                base_report,
            )
        ),
    )

    bad_returns = copy.deepcopy(base_returns)
    bad_returns[0]["causal"]["contract_digest"] = digest("f")
    check(
        "contrato causal divergente é detectado",
        bool(
            artifact_graph_errors(
                base_plan,
                base_assignments,
                bad_returns,
                base_report,
            )
        ),
    )

    failure_returns = [
        agent_return(AGENTS[0], "FAIL"),
        agent_return(AGENTS[1]),
        agent_return(AGENTS[2]),
    ]
    failure_report = consolidated(
        passed=2,
        failed=1,
        recommendation="REWORK_REQUIRED",
    )
    failure_report["pending"] = copy.deepcopy(failure_returns[0]["pending"])
    errors = artifact_graph_errors(
        base_plan,
        base_assignments,
        failure_returns,
        failure_report,
    )
    check(
        "grafo com FAIL correlacionado fecha",
        not errors,
        " | ".join(errors),
    )

    bad_failure_returns = copy.deepcopy(failure_returns)
    bad_failure_returns[0]["defects"][0]["case_id"] = "case-nao-relacionado"
    bad_failure_returns[0]["pending"][0]["causal_ref"] = "case-nao-relacionado"
    check(
        "defeito e pendência de outro caso são detectados",
        bool(
            artifact_graph_errors(
                base_plan,
                base_assignments,
                bad_failure_returns,
                failure_report,
            )
        ),
    )


def validate_inherited_authority() -> None:
    check(
        "schema do Diretor conhece o Departamento",
        DEPARTMENT in json.dumps(DIRECTOR_SCHEMA, ensure_ascii=False),
    )
    mission = director_mission()
    errors = valid_director(mission, "departmentMission")
    check(
        "entrada real DEPARTMENT_MISSION aceita pelo Diretor",
        not errors,
        " | ".join(errors[:3]),
    )
    report = consolidated()
    boundary = to_department_return(report, mission)
    errors = valid_director(boundary, "departmentReturn")
    check(
        "DEPARTMENT_RETURN derivado aceito pelo consumidor",
        not errors,
        " | ".join(errors[:3]),
    )
    errors = department_bridge_errors(report, boundary, mission)
    check(
        "ponte semântica reconcilia relatório e retorno",
        not errors,
        " | ".join(errors[:3]),
    )
    check(
        "retorno autentica o relatório por SHA-256",
        authenticated_artifact_ref(report, "report_id")
        in boundary["artifact_refs"],
    )
    check(
        "retorno é causado pelo relatório consolidado",
        boundary["causal"]["causation_message_ids"]
        == [report["causal"]["message_id"]],
    )

    partial_report = consolidated(
        passed=1,
        unverified=1,
        missing=1,
        recommendation="NOT_PROVEN",
    )
    partial_boundary = to_department_return(partial_report, mission)
    errors = department_bridge_errors(partial_report, partial_boundary, mission)
    check(
        "fronteira conservadora de incerteza passa no gate composto",
        not errors,
        " | ".join(errors[:3]),
    )
    check(
        "UNVERIFIED e MISSING permanecem visíveis na fronteira",
        partial_boundary["test_summary"]["skip"] == 2
        and any(
            reason.startswith("UNVERIFIED:1")
            for reason in partial_boundary["test_summary"]["skip_reasons"]
        )
        and any(
            reason.startswith("MISSING:1")
            for reason in partial_boundary["test_summary"]["skip_reasons"]
        ),
    )
    check(
        "incerteza na fronteira conserva pendências",
        len(partial_boundary["pending_refs"]) == 2,
    )

    bad = copy.deepcopy(partial_boundary)
    bad["test_summary"]["skip"] = 0
    bad["test_summary"]["skip_reasons"] = []
    bad["pending_refs"] = []
    schema_only_errors = valid_director(bad, "departmentReturn")
    bridge_errors = department_bridge_errors(partial_report, bad, mission)
    check(
        "gate composto bloqueia ocultação aceita pelo schema estrutural",
        not schema_only_errors and bool(bridge_errors),
        " | ".join(bridge_errors[:3]),
    )

    bad = copy.deepcopy(partial_boundary)
    bad["causal"]["contract_digest"] = digest("f")
    schema_only_errors = valid_director(bad, "departmentReturn")
    bridge_errors = department_bridge_errors(partial_report, bad, mission)
    check(
        "gate composto bloqueia causal válido porém divergente",
        not schema_only_errors and bool(bridge_errors),
        " | ".join(bridge_errors[:3]),
    )

    bad = copy.deepcopy(boundary)
    bad["causal"]["producer"] = AGENTS[0]
    errors = valid_director(bad, "departmentReturn")
    check("consumidor rejeita retorno direto de agente", bool(errors))

    bad = copy.deepcopy(boundary)
    bad["returned_by"] = "departamento-desenvolvimento"
    errors = valid_director(bad, "departmentReturn")
    check("consumidor rejeita returned_by divergente", bool(errors))

    bad = copy.deepcopy(boundary)
    bad["returned_to"] = "ceo-maestro"
    errors = valid_director(bad, "departmentReturn")
    check("consumidor rejeita salto ao CEO", bool(errors))


def validate_legacy_manifest() -> None:
    text = ORIGIN_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^([0-9a-f]{64})\s+(\d+)\s+"
        r"(REESCRITO|NAO_COPIADO)\s+(.+)$",
        re.MULTILINE,
    )
    rows = {
        path: (sha, int(size), classification)
        for sha, size, classification, path in pattern.findall(text)
    }
    live: dict[str, tuple[str, int]] = {}
    if LEGACY_ROOT.is_dir():
        for path in sorted(LEGACY_ROOT.rglob("*")):
            if path.is_file():
                relative = path.relative_to(LEGACY_ROOT).as_posix()
                live[relative] = (
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    path.stat().st_size,
                )
    check("legado existe para prova de integridade", LEGACY_ROOT.is_dir())
    check("manifesto contém 87 arquivos", len(rows) == 87, str(len(rows)))
    check("legado ainda contém 87 arquivos", len(live) == 87, str(len(live)))
    check("manifesto e legado têm os mesmos caminhos", set(rows) == set(live))
    mismatches = [
        path
        for path, (sha, size) in live.items()
        if path not in rows or rows[path][:2] != (sha, size)
    ]
    check(
        "SHA-256 e bytes do legado permanecem intactos",
        not mismatches,
        ", ".join(mismatches[:5]),
    )
    check(
        "todo arquivo possui uma classe de recorte",
        all(row[2] in {"REESCRITO", "NAO_COPIADO"} for row in rows.values()),
    )


def main() -> int:
    print("== Departamento de QA e Usabilidade: validação ==")
    validate_structure()
    validate_metadata()
    validate_normative_source()
    validate_links_and_evals()
    validate_schema_shape()
    validate_positive_fixtures()
    validate_negative_fixtures()
    validate_behavioral_rules()
    validate_inherited_authority()
    validate_legacy_manifest()
    total = PASSED + FAILED
    print(f"\nRESULTADO: {PASSED}/{total} PASS; {FAILED} FAIL")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    # T55: recusa medir a Estrutura a partir do runtime, onde a raiz
    # resolve para .claude/skills e as skills do Catalogo viram pacotes.
    recusar_execucao_fora_da_fonte(STRUCTURE_ROOT)
    raise SystemExit(main())
