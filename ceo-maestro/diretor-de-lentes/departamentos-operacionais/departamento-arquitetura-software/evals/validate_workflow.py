"""Validador determinístico do Departamento de Arquitetura de Software.

Verifica o pacote, o schema interno, os artefatos internos e — como regressão de
fronteira — que o contrato do `diretor-de-lentes` reconhece este Departamento.

Prova mecanicamente as duas restrições que o ADR-006 fixou: aqui não se pontua, e
aqui não se modela dado nem se escreve código.

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
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-arquitetura-software.schema.json"
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

DEPARTMENT = "departamento-arquitetura-software"
AGENT_KIND = {
    "agente-drivers-e-restricoes": "DRIVERS",
    "agente-modularidade-e-limites": "MODULARIDADE",
    "agente-integracoes-e-contratos": "INTEGRACAO",
    "agente-qualidade-e-operacao": "QUALIDADE",
    "agente-alternativas-e-tradeoffs": "ALTERNATIVAS",
    "agente-adr-e-c4": "ADR_C4",
}
AGENT_NAMES = list(AGENT_KIND)
DIMENSIONS = [
    "DRIVERS",
    "MODULARIDADE",
    "INTEGRACAO",
    "QUALIDADE",
    "ALTERNATIVAS",
    "ADR_C4",
    "EVIDENCIA",
    "SIMPLICIDADE",
]
RULES_LINK_DEPARTMENT = "../../../../regras-de-ouro/REGRAS-DE-OURO.md"
RULES_LINK_AGENT = "../../../../../../regras-de-ouro/REGRAS-DE-OURO.md"

# ADR-006, decisão 1: aqui não se pontua.
FORBIDDEN_SCORING = {
    "score", "nota", "notas", "minimum_score", "veredito", "verdict",
    "rubrica", "peso", "pesos", "corte", "aprovado",
}
# ADR-006, decisão 4: aqui não se modela dado nem se implementa.
FORBIDDEN_DATA = {
    "entidade", "entidades", "tabela", "tabelas", "coluna", "colunas",
    "indice", "indices", "migracao", "migracoes", "ddl", "normalizacao",
    "particionamento", "grao", "sharding", "banco",
}
FORBIDDEN_CODE = {
    "codigo", "code", "patch", "diff", "snippet", "implementacao", "query", "sql",
}

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        collect_property_names,
        conferir_digest_das_regras,
        digest,
        find_const,
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
# Regras comportamentais, recalculadas em código
# --------------------------------------------------------------------------

def option_set_valido(n_opcoes: int, justificativa: str) -> bool:
    """2–3 opções, ou uma única com justificativa verificável."""
    if n_opcoes >= 2:
        return n_opcoes <= 3
    return n_opcoes == 1 and len(justificativa) >= 30


def recomendacao_valida(perdas: list[str]) -> bool:
    """Recomendação sem perda declarada é propaganda."""
    return bool(perdas)


def delegacao_valida(target: str, decision_rule: str) -> bool:
    """Spike delegado ao desenvolvimento exige a regra que decide."""
    if target == "departamento-desenvolvimento":
        return len(decision_rule) >= 20
    return True


def pode_entregar(estados: dict[str, str], gates: dict[str, bool], lacunas: int) -> bool:
    if lacunas:
        return False
    if any(estado == "AUSENTE" for estado in estados.values()):
        return False
    return all(gates.values())


def acumulo_proibido(kind_a: str, kind_b: str) -> bool:
    pares = {frozenset({"ALTERNATIVAS", "ADR_C4"}), frozenset({"MODULARIDADE", "INTEGRACAO"})}
    return frozenset({kind_a, kind_b}) in pares


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

CONTRACT_DIGEST = digest("0")
PRODUCER = digest("1")


def causal(producer: str = DEPARTMENT) -> dict[str, Any]:
    return {
        "work_item_id": "work-003",
        "front_id": "front-arquitetura",
        "handoff_id": "handoff-003",
        "message_id": "message-arq-001",
        "causation_message_ids": ["message-diretor-003"],
        "contract_id": "contract-003",
        "contract_version": 1,
        "contract_digest": CONTRACT_DIGEST,
        "candidate_digest": "n/a",
        "round": 1,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": PRODUCER,
        "created_at": "2026-07-26T23:00:00-03:00",
    }


def driver_item(ident: str = "driver-latencia") -> dict[str, Any]:
    return {
        "id": ident,
        "enunciado": "O fluxo de cobrança responde dentro do limite acordado com o cliente.",
        "como_se_mede": "p95 do endpoint de cobrança <= 2 s, com 200 usuários simultâneos",
        "prioridade": 1,
        "origem": "objetivo de negócio, reunião de escopo",
    }


def module_item() -> dict[str, Any]:
    return {
        "nome": "Cobranca",
        "capacidade": "Emitir, cancelar e consultar faturas do cliente.",
        "nao_faz": "Não calcula imposto nem gera relatório analítico.",
        "data_ownership": "Dona das faturas; ninguém lê a base dela direto, só pelo contrato.",
        "depende_de": ["Cadastro"],
        "acoplamento": "fraco",
        "razao": "Ciclo de vida e dono de negócio próprios, taxa de mudança distinta.",
    }


def contract_item() -> dict[str, Any]:
    return {
        "entre": "Cobranca -> Relatorios",
        "estilo": "assincrono",
        "driver_que_decidiu": "driver-latencia",
        "contrato": "Evento FaturaEmitida, com identificador da fatura e momento da emissão.",
        "versionamento": "Campo novo é opcional; remoção exige versão nova do evento.",
        "idempotencia": "chave fatura_id",
        "modo_de_falha": "Consumidor fora: evento fica na fila; após 3 tentativas vai para a fila morta e alerta.",
    }


def scenario_item() -> dict[str, Any]:
    return {
        "atributo": "resiliencia",
        "driver_que_exige": "driver-latencia",
        "cenario_mensuravel": "Com o gateway fora, a cobrança enfileira e responde em ate 2 s; o pedido é processado em ate 15 min apos o retorno.",
        "meta": "RTO 15 min",
        "origem_da_meta": "restrição operacional declarada na missão",
        "implicacao_operacional": "Exige fila monitorada e plantão para a fila morta.",
    }


def option_item(nome: str = "monolito-modular") -> dict[str, Any]:
    return {
        "nome": nome,
        "essencia": "Um processo, módulos com fronteira forte e banco por contexto.",
        "atende_drivers": ["driver-latencia"],
        "perde": ["escala independente de cobrança"],
        "reversibilidade": "media",
        "custo": "baixo",
        "gatilho_de_mudanca": "cobrança passar de 40% da carga total",
    }


def adr_c4_item() -> dict[str, Any]:
    return {
        "adr_contexto": "SaaS B2B com cobrança e auditoria, time de quatro pessoas, sem stack decidida.",
        "adr_decisao": "Adotar monolito modular com fronteiras fortes.",
        "adr_consequencias": ["Perde escala independente de cobrança", "Ganha simplicidade operacional"],
        "alternativas_descartadas": [
            {
                "opcao": "dois servicos",
                "motivo_do_descarte": "Custo operacional acima da maturidade declarada do time.",
            }
        ],
        "adr_estado": "proposta",
        "c4_contexto": "Sistema, operador interno, gateway de pagamento e serviço de e-mail.",
        "c4_conteiner": "Aplicação web, worker de eventos e armazenamento por contexto.",
        "fontes": ["agente-alternativas-e-tradeoffs", "agente-modularidade-e-limites"],
        "divergencias": [],
    }


def delegated_dependency(target: str = "departamento-arquitetura-dados") -> dict[str, Any]:
    if target == "departamento-desenvolvimento":
        return {
            "target": target,
            "question": "Qual a latência do gateway sob 200 chamadas simultâneas?",
            "blocks": "a escolha entre monolito modular e dois serviços",
            "architectural_constraint": "O spike não altera contrato nem ownership já fixados.",
            "decision_rule": "Acima de 800 ms no p95, a opção de dois serviços cai.",
        }
    return {
        "target": target,
        "question": "Fatura e item ficam em um agregado ou em dois?",
        "blocks": "o fechamento do contrato de leitura de faturas",
        "architectural_constraint": "Cobranca é dona das faturas; leitura externa só pelo contrato.",
        "decision_rule": "n/a",
    }


def architecture_plan() -> dict[str, Any]:
    return {
        "artifact_type": "ARCHITECTURE_PLAN",
        "architecture_plan_id": "architecture-plan-001",
        "causal": causal(),
        "department_mission_ref": "department-mission-11",
        "drivers": [driver_item()],
        "restricoes": ["Time de quatro pessoas, sem plantão 24x7."],
        "adrs_vigentes": ["ADR-014 persistência relacional: aceita"],
        "fronts": [
            {
                "front_ref": "front-cobranca",
                "objetivo": "Definir a estrutura do domínio de cobrança.",
                "dimensoes": ["DRIVERS", "MODULARIDADE", "INTEGRACAO"],
                "wave": 1,
                "depende_de": [],
            }
        ],
        "created_at": "2026-07-26T23:05:00-03:00",
    }


def architecture_task(worker: str = "agente-drivers-e-restricoes") -> dict[str, Any]:
    kind = AGENT_KIND[worker]
    return {
        "artifact_type": "ARCHITECTURE_TASK",
        "task_id": f"task-{worker}",
        "causal": causal(),
        "worker_id": worker,
        "kind": kind,
        "front_ref": "front-cobranca",
        "wave": 4 if kind == "ADR_C4" else (0 if kind == "DRIVERS" else 1),
        "objective": "Produzir a contribuição desta ótica para a frente de cobrança.",
        "drivers": ["driver-latencia"],
        "constraints": ["ADR-014 persistência relacional: aceita"],
        "scope_in": ["O que esta ótica decide na frente."],
        "scope_out": [
            "Modelo de dados, banco, índice e migração: departamento-arquitetura-dados.",
            "Implementação e execução: departamento-desenvolvimento.",
        ],
        "inputs": ["contexto/missao-11.md"],
        "forbidden_context": [
            "preferência da gerente ou opção favorita",
            "retornos dos outros agentes desta onda",
            "conclusão esperada",
            "stack decidida por moda, sem driver",
        ],
        "stop_when": ["A ótica cobriu as dimensões atribuídas ou registrou lacuna."],
        "return_to": DEPARTMENT,
        "issued_at": "2026-07-26T23:10:00-03:00",
    }


def architecture_return(kind: str = "DRIVERS", status: str = "COMPLETED") -> dict[str, Any]:
    worker = next(name for name, k in AGENT_KIND.items() if k == kind)
    result: dict[str, Any] = {
        "artifact_type": "ARCHITECTURE_RETURN",
        "task_id": f"task-{worker}",
        "worker_id": worker,
        "kind": kind,
        "drivers": [driver_item()] if kind == "DRIVERS" else [],
        "modules": [module_item()] if kind == "MODULARIDADE" else [],
        "contracts": [contract_item()] if kind == "INTEGRACAO" else [],
        "scenarios": [scenario_item()] if kind == "QUALIDADE" else [],
        "options": (
            [option_item("monolito-modular"), option_item("dois-servicos")]
            if kind == "ALTERNATIVAS"
            else []
        ),
        "assumptions": [],
        "delegated_dependencies": [delegated_dependency()],
        "pending": ["R6 — a existência das tarefas não é verificável pelo runtime."],
        "status": status,
        "return_to": DEPARTMENT,
        "issued_at": "2026-07-26T23:40:00-03:00",
    }
    if kind == "ADR_C4":
        result["adr_c4"] = adr_c4_item()
    if status == "BLOCKED":
        for campo in ("drivers", "modules", "contracts", "scenarios", "options"):
            result[campo] = []
        result["blocked_reason"] = "Excerto incoerente: a opção recomendada não está entre as apresentadas."
    return result


def option_set(n: int = 2, justificativa: str = "n/a") -> dict[str, Any]:
    nomes = ["monolito-modular", "dois-servicos", "event-driven"]
    return {
        "artifact_type": "OPTION_SET",
        "option_set_id": "option-set-001",
        "causal": causal(),
        "front_ref": "front-cobranca",
        "options": [option_item(nomes[i]) for i in range(n)],
        "single_option_justification": justificativa,
        "recomendacao": "monolito-modular",
        "recomendacao_perde": ["escala independente de cobrança"],
        "created_at": "2026-07-27T00:00:00-03:00",
    }


def capability_gap() -> dict[str, Any]:
    return {
        "artifact_type": "ARCHITECTURE_CAPABILITY_GAP",
        "capability": "Cenários de qualidade sem ótica disponível nesta rodada.",
        "worker_id": "agente-qualidade-e-operacao",
        "dimensions": ["QUALIDADE"],
        "expected_contract": "Cenários mensuráveis com meta e implicação operacional.",
        "discovery_evidence": "SEM_RETORNO observado na tarefa task-agente-qualidade.",
        "impact": "A dimensão 4 fica PARCIAL e a entrega não fecha.",
        "status": "OPEN",
        "owner": "diretor-de-lentes",
    }


def architecture_ledger(
    entrega: bool = True,
    estados: dict[str, str] | None = None,
    gaps: list[dict[str, Any]] | None = None,
    with_assignments: bool = True,
    with_options: bool = True,
) -> dict[str, Any]:
    valores = estados or {d: "COBERTA" for d in DIMENSIONS}
    return {
        "artifact_type": "ARCHITECTURE_LEDGER",
        "architecture_ledger_id": "architecture-ledger-001",
        "causal": causal(),
        "department_mission_ref": "department-mission-11",
        "plan": architecture_plan(),
        "assignments": (
            [
                {
                    "task_id": f"task-{name}",
                    "worker_id": name,
                    "kind": AGENT_KIND[name],
                    "wave": 4 if AGENT_KIND[name] == "ADR_C4" else 1,
                    "issued_at": "2026-07-26T23:10:00-03:00",
                    "destination": f"arquitetura/task-{name}/",
                }
                for name in AGENT_NAMES
            ]
            if with_assignments
            else []
        ),
        "panel": [
            {"worker_id": name, "kind": AGENT_KIND[name], "status": "COMPLETED"}
            for name in AGENT_NAMES
        ],
        "dimensions": [
            {
                "dimension": d,
                "estado": valores[d],
                "razao": (
                    "Este candidato não expõe interface pública, então a dimensão não incide."
                    if valores[d] == "NAO_APLICAVEL"
                    else f"Estado consolidado da dimensão {d}."
                ),
                "dono": "gerente" if d in ("EVIDENCIA", "SIMPLICIDADE") else "agente",
            }
            for d in DIMENSIONS
        ],
        "option_sets": [option_set()] if with_options else [],
        "delegated_dependencies": [
            delegated_dependency(),
            delegated_dependency("departamento-desenvolvimento"),
        ],
        "capability_gaps": gaps or [],
        "gates": {
            "cobertura": True,
            "opcoes": True,
            "consistencia": True,
            "decisao": True,
            "fronteira": True,
            "documentacao": True,
            "evidencia": True,
        },
        "evidence_refs": ["evidencia/decisoes-cobranca.md"],
        "pending": [
            "R6 — a existência das tarefas não é verificável pelo runtime; emissão anexada."
        ],
        "entrega": entrega,
        "return_to": "diretor-de-lentes",
        "recorded_at": "2026-07-27T00:10:00-03:00",
    }


def derive_department_return(ledger: dict[str, Any]) -> dict[str, Any]:
    """Converte o ARCHITECTURE_LEDGER no envelope que o Diretor consome."""
    return {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "department-return-011",
        "causal": copy.deepcopy(ledger["causal"]),
        "department_mission_ref": ledger["department_mission_ref"],
        "returned_by": DEPARTMENT,
        "state": "RETURNED",
        "scope_touched": ["Estrutura macro do domínio de cobrança."],
        "artifact_refs": ["arquitetura/pacote-cobranca.md"],
        "evidence_refs": ledger["evidence_refs"],
        "candidate_digest": digest("a"),
        "test_summary": {
            "pass": 0,
            "fail": 0,
            "skip": 0,
            "skip_reasons": [],
            "critical_fail": False,
        },
        "pending_refs": [f"pending/{i:02d}" for i in range(len(ledger["pending"]))],
        "dissent_refs": [],
        "returned_to": "diretor-de-lentes",
        "returned_at": "2026-07-27T00:15:00-03:00",
    }


# --------------------------------------------------------------------------
# Verificações de pacote
# --------------------------------------------------------------------------

def validate_structure() -> list[str]:
    errors = validate_required_files(
        [
            SKILL_PATH,
            CONTRACT_PATH,
            OPENAI_PATH,
            SCHEMA_PATH,
            EVALS_PATH,
            PACKAGE_ROOT / "evals" / "PLACAR.md",
            PACKAGE_ROOT / "references" / "protocolo-de-arquitetura.md",
            PACKAGE_ROOT / "references" / "fronteiras-com-dados-e-desenvolvimento.md",
            PACKAGE_ROOT / "references" / "dimensoes-da-entrega.md",
            PACKAGE_ROOT / "references" / "origem-migracao.md",
            PACKAGE_ROOT
            / "references"
            / "adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md",
        ],
        "arquivo local",
    )
    errors.extend(
        validate_required_files(
            [
                DIRECTOR_SCHEMA_PATH,
                CEO_SCHEMA_PATH,
                RULES_PATH,
                DIRECTOR_ROOT / "SKILL.md",
                STRUCTURE_ROOT / "ORGANOGRAMA.md",
                STRUCTURE_ROOT / "GUIA-DE-EXPANSAO-E-MIGRACAO.md",
                STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
            ],
            "vínculo externo",
        )
    )
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
        validate_openai_yaml(
            OPENAI_PATH, "Departamento de Arquitetura de Software", f"${DEPARTMENT}"
        )
    )
    displays = {
        "agente-drivers-e-restricoes": "Drivers e Restrições",
        "agente-modularidade-e-limites": "Modularidade e Limites",
        "agente-integracoes-e-contratos": "Integrações e Contratos",
        "agente-qualidade-e-operacao": "Qualidade e Operação",
        "agente-alternativas-e-tradeoffs": "Alternativas e Trade-offs",
        "agente-adr-e-c4": "ADR e C4",
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
    for token in [
        "diretor-de-lentes",
        "departamento-arquitetura-dados",
        "departamento-desenvolvimento",
        "departamento-juizes",
        "ARCHITECTURE_TASK",
        "OPTION_SET",
        "delegated_dependenc",
        "Jeremias",
    ]:
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
    """ADR-006, decisão 1: aqui não se pontua nem se dá veredito."""
    found: set[str] = set()
    collect_property_names(schema, found)
    offenders = sorted(found.intersection(FORBIDDEN_SCORING))
    return (
        [f"schema contém campo de julgamento proibido pelo ADR-006: {offenders}"]
        if offenders
        else []
    )


def validate_scope_boundary(schema: dict[str, Any]) -> list[str]:
    """ADR-006, decisão 4: nem modelo de dados, nem implementação."""
    found: set[str] = set()
    collect_property_names(schema, found)
    errors: list[str] = []
    dados = sorted(found.intersection(FORBIDDEN_DATA))
    if dados:
        errors.append(f"schema invade o Departamento de Arquitetura de Dados: {dados}")
    codigo = sorted(found.intersection(FORBIDDEN_CODE))
    if codigo:
        errors.append(f"schema invade o Departamento de Desenvolvimento: {codigo}")
    return errors


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "architecturePlan",
        "architectureTask",
        "architectureReturn",
        "optionSet",
        "architectureCapabilityGap",
        "architectureLedger",
    }
    missing = expected.difference(schema.get("$defs", {}))
    if missing:
        errors.append(f"schema sem defs: {sorted(missing)}")
    worker_enum = schema.get("$defs", {}).get("workerId", {}).get("enum", [])
    if sorted(worker_enum) != sorted(AGENT_NAMES):
        errors.append(f"workerId divergente das pastas de agentes/: {worker_enum}")
    dimension_enum = schema.get("$defs", {}).get("dimension", {}).get("enum", [])
    if dimension_enum != DIMENSIONS:
        errors.append(f"as oito dimensões do schema divergem da referência: {dimension_enum}")
    return errors


def validate_director_contract() -> list[str]:
    if not DIRECTOR_SCHEMA_PATH.is_file():
        return ["schema do Diretor ausente"]
    director = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8")).get("$defs", {})
    errors: list[str] = []
    operacionais = director.get("operationalDepartment", {}).get("enum", [])
    if DEPARTMENT not in operacionais:
        errors.append("o Diretor não reconhece este Departamento como operacional")
    for vizinho in ("departamento-arquitetura-dados", "departamento-desenvolvimento"):
        if vizinho not in operacionais:
            errors.append(f"o Diretor não reconhece o vizinho {vizinho}")
    if not find_const(director.get("departmentMission", {}), "return_to", "diretor-de-lentes"):
        errors.append("a missão departamental deve retornar ao Diretor")
    if not find_const(director.get("departmentJudgeReport", {}), "producer", "departamento-juizes"):
        errors.append("pontuar continua sendo dos Juízes: contrato alterado")
    return errors


def validate_evals() -> list[str]:
    errors: list[str] = []
    evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    if evals.get("skill") != DEPARTMENT:
        errors.append("evals: skill incorreta")
    cases = evals.get("cases", [])
    if len(cases) < 12:
        errors.append(f"evals: necessários ao menos 12 casos, há {len(cases)}")
    if not any(c.get("origem") == "real" for c in cases):
        errors.append("evals: falta caso de origem real")
    if len({c["id"] for c in cases}) != len(cases):
        errors.append("evals: id duplicado")
    for c in cases:
        if f"${DEPARTMENT}" in c["prompt"]:
            errors.append(f"evals: {c['id']} nomeia a skill no prompt")
        if len(c.get("assertions", [])) < 3:
            errors.append(f"evals: {c['id']} com menos de 3 assertions")

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

def run() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    director_schema = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))

    cases: list[tuple[str, bool, list[str]]] = []

    cases.append(("pacote, seis agentes e vínculos externos", True, validate_structure()))
    cases.append(("metadata da gerente e dos seis agentes", True, validate_metadata()))
    cases.append(("fonte normativa única e tokens de contrato", True, validate_normative_source()))
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
    cases.append(("schema interno, workerId e dimensões", True, validate_schema_shape(schema)))
    cases.append(("ADR-006: sem nota nem veredito no schema", True, validate_no_scoring(schema)))
    cases.append(("ADR-006: sem modelo de dados nem código no schema", True, validate_scope_boundary(schema)))
    cases.append(("contrato do Diretor reconhece o Departamento", True, validate_director_contract()))
    cases.append(("catálogo de evals", True, validate_evals()))

    fixtures = [
        ("ARCHITECTURE_PLAN", architecture_plan()),
        ("ARCHITECTURE_TASK de drivers", architecture_task()),
        ("ARCHITECTURE_TASK de ADR/C4", architecture_task("agente-adr-e-c4")),
        ("ARCHITECTURE_RETURN de drivers", architecture_return("DRIVERS")),
        ("ARCHITECTURE_RETURN de modularidade", architecture_return("MODULARIDADE")),
        ("ARCHITECTURE_RETURN de integração", architecture_return("INTEGRACAO")),
        ("ARCHITECTURE_RETURN de qualidade", architecture_return("QUALIDADE")),
        ("ARCHITECTURE_RETURN de alternativas", architecture_return("ALTERNATIVAS")),
        ("ARCHITECTURE_RETURN de ADR/C4", architecture_return("ADR_C4")),
        ("OPTION_SET com duas opções", option_set()),
        ("ARCHITECTURE_CAPABILITY_GAP", capability_gap()),
        ("ARCHITECTURE_LEDGER", architecture_ledger()),
    ]
    for label, fixture in fixtures:
        cases.append((f"schema aceita {label}", True, validate_schema(fixture, schema, schema)))

    # --- tarefa: ótica, escopo e trava --------------------------------------

    wrong_worker = architecture_task()
    wrong_worker["worker_id"] = "agente-adr-e-c4"
    cases.append(
        ("tarefa rejeita ótica trocada para o kind", False,
         validate_schema(wrong_worker, schema, schema))
    )

    no_scope_out = architecture_task()
    no_scope_out["scope_out"] = []
    cases.append(
        ("tarefa exige scope_out literal", False,
         validate_schema(no_scope_out, schema, schema))
    )

    adr_early = architecture_task("agente-adr-e-c4")
    adr_early["wave"] = 1
    cases.append(
        ("ADR/C4 não roda antes da decisão fechada", False,
         validate_schema(adr_early, schema, schema))
    )

    leaky = architecture_task()
    leaky["forbidden_context"] = ["rodada anterior", "histórico", "outro time", "prazo"]
    cases.append(
        ("tarefa exige proibir conclusão esperada e favoritismo", False,
         validate_schema(leaky, schema, schema))
    )

    wrong_return = architecture_task()
    wrong_return["return_to"] = "diretor-de-lentes"
    cases.append(
        ("tarefa rejeita retorno fora da gerente", False,
         validate_schema(wrong_return, schema, schema))
    )

    # --- retorno: carga por ótica -------------------------------------------

    one_option = architecture_return("ALTERNATIVAS")
    one_option["options"] = [option_item()]
    cases.append(
        ("alternativas com uma opção só é rejeitada", False,
         validate_schema(one_option, schema, schema))
    )

    no_loss = architecture_return("ALTERNATIVAS")
    no_loss["options"][0]["perde"] = []
    cases.append(
        ("opção sem o que perde é rejeitada", False,
         validate_schema(no_loss, schema, schema))
    )

    happy_path = architecture_return("INTEGRACAO")
    happy_path["contracts"][0]["modo_de_falha"] = "ok"
    cases.append(
        ("contrato só com caminho feliz é rejeitado", False,
         validate_schema(happy_path, schema, schema))
    )

    unowned = architecture_return("MODULARIDADE")
    unowned["modules"][0]["data_ownership"] = ""
    cases.append(
        ("módulo sem dono de dado é rejeitado", False,
         validate_schema(unowned, schema, schema))
    )

    vague_driver = architecture_return("DRIVERS")
    vague_driver["drivers"][0]["como_se_mede"] = ""
    cases.append(
        ("driver sem como_se_mede é rejeitado", False,
         validate_schema(vague_driver, schema, schema))
    )

    accepted_adr = architecture_return("ADR_C4")
    accepted_adr["adr_c4"]["adr_estado"] = "aceita"
    cases.append(
        ("ADR nasce proposta, nunca aceita", False,
         validate_schema(accepted_adr, schema, schema))
    )

    mute_discard = architecture_return("ADR_C4")
    mute_discard["adr_c4"]["alternativas_descartadas"] = []
    cases.append(
        ("ADR exige alternativa descartada com motivo", False,
         validate_schema(mute_discard, schema, schema))
    )

    blocked = architecture_return("ADR_C4", status="BLOCKED")
    cases.append(
        ("retorno BLOCKED com motivo é válido", True,
         validate_schema(blocked, schema, schema))
    )

    blocked_mute = architecture_return("ADR_C4", status="BLOCKED")
    blocked_mute.pop("blocked_reason")
    cases.append(
        ("retorno BLOCKED exige motivo declarado", False,
         validate_schema(blocked_mute, schema, schema))
    )

    # --- fronteira: dependências delegadas -----------------------------------

    spike_no_rule = architecture_return("ALTERNATIVAS")
    spike_no_rule["delegated_dependencies"] = [delegated_dependency("departamento-desenvolvimento")]
    spike_no_rule["delegated_dependencies"][0]["decision_rule"] = "medir"
    cases.append(
        ("spike delegado sem regra de decisão é rejeitado", False,
         validate_schema(spike_no_rule, schema, schema))
    )

    bad_target = architecture_return("MODULARIDADE")
    bad_target["delegated_dependencies"][0]["target"] = "departamento-juizes"
    cases.append(
        ("dependência não se delega aos Juízes", False,
         validate_schema(bad_target, schema, schema))
    )

    no_constraint = architecture_return("MODULARIDADE")
    no_constraint["delegated_dependencies"][0]["architectural_constraint"] = ""
    cases.append(
        ("dependência de dados exige a restrição arquitetural", False,
         validate_schema(no_constraint, schema, schema))
    )

    # --- OPTION_SET -----------------------------------------------------------

    cases.append(
        ("opção única com justificativa verificável é aceita", True,
         validate_schema(
             option_set(1, "As demais caem por restrição de licença já contratada até 2029."),
             schema, schema))
    )
    cases.append(
        ("opção única sem justificativa é rejeitada", False,
         validate_schema(option_set(1, "n/a"), schema, schema))
    )
    cases.append(
        ("duas opções com justificativa pendurada é rejeitada", False,
         validate_schema(option_set(2, "sobrou justificativa de opção única"), schema, schema))
    )
    no_rec_loss = option_set()
    no_rec_loss["recomendacao_perde"] = []
    cases.append(
        ("recomendação sem perda declarada é rejeitada", False,
         validate_schema(no_rec_loss, schema, schema))
    )

    # --- livro-razão ----------------------------------------------------------

    missing_dimension = architecture_ledger()
    missing_dimension["dimensions"].pop()
    cases.append(
        ("livro-razão exige as oito dimensões", False,
         validate_schema(missing_dimension, schema, schema))
    )

    absent = architecture_ledger(estados={**{d: "COBERTA" for d in DIMENSIONS}, "QUALIDADE": "AUSENTE"})
    cases.append(
        ("entrega com dimensão AUSENTE é rejeitada", False,
         validate_schema(absent, schema, schema))
    )

    lazy_na = architecture_ledger(estados={**{d: "COBERTA" for d in DIMENSIONS}, "INTEGRACAO": "NAO_APLICAVEL"})
    lazy_na["dimensions"] = [
        {**d, "razao": "nao se aplica"} if d["dimension"] == "INTEGRACAO" else d
        for d in lazy_na["dimensions"]
    ]
    cases.append(
        ("NAO_APLICAVEL genérico é rejeitado", False,
         validate_schema(lazy_na, schema, schema))
    )

    with_gap = architecture_ledger(gaps=[capability_gap()])
    cases.append(
        ("entrega com lacuna aberta é rejeitada", False,
         validate_schema(with_gap, schema, schema))
    )

    no_assignments = architecture_ledger(with_assignments=False)
    cases.append(
        ("entrega sem registro de emissão é rejeitada (R6)", False,
         validate_schema(no_assignments, schema, schema))
    )

    no_options = architecture_ledger(with_options=False)
    cases.append(
        ("entrega sem conjunto de opções é rejeitada", False,
         validate_schema(no_options, schema, schema))
    )

    open_gate = architecture_ledger()
    open_gate["gates"]["fronteira"] = False
    cases.append(
        ("entrega com gate de fronteira vermelho é rejeitada", False,
         validate_schema(open_gate, schema, schema))
    )

    no_r6 = architecture_ledger()
    no_r6["pending"] = ["fingerprint residual anotado"]
    cases.append(
        ("livro-razão exige R6 nomeado em pending", False,
         validate_schema(no_r6, schema, schema))
    )

    forged = architecture_ledger()
    forged["causal"]["producer"] = "departamento-desenvolvimento"
    cases.append(
        ("livro-razão rejeita produtor forjado", False,
         validate_schema(forged, schema, schema))
    )

    # --- fronteira com o consumidor -------------------------------------------

    ledger = architecture_ledger()
    cases.append(
        ("Diretor aceita o DEPARTMENT_RETURN produzido", True,
         validate_schema(derive_department_return(ledger), director_schema, director_schema))
    )

    spoofed = derive_department_return(ledger)
    spoofed["causal"]["producer"] = "departamento-arquitetura-dados"
    cases.append(
        ("Diretor rejeita retorno com produtor forjado", False,
         validate_schema(spoofed, director_schema, director_schema))
    )

    # --- regras recalculadas em código ----------------------------------------

    derived = derive_department_return(ledger)
    checks = [
        ("duas opções dispensam justificativa", option_set_valido(2, "n/a")),
        ("três opções são aceitas", option_set_valido(3, "n/a")),
        ("quatro opções não são um conjunto", not option_set_valido(4, "n/a")),
        ("opção única exige justificativa longa",
         not option_set_valido(1, "só tem esse jeito")
         and option_set_valido(1, "As demais caem por restrição de licença contratada até 2029.")),
        ("recomendação sem perda é inválida",
         not recomendacao_valida([]) and recomendacao_valida(["escala independente"])),
        ("spike sem regra de decisão é inválido",
         not delegacao_valida("departamento-desenvolvimento", "medir")
         and delegacao_valida("departamento-desenvolvimento",
                              "Acima de 800 ms no p95, a opção de dois serviços cai.")),
        ("dependência de dados não exige regra de decisão",
         delegacao_valida("departamento-arquitetura-dados", "n/a")),
        ("dimensão AUSENTE impede entrega",
         not pode_entregar({**{d: "COBERTA" for d in DIMENSIONS}, "QUALIDADE": "AUSENTE"},
                           {g: True for g in ("cobertura", "opcoes", "consistencia", "decisao",
                                              "fronteira", "documentacao", "evidencia")}, 0)),
        ("gate de fronteira vermelho impede entrega",
         not pode_entregar({d: "COBERTA" for d in DIMENSIONS},
                           {"cobertura": True, "opcoes": True, "consistencia": True,
                            "decisao": True, "fronteira": False, "documentacao": True,
                            "evidencia": True}, 0)),
        ("lacuna aberta impede entrega",
         not pode_entregar({d: "COBERTA" for d in DIMENSIONS},
                           {g: True for g in ("cobertura", "opcoes", "consistencia", "decisao",
                                              "fronteira", "documentacao", "evidencia")}, 1)),
        ("tudo coberto e verde entrega",
         pode_entregar({d: "COBERTA" for d in DIMENSIONS},
                       {g: True for g in ("cobertura", "opcoes", "consistencia", "decisao",
                                          "fronteira", "documentacao", "evidencia")}, 0)),
        ("acúmulo alternativas × ADR é proibido",
         acumulo_proibido("ALTERNATIVAS", "ADR_C4")),
        ("acúmulo modularidade × integração é proibido",
         acumulo_proibido("MODULARIDADE", "INTEGRACAO")),
        ("acúmulo drivers × qualidade é permitido",
         not acumulo_proibido("DRIVERS", "QUALIDADE")),
        ("retorno da Arquitetura não conta teste executado",
         derived["test_summary"] == {"pass": 0, "fail": 0, "skip": 0,
                                     "skip_reasons": [], "critical_fail": False}),
        ("as seis óticas cobrem as seis primeiras dimensões",
         sorted(AGENT_KIND.values()) == sorted(DIMENSIONS[:6])),
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

    # --- Gabaritos da documentação validam contra o próprio schema -----------
    # Achado do forward de 2026-07-26: três instâncias independentes reportaram
    # que as Regras D e S da referência produziam artefato que o schema recusa.
    # O validador conferia o schema e conferia os links, mas nunca conferiu se o
    # exemplo em prosa era válido — o vão entre duas verificações corretas.
    import re as _re
    fronteiras = (PACKAGE_ROOT / "references"
                  / "fronteiras-com-dados-e-desenvolvimento.md").read_text(encoding="utf-8")
    dep_def = schema["$defs"]["delegatedDependency"]
    obrigatorios = set(dep_def["required"])
    permitidos = set(dep_def["properties"])
    erros_gabarito: list[str] = []
    blocos = _re.findall(r"delegated_dependency:\s*\n((?:\s{2}\w+:.*\n)+)", fronteiras)
    if not blocos:
        erros_gabarito.append("nenhum gabarito de delegated_dependency na referência")
    for i, bloco in enumerate(blocos, 1):
        campos = set(_re.findall(r"^\s{2}(\w+):", bloco, flags=_re.MULTILINE))
        faltando = obrigatorios - campos
        sobrando = campos - permitidos
        if faltando:
            erros_gabarito.append(f"gabarito {i}: falta obrigatório {sorted(faltando)}")
        if sobrando:
            erros_gabarito.append(f"gabarito {i}: campo inexistente no schema {sorted(sobrando)}")
    cases.append(("gabaritos de delegated_dependency da referência batem com o schema",
                  True, erros_gabarito))

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
