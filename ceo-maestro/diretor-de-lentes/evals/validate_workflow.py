from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "diretor-de-lentes.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
SKILL_PATH = PACKAGE_ROOT / "SKILL.md"
CONTRACT_PATH = PACKAGE_ROOT / "CONTRATO-DE-COMPROMISSO.md"
OPENAI_PATH = PACKAGE_ROOT / "agents" / "openai.yaml"
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(PACKAGE_ROOT.parents[1]))
).resolve()
CEO_ROOT = STRUCTURE_ROOT / "ceo-maestro"
CEO_SCHEMA_PATH = CEO_ROOT / "schemas" / "ceo-maestro.schema.json"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"

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

OPERATIONAL_DEPARTMENTS = [
    "departamento-arquitetura-software",
    "departamento-arquitetura-dados",
    "departamento-desenvolvimento",
    "departamento-design-ux-ui",
    "departamento-seguranca",
    "departamento-qa-usabilidade",
    "departamento-inovacao-melhoria",
    "departamento-auditoria-responsabilidades",
    "departamento-conteudo-marketing",
    "departamento-registros",
]


def causal(producer: str, candidate: str = "n/a", round_number: int = 1) -> dict[str, Any]:
    return {
        "work_item_id": "work-001",
        "front_id": "front-technical",
        "handoff_id": "handoff-001",
        "message_id": f"message-{producer}-001",
        "causation_message_ids": ["message-ceo-001"],
        "contract_id": "contract-001",
        "contract_version": 1,
        "contract_digest": digest("0"),
        "candidate_digest": candidate,
        "round": round_number,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": digest("1"),
        "created_at": "2026-07-26T16:00:00-03:00",
    }


def department_matrix() -> list[dict[str, Any]]:
    matrix = []
    for index, department in enumerate(OPERATIONAL_DEPARTMENTS):
        active = index in {0, 2, 5, 7}
        matrix.append(
            {
                "department": department,
                "mode": "ATUA" if active else "NAO_SE_APLICA",
                "reason": (
                    "Possui critério e entrega próprios."
                    if active
                    else "O domínio não é afetado por esta missão."
                ),
                "department_mission_ref": (
                    f"department-mission-{index + 1:02d}" if active else "n/a"
                ),
            }
        )
    return matrix


def director_plan() -> dict[str, Any]:
    return {
        "artifact_type": "DIRECTOR_PLAN",
        "director_plan_id": "director-plan-001",
        "causal": causal("diretor-de-lentes"),
        "executive_mission_ref": "mission-001",
        "state": "D_PLANNED",
        "department_matrix": department_matrix(),
        "dependencies": ["Arquitetura antes da implementação."],
        "integration_barriers": ["Contrato técnico aceito antes da construção."],
        "judge_gate_required": True,
        "blocking_pending_refs": [],
        "created_at": "2026-07-26T16:05:00-03:00",
    }


def department_mission(recipient: str = "departamento-desenvolvimento") -> dict[str, Any]:
    return {
        "artifact_type": "DEPARTMENT_MISSION",
        "department_mission_id": "department-mission-03",
        "causal": causal("diretor-de-lentes"),
        "recipient": recipient,
        "mode": "ATUA",
        "objective": "Entregar a implementação definida pelo contrato técnico.",
        "scope_in": ["Implementação do comportamento autorizado."],
        "scope_out": [],
        "inputs": ["contracts/technical-contract-v1.json"],
        "deliverables": ["artifacts/implementation.zip"],
        "done": ["Testes aplicáveis executados sem falha."],
        "required_evidence": ["evidence/test-report.json"],
        "depends_on": ["department-mission-01"],
        "handoff_to": ["diretor-de-lentes", "departamento-juizes"],
        "decision_authority": ["Microdesign dentro do contrato aceito."],
        "permissions": {
            "default_policy": "deny",
            "allowed_tools": [],
            "allowed_resources": [],
            "expires_at": "2026-07-27T16:00:00-03:00",
        },
        "stop_when": ["Escopo ou decisão vinculante divergir."],
        "return_to": "diretor-de-lentes",
        "issued_at": "2026-07-26T16:10:00-03:00",
    }


def department_return(
    department: str = "departamento-desenvolvimento",
) -> dict[str, Any]:
    candidate = digest("a")
    return {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "department-return-003",
        "causal": causal(department, candidate),
        "department_mission_ref": "department-mission-03",
        "returned_by": department,
        "state": "RETURNED",
        "scope_touched": ["Implementação do comportamento autorizado."],
        "artifact_refs": ["artifacts/implementation.zip"],
        "evidence_refs": ["evidence/test-report.json"],
        "candidate_digest": candidate,
        "test_summary": {
            "pass": 12,
            "fail": 0,
            "skip": 0,
            "skip_reasons": [],
            "critical_fail": False,
        },
        "pending_refs": [],
        "dissent_refs": [],
        "returned_to": "diretor-de-lentes",
        "returned_at": "2026-07-26T17:00:00-03:00",
    }


def judgment_request() -> dict[str, Any]:
    candidate = digest("a")
    return {
        "artifact_type": "JUDGMENT_REQUEST",
        "judgment_request_id": "judgment-request-001",
        "causal": causal("diretor-de-lentes", candidate),
        "department_return_ref": "department-return-003",
        "candidate_digest": candidate,
        "contract_digest": digest("0"),
        "applicable_criteria": ["Fidelidade, robustez e experiência."],
        "artifact_refs": ["artifacts/implementation.zip"],
        "evidence_refs": ["evidence/test-report.json"],
        "return_to": "diretor-de-lentes",
        "issued_at": "2026-07-26T17:05:00-03:00",
    }


def department_judge_report(
    scores: list[float] | None = None,
    verdict: str = "VALIDATED",
) -> dict[str, Any]:
    values = [9.5, 9.8, 10.0] if scores is None else scores
    candidate = digest("a")
    reproved = verdict == "REPROVED"
    return {
        "artifact_type": "DEPARTMENT_JUDGE_REPORT",
        "report_id": "department-judge-report-001",
        "causal": causal("departamento-juizes", candidate),
        "judgment_request_ref": "judgment-request-001",
        "candidate_digest": candidate,
        "contract_digest": digest("0"),
        "round": 1,
        "scorecard": [
            {
                "criterion_id": f"criterion-{index + 1:02d}",
                "score": score,
                "evidence_refs": [f"evidence/criterion-{index + 1:02d}.json"],
            }
            for index, score in enumerate(values)
        ],
        "minimum_score": min(values),
        "verdict": verdict,
        "critical_fail": False,
        "blocking_pending_refs": [],
        "evidence_refs": ["evidence/judge-report.json"],
        "criticisms": (
            ["A robustez ficou abaixo do contrato."] if reproved else []
        ),
        "required_changes": (
            ["Corrigir a falha e executar o reteste indicado."] if reproved else []
        ),
        "issued_at": "2026-07-26T17:10:00-03:00",
        "expires_at": "2026-07-27T17:10:00-03:00",
    }


def department_gate_record(
    scores: list[float] | None = None,
    verdict: str = "VALIDATED",
    decision: str = "ACCEPTED_FOR_INTEGRATION",
) -> dict[str, Any]:
    candidate = digest("a")
    return {
        "artifact_type": "DEPARTMENT_GATE_RECORD",
        "gate_record_id": "department-gate-record-001",
        "causal": causal("diretor-de-lentes", candidate),
        "department_mission": department_mission(),
        "department_return": department_return(),
        "judgment_request": judgment_request(),
        "judge_report": department_judge_report(scores, verdict),
        "decision": decision,
        "recorded_at": "2026-07-26T17:12:00-03:00",
    }


def executive_matrix_contract() -> dict[str, Any]:
    return {
        "mission_id": "mission-001",
        "causal": causal("ceo-maestro"),
        "recipients": ["diretor-de-lentes", "departamento-negocios"],
        "matrix_exchange": {
            "allowed": True,
            "topics": ["Viabilidade técnica e comercial."],
            "read_scope": ["Contrato e evidências compartilhadas."],
            "write_scope": ["Recomendação correlacionada."],
            "consolidation_owner": "diretor-de-lentes",
        },
    }


def matrix_exchange_message(
    sender: str = "diretor-de-lentes",
) -> dict[str, Any]:
    recipient = (
        "departamento-negocios"
        if sender == "diretor-de-lentes"
        else "diretor-de-lentes"
    )
    return {
        "artifact_type": "MATRIX_EXCHANGE_MESSAGE",
        "matrix_message_id": "matrix-message-001",
        "causal": causal(sender),
        "executive_mission_ref": "mission-001",
        "sender": sender,
        "recipient": recipient,
        "topic": "Viabilidade técnica e comercial.",
        "read_scope": ["Contrato e evidências compartilhadas."],
        "write_scope": ["Recomendação correlacionada."],
        "consolidation_owner": "diretor-de-lentes",
        "decision_requested": "Confirmar a compatibilidade entre valor e viabilidade.",
        "evidence_refs": ["evidence/matrix-analysis.json"],
        "sent_at": "2026-07-26T16:30:00-03:00",
    }


def rework_order() -> dict[str, Any]:
    candidate = digest("a")
    return {
        "artifact_type": "REWORK_ORDER",
        "rework_order_id": "rework-order-001",
        "causal": causal("diretor-de-lentes", candidate, 2),
        "department_mission_ref": "department-mission-03",
        "judge_report_ref": "judge-report-001",
        "target_department": "departamento-desenvolvimento",
        "below_cutoff_criteria": ["robustez: 9.49"],
        "required_changes": ["Cobrir a falha reproduzível indicada pelos Juízes."],
        "retest_criteria": ["Executar o teste de regressão ligado à crítica."],
        "round": 2,
        "max_rounds": 10,
        "return_to": "diretor-de-lentes",
        "issued_at": "2026-07-26T17:15:00-03:00",
    }


def director_gap() -> dict[str, Any]:
    return {
        "artifact_type": "DIRECTOR_CAPABILITY_GAP",
        "director_gap_id": "director-gap-001",
        "causal": causal("diretor-de-lentes"),
        "required_capability": "departamento-arquitetura-dados",
        "expected_path": (
            "diretor-de-lentes/departamentos-operacionais/"
            "departamento-arquitetura-dados/SKILL.md"
        ),
        "reason": "A skill e seu contrato ainda não foram migrados.",
        "impact": "A frente de dados não pode ser delegada.",
        "owner": "diretor-de-lentes",
        "safe_state": "D_BLOCKED",
        "recovery_condition": "Migrar e validar a capacidade no caminho aprovado.",
        "detected_at": "2026-07-26T16:05:00-03:00",
    }


def director_return(artifact_type: str = "PROGRESS") -> dict[str, Any]:
    blocked = artifact_type == "BLOCKED_RETURN"
    return {
        "artifact_type": artifact_type,
        "director_return_id": "director-return-001",
        "causal": causal("diretor-de-lentes"),
        "executive_mission_ref": "mission-001",
        "state": "D_BLOCKED" if blocked else "D_DELEGATED",
        "summary": (
            "Frente de dados bloqueada por capacidade ausente."
            if blocked
            else "Departamentos disponíveis receberam suas missões."
        ),
        "artifact_refs": [],
        "evidence_refs": ["evidence/capability-inventory.json"],
        "director_gap_refs": ["director-gap-001"] if blocked else [],
        "blocking_pending_refs": ["pending/data-capability"] if blocked else [],
        "next_event": "Migrar a capacidade ou receber os retornos contratados.",
        "returned_to": "ceo-maestro",
        "returned_at": "2026-07-26T16:20:00-03:00",
    }


def route_after_judgment(
    scores: list[float],
    verdict: str,
    *,
    critical_fail: bool = False,
    blocking_pending: bool = False,
    rules_compliant: bool = True,
    judges_available: bool = True,
    limitation_complete: bool = False,
    round_number: int = 1,
) -> str:
    if (
        not judges_available
        or not scores
        or critical_fail
        or blocking_pending
        or not rules_compliant
    ):
        return "D_BLOCKED"
    minimum_score = min(scores)
    if minimum_score >= 9.5 and verdict == "VALIDATED":
        return "D_READY_FOR_CEO"
    if minimum_score < 9.5 and limitation_complete:
        return "D_LIMITATION_VERIFIED"
    if round_number >= 10:
        return "D_LIMIT_REACHED_RETURNED"
    return "D_REWORK"


def matrix_allowed(
    recipients: list[str],
    allowed: bool,
    topics: list[str],
    read_scope: list[str],
    write_scope: list[str],
    owner: str | None,
) -> bool:
    both = {"diretor-de-lentes", "departamento-negocios"}.issubset(recipients)
    return (
        both
        and allowed
        and bool(topics)
        and bool(read_scope)
        and bool(write_scope)
        and owner in {"diretor-de-lentes", "departamento-negocios"}
    )


def validate_department_gate_record(
    record: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    errors = validate_schema(record, schema, schema)
    if errors:
        return errors

    mission_artifact = record["department_mission"]
    return_artifact = record["department_return"]
    request_artifact = record["judgment_request"]
    report_artifact = record["judge_report"]

    if return_artifact["department_mission_ref"] != mission_artifact[
        "department_mission_id"
    ]:
        errors.append("gate: retorno não referencia a missão departamental")
    if return_artifact["returned_by"] != mission_artifact["recipient"]:
        errors.append("gate: Departamento retornado difere do destinatário")
    if return_artifact["causal"]["producer"] != return_artifact["returned_by"]:
        errors.append("gate: produtor causal difere de returned_by")
    if request_artifact["department_return_ref"] != return_artifact[
        "department_return_id"
    ]:
        errors.append("gate: pedido não referencia o retorno")
    if report_artifact["judgment_request_ref"] != request_artifact[
        "judgment_request_id"
    ]:
        errors.append("gate: parecer não referencia o pedido")

    candidate_values = {
        record["causal"]["candidate_digest"],
        return_artifact["candidate_digest"],
        return_artifact["causal"]["candidate_digest"],
        request_artifact["candidate_digest"],
        request_artifact["causal"]["candidate_digest"],
        report_artifact["candidate_digest"],
        report_artifact["causal"]["candidate_digest"],
    }
    if len(candidate_values) != 1:
        errors.append("gate: candidate_digest divergente")

    contract_values = {
        record["causal"]["contract_digest"],
        mission_artifact["causal"]["contract_digest"],
        return_artifact["causal"]["contract_digest"],
        request_artifact["causal"]["contract_digest"],
        request_artifact["contract_digest"],
        report_artifact["causal"]["contract_digest"],
        report_artifact["contract_digest"],
    }
    if len(contract_values) != 1:
        errors.append("gate: contract_digest divergente")

    contract_ids = {
        artifact["causal"]["contract_id"]
        for artifact in [
            record,
            mission_artifact,
            return_artifact,
            request_artifact,
            report_artifact,
        ]
    }
    if len(contract_ids) != 1:
        errors.append("gate: contract_id divergente")

    contract_versions = {
        artifact["causal"]["contract_version"]
        for artifact in [
            record,
            mission_artifact,
            return_artifact,
            request_artifact,
            report_artifact,
        ]
    }
    if len(contract_versions) != 1:
        errors.append("gate: contract_version divergente")

    rounds = {
        record["causal"]["round"],
        mission_artifact["causal"]["round"],
        return_artifact["causal"]["round"],
        request_artifact["causal"]["round"],
        report_artifact["causal"]["round"],
        report_artifact["round"],
    }
    if len(rounds) != 1:
        errors.append("gate: rodada divergente")

    computed_minimum = min(
        item["score"] for item in report_artifact["scorecard"]
    )
    if report_artifact["minimum_score"] != computed_minimum:
        errors.append("gate: minimum_score não corresponde ao scorecard")

    if record["decision"] == "ACCEPTED_FOR_INTEGRATION":
        if report_artifact["verdict"] != "VALIDATED":
            errors.append("gate: integração aceita sem veredito VALIDATED")
        if computed_minimum < 9.5:
            errors.append("gate: integração aceita abaixo de 9,5")
        if report_artifact["critical_fail"]:
            errors.append("gate: integração aceita com falha crítica")
        if report_artifact["blocking_pending_refs"]:
            errors.append("gate: integração aceita com pendência bloqueante")
    return errors


def validate_matrix_exchange_message(
    message: dict[str, Any],
    mission_contract: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    errors = validate_schema(message, schema, schema)
    if errors:
        return errors
    matrix = mission_contract["matrix_exchange"]
    recipients = set(mission_contract["recipients"])
    if recipients != {"diretor-de-lentes", "departamento-negocios"}:
        errors.append("matriz: missão não contém os dois interlocutores")
    if not matrix["allowed"]:
        errors.append("matriz: troca não autorizada")
    if message["executive_mission_ref"] != mission_contract["mission_id"]:
        errors.append("matriz: referência da missão divergente")
    if message["topic"] not in matrix["topics"]:
        errors.append("matriz: tópico fora do contrato")
    if not set(message["read_scope"]).issubset(matrix["read_scope"]):
        errors.append("matriz: leitura fora do escopo")
    if not set(message["write_scope"]).issubset(matrix["write_scope"]):
        errors.append("matriz: escrita fora do escopo")
    if message["consolidation_owner"] != matrix["consolidation_owner"]:
        errors.append("matriz: dono da consolidação divergente")
    if message["causal"]["producer"] != message["sender"]:
        errors.append("matriz: produtor causal difere do remetente")
    causal_keys = ["contract_id", "contract_version", "contract_digest", "round"]
    for key in causal_keys:
        if message["causal"][key] != mission_contract["causal"][key]:
            errors.append(f"matriz: {key} divergente")
    if (
        message["causal"]["candidate_digest"]
        != mission_contract["causal"]["candidate_digest"]
    ):
        errors.append("matriz: candidate_digest divergente")
    return errors


def validate_ceo_authority_contract() -> list[str]:
    if not CEO_SCHEMA_PATH.is_file():
        return [f"schema do CEO ausente: {CEO_SCHEMA_PATH}"]
    schema = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))
    definitions = schema.get("$defs", {})
    checks = [
        (
            "capabilityGap",
            "producer",
            "ceo-maestro",
            "CAPABILITY_GAP deve ser autoria do CEO",
        ),
        (
            "exceptionRequest",
            "producer",
            "ceo-maestro",
            "EXCEPTION_REQUEST deve ser autoria do CEO",
        ),
        (
            "executiveDecision",
            "producer",
            "ceo-maestro",
            "decisão executiva deve ser autoria do CEO",
        ),
        (
            "exceptionAuthorization",
            "authorized_by",
            "jeremias",
            "autorização de exceção deve ser de Jeremias",
        ),
        (
            "judgeReport",
            "producer",
            "departamento-juizes",
            "JUDGE_REPORT deve ser autoria dos Juízes",
        ),
    ]
    errors: list[str] = []
    for definition, property_name, expected, message in checks:
        if definition not in definitions:
            errors.append(f"CEO schema sem $defs/{definition}")
        elif not find_const(
            definitions[definition], property_name, expected
        ):
            errors.append(message)
    return errors


def validate_package() -> list[str]:
    errors: list[str] = []
    required_local = [
        SKILL_PATH,
        CONTRACT_PATH,
        OPENAI_PATH,
        SCHEMA_PATH,
        EVALS_PATH,
        PACKAGE_ROOT / "evals" / "PLACAR.md",
        PACKAGE_ROOT / "evals" / "FORWARD-TEST.md",
        PACKAGE_ROOT / "references" / "workflow-operacional.md",
        PACKAGE_ROOT / "references" / "protocolo-de-handoff.md",
        PACKAGE_ROOT / "references" / "gate-juizes-e-retrabalho.md",
        PACKAGE_ROOT / "references" / "comunicacao-matricial-negocios.md",
        PACKAGE_ROOT / "references" / "bootstrap.md",
        PACKAGE_ROOT / "references" / "origem-migracao.md",
        PACKAGE_ROOT
        / "references"
        / "adr-001-diretoria-e-camada-de-juizes.md",
    ]
    errors.extend(validate_required_files(required_local, "arquivo local"))
    required_external = [
        STRUCTURE_ROOT / "AGENTS.md",
        CEO_ROOT / "SKILL.md",
        CEO_SCHEMA_PATH,
        RULES_PATH,
        STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
    ]
    errors.extend(validate_required_files(required_external, "vínculo externo"))
    errors.extend(validate_frontmatter(SKILL_PATH, "diretor-de-lentes"))
    errors.extend(
        validate_openai_yaml(
            OPENAI_PATH,
            "Diretor de Lentes",
            "$diretor-de-lentes",
            expected_short="Coordena Departamentos e o gate dos Juízes",
        )
    )
    errors.extend(
        validate_links(
            PACKAGE_ROOT,
            exclude=[PACKAGE_ROOT / "departamento-juizes",
                     PACKAGE_ROOT / "departamentos-operacionais"],
        )
    )

    skill = SKILL_PATH.read_text(encoding="utf-8")
    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    required_tokens = [
        "ceo-maestro",
        "departamento-negocios",
        "departamento-juizes",
        "DIRECTOR_CAPABILITY_GAP",
        "EXECUTIVE_SUBMISSION",
        "LIMITATION_REPORT",
        "9,49",
        "Jeremias",
        "../../regras-de-ouro/REGRAS-DE-OURO.md",
    ]
    for token in required_tokens:
        if token not in skill:
            errors.append(f"SKILL.md sem contrato obrigatório: {token}")
    if "../../regras-de-ouro/REGRAS-DE-OURO.md" not in contract:
        errors.append("contrato sem fonte normativa única")
    return errors


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_defs = {
        "directorPlan",
        "departmentMission",
        "departmentReturn",
        "judgmentRequest",
        "departmentJudgeReport",
        "departmentGateRecord",
        "reworkOrder",
        "matrixExchangeMessage",
        "directorCapabilityGap",
        "directorReturn",
    }
    missing = expected_defs.difference(schema.get("$defs", {}))
    if missing:
        errors.append(f"schema sem defs: {sorted(missing)}")

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


def run() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))

    cases: list[tuple[str, bool, list[str]]] = []

    cases.append(("pacote, vínculos e metadata", True, validate_package()))
    cases.append(("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT)))
    cases.append(("schema e referências locais", True, validate_schema_shape(schema)))
    cases.append(
        (
            "autoridades herdadas do schema do CEO",
            True,
            validate_ceo_authority_contract(),
        )
    )
    eval_errors = []
    if evals.get("skill") != "diretor-de-lentes":
        eval_errors.append("evals: skill incorreta")
    if len(evals.get("cases", [])) < 12:
        eval_errors.append("evals: necessários ao menos 12 casos")
    if not any(case.get("origem") == "real" for case in evals.get("cases", [])):
        eval_errors.append("evals: falta caso real")
    if not all("$diretor-de-lentes" not in case["prompt"] for case in evals["cases"]):
        eval_errors.append("evals: prompts devem testar acionamento sem nomear $skill")
    cases.append(("catálogo de evals", True, eval_errors))

    fixtures = [
        ("DIRECTOR_PLAN", director_plan()),
        ("DEPARTMENT_MISSION", department_mission()),
        ("DEPARTMENT_RETURN", department_return()),
        (
            "DEPARTMENT_RETURN de Conteúdo e Marketing",
            department_return("departamento-conteudo-marketing"),
        ),
        ("JUDGMENT_REQUEST", judgment_request()),
        ("DEPARTMENT_JUDGE_REPORT", department_judge_report()),
        ("DEPARTMENT_GATE_RECORD", department_gate_record()),
        ("REWORK_ORDER", rework_order()),
        ("MATRIX_EXCHANGE_MESSAGE", matrix_exchange_message()),
        ("DIRECTOR_CAPABILITY_GAP", director_gap()),
        ("PROGRESS", director_return("PROGRESS")),
        ("BLOCKED_RETURN", director_return("BLOCKED_RETURN")),
    ]
    for label, fixture in fixtures:
        cases.append(
            (
                f"schema aceita {label}",
                True,
                validate_schema(fixture, schema, schema),
            )
        )

    agent_mission = department_mission("agente-seguranca-aplicacao")
    cases.append(
        (
            "schema rejeita bypass para agente",
            False,
            validate_schema(agent_mission, schema, schema),
        )
    )

    incomplete_plan = director_plan()
    incomplete_plan["department_matrix"].pop()
    cases.append(
        (
            "plano exige dez Departamentos",
            False,
            validate_schema(incomplete_plan, schema, schema),
        )
    )

    duplicate_plan = director_plan()
    duplicate_plan["department_matrix"][-1] = copy.deepcopy(
        duplicate_plan["department_matrix"][0]
    )
    duplicate_plan["department_matrix"][-1]["reason"] = (
        "Duplicata com conteúdo diferente para testar a cobertura exata."
    )
    duplicate_errors = validate_schema(duplicate_plan, schema, schema)
    departments = [
        item["department"] for item in duplicate_plan["department_matrix"]
    ]
    if len(departments) != len(set(departments)):
        duplicate_errors.append("matriz contém Departamento duplicado")
    cases.append(("matriz não aceita cobertura duplicada", False, duplicate_errors))

    accepted_return = department_return()
    accepted_return["state"] = "ACCEPTED"
    cases.append(
        (
            "retorno departamental não se autoaceita",
            False,
            validate_schema(accepted_return, schema, schema),
        )
    )

    spoofed_plan = director_plan()
    spoofed_plan["causal"]["producer"] = "departamento-negocios"
    cases.append(
        (
            "plano exige autoria do Diretor",
            False,
            validate_schema(spoofed_plan, schema, schema),
        )
    )

    spoofed_return = department_return()
    spoofed_return["causal"]["producer"] = "departamento-seguranca"
    cases.append(
        (
            "retorno exige produtor igual ao Departamento",
            False,
            validate_schema(spoofed_return, schema, schema),
        )
    )

    cases.append(
        (
            "cadeia retorno-pedido-Juízes íntegra",
            True,
            validate_department_gate_record(
                department_gate_record(), schema
            ),
        )
    )

    mismatched_candidate = department_gate_record()
    mismatched_candidate["judge_report"]["candidate_digest"] = digest("b")
    cases.append(
        (
            "gate rejeita candidato divergente",
            False,
            validate_department_gate_record(
                mismatched_candidate, schema
            ),
        )
    )

    mismatched_contract = department_gate_record()
    mismatched_contract["judgment_request"]["contract_digest"] = digest("c")
    cases.append(
        (
            "gate rejeita contrato divergente",
            False,
            validate_department_gate_record(
                mismatched_contract, schema
            ),
        )
    )

    mismatched_version = department_gate_record()
    mismatched_version["department_mission"]["causal"]["contract_version"] = 2
    cases.append(
        (
            "gate rejeita versão de contrato divergente",
            False,
            validate_department_gate_record(
                mismatched_version, schema
            ),
        )
    )

    mismatched_round = department_gate_record()
    mismatched_round["department_mission"]["causal"]["round"] = 2
    cases.append(
        (
            "gate rejeita missão de outra rodada",
            False,
            validate_department_gate_record(
                mismatched_round, schema
            ),
        )
    )

    below_gate = department_gate_record(
        [9.49, 10.0, 10.0],
        "REPROVED",
        "ACCEPTED_FOR_INTEGRATION",
    )
    cases.append(
        (
            "gate departamental não aceita 9,49",
            False,
            validate_department_gate_record(below_gate, schema),
        )
    )

    missing_report = department_gate_record()
    missing_report.pop("judge_report")
    cases.append(
        (
            "gate exige parecer dos Juízes",
            False,
            validate_department_gate_record(missing_report, schema),
        )
    )

    cases.append(
        (
            "troca matricial correlacionada",
            True,
            validate_matrix_exchange_message(
                matrix_exchange_message(),
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    matrix_outside_topic = matrix_exchange_message()
    matrix_outside_topic["topic"] = "Alterar o orçamento do produto."
    cases.append(
        (
            "troca matricial rejeita tópico externo",
            False,
            validate_matrix_exchange_message(
                matrix_outside_topic,
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    matrix_spoofed = matrix_exchange_message()
    matrix_spoofed["causal"]["producer"] = "departamento-negocios"
    cases.append(
        (
            "troca matricial rejeita remetente forjado",
            False,
            validate_matrix_exchange_message(
                matrix_spoofed,
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    matrix_wrong_candidate = matrix_exchange_message()
    matrix_wrong_candidate["causal"]["candidate_digest"] = digest("d")
    cases.append(
        (
            "troca matricial rejeita candidato divergente",
            False,
            validate_matrix_exchange_message(
                matrix_wrong_candidate,
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    judges_gap = director_gap()
    judges_gap["required_capability"] = "departamento-juizes"
    cases.append(
        (
            "lacuna interna aceita Juízes ausentes",
            True,
            validate_schema(judges_gap, schema, schema),
        )
    )

    wrong_gap = director_gap()
    wrong_gap["required_capability"] = "departamento-negocios"
    cases.append(
        (
            "lacuna dirigida rejeita capacidade lateral",
            False,
            validate_schema(wrong_gap, schema, schema),
        )
    )

    progress_blocked = director_return("PROGRESS")
    progress_blocked["state"] = "D_BLOCKED"
    cases.append(
        (
            "PROGRESS não mascara estado bloqueado",
            False,
            validate_schema(progress_blocked, schema, schema),
        )
    )

    checks = [
        (
            "corte exato 9,5 prepara CEO",
            route_after_judgment([9.5, 9.7, 10.0], "VALIDATED")
            == "D_READY_FOR_CEO",
        ),
        (
            "9,49 não arredonda",
            route_after_judgment([9.49, 10.0, 10.0], "REPROVED") == "D_REWORK",
        ),
        (
            "média alta não compensa menor nota",
            route_after_judgment([9.0, 10.0, 10.0], "REPROVED") == "D_REWORK",
        ),
        (
            "Auditoria não substitui Juízes ausentes",
            route_after_judgment(
                [10.0], "VALIDATED", judges_available=False
            )
            == "D_BLOCKED",
        ),
        (
            "falha crítica bloqueia",
            route_after_judgment([10.0], "VALIDATED", critical_fail=True)
            == "D_BLOCKED",
        ),
        (
            "RI/RO violada bloqueia",
            route_after_judgment([10.0], "VALIDATED", rules_compliant=False)
            == "D_BLOCKED",
        ),
        (
            "pendência bloqueante impede submissão",
            route_after_judgment(
                [10.0], "VALIDATED", blocking_pending=True
            )
            == "D_BLOCKED",
        ),
        (
            "limite completo segue ao CEO sem validar",
            route_after_judgment(
                [9.3, 10.0], "REPROVED", limitation_complete=True
            )
            == "D_LIMITATION_VERIFIED",
        ),
        (
            "décima rodada retorna limite ao CEO",
            route_after_judgment(
                [9.4, 10.0], "REPROVED", round_number=10
            )
            == "D_LIMIT_REACHED_RETURNED",
        ),
        (
            "troca matricial completa é permitida",
            matrix_allowed(
                ["diretor-de-lentes", "departamento-negocios"],
                True,
                ["Viabilidade."],
                ["Contrato."],
                ["Recomendação."],
                "diretor-de-lentes",
            ),
        ),
        (
            "troca com destinatário único é negada",
            not matrix_allowed(
                ["diretor-de-lentes"],
                True,
                ["Viabilidade."],
                ["Contrato."],
                ["Recomendação."],
                "diretor-de-lentes",
            ),
        ),
        (
            "troca sem dono único é negada",
            not matrix_allowed(
                ["diretor-de-lentes", "departamento-negocios"],
                True,
                ["Viabilidade."],
                ["Contrato."],
                ["Recomendação."],
                None,
            ),
        ),
        (
            "digest das regras é verificável",
            RULES_PATH.is_file() and sha256_file(RULES_PATH).startswith("sha256:"),
        ),
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
