"""Validador determinístico do Departamento de Auditoria e Responsabilidades.

Verifica o pacote (arquivos, metadata, links), o schema interno, os artefatos
internos e — como regressão de fronteira — que os envelopes produzidos são
aceitos pelos schemas do `diretor-de-lentes` e do `ceo-maestro`.

Uso: python evals/validate_workflow.py
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
SCHEMA_PATH = (
    PACKAGE_ROOT / "schemas" / "departamento-auditoria-responsabilidades.schema.json"
)
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
AGENTS_ROOT = PACKAGE_ROOT / "agentes"

OPERATIONS_ROOT = PACKAGE_ROOT.parent
DIRECTOR_ROOT = OPERATIONS_ROOT.parent
CEO_ROOT = DIRECTOR_ROOT.parent
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(CEO_ROOT.parent))
).resolve()
DIRECTOR_SCHEMA_PATH = DIRECTOR_ROOT / "schemas" / "diretor-de-lentes.schema.json"
CEO_SCHEMA_PATH = CEO_ROOT / "schemas" / "ceo-maestro.schema.json"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"

DEPARTMENT = "departamento-auditoria-responsabilidades"
AGENT_NAMES = [
    "agente-reconciliar-contrato-e-autoridade",
    "agente-verificar-governanca-e-responsabilidades",
    "agente-conferir-evidencias-e-artefatos",
]
AGENT_CAPABILITY = {
    "agente-reconciliar-contrato-e-autoridade": "contrato-e-autoridade",
    "agente-verificar-governanca-e-responsabilidades": "governanca-e-responsabilidades",
    "agente-conferir-evidencias-e-artefatos": "evidencias-e-artefatos",
}
DIMENSIONS = [
    "INTENT",
    "AUTH",
    "ESCOPO",
    "PENDING",
    "RACI",
    "RI_RO",
    "SURPRESAS_BYPASS",
    "EVIDENCIA",
    "ARTEFATOS_TWINS",
    "RASTREABILIDADE",
]
OWNER = {
    "INTENT": "contrato-e-autoridade",
    "AUTH": "contrato-e-autoridade",
    "ESCOPO": "contrato-e-autoridade",
    "PENDING": "contrato-e-autoridade",
    "RACI": "governanca-e-responsabilidades",
    "RI_RO": "governanca-e-responsabilidades",
    "SURPRESAS_BYPASS": "governanca-e-responsabilidades",
    "EVIDENCIA": "evidencias-e-artefatos",
    "ARTEFATOS_TWINS": "evidencias-e-artefatos",
    "RASTREABILIDADE": "evidencias-e-artefatos",
}
SECONDARY = {
    "PENDING": "governanca-e-responsabilidades",
    "SURPRESAS_BYPASS": "contrato-e-autoridade",
}
SEVERITY = [
    "NAO_APLICAVEL",
    "CONFORME",
    "RESSALVA",
    "NAO_PROVADO",
    "NAO_CONFORME",
]
BLOCKING_STATES = {"NAO_CONFORME", "NAO_PROVADO"}
RULES_LINK_DEPARTMENT = "../../../../regras-de-ouro/REGRAS-DE-OURO.md"
RULES_LINK_AGENT = "../../../../../../regras-de-ouro/REGRAS-DE-OURO.md"

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        collect_property_names,
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

FORBIDDEN_SCORE_KEYS = {
    "score",
    "nota",
    "notas",
    "minimum_score",
    "absolute_score",
    "scorecard",
    "cut_score",
}



# --------------------------------------------------------------------------
# Regras comportamentais, recalculadas em código
# --------------------------------------------------------------------------

def worst_state(states: list[str]) -> str:
    """O estado mais grave vence. Nunca média, consenso ou o mais favorável."""
    return max(states, key=SEVERITY.index)


def decide_verdict(states: dict[str, str]) -> str:
    if any(state in BLOCKING_STATES for state in states.values()):
        return "REPROVADO"
    if any(state == "RESSALVA" for state in states.values()):
        return "APROVADO_COM_RESSALVAS"
    return "APROVADO"


def to_governance(internal_verdict: str) -> str:
    return "NONCOMPLIANT" if internal_verdict == "REPROVADO" else "COMPLIANT"


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

CANDIDATE = digest("a")
CONTRACT = digest("0")
PRODUCER = digest("1")
RULES_DIGEST = digest("2")


def causal(producer: str = DEPARTMENT) -> dict[str, Any]:
    return {
        "work_item_id": "work-001",
        "front_id": "front-technical",
        "handoff_id": "handoff-001",
        "message_id": "message-auditoria-001",
        "causation_message_ids": ["message-diretor-001"],
        "contract_id": "contract-001",
        "contract_version": 1,
        "contract_digest": CONTRACT,
        "candidate_digest": CANDIDATE,
        "round": 1,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": PRODUCER,
        "created_at": "2026-07-26T20:00:00-03:00",
    }


def custody_entry(auditor: str, index: int) -> dict[str, Any]:
    return {
        "evidence_ref": f"evidence-{index:02d}",
        "artifact_ref": f"evidence/artefato-{index:02d}.json",
        "source_version": "commit-9f2c1a",
        "artifact_digest": digest("b"),
        "collected_by": "departamento-desenvolvimento",
        "collected_at": "2026-07-26T19:30:00-03:00",
        "handed_from": "diretor-de-lentes",
        "handed_to": auditor,
        "handed_at": "2026-07-26T20:05:00-03:00",
        "access_mode": "read-only",
    }


def task_dimensions(auditor: str) -> list[dict[str, Any]]:
    capability = AGENT_CAPABILITY[auditor]
    items = [
        {"dimension": dim, "role": "owner"}
        for dim in DIMENSIONS
        if OWNER[dim] == capability
    ]
    items += [
        {"dimension": dim, "role": "secondary"}
        for dim in DIMENSIONS
        if SECONDARY.get(dim) == capability
    ]
    return items


def audit_task(auditor: str = "agente-reconciliar-contrato-e-autoridade") -> dict[str, Any]:
    return {
        "artifact_type": "AUDIT_TASK",
        "task_id": f"task-{auditor}",
        "causal": causal(),
        "auditor_id": auditor,
        "capability": AGENT_CAPABILITY[auditor],
        "candidate_digest": CANDIDATE,
        "dimensions": task_dimensions(auditor),
        "scope_in": ["Dimensões atribuídas a esta capacidade."],
        "scope_out": ["Dimensões das outras duas capacidades."],
        "inputs": ["dossie/contrato-v1.json", "dossie/diff-escopo.txt"],
        "checks": ["Contrato canônico v1, cláusula de escopo autorizado."],
        "evidence_required": ["Diff do escopo tocado, com versão."],
        "custody_chain": [custody_entry(auditor, 1), custody_entry(auditor, 2)],
        "review_chain": {
            "conflict_checked_by": DEPARTMENT,
            "solution_participant_conflict": False,
            "expected_conclusion_withheld": True,
            "prior_votes_withheld": True,
        },
        "forbidden_context": [
            "conclusão esperada ou veredito desejado",
            "recibos dos outros agentes",
            "racionalização do produtor",
            "rodada anterior e histórico de retrabalho",
        ],
        "stop_when": ["Todas as dimensões atribuídas têm estado."],
        "return_to": DEPARTMENT,
        "issued_at": "2026-07-26T20:10:00-03:00",
    }


def dimension_state(
    dimension: str,
    state: str = "CONFORME",
) -> dict[str, Any]:
    return {
        "dimension": dimension,
        "state": state,
        "reason": f"Verificado contra o dossiê para {dimension}.",
        "evidence_refs": [] if state == "NAO_PROVADO" else ["evidence-01"],
        "not_applicable_reason": (
            "Este candidato não expõe interface pública nesta rodada."
            if state == "NAO_APLICAVEL"
            else "n/a"
        ),
    }


def finding(dimension: str = "AUTH", severity: str = "BLOCKER") -> dict[str, Any]:
    return {
        "finding_id": f"finding-{dimension.lower()}",
        "dimension": dimension,
        "criterion_ref": "Contrato v1, cláusula de autorização anterior.",
        "evidence_refs": ["evidence-01"],
        "artifact_refs": ["evidence/artefato-01.json"],
        "severity": severity,
        "blocking": severity in {"BLOCKER", "HIGH"},
        "owner_role": "departamento-desenvolvimento",
        "corrective_condition": "Obter autorização anterior e reexecutar a publicação.",
    }


def audit_receipt(
    auditor: str = "agente-reconciliar-contrato-e-autoridade",
    states: dict[str, str] | None = None,
    findings: list[dict[str, Any]] | None = None,
    status: str = "COMPLETED",
) -> dict[str, Any]:
    assigned = [item["dimension"] for item in task_dimensions(auditor)]
    values = states or {dim: "CONFORME" for dim in assigned}
    receipt: dict[str, Any] = {
        "artifact_type": "AUDIT_RECEIPT",
        "task_id": f"task-{auditor}",
        "auditor_id": auditor,
        "capability": AGENT_CAPABILITY[auditor],
        "contract_digest": CONTRACT,
        "candidate_digest": CANDIDATE,
        "review_chain": {
            "context_clean": True,
            "independent": True,
            "reviewed_at": "2026-07-26T20:40:00-03:00",
            "reviewed_input_refs": ["evidence-01", "evidence-02"],
        },
        "dimension_states": [
            dimension_state(dim, state) for dim, state in values.items()
        ],
        "findings": findings or [],
        "scope_observed": ["Diff do escopo tocado."],
        "pending": [],
        "status": status,
        "return_to": DEPARTMENT,
        "issued_at": "2026-07-26T20:45:00-03:00",
    }
    if status == "BLOCKED":
        receipt["dimension_states"] = []
        receipt["findings"] = []
        receipt["blocked_reason"] = "Contexto contaminado: conclusão esperada presente."
    return receipt


def conformity_matrix(states: dict[str, str] | None = None) -> dict[str, Any]:
    values = states or {dim: "CONFORME" for dim in DIMENSIONS}
    return {
        "artifact_type": "CONFORMITY_MATRIX",
        "conformity_matrix_id": "conformity-matrix-001",
        "causal": causal(),
        "department_mission_ref": "department-mission-07",
        "dimensions": [
            {
                "dimension": dim,
                "state": values[dim],
                "owner_capability": OWNER[dim],
                "secondary_capability": SECONDARY.get(dim, "n/a"),
                "receipt_refs": [f"task-{name}" for name in AGENT_NAMES],
                "reason": f"Estado consolidado da dimensão {dim}.",
                "evidence_refs": ["evidence-01"],
            }
            for dim in DIMENSIONS
        ],
        "divergences": [],
        "created_at": "2026-07-26T21:00:00-03:00",
    }


def capability_gap() -> dict[str, Any]:
    return {
        "artifact_type": "AUDIT_CAPABILITY_GAP",
        "capability": "Evidências e artefatos sem inspetor nesta rodada.",
        "auditor_id": "agente-conferir-evidencias-e-artefatos",
        "dimensions": ["EVIDENCIA", "ARTEFATOS_TWINS", "RASTREABILIDADE"],
        "expected_contract": "Frescor, custódia, artefatos reais e rastreabilidade conferidos.",
        "discovery_evidence": "SEM_RETORNO observado na tarefa task-agente-conferir.",
        "impact": "Três dimensões ficam NAO_PROVADO e o veredito não pode ser positivo.",
        "status": "OPEN",
        "owner": "diretor-de-lentes",
    }


def audit_ledger(
    states: dict[str, str] | None = None,
    gaps: list[dict[str, Any]] | None = None,
    with_assignments: bool = True,
    dossier_missing: list[str] | None = None,
) -> dict[str, Any]:
    values = states or {dim: "CONFORME" for dim in DIMENSIONS}
    internal = decide_verdict(values)
    governance = to_governance(internal)
    violations = [
        f"{dim}: {values[dim]} — dimensão bloqueada, dono departamento-desenvolvimento."
        for dim in DIMENSIONS
        if values[dim] in BLOCKING_STATES
    ]
    ressalvas = [
        {
            "dimension": dim,
            "owner_role": "departamento-desenvolvimento",
            "impact": "Rastreabilidade parcial em um critério não bloqueante.",
            "closing_condition": "Publicar o índice de evidências da rodada.",
        }
        for dim in DIMENSIONS
        if values[dim] == "RESSALVA"
    ]
    return {
        "artifact_type": "AUDIT_LEDGER",
        "audit_ledger_id": "audit-ledger-001",
        "causal": causal(),
        "department_mission_ref": "department-mission-07",
        "dossier_missing": dossier_missing or [],
        "assignments": (
            [
                {
                    "task_id": f"task-{name}",
                    "auditor_id": name,
                    "capability": AGENT_CAPABILITY[name],
                    "issued_at": "2026-07-26T20:10:00-03:00",
                    "destination": f"auditoria/task-{name}/",
                }
                for name in AGENT_NAMES
            ]
            if with_assignments
            else []
        ),
        "panel": [
            {
                "auditor_id": name,
                "capability": AGENT_CAPABILITY[name],
                "status": "COMPLETED",
                "substrate": "desconhecido",
                "tier": "desconhecido",
            }
            for name in AGENT_NAMES
        ],
        "conformity_matrix": conformity_matrix(values),
        "findings": [finding()] if violations else [],
        "internal_verdict": internal,
        "governance_verdict": governance,
        "violations": violations,
        "ressalvas": ressalvas,
        "capability_gaps": gaps or [],
        "evidence_refs": ["evidence/artefato-01.json"],
        "executive_decisions_required": [],
        "pending": [
            "R6 — a existência do painel auditor não é verificável pelo runtime;"
            " registro de emissão anexado."
        ]
        + [
            f"Ressalva em {item['dimension']}: {item['closing_condition']}"
            for item in ressalvas
        ],
        "return_to": "diretor-de-lentes",
        "recorded_at": "2026-07-26T21:10:00-03:00",
    }


# --------------------------------------------------------------------------
# Derivação para os envelopes de fronteira
# --------------------------------------------------------------------------

def derive_governance_report(ledger: dict[str, Any]) -> dict[str, Any]:
    """Converte o AUDIT_LEDGER interno no envelope que o CEO consome."""
    return {
        "report_id": "governance-report-001",
        "auditor_ref": DEPARTMENT,
        "auditor_digest": PRODUCER,
        "candidate_digest": ledger["causal"]["candidate_digest"],
        "contract_digest": ledger["causal"]["contract_digest"],
        "rules_digest": RULES_DIGEST,
        "verdict": ledger["governance_verdict"],
        "violations": ledger["violations"],
        "evidence_refs": ledger["evidence_refs"],
        "issued_at": "2026-07-26T21:10:00-03:00",
    }


def derive_department_return(ledger: dict[str, Any]) -> dict[str, Any]:
    """Converte o AUDIT_LEDGER interno no envelope que o Diretor consome."""
    causal_header = copy.deepcopy(ledger["causal"])
    return {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "department-return-007",
        "causal": causal_header,
        "department_mission_ref": ledger["department_mission_ref"],
        "returned_by": DEPARTMENT,
        "state": "RETURNED",
        "scope_touched": ["Auditoria das dez dimensões de conformidade."],
        "artifact_refs": ["auditoria/governance-report-001.json"],
        "evidence_refs": ledger["evidence_refs"],
        "candidate_digest": ledger["causal"]["candidate_digest"],
        "test_summary": {
            "pass": 0,
            "fail": 0,
            "skip": 0,
            "skip_reasons": [],
            "critical_fail": False,
        },
        "pending_refs": [f"pending/{index:02d}" for index in range(len(ledger["pending"]))],
        "dissent_refs": [],
        "returned_to": "diretor-de-lentes",
        "returned_at": "2026-07-26T21:15:00-03:00",
    }


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
        PACKAGE_ROOT / "references" / "protocolo-auditoria.md",
        PACKAGE_ROOT / "references" / "dimensoes-e-conformidade.md",
        PACKAGE_ROOT / "references" / "origem-migracao.md",
        PACKAGE_ROOT / "references" / "adr-003-conformidade-sem-nota.md",
    ]
    errors.extend(validate_required_files(required_local, "arquivo local"))

    required_external = [
        DIRECTOR_SCHEMA_PATH,
        CEO_SCHEMA_PATH,
        RULES_PATH,
        DIRECTOR_ROOT / "SKILL.md",
        DIRECTOR_ROOT / "departamento-juizes" / "SKILL.md",
        STRUCTURE_ROOT / "ORGANOGRAMA.md",
        STRUCTURE_ROOT / "GUIA-DE-EXPANSAO-E-MIGRACAO.md",
        STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
    ]
    errors.extend(validate_required_files(required_external, "vínculo externo"))

    if PACKAGE_ROOT.parent.name != "departamentos-operacionais":
        errors.append(
            "o Departamento deve viver sob departamentos-operacionais/, "
            f"está sob {PACKAGE_ROOT.parent.name}/"
        )

    errors.extend(validate_agents_folder(AGENTS_ROOT, AGENT_NAMES))
    return errors


def validate_metadata() -> list[str]:
    errors = validate_frontmatter(SKILL_PATH, DEPARTMENT)
    errors.extend(
        validate_openai_yaml(
            OPENAI_PATH,
            "Departamento de Auditoria e Responsabilidades",
            f"${DEPARTMENT}",
        )
    )
    displays = {
        "agente-reconciliar-contrato-e-autoridade": "Auditor de Contrato e Autoridade",
        "agente-verificar-governanca-e-responsabilidades": "Auditor de Governança e Responsabilidades",
        "agente-conferir-evidencias-e-artefatos": "Auditor de Evidências e Artefatos",
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
        "departamento-juizes",
        "AUDIT_TASK",
        "AUDIT_RECEIPT",
        "GOVERNANCE_REPORT",
        "DEPARTMENT_RETURN",
        "APROVADO_COM_RESSALVAS",
        "NAO_PROVADO",
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
        if DEPARTMENT not in agent_skill:
            errors.append(f"{name}: SKILL.md sem o superior declarado")
    return errors


def validate_no_scoring(schema: dict[str, Any]) -> list[str]:
    """ADR-003: este Departamento não pontua. O schema não pode ter campo de nota."""
    found: set[str] = set()
    collect_property_names(schema, found)
    offenders = sorted(found.intersection(FORBIDDEN_SCORE_KEYS))
    if offenders:
        return [f"schema contém campo de pontuação proibido pelo ADR-003: {offenders}"]
    return []


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "auditTask",
        "auditReceipt",
        "conformityMatrix",
        "auditCapabilityGap",
        "auditLedger",
    }
    missing = expected.difference(schema.get("$defs", {}))
    if missing:
        errors.append(f"schema sem defs: {sorted(missing)}")
    auditor_enum = schema.get("$defs", {}).get("auditorId", {}).get("enum", [])
    if sorted(auditor_enum) != sorted(AGENT_NAMES):
        errors.append(f"auditorId do schema divergente das pastas de agentes/: {auditor_enum}")
    dimension_enum = schema.get("$defs", {}).get("dimension", {}).get("enum", [])
    if dimension_enum != DIMENSIONS:
        errors.append(f"as dez dimensões do schema divergem da referência: {dimension_enum}")

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
        (ceo, "governanceReport", "auditor_ref", DEPARTMENT,
         "o relatório de governança deve ser autoria da Auditoria"),
        (ceo, "judgeReport", "producer", "departamento-juizes",
         "a nota continua sendo dos Juízes, não da Auditoria"),
        (ceo, "exceptionAuthorization", "authorized_by", "jeremias",
         "só Jeremias autoriza exceção"),
        (director, "departmentMission", "return_to", "diretor-de-lentes",
         "a missão departamental deve retornar ao Diretor"),
        (director, "departmentReturn", "returned_to", "diretor-de-lentes",
         "o retorno departamental deve ir ao Diretor"),
        (director, "departmentJudgeReport", "producer", "departamento-juizes",
         "o parecer de julgamento continua sendo dos Juízes"),
    ]
    for definitions, name, prop, expected, message in checks:
        if name not in definitions:
            errors.append(f"schema de fronteira sem $defs/{name}")
        elif not find_const(definitions[name], prop, expected):
            errors.append(message)

    governance = ceo.get("governanceReport", {})
    if "score" in governance.get("properties", {}):
        errors.append("governanceReport do CEO não deveria ter campo de nota")
    verdict_enum = governance.get("properties", {}).get("verdict", {}).get("enum", [])
    if sorted(verdict_enum) != ["COMPLIANT", "NONCOMPLIANT"]:
        errors.append(f"governanceReport do CEO mudou o enum de veredito: {verdict_enum}")

    operational = director.get("operationalDepartment", {}).get("enum", [])
    if DEPARTMENT not in operational:
        errors.append("o Diretor não reconhece este Departamento como operacional")
    return errors


def validate_evals() -> list[str]:
    errors: list[str] = []
    evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    if evals.get("skill") != DEPARTMENT:
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
        if f"${DEPARTMENT}" in case["prompt"]:
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
    governance_def = ceo_schema["$defs"]["governanceReport"]

    cases: list[tuple[str, bool, list[str]]] = []

    cases.append(("pacote, agentes e vínculos externos", True, validate_structure()))
    cases.append(("metadata da gerente e dos três agentes", True, validate_metadata()))
    cases.append(("fonte normativa única e tokens de contrato", True, validate_normative_source()))
    cases.append(("links internos do pacote resolvem", True, validate_links(PACKAGE_ROOT)))
    cases.append(("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT)))
    cases.append(("schema interno e referências locais", True, validate_schema_shape(schema)))
    cases.append(("ADR-003: nenhum campo de nota no schema", True, validate_no_scoring(schema)))
    cases.append(
        ("autoridades herdadas dos schemas de fronteira", True, validate_inherited_authority())
    )
    cases.append(("catálogo de evals", True, validate_evals()))

    fixtures = [
        ("AUDIT_TASK de contrato e autoridade", audit_task()),
        ("AUDIT_TASK de governança", audit_task("agente-verificar-governanca-e-responsabilidades")),
        ("AUDIT_TASK de evidências", audit_task("agente-conferir-evidencias-e-artefatos")),
        ("AUDIT_RECEIPT", audit_receipt()),
        ("CONFORMITY_MATRIX", conformity_matrix()),
        ("AUDIT_CAPABILITY_GAP", capability_gap()),
        ("AUDIT_LEDGER", audit_ledger()),
    ]
    for label, fixture in fixtures:
        cases.append((f"schema aceita {label}", True, validate_schema(fixture, schema, schema)))

    # --- tarefa: capacidade, custódia e trava -------------------------------

    wrong_capability = audit_task()
    wrong_capability["capability"] = "evidencias-e-artefatos"
    cases.append(
        ("tarefa rejeita capacidade trocada para o agente", False,
         validate_schema(wrong_capability, schema, schema))
    )

    writable = audit_task()
    writable["custody_chain"][0]["access_mode"] = "read-write"
    cases.append(
        ("tarefa rejeita custódia com acesso de escrita", False,
         validate_schema(writable, schema, schema))
    )

    conflicted = audit_task()
    conflicted["review_chain"]["solution_participant_conflict"] = True
    cases.append(
        ("tarefa não é emitida com conflito de independência", False,
         validate_schema(conflicted, schema, schema))
    )

    leaky = audit_task()
    leaky["forbidden_context"] = [
        "recibos dos outros agentes",
        "racionalização do produtor",
        "rodada anterior",
    ]
    cases.append(
        ("tarefa exige proibição explícita de conclusão esperada", False,
         validate_schema(leaky, schema, schema))
    )

    wrong_return = audit_task()
    wrong_return["return_to"] = "diretor-de-lentes"
    cases.append(
        ("tarefa rejeita retorno fora da gerente", False,
         validate_schema(wrong_return, schema, schema))
    )

    # --- recibo: estados e achados ------------------------------------------

    invalid_state = audit_receipt(states={"INTENT": "APROVADO"})
    cases.append(
        ("recibo rejeita estado fora dos cinco", False,
         validate_schema(invalid_state, schema, schema))
    )

    lazy_na = audit_receipt(states={"INTENT": "NAO_APLICAVEL"})
    lazy_na["dimension_states"][0]["not_applicable_reason"] = "nao se aplica"
    cases.append(
        ("recibo rejeita NAO_APLICAVEL genérico", False,
         validate_schema(lazy_na, schema, schema))
    )

    conforme_sem_prova = audit_receipt(states={"INTENT": "CONFORME"})
    conforme_sem_prova["dimension_states"][0]["evidence_refs"] = []
    cases.append(
        ("recibo rejeita CONFORME sem evidência", False,
         validate_schema(conforme_sem_prova, schema, schema))
    )

    nao_provado = audit_receipt(states={"INTENT": "NAO_PROVADO"})
    cases.append(
        ("recibo aceita NAO_PROVADO sem evidência", True,
         validate_schema(nao_provado, schema, schema))
    )

    blocked = audit_receipt(status="BLOCKED")
    cases.append(
        ("recibo BLOCKED com motivo é válido", True,
         validate_schema(blocked, schema, schema))
    )

    blocked_mute = audit_receipt(status="BLOCKED")
    blocked_mute.pop("blocked_reason")
    cases.append(
        ("recibo BLOCKED exige motivo declarado", False,
         validate_schema(blocked_mute, schema, schema))
    )

    downgraded = audit_receipt(findings=[finding("AUTH", "BLOCKER")])
    downgraded["findings"][0]["blocking"] = False
    cases.append(
        ("recibo rejeita BLOCKER rebaixado para não bloqueante", False,
         validate_schema(downgraded, schema, schema))
    )

    # --- matriz: as dez dimensões -------------------------------------------

    short_matrix = conformity_matrix()
    short_matrix["dimensions"].pop()
    cases.append(
        ("matriz exige as dez dimensões", False,
         validate_schema(short_matrix, schema, schema))
    )

    duplicated = conformity_matrix()
    duplicated["dimensions"][-1] = copy.deepcopy(duplicated["dimensions"][0])
    duplicated["dimensions"][-1]["reason"] = "Duplicata com texto diferente."
    cases.append(
        ("matriz não aceita dimensão duplicada", False,
         validate_schema(duplicated, schema, schema))
    )

    # --- ledger: veredito, ressalva e R6 ------------------------------------

    reproved = audit_ledger({**{d: "CONFORME" for d in DIMENSIONS}, "AUTH": "NAO_CONFORME"})
    cases.append(
        ("ledger aceita REPROVADO com violação", True,
         validate_schema(reproved, schema, schema))
    )

    laundered = copy.deepcopy(reproved)
    laundered["internal_verdict"] = "APROVADO_COM_RESSALVAS"
    laundered["governance_verdict"] = "COMPLIANT"
    cases.append(
        ("ledger rejeita COMPLIANT com violação registrada", False,
         validate_schema(laundered, schema, schema))
    )

    mute_noncompliant = copy.deepcopy(reproved)
    mute_noncompliant["violations"] = []
    cases.append(
        ("ledger rejeita NONCOMPLIANT sem violação", False,
         validate_schema(mute_noncompliant, schema, schema))
    )

    wrong_binary = audit_ledger()
    wrong_binary["governance_verdict"] = "NONCOMPLIANT"
    cases.append(
        ("ledger rejeita binário divergente do veredito interno", False,
         validate_schema(wrong_binary, schema, schema))
    )

    ressalva_ledger = audit_ledger(
        {**{d: "CONFORME" for d in DIMENSIONS}, "RASTREABILIDADE": "RESSALVA"}
    )
    cases.append(
        ("ledger aceita APROVADO_COM_RESSALVAS com ressalva registrada", True,
         validate_schema(ressalva_ledger, schema, schema))
    )

    ressalva_sem_registro = copy.deepcopy(ressalva_ledger)
    ressalva_sem_registro["ressalvas"] = []
    cases.append(
        ("ledger rejeita ressalva só no texto", False,
         validate_schema(ressalva_sem_registro, schema, schema))
    )

    aprovado_com_ressalva = audit_ledger()
    aprovado_com_ressalva["ressalvas"] = ressalva_ledger["ressalvas"]
    cases.append(
        ("ledger rejeita APROVADO com ressalva pendurada", False,
         validate_schema(aprovado_com_ressalva, schema, schema))
    )

    with_gap = audit_ledger(gaps=[capability_gap()])
    cases.append(
        ("ledger rejeita veredito positivo com lacuna aberta", False,
         validate_schema(with_gap, schema, schema))
    )

    missing_dossier = audit_ledger(dossier_missing=["diff do escopo tocado"])
    cases.append(
        ("ledger rejeita veredito positivo com dossiê incompleto", False,
         validate_schema(missing_dossier, schema, schema))
    )

    no_assignments = audit_ledger(with_assignments=False)
    cases.append(
        ("ledger rejeita veredito positivo sem registro de emissão (R6)", False,
         validate_schema(no_assignments, schema, schema))
    )

    no_r6 = audit_ledger()
    no_r6["pending"] = ["custódia autodeclarada anotada"]
    cases.append(
        ("ledger exige R6 nomeado em pending", False,
         validate_schema(no_r6, schema, schema))
    )

    to_ceo = audit_ledger()
    to_ceo["return_to"] = "ceo-maestro"
    cases.append(
        ("ledger rejeita retorno fora do Diretor", False,
         validate_schema(to_ceo, schema, schema))
    )

    # --- fronteira: os envelopes produzidos servem aos consumidores ---------

    approved_ledger = audit_ledger()
    cases.append(
        ("CEO aceita o GOVERNANCE_REPORT COMPLIANT produzido", True,
         validate_schema(
             derive_governance_report(approved_ledger), governance_def, ceo_schema
         ))
    )
    cases.append(
        ("CEO aceita o GOVERNANCE_REPORT NONCOMPLIANT produzido", True,
         validate_schema(derive_governance_report(reproved), governance_def, ceo_schema))
    )
    cases.append(
        ("Diretor aceita o DEPARTMENT_RETURN produzido", True,
         validate_schema(
             derive_department_return(approved_ledger), director_schema, director_schema
         ))
    )

    forged_compliant = derive_governance_report(reproved)
    forged_compliant["verdict"] = "COMPLIANT"
    cases.append(
        ("CEO rejeita COMPLIANT com violação", False,
         validate_schema(forged_compliant, governance_def, ceo_schema))
    )

    forged_noncompliant = derive_governance_report(approved_ledger)
    forged_noncompliant["verdict"] = "NONCOMPLIANT"
    cases.append(
        ("CEO rejeita NONCOMPLIANT sem violação", False,
         validate_schema(forged_noncompliant, governance_def, ceo_schema))
    )

    scored_report = derive_governance_report(approved_ledger)
    scored_report["minimum_score"] = 9.5
    cases.append(
        ("CEO rejeita relatório de governança com nota", False,
         validate_schema(scored_report, governance_def, ceo_schema))
    )

    spoofed_return = derive_department_return(approved_ledger)
    spoofed_return["causal"]["producer"] = "departamento-desenvolvimento"
    cases.append(
        ("Diretor rejeita retorno com produtor forjado", False,
         validate_schema(spoofed_return, director_schema, director_schema))
    )

    # --- consolidação e veredito, recalculados em código --------------------

    all_conforme = {dim: "CONFORME" for dim in DIMENSIONS}
    one_ressalva = {**all_conforme, "RASTREABILIDADE": "RESSALVA"}
    one_nao_conforme = {**all_conforme, "AUTH": "NAO_CONFORME"}
    one_nao_provado = {**all_conforme, "EVIDENCIA": "NAO_PROVADO"}
    derived_return = derive_department_return(approved_ledger)

    checks = [
        ("estado mais grave vence entre dois inspetores",
         worst_state(["CONFORME", "NAO_CONFORME"]) == "NAO_CONFORME"),
        ("NAO_PROVADO vence RESSALVA",
         worst_state(["RESSALVA", "NAO_PROVADO"]) == "NAO_PROVADO"),
        ("CONFORME vence NAO_APLICAVEL",
         worst_state(["NAO_APLICAVEL", "CONFORME"]) == "CONFORME"),
        ("dez conformes aprovam",
         decide_verdict(all_conforme) == "APROVADO"),
        ("uma ressalva aprova com ressalvas",
         decide_verdict(one_ressalva) == "APROVADO_COM_RESSALVAS"),
        ("uma não conformidade reprova",
         decide_verdict(one_nao_conforme) == "REPROVADO"),
        ("um não provado reprova como não conformidade",
         decide_verdict(one_nao_provado) == "REPROVADO"),
        ("nove conformes não compensam uma bloqueada",
         decide_verdict(one_nao_conforme) == "REPROVADO"
         and sum(1 for s in one_nao_conforme.values() if s == "CONFORME") == 9),
        ("REPROVADO traduz para NONCOMPLIANT",
         to_governance("REPROVADO") == "NONCOMPLIANT"),
        ("APROVADO_COM_RESSALVAS traduz para COMPLIANT",
         to_governance("APROVADO_COM_RESSALVAS") == "COMPLIANT"),
        ("os três estados internos da RI-05 existem",
         {decide_verdict(all_conforme), decide_verdict(one_ressalva),
          decide_verdict(one_nao_conforme)}
         == {"APROVADO", "APROVADO_COM_RESSALVAS", "REPROVADO"}),
        ("cada dimensão bloqueada vira uma violação",
         len(audit_ledger(one_nao_conforme)["violations"]) == 1),
        ("cada ressalva vira uma pendência com dono",
         len(ressalva_ledger["ressalvas"]) == 1
         and all(item["owner_role"] for item in ressalva_ledger["ressalvas"])),
        ("retorno da Auditoria não conta teste executado",
         derived_return["test_summary"] == {
             "pass": 0, "fail": 0, "skip": 0, "skip_reasons": [], "critical_fail": False
         }),
        ("as dez dimensões têm dona declarada",
         set(OWNER) == set(DIMENSIONS) and len(set(OWNER.values())) == 3),
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
