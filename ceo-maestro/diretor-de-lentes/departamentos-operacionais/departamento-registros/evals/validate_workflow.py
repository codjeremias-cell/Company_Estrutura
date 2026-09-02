"""Validador determinístico do Departamento de Registros.

Verifica o pacote (arquivos, metadata, fonte normativa, links), o schema interno,
os artefatos internos, **os exemplos normativos do protocolo** e — como regressão
de fronteira — que o envelope produzido é aceito pelo schema do `diretor-de-lentes`.

O motor de schema e as verificações estruturais são **importados** de
`_compartilhado/`; nada deles é copiado para dentro deste pacote.

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
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-registros.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
PLACAR_PATH = PACKAGE_ROOT / "evals" / "PLACAR.md"
PROTOCOL_PATH = PACKAGE_ROOT / "references" / "protocolo-registros.md"
NATURES_PATH = PACKAGE_ROOT / "references" / "naturezas-e-roteamento.md"
ADR_PATH = (
    PACKAGE_ROOT / "references" / "adr-005-quatro-agentes-e-relatorios-de-registros.md"
)
ORIGIN_PATH = PACKAGE_ROOT / "references" / "origem-migracao.md"
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
EVOLUTION_REFERENCE = (
    CEO_ROOT
    / "departamento-evolucao-skills"
    / "references"
    / "mineracao-e-proveniencia.md"
)

DEPARTMENT = "departamento-registros"
AGENT_NAMES = [
    "agente-memoria-e-decisoes",
    "agente-estado-e-handoffs",
    "agente-documentacao-e-materiais",
    "agente-aprendizados-e-relatorios",
]
AGENT_CAPABILITY = {
    "agente-memoria-e-decisoes": "memoria-e-decisoes",
    "agente-estado-e-handoffs": "estado-e-handoffs",
    "agente-documentacao-e-materiais": "documentacao-e-materiais",
    "agente-aprendizados-e-relatorios": "aprendizados-e-relatorios",
}
AGENT_DISPLAY = {
    "agente-memoria-e-decisoes": "Registrador de Memória e Decisões",
    "agente-estado-e-handoffs": "Registrador de Estado e Handoffs",
    "agente-documentacao-e-materiais": "Registrador de Documentação e Materiais",
    "agente-aprendizados-e-relatorios": "Registrador de Aprendizados e Relatórios",
}

NATURES = [
    "memoria-duravel",
    "decisao-adr",
    "estado",
    "documento-produto",
    "guia-playbook",
    "ideia-backlog",
    "aprendizagem",
    "nao-registro",
]
RULE_TO_NATURE = {
    "R1": "nao-registro",
    "R2": "documento-produto",
    "R3": "decisao-adr",
    "R4": "estado",
    "R5": "memoria-duravel",
    "R6": "aprendizagem",
    "R7": "guia-playbook",
    "R8": "ideia-backlog",
}
INTEGRITY_GATES = [
    "REGISTRO_ORFAO",
    "INDICE_ADIANTADO",
    "VIEW_DIVERGENTE",
    "SEGREDO_EM_REGISTRO",
    "SNAPSHOT_COMO_ATUAL",
    "HISTORICO_SEM_DATA",
    "MEMORIA_CONTAMINADA",
    "REGISTRO_PERDIDO",
    "CONVENCAO_IMPROVISADA",
    "FATO_DUPLICADO",
    "FONTE_PERDIDA",
    "CAMINHO_FORA_DA_RAIZ",
    "INSTRUCAO_EMBUTIDA",
    "FONTE_ALTERADA_POR_TERCEIRO",
]
JUDGMENT_GATES = {
    "MEMORIA_CONTAMINADA",
    "CONVENCAO_IMPROVISADA",
    "INSTRUCAO_EMBUTIDA",
    "FONTE_PERDIDA",
}
# protocolo §1.4 — cada state alimenta exatamente um contador; trânsito não fecha.
STATE_COUNTER: dict[str, str | None] = {
    "VERIFICADO": "records_landed",
    "VIGENTE": "records_landed",
    "SUPERADO": "records_landed",
    "ARQUIVADO": "records_landed",
    "HANDOFF_DECLARADO": "records_handed_off",
    "PENDING_DESTINO": "records_pending_destino",
    "RECUSADO_FRONTEIRA": "records_refused_boundary",
    "LACUNA_CAPACIDADE": "records_capability_gap",
    "BLOQUEADO": "records_blocked",
    "PENDING_AUTORIZACAO": "records_blocked",
    "ORFAO": "records_blocked",
    "INDICE_ADIANTADO": "records_blocked",
    "DESCARTADO": "records_discarded",
    "CAPTURADO": None,
    "ROTEADO": None,
    "GRAVADO": None,
    "INDEXADO": None,
}
COUNTER_FIELDS = [
    "records_landed",
    "records_handed_off",
    "records_pending_destino",
    "records_refused_boundary",
    "records_capability_gap",
    "records_blocked",
    "records_discarded",
]
PARTIAL_SEVERITY = [
    "conservation_blocked",
    "integrity_fail",
    "pending_authorization",
    "capability_missing",
    "single_count_unverified",
    "unverified_gate",
    "alcance_de_escrita_insuficiente",
    "decisao_reservada_a_jeremias",
]
RULES_LINK_DEPARTMENT = "../../../../regras-de-ouro/REGRAS-DE-OURO.md"
RULES_LINK_AGENT = "../../../../../../regras-de-ouro/REGRAS-DE-OURO.md"

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
        validate_contratos_de_gerente,
        validate_fonte_normativa_conferida,
        achar_cadeia_no_presente,
        validate_placar_nao_declara_cadeia,
        achar_corpo_neutralizado,
        achar_pendencia_sem_dono,
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
# Regras do contrato, recalculadas em código (nunca lidas do campo declarado)
# --------------------------------------------------------------------------

def count_by_state(states: list[str]) -> dict[str, int]:
    """Contadores do CONSERVATION_LEDGER derivados dos estados observados."""
    counters = {field: 0 for field in COUNTER_FIELDS}
    for state in states:
        counter = STATE_COUNTER[state]
        if counter is not None:
            counters[counter] += 1
    return counters


def invariant_identified_equals_routed(identified: int, routed: int) -> bool:
    return identified == routed


def invariant_routed_equals_sum(routed: int, counters: dict[str, int]) -> bool:
    return routed == sum(counters[field] for field in COUNTER_FIELDS)


def in_transit(states: list[str]) -> list[str]:
    return [state for state in states if STATE_COUNTER[state] is None]


def ledger_closes(
    *,
    unaccounted: list[str],
    identified: int,
    routed: int,
    counters: dict[str, int],
    recount_proof: str,
    delta_final: int,
    entries: int,
) -> str:
    """protocolo §1.4 — `closed` é derivado, nunca escolhido."""
    if not invariant_routed_equals_sum(routed, counters) or delta_final != 0:
        if delta_final != 0:
            return "bloqueado_conservacao"
        return "single_count_unverified"
    if recount_proof == "not_verifiable":
        return "single_count_unverified"
    if unaccounted or entries < 1:
        return "single_count_unverified"
    if not invariant_identified_equals_routed(identified, routed):
        return "single_count_unverified"
    return "closed"


def recount_admissible(
    *,
    proof: str,
    tier: str,
    recorded_at: str,
    decomposition_started_at: str,
    performed_by: str,
    decomposed_by: str,
) -> bool:
    """protocolo §1.4 — o que sustenta a segunda contagem, e onde vale."""
    if proof == "independent_capability":
        return performed_by != decomposed_by
    if proof == "sealed_prior_count":
        if tier != "minima":
            return False
        return datetime.fromisoformat(recorded_at) < datetime.fromisoformat(
            decomposition_started_at
        )
    return False


def gate_independent(
    *, verified_by: str, author: str, mode: str, reproduction_kind: str, gate: str
) -> bool:
    """protocolo §2, regra 7 — a única substituição admitida da independência."""
    if verified_by != author:
        return True
    if mode != "sealed_independent_method":
        return False
    if gate in JUDGMENT_GATES:
        return False
    return reproduction_kind == "command"


def derive_partial_reasons(
    *,
    ledger_status: str,
    gate_results: dict[str, str],
    gaps: int,
    pending_authorization: int,
    out_of_reach_findings: int,
    reserved_to_jeremias: int,
) -> list[str]:
    reasons: set[str] = set()
    if ledger_status == "bloqueado_conservacao":
        reasons.add("conservation_blocked")
    if ledger_status == "single_count_unverified":
        reasons.add("single_count_unverified")
    if any(result == "FAIL" for result in gate_results.values()):
        reasons.add("integrity_fail")
    if any(result == "NAO_VERIFICADO" for result in gate_results.values()):
        reasons.add("unverified_gate")
    if gaps:
        reasons.add("capability_missing")
    if pending_authorization:
        reasons.add("pending_authorization")
    if out_of_reach_findings:
        reasons.add("alcance_de_escrita_insuficiente")
    if reserved_to_jeremias:
        reasons.add("decisao_reservada_a_jeremias")
    return [reason for reason in PARTIAL_SEVERITY if reason in reasons]


def derive_registry_status(
    *,
    mission_blocked: bool,
    ledger_status: str,
    gate_results: dict[str, str],
    gaps: int,
    dossier_missing: int,
    assignments: int,
    transit_records: int,
    partial_reasons: list[str],
) -> str:
    """protocolo §4 — o status é derivado, nunca escolhido."""
    if mission_blocked:
        return "BLOCKED"
    complete = (
        ledger_status == "closed"
        and len(gate_results) == len(INTEGRITY_GATES)
        and all(
            result in {"PASS", "NAO_APLICAVEL"} for result in gate_results.values()
        )
        and gaps == 0
        and dossier_missing == 0
        and assignments >= 1
        and transit_records == 0
        and not partial_reasons
    )
    return "COMPLETED" if complete else "PARTIAL"


def mission_verdict(mission: dict[str, Any], *, contract_digest: str,
                    material_present: bool, material_digest: str,
                    dossier_missing: list[str]) -> str:
    """protocolo §1.0 — tabela de rejeição percorrida no recebimento."""
    causal = mission.get("causal", {})
    if causal.get("producer") != "diretor-de-lentes":
        return "BLOCKED_BYPASS_ATTEMPT"
    if mission.get("return_to") != "diretor-de-lentes":
        return "BLOCKED_BYPASS_ATTEMPT"
    if mission.get("recipient") != DEPARTMENT:
        return "BLOCKED_INVALID_MISSION"
    for field in ("inputs", "done", "required_evidence"):
        if not mission.get(field):
            return "BLOCKED_INVALID_MISSION"
    if not causal.get("contract_digest"):
        return "BLOCKED_INVALID_MISSION"
    if causal.get("contract_digest") != contract_digest:
        return "BLOCKED_CONTRACT_MISMATCH"
    if not material_present or material_digest != MATERIAL_DIGEST:
        return "BLOCKED_SOURCE_MISMATCH"
    # dossiê incompleto NÃO bloqueia: vira registro que não pousa (§1.0)
    del dossier_missing
    return "ACEITA"


PANEL_CONVERSION = {
    "AVAILABLE_OK": ("emitida", "COMPLETED", False),
    "AVAILABLE_BLOCKED": ("emitida", "BLOCKED", True),
    "AVAILABLE_FALHO": ("emitida", "FALHO", True),
    "AVAILABLE_SEM_RETORNO": ("emitida", "SEM_RETORNO", True),
    "INVALID": ("nao_emitida", "SEM_RETORNO", True),
    "CONFLICTED": ("nao_emitida", "SEM_RETORNO", True),
    "MISSING": ("nao_emitida", "SEM_RETORNO", True),
}


def convert_discovery(state: str) -> tuple[str, str, bool]:
    """protocolo §1.8 — estado de descoberta → tarefa, panel[].status e lacuna."""
    return PANEL_CONVERSION[state]


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

CONTRACT_DIGEST = digest("0")
MATERIAL_DIGEST = digest("1")
PRODUCER_DIGEST = digest("2")
CANDIDATE_DIGEST = digest("3")
HEX_BASELINE = "a" * 64
HEX_POST = "b" * 64
TS = "2026-07-26T20:00:00-03:00"
TS_LATER = "2026-07-26T21:00:00-03:00"


def causal(producer: str = DEPARTMENT) -> dict[str, Any]:
    return {
        "work_item_id": "work-001",
        "front_id": "front-registros",
        "handoff_id": "handoff-001",
        "message_id": "message-registros-001",
        "causation_message_ids": ["message-diretor-001"],
        "contract_id": "contract-001",
        "contract_version": 1,
        "contract_digest": CONTRACT_DIGEST,
        "source_digest": MATERIAL_DIGEST,
        "round": 1,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": PRODUCER_DIGEST,
        "created_at": TS,
    }


def gate_evidence(gates: list[str] | None = None) -> list[dict[str, Any]]:
    names = gates or [
        "GATE_DECOMPOSICAO",
        "GATE_DESTINO_UNICO",
        "GATE_CUSTODIA",
        "GATE_FONTE_UNICA",
        "GATE_INDICE",
        "GATE_INTEGRIDADE",
    ]
    return [
        {
            "gate": name,
            "method": f"Ato executado para {name}, com reprodução registrada.",
            "evidence": f"Saída literal do ato de {name}, anexada à rodada.",
            "verified_by": "agente-estado-e-handoffs",
        }
        for name in names
    ]


def destination(
    *,
    derived_role: str = "fonte",
    write_scope: str = "departamento",
    existence: str = "confirmed",
    within: Any = True,
) -> dict[str, Any]:
    node: dict[str, Any] = {
        "path_or_container": "projeto/decisoes/adr-007.md",
        "resolved_path": "C:/alvo/projeto/decisoes/adr-007.md",
        "is_reparse_point": False,
        "within_trusted_root": within,
        "existence": existence,
        "existence_evidence": "Listagem e abertura do arquivo no caminho canônico.",
        "derived_role": derived_role,
        "source_of_truth_ref": (
            "n/a" if derived_role == "fonte" else "projeto/decisoes/adr-007.md"
        ),
        "write_scope": write_scope,
        "secret_scan": "mecanica",
        "index_obligations": [
            {
                "index_ref": "projeto/decisoes/INDICE.md",
                "kind": "mecanica",
                "evidence": "Saída do script de índice anexada.",
            }
        ],
    }
    return node


def convention_ref(level: int = 1) -> dict[str, Any]:
    return {
        "convention": "adr-00N-<slug>.md na pasta do dono da decisão",
        "source": "series de ADR observada na estrutura",
        "channel_level": level,
        "search_method": "Busca do maior número em uso na estrutura inteira, com os concorrentes nomeados.",
        "competing_values_found": ["ADR-0007-<slug>.md no projeto-alvo"],
    }


def routing_decision(
    *,
    record_id: str = "record-001",
    rule: str = "R3",
    nature: str | None = None,
    atomicity: str = "atomic",
    state: str = "VERIFICADO",
    matched: list[str] | None = None,
    channel_level: int = 1,
    dest: Any = None,
    artifact_ref: str = "projeto/decisoes/adr-007.md",
    gates: list[str] | None = None,
    tiebreak: str = "n/a",
    blocked_reason: str = "n/a",
    split_into: list[str] | None = None,
    owner: str = "memoria-e-decisoes",
    paired_with: list[str] | None = None,
) -> dict[str, Any]:
    resolved_nature = nature or RULE_TO_NATURE.get(rule, "estado")
    if dest is None:
        dest = destination(
            write_scope=(
                "somente_leitura"
                if resolved_nature == "memoria-duravel"
                else "departamento"
            )
        )
    return {
        "artifact_type": "ROUTING_DECISION",
        "record_id": record_id,
        "durable_key": "projeto:decisoes:adr-007#motor-de-banco",
        "department_mission_ref": "department-mission-10",
        "source_fragment": "decidimos trocar o motor de banco",
        "channel_level": channel_level,
        "nature": resolved_nature,
        "record_scope": "projeto",
        "matched_rules": matched if matched is not None else ([rule] if rule != "n/a" else []),
        "deciding_rule": rule,
        "tiebreak_ref": tiebreak,
        "atomicity": atomicity,
        "split_into": split_into or [],
        "destination": dest,
        "convention_ref": convention_ref(min(channel_level, 2)),
        "owner_capability_id": owner,
        "data_classification": "internal",
        "paired_with": paired_with or [],
        "state": state,
        "gate_evidence": gate_evidence(gates),
        "artifact_ref": artifact_ref,
        "blocked_reason": blocked_reason,
        "rationale": "Fixa escolha estrutural cara de reverter, com alternativas registradas.",
    }


def landed_decision() -> dict[str, Any]:
    return routing_decision()


def handoff_decision() -> dict[str, Any]:
    return routing_decision(
        record_id="record-002",
        rule="R5",
        state="HANDOFF_DECLARADO",
        artifact_ref="n/a",
        dest=destination(write_scope="somente_leitura"),
        owner="memoria-e-decisoes",
        paired_with=["record-001"],
    )


def refusal_decision() -> dict[str, Any]:
    return routing_decision(
        record_id="record-003",
        rule="R1",
        state="RECUSADO_FRONTEIRA",
        artifact_ref="n/a",
        dest="n/a",
        owner="n/a-recusa-indelegavel-da-gerente",
    )


def pending_decision() -> dict[str, Any]:
    return routing_decision(
        record_id="record-004",
        rule="n/a",
        nature="estado",
        atomicity="unmatched",
        state="PENDING_DESTINO",
        matched=[],
        artifact_ref="n/a",
        dest="n/a",
    )


def split_decision() -> dict[str, Any]:
    return routing_decision(
        record_id="record-005",
        rule="n/a",
        nature="decisao-adr",
        atomicity="split_required",
        state="CAPTURADO",
        matched=["R3", "R4"],
        split_into=["record-006", "record-007"],
        artifact_ref="n/a",
        dest="n/a",
        tiebreak="n/a",
    )


def write_target(**overrides: Any) -> dict[str, Any]:
    node = {
        "source_of_truth": "projeto/decisoes/adr-007.md",
        "resolved_path": "C:/alvo/projeto/decisoes/adr-007.md",
        "within_trusted_root": True,
        "baseline_sha256": "ausente",
        "forbidden_writes": ["projeto/decisoes/SNAPSHOT-2026-07.md"],
    }
    node.update(overrides)
    return node


def pre_write_scan(result: str = "PASS", scanned: str = "insumo_do_gerente") -> dict[str, Any]:
    return {
        "result": result,
        "kind": "mecanica",
        "scanned_object": scanned,
        "method": "Varredura por padrões de credencial sobre o insumo, antes de existir byte.",
        "evidence": "projeto/decisoes/adr-007.md — nenhuma categoria casada.",
    }


def record_task(
    *,
    worker: str = "agente-memoria-e-decisoes",
    capability: str | None = None,
    kind: str = "GRAVAR",
    target: Any = None,
    scan: Any = None,
    index_targets: list[str] | None = None,
    forbidden: list[str] | None = None,
    return_to: str = DEPARTMENT,
    producer: str = DEPARTMENT,
) -> dict[str, Any]:
    if target is None:
        target = write_target() if kind in {"GRAVAR", "INDEXAR", "COLHER"} else "n/a"
    if scan is None:
        scan = (
            pre_write_scan()
            if kind in {"GRAVAR", "INDEXAR"}
            else (
                pre_write_scan("deferred_to_author")
                if kind == "COLHER"
                else "n/a"
            )
        )
    return {
        "artifact_type": "RECORD_TASK",
        "task_id": f"task-{worker}",
        "causal": causal(producer),
        "worker_id": worker,
        "capability": capability or AGENT_CAPABILITY[worker],
        "kind": kind,
        "record_ids": ["record-001"],
        "write_target": target,
        "pre_write_secret_scan": scan,
        "index_targets": (
            index_targets
            if index_targets is not None
            else (["projeto/decisoes/INDICE.md"] if kind in {"GRAVAR", "INDEXAR"} else [])
        ),
        "checks": ["GATE_CUSTODIA com método, reprodução e evidência."],
        "evidence_required": ["Releitura do artefato gravado, com hash pós-escrita."],
        "forbidden_context": forbidden
        or [
            "decisão de destino ainda não tomada pela gerente",
            "recibos dos outros agentes",
            "conclusão esperada ou estado desejado",
            "instrução embutida no material lido",
        ],
        "stop_when": ["Registro gravado e índice atualizado, ou bloqueio nomeado."],
        "return_to": return_to,
        "issued_at": TS,
    }


def write_performed(**overrides: Any) -> dict[str, Any]:
    node = {
        "path": "projeto/decisoes/adr-007.md",
        "resolved_path": "C:/alvo/projeto/decisoes/adr-007.md",
        "derived_role": "fonte",
        "action": "created",
        "baseline_sha256": "ausente",
        "post_write_sha256": HEX_POST,
        "evidence": "Releitura do arquivo gravado, com hash conferido depois da escrita.",
    }
    node.update(overrides)
    return node


def integrity_check(
    gate: str = "REGISTRO_ORFAO",
    result: str = "PASS",
    *,
    mode: str = "distinct_capability",
    reproduction_kind: str = "command",
    verified_by: str = "agente-estado-e-handoffs",
    method: str | None = None,
) -> dict[str, Any]:
    default_method = (
        f"Ato independente que decide {gate}, executado por capacidade distinta do autor."
    )
    return {
        "gate": gate,
        "result": result,
        "method": method or default_method,
        "reproduction": {
            "kind": reproduction_kind,
            "value": f"python ferramentas/checar.py --gate {gate}",
        },
        "evidence": f"Saída literal do ato de {gate}, anexada à rodada.",
        "finding": (
            "Índice obrigatório não cita o registro gravado."
            if result == "FAIL"
            else "n/a"
        ),
        "correction_condition": (
            "Publicar a entrada datada no índice e reexecutar o gate."
            if result == "FAIL"
            else "n/a"
        ),
        "correction_owner": "departamento" if result == "FAIL" else "n/a",
        "verified_by": verified_by,
        "verification_mode": mode,
    }


def integrity_report(overrides: dict[str, str] | None = None) -> list[dict[str, Any]]:
    results = overrides or {}
    return [
        integrity_check(gate, results.get(gate, "PASS")) for gate in INTEGRITY_GATES
    ]


def record_receipt(
    *,
    worker: str = "agente-memoria-e-decisoes",
    status: str = "COMPLETED",
    writes: list[dict[str, Any]] | None = None,
    checks: list[dict[str, Any]] | None = None,
    scan_result: str = "PASS",
    touched: list[dict[str, Any]] | None = None,
    return_to: str = DEPARTMENT,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "artifact_type": "RECORD_RECEIPT",
        "task_id": f"task-{worker}",
        "worker_id": worker,
        "capability": AGENT_CAPABILITY[worker],
        "contract_digest": CONTRACT_DIGEST,
        "source_digest": MATERIAL_DIGEST,
        "authored_content_secret_scan": {
            "result": scan_result,
            "kind": "mecanica",
            "method": "Varredura por padrões de credencial sobre os bytes a gravar, antes de gravá-los.",
            "evidence": "projeto/decisoes/adr-007.md — nenhuma categoria casada.",
        },
        "writes_performed": writes if writes is not None else [write_performed()],
        "index_updates": ["projeto/decisoes/INDICE.md — entrada datada 2026-07-26."],
        "integrity_checks": checks if checks is not None else [integrity_check()],
        "records_touched": touched
        if touched is not None
        else [{"record_id": "record-001", "state_reached": "GRAVADO"}],
        "embedded_instruction_findings": [],
        "pending": [],
        "status": status,
        "return_to": return_to,
        "issued_at": TS_LATER,
    }
    if status == "BLOCKED":
        receipt["writes_performed"] = []
        receipt["records_touched"] = []
        receipt["blocked_reason"] = (
            "Varredura de autoria não verificável neste runtime; nada foi gravado."
        )
    return receipt


def capability_gap(status: str = "OPEN", owner: str = "diretor-de-lentes") -> dict[str, Any]:
    return {
        "artifact_type": "REGISTRY_CAPABILITY_GAP",
        "capability": "Gravação de estado sem executor nesta rodada.",
        "worker_id": "agente-estado-e-handoffs",
        "record_ids": ["record-004"],
        "expected_contract": "Gravar a tarefa derivada na fonte de estado e devolver recibo válido.",
        "discovery_evidence": "SEM_RETORNO observado na tarefa task-agente-estado-e-handoffs.",
        "preserved_inputs": [
            "Conteúdo íntegro do registro record-004, preservado sem reescrita."
        ],
        "impact": "A tarefa derivada não pousa e a soma do ledger não fecha como se nada faltasse.",
        "status": status,
        "owner": owner,
    }


def recount_block(
    *,
    proof: str = "independent_capability",
    delta_final: int = 0,
    delta_inicial: int = 1,
    recorded_at: str = TS_LATER,
    started_at: str = TS,
    artifact_ref: str = "registros/ledger/recontagem-001.json",
    performed_by: str = "agente-estado-e-handoffs",
    recounted: int = 5,
) -> dict[str, Any]:
    return {
        "performed_by": performed_by,
        "recount_proof": proof,
        "artifact_ref": artifact_ref,
        "recorded_at": recorded_at,
        "decomposition_started_at": started_at,
        "records_recounted": recounted,
        "slices": [
            {
                "index": index,
                "fragment_ref": f"fragmento-{index:02d}",
                "rule_named": rule,
            }
            for index, rule in enumerate(["R3", "R5", "R1", "R4", "nenhuma"])
        ],
        "delta_inicial": delta_inicial,
        "delta_final": delta_final,
        "resolution_kind": "adocao_pelo_decompositor",
        "method": "Recontagem sobre o mesmo recorte declarado, sem ver a decomposição.",
    }


DEFAULT_ENTRIES = [
    landed_decision,
    handoff_decision,
    refusal_decision,
    pending_decision,
]


def conservation_ledger(
    *,
    states: list[str] | None = None,
    entries: list[dict[str, Any]] | None = None,
    recount: dict[str, Any] | None = None,
    unaccounted: list[str] | None = None,
    status: str | None = None,
    identified: int | None = None,
    routed: int | None = None,
    counters: dict[str, int] | None = None,
    invariant_one: bool | None = None,
    invariant_two: bool | None = None,
) -> dict[str, Any]:
    resolved_entries = (
        entries if entries is not None else [maker() for maker in DEFAULT_ENTRIES]
    )
    resolved_states = states or [entry["state"] for entry in resolved_entries]
    resolved_counters = counters or count_by_state(resolved_states)
    resolved_identified = (
        identified if identified is not None else len(resolved_states)
    )
    resolved_routed = routed if routed is not None else len(resolved_states)
    resolved_recount = recount or recount_block(recounted=resolved_identified)
    resolved_unaccounted = unaccounted or []
    resolved_status = status or ledger_closes(
        unaccounted=resolved_unaccounted,
        identified=resolved_identified,
        routed=resolved_routed,
        counters=resolved_counters,
        recount_proof=resolved_recount["recount_proof"],
        delta_final=resolved_recount["delta_final"],
        entries=len(resolved_entries),
    )
    ledger = {
        "artifact_type": "CONSERVATION_LEDGER",
        "conservation_ledger_id": "conservation-ledger-001",
        "causal": causal(),
        "department_mission_ref": "department-mission-10",
        "artifact_ref": "registros/ledger/conservacao-001.json",
        "recorded_at": TS_LATER,
        "scope_of_decomposition": {
            "kind": "delivered_delimited",
            "included_span": "transcript da sessão, do início ao fim do bloco entregue",
            "included_span_digest": MATERIAL_DIGEST,
            "excluded_spans": ["envelope da missão: escopo, limites, prazo e motivação"],
            "method": "Recorte declarado e datado antes de a recontagem existir.",
            "method_declared_at": TS,
            "shared_with_recount": True,
        },
        "records_identified": resolved_identified,
        "records_routed": resolved_routed,
        "recount": resolved_recount,
        "divergences": [],
        "entries": resolved_entries,
        "unaccounted": resolved_unaccounted,
        "invariant_identified_equals_routed": (
            invariant_one
            if invariant_one is not None
            else invariant_identified_equals_routed(resolved_identified, resolved_routed)
        ),
        "invariant_routed_equals_sum": (
            invariant_two
            if invariant_two is not None
            else invariant_routed_equals_sum(resolved_routed, resolved_counters)
        ),
        "ledger_status": resolved_status,
    }
    ledger.update(resolved_counters)
    ordered = {}
    for key in [
        "artifact_type",
        "conservation_ledger_id",
        "causal",
        "department_mission_ref",
        "artifact_ref",
        "recorded_at",
        "scope_of_decomposition",
        "records_identified",
        "records_routed",
        *COUNTER_FIELDS,
        "recount",
        "divergences",
        "entries",
        "unaccounted",
        "invariant_identified_equals_routed",
        "invariant_routed_equals_sum",
        "ledger_status",
    ]:
        ordered[key] = ledger[key]
    return ordered


def learning_lesson(**overrides: Any) -> dict[str, Any]:
    lesson = {
        "licao_id": "licao-001",
        "projeto": "Estrutura Final de Skills",
        "categoria_falha": "gate-tautologico",
        "ocorrido_em": TS,
        "o_que_e": "Validador que confere presença de string não prova comportamento.",
        "evidence_excerpt": "trecho literal do relatório, com credencial substituída por [REDIGIDO: token]",
        "fonte_ref": "ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-registros/references/protocolo-registros.md",
        "fonte_titulo": "Protocolo único de registros",
        "fonte_versao": "2026-07-26",
        "fonte_digest": MATERIAL_DIGEST,
        "acessado_em": TS_LATER,
        "limite_declarado": "A fonte não cobre runtime sem API de caminho canônico.",
        "alvos_afetados": ["departamento-registros"],
        "sinais": {"acionou": True, "aderiu": True, "contorno": "n/a"},
    }
    lesson.update(overrides)
    return lesson


def learning_report(
    *,
    lessons: list[dict[str, Any]] | None = None,
    gaps: list[str] | None = None,
    saturation: bool = True,
    return_to: str = "diretor-de-lentes",
    produced_for: str = "departamento-evolucao-skills",
    requested_via: str = "ceo-maestro",
    producer: str = DEPARTMENT,
) -> dict[str, Any]:
    return {
        "artifact_type": "LEARNING_REPORT",
        "report_id": "learning-report-001",
        "causal": causal(producer),
        "department_mission_ref": "department-mission-10",
        "produced_for": produced_for,
        "requested_via": requested_via,
        "window": {"from": TS, "to": TS_LATER},
        "saturation_declared": saturation,
        "licoes": lessons if lessons is not None else [learning_lesson()],
        "gaps_de_colheita": gaps if gaps is not None else [],
        "artifact_ref": "registros/relatorios/aprendizagem/2026-07-26-licoes.md",
        "return_to": return_to,
        "recorded_at": TS_LATER,
    }


def assignment(worker: str, kind: str = "GRAVAR") -> dict[str, Any]:
    return {
        "task_id": f"task-{worker}",
        "worker_id": worker,
        "capability": AGENT_CAPABILITY[worker],
        "kind": kind,
        "issued_at": TS,
        "destination": f"registros/tarefas/task-{worker}.json",
    }


def panel_item(worker: str, status: str = "COMPLETED") -> dict[str, Any]:
    return {
        "worker_id": worker,
        "capability": AGENT_CAPABILITY[worker],
        "status": status,
        "path": f"agentes/{worker}/SKILL.md",
        "discovery_evidence": f"SKILL.md e agents/openai.yaml enumerados em {worker}/.",
    }


def mission_tier(tier: str = "padrao", disqualified: list[str] | None = None,
                 qualified: list[str] | None = None) -> dict[str, Any]:
    return {
        "tier": tier,
        "decided_at": TS,
        "qualified_by": qualified if qualified is not None else ["S1", "S2"],
        "disqualified_by": disqualified if disqualified is not None else ["S4"],
        "narrowed": False,
    }


def boundary_refusal(result: str = "identical") -> dict[str, Any]:
    return {
        "record_id": "record-003",
        "request_fragment": "corrige aquele bug do DAO",
        "why_not_a_record": "Pede executar trabalho de outra especialidade, não guardar um fato.",
        "suggested_capability": "departamento-desenvolvimento",
        "side_effects_proof": {
            "method": "Listagem e hash da subárvore antes e depois da recusa.",
            "before": HEX_BASELINE,
            "after": HEX_BASELINE,
            "result": result,
        },
    }


def registry_ledger(
    *,
    status: str = "COMPLETED",
    gates: dict[str, str] | None = None,
    gaps: list[dict[str, Any]] | None = None,
    conservation: dict[str, Any] | None = None,
    assignments: list[dict[str, Any]] | None = None,
    partial_reasons: list[str] | None = None,
    learning_ref: str = "n/a",
    dossier_missing: list[str] | None = None,
    pending: list[str] | None = None,
    return_to: str = "diretor-de-lentes",
    tier: dict[str, Any] | None = None,
    refusals: list[dict[str, Any]] | None = None,
    panel: list[dict[str, Any]] | None = None,
    report: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "artifact_type": "REGISTRY_LEDGER",
        "registry_ledger_id": "registry-ledger-001",
        "causal": causal(),
        "department_mission_ref": "department-mission-10",
        "mission_tier": tier or mission_tier(),
        "dossier_missing": dossier_missing or [],
        "assignments": assignments
        if assignments is not None
        else [assignment(name) for name in AGENT_NAMES[:2]],
        "panel": panel
        if panel is not None
        else [panel_item(name) for name in AGENT_NAMES[:2]],
        "conservation_ledger": conservation or conservation_ledger(),
        "integrity_report": report if report is not None else integrity_report(gates),
        "learning_report_ref": learning_ref,
        "capability_gaps": gaps or [],
        "boundary_refusals": refusals if refusals is not None else [boundary_refusal()],
        "status": status,
        "partial_reasons": partial_reasons or [],
        "evidence_refs": ["registros/ledger/conservacao-001.json"],
        "escalations_required": [],
        "pending": pending
        or [
            "R6 — a existência do time não é verificável pelo runtime; registro de emissão anexado."
        ],
        "return_to": return_to,
        "recorded_at": TS_LATER,
    }


# --------------------------------------------------------------------------
# Derivação para o envelope de fronteira do consumidor
# --------------------------------------------------------------------------

def derive_department_return(
    ledger: dict[str, Any],
    *,
    candidate_digest: str = CANDIDATE_DIGEST,
    keep_internal_causal: bool = False,
) -> dict[str, Any]:
    """Converte o REGISTRY_LEDGER interno no envelope que o Diretor consome.

    A conversão é mecânica e **não é identidade**: o `causalHeader` do Diretor
    exige `candidate_digest` e não conhece `source_digest`. Manter o cabeçalho
    interno intacto é caso negativo, não atalho.
    """
    header = copy.deepcopy(ledger["causal"])
    if not keep_internal_causal:
        header.pop("source_digest")
        header["candidate_digest"] = candidate_digest
    conservation = ledger["conservation_ledger"]
    return {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "department-return-010",
        "causal": header,
        "department_mission_ref": ledger["department_mission_ref"],
        "returned_by": DEPARTMENT,
        "state": "RETURNED",
        "scope_touched": [
            "Decomposição, roteamento por natureza e conservação da rodada."
        ],
        "artifact_refs": [
            conservation["artifact_ref"],
            "registros/ledger/registry-ledger-001.json",
        ],
        "evidence_refs": ledger["evidence_refs"],
        "candidate_digest": candidate_digest,
        "test_summary": {
            "pass": 0,
            "fail": 0,
            "skip": 0,
            "skip_reasons": [],
            "critical_fail": False,
        },
        "pending_refs": [
            f"pending/{index:02d}" for index in range(len(ledger["pending"]))
        ],
        "dissent_refs": [],
        "returned_to": "diretor-de-lentes",
        "returned_at": TS_LATER,
    }


def director_mission(
    *,
    producer: str = "diretor-de-lentes",
    recipient: str = DEPARTMENT,
    return_to: str = "diretor-de-lentes",
    contract_digest: str = CONTRACT_DIGEST,
) -> dict[str, Any]:
    return {
        "artifact_type": "DEPARTMENT_MISSION",
        "department_mission_id": "department-mission-10",
        "causal": {
            "work_item_id": "work-001",
            "front_id": "front-registros",
            "handoff_id": "handoff-001",
            "message_id": "message-diretor-001",
            "causation_message_ids": ["message-ceo-001"],
            "contract_id": "contract-001",
            "contract_version": 1,
            "contract_digest": contract_digest,
            "candidate_digest": CANDIDATE_DIGEST,
            "round": 1,
            "attempt": 1,
            "producer": producer,
            "producer_version": "1.0.0",
            "producer_digest": PRODUCER_DIGEST,
            "created_at": TS,
        },
        "recipient": recipient,
        "mode": "ATUA",
        "objective": "Registrar o resultado da sessão, com destino provado e contagem conservada.",
        "scope_in": ["Material original preservado da sessão."],
        "scope_out": ["Correção de código e execução de teste."],
        "inputs": ["material original preservado", "trusted_root canônico do alvo"],
        "deliverables": ["REGISTRY_LEDGER com conservação fechada"],
        "done": ["Todo registro identificado com desfecho terminal."],
        "required_evidence": ["Catorze gates de integridade com método e evidência."],
        "depends_on": [],
        "handoff_to": ["departamento-juizes"],
        "decision_authority": ["Natureza, destino e fechamento do ledger."],
        "permissions": {
            "default_policy": "deny",
            "allowed_tools": ["leitura de arquivo", "hash"],
            "allowed_resources": ["projeto/decisoes/**"],
            "expires_at": TS_LATER,
        },
        "stop_when": ["Ledger fechado ou bloqueio nomeado."],
        "return_to": return_to,
        "issued_at": TS,
    }


# --------------------------------------------------------------------------
# Exemplos normativos do protocolo — parser mínimo + concretização
# --------------------------------------------------------------------------

def _strip_comment(line: str) -> str:
    quoted = False
    for index, char in enumerate(line):
        if char == '"':
            quoted = not quoted
        elif char == "#" and not quoted:
            return line[:index].rstrip()
    return line.rstrip()


def _split_flow(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    quoted = False
    current = ""
    for char in text:
        if char == '"':
            quoted = not quoted
        if not quoted:
            if char in "{[":
                depth += 1
            elif char in "}]":
                depth -= 1
            elif char == "," and depth == 0:
                parts.append(current)
                current = ""
                continue
        current += char
    if current.strip():
        parts.append(current)
    return parts


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith("{") and raw.endswith("}"):
        node: dict[str, Any] = {}
        for part in _split_flow(raw[1:-1]):
            key, _, value = part.partition(":")
            node[key.strip()] = _parse_value(value)
        return node
    if raw.startswith("[") and raw.endswith("]"):
        return [_parse_value(part) for part in _split_flow(raw[1:-1])]
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return raw[1:-1]
    return raw


def _parse_map(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    node: dict[str, Any] = {}
    while index < len(lines):
        level, content = lines[index]
        if level < indent or content.startswith("- "):
            break
        key, _, rest = content.partition(":")
        key = key.strip()
        rest = rest.strip()
        index += 1
        if rest:
            node[key] = _parse_value(rest)
            continue
        if index < len(lines) and lines[index][0] > level:
            child_indent = lines[index][0]
            if lines[index][1].startswith("- "):
                node[key], index = _parse_list(lines, index, child_indent)
            else:
                node[key], index = _parse_map(lines, index, child_indent)
        else:
            node[key] = ""
    return node, index


def _parse_list(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    while index < len(lines):
        level, content = lines[index]
        if level != indent or not content.startswith("- "):
            break
        body = content[2:]
        index += 1
        block = [(level + 2, body)]
        while index < len(lines) and lines[index][0] > level:
            block.append(lines[index])
            index += 1
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*\s*:", body):
            item, _ = _parse_map(block, 0, level + 2)
            items.append(item)
        else:
            items.append(_parse_value(body))
    return items, index


def parse_yaml_block(text: str) -> dict[str, Any]:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        content = _strip_comment(raw)
        if not content.strip():
            continue
        lines.append((len(content) - len(content.lstrip(" ")), content.strip()))
    node, _ = _parse_map(lines, 0, 0)
    return node


def protocol_examples() -> dict[str, Any]:
    """Cada bloco ```yaml do protocolo, indexado pela chave de topo."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    blocks = re.findall(r"```yaml\r?\n(.*?)```", text, flags=re.DOTALL)
    examples: dict[str, Any] = {}
    for block in blocks:
        parsed = parse_yaml_block(block)
        if len(parsed) != 1:
            continue
        name, body = next(iter(parsed.items()))
        examples[name] = body
    return examples


CONCRETE: dict[str, Any] = {
    # --- causal, comum a três envelopes ------------------------------------
    "causal.work_item_id": "work-001",
    "causal.front_id": "front-registros",
    "causal.handoff_id": "handoff-001",
    "causal.message_id": "message-registros-001",
    "causal.causation_message_ids[]": "message-diretor-001",
    "causal.contract_id": "contract-001",
    "causal.contract_version": 1,
    "causal.contract_digest": CONTRACT_DIGEST,
    "causal.source_digest": MATERIAL_DIGEST,
    "causal.round": 1,
    "causal.attempt": 1,
    "causal.producer_version": "1.0.0",
    "causal.producer_digest": PRODUCER_DIGEST,
    "causal.created_at": TS,
    # --- RECORD_TASK -------------------------------------------------------
    "task_id": "task-agente-memoria-e-decisoes",
    "worker_id": "agente-memoria-e-decisoes",
    "capability": "memoria-e-decisoes",
    "kind": "GRAVAR",
    "record_ids[]": "record-001",
    "write_target.source_of_truth": "projeto/decisoes/adr-007.md",
    "write_target.resolved_path": "C:/alvo/projeto/decisoes/adr-007.md",
    "write_target.within_trusted_root": True,
    "write_target.baseline_sha256": "ausente",
    "write_target.forbidden_writes[]": "projeto/decisoes/SNAPSHOT-2026-07.md",
    "pre_write_secret_scan.result": "PASS",
    "pre_write_secret_scan.kind": "mecanica",
    "pre_write_secret_scan.scanned_object": "insumo_do_gerente",
    "pre_write_secret_scan.method": "Varredura por padrões de credencial sobre o insumo, antes de existir byte.",
    "pre_write_secret_scan.evidence": "projeto/decisoes/adr-007.md — nenhuma categoria casada.",
    "index_targets[]": "projeto/decisoes/INDICE.md",
    "checks[]": "GATE_CUSTODIA com método, reprodução e evidência.",
    "evidence_required[]": "Releitura do artefato gravado, com hash pós-escrita.",
    "stop_when[]": "Registro gravado e índice atualizado, ou bloqueio nomeado.",
    "issued_at": TS,
    # --- RECORD_RECEIPT ----------------------------------------------------
    "contract_digest": CONTRACT_DIGEST,
    "source_digest": MATERIAL_DIGEST,
    "authored_content_secret_scan.result": "PASS",
    "authored_content_secret_scan.kind": "mecanica",
    "authored_content_secret_scan.method": "Varredura sobre os bytes que serão gravados, antes de gravá-los.",
    "authored_content_secret_scan.evidence": "projeto/decisoes/adr-007.md — nenhuma categoria casada.",
    "writes_performed[].path": "projeto/decisoes/adr-007.md",
    "writes_performed[].resolved_path": "C:/alvo/projeto/decisoes/adr-007.md",
    "writes_performed[].derived_role": "fonte",
    "writes_performed[].action": "created",
    "writes_performed[].baseline_sha256": "ausente",
    "writes_performed[].post_write_sha256": HEX_POST,
    "writes_performed[].evidence": "Releitura do arquivo gravado, com hash conferido.",
    "index_updates[]": "projeto/decisoes/INDICE.md — entrada datada 2026-07-26.",
    "integrity_checks[].gate": "REGISTRO_ORFAO",
    "integrity_checks[].result": "PASS",
    "integrity_checks[].method": "Conferência, registro a registro, de que todo índice obrigatório o cita.",
    "integrity_checks[].reproduction.kind": "command",
    "integrity_checks[].reproduction.value": "python ferramentas/checar-indice.py projeto/decisoes",
    "integrity_checks[].evidence": "Saída do script: 1 registro, 1 citação no índice.",
    "integrity_checks[].finding": "n/a",
    "integrity_checks[].correction_condition": "n/a",
    "integrity_checks[].correction_owner": "n/a",
    "integrity_checks[].verified_by": "agente-estado-e-handoffs",
    "integrity_checks[].verification_mode": "distinct_capability",
    "records_touched[].record_id": "record-001",
    "records_touched[].state_reached": "GRAVADO",
    "embedded_instruction_findings[]": "Nenhum trecho casou o vocabulário específico da ameaça.",
    "pending[]": "Índice cross-projeto sem dono resolvido — dono diretor-de-lentes.",
    "status": "COMPLETED",
    "blocked_reason": "Sem bloqueio nesta tarefa; campo preenchido apenas em BLOCKED.",
    # --- REGISTRY_CAPABILITY_GAP ------------------------------------------
    "expected_contract": "Gravar a tarefa derivada na fonte de estado e devolver recibo válido.",
    "discovery_evidence": "SEM_RETORNO observado na tarefa task-agente-estado-e-handoffs.",
    "preserved_inputs[]": "Conteúdo íntegro do registro record-004, preservado sem reescrita.",
    "impact": "A tarefa derivada não pousa e a soma do ledger não fecha como se nada faltasse.",
    # --- LEARNING_REPORT ---------------------------------------------------
    "report_id": "learning-report-001",
    "department_mission_ref": "department-mission-10",
    "window.from": TS,
    "window.to": TS_LATER,
    "saturation_declared": True,
    "licoes[].licao_id": "licao-001",
    "licoes[].projeto": "Estrutura Final de Skills",
    "licoes[].categoria_falha": "gate-tautologico",
    "licoes[].ocorrido_em": TS,
    "licoes[].o_que_e": "Validador que confere presença de string não prova comportamento.",
    "licoes[].evidence_excerpt": "trecho literal com credencial substituída por [REDIGIDO: token]",
    "licoes[].fonte_ref": "references/protocolo-registros.md",
    "licoes[].fonte_titulo": "Protocolo único de registros",
    "licoes[].fonte_versao": "2026-07-26",
    "licoes[].fonte_digest": MATERIAL_DIGEST,
    "licoes[].acessado_em": TS_LATER,
    "licoes[].limite_declarado": "A fonte não cobre runtime sem API de caminho canônico.",
    "licoes[].alvos_afetados[]": "departamento-registros",
    "licoes[].sinais.acionou": True,
    "licoes[].sinais.aderiu": True,
    "licoes[].sinais.contorno": "n/a",
    "gaps_de_colheita[]": "Sessões sem transcript preservado não puderam ser colhidas.",
    "artifact_ref": "registros/relatorios/aprendizagem/2026-07-26-licoes.md",
    "recorded_at": TS_LATER,
}
# a capacidade do bloco de lacuna colide de nome com a da tarefa: desambigua por
# valor concreto próprio, aplicado só naquele envelope.
GAP_CONCRETE = {
    "capability": "Gravação de estado sem executor nesta rodada.",
    "worker_id": "agente-estado-e-handoffs",
    "record_ids[]": "record-004",
}


def concretize(node: Any, path: str, table: dict[str, Any], missing: list[str]) -> Any:
    """Substitui **só** os marcadores do exemplo; literal do documento é preservado.

    O que o protocolo escreve como valor fixo — `artifact_type`, `producer`,
    `return_to`, `status: "OPEN"` — chega ao schema exatamente como está escrito.
    É o que faz este bloco detectar divergência entre a redação e o schema, em vez
    de mascará-la com um valor conveniente do validador.
    """
    if isinstance(node, dict):
        return {
            key: concretize(value, f"{path}.{key}" if path else key, table, missing)
            for key, value in node.items()
        }
    if isinstance(node, list):
        return [concretize(item, f"{path}[]", table, missing) for item in node]
    text = str(node)
    if "<" in text or "|" in text:
        if path in table:
            return table[path]
        missing.append(path)
        return text
    if text in {"true", "false"}:
        return text == "true"
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def concrete_example(name: str, body: Any) -> tuple[Any, list[str]]:
    table = dict(CONCRETE)
    if name == "REGISTRY_CAPABILITY_GAP":
        table.update(GAP_CONCRETE)
    missing: list[str] = []
    return concretize(body, "", table, missing), missing


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
        PLACAR_PATH,
        PROTOCOL_PATH,
        NATURES_PATH,
        ADR_PATH,
        ORIGIN_PATH,
    ]
    errors.extend(validate_required_files(required_local, "arquivo local"))

    required_external = [
        DIRECTOR_SCHEMA_PATH,
        CEO_SCHEMA_PATH,
        RULES_PATH,
        EVOLUTION_REFERENCE,
        DIRECTOR_ROOT / "SKILL.md",
        DIRECTOR_ROOT / "departamento-juizes" / "SKILL.md",
        STRUCTURE_ROOT / "ORGANOGRAMA.md",
        STRUCTURE_ROOT / "GUIA-DE-EXPANSAO-E-MIGRACAO.md",
        STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
        STRUCTURE_ROOT / "_compartilhado" / "verificacoes_pacote.py",
    ]
    errors.extend(validate_required_files(required_external, "vínculo externo"))

    if PACKAGE_ROOT.parent.name != "departamentos-operacionais":
        errors.append(
            "o Departamento deve viver sob departamentos-operacionais/, "
            f"está sob {PACKAGE_ROOT.parent.name}/"
        )
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
    errors = validate_frontmatter(SKILL_PATH, DEPARTMENT)
    errors.extend(
        validate_openai_yaml(OPENAI_PATH, "Departamento de Registros", f"${DEPARTMENT}")
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
        errors.append("SKILL.md do Departamento sem a fonte normativa única")
    if RULES_LINK_DEPARTMENT not in contract:
        errors.append("contrato do Departamento sem a fonte normativa única")
    if RULES_LINK_AGENT in skill:
        errors.append("SKILL.md do Departamento com o caminho relativo do nível do agente")
    required_tokens = [
        "diretor-de-lentes",
        "departamento-juizes",
        "departamento-evolucao-skills",
        "RECORD_TASK",
        "DEPARTMENT_RETURN",
        "BLOCKED_BYPASS_ATTEMPT",
        "HANDOFF_DECLARADO",
        "PENDING_DESTINO",
        "R6",
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
        if "RECORD_TASK" not in agent_skill:
            errors.append(f"{name}: SKILL.md sem o envelope que o autoriza a operar")
        if DEPARTMENT not in agent_skill:
            errors.append(f"{name}: SKILL.md sem o superior declarado")
        if f'capability: "{AGENT_CAPABILITY[name]}"' not in agent_skill:
            errors.append(f"{name}: SKILL.md sem a capacidade travada")
    return errors


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    defs = schema.get("$defs", {})
    expected = {
        "routingDecision",
        "recordTask",
        "recordReceipt",
        "conservationLedger",
        "registryCapabilityGap",
        "learningReport",
        "registryLedger",
    }
    missing = expected.difference(defs)
    if missing:
        errors.append(f"schema sem defs: {sorted(missing)}")

    worker_enum = defs.get("workerId", {}).get("enum", [])
    real_agents = sorted(item.name for item in AGENTS_ROOT.iterdir() if item.is_dir())
    if sorted(worker_enum) != real_agents:
        errors.append(f"workerId do schema divergente das pastas de agentes/: {worker_enum}")
    capability_enum = defs.get("capability", {}).get("enum", [])
    if sorted(capability_enum) != sorted(AGENT_CAPABILITY[name] for name in real_agents):
        errors.append(f"capability do schema divergente das capacidades reais: {capability_enum}")
    if defs.get("nature", {}).get("enum", []) != NATURES:
        errors.append("as naturezas do schema divergem da referência de domínio")
    if defs.get("integrityGate", {}).get("enum", []) != INTEGRITY_GATES:
        errors.append("os catorze gates do schema divergem do protocolo")
    state_enum = defs.get("recordState", {}).get("enum", [])
    if sorted(state_enum) != sorted(STATE_COUNTER):
        errors.append("o ciclo de vida do schema divergiu do mapa de estado para contador")
    if "existence" in defs.get("writeTarget", {}).get("properties", {}):
        errors.append("writeTarget não pode ter existence: o campo é de destination (§1.1)")
    if "existence" not in defs.get("destination", {}).get("properties", {}):
        errors.append("destination sem existence: a prova de destino some do roteamento")

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
    if not DIRECTOR_SCHEMA_PATH.is_file():
        return ["schema de fronteira ausente"]
    director = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8")).get("$defs", {})

    operational = director.get("operationalDepartment", {}).get("enum", [])
    if DEPARTMENT not in operational:
        errors.append("o Diretor não reconhece este Departamento como operacional")
    if DEPARTMENT not in director.get("knownCapability", {}).get("enum", []):
        errors.append("o Diretor não reconhece este Departamento como produtor conhecido")

    checks = [
        ("departmentMission", "return_to", "diretor-de-lentes",
         "a missão departamental deve retornar ao Diretor"),
        ("departmentMission", "producer", "diretor-de-lentes",
         "a missão departamental deve ser emitida pelo Diretor"),
        ("departmentReturn", "returned_to", "diretor-de-lentes",
         "o retorno departamental deve ir ao Diretor"),
        ("departmentReturn", "returned_by", DEPARTMENT,
         "o Diretor deixou de reservar o retorno a este Departamento"),
        ("departmentReturn", "producer", DEPARTMENT,
         "o Diretor deixou de travar o produtor deste Departamento"),
        ("departmentJudgeReport", "producer", "departamento-juizes",
         "a nota continua sendo dos Juízes, não dos Registros"),
    ]
    for name, prop, expected, message in checks:
        if name not in director:
            errors.append(f"schema de fronteira sem $defs/{name}")
        elif not find_const(director[name], prop, expected):
            errors.append(message)

    header = director.get("causalHeader", {})
    if "candidate_digest" not in header.get("required", []):
        errors.append("o causalHeader do Diretor deixou de exigir candidate_digest")
    if "source_digest" in header.get("properties", {}):
        errors.append("o causalHeader do Diretor passou a aceitar source_digest")
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
    forbidden = [DEPARTMENT, *AGENT_NAMES]
    for case in cases:
        prompt = case["prompt"]
        for name in forbidden:
            if name in prompt:
                errors.append(f"evals: {case['id']} nomeia {name} no prompt")
        if len(case.get("assertions", [])) < 3:
            errors.append(f"evals: {case['id']} com menos de 3 assertions")
        if not case.get("origem"):
            errors.append(f"evals: {case['id']} sem origem declarada")
    return errors


def _evals_sem(campo: str, dentro: str | None = None) -> dict[str, Any]:
    """Copia do `evals.json` real com um campo removido de `aderiu`.

    Serve as contraprovas de `validate_criterios_de_leitura`: a bateria so prova
    que a trava obriga se existir o caso que fica VERMELHO quando o campo sai.
    Copia profunda de proposito -- mutar o dicionario carregado contaminaria os
    outros casos da mesma corrida.
    """
    evals = copy.deepcopy(json.loads(EVALS_PATH.read_text(encoding="utf-8")))
    aderiu = evals.get("criterios_de_leitura", {}).get("aderiu", {})
    if not isinstance(aderiu, dict):
        return evals
    if dentro is None:
        aderiu.pop(campo, None)
        return evals
    # Sensível a tipo de propósito: se `dentro` não for dicionário, devolver o
    # objeto intacto deixa a trava acusar a malformação e produzir um FAIL
    # contável. Assumir dicionário aqui derrubava a bateria inteira com
    # AttributeError — e validador que estoura não reprova, some da contagem.
    alvo = aderiu.get(dentro)
    if isinstance(alvo, dict):
        alvo.pop(campo, None)
    return evals

def validate_criterios_de_leitura(evals: dict[str, Any] | None = None) -> list[str]:
    """A régua de leitura de `aderiu` e `acionou` mora no catálogo, não no relatório.

    POR QUE ESTA TRAVA EXISTE. O critério de leitura foi declarado no
    `FORWARD-TEST.md` de quem mediu, e não aqui — apontado na rodada 1 e de novo
    na rodada 2, sem fecho nas duas. Enquanto a régua viaja no bolso do executor,
    dois medidores produzem placares diferentes sobre as MESMAS respostas, e a
    comparação entre rodadas deixa de significar alguma coisa.

    E declarar sem travar não resolve: medido em 2026-08-28, remover o bloco
    inteiro do `evals.json` deixava esta bateria verde em 184/184. Aviso em prosa
    não previne erro — o que obriga é o caso vermelho.
    """
    if evals is None:
        evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    criterios = evals.get("criterios_de_leitura")
    if not isinstance(criterios, dict):
        errors.append(
            "evals: falta o bloco `criterios_de_leitura` — a régua de `aderiu` e "
            "`acionou` não pode viver só no relatório de quem mede"
        )
        return errors
    exigidos = {
        "aderiu": ("regra", "conjuncao", "parcial"),
        "acionou": ("regra", "superficie_varrida", "leitura_no_contexto"),
    }
    # Blocos exigidos que sao DICIONARIO, e nao texto. O laco de baixo cobra
    # `isinstance(valor, str)`; promover um dicionario a ele acusaria "ausente ou
    # vazio" sobre um campo presente e correto. Por isso o ramo separado.
    #
    # `poder_de_discriminacao` entra por exigencia dos Juizes -- required_changes[13]
    # do DJR-T71-C13-R3-2026-08-29, sob CRIT-R3-INSTRUMENTO. Declarar sem travar era
    # o defeito que esta mesma docstring ja registrava: exigir aqui e o que faz
    # apagar o bloco ficar VERMELHO em vez de passar despercebido.
    exigidos_dicionario = {
        "aderiu": {
            "poder_de_discriminacao": (
                "particao_que_o_agregado_induz",
                "o_que_ele_nao_separa",
                "quanto_ele_esconde_na_R3",
                "o_que_ele_confunde_com_falha",
                "leitura_obrigatoria",
                "quando_ele_volta_a_discriminar",
            ),
        },
    }
    for chave, campos in exigidos.items():
        bloco = criterios.get(chave)
        if not isinstance(bloco, dict):
            errors.append(f"evals: `criterios_de_leitura` sem `{chave}`")
            continue
        for campo in campos:
            valor = bloco.get(campo)
            if not isinstance(valor, str) or not valor.strip():
                errors.append(
                    f"evals: `criterios_de_leitura.{chave}.{campo}` ausente ou vazio"
                )
    for chave, blocos in exigidos_dicionario.items():
        pai = criterios.get(chave)
        if not isinstance(pai, dict):
            continue
        for nome, campos in blocos.items():
            sub = pai.get(nome)
            if not isinstance(sub, dict):
                errors.append(
                    f"evals: `criterios_de_leitura.{chave}.{nome}` ausente — o "
                    "agregado precisa declarar o proprio poder de discriminacao, "
                    "senao o numero de manchete viaja sem a leitura que o sustenta"
                )
                continue
            for campo in campos:
                valor = sub.get(campo)
                if not isinstance(valor, str) or not valor.strip():
                    errors.append(
                        f"evals: `criterios_de_leitura.{chave}.{nome}.{campo}` "
                        "ausente ou vazio"
                    )
    return errors


def validate_learning_return_alignment(schema: dict[str, Any]) -> list[str]:
    """B1 — o §1.5 do protocolo e o schema dizem o mesmo `return_to`."""
    errors: list[str] = []
    const = (
        schema["$defs"]["learningReport"]["properties"]["return_to"].get("const")
    )
    examples = protocol_examples()
    if "LEARNING_REPORT" not in examples:
        return ["protocolo sem o exemplo normativo do LEARNING_REPORT"]
    declared = examples["LEARNING_REPORT"].get("return_to")
    if declared != const:
        errors.append(
            f"§1.5 declara return_to {declared!r} e o schema trava {const!r}"
        )
    if const != "diretor-de-lentes":
        errors.append(
            "ADR-005: o LEARNING_REPORT é artefato de Departamento e volta ao Diretor"
        )
    receipt = examples.get("RECORD_RECEIPT", {}).get("return_to")
    if receipt != DEPARTMENT:
        errors.append(f"§1.2 declara return_to {receipt!r}, e o recibo volta à gerente")
    return errors


def validate_existence_field_prose() -> list[str]:
    """B3 — a prosa da §1.1 não pode pendurar `existence` no `write_target`."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    errors: list[str] = []
    if re.search(r"write_target\.existence|`existence` (?:é|e) campo de `write_target`", text):
        errors.append("§1.1 atribui existence ao write_target, que não tem esse campo")
    if "`existence` é campo de `destination`" not in text:
        errors.append("§1.1 não diz de quem é o campo existence")
    return errors


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

def run() -> int:  # noqa: C901 - catálogo linear de casos
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    director_schema = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))
    mission_def = director_schema["$defs"]["departmentMission"]
    return_def = director_schema["$defs"]["departmentReturn"]

    cases: list[tuple[str, bool, list[str]]] = []

    def case(name: str, expected_valid: bool, errors: list[str]) -> None:
        cases.append((name, expected_valid, errors))

    def accepts(name: str, fixture: Any) -> None:
        case(f"schema aceita {name}", True, validate_schema(fixture, schema, schema))

    def rejects(name: str, fixture: Any) -> None:
        case(f"schema rejeita {name}", False, validate_schema(fixture, schema, schema))

    def condition(name: str, passed: bool) -> None:
        case(name, True, [] if passed else ["condição comportamental falhou"])

    # --- pacote --------------------------------------------------------------
    case("pacote, agentes e vínculos externos", True, validate_structure())
    case("metadata da gerente e dos quatro agentes", True, validate_metadata())
    case("fonte normativa única e tokens de contrato", True, validate_normative_source())
    case("links internos do pacote resolvem", True, validate_links(PACKAGE_ROOT))
    case("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT))
    case("todo pacote gerente tem validador que roda a trava global", True, validate_cobertura_de_validadores(STRUCTURE_ROOT))
    case("contratos de gerente na anatomia canônica", True, validate_contratos_de_gerente(STRUCTURE_ROOT))
    case("anatomia de contrato acusa raiz inexistente", False, validate_contratos_de_gerente(STRUCTURE_ROOT / "pacote-inexistente-t97"))
    case("a recusa de digest() dispara e ninguém tem cópia privada do motor", True, validate_trava_de_digest(STRUCTURE_ROOT))
    case("nenhuma asserção é verdadeira por construção sobre valor produzido", True, validate_sem_check_tautologico(STRUCTURE_ROOT))
    cases.append(("nenhum placar de pacote declara total de cadeia como estado corrente", True, validate_placar_nao_declara_cadeia(STRUCTURE_ROOT)))
    cases.append(("a contagem publicada aponta para o digest do instrumento vigente", True, validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)))
    cases.append(("as travas do modulo compartilhado nao estao neutralizadas", True, validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT)))
    cases.append(("toda pendencia declarada nomeia quem responde por ela", True, validate_pendencia_tem_dono(STRUCTURE_ROOT)))
    # Par NEGATIVO da trava do selo (T71), pelo mesmo motivo escrito abaixo: sem
    # raiz para varrer, a trava tem de FALHAR FECHADO. Trava que devolve vazio
    # quando não consegue olhar nada é verde por ausência, não por conformidade.
    cases.append((
        "trava do selo falha fechado quando a raiz não existe",
        False,
        validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT / "raiz-inexistente"),
    ))
    # Par NEGATIVO da trava da T84, no mesmo molde do caso da cadeia logo abaixo:
    # planta a forma proibida — trava desligada por `return` precoce, com o corpo
    # inteiro virando código morto — e exige que ela seja ACUSADA.
    cases.append((
        "trava desligada por return precoce é acusada",
        False,
        achar_corpo_neutralizado(
            "def validate_de_mentira(raiz):\n"
            "    return []\n"
            "    if not raiz.is_dir():\n"
            "        return ['raiz ausente']\n",
            "fixture",
        ),
    ))
    # Par NEGATIVO da trava do dono (T71): planta a forma proibida — item de
    # pendência sem linha na tabela de donos — e exige que ela seja ACUSADA.
    cases.append((
        "pendência sem dono é acusada",
        False,
        achar_pendencia_sem_dono(
            "# P\n\n## O que ainda não foi provado\n\n"
            "1. **Um.** texto\n2. **Dois.** texto\n",
            "fixture",
        ),
    ))
    # Caso NEGATIVO pareado: o passo 9 exige negativos >= positivos, e o
    # caso acima é positivo. Este exercita a MESMA trava pelo lado que
    # precisa reprovar — sem par, acrescentar trava desequilibra a suíte.
    cases.append((
        "alegação de total de cadeia no presente é rejeitada",
        False,
        achar_cadeia_no_presente(
            "A cadeia canônica hoje soma **1531/1531 PASS**.", "fixture"
        ),
    ))
    case("a fonte normativa confere com o valor declarado em ORIGEM.md", True, validate_fonte_normativa_conferida(STRUCTURE_ROOT))
    case("schema interno, enums e referências locais", True, validate_schema_shape(schema))
    case("autoridades herdadas do schema do Diretor", True, validate_inherited_authority())
    case("catálogo de evals", True, validate_evals())
    case("a régua de leitura de `aderiu` e `acionou` mora no catálogo", True,
         validate_criterios_de_leitura())
    case("catálogo sem régua de leitura é recusado", False,
         validate_criterios_de_leitura({"cases": []}))
    case("`aderiu` declara o próprio poder de discriminação", True,
         validate_criterios_de_leitura())
    case("`aderiu` sem poder de discriminação é recusado", False,
         validate_criterios_de_leitura(_evals_sem("poder_de_discriminacao")))
    case("poder de discriminação sem o que ele não separa é recusado", False,
         validate_criterios_de_leitura(
             _evals_sem("o_que_ele_nao_separa", dentro="poder_de_discriminacao")))
    case("B1: §1.5 e schema alinhados no return_to", True,
         validate_learning_return_alignment(schema))
    case("B3: existence é campo de destination, não de write_target", True,
         validate_existence_field_prose())

    # --- exemplos normativos do protocolo (B2) ------------------------------
    examples = protocol_examples()
    expected_examples = {
        "RECORD_TASK",
        "RECORD_RECEIPT",
        "REGISTRY_CAPABILITY_GAP",
        "LEARNING_REPORT",
    }
    case(
        "os quatro exemplos normativos foram extraídos do protocolo",
        True,
        [] if expected_examples.issubset(examples) else
        [f"exemplo ausente: {sorted(expected_examples.difference(examples))}"],
    )
    concrete_examples: dict[str, Any] = {}
    for name in sorted(expected_examples.intersection(examples)):
        concrete, missing = concrete_example(name, examples[name])
        concrete_examples[name] = concrete
        errors = [f"placeholder sem valor concreto: {item}" for item in missing]
        errors.extend(validate_schema(concrete, schema, schema))
        case(f"exemplo normativo {name} valida contra o schema", True, errors)

    header_fields = set(schema["$defs"]["causalHeader"]["required"])
    condition(
        "o exemplo da §1.1 carrega o cabeçalho causal completo, com o quarteto dentro",
        isinstance(examples.get("RECORD_TASK", {}).get("causal"), dict)
        and set(examples["RECORD_TASK"]["causal"]) == header_fields,
    )
    if "RECORD_TASK" in concrete_examples:
        legacy = copy.deepcopy(concrete_examples["RECORD_TASK"])
        legacy.pop("artifact_type")
        header = legacy.pop("causal")
        for field in ("contract_id", "contract_version", "contract_digest", "source_digest"):
            legacy[field] = header[field]
        rejects(
            "o formato anterior da §1.1: quarteto no topo, sem artifact_type nem causal (B2)",
            legacy,
        )
    if "LEARNING_REPORT" in concrete_examples:
        rerouted = copy.deepcopy(concrete_examples["LEARNING_REPORT"])
        rerouted["return_to"] = DEPARTMENT
        rejects(
            "o exemplo da §1.5 devolvendo o relatório à própria gerente (B1)", rerouted
        )
    if "RECORD_RECEIPT" in concrete_examples:
        unverified_mode = copy.deepcopy(concrete_examples["RECORD_RECEIPT"])
        for check in unverified_mode["integrity_checks"]:
            check.pop("verification_mode")
        rejects(
            "o exemplo da §1.2 sem o modo de verificação nos gates (B2)", unverified_mode
        )

    # --- ROUTING_DECISION: positivos ----------------------------------------
    accepts("ROUTING_DECISION pousada (R3, decisao-adr)", landed_decision())
    accepts("ROUTING_DECISION de memória como handoff (R5)", handoff_decision())
    accepts("ROUTING_DECISION de recusa de fronteira (R1)", refusal_decision())
    accepts("ROUTING_DECISION sem regra casada (PENDING_DESTINO)", pending_decision())
    accepts("ROUTING_DECISION de fatia não atômica (split_required)", split_decision())

    # --- ROUTING_DECISION: negativos ----------------------------------------
    wrong_nature = routing_decision(rule="R3", nature="estado")
    rejects("natureza que não casa a regra decisora", wrong_nature)

    memory_written = routing_decision(record_id="record-002", rule="R5", state="GRAVADO")
    rejects("memória durável em estado gravado", memory_written)

    memory_writable = routing_decision(
        record_id="record-002",
        rule="R5",
        state="HANDOFF_DECLARADO",
        artifact_ref="n/a",
        dest=destination(write_scope="departamento"),
    )
    rejects("memória durável com escopo de escrita do Departamento", memory_writable)

    atomic_without_rule = routing_decision(rule="n/a", nature="estado", matched=[])
    rejects("registro atômico sem regra decisora", atomic_without_rule)

    tie_without_reason = routing_decision(matched=["R3", "R5"], tiebreak="n/a")
    rejects("empate de duas regras sem desempate nomeado", tie_without_reason)

    split_with_destination = split_decision()
    split_with_destination["destination"] = destination()
    rejects("fatia não atômica com destino decidido", split_with_destination)

    unmatched_landed = pending_decision()
    unmatched_landed["state"] = "VERIFICADO"
    rejects("registro sem regra casada declarado verificado", unmatched_landed)

    unverified_landed = routing_decision(dest=destination(existence="unverified"))
    rejects("estado pousado com existência do destino não verificada", unverified_landed)

    unknown_root = routing_decision(dest=destination(within="unknown"))
    rejects("estado pousado com confinamento desconhecido", unknown_root)

    few_gates = routing_decision(gates=["GATE_DECOMPOSICAO", "GATE_DESTINO_UNICO",
                                        "GATE_CUSTODIA", "GATE_FONTE_UNICA"])
    rejects("estado pousado com menos de cinco gates de transição", few_gates)

    landed_without_artifact = routing_decision(artifact_ref="n/a")
    rejects("estado pousado sem artefato real", landed_without_artifact)

    embedded_convention = routing_decision(channel_level=4)
    embedded_convention["convention_ref"] = convention_ref(4)
    rejects("convenção decidida por fonte de canal 3–4", embedded_convention)

    blocked_mute = routing_decision(
        record_id="record-008", state="BLOQUEADO", artifact_ref="n/a", blocked_reason="n/a"
    )
    rejects("registro bloqueado sem motivo declarado", blocked_mute)

    derived_without_source = routing_decision(
        dest=destination(derived_role="view_regeneravel")
    )
    derived_without_source["destination"]["source_of_truth_ref"] = "n/a"
    rejects("artefato derivado sem fonte resolvida", derived_without_source)

    # --- RECORD_TASK: positivos ---------------------------------------------
    accepts("RECORD_TASK de gravação", record_task())
    accepts("RECORD_TASK de indexação", record_task(kind="INDEXAR"))
    accepts(
        "RECORD_TASK de verificação por capacidade distinta",
        record_task(worker="agente-estado-e-handoffs", kind="VERIFICAR"),
    )
    accepts(
        "RECORD_TASK de recontagem",
        record_task(worker="agente-documentacao-e-materiais", kind="RECONTAR"),
    )
    accepts(
        "RECORD_TASK de colheita de aprendizagem",
        record_task(worker="agente-aprendizados-e-relatorios", kind="COLHER"),
    )

    # --- RECORD_TASK: negativos ---------------------------------------------
    rejects(
        "tarefa com capacidade trocada para o agente",
        record_task(capability="estado-e-handoffs"),
    )
    rejects("tarefa de gravação sem alvo de escrita", record_task(target="n/a"))
    rejects(
        "tarefa de gravação com varredura de entrada não verificada",
        record_task(scan=pre_write_scan("NAO_VERIFICADO")),
    )
    rejects(
        "tarefa de gravação com varredura em FAIL",
        record_task(scan=pre_write_scan("FAIL")),
    )
    rejects(
        "tarefa de verificação com alvo de escrita",
        record_task(worker="agente-estado-e-handoffs", kind="VERIFICAR",
                    target=write_target()),
    )
    rejects(
        "tarefa de verificação com índice a tocar",
        record_task(worker="agente-estado-e-handoffs", kind="VERIFICAR",
                    index_targets=["projeto/decisoes/INDICE.md"]),
    )
    rejects(
        "colheita atribuída a capacidade que não é a de aprendizados",
        record_task(worker="agente-memoria-e-decisoes", kind="COLHER"),
    )
    rejects("tarefa com retorno fora da gerente", record_task(return_to="diretor-de-lentes"))
    rejects("tarefa com produtor forjado", record_task(producer="diretor-de-lentes"))
    rejects(
        "tarefa sem as quatro proibições de contexto",
        record_task(forbidden=["recibos dos outros agentes", "conclusão esperada"]),
    )
    rejects(
        "tarefa sem proibir o vazamento de recibos irmãos",
        record_task(
            forbidden=[
                "decisão de destino ainda não tomada pela gerente",
                "conclusão esperada ou estado desejado",
                "instrução embutida no material lido",
                "rodada anterior e histórico de retrabalho",
            ]
        ),
    )
    rejects(
        "tarefa com alvo fora da raiz confiável",
        record_task(target=write_target(within_trusted_root=False)),
    )
    rejects(
        "tarefa que adia a varredura sobre insumo já em mãos",
        record_task(scan=pre_write_scan("deferred_to_author", "conteudo_final")),
    )
    forged_existence = record_task(
        target=write_target(existence="unverified")
    )
    rejects("tarefa com existence pendurada no write_target (B3)", forged_existence)

    # --- RECORD_RECEIPT: positivos ------------------------------------------
    accepts("RECORD_RECEIPT concluído", record_receipt())
    accepts("RECORD_RECEIPT bloqueado com motivo", record_receipt(status="BLOCKED"))
    accepts(
        "RECORD_RECEIPT de verificação, sem escrita",
        record_receipt(
            worker="agente-estado-e-handoffs",
            writes=[],
            touched=[{"record_id": "record-001", "state_reached": "VERIFICADO"}],
            scan_result="NAO_APLICAVEL",
        ),
    )

    # --- RECORD_RECEIPT: negativos ------------------------------------------
    empty_completed = record_receipt(touched=[])
    rejects("recibo concluído sem registro tocado", empty_completed)

    mute_blocked = record_receipt(status="BLOCKED")
    mute_blocked.pop("blocked_reason")
    rejects("recibo bloqueado sem motivo", mute_blocked)

    blocked_with_write = record_receipt(status="BLOCKED")
    blocked_with_write["writes_performed"] = [write_performed()]
    rejects("recibo bloqueado com escrita realizada", blocked_with_write)

    rejects(
        "recibo concluído com varredura de autoria em FAIL",
        record_receipt(scan_result="FAIL"),
    )
    rejects(
        "escrita com varredura de autoria não verificada",
        record_receipt(scan_result="NAO_VERIFICADO"),
    )

    tautological = record_receipt(
        checks=[integrity_check(reproduction_kind="none")]
    )
    rejects("gate PASS sem reprodução executável", tautological)

    thin_evidence = record_receipt(checks=[integrity_check()])
    thin_evidence["integrity_checks"][0]["evidence"] = "ok"
    rejects("gate PASS com evidência que não sustenta", thin_evidence)

    fail_without_owner = record_receipt(checks=[integrity_check(result="FAIL")])
    fail_without_owner["integrity_checks"][0]["correction_owner"] = "n/a"
    rejects("gate FAIL sem dono da correção", fail_without_owner)

    sealed_without_command = record_receipt(
        checks=[
            integrity_check(
                mode="sealed_independent_method",
                reproduction_kind="artifact_locator",
                verified_by="agente-memoria-e-decisoes",
            )
        ]
    )
    rejects("independência mecânica sem comando reexecutável", sealed_without_command)

    sealed_on_judgment = record_receipt(
        checks=[
            integrity_check(
                gate="MEMORIA_CONTAMINADA",
                mode="sealed_independent_method",
                verified_by="agente-memoria-e-decisoes",
            )
        ]
    )
    rejects("independência mecânica em gate de juízo", sealed_on_judgment)

    lazy_na = record_receipt(
        checks=[integrity_check(result="NAO_APLICAVEL", method="nao se aplica")]
    )
    rejects("gate NAO_APLICAVEL sem justificativa concreta", lazy_na)

    created_with_baseline = record_receipt(
        writes=[write_performed(baseline_sha256=HEX_BASELINE)]
    )
    rejects("arquivo criado com baseline anterior", created_with_baseline)

    generated_edited = record_receipt(
        writes=[write_performed(derived_role="runtime_gerado", action="updated")]
    )
    rejects("escrita à mão em artefato gerado pelo runtime", generated_edited)

    check_without_mode = record_receipt(checks=[integrity_check()])
    check_without_mode["integrity_checks"][0].pop("verification_mode")
    rejects("gate sem modo de verificação declarado", check_without_mode)

    rejects("recibo devolvido fora da gerente", record_receipt(return_to="diretor-de-lentes"))

    # --- REGISTRY_CAPABILITY_GAP --------------------------------------------
    accepts("REGISTRY_CAPABILITY_GAP aberta", capability_gap())
    rejects("lacuna fechada pela própria gerente", capability_gap(status="MITIGATED"))
    rejects("lacuna com dono fora do Diretor", capability_gap(owner=DEPARTMENT))
    gap_without_inputs = capability_gap()
    gap_without_inputs["preserved_inputs"] = []
    rejects("lacuna sem o conteúdo do registro preservado", gap_without_inputs)

    # --- CONSERVATION_LEDGER -------------------------------------------------
    closed_ledger = conservation_ledger()
    accepts("CONSERVATION_LEDGER fechado com recontagem independente", closed_ledger)

    single_count = conservation_ledger(
        recount=recount_block(proof="not_verifiable", artifact_ref="n/a")
    )
    accepts("CONSERVATION_LEDGER com contagem única declarada", single_count)

    forged_closed = conservation_ledger(
        recount=recount_block(proof="not_verifiable", artifact_ref="n/a"),
        status="closed",
    )
    rejects("ledger fechado sem segunda contagem", forged_closed)

    unaccounted_closed = conservation_ledger(
        unaccounted=["fatia 4 sem RECORD_ID"], status="closed"
    )
    rejects("ledger fechado com fatia não contabilizada", unaccounted_closed)

    delta_closed = conservation_ledger(
        recount=recount_block(delta_final=1), status="closed"
    )
    rejects("ledger fechado com divergência de contagem em aberto", delta_closed)

    invariant_false = conservation_ledger(status="closed", invariant_two=False)
    rejects("ledger fechado com invariante declarado falso", invariant_false)

    empty_closed = conservation_ledger(entries=[], states=[], identified=0, routed=0,
                                       status="closed")
    rejects("ledger fechado sem nenhum registro roteado", empty_closed)

    sealed_without_artifact = conservation_ledger(
        recount=recount_block(proof="sealed_prior_count", artifact_ref="n/a",
                              recorded_at=TS, started_at=TS_LATER)
    )
    rejects("contagem selada sem artefato datado", sealed_without_artifact)

    # --- LEARNING_REPORT -----------------------------------------------------
    accepts("LEARNING_REPORT com lição e fonte que resolve", learning_report())
    accepts(
        "LEARNING_REPORT vazio com lacuna de colheita declarada",
        learning_report(lessons=[], gaps=["Sessões sem transcript preservado."]),
    )
    rejects(
        "relatório de aprendizagem devolvido à própria gerente",
        learning_report(return_to=DEPARTMENT),
    )
    rejects(
        "relatório entregue por canal paralelo ao consumidor",
        learning_report(requested_via="departamento-evolucao-skills"),
    )
    rejects(
        "relatório produzido para quem não o encomendou",
        learning_report(produced_for="diretor-de-lentes"),
    )
    gem_filled = learning_report(
        lessons=[learning_lesson(gap_alvo="fronteira do roteamento", degrau_proposto=3)]
    )
    rejects("lição com campos do gem do consumidor preenchidos", gem_filled)

    memory_lesson = learning_report(lessons=[learning_lesson()])
    memory_lesson["licoes"][0].pop("fonte_ref")
    rejects("lição afirmada de memória, sem fonte", memory_lesson)

    rejects(
        "relatório vazio sem lacuna de colheita",
        learning_report(lessons=[], gaps=[]),
    )
    rejects(
        "varredura sem saturação declarada e sem lacuna",
        learning_report(saturation=False, gaps=[]),
    )
    rejects("relatório com produtor forjado", learning_report(producer="ceo-maestro"))

    # --- REGISTRY_LEDGER -----------------------------------------------------
    completed = registry_ledger()
    accepts("REGISTRY_LEDGER concluído", completed)
    accepts(
        "REGISTRY_LEDGER parcial com gate em FAIL",
        registry_ledger(
            status="PARTIAL",
            gates={"REGISTRO_ORFAO": "FAIL"},
            partial_reasons=["integrity_fail"],
        ),
    )
    accepts(
        "REGISTRY_LEDGER parcial com lacuna aberta",
        registry_ledger(
            status="PARTIAL",
            gaps=[capability_gap()],
            partial_reasons=["capability_missing"],
        ),
    )
    accepts(
        "REGISTRY_LEDGER com relatório de aprendizagem referenciado",
        registry_ledger(
            learning_ref="registros/relatorios/aprendizagem/2026-07-26-licoes.md",
            assignments=[
                assignment("agente-memoria-e-decisoes"),
                assignment("agente-aprendizados-e-relatorios", "COLHER"),
            ],
        ),
    )

    rejects(
        "rodada concluída com gate em FAIL",
        registry_ledger(gates={"REGISTRO_ORFAO": "FAIL"}),
    )
    rejects(
        "rodada concluída com gate não verificado",
        registry_ledger(gates={"INDICE_ADIANTADO": "NAO_VERIFICADO"}),
    )
    rejects(
        "rodada concluída sobre contagem única",
        registry_ledger(
            conservation=conservation_ledger(
                recount=recount_block(proof="not_verifiable", artifact_ref="n/a")
            )
        ),
    )
    rejects(
        "rodada concluída com lacuna aberta",
        registry_ledger(gaps=[capability_gap()]),
    )
    rejects(
        "lacuna aberta sem o motivo parcial correspondente",
        registry_ledger(status="PARTIAL", gaps=[capability_gap()],
                        partial_reasons=["integrity_fail"]),
    )
    rejects(
        "rodada concluída sem registro de emissão de tarefa (R6)",
        registry_ledger(assignments=[]),
    )
    rejects(
        "rodada concluída com item de dossiê nomeado como faltante",
        registry_ledger(dossier_missing=["perfil de destinos do alvo"]),
    )
    rejects(
        "retorno sem R6 nomeado em pending",
        registry_ledger(pending=["Índice cross-projeto sem dono resolvido."]),
    )
    rejects("rodada devolvida fora do Diretor", registry_ledger(return_to="ceo-maestro"))
    rejects(
        "rodada parcial sem motivo declarado",
        registry_ledger(status="PARTIAL", partial_reasons=[]),
    )
    short_report = registry_ledger(report=integrity_report()[:13])
    rejects("relatório de integridade com treze gates", short_report)

    duplicated_gate = registry_ledger()
    duplicated_gate["integrity_report"][13] = integrity_check("REGISTRO_ORFAO")
    duplicated_gate["integrity_report"][13]["evidence"] = "Segunda passagem do mesmo gate."
    rejects("gate repetido no lugar de outro", duplicated_gate)

    rejects(
        "degrau mínimo com sinal derrubado",
        registry_ledger(tier=mission_tier("minima", disqualified=["S4"],
                                          qualified=["S1", "S2", "S3", "S5", "S6"])),
    )
    rejects(
        "recusa de fronteira com efeito colateral divergente",
        registry_ledger(refusals=[boundary_refusal("divergent")]),
    )
    rejects(
        "relatório de aprendizagem referenciado sem tarefa de colheita",
        registry_ledger(
            learning_ref="registros/relatorios/aprendizagem/2026-07-26-licoes.md"
        ),
    )
    rejects(
        "painel com mais executores do que capacidades",
        registry_ledger(panel=[panel_item(name) for name in AGENT_NAMES]
                        + [panel_item("agente-memoria-e-decisoes", "BLOCKED")]),
    )

    # --- fronteira: o Diretor aceita o que este Departamento produz ----------
    case(
        "Diretor aceita a DEPARTMENT_MISSION do dossiê mínimo",
        True,
        validate_schema(director_mission(), mission_def, director_schema),
    )
    derived = derive_department_return(completed)
    case(
        "Diretor aceita o DEPARTMENT_RETURN derivado",
        True,
        validate_schema(derived, return_def, director_schema),
    )
    case(
        "Diretor aceita o retorno com candidato da rodada",
        True,
        validate_schema(
            derive_department_return(completed, candidate_digest=CANDIDATE_DIGEST),
            return_def,
            director_schema,
        ),
    )
    case(
        "Diretor rejeita o cabeçalho causal interno sem conversão",
        False,
        validate_schema(
            derive_department_return(completed, keep_internal_causal=True),
            return_def,
            director_schema,
        ),
    )
    spoofed = derive_department_return(completed)
    spoofed["causal"]["producer"] = "departamento-desenvolvimento"
    case(
        "Diretor rejeita retorno com produtor forjado",
        False,
        validate_schema(spoofed, return_def, director_schema),
    )
    impersonated = derive_department_return(completed)
    impersonated["returned_by"] = "departamento-qa-usabilidade"
    case(
        "Diretor rejeita retorno assinado por outro Departamento",
        False,
        validate_schema(impersonated, return_def, director_schema),
    )
    to_ceo = derive_department_return(completed)
    to_ceo["returned_to"] = "ceo-maestro"
    case(
        "Diretor rejeita retorno endereçado ao CEO",
        False,
        validate_schema(to_ceo, return_def, director_schema),
    )
    smuggled = derive_department_return(completed)
    smuggled["registry_ledger"] = completed
    case(
        "Diretor rejeita o livro-razão embutido como campo novo",
        False,
        validate_schema(smuggled, return_def, director_schema),
    )
    no_artifacts = derive_department_return(completed)
    no_artifacts["artifact_refs"] = []
    case(
        "Diretor rejeita retorno sem artefato referenciado",
        False,
        validate_schema(no_artifacts, return_def, director_schema),
    )
    without_candidate = derive_department_return(completed, candidate_digest="n/a")
    case(
        "Diretor rejeita retorno sem digest de candidato, mesmo sem candidato tocado",
        False,
        validate_schema(without_candidate, return_def, director_schema),
    )
    forged_mission = director_mission(producer="departamento-desenvolvimento")
    case(
        "Diretor rejeita missão que não veio dele",
        False,
        validate_schema(forged_mission, mission_def, director_schema),
    )

    # --- aritmética e regras, recalculadas em código -------------------------
    entries = [maker() for maker in DEFAULT_ENTRIES]
    states = [entry["state"] for entry in entries]
    counters = count_by_state(states)
    declared = {field: closed_ledger[field] for field in COUNTER_FIELDS}
    wrong_counters = dict(counters)
    wrong_counters["records_refused_boundary"] = 0

    condition(
        "o mapa de estado para contador cobre exatamente o ciclo de vida do schema",
        sorted(STATE_COUNTER) == sorted(schema["$defs"]["recordState"]["enum"]),
    )
    condition(
        "os contadores recalculados batem com os declarados no ledger",
        counters == declared,
    )
    condition(
        "os quatro desfechos da rodada particionam a soma",
        sum(counters[field] for field in COUNTER_FIELDS) == len(states),
    )
    condition(
        "o invariante identificados == roteados fecha",
        invariant_identified_equals_routed(
            closed_ledger["records_identified"], closed_ledger["records_routed"]
        ),
    )
    condition(
        "o invariante roteados == soma fecha pelos contadores, não pelo campo",
        invariant_routed_equals_sum(closed_ledger["records_routed"], counters),
    )
    condition(
        "esquecer uma parcela da soma daria outro resultado",
        not invariant_routed_equals_sum(closed_ledger["records_routed"], wrong_counters)
        and closed_ledger["invariant_routed_equals_sum"] is True,
    )
    condition(
        "estado em trânsito não alimenta contador e impede o fechamento",
        count_by_state(["GRAVADO", "INDEXADO"]) == {field: 0 for field in COUNTER_FIELDS}
        and in_transit(["GRAVADO", "VERIFICADO"]) == ["GRAVADO"],
    )
    condition(
        "ledger com registro em trânsito não fecha pela soma",
        ledger_closes(
            unaccounted=[],
            identified=2,
            routed=2,
            counters=count_by_state(["VERIFICADO", "GRAVADO"]),
            recount_proof="independent_capability",
            delta_final=0,
            entries=2,
        )
        != "closed",
    )
    condition(
        "delta final diferente de zero bloqueia a conservação",
        ledger_closes(
            unaccounted=[],
            identified=len(states),
            routed=len(states),
            counters=counters,
            recount_proof="independent_capability",
            delta_final=1,
            entries=len(states),
        )
        == "bloqueado_conservacao",
    )
    condition(
        "sem segunda contagem o honesto é contagem única, nunca fechado",
        ledger_closes(
            unaccounted=[],
            identified=len(states),
            routed=len(states),
            counters=counters,
            recount_proof="not_verifiable",
            delta_final=0,
            entries=len(states),
        )
        == "single_count_unverified",
    )
    condition(
        "fatia não contabilizada impede o fechamento",
        ledger_closes(
            unaccounted=["fatia 4"],
            identified=len(states),
            routed=len(states),
            counters=counters,
            recount_proof="independent_capability",
            delta_final=0,
            entries=len(states),
        )
        != "closed",
    )
    condition(
        "o ledger de referência fecha, e o status declarado é o derivado",
        ledger_closes(
            unaccounted=[],
            identified=len(states),
            routed=len(states),
            counters=counters,
            recount_proof=closed_ledger["recount"]["recount_proof"],
            delta_final=closed_ledger["recount"]["delta_final"],
            entries=len(closed_ledger["entries"]),
        )
        == closed_ledger["ledger_status"]
        == "closed",
    )
    condition(
        "recontagem por capacidade independente vale em qualquer degrau",
        recount_admissible(
            proof="independent_capability", tier="padrao", recorded_at=TS_LATER,
            decomposition_started_at=TS, performed_by="agente-estado-e-handoffs",
            decomposed_by=DEPARTMENT,
        ),
    )
    condition(
        "quem decompôs não pode reconter a própria decomposição",
        not recount_admissible(
            proof="independent_capability", tier="padrao", recorded_at=TS_LATER,
            decomposition_started_at=TS, performed_by=DEPARTMENT,
            decomposed_by=DEPARTMENT,
        ),
    )
    condition(
        "contagem selada só vale no degrau mínimo e antes da decomposição",
        recount_admissible(
            proof="sealed_prior_count", tier="minima", recorded_at=TS,
            decomposition_started_at=TS_LATER, performed_by=DEPARTMENT,
            decomposed_by=DEPARTMENT,
        )
        and not recount_admissible(
            proof="sealed_prior_count", tier="padrao", recorded_at=TS,
            decomposition_started_at=TS_LATER, performed_by=DEPARTMENT,
            decomposed_by=DEPARTMENT,
        )
        and not recount_admissible(
            proof="sealed_prior_count", tier="minima", recorded_at=TS_LATER,
            decomposition_started_at=TS, performed_by=DEPARTMENT,
            decomposed_by=DEPARTMENT,
        ),
    )
    condition(
        "verificador igual ao autor só passa por método mecânico selado",
        gate_independent(verified_by="a", author="a", mode="sealed_independent_method",
                         reproduction_kind="command", gate="REGISTRO_ORFAO")
        and not gate_independent(verified_by="a", author="a", mode="distinct_capability",
                                 reproduction_kind="command", gate="REGISTRO_ORFAO")
        and not gate_independent(verified_by="a", author="a",
                                 mode="sealed_independent_method",
                                 reproduction_kind="command",
                                 gate="MEMORIA_CONTAMINADA"),
    )
    all_pass = {gate: "PASS" for gate in INTEGRITY_GATES}
    with_fail = {**all_pass, "REGISTRO_ORFAO": "FAIL"}
    with_unverified = {**all_pass, "INDICE_ADIANTADO": "NAO_VERIFICADO"}
    with_na = {**all_pass, "VIEW_DIVERGENTE": "NAO_APLICAVEL"}

    def status_for(gates_map: dict[str, str], **kwargs: Any) -> tuple[str, list[str]]:
        reasons = derive_partial_reasons(
            ledger_status=kwargs.get("ledger_status", "closed"),
            gate_results=gates_map,
            gaps=kwargs.get("gaps", 0),
            pending_authorization=kwargs.get("pending_authorization", 0),
            out_of_reach_findings=kwargs.get("out_of_reach", 0),
            reserved_to_jeremias=kwargs.get("reserved", 0),
        )
        return (
            derive_registry_status(
                mission_blocked=kwargs.get("mission_blocked", False),
                ledger_status=kwargs.get("ledger_status", "closed"),
                gate_results=gates_map,
                gaps=kwargs.get("gaps", 0),
                dossier_missing=kwargs.get("dossier_missing", 0),
                assignments=kwargs.get("assignments", 2),
                transit_records=kwargs.get("transit", 0),
                partial_reasons=reasons,
            ),
            reasons,
        )

    condition("catorze gates com prova e ledger fechado concluem",
              status_for(all_pass)[0] == "COMPLETED")
    condition("um gate em FAIL derruba para parcial",
              status_for(with_fail) == ("PARTIAL", ["integrity_fail"]))
    condition("um gate não verificado derruba para parcial",
              status_for(with_unverified) == ("PARTIAL", ["unverified_gate"]))
    condition("não aplicável justificado não derruba a rodada",
              status_for(with_na)[0] == "COMPLETED")
    condition("treze gates reportados não concluem a rodada",
              status_for({gate: "PASS" for gate in INTEGRITY_GATES[:13]})[0] == "PARTIAL")
    condition("lacuna aberta impede a conclusão e nomeia o motivo",
              status_for(all_pass, gaps=1) == ("PARTIAL", ["capability_missing"]))
    condition("sem registro de emissão de tarefa não há conclusão (R6)",
              status_for(all_pass, assignments=0)[0] == "PARTIAL")
    condition("registro em trânsito impede a conclusão",
              status_for(all_pass, transit=1)[0] == "PARTIAL")
    condition("contagem única não fecha a rodada",
              status_for(all_pass, ledger_status="single_count_unverified")
              == ("PARTIAL", ["single_count_unverified"]))
    condition("conservação bloqueada é o motivo mais grave, e vem primeiro",
              status_for(with_fail, ledger_status="bloqueado_conservacao")[1]
              == ["conservation_blocked", "integrity_fail"])
    condition("material ausente bloqueia a rodada, não a torna parcial",
              status_for(all_pass, mission_blocked=True)[0] == "BLOCKED")
    condition(
        "os motivos parciais saem ordenados por gravidade",
        derive_partial_reasons(
            ledger_status="single_count_unverified",
            gate_results=with_fail,
            gaps=1,
            pending_authorization=1,
            out_of_reach_findings=1,
            reserved_to_jeremias=1,
        )
        == [
            "integrity_fail",
            "pending_authorization",
            "capability_missing",
            "single_count_unverified",
            "alcance_de_escrita_insuficiente",
            "decisao_reservada_a_jeremias",
        ],
    )
    mission = director_mission()
    condition(
        "missão íntegra do Diretor abre a rodada",
        mission_verdict(mission, contract_digest=CONTRACT_DIGEST, material_present=True,
                        material_digest=MATERIAL_DIGEST, dossier_missing=[]) == "ACEITA",
    )
    condition(
        "dossiê incompleto não bloqueia: vira registro que não pousa",
        mission_verdict(mission, contract_digest=CONTRACT_DIGEST, material_present=True,
                        material_digest=MATERIAL_DIGEST,
                        dossier_missing=["perfil de destinos"]) == "ACEITA",
    )
    condition(
        "missão de outro produtor é tentativa de bypass",
        mission_verdict(director_mission(producer="ceo-maestro"),
                        contract_digest=CONTRACT_DIGEST, material_present=True,
                        material_digest=MATERIAL_DIGEST, dossier_missing=[])
        == "BLOCKED_BYPASS_ATTEMPT",
    )
    condition(
        "missão endereçada a outro Departamento é inválida",
        mission_verdict(director_mission(recipient="departamento-desenvolvimento"),
                        contract_digest=CONTRACT_DIGEST, material_present=True,
                        material_digest=MATERIAL_DIGEST, dossier_missing=[])
        == "BLOCKED_INVALID_MISSION",
    )
    condition(
        "contrato divergente bloqueia antes de qualquer leitura",
        mission_verdict(director_mission(contract_digest=digest("9")),
                        contract_digest=CONTRACT_DIGEST, material_present=True,
                        material_digest=MATERIAL_DIGEST, dossier_missing=[])
        == "BLOCKED_CONTRACT_MISMATCH",
    )
    condition(
        "resumo no lugar do material original bloqueia a rodada",
        mission_verdict(mission, contract_digest=CONTRACT_DIGEST, material_present=False,
                        material_digest=MATERIAL_DIGEST, dossier_missing=[])
        == "BLOCKED_SOURCE_MISMATCH",
    )
    condition(
        "todo estado de descoberta converte para painel, e o não emitido abre lacuna",
        all(state in PANEL_CONVERSION for state in
            ["AVAILABLE_OK", "AVAILABLE_BLOCKED", "AVAILABLE_FALHO",
             "AVAILABLE_SEM_RETORNO", "INVALID", "CONFLICTED", "MISSING"])
        and convert_discovery("AVAILABLE_OK") == ("emitida", "COMPLETED", False)
        and convert_discovery("INVALID") == ("nao_emitida", "SEM_RETORNO", True)
        and all(convert_discovery(state)[2] for state in
                ["AVAILABLE_BLOCKED", "AVAILABLE_FALHO", "AVAILABLE_SEM_RETORNO",
                 "INVALID", "CONFLICTED", "MISSING"]),
    )
    condition(
        "cada natureza tem exatamente uma regra decisora, e o não-registro não tem agente",
        sorted(RULE_TO_NATURE.values()) == sorted(NATURES)
        and len(set(RULE_TO_NATURE.values())) == len(NATURES),
    )
    condition(
        "as quatro capacidades cobrem as sete naturezas de registro sem sobreposição",
        len(AGENT_CAPABILITY) == 4
        and len([nature for nature in NATURES if nature != "nao-registro"]) == 7,
    )
    condition(
        "o retorno não conta bateria de teste executada",
        derived["test_summary"] == {"pass": 0, "fail": 0, "skip": 0,
                                    "skip_reasons": [], "critical_fail": False},
    )
    condition(
        "a conversão de fronteira troca source_digest por candidate_digest",
        "source_digest" not in derived["causal"]
        and derived["causal"]["candidate_digest"] == CANDIDATE_DIGEST
        and "source_digest" in completed["causal"]
        and derived["candidate_digest"] == CANDIDATE_DIGEST,
    )
    condition(
        "todo artefato do retorno resolve a partir do livro-razão",
        derived["artifact_refs"][0]
        == completed["conservation_ledger"]["artifact_ref"]
        and derived["evidence_refs"] == completed["evidence_refs"],
    )
    condition(
        "fatia em trânsito no ledger impede o fechamento, mesmo com a soma coerente",
        ledger_closes(
            unaccounted=[],
            identified=5,
            routed=5,
            counters=count_by_state([*states, split_decision()["state"]]),
            recount_proof="independent_capability",
            delta_final=0,
            entries=5,
        )
        != "closed",
    )
    case("digest da fonte normativa confere com o declarado em ORIGEM.md", True,
         conferir_digest_das_regras(RULES_PATH))

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
