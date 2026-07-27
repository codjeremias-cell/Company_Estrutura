"""Validador determinístico do Departamento de Arquitetura de Dados.

Verifica o pacote, o schema interno, os artefatos internos e — como regressão de
fronteira — que o contrato do `diretor-de-lentes` reconhece este Departamento e
aceita o `DEPARTMENT_RETURN` convertido a partir do `DATA_LEDGER`.

Prova mecanicamente o que o ADR-008 fixou: aqui não se pontua, não se escreve
código e não se decide arquitetura macro; e o gate de saída RI-04 — grão,
expand/contract com rollback, acesso justificado — não admite compensação.

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
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-arquitetura-dados.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
AGENTS_ROOT = PACKAGE_ROOT / "agentes"
REFERENCES_ROOT = PACKAGE_ROOT / "references"

OPERATIONS_ROOT = PACKAGE_ROOT.parent
DIRECTOR_ROOT = OPERATIONS_ROOT.parent
CEO_ROOT = DIRECTOR_ROOT.parent
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(CEO_ROOT.parent))
).resolve()
DIRECTOR_SCHEMA_PATH = DIRECTOR_ROOT / "schemas" / "diretor-de-lentes.schema.json"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        collect_property_names, digest, find_const, sha256_file, validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_adr_series,
        validate_agents_folder, validate_frontmatter, validate_links,
        validate_openai_yaml, validate_required_files,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print("[FAIL] motor compartilhado ausente em "
          f"{STRUCTURE_ROOT}/_compartilhado: {exc}")
    raise SystemExit(1)


DEPARTMENT = "departamento-arquitetura-dados"

AGENT_CAPABILITY = {
    "agente-perguntas-e-volumetria": "PERGUNTAS_VOLUMETRIA",
    "agente-escolha-de-persistencia": "ESCOLHA_PERSISTENCIA",
    "agente-modelo-e-grao": "MODELO_GRAO",
    "agente-evolucao-e-migracao": "EVOLUCAO_MIGRACAO",
    "agente-escala-e-acesso": "ESCALA_ACESSO",
    "agente-contratos-e-integridade": "CONTRATOS_INTEGRIDADE",
}
CAPABILITY_WAVE = {
    "PERGUNTAS_VOLUMETRIA": 1,
    "ESCOLHA_PERSISTENCIA": 2,
    "MODELO_GRAO": 3,
    "EVOLUCAO_MIGRACAO": 4,
    "ESCALA_ACESSO": 4,
    "CONTRATOS_INTEGRIDADE": 4,
}
CLOSURE_ITEMS = ["GRAO", "EVOLUCAO_ROLLBACK", "ACESSO_JUSTIFICADO"]

AGENT_DISPLAY = {
    "agente-perguntas-e-volumetria": "Agente de Perguntas e Volumetria",
    "agente-escolha-de-persistencia": "Agente de Escolha de Persistência",
    "agente-modelo-e-grao": "Agente de Modelo e Grão",
    "agente-evolucao-e-migracao": "Agente de Evolução e Migração",
    "agente-escala-e-acesso": "Agente de Escala e Acesso",
    "agente-contratos-e-integridade": "Agente de Contratos e Integridade",
}

# ADR-008: o que não pode existir como nome de propriedade em lugar nenhum do schema.
FORBIDDEN_SCORING = {
    "score", "nota", "notas", "minimum_score", "absolute_score", "scorecard",
    "veredito", "verdict", "rubrica", "peso", "pesos", "corte", "cut_score",
    "aprovado", "ranking", "vencedor", "winner",
}
FORBIDDEN_CODE = {
    "codigo", "code", "patch", "diff", "snippet", "implementacao", "query",
    "sql", "ddl", "script", "dao", "repositorio",
}
FORBIDDEN_ARCH = {
    "modulo", "modulos", "c4", "topologia", "deployment", "componente",
    "componentes", "bounded_context", "sincrono", "assincrono",
}

DIG = "sha256:" + "a" * 64
STAMP = "2026-07-26T10:00:00Z"


def causal(producer: str = DEPARTMENT, **over: Any) -> dict[str, Any]:
    base = {
        "work_item_id": "WI-DADOS-001",
        "front_id": "FR-DADOS-001",
        "handoff_id": "HO-DADOS-001",
        "message_id": "MSG-DADOS-001",
        "causation_message_ids": ["MSG-DIRETOR-001"],
        "contract_id": "CT-DADOS-001",
        "contract_version": 1,
        "contract_digest": DIG,
        "candidate_digest": "n/a",
        "round": 1,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": DIG,
        "created_at": STAMP,
    }
    base.update(over)
    return base


def question(n: int = 1, workload: str = "OLTP") -> dict[str, Any]:
    return {
        "question": f"Quantas matriculas por curso no mes corrente, recorte {n}?",
        "frequency": "40 vezes por dia",
        "latency_budget": "300ms",
        "workload": workload,
    }


def grain(entity: str = "fato_matricula") -> dict[str, Any]:
    return {
        "entity": entity,
        "one_row_means": "uma matricula confirmada de um aluno em uma turma",
        "history_strategy": "SCD2",
        "transactional_boundary": "matricula + saldo de vagas na mesma transacao",
    }


def phase(name: str, destructive: bool = False) -> dict[str, Any]:
    return {
        "phase": name,
        "action": f"executa a fase {name} sobre a tabela de matricula",
        "rollback": f"reverte a fase {name} sem perda de dado ja gravado",
        "destructive": destructive,
    }


def migration(**over: Any) -> dict[str, Any]:
    base = {
        "phases": [phase("EXPAND"), phase("DUAL_WRITE"), phase("BACKFILL"),
                   phase("SWITCH_READ"), phase("CONTRACT", True)],
        "next_free_version": "V27",
        "immutability_ack": True,
        "engine": "PostgreSQL 16",
        "same_engine_dev_prod": True,
    }
    base.update(over)
    return base


def access(**over: Any) -> dict[str, Any]:
    base = {
        "structure": "idx_matricula_turma_data",
        "kind": "INDICE",
        "driven_by_question": "Quantas matriculas por curso no mes corrente, recorte 1?",
        "expected_effect": "troca varredura por busca por faixa",
        "write_cost": "encarece insercao de matricula em um indice",
        "measured": False,
    }
    base.update(over)
    return base


def contract_item(**over: Any) -> dict[str, Any]:
    base = {
        "subject": "matricula",
        "meaning": "matricula confirmada, ja paga e nao cancelada",
        "constraint_error_flow": "unicidade aluno+turma devolve 409 tratado fora da transacao",
        "commit_relative_trigger": "AFTER_COMMIT",
        "anti_dual_write": "OUTBOX",
        "pii": False,
    }
    base.update(over)
    return base


def dependency(**over: Any) -> dict[str, Any]:
    base = {
        "target": "departamento-desenvolvimento",
        "need": "implementar o acesso parametrizado sobre o modelo entregue",
        "attached_constraint": "acesso parametrizado obrigatorio, RO-04, sem concatenar entrada",
        "origin_rule": "RO-04",
    }
    base.update(over)
    return base


def assignment(capability: str = "MODELO_GRAO", **over: Any) -> dict[str, Any]:
    base = {
        "task_id": f"TASK-{capability}",
        "worker_id": next(a for a, c in AGENT_CAPABILITY.items() if c == capability),
        "capability": capability,
        "wave": CAPABILITY_WAVE[capability],
        "issued_at": STAMP,
        "destination": "evidencias/retorno-modelo.md",
    }
    base.update(over)
    return base


def plan(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DATA_PLAN",
        "data_plan_id": "PLAN-DADOS-001",
        "causal": causal(),
        "department_mission_ref": "DM-DADOS-001",
        "floor_met": True,
        "questions": [question(1), question(2), question(3, "OLAP")],
        "volumetry_order": "1e6 linhas hoje, 2x ao ano, 80 leituras por segundo no pico",
        "waves": [assignment(c) for c in CAPABILITY_WAVE],
        "return_to": DEPARTMENT,
        "issued_at": STAMP,
    }
    base.update(over)
    return base


def task(capability: str = "MODELO_GRAO", **over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DATA_TASK",
        "task_id": f"TASK-{capability}",
        "causal": causal(),
        "capability": capability,
        "worker_id": next(a for a, c in AGENT_CAPABILITY.items() if c == capability),
        "wave": CAPABILITY_WAVE[capability],
        "question": "Qual o grao de cada tabela do modelo de matricula?",
        "return_to": DEPARTMENT,
        "forbidden_context": [
            "nao produz codigo, DDL nem arquivo de migracao",
            "nao pontua e nao emite veredito",
        ],
        "issued_at": STAMP,
    }
    base.update(over)
    return base


def worker_return(capability: str = "MODELO_GRAO", **over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DATA_RETURN",
        "task_id": f"TASK-{capability}",
        "causal": causal(),
        "capability": capability,
        "worker_id": next(a for a, c in AGENT_CAPABILITY.items() if c == capability),
        "status": "COMPLETED",
        "assumptions": ["volumetria informada pelo solicitante, nao medida"],
        "delegated_dependencies": [dependency()],
        "pending": [],
        "return_to": DEPARTMENT,
        "issued_at": STAMP,
    }
    extras = {
        "PERGUNTAS_VOLUMETRIA": {
            "questions": [question(1), question(2), question(3, "OLAP")],
            "volumetry_order": "1e6 linhas hoje, 2x ao ano, 80 leituras por segundo",
        },
        "ESCOLHA_PERSISTENCIA": {
            "engine_choice": "PostgreSQL",
            "engine_rationale": "relacional atende as tres perguntas com juncao simples",
            "same_engine_dev_prod": True,
        },
        "MODELO_GRAO": {"grains": [grain()]},
        "EVOLUCAO_MIGRACAO": {"migration_plan": migration()},
        "ESCALA_ACESSO": {"access_justifications": [access()]},
        "CONTRATOS_INTEGRIDADE": {"data_contracts": [contract_item()]},
    }
    base.update(extras.get(capability, {}))
    base.update(over)
    return base


def closure(**states: str) -> list[dict[str, Any]]:
    return [
        {
            "item": item,
            "state": states.get(item, "ATENDIDO"),
            "evidence": f"evidencia registrada para o item {item}",
        }
        for item in CLOSURE_ITEMS
    ]


def ledger(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DATA_LEDGER",
        "data_ledger_id": "LEDGER-DADOS-001",
        "causal": causal(),
        "department_mission_ref": "DM-DADOS-001",
        "plan": plan(),
        "assignments": [assignment(c) for c in CAPABILITY_WAVE],
        "returns_seen": 6,
        "closure": closure(),
        "grain_declarations": [grain()],
        "migration_plan": migration(),
        "access_justifications": [access()],
        "data_contracts": [contract_item()],
        "delegated_dependencies": [dependency()],
        "capability_gaps": [],
        "constraint_conflict": False,
        "test_summary": {
            "pass": 0, "fail": 0, "skip": 1,
            "skip_reasons": ["este Departamento nao executa teste"],
            "critical_fail": False,
        },
        "evidence_refs": ["evidencias/ledger-dados.md"],
        "pending": [],
        "entrega": "ENTREGUE",
        "return_to": "diretor-de-lentes",
        "recorded_at": STAMP,
    }
    base.update(over)
    return base


def capability_gap(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DATA_CAPABILITY_GAP",
        "reason": "PISO_NAO_ATENDIDO",
        "capability": "levantamento de perguntas do negocio e volumetria",
        "worker_id": "n/a",
        "expected_contract": "tres perguntas escritas e volumetria em ordem de grandeza",
        "discovery_evidence": "a missao trouxe apenas o pedido de modelar o banco",
        "impact": "sem o piso, o modelo responderia a perguntas nao formuladas",
        "status": "OPEN",
        "owner": "diretor-de-lentes",
    }
    base.update(over)
    return base


# ---------------------------------------------------------------------------
# Conversão de fronteira: DATA_LEDGER -> DEPARTMENT_RETURN do Diretor.
# ---------------------------------------------------------------------------

def to_department_return(led: dict[str, Any]) -> dict[str, Any]:
    """Converte o livro-razão interno no envelope que o Diretor consome."""
    return {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "DR-DADOS-001",
        "causal": {
            **{k: v for k, v in led["causal"].items()},
        },
        "department_mission_ref": led["department_mission_ref"],
        "returned_by": led["causal"]["producer"],
        "state": "RETURNED",
        "scope_touched": ["modelo de dados da matricula"],
        "artifact_refs": ["evidencias/modelo-matricula.md"],
        "evidence_refs": led["evidence_refs"],
        "candidate_digest": DIG,
        "test_summary": led["test_summary"],
        "pending_refs": [],
        "dissent_refs": [],
        "returned_to": "diretor-de-lentes",
        "returned_at": led["recorded_at"],
    }


# ---------------------------------------------------------------------------
# Gate de saída recalculado em código — sem consultar o campo `entrega`.
# ---------------------------------------------------------------------------

def gate_fecha(led: dict[str, Any]) -> bool:
    estados = {c["item"]: c["state"] for c in led.get("closure", [])}
    if sorted(estados) != sorted(CLOSURE_ITEMS):
        return False
    if any(state != "ATENDIDO" for state in estados.values()):
        return False
    if not led.get("grain_declarations"):
        return False
    if not led.get("access_justifications"):
        return False
    if "migration_plan" not in led:
        return False
    if not led.get("assignments"):
        return False
    if led.get("capability_gaps"):
        return False
    if led.get("constraint_conflict"):
        return False
    if led.get("pending"):
        return False
    if not led.get("plan", {}).get("floor_met", False):
        return False
    return True


def grao_completo(grains: list[dict[str, Any]]) -> bool:
    return bool(grains) and all(
        len(g.get("one_row_means", "").strip()) >= 15 for g in grains
    )


def evolucao_reversivel(plan_: dict[str, Any] | None) -> bool:
    if not plan_:
        return False
    fases = plan_.get("phases", [])
    if len(fases) < 2:
        return False
    if not all(f.get("rollback") for f in fases):
        return False
    if any(f.get("destructive") and f.get("phase") != "CONTRACT" for f in fases):
        return False
    return bool(plan_.get("next_free_version")) and plan_.get("immutability_ack") is True


def acesso_justificado(items: list[dict[str, Any]]) -> bool:
    return bool(items) and all(
        len(a.get("driven_by_question", "").strip()) >= 15 and a.get("measured") is False
        for a in items
    )


def run() -> int:
    cases: list[tuple[str, bool, list[str]]] = []

    def case(name: str, expected_valid: bool, errors: list[str]) -> None:
        cases.append((name, expected_valid, errors))

    def check(name: str, condition: bool, detail: str = "condição falhou") -> None:
        cases.append((name, True, [] if condition else [detail]))

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    director = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))

    # --- A. Pacote e vínculos ------------------------------------------------
    case("arquivos obrigatórios da gerente", True, validate_required_files(
        [SKILL_PATH, CONTRACT_PATH, OPENAI_PATH, SCHEMA_PATH, EVALS_PATH]))
    case("references/ completo", True, validate_required_files([
        REFERENCES_ROOT / "adr-008-dados-skill-nova-e-seis-agentes.md",
        REFERENCES_ROOT / "fronteiras-do-departamento.md",
        REFERENCES_ROOT / "gates-e-licoes-de-producao.md",
        REFERENCES_ROOT / "protocolo-de-dados.md",
        REFERENCES_ROOT / "origem-e-fundamentacao.md",
    ]))
    case("agentes/ contém exatamente os seis nomes canônicos", True,
         validate_agents_folder(AGENTS_ROOT, list(AGENT_CAPABILITY)))
    case("frontmatter da gerente", True,
         validate_frontmatter(SKILL_PATH, DEPARTMENT))

    agent_errors: list[str] = []
    for name, display in AGENT_DISPLAY.items():
        agent_errors += validate_frontmatter(AGENTS_ROOT / name / "SKILL.md", name)
        agent_errors += validate_openai_yaml(
            AGENTS_ROOT / name / "agents" / "openai.yaml", display, f"${name}")
    case("frontmatter e interface dos seis agentes", True, agent_errors)

    case("interface da gerente", True, validate_openai_yaml(
        OPENAI_PATH, "Departamento de Arquitetura de Dados", f"${DEPARTMENT}"))
    case("todos os links markdown internos resolvem", True,
         validate_links(PACKAGE_ROOT))
    case("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT))

    posicao: list[str] = []
    if PACKAGE_ROOT.parent.name != "departamentos-operacionais":
        posicao.append("Departamento fora de departamentos-operacionais/")
    if DIRECTOR_ROOT.name != "diretor-de-lentes":
        posicao.append("Departamento fora do diretor-de-lentes")
    if not RULES_PATH.is_file():
        posicao.append(f"fonte normativa ausente em {RULES_PATH}")
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    if "../../../../regras-de-ouro/REGRAS-DE-OURO.md" not in skill_text:
        posicao.append("gerente sem fonte normativa no caminho relativo do nível 4")
    for name in AGENT_CAPABILITY:
        texto = (AGENTS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")
        if "../../../../../../regras-de-ouro/REGRAS-DE-OURO.md" not in texto:
            posicao.append(f"{name} sem fonte normativa no caminho relativo do nível 6")
    case("posição na hierarquia e fonte normativa por nível", True, posicao)

    enum_worker = schema["$defs"]["workerId"]["enum"]
    case("enum workerId bate com as pastas reais de agentes/", True,
         [] if sorted(enum_worker) == sorted(AGENT_CAPABILITY)
         else [f"workerId {sorted(enum_worker)} != {sorted(AGENT_CAPABILITY)}"])

    # --- B. Travas mecânicas do ADR-008 --------------------------------------
    nomes: set[str] = set()
    collect_property_names(schema, nomes)
    for rotulo, proibidos in (
        ("nota", FORBIDDEN_SCORING),
        ("código", FORBIDDEN_CODE),
        ("arquitetura macro", FORBIDDEN_ARCH),
    ):
        achados = sorted(nomes & proibidos)
        case(f"schema não tem nenhum campo de {rotulo}", True,
             [] if not achados else [f"campos proibidos no schema: {achados}"])

    case("producer travado por const no causalHeader", True,
         [] if find_const(schema, "producer", DEPARTMENT)
         else ["causalHeader.producer não está travado por const"])
    case("measured travado em false — R2, projeção nunca vira medição", True,
         [] if find_const(schema, "measured", False)
         else ["accessJustification.measured não está travado em false"])
    case("immutability_ack travado em true — L1", True,
         [] if find_const(schema, "immutability_ack", True)
         else ["migrationPlan.immutability_ack não está travado em true"])

    # --- C. Artefatos aceitos ------------------------------------------------
    case("schema aceita DATA_PLAN com piso atendido", True,
         validate_schema(plan(), schema, schema))
    case("schema aceita DATA_PLAN com piso não atendido e nenhuma onda", True,
         validate_schema(plan(floor_met=False, questions=[], volumetry_order="",
                              waves=[]), schema, schema))
    for capability in CAPABILITY_WAVE:
        case(f"schema aceita DATA_TASK de {capability}", True,
             validate_schema(task(capability), schema, schema))
        case(f"schema aceita DATA_RETURN de {capability}", True,
             validate_schema(worker_return(capability), schema, schema))
    case("schema aceita DATA_CAPABILITY_GAP", True,
         validate_schema(capability_gap(), schema, schema))
    case("schema aceita DATA_LEDGER com o gate fechado", True,
         validate_schema(ledger(), schema, schema))

    # --- D. Negativos: plano -------------------------------------------------
    case("piso declarado atendido com apenas duas perguntas", False,
         validate_schema(plan(questions=[question(1), question(2)]), schema, schema))
    case("piso declarado atendido sem volumetria", False,
         validate_schema(plan(volumetry_order="1e6"), schema, schema))
    case("piso não atendido mas com onda emitida", False,
         validate_schema(plan(floor_met=False, questions=[], volumetry_order=""),
                         schema, schema))
    case("plano com produtor forjado por outro Departamento", False,
         validate_schema(plan(causal=causal(producer="departamento-desenvolvimento")),
                         schema, schema))
    case("plano devolvido para fora do Departamento", False,
         validate_schema(plan(return_to="diretor-de-lentes"), schema, schema))

    # --- E. Negativos: tarefa ------------------------------------------------
    case("tarefa com capacidade trocada para o agente", False,
         validate_schema(task("MODELO_GRAO", worker_id="agente-escala-e-acesso"),
                         schema, schema))
    case("tarefa de modelagem emitida na onda da persistência", False,
         validate_schema(task("MODELO_GRAO", wave=2), schema, schema))
    case("forbidden_context sem a proibição de produzir código", False,
         validate_schema(task("MODELO_GRAO",
                              forbidden_context=["nao pontua e nao emite veredito"]),
                         schema, schema))
    case("forbidden_context vazio", False,
         validate_schema(task("MODELO_GRAO", forbidden_context=[]), schema, schema))
    case("tarefa endereçada a agente fora do time", False,
         validate_schema(task("MODELO_GRAO", worker_id="agente-drivers-e-restricoes"),
                         schema, schema))
    case("tarefa com retorno endereçado ao Diretor", False,
         validate_schema(task("MODELO_GRAO", return_to="diretor-de-lentes"),
                         schema, schema))

    # --- F. Negativos: retorno ----------------------------------------------
    case("modelo concluído sem nenhum grão declarado", False,
         validate_schema(worker_return("MODELO_GRAO", grains=[]), schema, schema))
    case("grão vazio de significado", False,
         validate_schema(worker_return("MODELO_GRAO", grains=[grain_vazio := {
             "entity": "matricula", "one_row_means": "linha",
             "history_strategy": "NENHUMA"}]), schema, schema))
    case("evolução concluída sem plano de migração", False,
         validate_schema({k: v for k, v in worker_return("EVOLUCAO_MIGRACAO").items()
                          if k != "migration_plan"}, schema, schema))
    case("escala concluída sem nenhuma justificativa de acesso", False,
         validate_schema(worker_return("ESCALA_ACESSO", access_justifications=[]),
                         schema, schema))
    case("persistência concluída sem evidência da escolha", False,
         validate_schema({k: v for k, v in worker_return("ESCOLHA_PERSISTENCIA").items()
                          if k != "engine_rationale"}, schema, schema))
    case("perguntas concluídas com apenas duas perguntas", False,
         validate_schema(worker_return("PERGUNTAS_VOLUMETRIA",
                                       questions=[question(1), question(2)]),
                         schema, schema))
    case("contratos concluídos sem nenhum contrato de dado", False,
         validate_schema(worker_return("CONTRATOS_INTEGRIDADE", data_contracts=[]),
                         schema, schema))
    case("retorno BLOCKED sem motivo", False,
         validate_schema(worker_return("MODELO_GRAO", status="BLOCKED", grains=[]),
                         schema, schema))
    case("retorno BLOCKED com motivo (aceito)", True,
         validate_schema(worker_return("MODELO_GRAO", status="BLOCKED", grains=[],
                                       blocked_reason="a missao pede tuning de query, que e do desenvolvimento"),
                         schema, schema))
    case("índice declarado como medido — R2 violada", False,
         validate_schema(worker_return("ESCALA_ACESSO",
                                       access_justifications=[access(measured=True)]),
                         schema, schema))
    case("índice sem acesso que o justifique", False,
         validate_schema(worker_return("ESCALA_ACESSO",
                                       access_justifications=[access(driven_by_question="por garantia")]),
                         schema, schema))
    case("cache proposto sem invalidação declarada", False,
         validate_schema(worker_return("ESCALA_ACESSO", access_justifications=[
             access(kind="CACHE", structure="cache_matricula")]), schema, schema))
    case("cache com invalidação declarada (aceito)", True,
         validate_schema(worker_return("ESCALA_ACESSO", access_justifications=[
             access(kind="CACHE", structure="cache_matricula",
                    invalidation="invalidado no AFTER_COMMIT da matricula")]),
             schema, schema))
    case("fase destrutiva fora do CONTRACT — L1/ADR-008 §7", False,
         validate_schema(worker_return("EVOLUCAO_MIGRACAO", migration_plan=migration(
             phases=[phase("EXPAND", True), phase("CONTRACT", True)])), schema, schema))
    case("plano de migração sem reconhecer a imutabilidade", False,
         validate_schema(worker_return("EVOLUCAO_MIGRACAO",
                                       migration_plan=migration(immutability_ack=False)),
                         schema, schema))
    case("fase de migração sem rollback", False,
         validate_schema(worker_return("EVOLUCAO_MIGRACAO", migration_plan=migration(
             phases=[{"phase": "EXPAND", "action": "adiciona coluna nova",
                      "destructive": False}, phase("CONTRACT", True)])),
             schema, schema))
    case("campo PII sem retenção declarada — L7", False,
         validate_schema(worker_return("CONTRATOS_INTEGRIDADE",
                                       data_contracts=[contract_item(pii=True)]),
                         schema, schema))
    case("campo PII com retenção e RLS (aceito)", True,
         validate_schema(worker_return("CONTRATOS_INTEGRIDADE", data_contracts=[
             contract_item(pii=True, retention="5 anos", rls_required=True)]),
             schema, schema))
    case("dependência ao desenvolvimento sem restrição anexada", False,
         validate_schema(worker_return("MODELO_GRAO", delegated_dependencies=[
             dependency(attached_constraint="ver modelo")]), schema, schema))
    # L5 mecanizada — achado do forward de 2026-07-26: a regra existia só em prosa.
    case("efeito colateral IN_TRANSACTION sem outbox — L5", False,
         validate_schema(worker_return("CONTRATOS_INTEGRIDADE", data_contracts=[
             contract_item(commit_relative_trigger="IN_TRANSACTION",
                           anti_dual_write="NAO_SE_APLICA")]), schema, schema))
    case("IN_TRANSACTION com CDC não basta — só outbox é escrita no commit", False,
         validate_schema(worker_return("CONTRATOS_INTEGRIDADE", data_contracts=[
             contract_item(commit_relative_trigger="IN_TRANSACTION",
                           anti_dual_write="CDC")]), schema, schema))
    case("escrita no outbox dentro da transação (aceita)", True,
         validate_schema(worker_return("CONTRATOS_INTEGRIDADE", data_contracts=[
             contract_item(commit_relative_trigger="IN_TRANSACTION",
                           anti_dual_write="OUTBOX")]), schema, schema))

    # --- G. Negativos: livro-razão e gate de saída ---------------------------
    for item in CLOSURE_ITEMS:
        case(f"entrega ENTREGUE com {item} AUSENTE", False,
             validate_schema(ledger(closure=closure(**{item: "AUSENTE"})),
                             schema, schema))
    case("closure com apenas dois itens", False,
         validate_schema(ledger(closure=closure()[:2]), schema, schema))
    case("ENTREGUE sem nenhum grão declarado", False,
         validate_schema(ledger(grain_declarations=[]), schema, schema))
    case("ENTREGUE sem nenhuma justificativa de acesso", False,
         validate_schema(ledger(access_justifications=[]), schema, schema))
    case("ENTREGUE sem plano de migração", False,
         validate_schema({k: v for k, v in ledger().items() if k != "migration_plan"},
                         schema, schema))
    case("ENTREGUE sem registro de emissão das tarefas — R6", False,
         validate_schema(ledger(assignments=[]), schema, schema))
    case("ENTREGUE com lacuna de capacidade aberta", False,
         validate_schema(ledger(capability_gaps=[capability_gap()]), schema, schema))
    case("ENTREGUE com pendência pendurada", False,
         validate_schema(ledger(pending=["falta confirmar a volumetria real"]),
                         schema, schema))
    case("conflito arquitetural sem escalação", False,
         validate_schema(ledger(constraint_conflict=True, entrega="BLOQUEADA"),
                         schema, schema))
    case("conflito arquitetural contornado com entrega normal", False,
         validate_schema(ledger(constraint_conflict=True,
                                escalation="o ownership impede a leitura direta exigida pelo modelo"),
                         schema, schema))
    case("conflito arquitetural escalado e bloqueado (aceito)", True,
         validate_schema(ledger(
             constraint_conflict=True, entrega="BLOQUEADA",
             escalation="o ownership impede a leitura direta exigida pelo modelo",
             closure=closure(GRAO="AUSENTE")), schema, schema))
    case("piso não atendido com entrega normal", False,
         validate_schema(ledger(plan=plan(floor_met=False, questions=[],
                                          volumetry_order="", waves=[])),
                         schema, schema))
    case("livro-razão declarando teste executado", False,
         validate_schema(ledger(test_summary={
             "pass": 3, "fail": 0, "skip": 0, "skip_reasons": [],
             "critical_fail": False}), schema, schema))
    case("entrega INCOMPLETA com item ausente (aceita)", True,
         validate_schema(ledger(entrega="INCOMPLETA",
                                closure=closure(ACESSO_JUSTIFICADO="AUSENTE"),
                                access_justifications=[]), schema, schema))
    case("livro-razão devolvido para fora do Diretor", False,
         validate_schema(ledger(return_to="ceo-maestro"), schema, schema))

    # --- H. Fronteira: validada contra o schema do CONSUMIDOR ----------------
    dept_return = to_department_return(ledger())
    case("Diretor aceita o DEPARTMENT_RETURN convertido do DATA_LEDGER", True,
         validate_schema(dept_return, director["$defs"]["departmentReturn"], director))

    forjado = copy.deepcopy(dept_return)
    forjado["returned_by"] = "departamento-desenvolvimento"
    case("Diretor rejeita retorno com autor divergente do produtor", False,
         validate_schema(forjado, director["$defs"]["departmentReturn"], director))

    fora = copy.deepcopy(dept_return)
    fora["returned_to"] = "ceo-maestro"
    case("Diretor rejeita retorno endereçado ao CEO", False,
         validate_schema(fora, director["$defs"]["departmentReturn"], director))

    executou = copy.deepcopy(dept_return)
    executou["test_summary"] = {"pass": 12, "fail": 0, "skip": 0,
                                "skip_reasons": [], "critical_fail": False}
    case("Diretor aceita estrutura, mas o teste executado não vem daqui", True,
         validate_schema(executou, director["$defs"]["departmentReturn"], director))

    op_enum = director["$defs"]["operationalDepartment"]["enum"]
    check("Diretor reconhece este Departamento como operacional",
          DEPARTMENT in op_enum, f"{DEPARTMENT} ausente de operationalDepartment")
    known = json.dumps(director["$defs"].get("knownCapability", {}), ensure_ascii=False)
    check("Diretor reconhece este Departamento como produtor causal",
          DEPARTMENT in known, f"{DEPARTMENT} ausente de knownCapability")
    check("Arquitetura de Software delega para este Departamento",
          DEPARTMENT in json.dumps(json.loads(
              (OPERATIONS_ROOT / "departamento-arquitetura-software" / "schemas"
               / "departamento-arquitetura-software.schema.json").read_text(encoding="utf-8")
          )["$defs"]["delegationTarget"], ensure_ascii=False),
          "delegationTarget da Arquitetura não aponta para cá")

    # --- I. Gate recalculado em código, sem ler o campo declarado ------------
    check("gate fecha quando os três itens estão atendidos", gate_fecha(ledger()))
    for item in CLOSURE_ITEMS:
        check(f"gate não fecha com {item} ausente",
              not gate_fecha(ledger(closure=closure(**{item: "AUSENTE"}))))
    check("dois itens atendidos não compensam o terceiro",
          not gate_fecha(ledger(closure=closure(GRAO="AUSENTE"))))
    check("dez acessos justificados não substituem o grão",
          not gate_fecha(ledger(grain_declarations=[],
                                access_justifications=[access() for _ in range(10)])))
    check("gate não fecha sem registro de emissão — R6",
          not gate_fecha(ledger(assignments=[])))
    check("gate não fecha com lacuna aberta",
          not gate_fecha(ledger(capability_gaps=[capability_gap()])))
    check("gate não fecha com conflito arquitetural",
          not gate_fecha(ledger(constraint_conflict=True)))
    check("gate não fecha se o piso não foi atendido",
          not gate_fecha(ledger(plan=plan(floor_met=False, questions=[],
                                          volumetry_order="", waves=[]))))
    check("grão sem significado não conta como declarado",
          not grao_completo([{"entity": "x", "one_row_means": "linha",
                              "history_strategy": "NENHUMA"}]))
    check("grão com significado conta", grao_completo([grain()]))
    check("evolução sem rollback em uma fase não é reversível",
          not evolucao_reversivel(migration(phases=[
              {"phase": "EXPAND", "action": "adiciona coluna", "destructive": False},
              phase("CONTRACT", True)])))
    check("evolução com destrutivo fora do CONTRACT não é reversível",
          not evolucao_reversivel(migration(phases=[phase("EXPAND", True),
                                                    phase("CONTRACT", True)])))
    check("evolução sem versão livre declarada não é reversível",
          not evolucao_reversivel(migration(next_free_version="")))
    check("evolução completa é reversível", evolucao_reversivel(migration()))
    check("acesso 'por garantia' não é justificado",
          not acesso_justificado([access(driven_by_question="por garantia")]))
    check("acesso declarado como medido não é aceito — R2",
          not acesso_justificado([access(measured=True)]))
    check("acesso amarrado a pergunta nomeada é justificado",
          acesso_justificado([access()]))
    check("uma fase só não é plano de evolução",
          not evolucao_reversivel(migration(phases=[phase("CONTRACT", True)])))

    # --- Coerência do catálogo de evals -------------------------------------
    catalogo = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    check("catálogo de evals tem ao menos 12 casos", len(catalogo.get("cases", [])) >= 12,
          f"catálogo com {len(catalogo.get('cases', []))} casos")
    check("todo caso do catálogo declara acionamento e aderência",
          all({"acionou", "aderiu"} <= set(c) for c in catalogo.get("cases", [])),
          "caso sem acionou/aderiu")
    check("catálogo tem ao menos um caso de recusa por fronteira",
          any(c.get("espera_recusa") for c in catalogo.get("cases", [])),
          "nenhum caso de recusa")
    check("digest das regras de ouro é verificável",
          RULES_PATH.is_file() and sha256_file(RULES_PATH).startswith("sha256:"))
    check("digest do próprio schema é verificável",
          digest(SCHEMA_PATH.read_text(encoding="utf-8")).startswith("sha256:"))

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
