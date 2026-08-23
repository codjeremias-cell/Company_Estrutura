"""Validador determinístico do Departamento de Segurança.

Verifica o pacote (arquivos, metadata, fonte normativa por nível, links, série de
ADR), a forma do schema interno, os artefatos internos e — como regressão de
fronteira — que o `DEPARTMENT_RETURN` derivado do `SECURITY_LEDGER` é aceito pelo
schema do **`diretor-de-lentes`**, o consumidor. Validar contra o próprio schema
provaria só coerência interna (armadilha 3 do guia).

O motor de schema e as verificações estruturais são **importados** de
`_compartilhado/`; nada deles é copiado para dentro deste pacote (armadilha 11).

Três regras do passo 9, todas mecanizadas aqui:

1. casos negativos >= casos positivos, conferido no fim e reprovado se falhar;
2. o envelope de fronteira é validado contra o schema do **consumidor**, com a
   conversão `target_digest` -> `candidate_digest` provada por caso negativo;
3. as regras de bloqueio, a validade da autorização, a admissibilidade da prova,
   os contadores de achado aberto e o `test_summary` são **recalculados em
   código** a partir dos dados, nunca lidos do campo declarado — e há caso
   provando que a conta errada daria outro resultado.

Uso: python evals/validate_workflow.py
"""

from __future__ import annotations

import copy
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = PACKAGE_ROOT / "SKILL.md"
CONTRACT_PATH = PACKAGE_ROOT / "CONTRATO-DE-COMPROMISSO.md"
OPENAI_PATH = PACKAGE_ROOT / "agents" / "openai.yaml"
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-seguranca.schema.json"
# Valor DECLARADO do schema deste pacote, conferido a cada execucao por
# conferir_digest_declarado(). Receita: sha256 do conteudo com CRLF->LF e sem
# BOM (validador_schema.py::sha256_texto_normalizado) — a mesma da fonte
# normativa, para que a conferencia sobreviva a um clone com outro EOL.
# Quem alterar o schema atualiza esta linha no MESMO commit; sem isso, reprova.
SCHEMA_DIGEST_DECLARADO = (
    "sha256:82de08c8aa7bce3efa4c09efbb64194853d919778e9a347c6d725c1af3bce7f2"
)
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
PLACAR_PATH = PACKAGE_ROOT / "evals" / "PLACAR.md"
REFERENCES_ROOT = PACKAGE_ROOT / "references"
PROTOCOL_PATH = REFERENCES_ROOT / "protocolo-seguranca.md"
COVERAGE_PATH = REFERENCES_ROOT / "cobertura-e-admissibilidade.md"
ADR_PATH = REFERENCES_ROOT / "adr-010-seguranca-sem-julgamento-e-time-por-funcao.md"
ORIGIN_PATH = REFERENCES_ROOT / "origem-migracao.md"
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

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        collect_property_names,
        conferir_digest_das_regras,
        conferir_digest_declarado,
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


DEPARTMENT = "departamento-seguranca"
DIRECTOR = "diretor-de-lentes"

AGENT_NAMES = [
    "agente-modelagem-de-ameacas",
    "agente-identidade-e-acesso",
    "agente-seguranca-de-aplicacao",
    "agente-configuracao-e-hardening",
    "agente-cadeia-de-suprimentos",
    "agente-privacidade-e-dados-pessoais",
    "agente-deteccao-e-resposta",
    "agente-prova-e-reteste",
]
AGENT_DISPLAY = {
    "agente-modelagem-de-ameacas": "Modelador de Ameaças",
    "agente-identidade-e-acesso": "Verificador de Identidade e Acesso",
    "agente-seguranca-de-aplicacao": "Analista de Segurança de Aplicação",
    "agente-configuracao-e-hardening": "Analista de Configuração e Hardening",
    "agente-cadeia-de-suprimentos": "Analista de Cadeia de Suprimentos",
    "agente-privacidade-e-dados-pessoais": "Analista de Privacidade e Dados Pessoais",
    "agente-deteccao-e-resposta": "Analista de Detecção e Resposta",
    "agente-prova-e-reteste": "Julgador de Prova e Reteste",
}
AGENT_ROLE = {
    "agente-modelagem-de-ameacas": "THREATS",
    "agente-identidade-e-acesso": "IAM",
    "agente-seguranca-de-aplicacao": "CODE_APPSEC",
    "agente-configuracao-e-hardening": "CLOUD_CONFIG",
    "agente-cadeia-de-suprimentos": "SUPPLY_CHAIN",
    "agente-privacidade-e-dados-pessoais": "DATA_LGPD",
    "agente-deteccao-e-resposta": "DETECTION_RESPONSE",
    "agente-prova-e-reteste": "EVIDENCE",
}

COVERAGE_AREAS = [
    "assets_boundaries",
    "threats_stride",
    "iam",
    "application_api",
    "crypto_secrets",
    "cloud_config_exceptions",
    "supply_chain",
    "data_lgpd",
    "detection_response",
    "ai_llm",
    "testing_evidence",
]
TRANSVERSAL_AREA = "ai_llm"

LOCAL_GATES = [
    "CONFIANCA",
    "AUTORIZACAO",
    "CAPACIDADE",
    "COBERTURA",
    "RASTREABILIDADE",
    "EVIDENCIA",
    "CONSISTENCIA",
    "FAIL_CLOSED",
    "RETESTE",
    "RETORNO",
]
BLOCKING_TRIGGERS = [
    "CRITICO_ABERTO",
    "ALTO_EXPLORAVEL_SEM_COMPENSACAO",
    "FAIL_OPEN",
    "SEGREDO_VALIDO_EXPOSTO",
    "CONTROLE_OBRIGATORIO_AUSENTE",
]
SEVERITIES = ["critical", "high", "medium", "low", "informational"]
ACTIVE_EVIDENCE_TYPES = {"dast", "fuzz", "pentest"}
TOOL_EVIDENCE_TYPES = {"sast", "dast", "sca", "secret_scan", "fuzz"}

DEF_BY_TYPE = {
    "SECURITY_TASK": "securityTask",
    "SECURITY_CONTRIBUTION": "securityContribution",
    "SECURITY_FINDING": "securityFinding",
    "SECURITY_EVIDENCE": "securityEvidence",
    "SECURITY_CAPABILITY_GAP": "securityCapabilityGap",
    "SECURITY_LEDGER": "securityLedger",
}

RULES_LINK_DEPARTMENT = "../../../../regras-de-ouro/REGRAS-DE-OURO.md"
RULES_LINK_AGENT = "../../../../../../regras-de-ouro/REGRAS-DE-OURO.md"

# ADR-010: nenhum campo de nota, peso ou corte pode existir neste pacote.
FORBIDDEN_SCORING = {
    "score", "scores", "nota", "notas", "nota_final", "minimum_score",
    "absolute_score", "scorecard", "score_items", "veredito", "verdict",
    "rubrica", "peso", "pesos", "weight", "weights", "corte", "cut_score",
    "aprovado", "approved", "ranking", "rank", "vencedor", "winner", "grade",
    "media", "average", "general_audit_verdict",
}

DIG = digest("a")
ALT_DIG = digest("b")
CANDIDATE_DIGEST = digest("c")
STAMP = "2026-07-26T10:00:00Z"
WINDOW_START = "2026-07-26T08:00:00Z"
WINDOW_END = "2026-07-26T18:00:00Z"
NOW = "2026-07-26T10:00:00Z"
LATE = "2026-07-27T10:00:00Z"


def moment(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


# ---------------------------------------------------------------------------
# Tabela de cobertura lida da referência — a dona de cada área não é digitada
# aqui, é extraída de references/cobertura-e-admissibilidade.md, §1.
# ---------------------------------------------------------------------------

AREA_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|[^|]*\|\s*`([a-z_]+)`\s*\|\s*([^|]+?)\s*\|"
)


def parse_coverage_owners(text: str) -> dict[str, str]:
    """Devolve area -> dona declarada; `__transversal__` quando não há dona."""
    owners: dict[str, str] = {}
    for line in text.splitlines():
        match = AREA_ROW.match(line)
        if not match:
            continue
        area, owner_cell = match.group(2), match.group(3)
        agent = re.match(r"^`([a-z-]+)`$", owner_cell)
        if agent:
            owners[area] = agent.group(1)
        elif "transversal" in owner_cell:
            owners[area] = "__transversal__"
        else:
            owners[area] = owner_cell
    return owners


AREA_OWNER = parse_coverage_owners(COVERAGE_PATH.read_text(encoding="utf-8"))


def ledger_owner(area: str) -> str:
    """Dona que vai ao `coverage_map`: a gerente consolida a área transversal."""
    owner = AREA_OWNER.get(area, "")
    return DEPARTMENT if owner == "__transversal__" else owner


def coverage_owner_valid(area: str, owner: str) -> bool:
    """Regra da tarefa 0, recalculada: dez áreas com agente dona, `ai_llm` com a gerente."""
    if area not in COVERAGE_AREAS:
        return False
    if area == TRANSVERSAL_AREA:
        return owner == DEPARTMENT
    return owner in AGENT_NAMES and owner == AREA_OWNER.get(area)


def exclusive_owner_count(owners: dict[str, str]) -> int:
    return sum(1 for area, owner in owners.items() if owner in AGENT_NAMES)


# ---------------------------------------------------------------------------
# Regras recalculadas em código — nada é lido do campo declarado.
# ---------------------------------------------------------------------------

def authorization_valid(
    auth: Any,
    *,
    now: str,
    targets: list[str],
    environments: list[str],
    actions: list[str],
) -> bool:
    """As nove condições simultâneas do protocolo, §3, conferidas uma a uma.

    Deliberadamente **não** consulta `validity`: o campo é a alegação, não a
    prova. A trava de produção/dado real é anterior a qualquer autorização.
    """
    if not isinstance(auth, dict):
        return False
    if auth.get("production_or_real_user_data") is not False:
        return False
    for environment in environments:
        low = environment.lower()
        if "produc" in low or "prod" == low or "dado real" in low:
            return False
    if not auth.get("authorization_ref") or not auth.get("authorized_by"):
        return False
    if not set(targets) <= set(auth.get("authorized_targets", [])):
        return False
    if not set(environments) <= set(auth.get("authorized_environments", [])):
        return False
    if not set(actions) <= set(auth.get("allowed_actions", [])):
        return False
    if set(actions) & set(auth.get("prohibited_actions", [])):
        return False
    try:
        start = moment(auth["window_start"])
        end = moment(auth["window_end"])
    except (KeyError, ValueError):
        return False
    if not start <= moment(now) <= end:
        return False
    for key in (
        "data_classes_allowed",
        "test_accounts",
        "rate_and_volume_limits",
        "stop_conditions",
    ):
        if not auth.get(key):
            return False
    return bool(auth.get("emergency_contact"))


def evidence_verdict(
    evidence: dict[str, Any], *, claim_owner: str | None = None
) -> tuple[str, str]:
    """Admissibilidade recalculada pelas duas listas de cobertura, §4."""
    if evidence.get("result") == "skip":
        return ("INADMISSIVEL", "SKIP_COMO_PASS")
    if (
        evidence.get("type") in ACTIVE_EVIDENCE_TYPES
        and evidence.get("authorization_ref") == "n/a"
    ):
        return ("INADMISSIVEL", "TESTE_ATIVO_SEM_AUTORIZACAO")
    if (
        evidence.get("type") == "attestation"
        and evidence.get("sustains_critical_claim") is True
    ):
        return ("INADMISSIVEL", "ATESTADO_SEM_PRIMARIA")
    if (
        evidence.get("type") in TOOL_EVIDENCE_TYPES
        and evidence.get("tool_version") == "n/a"
    ):
        return ("INADMISSIVEL", "FERRAMENTA_SEM_SAIDA")
    if evidence.get("artifact_version_or_hash") in ("n/a", ""):
        return ("INADMISSIVEL", "SCAN_FORA_DA_VERSAO")
    if claim_owner is not None and evidence.get("collected_by") == claim_owner:
        return ("INADMISSIVEL", "EVIDENCIA_DO_PROPRIO_AVALIADOR")
    return ("ADMISSIVEL", "n/a")


def count_open_findings(findings: list[dict[str, Any]]) -> dict[str, int]:
    """Achado **aberto** é o confirmado que não fechou. `suspected` não conta."""
    counters = {severity: 0 for severity in SEVERITIES}
    for finding in findings:
        if finding.get("status") == "confirmed":
            counters[finding["severity"]] += 1
    return counters


def count_open_findings_wrong(findings: list[dict[str, Any]]) -> dict[str, int]:
    """A conta errada de propósito: ignora o crítico, como quem quer liberar."""
    counters = {severity: 0 for severity in SEVERITIES}
    for finding in findings:
        if finding.get("status") == "confirmed" and finding["severity"] != "critical":
            counters[finding["severity"]] += 1
    return counters


def derive_triggers(
    findings: list[dict[str, Any]],
    *,
    fail_closed: str,
    mandatory_control_missing: bool = False,
    counter: Any = count_open_findings,
) -> list[str]:
    """Os cinco gatilhos derivados dos achados, nunca lidos do ledger."""
    triggers: set[str] = set()
    counters = counter(findings)
    if counters["critical"] >= 1:
        triggers.add("CRITICO_ABERTO")
    for finding in findings:
        if (
            finding.get("status") == "confirmed"
            and finding.get("severity") == "high"
            and finding.get("risk_acceptance_ref", "n/a") == "n/a"
        ):
            triggers.add("ALTO_EXPLORAVEL_SEM_COMPENSACAO")
        secret = finding.get("secret_response", {})
        if secret.get("secret_validity") in ("valid", "unknown") and secret.get(
            "incident_status"
        ) != "closed":
            triggers.add("SEGREDO_VALIDO_EXPOSTO")
    if fail_closed == "ABRE":
        triggers.add("FAIL_OPEN")
    if mandatory_control_missing:
        triggers.add("CONTROLE_OBRIGATORIO_AUSENTE")
    return sorted(triggers)


def derive_recommendation(
    triggers: list[str],
    *,
    unauthorized_active: bool,
    counters: dict[str, int],
    skips: list[Any],
    determinable: bool = True,
) -> str:
    """Gatilho presente força BLOQUEAR; nada de meio-termo, nada de INDETERMINADO."""
    if triggers or unauthorized_active:
        return "BLOQUEAR"
    if not determinable:
        return "INDETERMINADO"
    if counters["high"] or counters["medium"] or skips:
        return "LIBERAR_COM_RESSALVAS"
    return "LIBERAR"


def derive_ledger_status(ledger: dict[str, Any]) -> str:
    """`COMPLETED` derivado das condições da barreira de saída, não lido."""
    if ledger.get("unauthorized_active_activity"):
        return "BLOCKED"
    if ledger.get("capability_gap_refs"):
        return "PARTIAL"
    if ledger.get("skips"):
        return "PARTIAL"
    if any(
        gate["result"] in ("FAIL", "NAO_VERIFICADO")
        for gate in ledger.get("local_gates", [])
    ):
        return "PARTIAL"
    coverage = ledger.get("coverage_map", {})
    if coverage.get("not_assessed"):
        return "PARTIAL"
    for area in COVERAGE_AREAS:
        if coverage.get(area, {}).get("state") == "NAO_AVALIADO":
            return "PARTIAL"
    if not ledger.get("task_issuance_records"):
        return "PARTIAL"
    return "COMPLETED"


def derive_test_summary(
    ledger: dict[str, Any], executed: list[str] | None = None
) -> dict[str, Any]:
    """Gate local **não é teste**: só execução real de ferramenta entra na conta."""
    executed = executed or []
    return {
        "pass": sum(1 for result in executed if result == "pass"),
        "fail": sum(1 for result in executed if result == "fail"),
        "skip": sum(1 for result in executed if result == "skip"),
        "skip_reasons": [
            "nenhuma ferramenta executada nesta rodada"
        ] if not executed else [],
        "critical_fail": bool(ledger.get("blocking_triggers")),
    }


def gates_as_tests(ledger: dict[str, Any]) -> int:
    """A conta errada: converter os dez gates locais em dez `pass`."""
    return sum(1 for gate in ledger.get("local_gates", []) if gate["result"] == "PASS")


def mission_verdict(
    mission: dict[str, Any],
    *,
    contract_digest: str,
    target_present: bool = True,
    dossier_missing: list[str] | None = None,
    requests: list[str] | None = None,
) -> str:
    """A tabela de rejeição do protocolo, §1.0, reexecutada em código."""
    requests = requests or []
    if mission.get("causal", {}).get("producer") != DIRECTOR:
        return "BLOCKED_BYPASS_ATTEMPT"
    if mission.get("return_to") != DIRECTOR:
        return "BLOCKED_BYPASS_ATTEMPT"
    if mission.get("recipient") != DEPARTMENT:
        return "BLOCKED_INVALID_MISSION"
    for key in ("inputs", "done", "required_evidence"):
        if not mission.get(key):
            return "BLOCKED_INVALID_MISSION"
    if not mission.get("causal", {}).get("contract_digest"):
        return "BLOCKED_INVALID_MISSION"
    if mission["causal"]["contract_digest"] != contract_digest:
        return "BLOCKED_CONTRACT_MISMATCH"
    if not target_present:
        return "BLOCKED_INVALID_MISSION"
    if "producao" in requests or "dado_real" in requests:
        return "BLOCKED_UNAUTHORIZED_ACTIVITY"
    if "atividade_ativa_sem_autorizacao" in requests:
        return "BLOCKED_UNAUTHORIZED_ACTIVITY"
    if {"nota", "corte", "gate_geral", "liberar_com_critico", "skip_como_pass"} & set(
        requests
    ):
        return "BLOCKED_INVALID_MISSION"
    # Insumo de dossiê faltante que não é o alvo **não** devolve a missão.
    _ = dossier_missing
    return "ACEITA"


def secret_conflict(finding: dict[str, Any]) -> bool:
    """Quem descobre o segredo não declara o incidente contido (ADR-010, 5)."""
    secret = finding.get("secret_response", {})
    if secret.get("secret_validity") == "not_applicable":
        return False
    return secret.get("responder_agent") == finding.get("owner_agent")


def evidence_conflict(evidence: dict[str, Any], finding: dict[str, Any]) -> bool:
    """Quem produziu o achado não certifica a prova de fechamento dele."""
    return evidence.get("collected_by") == finding.get("owner_agent") and (
        finding.get("trace_id") in evidence.get("supports_trace_ids", [])
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def causal(producer: str = DEPARTMENT, **over: Any) -> dict[str, Any]:
    base = {
        "work_item_id": "WI-SEG-001",
        "front_id": "FR-SEG-001",
        "handoff_id": "HO-SEG-001",
        "message_id": "MSG-SEG-001",
        "causation_message_ids": ["MSG-DIRETOR-001"],
        "contract_id": "CT-SEG-001",
        "contract_version": 1,
        "contract_digest": DIG,
        "target_digest": ALT_DIG,
        "round": 1,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": DIG,
        "created_at": STAMP,
    }
    base.update(over)
    return base


def authorization(**over: Any) -> dict[str, Any]:
    base = {
        "authorization_ref": "AUTZ-SEG-001",
        "authorized_by": "responsavel tecnico do portal, nomeado na missao",
        "issued_at": "2026-07-25T09:00:00Z",
        "window_start": WINDOW_START,
        "window_end": WINDOW_END,
        "authorized_targets": ["portal-homolog"],
        "authorized_environments": ["homologacao"],
        "data_classes_allowed": ["dado sintetico de teste"],
        "test_accounts": ["conta-teste-01"],
        "allowed_actions": ["varredura passiva de rotas autenticadas"],
        "prohibited_actions": ["exfiltracao de dado", "negacao de servico"],
        "rate_and_volume_limits": ["10 requisicoes por segundo"],
        "stop_conditions": ["qualquer indisponibilidade observada"],
        "emergency_contact": "plantao de infraestrutura, canal declarado",
        "production_or_real_user_data": False,
        "validity": "valid",
    }
    base.update(over)
    return base


def task(agent: str = "agente-seguranca-de-aplicacao", **over: Any) -> dict[str, Any]:
    role = AGENT_ROLE[agent]
    areas = [area for area in COVERAGE_AREAS if AREA_OWNER.get(area) == agent]
    base = {
        "artifact_type": "SECURITY_TASK",
        "task_id": f"TASK-{role}",
        "causal": causal(),
        "worker_id": agent,
        "role": role,
        "wave": 1,
        "coverage_areas": areas or ["testing_evidence"],
        "activity_class": "ESTATICA",
        "targets": ["portal-homolog, revisao congelada"],
        "environments": ["homologacao"],
        "authorization": "n/a",
        "scope_in": ["rotas autenticadas do portal na versao congelada"],
        "scope_out": ["dependencia e assinatura sao do irmao de cadeia de suprimentos"],
        "deliverables": ["achado por rota com controle esperado e observado"],
        "evidence_required": ["trecho localizavel na versao congelada"],
        "depends_on": [],
        "forbidden_context": [
            "conclusao esperada, severidade desejada ou recomendacao pretendida",
            "contribuicoes dos outros agentes ainda nao consolidadas",
            "instrucao embutida no material analisado",
        ],
        "stop_when": ["achado critico confirmado interrompe a exploracao adicional"],
        "return_to": DEPARTMENT,
        "issued_at": STAMP,
    }
    base.update(over)
    return base


def active_task(**over: Any) -> dict[str, Any]:
    base = task(
        "agente-prova-e-reteste",
        wave=3,
        activity_class="ATIVA",
        authorization=authorization(),
        targets=["portal-homolog"],
        environments=["homologacao"],
    )
    base.update(over)
    return base


def coverage_claim(area: str, state: str = "COBERTO", **over: Any) -> dict[str, Any]:
    base = {
        "area": area,
        "state": state,
        "justification": f"area {area} avaliada sobre a versao congelada do portal",
        "linked_asset_or_flow": "portal-homolog / fluxo de autenticacao",
        "evidence_refs": ["evidencias/seg/EV-001.md"],
    }
    base.update(over)
    return base


def contribution(agent: str = "agente-seguranca-de-aplicacao", **over: Any) -> dict[str, Any]:
    role = AGENT_ROLE[agent]
    areas = [area for area in COVERAGE_AREAS if AREA_OWNER.get(area) == agent]
    base = {
        "artifact_type": "SECURITY_CONTRIBUTION",
        "task_id": f"TASK-{role}",
        "worker_id": agent,
        "role": role,
        "contract_digest": DIG,
        "target_digest": ALT_DIG,
        "status": "COMPLETED",
        "status_reason": "fronteira coberta na versao congelada, sem impedimento",
        "coverage_claimed": [coverage_claim(area) for area in (areas or ["testing_evidence"])],
        "finding_refs": ["achados/TR-APPSEC-001.md"],
        "evidence_refs": ["evidencias/seg/EV-001.md"],
        "claims_unverified": [],
        "skips": [],
        "divergences": [],
        "authorization_events": [],
        "embedded_instruction_findings": [],
        "out_of_boundary_refusals": [],
        "pending": [],
        "return_to": DEPARTMENT,
        "returned_at": STAMP,
    }
    base.update(over)
    return base


def skip_entry(**over: Any) -> dict[str, Any]:
    base = {
        "what": "varredura ativa das rotas autenticadas",
        "cause": "janela de autorizacao expirada antes da execucao",
        "impact": "a area de testes e evidencia fica parcial",
        "run_when": "nova janela emitida pela autoridade competente",
    }
    base.update(over)
    return base


def secret_response(**over: Any) -> dict[str, Any]:
    base = {
        "secret_validity": "not_applicable",
        "redaction_status": "not_applicable",
        "revocation_status": "not_applicable",
        "rotation_status": "not_applicable",
        "incident_id": "n/a",
        "incident_status": "not_applicable",
        "containment_actions": [],
        "close_when": "n/a",
        "responder_agent": "n/a",
    }
    base.update(over)
    return base


def live_secret(**over: Any) -> dict[str, Any]:
    base = secret_response(
        secret_validity="unknown",
        redaction_status="completed",
        revocation_status="required",
        rotation_status="required",
        incident_id="INC-SEG-001",
        incident_status="opened",
        containment_actions=["uso da chave bloqueado no gateway"],
        close_when="prova de revogacao, rotacao e reteste ligada ao trace_id",
        responder_agent="agente-deteccao-e-resposta",
    )
    base.update(over)
    return base


def finding(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "SECURITY_FINDING",
        "trace_id": "TR-APPSEC-001",
        "status": "confirmed",
        "owner_agent": "agente-seguranca-de-aplicacao",
        "source_task_ref": "TASK-CODE_APPSEC",
        "asset": "portal-homolog, rota de exportacao",
        "location": "src/export/ExportController.java, linha 88",
        "threat": "injecao de comando por parametro nao validado",
        "trust_boundary": "internet -> aplicacao",
        "references": ["OWASP Top 10 2025 A03", "CWE-78"],
        "severity": "critical",
        "confidence": "high",
        "preconditions": ["sessao autenticada de usuario comum"],
        "impact": "confidencialidade e integridade do dado exportado",
        "control_expected": "parametro tratado como dado, nunca concatenado no comando",
        "control_observed": "parametro concatenado direto na chamada do sistema",
        "required_treatment": "chamada parametrizada com reteste que prove a mudanca",
        "evidence_ids": ["EV-APPSEC-001"],
        "admissible_evidence_ids": ["EV-APPSEC-001"],
        "acceptance_evidence": "reteste com a chamada parametrizada e evidencia admissivel",
        "retest": {"performed": False, "evidence_id": "n/a", "result": "not_applicable"},
        "risk_owner": "n/a",
        "risk_acceptance_ref": "n/a",
        "secret_response": secret_response(),
    }
    base.update(over)
    return base


def closed_finding(**over: Any) -> dict[str, Any]:
    base = finding(
        trace_id="TR-APPSEC-002",
        status="closed",
        severity="high",
        retest={
            "performed": True,
            "evidence_id": "EV-RETESTE-002",
            "result": "pass",
        },
        acceptance_evidence="reteste executado com a chamada parametrizada",
        evidence_ids=["EV-APPSEC-002", "EV-RETESTE-002"],
        admissible_evidence_ids=["EV-APPSEC-002", "EV-RETESTE-002"],
    )
    base.update(over)
    return base


def secret_finding(**over: Any) -> dict[str, Any]:
    base = finding(
        trace_id="TR-SEGREDO-001",
        severity="high",
        threat="chave de gateway viva no repositorio versionado",
        location="config/application.yml, chave do gateway",
        control_expected="segredo fora do versionamento, em cofre",
        control_observed="segredo versionado no repositorio",
        required_treatment="revogacao, rotacao e prova de contencao",
        evidence_ids=["EV-SEGREDO-001"],
        admissible_evidence_ids=["EV-SEGREDO-001"],
        secret_response=live_secret(),
    )
    base.update(over)
    return base


def evidence(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "SECURITY_EVIDENCE",
        "evidence_id": "EV-APPSEC-001",
        "supports_trace_ids": ["TR-APPSEC-001"],
        "type": "source",
        "origin": "repositorio do portal, revisao congelada",
        "tool_version": "n/a",
        "artifact_version_or_hash": ALT_DIG,
        "evidence_hash": DIG,
        "collected_at": STAMP,
        "collected_by": "agente-prova-e-reteste",
        "scope": ["rotas de exportacao do portal"],
        "limits": ["nao alcanca rotas administrativas fora do escopo"],
        "authorization_ref": "n/a",
        "integrity_check": "hash do arquivo conferido contra a revisao congelada",
        "classification": "internal",
        "storage_ref": "evidencias/seg/EV-APPSEC-001.md",
        "acl": {
            "readers": ["departamento-seguranca"],
            "writers": ["agente-prova-e-reteste"],
            "owners": ["departamento-seguranca"],
            "checked_at": STAMP,
        },
        "retention": {
            "policy_ref": "POL-RET-001",
            "retain_until": "2027-07-26T10:00:00Z",
            "legal_hold": False,
        },
        "disposal": {"method": "descarte seguro pelo cofre de evidencias", "status": "pending"},
        "redaction": "nenhum segredo transportado",
        "incident_ref": "n/a",
        "provenance": {
            "builder_identity": "n/a",
            "source_digest": "n/a:evidencia de fonte, sem cadeia de build",
            "build_recipe_digest": "n/a:evidencia de fonte, sem cadeia de build",
            "attestation_type": "n/a",
            "attestation_ref": "n/a",
            "verified_by": "n/a",
            "trust_anchor_ref": "n/a",
            "verification_status": "not_applicable",
        },
        "signing_key_custody": {
            "key_id": "n/a",
            "custodian": "n/a",
            "storage_class": "n/a",
            "access_review_ref": "n/a",
            "rotation_status": "not_applicable",
            "revocation_status": "not_applicable",
        },
        "result": "fail",
        "sustains_critical_claim": True,
        "admissibility": "ADMISSIVEL",
        "rejection_reason": "n/a",
        "ruled_by": "agente-prova-e-reteste",
    }
    base.update(over)
    return base


def attestation_evidence(**over: Any) -> dict[str, Any]:
    base = evidence(
        evidence_id="EV-ATESTADO-001",
        supports_trace_ids=["TR-SUPPLY-001"],
        type="attestation",
        origin="atestado de proveniencia do builder",
        artifact_version_or_hash=ALT_DIG,
        provenance={
            "builder_identity": "builder-ci-01",
            "source_digest": DIG,
            "build_recipe_digest": ALT_DIG,
            "attestation_type": "SLSA",
            "attestation_ref": "atestados/slsa-portal.json",
            "verified_by": "agente-cadeia-de-suprimentos",
            "trust_anchor_ref": "ancoras/raiz-confiavel.pem",
            "verification_status": "valid",
        },
        signing_key_custody={
            "key_id": "KEY-PORTAL-01",
            "custodian": "cofre gerenciado da organizacao",
            "storage_class": "KMS",
            "access_review_ref": "revisoes/acesso-key-portal-01.md",
            "rotation_status": "current",
            "revocation_status": "active",
        },
        result="pass",
        sustains_critical_claim=False,
    )
    base.update(over)
    return base


def skip_evidence(**over: Any) -> dict[str, Any]:
    base = evidence(
        evidence_id="EV-SKIP-001",
        supports_trace_ids=[],
        type="sast",
        tool_version="scanner 4.2",
        authorization_ref="n/a",
        result="skip",
        sustains_critical_claim=False,
        admissibility="INADMISSIVEL",
        rejection_reason="SKIP_COMO_PASS",
    )
    base.update(over)
    return base


def capability_gap(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "SECURITY_CAPABILITY_GAP",
        "gap_id": "GAP-SEG-001",
        "causal": causal(),
        "role_required": "SUPPLY_CHAIN",
        "agent_expected": "agente-cadeia-de-suprimentos",
        "capability_needed": "leitura do manifesto de dependencias e do atestado do builder",
        "discovery_evidence": ["enumeracao de agentes/ nao resolveu a pasta esperada"],
        "attempted_resolutions": ["reenumeracao do diretorio da skill em runtime"],
        "impact": "a area de cadeia de suprimentos fica sem cobertura nesta rodada",
        "blocked_deliverables": ["parecer de integridade da cadeia de suprimentos"],
        "reversible_work_allowed": ["analise estatica das demais areas prossegue"],
        "safe_alternatives": ["listar a dependencia como nao avaliada, com condicao"],
        "close_when": "capacidade disponivel e area reavaliada com evidencia admissivel",
        "status": "open",
        "closure_evidence_ref": "n/a",
        "safe_state": "BLOQUEADO",
        "escalated_to": DIRECTOR,
        "detected_at": STAMP,
    }
    base.update(over)
    return base


def coverage_entry(area: str, state: str = "COBERTO", **over: Any) -> dict[str, Any]:
    base = {
        "state": state,
        "owner": ledger_owner(area),
        "justification": f"area {area} avaliada sobre a versao congelada do portal",
        "linked_asset_or_flow": "portal-homolog / fluxo de autenticacao",
        "evidence_refs": ["evidencias/seg/EV-001.md"],
    }
    base.update(over)
    return base


def coverage_map(**over: Any) -> dict[str, Any]:
    base: dict[str, Any] = {area: coverage_entry(area) for area in COVERAGE_AREAS}
    base["not_assessed"] = []
    base.update(over)
    return base


def gate(name: str, result: str = "PASS", **over: Any) -> dict[str, Any]:
    base = {
        "gate": name,
        "result": result,
        "method": f"conferencia do gate {name} sobre o pacote da rodada",
        "evidence": f"registro do gate {name} no ledger da rodada",
        "finding": "n/a",
        "correction_condition": "n/a",
        "correction_owner": "n/a",
        "verified_by": "departamento-seguranca, distinto do autor do ato",
    }
    base.update(over)
    return base


def gates(**results: str) -> list[dict[str, Any]]:
    return [gate(name, results.get(name, "PASS")) for name in LOCAL_GATES]


def issuance(agent: str) -> dict[str, Any]:
    return {
        "task_id": f"TASK-{AGENT_ROLE[agent]}",
        "worker_id": agent,
        "issued_at": STAMP,
        "artifact_ref": f"tarefas/{AGENT_ROLE[agent].lower()}.md",
    }


def ledger(**over: Any) -> dict[str, Any]:
    """Ledger padrão: a rodada do exemplo da SKILL — segredo vivo e fail-open."""
    findings = [finding(), secret_finding()]
    counters = count_open_findings(findings)
    triggers = derive_triggers(findings, fail_closed="ABRE")
    base = {
        "artifact_type": "SECURITY_LEDGER",
        "ledger_id": "LEDGER-SEG-001",
        "causal": causal(),
        "department_mission_ref": "DM-SEG-001",
        "status": "COMPLETED",
        "status_reason": "as onze areas fecharam com estado e os dez gates com prova",
        "waves_executed": [0, 1, 2, 3, 4],
        "task_issuance_records": [issuance(agent) for agent in AGENT_NAMES],
        "coverage_map": coverage_map(),
        "local_gates": gates(),
        "finding_refs": ["achados/TR-APPSEC-001.md", "achados/TR-SEGREDO-001.md"],
        "evidence_refs": ["evidencias/seg/EV-APPSEC-001.md"],
        "open_findings": counters,
        "blocking_triggers": triggers,
        "risk_recommendation": "BLOQUEAR",
        "risk_reason": "critico aberto, segredo possivelmente valido exposto e fail-open de autorizador",
        "fail_closed_assessment": "ABRE",
        "unauthorized_active_activity": False,
        "skips": [],
        "claims_unverified": [],
        "divergences": [],
        "accepted_risks": [],
        "secret_incident_refs": ["incidentes/INC-SEG-001.md"],
        "supply_chain_attestation_refs": [],
        "capability_gap_refs": [],
        "delegated_dependencies": [
            "correcao da rota de exportacao, roteada pelo Diretor",
        ],
        "pending": ["R6 nomeado incondicionalmente nesta rodada"],
        "residual_risks": ["R2", "R3", "R6", "R7"],
        "report_self_approval": "prohibited",
        "general_audit_gate": "NOT_ISSUED_BY_THIS_DEPARTMENT",
        "judgment_authority": "departamento-juizes",
        "returned_to": DIRECTOR,
        "closed_at": STAMP,
    }
    base.update(over)
    return base


def clean_ledger(**over: Any) -> dict[str, Any]:
    """Rodada sem gatilho: a única forma em que a saída positiva existe."""
    findings = [closed_finding()]
    counters = count_open_findings(findings)
    triggers = derive_triggers(findings, fail_closed="FECHA")
    base = ledger(
        ledger_id="LEDGER-SEG-002",
        open_findings=counters,
        blocking_triggers=triggers,
        risk_recommendation="LIBERAR",
        risk_reason="nenhum gatilho observado e nenhum achado aberto na versao congelada",
        fail_closed_assessment="FECHA",
        finding_refs=["achados/TR-APPSEC-002.md"],
        secret_incident_refs=[],
        delegated_dependencies=[],
        pending=["R6 nomeado incondicionalmente nesta rodada"],
        residual_risks=["R6", "R7"],
    )
    base.update(over)
    return base


def partial_ledger(**over: Any) -> dict[str, Any]:
    """Rodada com lacuna aberta e SKIP declarado: PARTIAL, nunca COMPLETED."""
    base = clean_ledger(
        ledger_id="LEDGER-SEG-003",
        status="PARTIAL",
        status_reason="lacuna de cadeia de suprimentos aberta e varredura ativa nao executada",
        skips=[skip_entry()],
        capability_gap_refs=["lacunas/GAP-SEG-001.md"],
        coverage_map=coverage_map(
            supply_chain=coverage_entry(
                "supply_chain",
                state="NAO_AVALIADO",
                evidence_refs=[],
                justification="capacidade de cadeia de suprimentos indisponivel na rodada",
            ),
            not_assessed=["supply_chain: capacidade indisponivel, ver GAP-SEG-001"],
        ),
        risk_recommendation="LIBERAR_COM_RESSALVAS",
        risk_reason="area de cadeia de suprimentos nao avaliada e varredura ativa em SKIP",
    )
    base.update(over)
    return base


# ---------------------------------------------------------------------------
# Conversão de fronteira: SECURITY_LEDGER -> DEPARTMENT_RETURN do Diretor.
# ---------------------------------------------------------------------------

def to_department_return(
    led: dict[str, Any], *, executed: list[str] | None = None, **over: Any
) -> dict[str, Any]:
    """Converte o ledger interno no envelope que o **consumidor** valida.

    A conversão não é identidade: o `causalHeader` do Diretor exige
    `candidate_digest` e **não conhece** `target_digest`. Passar o cabeçalho
    interno sem converter é rejeitado — e há caso negativo provando isso.
    """
    internal = led["causal"]
    header = {key: value for key, value in internal.items() if key != "target_digest"}
    header["candidate_digest"] = CANDIDATE_DIGEST
    base = {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "DR-SEG-001",
        "causal": header,
        "department_mission_ref": led["department_mission_ref"],
        "returned_by": internal["producer"],
        "state": "RETURNED",
        "scope_touched": ["analise de seguranca do portal na versao congelada"],
        "artifact_refs": [f"ledgers/{led['ledger_id']}.md", *led["finding_refs"]],
        "evidence_refs": led["evidence_refs"],
        "candidate_digest": CANDIDATE_DIGEST,
        "test_summary": derive_test_summary(led, executed),
        "pending_refs": [
            *(f"skip: {item['what']}" for item in led["skips"]),
            *led["capability_gap_refs"],
            *led["pending"],
        ],
        "dissent_refs": led["divergences"],
        "returned_to": DIRECTOR,
        "returned_at": led["closed_at"],
    }
    base.update(over)
    return base


def director_mission(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DEPARTMENT_MISSION",
        "department_mission_id": "DM-SEG-001",
        "causal": {
            "work_item_id": "WI-SEG-001",
            "front_id": "FR-SEG-001",
            "handoff_id": "HO-SEG-001",
            "message_id": "MSG-DIRETOR-001",
            "causation_message_ids": ["MSG-CEO-001"],
            "contract_id": "CT-SEG-001",
            "contract_version": 1,
            "contract_digest": DIG,
            "candidate_digest": CANDIDATE_DIGEST,
            "round": 1,
            "attempt": 1,
            "producer": DIRECTOR,
            "producer_version": "1.0.0",
            "producer_digest": DIG,
            "created_at": STAMP,
        },
        "recipient": DEPARTMENT,
        "mode": "ATUA",
        "objective": "avaliar o risco de seguranca do portal antes do go-live",
        "scope_in": ["portal-homolog na revisao congelada"],
        "scope_out": ["correcao de codigo e execucao de bateria"],
        "inputs": ["repositorio do portal, revisao congelada com hash"],
        "deliverables": ["ledger de seguranca com cobertura, achados e risco"],
        "done": ["as onze areas com estado e os dez gates com prova"],
        "required_evidence": ["evidencia admissivel por alegacao viva"],
        "depends_on": [],
        "handoff_to": ["diretor-de-lentes"],
        "decision_authority": ["diretor-de-lentes decide o encaminhamento"],
        "permissions": {
            "default_policy": "deny",
            "allowed_tools": ["leitura de arquivo do alvo"],
            "allowed_resources": ["repositorio do portal"],
            "expires_at": WINDOW_END,
        },
        "stop_when": ["pedido de ato proibido observado"],
        "return_to": DIRECTOR,
        "issued_at": STAMP,
    }
    base.update(over)
    return base


# ---------------------------------------------------------------------------
# Verificações de pacote
# ---------------------------------------------------------------------------

def validate_structure() -> list[str]:
    errors: list[str] = []
    errors.extend(
        validate_required_files(
            [
                SKILL_PATH,
                CONTRACT_PATH,
                OPENAI_PATH,
                SCHEMA_PATH,
                EVALS_PATH,
                PLACAR_PATH,
                PROTOCOL_PATH,
                COVERAGE_PATH,
                ADR_PATH,
                ORIGIN_PATH,
            ],
            "arquivo local",
        )
    )
    errors.extend(
        validate_required_files(
            [
                DIRECTOR_SCHEMA_PATH,
                CEO_SCHEMA_PATH,
                RULES_PATH,
                DIRECTOR_ROOT / "SKILL.md",
                DIRECTOR_ROOT / "departamento-juizes" / "SKILL.md",
                STRUCTURE_ROOT / "ORGANOGRAMA.md",
                STRUCTURE_ROOT / "GUIA-DE-EXPANSAO-E-MIGRACAO.md",
                STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
                STRUCTURE_ROOT / "_compartilhado" / "verificacoes_pacote.py",
            ],
            "vínculo externo",
        )
    )
    if PACKAGE_ROOT.parent.name != "departamentos-operacionais":
        errors.append(
            "o Departamento deve viver sob departamentos-operacionais/, "
            f"está sob {PACKAGE_ROOT.parent.name}/"
        )
    if DIRECTOR_ROOT.name != DIRECTOR:
        errors.append(f"o Departamento deve viver sob {DIRECTOR}/")
    errors.extend(validate_agents_folder(AGENTS_ROOT, AGENT_NAMES))
    if len(AGENT_NAMES) != 8:
        errors.append(f"o time é fixo em 8 capacidades, há {len(AGENT_NAMES)}")
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
    errors = validate_frontmatter(SKILL_PATH, DEPARTMENT)
    errors.extend(
        validate_openai_yaml(OPENAI_PATH, "Departamento de Segurança", f"${DEPARTMENT}")
    )
    for name in AGENT_NAMES:
        root = AGENTS_ROOT / name
        errors.extend(validate_frontmatter(root / "SKILL.md", name))
        errors.extend(
            validate_openai_yaml(
                root / "agents" / "openai.yaml", AGENT_DISPLAY[name], f"${name}"
            )
        )
    return errors


def validate_normative_source() -> list[str]:
    errors: list[str] = []
    skill = SKILL_PATH.read_text(encoding="utf-8")
    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    if RULES_LINK_DEPARTMENT not in skill:
        errors.append("SKILL.md do Departamento sem a fonte normativa do nível 4")
    if RULES_LINK_DEPARTMENT not in contract:
        errors.append("contrato do Departamento sem a fonte normativa do nível 4")
    if RULES_LINK_AGENT in skill:
        errors.append("SKILL.md do Departamento com o caminho relativo do nível 6")
    for token in (
        DIRECTOR,
        "departamento-juizes",
        "SECURITY_TASK",
        "SECURITY_LEDGER",
        "DEPARTMENT_RETURN",
        "BLOCKED_UNAUTHORIZED_ACTIVITY",
        "BLOCKED_BYPASS_ATTEMPT",
        "BLOQUEAR",
        "R6",
        "Jeremias",
    ):
        if token not in skill:
            errors.append(f"SKILL.md sem contrato obrigatório: {token}")
    for name in AGENT_NAMES:
        root = AGENTS_ROOT / name
        agent_skill = (root / "SKILL.md").read_text(encoding="utf-8")
        agent_contract = (root / "CONTRATO-DE-COMPROMISSO.md").read_text(encoding="utf-8")
        if RULES_LINK_AGENT not in agent_skill:
            errors.append(f"{name}: SKILL.md sem a fonte normativa do nível 6")
        if RULES_LINK_AGENT not in agent_contract:
            errors.append(f"{name}: contrato sem a fonte normativa do nível 6")
        if RULES_LINK_DEPARTMENT in agent_skill.replace(RULES_LINK_AGENT, ""):
            errors.append(f"{name}: SKILL.md com o caminho relativo do nível 4")
        if "BLOCKED_BYPASS_ATTEMPT" not in agent_skill:
            errors.append(f"{name}: SKILL.md sem a trava anti-bypass")
        if "SECURITY_TASK" not in agent_skill:
            errors.append(f"{name}: SKILL.md sem o envelope que o autoriza a operar")
        if DEPARTMENT not in agent_skill:
            errors.append(f"{name}: SKILL.md sem a gerente declarada")
        if AGENT_ROLE[name] not in agent_skill:
            errors.append(f"{name}: SKILL.md sem a função {AGENT_ROLE[name]}")
    return errors


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    defs = schema.get("$defs", {})
    expected = {
        "securityTask",
        "securityContribution",
        "securityFinding",
        "securityEvidence",
        "securityCapabilityGap",
        "securityLedger",
        "coverageMap",
        "activeAuthorization",
        "causalHeader",
    }
    missing = expected.difference(defs)
    if missing:
        errors.append(f"schema sem defs: {sorted(missing)}")

    real_agents = sorted(item.name for item in AGENTS_ROOT.iterdir() if item.is_dir())
    identity_enum = defs.get("agentIdentity", {}).get("enum", [])
    if sorted(identity_enum) != real_agents:
        errors.append(
            f"agentIdentity do schema divergente das pastas reais: {sorted(identity_enum)}"
        )
    if sorted(identity_enum) != sorted(AGENT_NAMES):
        errors.append("agentIdentity divergente do time canônico do ADR-010")
    if defs.get("coverageArea", {}).get("enum", []) != COVERAGE_AREAS:
        errors.append("coverageArea do schema divergente das onze áreas da referência")
    if sorted(defs.get("securityRole", {}).get("enum", [])) != sorted(AGENT_ROLE.values()):
        errors.append("securityRole do schema divergente das oito funções")
    if defs.get("gateId", {}).get("enum", []) != LOCAL_GATES:
        errors.append("os dez gates do schema divergem do protocolo, §4")
    if defs.get("blockingTrigger", {}).get("enum", []) != BLOCKING_TRIGGERS:
        errors.append("os cinco gatilhos do schema divergem do protocolo, §5")
    if defs.get("severity", {}).get("enum", []) != SEVERITIES:
        errors.append("as severidades do schema divergem da referência, §5")

    coverage_required = defs.get("coverageMap", {}).get("required", [])
    if sorted(coverage_required) != sorted([*COVERAGE_AREAS, "not_assessed"]):
        errors.append("coverageMap não exige as onze áreas mais not_assessed")

    owner_ref = (
        defs.get("coverageEntry", {}).get("properties", {}).get("owner", {}).get("$ref")
    )
    if owner_ref != "#/$defs/agentIdentityOrDepartment":
        errors.append(
            "coverageEntry.owner precisa aceitar a gerente: ai_llm é consolidada por ela"
        )

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


def validate_no_score(schema: dict[str, Any]) -> list[str]:
    """ADR-010, decisão 3: nenhum campo de nota existe — nem pode ser acrescentado."""
    errors: list[str] = []
    names: set[str] = set()
    collect_property_names(schema, names)
    found = sorted(names & FORBIDDEN_SCORING)
    if found:
        errors.append(f"campos de nota no schema: {found}")

    open_objects = [
        name
        for name, node in schema.get("$defs", {}).items()
        if isinstance(node, dict)
        and node.get("type") == "object"
        and node.get("additionalProperties") is not False
    ]
    if open_objects:
        errors.append(
            "defs de objeto sem additionalProperties: false — campo de nota poderia "
            f"ser acrescentado em {sorted(open_objects)}"
        )
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    for token in ("0-10", "0 a 10", "minimum_score", "cut_score"):
        if token in text:
            errors.append(f"schema menciona escala de nota: {token}")
    return errors


def validate_inherited_authority() -> list[str]:
    """O consumidor **ainda** reserva este Departamento e trava o par de autoria."""
    errors: list[str] = []
    if not DIRECTOR_SCHEMA_PATH.is_file():
        return ["schema do consumidor ausente"]
    director = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8")).get("$defs", {})

    if DEPARTMENT not in director.get("operationalDepartment", {}).get("enum", []):
        errors.append("o Diretor não reconhece este Departamento como operacional")
    if DEPARTMENT not in director.get("knownCapability", {}).get("enum", []):
        errors.append("o Diretor não reconhece este Departamento como produtor conhecido")

    checks = [
        ("departmentMission", "producer", DIRECTOR,
         "a missão departamental deixou de ser emitida pelo Diretor"),
        ("departmentMission", "return_to", DIRECTOR,
         "a missão departamental deixou de retornar ao Diretor"),
        ("departmentReturn", "returned_to", DIRECTOR,
         "o retorno departamental deixou de ir ao Diretor"),
        ("departmentReturn", "returned_by", DEPARTMENT,
         "o Diretor deixou de reservar o retorno a este Departamento"),
        ("departmentReturn", "producer", DEPARTMENT,
         "o Diretor deixou de travar o produtor deste Departamento"),
        ("departmentJudgeReport", "producer", "departamento-juizes",
         "a nota deixou de ser dos Juízes"),
    ]
    for name, prop, expected, message in checks:
        if name not in director:
            errors.append(f"schema do consumidor sem $defs/{name}")
        elif not find_const(director[name], prop, expected):
            errors.append(message)

    header = director.get("causalHeader", {})
    if "candidate_digest" not in header.get("required", []):
        errors.append("o causalHeader do Diretor deixou de exigir candidate_digest")
    if "target_digest" in header.get("properties", {}):
        errors.append("o causalHeader do Diretor passou a aceitar target_digest")
    if director.get("scoreItem", {}).get("properties", {}).get("score") is None:
        errors.append("o Diretor deixou de manter o campo de nota fora deste pacote")
    return errors


def validate_evals() -> list[str]:
    errors: list[str] = []
    catalogue = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    if catalogue.get("skill") != DEPARTMENT:
        errors.append("evals: skill incorreta")
    cases = catalogue.get("cases", [])
    if len(cases) < 12:
        errors.append(f"evals: necessários ao menos 12 casos, há {len(cases)}")
    if not any(case.get("origem") == "real" for case in cases):
        errors.append("evals: falta caso de origem real")
    identifiers = [case.get("id") for case in cases]
    if len(identifiers) != len(set(identifiers)):
        errors.append("evals: id duplicado")
    forbidden = [DEPARTMENT, *AGENT_NAMES]
    for case in cases:
        prompt = case.get("prompt", "")
        for name in forbidden:
            if name in prompt:
                errors.append(f"evals: {case.get('id')} nomeia {name} no prompt")
        if len(case.get("assertions", [])) < 3:
            errors.append(f"evals: {case.get('id')} com menos de 3 assertions")
        if not case.get("origem"):
            errors.append(f"evals: {case.get('id')} sem origem declarada")
        if case.get("acionou") != "NAO_MEDIDO" or case.get("aderiu") != "NAO_MEDIDO":
            errors.append(
                f"evals: {case.get('id')} declara resultado comportamental não executado"
            )
    if not any(case.get("espera_recusa") for case in cases):
        errors.append("evals: nenhum caso de recusa por contrato")
    return errors


def validate_coverage_ownership() -> list[str]:
    """Tarefa 0: dez áreas com agente dona, mais `ai_llm` consolidada pela gerente."""
    errors: list[str] = []
    if sorted(AREA_OWNER) != sorted(COVERAGE_AREAS):
        errors.append(
            f"a tabela de cobertura não descreve as onze áreas: {sorted(AREA_OWNER)}"
        )
    if AREA_OWNER.get(TRANSVERSAL_AREA) != "__transversal__":
        errors.append("a referência deixou de declarar ai_llm como transversal")
    exclusive = exclusive_owner_count(AREA_OWNER)
    if exclusive != 10:
        errors.append(f"esperadas 10 áreas com agente dona, há {exclusive}")
    for area, owner in AREA_OWNER.items():
        if area == TRANSVERSAL_AREA:
            continue
        if owner not in AGENT_NAMES:
            errors.append(f"área {area} com dona fora do time: {owner}")
    without_area = [
        agent for agent in AGENT_NAMES if agent not in AREA_OWNER.values()
    ]
    if without_area:
        errors.append(f"agentes sem área exclusiva: {without_area}")

    skill = SKILL_PATH.read_text(encoding="utf-8")
    banned = [
        "as onze áreas têm dona e estado inicial",
        "onze áreas do `coverage_map` à agente dona",
        "Onze áreas com dona única",
        "Confirmar uma dona única por área do `coverage_map`",
        "cada área aplicável tem dona única existente e válida",
    ]
    for phrase in banned:
        if phrase in skill:
            errors.append(
                f"SKILL.md ainda exige dona de agente para as onze áreas: {phrase!r}"
            )
    if "dez" not in skill.lower():
        errors.append("SKILL.md não distingue as dez áreas de dona exclusiva")
    if "consolidad" not in skill.lower() or "ai_llm" not in skill:
        errors.append("SKILL.md não diz que ai_llm é consolidada pela gerente")
    if "transversal" not in skill:
        errors.append("SKILL.md não declara ai_llm como transversal")
    return errors


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def run() -> int:  # noqa: C901 - catálogo linear de casos
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    director = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))
    mission_def = director["$defs"]["departmentMission"]
    return_def = director["$defs"]["departmentReturn"]

    cases: list[tuple[str, bool, list[str]]] = []

    def case(name: str, expected_valid: bool, errors: list[str]) -> None:
        cases.append((name, expected_valid, errors))

    def accepts(name: str, fixture: Any) -> None:
        """Aceito pelo schema inteiro: prova também que o `oneOf` discrimina."""
        case(f"schema aceita {name}", True, validate_schema(fixture, schema, schema))

    def rejects(name: str, fixture: Any) -> None:
        """Rejeitado pela `$def` do próprio artefato — o erro fica legível.

        Validar o negativo contra o `oneOf` da raiz devolveria sempre
        "0 alternativas", escondendo se a rejeição veio da regra pretendida.
        """
        node = schema["$defs"][DEF_BY_TYPE[fixture["artifact_type"]]]
        case(f"schema rejeita {name}", False, validate_schema(fixture, node, schema))

    def condition(name: str, passed: bool) -> None:
        case(name, True, [] if passed else ["condição recalculada falhou"])

    # --- A. Pacote, metadata, fonte normativa, links, ADR --------------------
    case("estrutura: arquivos, oito pastas canônicas e vínculos externos", True,
         validate_structure())
    case("metadata: frontmatter e interface da gerente e dos oito agentes", True,
         validate_metadata())
    case("fonte normativa única no caminho relativo de cada nível (4 e 6)", True,
         validate_normative_source())
    case("todo link markdown interno do pacote resolve", True, validate_links(PACKAGE_ROOT))
    case("série global de ADR é única em toda a estrutura", True,
         validate_adr_series(STRUCTURE_ROOT))
    case("todo pacote gerente tem validador que roda a trava global", True,
         validate_cobertura_de_validadores(STRUCTURE_ROOT))
    case("a recusa de digest() dispara e ninguém tem cópia privada do motor", True,
         validate_trava_de_digest(STRUCTURE_ROOT))
    case("nenhuma asserção é verdadeira por construção sobre valor produzido", True,
         validate_sem_check_tautologico(STRUCTURE_ROOT))
    cases.append(("nenhum placar de pacote declara total de cadeia como estado corrente", True, validate_placar_nao_declara_cadeia(STRUCTURE_ROOT)))
    cases.append(("a contagem publicada aponta para o digest do instrumento vigente", True, validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)))
    cases.append(("as travas do modulo compartilhado nao estao neutralizadas", True, validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT)))
    cases.append(("toda pendencia declarada nomeia quem responde por ela", True, validate_pendencia_tem_dono(STRUCTURE_ROOT)))
    case("a fonte normativa confere com o valor declarado em ORIGEM.md", True,
         validate_fonte_normativa_conferida(STRUCTURE_ROOT))
    case("forma do schema: $defs, $ref e enum de identidades = pastas reais", True,
         validate_schema_shape(schema))
    case("ausência de nota: nenhum campo de score existe nem pode ser acrescentado", True,
         validate_no_score(schema))
    case("autoridade herdada: o schema do Diretor ainda reserva este Departamento", True,
         validate_inherited_authority())
    case("catálogo de evals comportamentais", True, validate_evals())
    case("cobertura: dez áreas com dona única + ai_llm transversal (tarefa 0)", True,
         validate_coverage_ownership())

    # --- B. Fixtures positivas ----------------------------------------------
    for agent in AGENT_NAMES:
        accepts(f"SECURITY_TASK estática de {AGENT_ROLE[agent]}", task(agent))
    accepts("SECURITY_TASK ativa com autorização completa", active_task())
    accepts("SECURITY_CONTRIBUTION concluída", contribution())
    accepts(
        "SECURITY_CONTRIBUTION parcial com SKIP declarado",
        contribution(status="PARTIAL", skips=[skip_entry()],
                     status_reason="varredura ativa nao executada, SKIP declarado"),
    )
    accepts(
        "SECURITY_CONTRIBUTION com lacuna de capacidade",
        contribution(
            "agente-cadeia-de-suprimentos",
            status="CAPABILITY_GAP",
            status_reason="capacidade indisponivel para a area de cadeia de suprimentos",
            pending=["cadeia de suprimentos sem dona disponivel nesta rodada"],
            coverage_claimed=[
                coverage_claim("supply_chain", state="NAO_AVALIADO", evidence_refs=[])
            ],
            finding_refs=[],
            evidence_refs=[],
        ),
    )
    accepts("SECURITY_FINDING crítico confirmado e aberto", finding())
    accepts("SECURITY_FINDING fechado com reteste pass", closed_finding())
    accepts("SECURITY_FINDING de segredo com incidente aberto", secret_finding())
    accepts(
        "SECURITY_FINDING de segredo fechado com o ciclo completo",
        secret_finding(
            status="closed",
            retest={"performed": True, "evidence_id": "EV-RETESTE-SEG", "result": "pass"},
            acceptance_evidence="reteste com chave revogada, rotacionada e ausente do repositorio",
            evidence_ids=["EV-SEGREDO-001", "EV-RETESTE-SEG"],
            admissible_evidence_ids=["EV-SEGREDO-001", "EV-RETESTE-SEG"],
            secret_response=live_secret(
                revocation_status="completed",
                rotation_status="completed",
                incident_status="closed",
            ),
        ),
    )
    accepts("SECURITY_EVIDENCE de fonte admissível", evidence())
    accepts("SECURITY_EVIDENCE de SKIP declarada inadmissível", skip_evidence())
    accepts("SECURITY_EVIDENCE de atestado com proveniência e custódia", attestation_evidence())
    accepts("SECURITY_CAPABILITY_GAP aberta e escalada ao Diretor", capability_gap())
    accepts("SECURITY_LEDGER que bloqueia por gatilho observado", ledger())
    accepts("SECURITY_LEDGER sem gatilho, com saída positiva", clean_ledger())
    accepts("SECURITY_LEDGER parcial com lacuna e SKIP", partial_ledger())

    # --- C. Negativos: tarefa ------------------------------------------------
    rejects("tarefa com produtor forjado por outro Departamento",
            task(causal=causal(producer="departamento-desenvolvimento")))
    rejects("tarefa endereçada a agente fora do time",
            task(worker_id="agente-ia-e-autonomia"))
    rejects("tarefa ATIVA sem autorização estruturada",
            active_task(authorization="n/a"))
    rejects("tarefa ATIVA contra produção ou dado real",
            active_task(authorization=authorization(production_or_real_user_data=True)))
    rejects("tarefa ATIVA com autorização inválida",
            active_task(authorization=authorization(validity="invalid")))
    rejects("tarefa ATIVA emitida na onda 0, antes de fixar a confiança",
            active_task(wave=0))
    rejects("tarefa ESTATICA carregando autorização de atividade ativa",
            task(authorization=authorization()))
    rejects("prova delegada a quem não é o julgador de admissibilidade",
            task("agente-seguranca-de-aplicacao", role="EVIDENCE"))
    rejects("contenção de segredo delegada a quem descobriu o segredo",
            task("agente-seguranca-de-aplicacao", role="DETECTION_RESPONSE"))
    rejects("tarefa devolvida ao Diretor, contornando a gerente",
            task(return_to=DIRECTOR))
    rejects("tarefa sem nenhuma área de cobertura", task(coverage_areas=[]))
    rejects("tarefa com área fora das onze do coverage_map",
            task(coverage_areas=["ia_llm_dedicada"]))
    rejects("tarefa sem forbidden_context", task(forbidden_context=[]))
    rejects("tarefa em onda inexistente", task(wave=5))
    rejects("tarefa em rodada fora do limite de dez", task(causal=causal(round=11)))
    rejects("tarefa ATIVA sem condição de parada declarada",
            active_task(authorization=authorization(stop_conditions=[])))
    rejects("tarefa ATIVA sem contato de emergência",
            active_task(authorization=authorization(emergency_contact="")))
    rejects("tarefa ATIVA com autorização sem janela resolvível",
            active_task(authorization=authorization(window_end="ontem")))
    rejects("tarefa sem fronteira declarada ao irmão dono", task(scope_out=[]))

    # --- D. Negativos: contribuição -----------------------------------------
    rejects("contribuição COMPLETED com SKIP pendurado",
            contribution(skips=[skip_entry()]))
    rejects("contribuição COMPLETED com área não avaliada",
            contribution(coverage_claimed=[
                coverage_claim("application_api", state="NAO_AVALIADO", evidence_refs=[])
            ]))
    rejects("lacuna de capacidade declarada sem pendência nomeada",
            contribution(status="CAPABILITY_GAP", pending=[]))
    rejects("contribuição devolvida para fora da gerente",
            contribution(return_to=DIRECTOR))
    rejects("contribuição sem nenhuma área declarada", contribution(coverage_claimed=[]))
    rejects("NAO_APLICAVEL sem ativo ou fluxo que o justifique",
            contribution(coverage_claimed=[
                coverage_claim("application_api", state="NAO_APLICAVEL",
                               linked_asset_or_flow="n/a", evidence_refs=[])
            ]))

    # --- E. Negativos: achado ------------------------------------------------
    rejects("achado confirmado sem evidência admissível",
            finding(admissible_evidence_ids=[]))
    rejects("achado fechado sem reteste executado", closed_finding(
        retest={"performed": False, "evidence_id": "n/a", "result": "not_applicable"}))
    rejects("achado fechado com reteste que falhou", closed_finding(
        retest={"performed": True, "evidence_id": "EV-RETESTE-002", "result": "fail"}))
    rejects("reteste declarado executado sem evidência", closed_finding(
        retest={"performed": True, "evidence_id": "n/a", "result": "pass"}))
    rejects("segredo possivelmente válido fechado sem revogação e rotação",
            secret_finding(
                status="closed",
                retest={"performed": True, "evidence_id": "EV-RETESTE-SEG", "result": "pass"},
                acceptance_evidence="o time disse que trocou a chave",
                secret_response=live_secret(incident_status="closed"),
            ))
    rejects("segredo possivelmente válido sem incidente aberto",
            secret_finding(secret_response=live_secret(incident_id="n/a")))
    rejects("segredo possivelmente válido sem responsável pela contenção",
            secret_finding(secret_response=live_secret(responder_agent="n/a")))
    # ADR-010, decisão 5: quem descobre o segredo não declara o incidente contido.
    # A trava saiu da regra recalculada (`secret_conflict`) e virou condição de schema.
    rejects("segredo possivelmente válido descoberto e contido pelo mesmo agente",
            secret_finding(owner_agent="agente-deteccao-e-resposta"))
    rejects("risco aceito sem autoridade que responda por ele",
            finding(risk_acceptance_ref="aceites/RISCO-001.md", risk_owner="n/a"))
    rejects("achado carregando campo de nota", finding(score=9.5))
    rejects("achado atribuído a agente fora do time",
            finding(owner_agent="agente-ia-e-autonomia"))
    rejects("achado com severidade inventada", finding(severity="catastrophic"))
    rejects("achado com confiança fora da escala", finding(confidence="altissima"))
    rejects("achado sem controle observado", finding(control_observed=""))
    rejects("contribuição de agente fora do time",
            contribution(worker_id="agente-ia-e-autonomia"))

    # --- F. Negativos: evidência --------------------------------------------
    rejects("SKIP apresentado como prova admissível",
            skip_evidence(admissibility="ADMISSIVEL", rejection_reason="n/a"))
    rejects("teste ativo sem autorização aceito como prova",
            evidence(type="pentest", tool_version="suite 2.0", authorization_ref="n/a",
                     result="fail", admissibility="ADMISSIVEL", rejection_reason="n/a"))
    rejects("atestado sustentando sozinho alegação crítica",
            attestation_evidence(sustains_critical_claim=True,
                                 admissibility="ADMISSIVEL", rejection_reason="n/a"))
    rejects("evidência inadmissível sem motivo declarado",
            evidence(admissibility="INADMISSIVEL", rejection_reason="n/a",
                     sustains_critical_claim=False))
    rejects("evidência admissível com motivo de rejeição preenchido",
            evidence(rejection_reason="ALEGACAO_SEM_ARTEFATO"))
    rejects("evidência inadmissível sustentando alegação crítica",
            evidence(admissibility="INADMISSIVEL",
                     rejection_reason="ALEGACAO_SEM_ARTEFATO",
                     sustains_critical_claim=True))
    rejects("saída de ferramenta sem a versão da ferramenta",
            evidence(type="sast", tool_version="n/a", admissibility="INADMISSIVEL",
                     rejection_reason="FERRAMENTA_SEM_SAIDA",
                     sustains_critical_claim=False))
    rejects("admissibilidade decidida por quem não é o julgador",
            evidence(ruled_by="agente-seguranca-de-aplicacao"))
    rejects("atestado admissível com proveniência não verificada",
            attestation_evidence(provenance={
                **attestation_evidence()["provenance"], "verification_status": "unknown"}))
    rejects("atestado admissível com chave de assinatura revogada",
            attestation_evidence(signing_key_custody={
                **attestation_evidence()["signing_key_custody"],
                "revocation_status": "revoked"}))
    rejects("evidência admissível sem versão do alvo — SCAN_FORA_DA_VERSAO",
            evidence(artifact_version_or_hash="n/a"))
    rejects("evidência com motivo de rejeição fora da tabela",
            evidence(admissibility="INADMISSIVEL", sustains_critical_claim=False,
                     rejection_reason="PROVA_FRACA"))
    rejects("evidência com classificação fora do enum",
            evidence(classification="secretissimo"))
    rejects("evidência sem limites declarados da coleta", evidence(limits=[]))

    # --- G. Negativos: lacuna ------------------------------------------------
    rejects("lacuna fechada sem evidência de fechamento",
            capability_gap(status="closed"))
    rejects("lacuna escalada para fora do Diretor",
            capability_gap(escalated_to="ceo-maestro"))
    rejects("lacuna com estado seguro diferente de BLOQUEADO",
            capability_gap(safe_state="PARCIAL"))
    rejects("lacuna aberta sem impacto declarado", capability_gap(impact=""))
    rejects("lacuna com função fora das oito do time",
            capability_gap(role_required="IA_AUTONOMIA"))

    # --- H. Negativos: ledger e recomendação de risco ------------------------
    rejects("saída positiva com gatilho de BLOQUEAR presente",
            ledger(risk_recommendation="LIBERAR"))
    rejects("ressalva usada como meio-termo para crítico aberto",
            ledger(risk_recommendation="LIBERAR_COM_RESSALVAS"))
    rejects("crítico aberto sem o gatilho CRITICO_ABERTO listado",
            ledger(blocking_triggers=["FAIL_OPEN"]))
    rejects("fail-open com saída positiva",
            clean_ledger(fail_closed_assessment="ABRE"))
    rejects("fail-open sem o gatilho FAIL_OPEN listado",
            ledger(fail_closed_assessment="ABRE",
                   blocking_triggers=["CRITICO_ABERTO"]))
    rejects("atividade ativa não autorizada com rodada concluída",
            ledger(unauthorized_active_activity=True))
    rejects("COMPLETED com gate local em FAIL",
            clean_ledger(local_gates=gates(AUTORIZACAO="FAIL")))
    rejects("COMPLETED com gate local NAO_VERIFICADO",
            clean_ledger(local_gates=gates(EVIDENCIA="NAO_VERIFICADO")))
    rejects("COMPLETED sem registro de emissão de tarefa — R6",
            clean_ledger(task_issuance_records=[]))
    rejects("COMPLETED com SKIP aberto", clean_ledger(skips=[skip_entry()]))
    rejects("COMPLETED com lacuna de capacidade aberta",
            clean_ledger(capability_gap_refs=["lacunas/GAP-SEG-001.md"]))
    rejects("COMPLETED com área na lista de exclusão explícita",
            clean_ledger(coverage_map=coverage_map(not_assessed=["supply_chain sem dona"])))
    rejects("ledger sem R6 nos riscos residuais", ledger(residual_risks=["R2", "R7"]))
    rejects("ledger com nove gates locais", ledger(local_gates=gates()[:9]))
    rejects("ledger com gate local repetido",
            ledger(local_gates=[*gates()[:9], gate("CONFIANCA", "PASS")]))
    rejects("ledger carregando campo de nota", ledger(score=9.5))
    rejects("ledger aprovando a própria entrega",
            ledger(report_self_approval="allowed"))
    rejects("ledger emitindo gate geral de conformidade",
            ledger(general_audit_gate="ISSUED"))
    rejects("ledger avocando a autoridade de julgamento",
            ledger(judgment_authority=DEPARTMENT))
    rejects("ledger devolvido para fora do Diretor", ledger(returned_to="ceo-maestro"))
    rejects("coverage_map sem a área transversal ai_llm",
            ledger(coverage_map={k: v for k, v in coverage_map().items() if k != "ai_llm"}))
    rejects("área declarada COBERTO sem nenhuma evidência",
            clean_ledger(coverage_map=coverage_map(
                iam=coverage_entry("iam", evidence_refs=[]))))
    rejects("NAO_APLICAVEL com justificativa que não liga a ativo nem a fluxo",
            clean_ledger(coverage_map=coverage_map(
                ai_llm=coverage_entry("ai_llm", state="NAO_APLICAVEL",
                                      justification="nao se aplica",
                                      linked_asset_or_flow="n/a",
                                      evidence_refs=[]))))
    rejects("lacuna aberta com rodada concluída",
            clean_ledger(capability_gap_refs=["lacunas/GAP-SEG-001.md"], status="COMPLETED"))
    rejects("ledger com gatilho fora dos cinco do protocolo",
            ledger(blocking_triggers=["RISCO_ALTO_DEMAIS"]))
    rejects("ledger com recomendação de risco fora do enum",
            ledger(risk_recommendation="LIBERAR_PARCIAL"))
    rejects("ledger sem nenhuma onda executada", ledger(waves_executed=[]))
    rejects("ledger com onda inexistente", ledger(waves_executed=[5]))
    rejects("gate em FAIL sem dono da correção",
            partial_ledger(local_gates=gates(COBERTURA="FAIL")))
    rejects("ledger sem motivo da recomendação de risco", ledger(risk_reason=""))
    rejects("estado de cobertura inventado",
            clean_ledger(coverage_map=coverage_map(
                iam=coverage_entry("iam", state="QUASE_COBERTO"))))

    scoreless_return = to_department_return(clean_ledger(), state="ENTREGUE")
    case("Diretor rejeita retorno em estado diferente de RETURNED", False,
         validate_schema(scoreless_return, return_def, director))
    case("Diretor rejeita missão em modo que não delega", False,
         validate_schema(director_mission(mode="NAO_SE_APLICA"), mission_def, director))

    # --- I. Fronteira: validada contra o schema do CONSUMIDOR ----------------
    blocked_return = to_department_return(ledger())
    case("Diretor aceita o DEPARTMENT_RETURN derivado do ledger que bloqueia", True,
         validate_schema(blocked_return, return_def, director))
    clean_return = to_department_return(clean_ledger())
    case("Diretor aceita o DEPARTMENT_RETURN derivado do ledger sem gatilho", True,
         validate_schema(clean_return, return_def, director))
    case("Diretor aceita a DEPARTMENT_MISSION endereçada a este Departamento", True,
         validate_schema(director_mission(), mission_def, director))

    forged = copy.deepcopy(blocked_return)
    forged["returned_by"] = "departamento-desenvolvimento"
    case("Diretor rejeita retorno assinado por outro Departamento", False,
         validate_schema(forged, return_def, director))

    to_ceo = copy.deepcopy(blocked_return)
    to_ceo["returned_to"] = "ceo-maestro"
    case("Diretor rejeita retorno endereçado ao CEO", False,
         validate_schema(to_ceo, return_def, director))

    unconverted = copy.deepcopy(blocked_return)
    unconverted["causal"] = copy.deepcopy(ledger()["causal"])
    case("Diretor rejeita o cabeçalho interno passado sem converter", False,
         validate_schema(unconverted, return_def, director))

    no_evidence = copy.deepcopy(blocked_return)
    no_evidence["evidence_refs"] = []
    case("Diretor rejeita retorno sem nenhuma evidência", False,
         validate_schema(no_evidence, return_def, director))

    embedded = copy.deepcopy(blocked_return)
    embedded["security_ledger"] = ledger()
    case("Diretor rejeita ledger embutido como campo novo no envelope", False,
         validate_schema(embedded, return_def, director))

    scored = copy.deepcopy(blocked_return)
    scored["score"] = 9.5
    case("Diretor rejeita nota acrescentada ao retorno deste Departamento", False,
         validate_schema(scored, return_def, director))

    case("Diretor rejeita missão que não veio dele", False,
         validate_schema(director_mission(causal={**director_mission()["causal"],
                                                  "producer": "ceo-maestro"}),
                         mission_def, director))
    case("Diretor rejeita missão endereçada a Departamento inexistente", False,
         validate_schema(director_mission(recipient="departamento-seguranca-ofensiva"),
                         mission_def, director))

    # --- J. Aritmética e regras recalculadas em código ----------------------
    blocked = ledger()
    clean = clean_ledger()
    findings_blocked = [finding(), secret_finding()]
    findings_clean = [closed_finding()]

    condition(
        "os gatilhos do ledger que bloqueia são derivados, não lidos",
        derive_triggers(findings_blocked, fail_closed="ABRE")
        == blocked["blocking_triggers"],
    )
    condition(
        "os gatilhos do ledger sem gatilho também são derivados",
        derive_triggers(findings_clean, fail_closed="FECHA") == [],
    )
    condition(
        "os contadores de achado aberto são recomputados dos achados",
        count_open_findings(findings_blocked) == blocked["open_findings"],
    )
    condition(
        "achado suspeito não conta como crítico aberto",
        count_open_findings([finding(status="suspected")])["critical"] == 0
        and count_open_findings([finding()])["critical"] == 1,
    )
    condition(
        "achado fechado sai da contagem de abertos",
        count_open_findings([closed_finding()])["high"] == 0,
    )
    condition(
        "a recomendação do ledger que bloqueia é derivada dos gatilhos",
        derive_recommendation(
            derive_triggers(findings_blocked, fail_closed="ABRE"),
            unauthorized_active=False,
            counters=count_open_findings(findings_blocked),
            skips=[],
        ) == blocked["risk_recommendation"] == "BLOQUEAR",
    )
    condition(
        "a conta errada — ignorar o crítico — daria outro resultado",
        derive_recommendation(
            derive_triggers([finding()], fail_closed="FECHA"),
            unauthorized_active=False,
            counters=count_open_findings([finding()]),
            skips=[],
        ) == "BLOQUEAR"
        and derive_recommendation(
            derive_triggers([finding()], fail_closed="FECHA",
                            counter=count_open_findings_wrong),
            unauthorized_active=False,
            counters=count_open_findings_wrong([finding()]),
            skips=[],
        ) == "LIBERAR",
    )
    condition(
        "a recomendação positiva só existe sem gatilho e sem crítico",
        derive_recommendation(
            derive_triggers(findings_clean, fail_closed="FECHA"),
            unauthorized_active=False,
            counters=count_open_findings(findings_clean),
            skips=[],
        ) == clean["risk_recommendation"] == "LIBERAR",
    )
    condition(
        "SKIP aberto rebaixa a saída positiva para ressalva",
        derive_recommendation([], unauthorized_active=False,
                              counters=count_open_findings(findings_clean),
                              skips=[skip_entry()]) == "LIBERAR_COM_RESSALVAS",
    )
    condition(
        "atividade ativa não autorizada bloqueia sozinha, sem nenhum achado",
        derive_recommendation([], unauthorized_active=True,
                              counters=count_open_findings([]), skips=[]) == "BLOQUEAR",
    )
    condition(
        "INDETERMINADO é honesto sem base, e não contorna gatilho observado",
        derive_recommendation([], unauthorized_active=False,
                              counters=count_open_findings([]), skips=[],
                              determinable=False) == "INDETERMINADO"
        and derive_recommendation(["CRITICO_ABERTO"], unauthorized_active=False,
                                  counters=count_open_findings([]), skips=[],
                                  determinable=False) == "BLOQUEAR",
    )
    condition(
        "segredo possivelmente válido e aberto é gatilho por si só",
        "SEGREDO_VALIDO_EXPOSTO" in derive_triggers([secret_finding()],
                                                    fail_closed="FECHA"),
    )
    condition(
        "segredo com incidente fechado deixa de ser gatilho",
        "SEGREDO_VALIDO_EXPOSTO" not in derive_triggers(
            [secret_finding(secret_response=live_secret(
                revocation_status="completed", rotation_status="completed",
                incident_status="closed"))],
            fail_closed="FECHA"),
    )
    condition(
        "alto confirmado sem aceite formal é gatilho; com aceite, não é",
        "ALTO_EXPLORAVEL_SEM_COMPENSACAO" in derive_triggers(
            [finding(severity="high")], fail_closed="FECHA")
        and "ALTO_EXPLORAVEL_SEM_COMPENSACAO" not in derive_triggers(
            [finding(severity="high", risk_acceptance_ref="aceites/RISCO-001.md",
                     risk_owner="autoridade competente nomeada")],
            fail_closed="FECHA"),
    )
    condition(
        "o status do ledger é derivado das condições da barreira de saída",
        derive_ledger_status(blocked) == blocked["status"] == "COMPLETED"
        and derive_ledger_status(clean) == "COMPLETED",
    )
    condition(
        "SKIP, lacuna, gate em FAIL, exclusão explícita e falta de emissão rebaixam a PARTIAL",
        derive_ledger_status(clean_ledger(skips=[skip_entry()])) == "PARTIAL"
        and derive_ledger_status(clean_ledger(
            capability_gap_refs=["lacunas/GAP-SEG-001.md"])) == "PARTIAL"
        and derive_ledger_status(clean_ledger(
            local_gates=gates(COBERTURA="FAIL"))) == "PARTIAL"
        and derive_ledger_status(clean_ledger(
            coverage_map=coverage_map(not_assessed=["supply_chain"]))) == "PARTIAL"
        and derive_ledger_status(clean_ledger(task_issuance_records=[])) == "PARTIAL",
    )
    condition(
        "atividade ativa não autorizada leva o ledger a BLOCKED",
        derive_ledger_status(ledger(unauthorized_active_activity=True)) == "BLOCKED",
    )
    condition(
        "o status derivado do ledger parcial confere com o declarado",
        derive_ledger_status(partial_ledger()) == partial_ledger()["status"] == "PARTIAL",
    )
    condition(
        "gate local não é teste: dez PASS não viram dez pass no resumo",
        derive_test_summary(blocked) == blocked_return["test_summary"]
        and blocked_return["test_summary"]["pass"] == 0
        and gates_as_tests(blocked) == 10,
    )
    condition(
        "critical_fail do resumo é derivado do gatilho observado",
        blocked_return["test_summary"]["critical_fail"] is True
        and clean_return["test_summary"]["critical_fail"] is False,
    )
    condition(
        "scan e reteste executados de fato entram no resumo com o resultado real",
        derive_test_summary(clean, ["pass", "fail", "skip"])
        == {"pass": 1, "fail": 1, "skip": 1, "skip_reasons": [], "critical_fail": False},
    )
    condition(
        "a conversão de fronteira troca target_digest por candidate_digest",
        "target_digest" not in blocked_return["causal"]
        and blocked_return["causal"]["candidate_digest"] == CANDIDATE_DIGEST
        and "target_digest" in blocked["causal"],
    )
    condition(
        "todo artefato e toda evidência do retorno resolvem a partir do ledger",
        blocked_return["artifact_refs"][0] == f"ledgers/{blocked['ledger_id']}.md"
        and blocked_return["evidence_refs"] == blocked["evidence_refs"]
        and all(ref in blocked_return["pending_refs"] for ref in blocked["pending"]),
    )
    condition(
        "autorização completa e dentro da janela é válida",
        authorization_valid(authorization(), now=NOW, targets=["portal-homolog"],
                            environments=["homologacao"],
                            actions=["varredura passiva de rotas autenticadas"]),
    )
    condition(
        "a janela expirada invalida a autorização que se declara válida",
        authorization()["validity"] == "valid"
        and not authorization_valid(authorization(), now=LATE,
                                    targets=["portal-homolog"],
                                    environments=["homologacao"],
                                    actions=["varredura passiva de rotas autenticadas"]),
    )
    condition(
        "alvo fora do autorizado invalida a autorização",
        not authorization_valid(authorization(), now=NOW, targets=["portal-producao"],
                                environments=["homologacao"],
                                actions=["varredura passiva de rotas autenticadas"]),
    )
    condition(
        "produção é recusa absoluta, mesmo com autorização assinada",
        not authorization_valid(
            authorization(authorized_environments=["producao"]), now=NOW,
            targets=["portal-homolog"], environments=["producao"],
            actions=["varredura passiva de rotas autenticadas"]),
    )
    condition(
        "ação proibida pela autorização invalida a frente",
        not authorization_valid(authorization(), now=NOW, targets=["portal-homolog"],
                                environments=["homologacao"],
                                actions=["exfiltracao de dado"]),
    )
    condition(
        "condição de parada ausente invalida a autorização",
        not authorization_valid(authorization(stop_conditions=[]), now=NOW,
                                targets=["portal-homolog"],
                                environments=["homologacao"],
                                actions=["varredura passiva de rotas autenticadas"]),
    )
    condition(
        "a admissibilidade recalculada confere com a declarada em cada fixture",
        evidence_verdict(evidence())[0] == evidence()["admissibility"]
        and evidence_verdict(skip_evidence()) == (
            skip_evidence()["admissibility"], skip_evidence()["rejection_reason"])
        and evidence_verdict(attestation_evidence())[0] == "ADMISSIVEL",
    )
    condition(
        "SKIP nunca sustenta PASS, e o motivo é o da tabela",
        evidence_verdict(evidence(result="skip")) == ("INADMISSIVEL", "SKIP_COMO_PASS"),
    )
    condition(
        "teste ativo sem autorização e atestado sozinho caem por motivos distintos",
        evidence_verdict(evidence(type="pentest", authorization_ref="n/a"))
        == ("INADMISSIVEL", "TESTE_ATIVO_SEM_AUTORIZACAO")
        and evidence_verdict(attestation_evidence(sustains_critical_claim=True))
        == ("INADMISSIVEL", "ATESTADO_SEM_PRIMARIA"),
    )
    condition(
        "varredura fora da versão avaliada é rejeitada pelo motivo próprio",
        evidence_verdict(evidence(artifact_version_or_hash="n/a"))
        == ("INADMISSIVEL", "SCAN_FORA_DA_VERSAO"),
    )
    condition(
        "prova produzida por quem avalia a própria alegação é inadmissível",
        evidence_verdict(evidence(collected_by="agente-seguranca-de-aplicacao"),
                         claim_owner="agente-seguranca-de-aplicacao")
        == ("INADMISSIVEL", "EVIDENCIA_DO_PROPRIO_AVALIADOR"),
    )
    condition(
        "conflito de interesse: só o julgador de prova recebe a função EVIDENCE",
        task("agente-prova-e-reteste")["role"] == "EVIDENCE"
        and [agent for agent, role in AGENT_ROLE.items() if role == "EVIDENCE"]
        == ["agente-prova-e-reteste"],
    )
    condition(
        "quem descobre o segredo não declara o incidente contido",
        secret_conflict(secret_finding(owner_agent="agente-deteccao-e-resposta"))
        and not secret_conflict(secret_finding())
        and not secret_conflict(finding()),
    )
    condition(
        "quem produziu o achado não certifica a prova de fechamento dele",
        evidence_conflict(evidence(collected_by="agente-seguranca-de-aplicacao"),
                          finding())
        and not evidence_conflict(evidence(), finding()),
    )
    condition(
        "a tabela de rejeição da missão é reexecutada, e o dossiê incompleto não bloqueia",
        mission_verdict(director_mission(), contract_digest=DIG) == "ACEITA"
        and mission_verdict(director_mission(), contract_digest=DIG,
                            dossier_missing=["classificacao de dados"]) == "ACEITA",
    )
    condition(
        "missão de outro produtor e retorno fora do Diretor são bypass",
        mission_verdict(director_mission(causal={**director_mission()["causal"],
                                                 "producer": "ceo-maestro"}),
                        contract_digest=DIG) == "BLOCKED_BYPASS_ATTEMPT"
        and mission_verdict(director_mission(return_to="ceo-maestro"),
                            contract_digest=DIG) == "BLOCKED_BYPASS_ATTEMPT",
    )
    condition(
        "alvo ausente, contrato divergente e destinatário errado bloqueiam a rodada",
        mission_verdict(director_mission(), contract_digest=DIG,
                        target_present=False) == "BLOCKED_INVALID_MISSION"
        and mission_verdict(director_mission(), contract_digest=ALT_DIG)
        == "BLOCKED_CONTRACT_MISMATCH"
        and mission_verdict(director_mission(recipient="departamento-qa-usabilidade"),
                            contract_digest=DIG) == "BLOCKED_INVALID_MISSION",
    )
    condition(
        "pedido de ato proibido bloqueia com o código próprio",
        mission_verdict(director_mission(), contract_digest=DIG,
                        requests=["producao"]) == "BLOCKED_UNAUTHORIZED_ACTIVITY"
        and mission_verdict(director_mission(), contract_digest=DIG,
                            requests=["atividade_ativa_sem_autorizacao"])
        == "BLOCKED_UNAUTHORIZED_ACTIVITY"
        and mission_verdict(director_mission(), contract_digest=DIG,
                            requests=["nota"]) == "BLOCKED_INVALID_MISSION"
        and mission_verdict(director_mission(), contract_digest=DIG,
                            requests=["liberar_com_critico"]) == "BLOCKED_INVALID_MISSION"
        and mission_verdict(director_mission(), contract_digest=DIG,
                            requests=["skip_como_pass"]) == "BLOCKED_INVALID_MISSION",
    )
    condition(
        "cada uma das onze áreas do ledger tem dona admissível pela regra da tarefa 0",
        all(coverage_owner_valid(area, coverage_map()[area]["owner"])
            for area in COVERAGE_AREAS),
    )
    condition(
        "pôr uma agente como dona de ai_llm viola o ADR-010",
        not coverage_owner_valid("ai_llm", "agente-seguranca-de-aplicacao"),
    )
    condition(
        "a gerente não é dona de área de especialidade",
        not coverage_owner_valid("application_api", DEPARTMENT),
    )
    condition(
        "trocar a dona de uma área pela irmã é rejeitado pela regra",
        not coverage_owner_valid("iam", "agente-cadeia-de-suprimentos"),
    )
    condition(
        "a conta de donas exclusivas dá dez, e onze seria a conta errada",
        exclusive_owner_count(AREA_OWNER) == 10
        and len(COVERAGE_AREAS) == 11
        and exclusive_owner_count(AREA_OWNER) != len(COVERAGE_AREAS),
    )
    condition(
        "cada uma das oito capacidades tem função própria e sem repetição",
        len(set(AGENT_ROLE.values())) == 8 and len(AGENT_NAMES) == 8,
    )
    case("digest da fonte normativa confere com o declarado em ORIGEM.md", True,
         conferir_digest_das_regras(RULES_PATH))
    case("digest do próprio schema confere com o declarado", True,
         conferir_digest_declarado(SCHEMA_PATH, SCHEMA_DIGEST_DECLARADO,
                                   "schema do pacote"))

    positives = sum(1 for _, expected, _ in cases if expected)
    negatives = len(cases) - positives
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

    print(f"\nCasos positivos: {positives} · casos negativos: {negatives}")
    if negatives < positives:
        print(
            "[FAIL] regra do passo 9: casos negativos devem ser >= positivos "
            f"({negatives} < {positives})"
        )
        failures += 1
    print(f"Resultado: {len(cases) - failures}/{len(cases)} casos passaram.")
    return 1 if failures else 0


if __name__ == "__main__":
    # T55: recusa medir a Estrutura a partir do runtime, onde a raiz
    # resolve para .claude/skills e as skills do Catalogo viram pacotes.
    recusar_execucao_fora_da_fonte(STRUCTURE_ROOT)
    sys.exit(run())
