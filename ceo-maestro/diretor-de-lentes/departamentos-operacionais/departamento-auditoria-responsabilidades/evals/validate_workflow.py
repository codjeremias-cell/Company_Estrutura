"""Validador determinístico do Departamento de Auditoria e Responsabilidades.

Verifica o pacote (arquivos, metadata, links), o schema interno, os artefatos
internos e — como regressão de fronteira — que os envelopes produzidos são
aceitos pelos schemas do `diretor-de-lentes` e do `ceo-maestro`.

Uso: python evals/validate_workflow.py
"""

from __future__ import annotations

import ast
import contextlib
import copy
import io
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = PACKAGE_ROOT / "SKILL.md"
SCRIPTS_ROOT = PACKAGE_ROOT / "scripts"
ENGINE_PATH = SCRIPTS_ROOT / "inspecao_executada.py"
EMITTER_PATH = SCRIPTS_ROOT / "emitir_governanca.py"
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
sys.path.insert(0, str(SCRIPTS_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        collect_property_names,
        conferir_digest_das_regras,
        digest,
        find_const,
        json_pointer,
        sha256_file,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        candidate_digest_de_arvore,
        conferir_manifesto_do_candidato,
        conferir_candidate_digest,
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
        validate_placar_nao_declara_cadeia,
        validate_contagem_ligada_ao_instrumento,
        validate_travas_compartilhadas_com_efeito,
        validate_pendencia_tem_dono,
        validate_sem_check_tautologico,
        validate_trava_de_digest,
    )
    # Motor da inspeção executada. Autoridade ÚNICA da consolidação: o emissor
    # real (`scripts/emitir_governanca.py`) e este validador leem daqui, e não
    # existe segunda cópia das regras de estado, gravidade e veredito. Duas
    # cópias divergem em silêncio, e foi assim que a tabela por pacote da tarefa
    # 14 mostrou verde onde o artefato cru estava vermelho.
    from inspecao_executada import (  # noqa: E402
        ESTADOS_QUE_EXIGEM_ANCORA,
        auditar_ledger_contra_evidencia,
    # RODADA 7 — a junção que confronta o nome declarado com as missões em disco,
    # e o estado nomeado que ela produz. O estado desce da MESMA constante que o
    # emissor importa: segunda cópia de string diverge da primeira em silêncio.
        resolver_evidence_refs,
        conferir_metodo,
        consolidar_inspecao,
        ALEGACAO_DO_COMPLIANT,
    NAO_COBERTO_PELA_ALEGACAO,
    contar_ancoras_declaradas,
        contar_itens_do_contrato,
        cruzar_identidade_dos_recibos,
        decidir_veredito,
        derivar_binario,
        estado_efetivo,
        estado_mais_grave,
        reverificar_ancora,
        sha256_de_arquivo,
        verificar_inspecao_executada,
    )
    # O emissor real é IMPORTADO por este validador, e não apenas lido como
    # texto. Duas travas da rodada 2 exigem chamá-lo de verdade: a conferência de
    # identidade tem três desfechos e cada um é um caso, e o caminho documentado
    # é executado como subprocesso. Ler o fonte prova forma; chamar prova efeito.
    import emitir_governanca  # noqa: E402
    from emitir_governanca import (  # noqa: E402
        conferir_identidade_do_candidato,
        resolver_raiz_do_candidato,
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

# Antes destas linhas o validador reimplementava a consolidação. Duas cópias da
# mesma regra é como um resumo passa a mostrar verde enquanto o bruto está
# vermelho: nada obriga as duas a concordarem. Agora as três funções são
# **apelidos** do motor — se o motor mudar, este validador muda junto ou quebra.
worst_state = estado_mais_grave
decide_verdict = decidir_veredito
to_governance = derivar_binario


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
        "producer_digest_recipe": (
            "_compartilhado/validador_schema.py::sha256_file sobre o SKILL.md do produtor"
        ),
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


# --------------------------------------------------------------------------
# Âncoras REAIS — as fixtures apontam para arquivos que existem no pacote
# --------------------------------------------------------------------------
#
# Âncora sintética passaria no schema e não exercitaria a reabertura, que é a
# trava inteira. Estas apontam para o contrato do próprio Departamento, com
# linha, citação e digest recomputados agora: se o arquivo mudar, a fixture
# acompanha; se a função de reabertura quebrar, o caso cai.

def _primeira_linha_util(caminho: Path, minimo: int = 20) -> tuple[int, str]:
    """Primeira linha com conteúdo suficiente para ancorar, e o número dela."""
    for numero, linha in enumerate(
        caminho.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if len(linha.strip()) >= minimo:
            return numero, linha.strip()
    raise RuntimeError(f"sem linha ancorável em {caminho}")


def ancora_real(
    caminho: Path = CONTRACT_PATH,
    evidence_ref: str = "evidence-01",
) -> dict[str, Any]:
    numero, texto = _primeira_linha_util(caminho)
    return {
        "evidence_ref": evidence_ref,
        "artifact_ref": caminho.relative_to(STRUCTURE_ROOT).as_posix(),
        "line": numero,
        "quote": texto[:120],
        "file_digest": sha256_de_arquivo(caminho),
    }


def metodo_real(auditor: str) -> dict[str, Any]:
    """O contrato do agente como MÉTODO, com as contagens lidas do documento."""
    contrato = AGENTS_ROOT / auditor / "CONTRATO-DE-COMPROMISSO.md"
    texto = contrato.read_text(encoding="utf-8")
    return {
        "role_of": auditor,
        "executed_by": DEPARTMENT,
        "execution_mode": "PAPEL_SOB_PORTA_UNICA",
        "agent_contract_ref": contrato.relative_to(STRUCTURE_ROOT).as_posix(),
        "agent_contract_digest": sha256_de_arquivo(contrato),
        "obrigacoes_declaradas": contar_itens_do_contrato(texto, "Obrigações"),
        "barreira_de_saida_declarada": contar_itens_do_contrato(
            texto, "Barreira de saída"
        ),
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
        "evidence_anchors": [] if state == "NAO_PROVADO" else [ancora_real()],
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
        "method": metodo_real(auditor),
        "review_chain": {
            "context_clean": True,
            "independent": True,
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


def method_execution(name: str) -> dict[str, Any]:
    metodo = metodo_real(name)
    return {
        "task_id": f"task-{name}",
        "auditor_id": name,
        "capability": AGENT_CAPABILITY[name],
        "execution_mode": metodo["execution_mode"],
        "agent_contract_ref": metodo["agent_contract_ref"],
        "agent_contract_digest": metodo["agent_contract_digest"],
        "executed_at": "2026-07-26T20:40:00-03:00",
        "destination": f"auditoria/recibos/task-{name}.json",
    }


# RODADA 8 — a raiz da fixture e uma subarvore VIVA, nao um pacote de
# candidato entregue: ela nao tem manifest.json, e o estado disso e nomeado.
MOTIVO_DO_MANIFESTO_NA_FIXTURE = (
    "a raiz desta fixture nao e pacote de candidato entregue e nao traz"
    " manifest.json: nada foi conferido, e ausencia permanece ausencia"
)


def candidate_identity(
    status: str = "CONFERIDO",
    source: str = "rodada.json::candidate_root",
) -> dict[str, Any]:
    """O resultado da conferência de identidade, como ele entra no ledger.

    `NAO_CONFERIDO` carrega `n/a` e `ausente` por exigência do schema: um estado
    que declara "não recomputei" não pode exibir a raiz sobre a qual teria
    recomputado.
    """
    if status == "NAO_CONFERIDO":
        return {
            "status": "NAO_CONFERIDO",
            "candidate_root_ref": "n/a",
            "source": "ausente",
            "recipe": "_compartilhado/verificacoes_pacote.py::digest_de_arvore",
            "recomputed_digest": "n/a",
            "reason": (
                "identidade NAO conferida: a rodada não declara candidate_root e"
                " nenhuma raiz do candidato foi passada; nada foi recomputado"
            ),
            "checked_at": "2026-07-26T21:05:00-03:00",
            "manifest_status": "SEM_MANIFESTO",
            "manifest_reason": MOTIVO_DO_MANIFESTO_NA_FIXTURE,
        }
    return {
        "status": status,
        "candidate_root_ref": "departamento-auditoria-responsabilidades",
        "source": source,
        "recipe": "_compartilhado/verificacoes_pacote.py::digest_de_arvore",
        "recomputed_digest": digest("a"),
        "reason": (
            "identidade conferida: candidate_digest recomputado sobre a árvore"
            " aberta pela receita oficial e idêntico ao declarado"
        ),
        "checked_at": "2026-07-26T21:05:00-03:00",
        "manifest_status": "SEM_MANIFESTO",
        "manifest_reason": MOTIVO_DO_MANIFESTO_NA_FIXTURE,
    }


def inspection_verification(
    reverified: bool = True,
    anchors_failed: int = 0,
    methods_failed: int = 0,
) -> dict[str, Any]:
    return {
        "all_anchors_reverified": reverified,
        "anchors_total": 10,
        "anchors_failed": anchors_failed,
        "methods_total": 3,
        "methods_failed": methods_failed,
        "counted_by": "scripts/inspecao_executada.py::contar_ancoras_declaradas",
        "counted_limit": (
            "anchors_total e methods_total são CONTADOS dos recibos em disco;"
            " anchors_failed e methods_failed vêm da reabertura e têm origem"
            " única — não há segunda medida que os confronte"
        ),
        "verified_by": "scripts/inspecao_executada.py::verificar_inspecao_executada",
        "verified_at": "2026-07-26T21:05:00-03:00",
    }




# ---------------------------------------------------------------------------
# RODADA 7, OI6-01 — OS QUATRO LIMITES RESIDUAIS, POR IGUALDADE EXATA
# ---------------------------------------------------------------------------
#
# O que estava medido, e o que o proprio comentario do codigo ja dizia
# --------------------------------------------------------------------
# Dos ONZE limites que o envelope carrega, SETE (`declared_limits`) eram
# exigidos por `id` com `const`/`enum` — igualdade exata — e QUATRO (`pending`:
# R6, R9, R10, R11) por PREFIXO ABERTO. `OI6-01` mediu a assimetria: a lista
# `["R6 x", "R9 x", "R10 x", "R11 x"]` atravessava o schema E esta barreira, e
# `"R6 "` sozinho tambem.
#
# O mais duro do achado nao e o buraco: e que o comentario ao lado do proprio
# `IDS_DOS_LIMITES_DE_B`, logo acima, JA DIAGNOSTICAVA o mecanismo como quebrado
# — "sob ela o texto vigente, o texto RETIRADO e um 'R6 — qualquer coisa' eram
# indistinguiveis" (`OI5-08`) — e o mantinha vivo para os quatro. O diagnostico
# correto convivia com o defeito porque estava em PROSA e nao em codigo. E isso
# que acaba aqui.
#
# Os quatro textos abaixo sao copia byte a byte das constantes
# `TEXTO_R6`, `TEXTO_R9`, `TEXTO_R10` e `TEXTO_R11` de
# `departamento-auditoria-responsabilidades/scripts/emitir_governanca.py`, e sao
# os mesmos `const` dos dois schemas — a mesma disciplina de tres lugares que
# `ALEGACAO_DO_COMPLIANT` ja usava. Alargar um limite passa a exigir tres
# edicoes, e uma so derruba a barreira.
TEXTO_R6 = (
    'R6 — a existência do painel auditor não é verificável pelo runtime; sob porta única a inspeção é executada em papel pela gerente. A âncora NÃO impede a fabricação, e o custo dela está medido: recibos íntegros que reabrem foram forjados em 80 linhas e 0,031 s, com 1 tentativa (OI-04, 2026-08-02).'
)
TEXTO_R9 = (
    'R9 — a âncora prova que UM arquivo da raiz auditada foi reaberto na versão declarada; ela NÃO liga a dimensão ao artefato que deveria sustentá-la. Pertinência de evidência é mérito, e mérito é dos Juízes (R5). (Este limite viajava como R8 até a rodada 3, e colidia com o R8 do §7, bypass para fora.)'
)
TEXTO_R10 = (
    'R10 — nada assina este envelope. Edição do arquivo posterior à gravação é invisível ao emissor E ao validador, e o consumidor pode ler um veredito que o emissor não produziu. A defesa correspondente é o CONSUMIDOR recomputar o envelope a partir do ledger e do candidato, e ela mora fora deste pacote. Medido pela sonda S14-ENVELOPE-EDITADO.'
)
TEXTO_R11 = (
    "R11 — TETO DO MÉTODO: forjar a evidência é chamar as mesmas funções que "
    "a verificam. Derivar da evidência protege contra valor DIGITADO; não "
    "protege contra quem CHAMA o derivador, porque atacante e verificador "
    "compartilham o código, o processo e a árvore. Medido por origem "
    "independente em 2026-08-02 (OI-04): 80 linhas, 0,031 s, 1 tentativa, 4 "
    "arquivos lidos, zero conhecimento do conteúdo auditado. Fechar isto "
    "exige âncora externa ao pacote — runtime separado, assinatura fora da "
    "árvore ou terceiro que não compartilhe o processo — e não cabe no "
    "runtime atual. Este envelope NÃO carrega defesa contra isto e não obriga "
    "nenhuma: a origem independente dos casos foi retirada do envelope na "
    "rodada 8, e o limite permanece ABERTO."
)
TEXTO_DE_CADA_LIMITE = {
    "R6": TEXTO_R6,
    "R9": TEXTO_R9,
    "R10": TEXTO_R10,
    "R11": TEXTO_R11,
}





def audit_ledger(
    states: dict[str, str] | None = None,
    gaps: list[dict[str, Any]] | None = None,
    with_assignments: bool = True,
    dossier_missing: list[str] | None = None,
    with_methods: bool = True,
    verification: dict[str, Any] | None = None,
    identity: dict[str, Any] | None = None,
    claim: dict[str, Any] | None = None,
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
        "method_executions": (
            [method_execution(name) for name in AGENT_NAMES] if with_methods else []
        ),
        "candidate_identity": identity or candidate_identity(),
        # RODADA 5 — a alegação e a origem independente são campos do ledger.
        # A alegação sai das CONSTANTES do módulo da trava, aqui como no
        # emissor: fixture que digitasse o texto mediria o schema contra uma
        # segunda fonte, e as duas divergiriam no primeiro ajuste.
        "compliance_claim": claim or {
            "certifies": ALEGACAO_DO_COMPLIANT,
            "does_not_certify": NAO_COBERTO_PELA_ALEGACAO,
            "ceiling_ref": "R11",
            "source": "scripts/inspecao_executada.py::ALEGACAO_DO_COMPLIANT",
        },
        "inspection_verification": verification or inspection_verification(),
        "panel": [
            {
                "auditor_id": name,
                "capability": AGENT_CAPABILITY[name],
                "status": "COMPLETED",
                "context_clean": True,
                "independent": True,
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
            TEXTO_R6,
            TEXTO_R9,
            TEXTO_R10,
            TEXTO_R11,
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
    conferido = ledger["candidate_identity"]["status"] == "CONFERIDO"
    return {
        "report_id": "governance-report-001",
        "auditor_ref": DEPARTMENT,
        "auditor_digest": PRODUCER,
        "candidate_digest": (
            ledger["candidate_identity"]["recomputed_digest"]
            if conferido
            else ledger["causal"]["candidate_digest"]
        ),
        "candidate_identity_status": ledger["candidate_identity"]["status"],
        "candidate_manifest_status": ledger["candidate_identity"]["manifest_status"],
        # T71 — DERIVADO do painel, nunca digitado. O `if` do painel vazio é a
        # armadilha, não a defesa: `all([])` é True, e sem ele um ledger sem
        # inspetor nenhum sairia INDEPENDENTE.
        "panel_independence_status": (
            "INDEPENDENTE"
            if ledger["panel"]
            and all(bool(item.get("independent")) for item in ledger["panel"])
            else "NAO_INDEPENDENTE"
        ),
        "candidate_digest_source": (
            "RECOMPUTADO" if conferido else "DECLARADO_NAO_CONFERIDO"
        ),
        "contract_digest": ledger["causal"]["contract_digest"],
        "rules_digest": RULES_DIGEST,
        "verdict": ledger["governance_verdict"],
        "violations": ledger["violations"],
        "evidence_refs": ledger["evidence_refs"],
        # RODADA 5 — a alegação e o estado da origem viajam em campo próprio.
        "compliance_claim": ledger["compliance_claim"],
        # Os QUATRO limites viajam com o envelope que a barreira lê — e são os
        # do ledger, não uma segunda lista digitada aqui.
        "pending": ledger["pending"],
        "issued_at": "2026-07-26T21:10:00-03:00",
    }


def derive_department_return(ledger: dict[str, Any]) -> dict[str, Any]:
    """Converte o AUDIT_LEDGER interno no envelope que o Diretor consome."""
    causal_header = copy.deepcopy(ledger["causal"])
    # RODADA 8, LIMITE DECLARADO — o schema do Diretor ainda não conhece
    # `producer_digest_recipe`, e recusa campo fora do schema. Alcance da
    # receita normativa nesta rodada: 3 dos 16 schemas de pacote.
    causal_header.pop("producer_digest_recipe", None)
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
        PACKAGE_ROOT / "references" / "adr-017-inspecao-em-papel-sob-porta-unica.md",
        ENGINE_PATH,
        EMITTER_PATH,
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


def _funcao(arvore: ast.AST, nome: str) -> ast.FunctionDef | None:
    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name == nome:
            return no
    return None


def _nomes(no: ast.AST) -> set[str]:
    """Todo identificador mencionado numa expressão."""
    return {n.id for n in ast.walk(no) if isinstance(n, ast.Name)}


def _alvos(no: ast.AST) -> set[str]:
    """Nomes que uma atribuição liga — inclusive desempacotamento de tupla."""
    return {n.id for n in ast.walk(no) if isinstance(n, ast.Name)}


def _chamada_para(no: ast.AST, nome: str) -> ast.Call | None:
    for sub in ast.walk(no):
        if not isinstance(sub, ast.Call):
            continue
        alvo = sub.func
        if isinstance(alvo, ast.Name) and alvo.id == nome:
            return sub
        if isinstance(alvo, ast.Attribute) and alvo.attr == nome:
            return sub
    return None


def _propagar(
    corpo: list[ast.stmt],
    tingidos: set[str],
    origens: frozenset[str] = frozenset(),
) -> set[str]:
    """Propaga a marca de origem, em ordem de execução, por um corpo de função.

    **Esta função é o conserto do achado `A2`.** A versão da rodada 1 conferia o
    call site pelo NOME chamado: bastava `verificar_inspecao_executada` aparecer
    entre as chamadas do emissor. Manter a chamada e jogar o retorno fora
    produzia `COMPLIANT` com zero âncoras e o validador ficava 118/118 verde.

    A regra aqui tem três metades, e a terceira é a que importa:

    - uma atribuição cujo valor **chama uma origem** tinge o alvo;
    - uma atribuição cujo valor **menciona um nome tingido** tinge o alvo;
    - e qualquer outra atribuição ao mesmo nome o **limpa**.

    É a limpeza que faz a checagem valer. Reatribuir `relatorio` a um dicionário
    fabricado depois de chamar a trava mata a marca, e o consumo a jusante deixa
    de estar ligado à origem — que é exatamente a sonda `V09b` do julgamento.

    Ramos (`if`, `for`, `while`, `with`, `try`) são percorridos em sequência, com
    o mesmo conjunto. É estrito de propósito: uma limpeza escondida dentro de um
    ramo conta como limpeza.
    """
    def marca(valor: ast.AST) -> bool:
        if _nomes(valor) & tingidos:
            return True
        return any(_chamada_para(valor, origem) is not None for origem in origens)

    for no in corpo:
        if isinstance(no, ast.Assign):
            marcado = marca(no.value)
            for alvo in no.targets:
                for nome in _alvos(alvo):
                    if marcado:
                        tingidos.add(nome)
                    else:
                        tingidos.discard(nome)
        elif isinstance(no, ast.AnnAssign) and no.value is not None:
            marcado = marca(no.value)
            for nome in _alvos(no.target):
                if marcado:
                    tingidos.add(nome)
                else:
                    tingidos.discard(nome)
        elif isinstance(no, ast.AugAssign):
            if marca(no.value):
                tingidos |= _alvos(no.target)
        elif isinstance(no, ast.For):
            if marca(no.iter):
                tingidos |= _alvos(no.target)
            _propagar(no.body, tingidos, origens)
            _propagar(no.orelse, tingidos, origens)
        elif isinstance(no, (ast.If, ast.While)):
            _propagar(no.body, tingidos, origens)
            _propagar(no.orelse, tingidos, origens)
        elif isinstance(no, ast.With):
            _propagar(no.body, tingidos, origens)
        elif isinstance(no, ast.Try):
            _propagar(no.body, tingidos, origens)
            for tratador in no.handlers:
                _propagar(tratador.body, tingidos, origens)
            _propagar(no.orelse, tingidos, origens)
            _propagar(no.finalbody, tingidos, origens)
    return tingidos


def _mapa_do_dicionario(no: ast.Dict) -> dict[str, ast.AST]:
    mapa: dict[str, ast.AST] = {}
    for chave, valor in zip(no.keys, no.values):
        if isinstance(chave, ast.Constant) and isinstance(chave.value, str):
            mapa[chave.value] = valor
    return mapa


def _dicionario_devolvido(funcao: ast.FunctionDef) -> dict[str, ast.AST]:
    """Mapa chave -> nó de valor do dicionário que a função devolve.

    Segue três formas, e a segunda e a terceira foram acrescentadas na rodada 4:

    1. `return {...}` — o dicionário literal, direto;
    2. `bloco = {...}` … `return bloco` — resolve o nome até a atribuição;
    3. `return bloco, erros` — a tupla, resolvendo cada nome dela.

    Sem 2 e 3 uma função que monta o dicionário numa variável — que é como se
    escreve quando há validação antes do `return` — apareceria como "não devolve
    dicionário literal", e a conferência dos subcampos ficaria impossível de
    satisfazer sem piorar o código. A análise tem de alcançar a forma que a boa
    escrita produz; senão a trava empurra para a escrita ruim.
    """
    candidatos: list[ast.AST] = []
    for no in ast.walk(funcao):
        if not isinstance(no, ast.Return) or no.value is None:
            continue
        if isinstance(no.value, ast.Tuple):
            candidatos.extend(no.value.elts)
        else:
            candidatos.append(no.value)

    for candidato in candidatos:
        if isinstance(candidato, ast.Dict):
            return _mapa_do_dicionario(candidato)
    for candidato in candidatos:
        if not isinstance(candidato, ast.Name):
            continue
        for no in ast.walk(funcao):
            if (
                isinstance(no, ast.Assign)
                and isinstance(no.value, ast.Dict)
                and candidato.id in _alvos(no.targets[0])
            ):
                return _mapa_do_dicionario(no.value)
    return {}


def _descende_de(
    funcao: ast.FunctionDef,
    parametro: str,
    campos: tuple[str, ...],
    rotulo: str,
) -> list[str]:
    """Cada `campo` do dicionário devolvido tem de descender de `parametro`."""
    erros: list[str] = []
    tingidos = _propagar(funcao.body, {parametro})
    devolvido = _dicionario_devolvido(funcao)
    if not devolvido:
        return [f"{funcao.name} não devolve um dicionário literal: {rotulo}"]
    for campo in campos:
        if campo not in devolvido:
            erros.append(f"{funcao.name} não devolve o campo {campo} ({rotulo})")
            continue
        if not (_nomes(devolvido[campo]) & tingidos):
            erros.append(
                f"{funcao.name}: {campo} NÃO descende de {parametro} — o valor é"
                f" fabricado, não vem da trava ({rotulo})"
            )
    return erros


def _subcampos_descendem(
    funcao: ast.FunctionDef,
    parametro: str,
    campo: str,
    subcampos: tuple[str, ...],
) -> list[str]:
    """Cada subcampo de um bloco aninhado devolvido descende do parâmetro."""
    erros: list[str] = []
    tingidos = _propagar(funcao.body, {parametro})
    devolvido = _dicionario_devolvido(funcao)
    aninhado = devolvido.get(campo)
    if aninhado is None:
        return [f"{funcao.name} não devolve {campo}"]
    if isinstance(aninhado, ast.Name):
        # Devolvido por NOME. Resolver a atribuição que o construiu, dentro da
        # própria função, é o que a sonda `S11` obrigou a acrescentar: sem isso a
        # conferência ficava no nível do BLOCO, e trocar um subcampo por literal
        # — `"status": "CONFERIDO"` em vez de `identidade["status"]` — passava
        # verde, porque os outros subcampos mantinham o bloco ligado à origem.
        # Conferir o bloco e não o subcampo é a mesma classe de erro que conferir
        # o nome e não o uso.
        if not (_nomes(aninhado) & tingidos):
            return [
                f"{funcao.name}: {campo} NÃO descende de {parametro} — o bloco"
                " inteiro é fabricado"
            ]
        for no in ast.walk(funcao):
            if (
                isinstance(no, ast.Assign)
                and isinstance(no.value, ast.Dict)
                and aninhado.id in _alvos(no.targets[0])
            ):
                aninhado = no.value
                break
    if not isinstance(aninhado, ast.Dict):
        if not (_nomes(aninhado) & tingidos):
            return [
                f"{funcao.name}: {campo} NÃO descende de {parametro} — o bloco"
                " inteiro é fabricado"
            ]
        # BLOCO OPACO — rodada 4.
        #
        # Aqui a versão da rodada 3 devolvia `[]`, isto é, PASSAVA. O bloco
        # descendia do parâmetro **por menção**, os subcampos ficavam invisíveis
        # à análise, e "não consegui conferir" era registrado como "conferido".
        # Foi exatamente por esta porta que a lavagem interprocedural dos Juízes
        # entrou: `verificacao = consolidado["inspecao"]` mantém a marca e esconde
        # os números.
        #
        # A regra da rodada é que valor derivável não é aceito como declarado, e
        # que onde a derivação não alcança o campo carrega estado NOMEADO. Silêncio
        # não é estado nomeado. Bloco que a análise não abre passa a ser ERRO.
        return [
            f"{funcao.name}: {campo} é um BLOCO OPACO — descende de {parametro}"
            " por menção, mas a análise não alcança os subcampos"
            f" {list(subcampos)}. Conferência que não enxerga o subcampo não"
            " confere o subcampo: devolva um dicionário literal, ou o valor"
            " decidido pode ser fabricado dentro do intermediário"
        ]
    mapa = {
        chave.value: valor
        for chave, valor in zip(aninhado.keys, aninhado.values)
        if isinstance(chave, ast.Constant) and isinstance(chave.value, str)
    }
    for subcampo in subcampos:
        if subcampo not in mapa:
            erros.append(f"{funcao.name}: {campo} sem o subcampo {subcampo}")
            continue
        if not (_nomes(mapa[subcampo]) & tingidos):
            erros.append(
                f"{funcao.name}: {campo}.{subcampo} NÃO descende de {parametro}"
                " — número fabricado no lugar do que a trava mediu"
            )
    return erros


def _chamadas(arquivo: Path) -> set[str]:
    """Nomes efetivamente CHAMADOS no módulo, lidos da AST — não do texto.

    Busca por string acharia o nome num comentário, num docstring ou num import
    morto. `ast` só devolve o que está na posição de chamada.

    **Presença de chamada é necessária e insuficiente.** Continua aqui porque
    pega a remoção grosseira; o que decide é `validate_call_site`, que confere o
    FLUXO do resultado. Em 2026-08-01 os Juízes mostraram que só esta
    conferência deixava passar `COMPLIANT` com a trava chamada e o retorno
    descartado.
    """
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    nomes: set[str] = set()
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Call):
            continue
        alvo = no.func
        if isinstance(alvo, ast.Name):
            nomes.add(alvo.id)
        elif isinstance(alvo, ast.Attribute):
            nomes.add(alvo.attr)
    return nomes


def validate_call_site() -> list[str]:
    """Toda trava é chamada onde a decisão acontece — e o RESULTADO dela decide.

    O julgamento da tarefa 14 achou três travas que existiam, ficavam vermelhas
    sob mutação e **não tinham call site sobre o fluxo real**: eram funções puras
    chamadas só pelo construtor de casos do eval. Protegiam o eval, não a
    operação.

    O julgamento da tarefa 15, rodada 1, achou o nível seguinte: o call site era
    conferido **por nome**. Manter a chamada e descartar o retorno emitia
    `COMPLIANT` com zero âncoras reais, gravava `inspection_verification`
    fabricado e mantinha o validador 118/118 verde. `C04-CALL-SITE-REAL` = 3.

    Esta versão confere **fluxo de dados**, ligando atribuição a uso:

    1. o emissor liga a um nome o retorno de `verificar_inspecao_executada` e o
       de `conferir_identidade_do_candidato` — retorno descartado é erro;
    2. os dois nomes chegam **ainda ligados à origem** à chamada de
       `montar_ledger`;
    3. dentro de `montar_ledger`, `internal_verdict` e `governance_verdict`
       descendem do relatório da trava, cada número de `inspection_verification`
       descende dele, e `candidate_identity` descende da conferência de
       identidade;
    4. o ledger produzido é o que vai ao schema e ao envelope do CEO;
    5. em `derivar_relatorio_de_governanca`, `verdict`, `violations` e
       `candidate_identity_status` descendem do ledger;
    6. o resultado da conferência de identidade **recusa**: há um ramo que o lê e
       devolve código diferente de zero;
    7. **este próprio validador** chama a trava.

    O item 7 não é zelo: uma trava que aceita "alguma checagem roda" não obriga a
    própria presença e erode sem nada acusar.
    """
    errors: list[str] = []
    if not EMITTER_PATH.is_file():
        return [f"emissor real ausente em {EMITTER_PATH}"]

    do_emissor = _chamadas(EMITTER_PATH)
    for obrigatoria in (
        "verificar_inspecao_executada",
        "conferir_candidate_digest",
        "conferir_identidade_do_candidato",
        "decidir_veredito",
        "derivar_binario",
        # Rodada 4 - as travas que fazem o valor ser DERIVADO, nao declarado.
        "consolidar_inspecao",
        "cruzar_identidade_dos_recibos",
        "auditar_ledger_contra_evidencia",
    ):
        if obrigatoria not in do_emissor:
            errors.append(
                f"emitir_governanca.py não chama {obrigatoria}: a trava não tem"
                " call site no fluxo que emite o GOVERNANCE_REPORT"
            )

    arvore = ast.parse(EMITTER_PATH.read_text(encoding="utf-8"))
    principal = _funcao(arvore, "main")
    montar = _funcao(arvore, "montar_ledger")
    derivar = _funcao(arvore, "derivar_relatorio_de_governanca")
    if principal is None:
        return errors + ["emitir_governanca.py não define main"]
    if montar is None:
        return errors + ["emitir_governanca.py não define montar_ledger"]
    if derivar is None:
        return errors + [
            "emitir_governanca.py não define derivar_relatorio_de_governanca"
        ]

    # --- 1 e 2. o retorno de cada trava é ligado, e chega ligado ------------
    marcas: dict[str, set[str]] = {}
    for trava in (
        "verificar_inspecao_executada",
        "conferir_identidade_do_candidato",
        "consolidar_inspecao",
    ):
        marcas[trava] = _propagar(principal.body, set(), frozenset({trava}))
        if not marcas[trava]:
            errors.append(
                f"main descarta o retorno de {trava}: a trava é chamada e o"
                " resultado dela não sobrevive ligado a nome nenhum — chamada"
                " sem uso não é trava"
            )

    chamada_montar = _chamada_para(principal, "montar_ledger")
    if chamada_montar is None:
        errors.append("main não chama montar_ledger")
    else:
        argumentos: set[str] = set()
        for argumento in list(chamada_montar.args) + [
            kw.value for kw in chamada_montar.keywords
        ]:
            argumentos |= _nomes(argumento)
        for trava, tingidos in marcas.items():
            if not (argumentos & tingidos):
                errors.append(
                    f"montar_ledger não recebe o resultado de {trava}: nenhum"
                    " argumento dela descende da trava — ou o retorno foi"
                    " descartado, ou foi reatribuído no caminho e o que decide é"
                    " o valor fabricado"
                )

    # --- 3. dentro de montar_ledger, o que decide descende das travas -------
    parametros = [arg.arg for arg in montar.args.args]
    if len(parametros) < 5:
        errors.append(
            "montar_ledger não recebe as três travas: assinatura com"
            f" {len(parametros)} parâmetros, esperados ao menos 5 — rodada,"
            " recibos, relatório da trava, identidade e o bloco CONTADO"
        )
    else:
        param_relatorio = parametros[2]
        param_identidade = parametros[3]
        param_verificacao = parametros[4]
        errors.extend(
            _descende_de(
                montar,
                param_relatorio,
                ("internal_verdict", "governance_verdict"),
                "o binário tem de sair dos estados EFETIVOS",
            )
        )
        # Rodada 4: os números descem do bloco CONTADO, não do relatório da
        # trava. Se voltarem a descer de `relatorio`, esta conferência fica
        # vermelha — e foi por esse caminho que a lavagem entrou.
        errors.extend(
            _subcampos_descendem(
                montar,
                param_verificacao,
                "inspection_verification",
                (
                    "all_anchors_reverified",
                    "anchors_total",
                    "anchors_failed",
                    "methods_total",
                    "methods_failed",
                    "counted_by",
                    "counted_limit",
                ),
            )
        )
        errors.extend(
            _descende_de(
                montar,
                param_identidade,
                ("candidate_identity",),
                "a identidade registrada tem de ser a conferida",
            )
        )
        errors.extend(
            _subcampos_descendem(
                montar,
                param_identidade,
                "candidate_identity",
                ("status", "candidate_root_ref", "source", "reason", "checked_at"),
            )
        )

    # --- 4. o ledger produzido é o que vai ao schema e ao CEO ---------------
    marca_ledger = _propagar(principal.body, set(), frozenset({"montar_ledger"}))
    if not marca_ledger:
        errors.append("main descarta o AUDIT_LEDGER que montar_ledger devolveu")
    else:
        consumidores = {
            "validate_schema": False,
            "derivar_relatorio_de_governanca": False,
            # O ledger PRONTO tem de ser confrontado com os recibos em disco.
            # Sem este consumidor, a auditoria de classe existiria e não veria o
            # artefato que decide.
            "auditar_ledger_contra_evidencia": False,
        }
        for no in ast.walk(principal):
            if not isinstance(no, ast.Call):
                continue
            alvo = no.func
            nome_chamado = (
                alvo.id
                if isinstance(alvo, ast.Name)
                else alvo.attr
                if isinstance(alvo, ast.Attribute)
                else ""
            )
            if nome_chamado not in consumidores:
                continue
            mencionados: set[str] = set()
            for argumento in list(no.args) + [kw.value for kw in no.keywords]:
                mencionados |= _nomes(argumento)
            if mencionados & marca_ledger:
                consumidores[nome_chamado] = True
        for consumidor, achou in consumidores.items():
            if not achou:
                errors.append(
                    f"o AUDIT_LEDGER não é consumido por {consumidor}: o envelope"
                    " que decide não é o que foi montado a partir das travas"
                )

    # --- 5. o envelope do CEO descende do ledger ----------------------------
    param_ledger = [arg.arg for arg in derivar.args.args]
    if not param_ledger:
        errors.append("derivar_relatorio_de_governanca sem parâmetro de ledger")
    else:
        errors.extend(
            _descende_de(
                derivar,
                param_ledger[0],
                (
                    "verdict",
                    "candidate_identity_status",
                    "violations",
                    # Rodada 4: os limites viajam com o envelope da barreira, e
                    # são os do ledger — lista digitada aqui divergiria dele em
                    # silêncio.
                    "pending",
                    # E o digest publicado desce da identidade CONFERIDA, em vez
                    # de ser cópia do declarado.
                    "candidate_digest",
                ),
                "o CEO tem de ler o que o ledger decidiu",
            )
        )

    # --- 6. o resultado da identidade RECUSA --------------------------------
    da_identidade = marcas.get("conferir_identidade_do_candidato", set())
    recusa = False
    for no in ast.walk(principal):
        if not isinstance(no, ast.If):
            continue
        if not (_nomes(no.test) & da_identidade):
            continue
        for sub in ast.walk(no):
            if (
                isinstance(sub, ast.Return)
                and isinstance(sub.value, ast.Constant)
                and sub.value.value not in (0, None)
            ):
                recusa = True
    if not recusa:
        errors.append(
            "o resultado da conferência de identidade não recusa nada: não há"
            " ramo que o leia e devolva código diferente de zero"
        )

    # --- 6b. o resultado da auditoria contra a evidência RECUSA -------------
    da_auditoria = _propagar(
        principal.body, set(), frozenset({"auditar_ledger_contra_evidencia"})
    )
    if not da_auditoria:
        errors.append(
            "main descarta o retorno de auditar_ledger_contra_evidencia: a"
            " auditoria do artefato contra a evidência roda e não decide nada"
        )
    else:
        recusa_por_evidencia = False
        for no in ast.walk(principal):
            if not isinstance(no, ast.If):
                continue
            if not (_nomes(no.test) & da_auditoria):
                continue
            for sub in ast.walk(no):
                if (
                    isinstance(sub, ast.Return)
                    and isinstance(sub.value, ast.Constant)
                    and sub.value.value not in (0, None)
                ):
                    recusa_por_evidencia = True
        if not recusa_por_evidencia:
            errors.append(
                "o ledger que diverge da evidência não é recusado: não há ramo"
                " que leia auditar_ledger_contra_evidencia e devolva código"
                " diferente de zero"
            )

    # --- 7. a autoexigência do próprio validador ----------------------------
    do_validador = _chamadas(Path(__file__).resolve())
    # `validate_call_site` na própria lista é o item que impede a erosão: sem
    # ele, apagar a linha que chama esta função sairia verde, porque as outras
    # duas continuam sendo chamadas pelos casos de âncora. Trava que aceita
    # "alguma checagem roda" não obriga a própria presença.
    for obrigatoria in (
        "validate_call_site",
        "validate_identidade_nao_opcional",
        "validate_documented_usage",
        "validate_caminho_documentado_executado",
        "validate_ceo_gate_identidade",
        # Rodada 4 - as travas novas se autoexigem desde o primeiro dia. Trava
        # que nasce sem se exigir erode antes de alguem lembrar dela.
        "validate_numeros_contados",
        "validate_ledger_auditado_executado",
        "validate_limites_no_envelope",
        "validate_dois_ramos_do_passo_7",
        "verificar_inspecao_executada",
        "conferir_identidade_do_candidato",
        "reverificar_ancora",
        "conferir_metodo",
        "estado_efetivo",
        "contar_ancoras_declaradas",
        "consolidar_inspecao",
        "auditar_ledger_contra_evidencia",
        "cruzar_identidade_dos_recibos",
    ):
        if obrigatoria not in do_validador:
            errors.append(
                f"validate_workflow.py não chama {obrigatoria}: a trava deixou"
                " de se autoexigir e erode sem nada acusar"
            )
    return errors


def validate_identidade_nao_opcional() -> list[str]:
    """A conferência de identidade não pode depender da aridade de `argv`.

    **Este é o conserto do achado `A1`.** Na rodada 1 a raiz do candidato só
    existia como quarto argumento (`emitir_governanca.py:313`) e a conferência
    morava atrás de `if raiz_do_candidato is not None` (`:325`). A `SKILL.md:215`
    publicava a invocação de **dois** argumentos. Resultado medido pelos Juízes,
    com `candidate_digest` falso: pela invocação documentada saía `COMPLIANT`
    exit 0, gravando `sha256:ffff…` no relatório que o CEO lê na barreira.

    A regra, em código:

    1. `conferir_identidade_do_candidato` é chamada no corpo de `main`, **fora de
       qualquer `if`**;
    2. nenhum `if` ou expressão condicional cujo teste mencione `argv` ou `len`
       contém, em qualquer profundidade, chamada à conferência de identidade ou à
       receita de digest;
    3. `conferir_identidade_do_candidato` chama de fato `conferir_candidate_digest`.

    Continua legítimo a aridade escolher **onde** está a raiz. Deixou de ser
    legítimo a aridade escolher **se** a identidade é conferida.
    """
    errors: list[str] = []
    if not EMITTER_PATH.is_file():
        return [f"emissor real ausente em {EMITTER_PATH}"]

    arvore = ast.parse(EMITTER_PATH.read_text(encoding="utf-8"))
    principal = _funcao(arvore, "main")
    if principal is None:
        return ["emitir_governanca.py não define main"]

    no_topo = any(
        isinstance(no, (ast.Assign, ast.Expr))
        and _chamada_para(no, "conferir_identidade_do_candidato") is not None
        for no in principal.body
    )
    if not no_topo:
        errors.append(
            "conferir_identidade_do_candidato não é chamada no corpo de main: ou"
            " está aninhada sob condição, ou sumiu — nos dois casos existe"
            " invocação que emite sem conferir identidade"
        )

    protegidas = ("conferir_identidade_do_candidato", "conferir_candidate_digest")
    for no in ast.walk(arvore):
        teste = None
        if isinstance(no, (ast.If, ast.IfExp)):
            teste = no.test
        if teste is None:
            continue
        fala_de_argv = (
            "argv" in _nomes(teste) or _chamada_para(teste, "len") is not None
        )
        if not fala_de_argv:
            continue
        for protegida in protegidas:
            if _chamada_para(no, protegida) is not None:
                errors.append(
                    f"{protegida} está sob condição que fala de argv: a"
                    " conferência de identidade voltou a ser opcional por"
                    " aridade — é o achado A1"
                )

    conferidora = _funcao(arvore, "conferir_identidade_do_candidato")
    if conferidora is None:
        errors.append(
            "emitir_governanca.py não define conferir_identidade_do_candidato"
        )
    elif _chamada_para(conferidora, "conferir_candidate_digest") is None:
        errors.append(
            "conferir_identidade_do_candidato não chama conferir_candidate_digest:"
            " o status seria afirmado, não medido"
        )
    return errors


INVOCACAO = re.compile(r"python\s+scripts/emitir_governanca\.py([^\n`]*)")
FRASE_ABSOLUTA = "Não há caminho que produza o binário sem passar pela trava"

# RODADA 4 — a segunda frase absoluta, e ela era do lado oposto.
#
# A rodada 3 mediu que sem `candidate_root` a corrida abortava, e escreveu isso
# SEM CONDIÇÃO. Os Juízes mediram a outra metade: com veredito interno REPROVADO
# a mesma entrada sai exit 0 e grava os dois envelopes. Uma frase absoluta é
# falsa em metade do domínio quer ela afirme demais, quer afirme de menos.
#
# A trava não proíbe a frase: exige que, onde ela aparecer, a **variável que
# decide** apareça junto. É a diferença entre descrever um caso e descrever o
# comportamento.
FRASE_DO_ABORTO = "aborta e nada é gravado"
VARIAVEL_QUE_DECIDE = "veredito interno"


def _fontes_publicadas() -> list[tuple[str, str]]:
    """Todo texto que ensina alguém a operar este pacote."""
    fontes: list[tuple[str, str]] = []
    for caminho in [
        SKILL_PATH,
        PACKAGE_ROOT / "references" / "protocolo-auditoria.md",
    ]:
        if caminho.is_file():
            fontes.append((caminho.name, caminho.read_text(encoding="utf-8")))
    for caminho in sorted((PACKAGE_ROOT / "references").glob("adr-*.md")):
        fontes.append((caminho.name, caminho.read_text(encoding="utf-8")))
    if EMITTER_PATH.is_file():
        texto = ast.get_docstring(
            ast.parse(EMITTER_PATH.read_text(encoding="utf-8"))
        )
        fontes.append(("emitir_governanca.py::docstring", texto or ""))
    return fontes


def validate_documented_usage() -> list[str]:
    """**A documentação de uso faz parte da trava** — eixo 3, ADR-018.

    O achado `A1` não foi um defeito de código: o código tinha a conferência e a
    chamava. O defeito foi que a **instrução publicada** ensinava o caminho que
    passava por fora dela. Quem opera segue o texto, não a AST.

    Por isso o texto entra no validador. Esta função exige:

    1. a `SKILL.md` publica ao menos uma invocação do emissor;
    2. toda invocação publicada, em qualquer fonte, tem aridade que `main` aceita
       (2 ou 3 argumentos) — invocação publicada que o emissor recusa é instrução
       que não roda;
    3. `candidate_root` está documentado como campo de `rodada.json` na
       `SKILL.md` **e** no protocolo: é dele que sai a raiz na forma de dois
       argumentos, e sem essa linha o operador não sabe o que preencher;
    4. nenhuma fonte publicada repete a frase absoluta que a medição desmentiu.

    O item 4 é conferência de **texto**, e texto é instrumento fraco para provar
    comportamento — mas aqui o objeto medido É o texto publicado. Usar AST para
    isso seria medir a coisa errada.
    """
    errors: list[str] = []
    fontes = _fontes_publicadas()
    if not fontes:
        return ["nenhuma fonte publicada encontrada"]

    invocacoes_na_skill = 0
    for rotulo, texto in fontes:
        for achado in INVOCACAO.finditer(texto):
            argumentos = [a for a in achado.group(1).split() if a]
            if rotulo == SKILL_PATH.name:
                invocacoes_na_skill += 1
            if len(argumentos) not in (2, 3):
                errors.append(
                    f"{rotulo}: invocação publicada com {len(argumentos)}"
                    f" argumentos, que main recusa: {achado.group(0)!r}"
                )
        if FRASE_ABSOLUTA in texto:
            errors.append(
                f"{rotulo}: repete a garantia absoluta que a medição de"
                " 2026-08-01 desmentiu — a sonda V09b produziu COMPLIANT com a"
                " trava chamada e o retorno descartado"
            )
        if FRASE_DO_ABORTO in texto and VARIAVEL_QUE_DECIDE not in texto:
            errors.append(
                f"{rotulo}: afirma que a corrida 'aborta e nada é gravado' sem"
                " nomear o veredito interno, que é a variável que decide entre"
                " os dois desfechos. Medido em"
                " prova-r4/41-DOIS-RAMOS-DO-PASSO-7.json: no ramo REPROVADO a"
                " mesma entrada sai exit 0 com os dois envelopes gravados"
            )

    if invocacoes_na_skill < 1:
        errors.append("SKILL.md não publica nenhuma invocação do emissor")

    por_rotulo = dict(fontes)
    for rotulo in (SKILL_PATH.name, "protocolo-auditoria.md"):
        if "candidate_root" not in por_rotulo.get(rotulo, ""):
            errors.append(
                f"{rotulo} não documenta candidate_root em rodada.json: a raiz do"
                " candidato ficaria indocumentada e a forma de dois argumentos"
                " cairia em NAO_CONFERIDO sem que o operador soubesse por quê"
            )
    return errors


def validate_caminho_documentado_executado() -> list[str]:
    """Roda o comando **publicado**, com digest falso, e exige que ele barre.

    Conferir a documentação por texto ainda é conferir forma. Este caso executa:
    monta uma rodada mínima em pasta temporária, declara um `candidate_digest`
    falso e chama o emissor **exatamente pela linha que a `SKILL.md` publica** —
    dois argumentos, sem o terceiro.

    Espera `exit 2`, `BLOCKED_CANDIDATE_MISMATCH` na saída e **nenhum**
    `GOVERNANCE-REPORT.json` gravado.

    O controle que impede o falso vermelho: a mesma rodada, o mesmo comando, com
    o digest **correto** — e aí `BLOCKED_CANDIDATE_MISMATCH` não pode aparecer. O
    par difere em um campo só, e é o campo em teste.

    A rodada mínima não pretende emitir: o portão de identidade roda antes de
    qualquer recibo ser lido, e é só ele que este caso mede.
    """
    if not EMITTER_PATH.is_file():
        return [f"emissor real ausente em {EMITTER_PATH}"]

    errors: list[str] = []
    raiz_relativa = PACKAGE_ROOT.resolve().relative_to(STRUCTURE_ROOT).as_posix()
    verdadeiro = candidate_digest_de_arvore(PACKAGE_ROOT)
    falso = "sha256:" + "f" * 64

    ambiente = dict(os.environ)
    ambiente["PYTHONIOENCODING"] = "utf-8"
    ambiente["SKILL_STRUCTURE_ROOT"] = str(STRUCTURE_ROOT)

    with tempfile.TemporaryDirectory(prefix="caminho-documentado-") as temporario:
        base = Path(temporario)
        (base / "recibos").mkdir(parents=True, exist_ok=True)
        (base / "recibos" / "minimo.json").write_text("{}", encoding="utf-8")

        for rotulo, declarado, espera_bloqueio in (
            ("digest falso", falso, True),
            ("digest correto", verdadeiro, False),
        ):
            cabecalho = causal()
            cabecalho["candidate_digest"] = declarado
            (base / "rodada.json").write_text(
                json.dumps(
                    {
                        "audit_ledger_id": "audit-ledger-doc",
                        "conformity_matrix_id": "conformity-matrix-doc",
                        "report_id": "governance-report-doc",
                        "department_mission_ref": "department-mission-doc",
                        "candidate_root": raiz_relativa,
                        "causal": cabecalho,
                        # RODADA 6 — referência REAL, resolvida contra a raiz
                        # auditada. Até o cand-E esta fixture publicava
                        # `evidence/artefato-01.json`, que não existe em disco:
                        # é o `OI5-04` dentro do próprio validador. Com a trava
                        # `resolver_evidence_refs` no emissor, a fixture falsa
                        # passa a bloquear a corrida — e a correção certa é a
                        # fixture apontar para arquivo que existe, não a trava
                        # afrouxar.
                        "evidence_refs": [f"{raiz_relativa}/SKILL.md"],
                        "recorded_at": "2026-08-01T18:00:00-03:00",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            alvo = base / "GOVERNANCE-REPORT.json"
            if alvo.exists():
                alvo.unlink()
            processo = subprocess.run(
                [
                    sys.executable,
                    "scripts/emitir_governanca.py",
                    str(base),
                    str(STRUCTURE_ROOT),
                ],
                cwd=str(PACKAGE_ROOT),
                env=ambiente,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            saida = (processo.stdout or "") + (processo.stderr or "")
            bloqueou = "BLOCKED_CANDIDATE_MISMATCH" in saida
            if espera_bloqueio and not bloqueou:
                errors.append(
                    "o caminho DOCUMENTADO (dois argumentos) não barrou"
                    f" candidate_digest falso: exit={processo.returncode}."
                    " É o achado A1 de volta"
                )
            if espera_bloqueio and processo.returncode != 2:
                errors.append(
                    "o caminho DOCUMENTADO com digest falso devolveu"
                    f" exit={processo.returncode}, esperado 2"
                )
            if espera_bloqueio and alvo.exists():
                errors.append(
                    "o caminho DOCUMENTADO gravou GOVERNANCE-REPORT.json mesmo"
                    " com identidade divergente"
                )
            if not espera_bloqueio and bloqueou:
                errors.append(
                    f"o controle falhou: com o {rotulo} o caminho documentado"
                    " ainda barrou — a trava está sempre vermelha e não"
                    " discrimina nada"
                )
    return errors


def validate_ceo_gate_identidade() -> list[str]:
    """O gate de identidade está escrito no schema do CEO, como texto normativo.

    O emissor pode ser corrigido; o schema do CEO é o contrato que sobrevive a
    ele. `COMPLIANT` no `GOVERNANCE_REPORT` exige `candidate_identity_status`
    presente e igual a `CONFERIDO`. Sem esta cláusula o campo viraria decoração
    opcional — e a mutação `M12` já provou, na rodada 1, que fixture cobre
    caminho e não garante que a regra continua escrita.
    """
    if not CEO_SCHEMA_PATH.is_file():
        return ["schema do CEO ausente"]
    ceo = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))
    relatorio = ceo.get("$defs", {}).get("governanceReport", {})
    propriedades = relatorio.get("properties", {})
    if propriedades.get("candidate_identity_status", {}).get("enum") != [
        "CONFERIDO",
        "NAO_CONFERIDO",
    ]:
        return [
            "governanceReport do CEO sem o enum de candidate_identity_status: o"
            " CEO não consegue distinguir identidade conferida de não conferida"
        ]
    for clausula in relatorio.get("allOf", []):
        se = clausula.get("if", {}).get("properties", {}).get("verdict", {})
        entao = clausula.get("then", {})
        if se.get("const") != "COMPLIANT":
            continue
        if "candidate_identity_status" not in entao.get("required", []):
            continue
        if entao.get("properties", {}).get("candidate_identity_status") == {
            "const": "CONFERIDO"
        }:
            return []
    return [
        "schema do CEO sem a cláusula que exige candidate_identity_status"
        " CONFERIDO para COMPLIANT: a barreira aceitaria relatório cuja"
        " identidade nunca foi recomputada"
    ]


def validate_ceo_gate_independencia() -> list[str]:
    """A independência do painel é CONDIÇÃO de `COMPLIANT` no schema do CEO.

    `FIND-REMED7-C08-CA-01`. A Barreira de saída do contrato promete "cada recibo
    usado é válido, **independente** e rastreável" como condição de veredito
    positivo, e nenhuma das cláusulas que governavam `COMPLIANT` lia a
    independência: o campo era preenchido em `panel[]` e **jamais lido**. Recibo
    não independente fechava `COMPLIANT` do mesmo jeito.

    A trava mora aqui, e não no recibo, porque a promessa é quantificada sobre um
    conjunto — o painel é o único artefato que vê o conjunto, e no recibo o campo
    tem de continuar MEDIDO, ou o schema volta a premiar quem mente (rodada 9).
    Esta função cuida da SEGUNDA camada: o escalar derivado que atravessa a
    fronteira. O emissor pode ser corrigido; o schema do CEO é o contrato que
    sobrevive a ele.

    A terceira conferência é a que não existia em lugar nenhum, e é o que teria
    pego a `T83`: **toda chave citada num `if` tem de existir em `properties`**.
    `governanceReport` é `additionalProperties: false`, então cláusula chaveada em
    campo que o objeto não tem é logicamente insatisfazível — ela fica escrita,
    passa em qualquer revisão de leitura, e nunca dispara. Foi assim que a
    cláusula do manifesto nasceu morta na rodada 8, chaveada em
    `governance_verdict`, que é o nome do veredito no `AUDIT_LEDGER` e não aqui.
    Presença de cláusula não é alcance de cláusula.
    """
    if not CEO_SCHEMA_PATH.is_file():
        return ["schema do CEO ausente"]
    ceo = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))
    relatorio = ceo.get("$defs", {}).get("governanceReport", {})
    propriedades = relatorio.get("properties", {})
    errors: list[str] = []

    if propriedades.get("panel_independence_status", {}).get("enum") != [
        "INDEPENDENTE",
        "NAO_INDEPENDENTE",
    ]:
        errors.append(
            "governanceReport do CEO sem o enum de panel_independence_status: o"
            " CEO não consegue distinguir painel independente de painel que não"
            " foi, e a promessa do contrato não alcança a barreira"
        )

    # Toda cláusula tem de poder disparar. Sem isto, a trava abaixo poderia ser
    # satisfeita por uma cláusula tão morta quanto a que a T83 encontrou.
    for indice, clausula in enumerate(relatorio.get("allOf", [])):
        for chave in (clausula.get("if", {}).get("properties", {}) or {}):
            if chave not in propriedades:
                errors.append(
                    f"CLÁUSULA INALCANÇÁVEL em governanceReport.allOf[{indice}]:"
                    f" o `if` é chaveado em {chave!r}, que não está em"
                    " `properties` e que `additionalProperties: false` proíbe."
                    " O `if` nunca casa e o `then` nunca aplica — a cláusula"
                    " está escrita e não decide nada (T83)"
                )

    for clausula in relatorio.get("allOf", []):
        se = clausula.get("if", {}).get("properties", {}).get("verdict", {})
        entao = clausula.get("then", {})
        if se.get("const") != "COMPLIANT":
            continue
        if "panel_independence_status" not in entao.get("required", []):
            continue
        if entao.get("properties", {}).get("panel_independence_status") == {
            "const": "INDEPENDENTE"
        }:
            return errors
    return errors + [
        "schema do CEO sem a cláusula que exige panel_independence_status"
        " INDEPENDENTE para COMPLIANT: a barreira aceitaria relatório cujo"
        " painel de inspetores não foi independente, que é o achado"
        " FIND-REMED7-C08-CA-01"
    ]


def validate_emissor_deriva_independencia() -> list[str]:
    """O EMISSOR — não a cópia deste validador — deriva a independência do painel.

    Esta trava nasceu de um mutante que ESCAPOU. A prova de mutação da T71 pegou
    5 de 6; o que passou foi apagar o guarda do painel vazio **dentro** de
    `emitir_governanca.py`: a bateria seguiu em 174/174. Este arquivo
    reimplementa a derivação em `derive_governance_report` e estava testando a
    própria cópia — a função que a operação chama não era exercitada por caso
    algum. Cópia local não é a que carrega.

    Duas conferências, porque nenhuma fecha sozinha:

    1. a função do emissor **responde** certo, inclusive no painel vazio, onde
       `all([])` é `True` e a resposta ingênua seria `INDEPENDENTE`;
    2. `derivar_relatorio_de_governanca` **chama** essa função — helper correto
       que ninguém chama protege o eval, não a emissão.
    """
    errors: list[str] = []
    derivar = getattr(emitir_governanca, "derivar_independencia_do_painel", None)
    if derivar is None:
        return [
            "emitir_governanca.py não define derivar_independencia_do_painel: a"
            " independência do painel não é derivada no fluxo real"
        ]

    for rotulo, painel, esperado in (
        ("painel todo independente",
         [{"independent": True}, {"independent": True}], "INDEPENDENTE"),
        ("um inspetor não independente",
         [{"independent": True}, {"independent": False}], "NAO_INDEPENDENTE"),
        ("painel VAZIO", [], "NAO_INDEPENDENTE"),
        ("item sem o campo", [{"auditor_id": "x"}], "NAO_INDEPENDENTE"),
    ):
        obtido = derivar(painel)
        if obtido != esperado:
            errors.append(
                f"o emissor deriva {obtido!r} para {rotulo} e o contrato exige"
                f" {esperado!r}"
                + (" — `all([])` é True, e sem guarda painel vazio vira"
                   " independência: ausência de inspetor não é independência"
                   if not painel else "")
            )

    arvore = ast.parse(EMITTER_PATH.read_text(encoding="utf-8"))
    relatorio = _funcao(arvore, "derivar_relatorio_de_governanca")
    if relatorio is None:
        return errors + [
            "emitir_governanca.py não define derivar_relatorio_de_governanca"
        ]
    if _chamada_para(relatorio, "derivar_independencia_do_painel") is None:
        errors.append(
            "derivar_relatorio_de_governanca NÃO chama"
            " derivar_independencia_do_painel: o envelope voltaria a carregar"
            " valor digitado, e o helper certo protegeria apenas o eval"
        )
    return errors


# --------------------------------------------------------------------------
# RODADA 4 — o valor é DERIVADO, nunca declarado
# --------------------------------------------------------------------------

def validate_numeros_contados() -> list[str]:
    """`anchors_total` sai de uma CONTAGEM, e a análise prova a origem.

    O julgamento da rodada 3 achou o nível 6 do defeito que atravessou esta
    frente inteira: o número que ia ao envelope era **lido** de um campo. Uma
    função intermediária que devolvesse `{"anchors_total": 12}` preservava a
    cadeia de nomes, o gate de schema `anchors_total >= 10` aceitava o valor
    fabricado, e o emissor gravava `COMPLIANT` sobre recibos com **zero**
    âncoras. Reproduzido em `prova-r4/40-RC14-REPRODUZIDO.json`.

    Esta função confere, na AST de `inspecao_executada.py`, três coisas:

    1. `consolidar_inspecao` **chama** `contar_ancoras_declaradas`;
    2. no dicionário que ela devolve, `anchors_total` e `methods_total`
       descendem do resultado dessa chamada — não do parâmetro `relatorio`;
    3. `all_anchors_reverified` **não** é cópia de um campo homônimo do
       relatório: é expressão comparativa, derivada das falhas.

    O item 2 é o que fecha a porta pela origem. O item 3 fecha a variante barata:
    booleano copiado é declaração com cara de medida.
    """
    errors: list[str] = []
    if not ENGINE_PATH.is_file():
        return [f"módulo da trava ausente em {ENGINE_PATH}"]

    arvore = ast.parse(ENGINE_PATH.read_text(encoding="utf-8"))
    consolidar = _funcao(arvore, "consolidar_inspecao")
    contar = _funcao(arvore, "contar_ancoras_declaradas")
    if contar is None:
        errors.append(
            "inspecao_executada.py não define contar_ancoras_declaradas: não há"
            " de onde o número vir contado"
        )
    if consolidar is None:
        return errors + ["inspecao_executada.py não define consolidar_inspecao"]

    if _chamada_para(consolidar, "contar_ancoras_declaradas") is None:
        errors.append(
            "consolidar_inspecao não chama contar_ancoras_declaradas: o total"
            " voltaria a ser lido de um campo, que é o achado RC-14"
        )

    parametros = [arg.arg for arg in consolidar.args.args]
    param_relatorio = parametros[1] if len(parametros) > 1 else "relatorio"
    da_contagem = _propagar(
        consolidar.body, set(), frozenset({"contar_ancoras_declaradas"})
    )
    if not da_contagem:
        errors.append(
            "consolidar_inspecao descarta o retorno de contar_ancoras_declaradas"
        )

    devolvido = _dicionario_devolvido(consolidar)
    if not devolvido:
        return errors + [
            "consolidar_inspecao não devolve um dicionário literal: os subcampos"
            " ficam opacos e a origem do número deixa de ser conferível"
        ]

    for campo in ("anchors_total", "methods_total"):
        valor = devolvido.get(campo)
        if valor is None:
            errors.append(f"consolidar_inspecao não devolve {campo}")
            continue
        if not (_nomes(valor) & da_contagem):
            errors.append(
                f"consolidar_inspecao: {campo} NÃO descende da contagem — o"
                " número que vai ao envelope é lido, não contado. É o RC-14"
            )
        if param_relatorio in _nomes(valor):
            errors.append(
                f"consolidar_inspecao: {campo} lê {param_relatorio} — o campo"
                " homônimo do relatório voltou a ser a fonte do total"
            )

    reverificado = devolvido.get("all_anchors_reverified")
    if reverificado is None:
        errors.append("consolidar_inspecao não devolve all_anchors_reverified")
    elif not isinstance(reverificado, (ast.Compare, ast.BoolOp)):
        errors.append(
            "consolidar_inspecao: all_anchors_reverified não é derivado das"
            " falhas — booleano copiado é declaração com cara de medida"
        )
    return errors




def _rodada_minima(
    base: Path,
    ancoras_por_dimensao: int = 2,
) -> tuple[str, list[str]]:
    """Monta em disco uma rodada real, com âncoras que reabrem de verdade.

    Devolve `(candidate_digest, task_ids)`. As âncoras saem do disco — linha,
    citação e digest são lidos —, porque uma rodada de fixture com âncora
    inventada mediria o emissor contra um mundo que não existe.
    """
    (base / "recibos").mkdir(parents=True, exist_ok=True)
    raiz_relativa = PACKAGE_ROOT.resolve().relative_to(STRUCTURE_ROOT).as_posix()
    candidate = candidate_digest_de_arvore(PACKAGE_ROOT)
    contrato = digest("b")
    identificadores: list[str] = []

    for nome in AGENT_NAMES:
        capacidade = AGENT_CAPABILITY[nome]
        minhas = [d for d, c in OWNER.items() if c == capacidade]
        minhas += [d for d, c in SECONDARY.items() if c == capacidade]
        contrato_ref = (
            f"{raiz_relativa}/agentes/{nome}/CONTRATO-DE-COMPROMISSO.md"
        )
        contrato_path = STRUCTURE_ROOT / contrato_ref
        texto_contrato = contrato_path.read_text(encoding="utf-8")
        estados: list[dict[str, Any]] = []
        for indice, dimensao in enumerate(minhas):
            ancoras = []
            refs = []
            for repeticao in range(ancoras_por_dimensao):
                referencia = f"{raiz_relativa}/SKILL.md"
                caminho = STRUCTURE_ROOT / referencia
                linhas = caminho.read_text(encoding="utf-8").splitlines()
                uteis = [
                    (numero, texto.strip())
                    for numero, texto in enumerate(linhas, start=1)
                    if len(texto.strip()) >= 30
                ]
                numero, texto = uteis[(indice + repeticao) % len(uteis)]
                nome_ref = f"EV-{dimensao}-{repeticao:02d}"
                refs.append(nome_ref)
                ancoras.append(
                    {
                        "evidence_ref": nome_ref,
                        "artifact_ref": referencia,
                        "line": numero,
                        "quote": texto[:120],
                        "file_digest": sha256_file(caminho),
                    }
                )
            estados.append(
                {
                    "dimension": dimensao,
                    "state": "CONFORME",
                    "reason": (
                        f"{dimensao} percorrida pelo contrato de {nome}, com a"
                        " evidência aberta em disco."
                    ),
                    "evidence_refs": refs,
                    "evidence_anchors": ancoras,
                    "not_applicable_reason": "n/a",
                }
            )
        identificador = f"AUDIT-CONTAGEM-{capacidade}"
        identificadores.append(identificador)
        recibo = {
            "artifact_type": "AUDIT_RECEIPT",
            "task_id": identificador,
            "auditor_id": nome,
            "capability": capacidade,
            "contract_digest": contrato,
            "candidate_digest": candidate,
            "method": {
                "role_of": nome,
                "executed_by": DEPARTMENT,
                "execution_mode": "PAPEL_SOB_PORTA_UNICA",
                "agent_contract_ref": contrato_ref,
                "agent_contract_digest": sha256_file(contrato_path),
                "obrigacoes_declaradas": contar_itens_do_contrato(
                    texto_contrato, "Obrigações"
                ),
                "barreira_de_saida_declarada": contar_itens_do_contrato(
                    texto_contrato, "Barreira de saída"
                ),
            },
            "review_chain": {
                "context_clean": True,
                "independent": True,
                "independent": True,
                "reviewed_at": "2026-08-02T09:00:00-03:00",
                "reviewed_input_refs": [f"EV-{d}-00" for d in minhas],
            },
            "dimension_states": estados,
            "findings": [],
            "scope_observed": [f"Dimensões da capacidade {capacidade}."],
            "pending": [],
            "status": "COMPLETED",
            "return_to": DEPARTMENT,
            "issued_at": "2026-08-02T09:05:00-03:00",
        }
        (base / "recibos" / f"{identificador}.json").write_text(
            json.dumps(recibo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    cabecalho = causal()
    cabecalho["candidate_digest"] = candidate
    cabecalho["contract_digest"] = contrato
    (base / "rodada.json").write_text(
        json.dumps(
            {
                "audit_ledger_id": "audit-ledger-contagem",
                "conformity_matrix_id": "conformity-matrix-contagem",
                "report_id": "governance-report-contagem",
                "department_mission_ref": "department-mission-contagem",
                "candidate_root": raiz_relativa,
                "causal": cabecalho,
                # RODADA 6 — referência REAL, resolvida contra a raiz auditada.
                # Ver a nota gêmea em `validate_caminho_documentado_executado`:
                # a fixture antiga apontava para arquivo inexistente, e era o
                # `OI5-04` reproduzido dentro do validador.
                "evidence_refs": [f"{raiz_relativa}/SKILL.md"],
                "recorded_at": "2026-08-02T09:10:00-03:00",
                "substrate": "desconhecido",
                "tier": "desconhecido",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return candidate, identificadores


def _rodar_emissor(base: Path) -> subprocess.CompletedProcess[str]:
    ambiente = dict(os.environ)
    ambiente["PYTHONIOENCODING"] = "utf-8"
    ambiente["SKILL_STRUCTURE_ROOT"] = str(STRUCTURE_ROOT)
    return subprocess.run(
        [
            sys.executable,
            "scripts/emitir_governanca.py",
            str(base),
            str(STRUCTURE_ROOT),
        ],
        cwd=str(PACKAGE_ROOT),
        env=ambiente,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def validate_ledger_auditado_executado() -> list[str]:
    """Planta contagem falsa **na evidência** e exige que o emissor recuse.

    O caso é o RC-14 ao contrário. Uma rodada real é montada em disco, com
    âncoras que reabrem, e o emissor roda três vezes:

    - **controle** — a rodada íntegra. Tem de emitir, exit 0, e o
      `anchors_total` gravado tem de ser **exatamente** o número de âncoras que
      existem nos recibos. Sem este controle a trava poderia estar sempre
      vermelha e não discriminar nada;
    - **âncoras removidas dos recibos depois da contagem** — o emissor tem de
      sair com 2 e não gravar envelope. É a forma que produziu `COMPLIANT` com
      `anchors_total: 12` sobre zero âncoras na rodada 3;
    - **recibo de outro candidato** — `candidate_digest` do recibo trocado. Tem
      de sair `BLOCKED_RECEIPT_IDENTITY_MISMATCH`.

    A alegação que este caso sustenta é estreita de propósito: ele prova que
    **este** emissor, rodando, recusa **estas** três formas. Não prova
    impossibilidade universal, e o `pending` do envelope diz isso.
    """
    if not EMITTER_PATH.is_file():
        return [f"emissor real ausente em {EMITTER_PATH}"]
    errors: list[str] = []

    with tempfile.TemporaryDirectory(prefix="contagem-") as temporario:
        base = Path(temporario) / "rodada"
        candidate, identificadores = _rodada_minima(base)

        # --- controle: a rodada íntegra emite, e o número bate ---------------
        processo = _rodar_emissor(base)
        alvo = base / "AUDIT-LEDGER.json"
        if processo.returncode != 0 or not alvo.is_file():
            errors.append(
                "CONTROLE FALHOU: a rodada íntegra não emitiu"
                f" (exit={processo.returncode}). A trava estaria sempre vermelha"
                " e não discriminaria nada"
            )
        else:
            ledger = json.loads(alvo.read_text(encoding="utf-8"))
            reais = sum(
                len(linha.get("evidence_anchors", []))
                for arquivo in sorted((base / "recibos").glob("*.json"))
                for linha in json.loads(
                    arquivo.read_text(encoding="utf-8")
                )["dimension_states"]
            )
            gravado = ledger["inspection_verification"]["anchors_total"]
            if gravado != reais:
                errors.append(
                    f"anchors_total gravado {gravado} e âncoras em disco {reais}:"
                    " o número não é a contagem"
                )
            if ledger["inspection_verification"]["counted_by"] != (
                "scripts/inspecao_executada.py::contar_ancoras_declaradas"
            ):
                errors.append("o envelope não publica a receita da contagem")

        # --- ataque 1: LAVAGEM no ponto de costura, em processo ------------
        #
        # Este é o RC-14, executado. A lavagem não é plantada editando arquivo:
        # é plantada onde ela de fato mora — no valor que o emissor recebe da
        # consolidação. `consolidar_inspecao` é substituída por uma função que
        # devolve `anchors_total: 12` e nenhuma divergência, que é exatamente o
        # que a variante dos Juízes conseguia. O que tem de barrar é a auditoria
        # do artefato contra os recibos em disco.
        for gravado in ("AUDIT-LEDGER.json", "GOVERNANCE-REPORT.json"):
            if (base / gravado).exists():
                (base / gravado).unlink()

        def _lavagem(recibos: list[dict[str, Any]], relatorio: dict[str, Any]):
            return (
                {
                    "all_anchors_reverified": True,
                    "anchors_total": 12,
                    "anchors_failed": 0,
                    "methods_total": 3,
                    "methods_failed": 0,
                    "counted_by": (
                        "scripts/inspecao_executada.py::contar_ancoras_declaradas"
                    ),
                    "counted_limit": (
                        "anchors_failed e methods_failed vêm da reabertura e têm"
                        " origem única — não há segunda medida que os confronte"
                    ),
                },
                [],
            )

        original = emitir_governanca.consolidar_inspecao
        emitir_governanca.consolidar_inspecao = _lavagem
        capturado = io.StringIO()
        try:
            with contextlib.redirect_stdout(capturado):
                codigo = emitir_governanca.main(
                    ["emitir_governanca.py", str(base), str(STRUCTURE_ROOT)]
                )
        finally:
            emitir_governanca.consolidar_inspecao = original
        saida = capturado.getvalue()
        if codigo == 0:
            errors.append(
                "a LAVAGEM passou: anchors_total 12 sobre a evidência real"
                " produziu emissão. É o achado RC-14 de volta"
            )
        if "BLOCKED_LEDGER_EVIDENCE_MISMATCH" not in saida:
            errors.append(
                "a lavagem não foi acusada pela auditoria contra a evidência:"
                f" saída {saida.strip()[-200:]!r}"
            )
        if (base / "GOVERNANCE-REPORT.json").exists():
            errors.append("envelope gravado sob lavagem de contagem")

        # --- controle do ataque 1: sem lavagem, a MESMA rodada emite -------
        # O par difere em uma coisa só, e é a coisa em teste. Sem ele a trava
        # poderia estar sempre vermelha e o vermelho não provaria nada.
        capturado = io.StringIO()
        with contextlib.redirect_stdout(capturado):
            codigo = emitir_governanca.main(
                ["emitir_governanca.py", str(base), str(STRUCTURE_ROOT)]
            )
        if codigo != 0 or not (base / "GOVERNANCE-REPORT.json").exists():
            errors.append(
                "CONTROLE FALHOU: sem a lavagem a mesma rodada não emitiu"
                f" (exit={codigo})"
            )

        # --- ataque 1b: âncoras somem dos recibos --------------------------
        # Não é lavagem: é evidência que encolheu. O desfecho CERTO aqui é
        # emitir NONCOMPLIANT, não recusar — todas as dimensões caem para
        # NAO_PROVADO e o veredito reprova. Este caso existe para provar que a
        # trava discrimina fabricação de escassez.
        for arquivo in sorted((base / "recibos").glob("*.json")):
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            for linha in dados["dimension_states"]:
                linha["evidence_anchors"] = []
                linha["evidence_refs"] = []
            arquivo.write_text(
                json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        for gravado in ("AUDIT-LEDGER.json", "GOVERNANCE-REPORT.json"):
            if (base / gravado).exists():
                (base / gravado).unlink()
        processo = _rodar_emissor(base)
        if processo.returncode != 0:
            errors.append(
                "recibos sem âncora deveriam emitir NONCOMPLIANT, e a corrida"
                f" abortou (exit={processo.returncode})"
            )
        elif (base / "AUDIT-LEDGER.json").is_file():
            emitido = json.loads((base / "AUDIT-LEDGER.json").read_text(encoding="utf-8"))
            if emitido["governance_verdict"] != "NONCOMPLIANT":
                errors.append(
                    "recibos sem âncora fecharam"
                    f" {emitido['governance_verdict']}, esperado NONCOMPLIANT"
                )
            if emitido["inspection_verification"]["anchors_total"] != 0:
                errors.append(
                    "recibos sem âncora gravaram anchors_total"
                    f" {emitido['inspection_verification']['anchors_total']},"
                    " e a contagem em disco é 0"
                )

        # --- ataque 2: recibo de outro candidato ---------------------------
        base2 = Path(temporario) / "rodada2"
        _rodada_minima(base2)
        alvo_recibo = sorted((base2 / "recibos").glob("*.json"))[0]
        dados = json.loads(alvo_recibo.read_text(encoding="utf-8"))
        dados["candidate_digest"] = digest("e")
        alvo_recibo.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        processo = _rodar_emissor(base2)
        saida = (processo.stdout or "") + (processo.stderr or "")
        if "BLOCKED_RECEIPT_IDENTITY_MISMATCH" not in saida:
            errors.append(
                "recibo de OUTRO candidato entrou na matriz sem acusação:"
                f" exit={processo.returncode}"
            )
        if (base2 / "GOVERNANCE-REPORT.json").exists():
            errors.append("envelope gravado com recibo de outro candidato")
    return errors


def validate_limites_no_envelope() -> list[str]:
    """Os três limites alcançam o artefato que a barreira do CEO lê.

    Duas óticas independentes dos Juízes acusaram a mesma contradição na rodada
    3: a `SKILL.md` afirmava que quem lê o envelope na barreira lê `R6`, `R9` e
    `R10` **no próprio artefato**, e o artefato lido — o `governanceReport` do
    schema do CEO — não tinha `pending`, com `additionalProperties: false`
    proibindo o campo. Ou a frase saía, ou o limite passava a alcançar o
    envelope. Esta função confere que a segunda opção foi a escolhida:

    1. o `governanceReport` do CEO **tem** `pending`, e ele é obrigatório;
    2. o schema exige, por `contains`, uma linha de cada um dos três;
    3. o emissor real, rodando, grava os três no envelope — conferido no
       artefato emitido, não no código que o emite.
    """
    errors: list[str] = []
    if not CEO_SCHEMA_PATH.is_file():
        return ["schema do CEO ausente"]
    ceo = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))
    relatorio = ceo.get("$defs", {}).get("governanceReport", {})

    if "pending" not in relatorio.get("required", []):
        errors.append(
            "governanceReport do CEO não exige pending: os três limites não"
            " alcançam o artefato que a barreira lê, e a SKILL.md afirma que"
            " alcançam"
        )
    pendente = relatorio.get("properties", {}).get("pending")
    if not isinstance(pendente, dict):
        return errors + ["governanceReport do CEO sem a propriedade pending"]
    exigidos = {
        clausula.get("contains", {}).get("pattern")
        for clausula in pendente.get("allOf", [])
    }
    for limite in ("^R6 ", "^R9 ", "^R10 "):
        if limite not in exigidos:
            errors.append(
                f"governanceReport do CEO não exige o limite {limite!r} em"
                " pending: ele poderia sumir do envelope sem nada acusar"
            )
    # RODADA 7, OI6-01 — O SCHEMA DO CEO EXIGE O TEXTO, NÃO O PREFIXO.
    #
    # A conferência acima continua de pé e não sai: ela acusa a ausência do
    # `contains`. A que entra confere que o `const` ao lado do `pattern` é o
    # texto vigente do emissor, byte a byte. Sem ela, `["R6 x", "R9 x", "R10 x"]`
    # satisfazia o schema E esta trava, que é o que `OI6-01` mediu.
    consts = {
        clausula.get("contains", {}).get("pattern"): clausula.get(
            "contains", {}
        ).get("const")
        for clausula in pendente.get("allOf", [])
    }
    for prefixo, identificador in (("^R6 ", "R6"), ("^R9 ", "R9"), ("^R10 ", "R10")):
        if consts.get(prefixo) != TEXTO_DE_CADA_LIMITE[identificador]:
            errors.append(
                f"governanceReport do CEO não exige o limite {identificador} por"
                " IGUALDADE EXATA: o `contains` decide por prefixo aberto, e sob"
                " prefixo o texto vigente, o texto RETIRADO e"
                f" {identificador!r} + qualquer coisa são indistinguíveis"
                " (OI6-01; o próprio comentário de OI5-08 já dizia isso e o"
                " mecanismo seguia vivo para estes quatro)"
            )

    with tempfile.TemporaryDirectory(prefix="limites-") as temporario:
        base = Path(temporario) / "rodada"
        _rodada_minima(base)
        processo = _rodar_emissor(base)
        alvo = base / "GOVERNANCE-REPORT.json"
        if processo.returncode != 0 or not alvo.is_file():
            errors.append(
                "CONTROLE FALHOU: o emissor não produziu envelope para conferir"
                f" os limites (exit={processo.returncode})"
            )
        else:
            emitido = json.loads(alvo.read_text(encoding="utf-8"))
            publicados = emitido.get("pending", [])
            for limite in ("R6", "R9", "R10"):
                if not any(
                    isinstance(linha, str) and linha.startswith(f"{limite} ")
                    for linha in publicados
                ):
                    errors.append(
                        f"o envelope emitido não carrega o limite {limite}:"
                        " quem lê na barreira teria de lembrar dele de fora"
                    )
                # RODADA 7 — e o que ele carrega é O TEXTO. Terceiro eixo do
                # conserto: schema, barreira e ENVELOPE EMITIDO, rodando.
                if not any(
                    linha == TEXTO_DE_CADA_LIMITE[limite] for linha in publicados
                ):
                    errors.append(
                        f"o envelope emitido carrega um {limite} que NÃO é o"
                        " texto vigente do emissor, byte a byte"
                    )
            if emitido.get("candidate_digest_source") != "RECOMPUTADO":
                errors.append(
                    "o envelope emitido não declara que o digest publicado é o"
                    " RECOMPUTADO: o consumidor não distingue conferido de"
                    " copiado"
                )
    return errors



def validate_dois_ramos_do_passo_7() -> list[str]:
    """Roda a MESMA entrada nos dois ramos e exige desfechos diferentes.

    A entrada é uma só: `rodada.json` **sem** `candidate_root`. O que separa os
    dois desfechos é o veredito interno, e este caso o produz das duas formas:

    - **rodada íntegra** → veredito interno `APROVADO` → o ramo `COMPLIANT` do
      schema do ledger exige `CONFERIDO`, e a corrida **aborta**: exit 2, nenhum
      arquivo gravado;
    - **uma dimensão sem âncora** → veredito interno `REPROVADO` → aquela
      cláusula não se aplica, e os **dois envelopes são gravados**: exit 0,
      `NONCOMPLIANT`, com a razão em `pending`.

    Este caso é o controle mútuo de si mesmo: se os dois desfechos fossem
    iguais, um deles estaria errado, e a prosa que descreve dois seria ficção.
    """
    if not EMITTER_PATH.is_file():
        return [f"emissor real ausente em {EMITTER_PATH}"]
    errors: list[str] = []

    with tempfile.TemporaryDirectory(prefix="dois-ramos-") as temporario:
        for rotulo, reprova in (("A-aprovado", False), ("B-reprovado", True)):
            base = Path(temporario) / rotulo
            _rodada_minima(base)
            rodada = json.loads((base / "rodada.json").read_text(encoding="utf-8"))
            rodada.pop("candidate_root", None)
            (base / "rodada.json").write_text(
                json.dumps(rodada, ensure_ascii=False), encoding="utf-8"
            )
            if reprova:
                alvo = sorted((base / "recibos").glob("*.json"))[0]
                dados = json.loads(alvo.read_text(encoding="utf-8"))
                dados["dimension_states"][0]["evidence_anchors"] = []
                dados["dimension_states"][0]["evidence_refs"] = []
                alvo.write_text(
                    json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            processo = _rodar_emissor(base)
            gravou = (base / "GOVERNANCE-REPORT.json").is_file()
            if not reprova:
                if processo.returncode != 2:
                    errors.append(
                        "ramo A (veredito diferente de REPROVADO) devolveu"
                        f" exit={processo.returncode}, esperado 2"
                    )
                if gravou:
                    errors.append(
                        "ramo A gravou envelope: a frase 'aborta e nada é"
                        " gravado' deixaria de valer também aqui"
                    )
            else:
                if processo.returncode != 0:
                    errors.append(
                        "ramo B (veredito REPROVADO) devolveu"
                        f" exit={processo.returncode}, esperado 0"
                    )
                if not gravou:
                    errors.append(
                        "ramo B não gravou envelope: a SKILL.md descreve dois"
                        " desfechos e só existiria um"
                    )
                else:
                    emitido = json.loads(
                        (base / "GOVERNANCE-REPORT.json").read_text(encoding="utf-8")
                    )
                    if emitido.get("candidate_identity_status") != "NAO_CONFERIDO":
                        errors.append(
                            "ramo B não publicou NAO_CONFERIDO no envelope"
                        )
                    if emitido.get("verdict") != "NONCOMPLIANT":
                        errors.append(
                            "ramo B fechou"
                            f" {emitido.get('verdict')!r}, esperado NONCOMPLIANT"
                        )
                    if not any(
                        "identidade" in linha.lower()
                        for linha in emitido.get("pending", [])
                    ):
                        errors.append(
                            "ramo B não registrou a razão da identidade em"
                            " pending, e a SKILL.md diz que registra"
                        )
    return errors


# Casos que NÃO PODEM sumir da bateria.
#
# A mutação M11 apagou a linha que chama `validate_call_site()` e o validador
# ficou verde. A causa é um problema de ponto fixo: a autoexigência morava
# **dentro** da função que a mutação deixou de chamar, e uma checagem que só
# roda quando é chamada não consegue perceber que não foi chamada.
#
# A saída é ancorar a exigência no **ponto de entrada**, que sempre roda:
# `run()` confere, no fim, que cada rótulo obrigatório está na lista de casos
# efetivamente construída. Apagar um `cases.append(...)` passa a mudar o
# resultado.
#
# Limite declarado, porque não é turtles all the way down: quem apagar também
# esta conferência dentro de `run()` quebra o ponto fixo. O que se ganha é que a
# remoção deixa de ser invisível — ela passa a aparecer como edição do laço
# principal do validador, e não como uma linha a menos no meio de trezentas.
def validate_matriz_recontada() -> list[str]:
    """`OI-01` — a auditoria RECONTA o estado da matriz, não o lê para decidir.

    O defeito, medido por origem independente em 2026-08-02, é o desta frente em
    forma pura: `auditar_ledger_contra_evidencia` **lia**
    `conformity_matrix.dimensions[].state` e recomputava o veredito **a partir**
    dele. Conferia o artefato consigo mesmo. Uma matriz mentirosa produzia um
    veredito coerente com ela própria, zero divergências, `[REBAIXA]` no console
    e `COMPLIANT` no envelope, com exit 0.

    Esta trava confere as três coisas que a correção precisa ter, e as três em
    eixos diferentes — **estático**, **estrutural** e **executado**:

    1. **assinatura**: a função recebe `raiz` como parâmetro **obrigatório e
       posicional**. Raiz com valor padrão seria a opcionalidade por aridade do
       achado `A1`, na função que existe para não repetir a classe;
    2. **fluxo de dados**: o corpo chama `verificar_inspecao_executada` e o
       retorno alimenta a comparação com a matriz. Manter a chamada e decidir
       por `gravados` fica vermelho aqui;
    3. **executado**: uma matriz mentirosa, em processo, é ACUSADA — e o
       controle, uma matriz honesta, não é.
    """
    errors: list[str] = []
    caminho = PACKAGE_ROOT / "scripts" / "inspecao_executada.py"
    if not caminho.is_file():
        return ["scripts/inspecao_executada.py ausente"]
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    alvo = next(
        (
            no
            for no in ast.walk(arvore)
            if isinstance(no, ast.FunctionDef)
            and no.name == "auditar_ledger_contra_evidencia"
        ),
        None,
    )
    if alvo is None:
        return ["auditar_ledger_contra_evidencia não existe"]

    # (1) assinatura
    nomes = [argumento.arg for argumento in alvo.args.args]
    if "raiz" not in nomes:
        errors.append(
            "auditar_ledger_contra_evidencia não recebe raiz: sem raiz não há"
            " reabertura, e os estados da matriz voltam a ser conferidos contra"
            " si mesmos"
        )
    elif alvo.args.defaults and len(alvo.args.defaults) >= (
        len(nomes) - nomes.index("raiz")
    ):
        errors.append(
            "raiz tem valor padrão em auditar_ledger_contra_evidencia:"
            " conferência opcional por aridade é o achado A1, e ela não pode"
            " voltar justamente aqui"
        )

    # (2) fluxo de dados: a recontagem alimenta a comparação
    recontagens = [
        no
        for no in ast.walk(alvo)
        if isinstance(no, ast.Assign)
        and isinstance(no.value, ast.Call)
        and isinstance(no.value.func, ast.Name)
        and no.value.func.id == "verificar_inspecao_executada"
    ]
    if not recontagens:
        errors.append(
            "auditar_ledger_contra_evidencia não chama"
            " verificar_inspecao_executada: ela não reabre nada, e 'auditar"
            " contra a evidência' descreve coerência interna"
        )
    else:
        ligados = {
            destino.id
            for atribuicao in recontagens
            for destino in atribuicao.targets
            if isinstance(destino, ast.Name)
        }
        # O valor recontado tem de chegar a `decidir_veredito`. Se o veredito
        # for recomputado de outra coisa, a recontagem é decoração.
        usados_no_veredito = False
        for no in ast.walk(alvo):
            if (
                isinstance(no, ast.Call)
                and isinstance(no.func, ast.Name)
                and no.func.id == "decidir_veredito"
            ):
                for argumento in no.args:
                    for interno in ast.walk(argumento):
                        if isinstance(interno, ast.Name) and interno.id in ligados:
                            usados_no_veredito = True
                        if isinstance(interno, ast.Name) and interno.id == "esperados":
                            usados_no_veredito = True
        if not usados_no_veredito:
            errors.append(
                "o retorno de verificar_inspecao_executada não alimenta"
                " decidir_veredito dentro de auditar_ledger_contra_evidencia:"
                " a recontagem acontece e o veredito continua descendo da"
                " matriz — é exatamente o OI-01"
            )

    # (3) executado — matriz mentirosa é ACUSADA, matriz honesta não é
    with tempfile.TemporaryDirectory(prefix="matriz-") as temporario:
        base = Path(temporario) / "rodada"
        _rodada_minima(base)
        recibos = [
            json.loads(caminho_do_recibo.read_text(encoding="utf-8"))
            for caminho_do_recibo in sorted((base / "recibos").glob("*.json"))
        ]
        processo = _rodar_emissor(base)
        arquivo = base / "AUDIT-LEDGER.json"
        if processo.returncode != 0 or not arquivo.is_file():
            errors.append(
                "CONTROLE FALHOU: o emissor não produziu ledger para a"
                f" recontagem da matriz (exit={processo.returncode})"
            )
            return errors
        honesto = json.loads(arquivo.read_text(encoding="utf-8"))
        if auditar_ledger_contra_evidencia(honesto, recibos, STRUCTURE_ROOT):
            errors.append(
                "CONTROLE FALHOU: o ledger honesto foi acusado pela recontagem"
                " da matriz — trava sempre-vermelha não discrimina nada"
            )
        mentiroso = json.loads(json.dumps(honesto))
        mentiroso["conformity_matrix"]["dimensions"][0]["state"] = "NAO_CONFORME"
        acusacoes = auditar_ledger_contra_evidencia(
            mentiroso, recibos, STRUCTURE_ROOT
        )
        if not any("MATRIZ DIVERGE DA EVIDÊNCIA" in linha for linha in acusacoes):
            errors.append(
                "matriz com estado trocado NÃO é acusada: o campo de onde o"
                " veredito desce continua sendo conferido contra si mesmo"
            )

        # ------------------------------------------------------------------
        # CONSOLE × ENVELOPE, exercitado na TRAVA REAL.
        # ------------------------------------------------------------------
        # Uma âncora é quebrada num recibo em disco: a inspeção rebaixa, a
        # corrida imprime `[REBAIXA]`, e o ledger passa a ter de registrar o
        # rebaixamento em `pending`. Apagar essa linha do `pending` tem de ser
        # ACUSADO — é o que impede o rastro de morrer com o console.
        #
        # A primeira escrita deste caso reimplementava a regra aqui dentro e
        # media a cópia: a mutação que neutralizava a trava real saía VERDE. O
        # caso agora chama `auditar_ledger_contra_evidencia`, e só ela.
        quebrado = json.loads(json.dumps(recibos))
        primeiro = quebrado[0]["dimension_states"][0]
        primeiro["evidence_anchors"][0]["quote"] = (
            "# citação que não existe nesta linha, plantada pelo caso"
        )
        for ancora in primeiro["evidence_anchors"][1:]:
            ancora["quote"] = "# citação que não existe nesta linha, plantada"
        rebaixado = verificar_inspecao_executada(quebrado, STRUCTURE_ROOT)
        if not rebaixado["downgrades"]:
            errors.append(
                "CONTROLE FALHOU: quebrar a citação não produziu rebaixamento,"
                " e sem rebaixamento o caso de console × envelope não mede nada"
            )
        else:
            dimensao = rebaixado["downgrades"][0]["dimension"]
            com_pendencia = json.loads(json.dumps(honesto))
            com_pendencia["conformity_matrix"]["dimensions"] = [
                {
                    **linha,
                    "state": rebaixado["effective_states"].get(
                        linha["dimension"], "NAO_PROVADO"
                    ),
                }
                for linha in com_pendencia["conformity_matrix"]["dimensions"]
            ]
            com_pendencia["internal_verdict"] = "REPROVADO"
            com_pendencia["governance_verdict"] = "NONCOMPLIANT"
            com_pendencia["violations"] = [
                f"{linha['dimension']}: bloqueada."
                for linha in com_pendencia["conformity_matrix"]["dimensions"]
                if linha["state"] in ("NAO_CONFORME", "NAO_PROVADO")
            ]
            com_pendencia["inspection_verification"] = {
                **com_pendencia["inspection_verification"],
                "all_anchors_reverified": False,
                "anchors_failed": rebaixado["anchors_failed"],
            }
            sem_pendencia = json.loads(json.dumps(com_pendencia))
            com_pendencia["pending"] = com_pendencia["pending"] + [
                f"Rebaixada {dimensao} de CONFORME para NAO_PROVADO no papel de"
                f" {rebaixado['downgrades'][0]['auditor_id']}: nenhuma âncora"
                " reabriu."
            ]
            if auditar_ledger_contra_evidencia(
                com_pendencia, quebrado, STRUCTURE_ROOT
            ):
                errors.append(
                    "CONTROLE FALHOU: o ledger que REGISTRA o rebaixamento em"
                    " pending foi acusado — a trava estaria sempre vermelha"
                )
            divergentes = auditar_ledger_contra_evidencia(
                sem_pendencia, quebrado, STRUCTURE_ROOT
            )
            if not any(
                "CONSOLE DIVERGE DO ENVELOPE" in linha for linha in divergentes
            ):
                errors.append(
                    "rebaixamento apagado do pending NÃO é acusado: o que o"
                    " operador viu na tela pode divergir do que o CEO lê na"
                    " barreira, e o único rastro morre com o console"
                )
    return errors


def validate_alegacao_no_envelope() -> list[str]:
    """A alegação de `COMPLIANT` viaja no envelope, e é a que o código produz.

    Frente A da rodada 5. A alegação foi **reduzida** ao que o mecanismo faz —
    *nenhum valor digitado divergente da evidência reaberta* —, e deixou de
    dizer *a evidência não foi forjada*, que `OI-04` mediu em 80 linhas e
    0,031 s. Reduzir a alegação só vale alguma coisa se ela **chegar a quem
    decide**: foi assim que `R6`, `R9` e `R10` falharam até a rodada 3, morando
    em documentação enquanto o envelope não tinha campo para eles.

    Quatro conferências:

    1. o `governanceReport` do CEO **exige** `compliance_claim`;
    2. o `const` de `certifies` e `does_not_certify` no schema é **idêntico** às
       constantes do módulo da trava — alargar a alegação exige duas edições,
       em dois arquivos, e uma só derruba a emissão;
    3. `pending` exige `^R11 `, o teto, por `contains`;
    4. o envelope **emitido**, rodando, carrega os dois textos e o `R11`.
    """
    errors: list[str] = []
    if not CEO_SCHEMA_PATH.is_file():
        return ["schema do CEO ausente"]
    ceo = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))
    relatorio = ceo.get("$defs", {}).get("governanceReport", {})

    if "compliance_claim" not in relatorio.get("required", []):
        errors.append(
            "governanceReport do CEO não exige compliance_claim: a alegação não"
            " alcança quem decide na barreira"
        )
    alegacao = relatorio.get("properties", {}).get("compliance_claim", {})
    propriedades = alegacao.get("properties", {})
    if propriedades.get("certifies", {}).get("const") != ALEGACAO_DO_COMPLIANT:
        errors.append(
            "o const de compliance_claim.certifies no schema do CEO não é o"
            " texto de inspecao_executada.py::ALEGACAO_DO_COMPLIANT: a alegação"
            " publicada e a alegação do código podem divergir em silêncio"
        )
    if (
        propriedades.get("does_not_certify", {}).get("const")
        != NAO_COBERTO_PELA_ALEGACAO
    ):
        errors.append(
            "o const de compliance_claim.does_not_certify no schema do CEO não é"
            " o texto de inspecao_executada.py::NAO_COBERTO_PELA_ALEGACAO"
        )
    pendente = relatorio.get("properties", {}).get("pending", {})
    exigidos = {
        clausula.get("contains", {}).get("pattern")
        for clausula in pendente.get("allOf", [])
    }
    if "^R11 " not in exigidos:
        errors.append(
            "governanceReport do CEO não exige o TETO R11 em pending: o limite"
            " que governa o significado do binário poderia sumir do envelope"
        )
    # RODADA 7, OI6-01 — o TETO por igualdade exata, no schema do CEO.
    teto_no_schema = {
        clausula.get("contains", {}).get("pattern"): clausula.get(
            "contains", {}
        ).get("const")
        for clausula in pendente.get("allOf", [])
    }
    if teto_no_schema.get("^R11 ") != TEXTO_DE_CADA_LIMITE["R11"]:
        errors.append(
            "governanceReport do CEO não exige o TETO R11 por IGUALDADE EXATA:"
            " sob `^R11 ` um teto que diz outra coisa passava, e o teto é o"
            " limite que governa o significado do binário inteiro"
        )

    with tempfile.TemporaryDirectory(prefix="alegacao-") as temporario:
        base = Path(temporario) / "rodada"
        _rodada_minima(base)
        processo = _rodar_emissor(base)
        alvo = base / "GOVERNANCE-REPORT.json"
        if processo.returncode != 0 or not alvo.is_file():
            errors.append(
                "CONTROLE FALHOU: o emissor não produziu envelope para conferir"
                f" a alegação (exit={processo.returncode})"
            )
            return errors
        emitido = json.loads(alvo.read_text(encoding="utf-8"))
        publicada = emitido.get("compliance_claim") or {}
        if publicada.get("certifies") != ALEGACAO_DO_COMPLIANT:
            errors.append(
                "o envelope emitido não carrega a alegação do módulo da trava"
            )
        if publicada.get("does_not_certify") != NAO_COBERTO_PELA_ALEGACAO:
            errors.append(
                "o envelope emitido não carrega o que a alegação NÃO cobre:"
                " quem decide na barreira leria COMPLIANT sem o teto ao lado"
            )
        if not any(
            isinstance(linha, str) and linha.startswith("R11 ")
            for linha in emitido.get("pending", [])
        ):
            errors.append("o envelope emitido não carrega o TETO R11 em pending")
        # RODADA 7 — e o teto que ele carrega é O TEXTO do emissor, byte a byte.
        if not any(
            linha == TEXTO_DE_CADA_LIMITE["R11"]
            for linha in emitido.get("pending", [])
        ):
            errors.append(
                "o envelope emitido carrega um R11 que NÃO é o texto vigente do"
                " emissor: o teto publicado promete outra coisa"
            )
    return errors






def validate_cruzamento_externo() -> list[str]:
    """`OI-03` — a identidade é cruzada com fonte EXTERNA À LINHA.

    O `pattern` do `candidateIdentityCrosscheck` obriga a linha a ser coerente
    **consigo mesma**. Uma linha coerente sobre outro candidato, outra rodada ou
    outro digest passa — e uma linha é escrita por quem quiser, não é derivada
    de nada. O executor independente mediu isso em 2026-08-02 e escreveu a frase
    que fecha o assunto: enquanto o confronto viver na função que DERIVA a
    linha, o instrumento testa o produtor honesto, não a trava.

    Esta trava confere que o confronto vive **fora** da derivação: a linha é
    comparada com os campos irmãos, com a missão em disco e com a árvore em
    disco. Com casos, e com o controle — identidade honesta tem de passar.
    """
    errors: list[str] = []
    try:
        from _compartilhado.verificacoes_pacote import (
            cruzar_identidade_externa,
            montar_linha_de_cruzamento,
        )
    except ImportError as falha:
        return [f"_compartilhado não expõe o cruzamento externo: {falha}"]

    def artefato(
        *,
        declarado: str,
        recomputado: str,
        rodada: int,
        do_plano: int,
        da_missao: int,
        causal_digest: str,
        causal_round: int,
        plano_round: int,
    ) -> dict[str, Any]:
        bloco = {
            "status": "CONFERIDO",
            "recipe": "_compartilhado/verificacoes_pacote.py::digest_de_arvore",
            "candidate_id": "cand-fixture",
            "candidate_root_ref": "candidatos/cand-fixture",
            "declared_digest": declarado,
            "recomputed_digest": recomputado,
            "round_declared": rodada,
            "plan_round": do_plano,
            "mission_round": da_missao,
            "mission_ref": "missao.json",
            "errors": [],
            "checked_at": "2026-08-02T16:00:00-03:00",
        }
        bloco["line"] = montar_linha_de_cruzamento(bloco)
        return {
            "causal": {"candidate_digest": causal_digest, "round": causal_round},
            "plan": {"causal": {"round": plano_round}},
            "candidate_identity": bloco,
        }

    honesto = digest("h")
    outro = digest("o")
    casos: list[tuple[str, dict[str, Any], bool]] = [
        (
            "CONTROLE: identidade honesta, batendo com irmãos, missão e árvore",
            artefato(
                declarado=honesto,
                recomputado=honesto,
                rodada=5,
                do_plano=5,
                da_missao=5,
                causal_digest=honesto,
                causal_round=5,
                plano_round=5,
            ),
            False,
        ),
        (
            "linha auto-consistente sobre OUTRO digest que o irmão não declara",
            artefato(
                declarado=outro,
                recomputado=outro,
                rodada=5,
                do_plano=5,
                da_missao=5,
                causal_digest=honesto,
                causal_round=5,
                plano_round=5,
            ),
            True,
        ),
        (
            "linha auto-consistente sobre OUTRA rodada que o irmão não declara",
            artefato(
                declarado=honesto,
                recomputado=honesto,
                rodada=2,
                do_plano=2,
                da_missao=2,
                causal_digest=honesto,
                causal_round=5,
                plano_round=5,
            ),
            True,
        ),
        (
            "rodada do PLANO divergente da que a linha declara",
            artefato(
                declarado=honesto,
                recomputado=honesto,
                rodada=5,
                do_plano=5,
                da_missao=5,
                causal_digest=honesto,
                causal_round=5,
                plano_round=2,
            ),
            True,
        ),
    ]
    for rotulo, alvo, deve_acusar in casos:
        acusacoes = cruzar_identidade_externa(
            alvo, rodada_da_missao=5, digest_em_disco=honesto
        )
        if deve_acusar and not acusacoes:
            errors.append(f"cruzamento externo NÃO acusou: {rotulo}")
        if not deve_acusar and acusacoes:
            errors.append(
                f"CONTROLE FALHOU: cruzamento externo acusou o honesto — {rotulo}"
                f" — {acusacoes[:2]}"
            )

    # A LINHA que não é a composição dos campos: é a forma pura do defeito.
    forjado = json.loads(json.dumps(casos[0][1]))
    forjado["candidate_identity"]["line"] = forjado["candidate_identity"]["line"].replace(
        "cand-fixture", "cand-outro", 1
    )
    if not cruzar_identidade_externa(
        forjado, rodada_da_missao=5, digest_em_disco=honesto
    ):
        errors.append(
            "linha que NÃO é a composição dos campos irmãos passou: a linha"
            " voltaria a ser texto livre, e é o OI-03"
        )

    # Ausência de fonte externa é ERRO NOMEADO, nunca desligamento silencioso.
    if not cruzar_identidade_externa(
        casos[0][1], rodada_da_missao=None, digest_em_disco=honesto
    ):
        errors.append(
            "missão não conferida passou em silêncio: ausência de fonte externa"
            " tem de aparecer como ausência"
        )
    if not cruzar_identidade_externa(
        casos[0][1], rodada_da_missao=5, digest_em_disco=None
    ):
        errors.append("árvore não conferida passou em silêncio")
    return errors




def validate_evidence_refs_resolvem() -> list[str]:
    """Todo `evidence_ref` da rodada RESOLVE contra a raiz auditada, ou bloqueia.

    Fecha `OI5-04`, CRÍTICO da rodada 5: uma lista digitada apontando para
    arquivo inexistente viajava para o `AUDIT_LEDGER` e para o
    `GOVERNANCE_REPORT` que o CEO lê na barreira, dentro de um `COMPLIANT` exit
    0, com interseção VAZIA em relação ao que a corrida havia reaberto.

    O controle usa arquivos REAIS da árvore — não um diretório de mentira — para
    que o verde signifique "resolve o que existe", e não "resolve o que eu mesmo
    plantei".
    """
    errors: list[str] = []
    raiz = STRUCTURE_ROOT
    reais = [
        PACKAGE_ROOT.joinpath("SKILL.md").relative_to(raiz).as_posix(),
        PACKAGE_ROOT.joinpath("CONTRATO-DE-COMPROMISSO.md").relative_to(raiz).as_posix(),
    ]

    resolvidos, erros = resolver_evidence_refs(reais, raiz)
    if erros or sorted(resolvidos) != sorted(reais):
        errors.append(
            "CONTROLE FALHOU: referências reais foram recusadas"
            f" — {erros}. Trava que recusa o honesto não discrimina nada"
        )

    ataques = (
        ("arquivo inexistente", [f"{reais[0]}", "ceo-maestro/NAO-EXISTE-NUNCA.md"]),
        ("lista vazia", []),
        ("não é lista", "ceo-maestro/SKILL.md"),
        ("caminho absoluto", [str(PACKAGE_ROOT / "SKILL.md")]),
        ("fuga da raiz", ["../fora-da-arvore.md"]),
        ("entrada não textual", [123]),
    )
    for rotulo, refs in ataques:
        _, erros = resolver_evidence_refs(refs, raiz)
        if not erros:
            errors.append(
                f"OI5-04 REABERTO: {rotulo} passou — referência que não resolve"
                " viajaria no envelope que o CEO lê na barreira"
            )
    return errors


# ---------------------------------------------------------------------------
# O RÓTULO NÃO É A TRAVA — rodada 5, e é um achado da própria prova de mutação
# ---------------------------------------------------------------------------
#
# `CASOS_OBRIGATORIOS` confere que o RÓTULO de cada caso continua na bateria. A
# prova de mutação desta rodada mostrou o que isso não cobre: trocar
#
#     ("a matriz é RECONTADA da evidência, não lida para decidir", True,
#      validate_matriz_recontada())
#
# por
#
#     ("a matriz é RECONTADA da evidência, não lida para decidir", True,
#      [])
#
# preserva o rótulo, preserva a contagem, e **apaga a trava**. A bateria saiu
# 157/157, verde. É a neutralização por efeito que `OI-05` mediu nas travas da
# rodada 4, reaparecendo dentro da conferência que existia para pegá-la — a
# mesma curva que esta frente inteira vem medindo.
#
# A correção liga o rótulo à FUNÇÃO, por AST: cada caso obrigatório declara qual
# validador tem de ser **chamado** dentro dele. Rótulo sem chamada é erro.
#
# Limite declarado, e ele é honesto: quem editar esta tabela junto com o `run()`
# derruba as duas coisas na mesma passada. O que se ganha é que a queda deixa de
# custar uma edição e passa a custar três — a chamada, o rótulo e a tabela — e a
# prova de mutação exibe cada uma.
VALOR_MEDIDO_DO_CONTEXTO = "O revisor leu o artefato do produtor antes de inspecionar; a contaminacao foi medida em 2 dos 3 insumos e esta declarada."
CAMPO_DO_CONTEXTO = "context_notes"


# ===========================================================================
# RODADA 8 — AS TRES TRAVAS QUE PROTEGEM O QUE O PACOTE AINDA AFIRMA
# ===========================================================================
#
# Nenhuma delas defende alegacao nova. Cada uma protege algo que o pacote
# continua afirmando depois da extracao:
#
# 1. o pacote afirma a PROPRIA IDENTIDADE — e `C07` mediu que a arvore reproduz
#    com o manifesto mentiroso dentro dela;
# 2. o recibo afirma o CONTEXTO do revisor — e o schema premiava quem mentia;
# 3. todo envelope afirma um `producer_digest` — e a receita so existia em prosa.


def _pacote_de_candidato(base: Path, nome: str, conteudo: dict[str, str]) -> Path:
    """Monta em disco um pacote de candidato minimo, com manifesto DERIVADO."""
    raiz = base / nome
    (raiz / "overlay").mkdir(parents=True, exist_ok=True)
    arquivos = []
    for relativo, texto in sorted(conteudo.items()):
        alvo = raiz / "overlay" / relativo
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(texto, encoding="utf-8")
        arquivos.append(
            {
                "caminho_alvo": relativo,
                "arquivo_no_candidato": f"overlay/{relativo}",
                "estado": "NOVO",
                "bytes_antes": 0,
                "bytes_depois": alvo.stat().st_size,
                "sha256_antes": "n/a:arquivo novo",
                "sha256_depois": "sha256:"
                + hashlib.sha256(alvo.read_bytes()).hexdigest(),
            }
        )
    (raiz / "manifest.json").write_text(
        json.dumps(
            {"candidate_id": nome, "arquivos": arquivos}, ensure_ascii=False, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    return raiz


def validate_manifesto_do_candidato() -> list[str]:
    """O manifesto entregue descreve o PROPRIO candidato — executado, com controle.

    `C07` da rodada 7, falha critica: o `manifest.json` entregue como `cand-G` era
    byte-identico ao do `cand-F`, declarava `candidate_id: cand-F-gate-satisfazivel`
    e 8 dos 13 `sha256_depois` eram do overlay do F. **A arvore reproduzia** — o
    manifesto mentiroso e membro dela, e `digest_de_arvore` autentica a declaracao
    falsa junto com o resto. Trava propria, porque digest de arvore nao detecta.

    Tres medidas, e a primeira e o CONTROLE: sem ela, uma trava que reprova sempre
    passaria por trava que discrimina.
    """
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="manifesto-r8-") as temporario:
        base = Path(temporario)
        p = _pacote_de_candidato(base, "cand-P-honesto", {"a.txt": "alfa\n"})
        q = _pacote_de_candidato(
            base, "cand-Q-honesto", {"a.txt": "alfa\n", "b.txt": "beta\n"}
        )

        # 1. CONTROLE — pacote honesto tem de sair CONFERIDO.
        for pacote in (p, q):
            resultado = conferir_manifesto_do_candidato(pacote)
            if resultado["status"] != "CONFERIDO":
                errors.append(
                    f"CONTROLE FALHOU: {pacote.name} honesto saiu"
                    f" {resultado['status']} — {resultado['reason']}"
                )

        # 2. O CASO DE `C07` — o manifesto de OUTRO candidato viaja dentro deste.
        (q / "manifest.json").write_text(
            (p / "manifest.json").read_text(encoding="utf-8"), encoding="utf-8"
        )
        mentiroso = conferir_manifesto_do_candidato(q)
        if mentiroso["status"] != "DIVERGENTE":
            errors.append(
                "C07 REABERTO: o manifesto de cand-P dentro de cand-Q saiu"
                f" {mentiroso['status']} — o pacote entregue nao diz de si a verdade"
                " e a trava nao acusa"
            )
        elif not any("cand-P-honesto" in erro for erro in mentiroso["errors"]):
            errors.append(
                "a recusa nao NOMEIA o candidato que o manifesto declara ser:"
                " bloqueio anonimo e bloqueio que ninguem endereca"
            )

        # 3. AUSENCIA PERMANECE AUSENCIA — raiz sem manifesto nao vira CONFERIDO.
        sem = base / "sem-manifesto"
        sem.mkdir()
        vazio = conferir_manifesto_do_candidato(sem)
        if vazio["status"] != "SEM_MANIFESTO":
            errors.append(
                f"raiz sem manifest.json saiu {vazio['status']}: ausencia de"
                " conferencia tem de permanecer ausencia, com nome proprio"
            )

    # 4. O EMISSOR BLOQUEIA, e o schema PROIBE o par COMPLIANT/DIVERGENTE.
    fonte = EMITTER_PATH.read_text(encoding="utf-8")
    if "conferir_manifesto_do_candidato(raiz_do_candidato)" not in fonte:
        errors.append(
            "o emissor nao chama conferir_manifesto_do_candidato sobre a raiz do"
            " candidato: trava sem call site no fluxo real protege o eval, nao a"
            " operacao"
        )
    if "BLOCKED_MANIFESTO_NAO_DESCREVE_O_PROPRIO_CANDIDATO" not in fonte:
        errors.append("o emissor nao nomeia a recusa do manifesto divergente")
    return errors


def validate_contexto_medido_no_schema() -> list[str]:
    """`context_clean` e BOOLEANO MEDIDO — o recibo honesto de contexto sujo PASSA.

    Achado da propria Auditoria contra ela mesma, na rodada 7: `context_clean` era
    `const true`, entao **o schema premiava o recibo que mente**. Dois inspetores
    relataram contexto contaminado e SAIRAM DO SCHEMA por isso — honestidade virou
    violacao de formato, dentro do instrumento que julga as outras.
    """
    errors: list[str] = []
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    cadeia = schema["$defs"]["auditReceipt"]["properties"]["review_chain"]
    if cadeia["properties"]["context_clean"].get("const") is True:
        errors.append(
            "context_clean continua `const true`: o schema segue premiando o"
            " recibo que mente e expulsando o inspetor honesto"
        )
    if cadeia["properties"]["context_clean"].get("type") != "boolean":
        errors.append("context_clean nao e booleano no schema")

    honesto = audit_receipt()
    honesto["review_chain"]["context_clean"] = False
    honesto["review_chain"][CAMPO_DO_CONTEXTO] = VALOR_MEDIDO_DO_CONTEXTO
    erros_do_honesto = validate_schema(honesto, schema, schema)
    if erros_do_honesto:
        errors.append(
            "RECIBO HONESTO DE CONTEXTO SUJO FOI RECUSADO PELO SCHEMA:"
            f" {erros_do_honesto[:2]} — e exatamente o defeito que esta trava"
            " existe para fechar"
        )

    calado = audit_receipt()
    calado["review_chain"]["context_clean"] = False
    if not validate_schema(calado, schema, schema):
        errors.append(
            "recibo que declara contexto sujo SEM a medicao ao lado passou no"
            " schema: limite sem medicao e limite decorativo"
        )

    limpo = audit_receipt()
    if validate_schema(limpo, schema, schema):
        errors.append("CONTROLE FALHOU: recibo de contexto limpo foi recusado")
    return errors


def validate_receita_do_producer_digest() -> list[str]:
    """A receita do `producer_digest` e NORMATIVA no schema, e diz que objeto hasheia.

    Achado contra o ceo-maestro na rodada 7: a receita so existia em **prosa nao
    normativa**, e por isso um leitor diligente concluiu "bate com NENHUM" e a
    acusacao de forjadura saiu plausivel e falsa. Alcance medido: 17 envelopes em
    7 rodadas. Aviso em prosa nao previne erro; schema previne.
    """
    errors: list[str] = []
    for rotulo, caminho in (
        ("departamento", SCHEMA_PATH),
        ("CEO", CEO_SCHEMA_PATH),
    ):
        schema = json.loads(caminho.read_text(encoding="utf-8"))
        cabecalho = schema["$defs"].get("causalHeader")
        if cabecalho is None:
            errors.append(f"{rotulo}: sem causalHeader")
            continue
        if "producer_digest_recipe" not in cabecalho.get("required", []):
            errors.append(
                f"{rotulo}: producer_digest_recipe nao e obrigatorio no cabecalho"
                " causal — a receita volta a viver so em prosa"
            )
        campo = cabecalho.get("properties", {}).get("producer_digest_recipe")
        if not isinstance(campo, dict) or not (campo.get("enum") or campo.get("pattern")):
            errors.append(
                f"{rotulo}: producer_digest_recipe sem enum nem pattern — campo"
                " livre nao constrange nada"
            )

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    sem_receita = audit_ledger()
    sem_receita["causal"] = dict(sem_receita["causal"])
    sem_receita["causal"].pop("producer_digest_recipe", None)
    if not validate_schema(sem_receita, schema, schema):
        errors.append(
            "ledger SEM producer_digest_recipe passou no schema: o campo existe e"
            " nao e exigido, que e o mesmo que nao existir"
        )
    return errors


TRAVA_DE_CADA_CASO = {
    "call site de cada trava no fluxo real": "validate_call_site",
    "anchors_total é contado da evidência, não lido": "validate_numeros_contados",
    "todo evidence_ref resolve contra a raiz auditada":
        "validate_evidence_refs_resolvem",
    "o ledger emitido é confrontado com os recibos em disco":
        "validate_ledger_auditado_executado",
    "os três limites alcançam o envelope da barreira": "validate_limites_no_envelope",
    "o passo 7 descreve os dois ramos, e os dois acontecem":
        "validate_dois_ramos_do_passo_7",
    "conferência de identidade não é opcional por aridade de argv":
        "validate_identidade_nao_opcional",
    "toda invocação publicada passa pelas travas": "validate_documented_usage",
    "o caminho documentado, executado, barra digest falso":
        "validate_caminho_documentado_executado",
    "gate de identidade escrito no schema do CEO": "validate_ceo_gate_identidade",
    "a matriz é RECONTADA da evidência, não lida para decidir":
        "validate_matriz_recontada",
    "a alegação de COMPLIANT viaja no envelope da barreira":
        "validate_alegacao_no_envelope",
    "a identidade é cruzada com fonte externa à linha":
        "validate_cruzamento_externo",
    "a bateria liga cada caso obrigatório à trava dele":
        "validate_casos_ligados_a_travas",
    "nenhuma trava deste arquivo está inerte":
        "validate_nenhuma_trava_esta_inerte",
    # RODADA 8 — as tres travas que protegem o que o pacote AINDA afirma.
    "o manifesto entregue descreve o próprio candidato":
        "validate_manifesto_do_candidato",
    "context_clean é booleano medido e o recibo honesto passa":
        "validate_contexto_medido_no_schema",
    "a receita do producer_digest é normativa no schema":
        "validate_receita_do_producer_digest",
    # T71 — o campo `independent` deixa de ser preenchido e jamais lido.
    "gate de independência do painel escrito no schema do CEO":
        "validate_ceo_gate_independencia",
    "o emissor real deriva a independência do painel":
        "validate_emissor_deriva_independencia",
}


# ---------------------------------------------------------------------------
# RODADA 7 — A TRAVA INERTE, QUE O RÓTULO E A CONTAGEM NÃO PEGAM
# ---------------------------------------------------------------------------
#
# `validate_casos_ligados_a_travas` liga o RÓTULO à CHAMADA por AST, e foi um
# ganho real da rodada 5. `OI6-04` mediu o que ela não cobre, e eu reproduzi a
# medição contra o meu próprio conserto antes de entregá-lo:
#
#     def validate_produtor_confere_com_a_raiz() -> list[str]:
#         return []
#
# O rótulo continua na bateria. A chamada continua no `run()`. `CASOS_OBRIGATORIOS`
# continua satisfeito. A contagem continua 171/171, exit 0 — VERDE, com a trava
# morta. Medido aqui em 2026-08-02: mutante `M-R7-02`, um escape em três.
#
# A conferência abaixo é estrutural: uma função `validate_*` cujo corpo, tirada a
# docstring, seja UM `return` de coleção vazia não está verificando nada.
#
# LIMITE DECLARADO, e ele é um ponto fixo que não fecha aqui: esvaziar ESTA
# função também a desliga, porque uma varredura que não roda não acha nada. O que
# se ganha é preço — a inertização passa a custar DUAS edições, esta e a da trava
# alvo, e a prova de mutação exibe as duas. Fechar de verdade exige a bateria ser
# executada por instrumento que não more dentro dela, e isso é outra frente.
def _corpo_inerte(funcao: ast.FunctionDef) -> bool:
    """`True` quando o corpo, tirada a docstring, é um `return` de vazio."""
    corpo = list(funcao.body)
    if (
        corpo
        and isinstance(corpo[0], ast.Expr)
        and isinstance(corpo[0].value, ast.Constant)
        and isinstance(corpo[0].value.value, str)
    ):
        corpo = corpo[1:]
    if len(corpo) != 1 or not isinstance(corpo[0], ast.Return):
        return False
    valor = corpo[0].value
    if valor is None:
        return True
    if isinstance(valor, (ast.List, ast.Tuple, ast.Set)) and not valor.elts:
        return True
    if isinstance(valor, ast.Dict) and not valor.keys:
        return True
    # `return set(), []` e afins — tupla de coleções todas vazias.
    if isinstance(valor, ast.Tuple) and valor.elts:
        return all(
            (isinstance(elemento, (ast.List, ast.Tuple, ast.Set)) and not elemento.elts)
            or (
                isinstance(elemento, ast.Call)
                and isinstance(elemento.func, ast.Name)
                and elemento.func.id in {"set", "list", "dict", "tuple"}
                and not elemento.args
            )
            for elemento in valor.elts
        )
    return False


def _travas_inertes() -> list[str]:
    """As `validate_*` deste arquivo cujo corpo não verifica nada."""
    arvore = ast.parse(Path(__file__).resolve().read_text(encoding="utf-8"))
    return sorted(
        no.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.FunctionDef)
        and no.name.startswith("validate_")
        and _corpo_inerte(no)
    )


def validate_nenhuma_trava_esta_inerte() -> list[str]:
    """Nenhuma `validate_*` deste arquivo tem corpo que não verifica nada.

    RODADA 7, ressalva do `C02`. `OI6-04` mediu que esvaziar UMA trava por vez
    mantinha a bateria do pacote verde e o total dos quinze em 1783/1788, delta
    ZERO — e o defeito reapareceu nas travas que a rodada 6 criou, inclusive numa
    que EU acrescentei nesta rodada (mutante `M-R7-02`, medido antes da entrega).

    Verde não é aprovação: é pergunta. Esta trava faz a pergunta estruturalmente.
    """
    inertes = _travas_inertes()
    return [
        f"TRAVA INERTE: {nome} tem corpo que devolve vazio sem verificar nada."
        " O rótulo, a contagem e o caso obrigatório continuam de pé e a trava não"
        " decide — é a neutralização por efeito que OI6-04 mediu"
        for nome in inertes
    ]


def validate_casos_ligados_a_travas() -> list[str]:
    """Cada caso obrigatório CHAMA a trava dele — conferido na AST, não no texto.

    Três conferências, e a terceira é a que fecha o ponto fixo:

    1. todo rótulo de `TRAVA_DE_CADA_CASO` aparece num `cases.append` do `run()`
       **com uma chamada** à função declarada;
    2. toda função `validate_*` definida no arquivo é chamada em algum lugar —
       trava definida e nunca chamada é o `M11` da rodada 1;
    3. **esta própria conferência** está em `TRAVA_DE_CADA_CASO` e em
       `CASOS_OBRIGATORIOS`. Uma trava que não se autoexige erode: a lição está
       registrada, e aqui ela é aplicada à trava que a aplica.
    """
    errors: list[str] = []
    fonte = Path(__file__).resolve()
    arvore = ast.parse(fonte.read_text(encoding="utf-8"))

    entrada = next(
        (
            no
            for no in ast.walk(arvore)
            if isinstance(no, ast.FunctionDef) and no.name == "run"
        ),
        None,
    )
    if entrada is None:
        return ["run() não existe: a bateria não tem ponto de entrada"]

    # rótulo -> funções chamadas dentro da tupla daquele `cases.append`
    chamadas_por_rotulo: dict[str, set[str]] = {}
    for no in ast.walk(entrada):
        if not (
            isinstance(no, ast.Call)
            and isinstance(no.func, ast.Attribute)
            and no.func.attr == "append"
            and isinstance(no.func.value, ast.Name)
            and no.func.value.id == "cases"
        ):
            continue
        if not no.args or not isinstance(no.args[0], ast.Tuple):
            continue
        tupla = no.args[0]
        if not tupla.elts or not isinstance(tupla.elts[0], ast.Constant):
            continue
        rotulo = tupla.elts[0].value
        if not isinstance(rotulo, str):
            continue
        nomes = {
            interno.func.id
            for interno in ast.walk(tupla)
            if isinstance(interno, ast.Call) and isinstance(interno.func, ast.Name)
        }
        chamadas_por_rotulo.setdefault(rotulo, set()).update(nomes)

    for rotulo, funcao in sorted(TRAVA_DE_CADA_CASO.items()):
        if rotulo not in chamadas_por_rotulo:
            errors.append(
                f"caso obrigatório ausente do run(): {rotulo!r} — a trava"
                f" {funcao} não é exercitada por caso algum"
            )
            continue
        if funcao not in chamadas_por_rotulo[rotulo]:
            errors.append(
                f"RÓTULO SEM TRAVA: o caso {rotulo!r} está na bateria e NÃO"
                f" chama {funcao}. Rótulo, contagem e caso obrigatório"
                " continuam de pé, e a trava não decide — é a neutralização"
                " por efeito"
            )

    definidas = {
        no.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.FunctionDef) and no.name.startswith("validate_")
    }
    chamadas = {
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }
    orfas = sorted(nome for nome in definidas if nome not in chamadas)
    for nome in orfas:
        errors.append(
            f"trava definida e NUNCA chamada: {nome} — fica vermelha quando"
            " mutada e não protege nada, que é o achado M11 da rodada 1"
        )

    if "a bateria liga cada caso obrigatório à trava dele" not in TRAVA_DE_CADA_CASO:
        errors.append(
            "esta conferência não se autoexige: TRAVA_DE_CADA_CASO não inclui o"
            " próprio caso que a exercita, e trava que não se autoexige erode"
        )

    # RODADA 7 — a mesma conferência de inertez roda AQUI também, de propósito.
    #
    # Ela já tem trava própria (`validate_nenhuma_trava_esta_inerte`). Repetir
    # não é redundância: é PREÇO. Inertizar uma trava passa a exigir esvaziar
    # também estas DUAS, e a prova de mutação exibe cada edição. É a mesma
    # disciplina de três lugares que a alegação de `COMPLIANT` já usa.
    for nome in _travas_inertes():
        errors.append(
            f"TRAVA INERTE (segunda linha): {nome} devolve vazio sem verificar"
            " nada, e o rótulo com a chamada continua satisfeito — o par"
            " rótulo↔chamada não alcança o CORPO (OI6-04)"
        )
    return errors


CASOS_OBRIGATORIOS = (
    "call site de cada trava no fluxo real",
    "anchors_total é contado da evidência, não lido",
    "todo evidence_ref resolve contra a raiz auditada",
    "o ledger emitido é confrontado com os recibos em disco",
    "os três limites alcançam o envelope da barreira",
    "o passo 7 descreve os dois ramos, e os dois acontecem",
    "conferência de identidade não é opcional por aridade de argv",
    "toda invocação publicada passa pelas travas",
    "o caminho documentado, executado, barra digest falso",
    "gate de identidade escrito no schema do CEO",
    "ledger rejeita COMPLIANT com identidade não conferida",
    "CEO rejeita COMPLIANT com identidade não conferida",
    "sem raiz declarada a identidade sai NAO_CONFERIDO, nunca CONFERIDO",
    "gate do COMPLIANT continua escrito no schema",
    "ADR-003: nenhum campo de nota no schema",
    "recibo rejeita CONFORME sem âncora que reabra",
    "ledger rejeita COMPLIANT com âncora que não reabriu",
    "ledger rejeita COMPLIANT com all_anchors_reverified false, sozinho",
    "âncora sobre arquivo real reabre",
    "âncora com citação que não está na linha não reabre",
    "método sem contrato em disco continua MISSING",
    "NAO_PROVADO nunca é promovido, nem com âncora e método",
    "inspeção apenas afirmada fecha NONCOMPLIANT",
    "consumidor rejeita candidate_digest de outra receita",
    "a matriz é RECONTADA da evidência, não lida para decidir",
    "a alegação de COMPLIANT viaja no envelope da barreira",
    "a identidade é cruzada com fonte externa à linha",
    "a bateria liga cada caso obrigatório à trava dele",
    "nenhuma trava deste arquivo está inerte",
    "o manifesto entregue descreve o próprio candidato",
    "context_clean é booleano medido e o recibo honesto passa",
    "a receita do producer_digest é normativa no schema",
    # T71
    "gate de independência do painel escrito no schema do CEO",
    "o emissor real deriva a independência do painel",
    "ledger rejeita COMPLIANT com inspetor não independente",
    "CEO rejeita COMPLIANT com painel não independente",
    "painel vazio não é independência",
)

# Piso de casos. Contagem que cai sem FAIL é regressão: um `cases.append` que
# some não produz vermelho nenhum, só um total menor que ninguém confere.
#
# T71 — o piso sobe de 155 para 160 junto com os 5 casos desta frente, medidos:
# 170/170 antes, 175/175 depois. Piso que não acompanha o acréscimo aceita, na
# rodada seguinte, que os 5 sumam sem vermelho nenhum.
MINIMO_DE_CASOS = 160


# Estrutura normativa do gate, DENTRO do validador.
#
# O schema é uma trava, e uma trava também erode. A mutação M12 afrouxou
# `all_anchors_reverified` de `const: true` para `type: boolean` e o validador
# ficou verde, porque outra restrição da mesma cláusula ainda pegava o caso
# negativo. Um caso de fixture cobre um caminho; ele não garante que a **regra**
# continua escrita. Por isso a cláusula é conferida como texto normativo.
GATE_DO_COMPLIANT = {
    "all_anchors_reverified": {"const": True},
    "anchors_failed": {"const": 0},
    "methods_failed": {"const": 0},
    "anchors_total": {"minimum": 10},
}

# Segunda fonte de dados do gate, e é de propósito que seja outra.
#
# Os Juízes registraram, em `C03`, que as cinco exigências novas do ramo
# `COMPLIANT` da rodada 1 desciam todas de UMA fonte — o relatório de
# `verificar_inspecao_executada` —, e que uma barra sustentada por uma única
# medida parece maior do que é. A identidade do candidato vem de outro lugar:
# `conferir_candidate_digest` sobre a árvore em disco. Derrubar as duas exige
# fabricar duas coisas independentes.
GATE_DA_IDENTIDADE = {"status": {"const": "CONFERIDO"}}

# T71 — TERCEIRA fonte de dados do gate, e de novo é de propósito que seja outra.
#
# `inspection_verification` desce da reabertura das âncoras; `candidate_identity`
# desce do digest recomputado sobre a árvore. A independência desce de outro lugar
# ainda: do que CADA inspetor declarou no próprio recibo, em `review_chain`. São
# três medidas de origens distintas, e derrubar as três exige fabricar três coisas
# independentes.
#
# A forma é `items`, não `properties`, porque a promessa do contrato é
# quantificada: "CADA recibo usado é válido, independente e rastreável". Um item
# não independente no painel derruba o COMPLIANT inteiro.
GATE_DA_INDEPENDENCIA = {"independent": {"const": True}}


def validate_schema_gates(schema: dict[str, Any]) -> list[str]:
    """O ramo `COMPLIANT` do ledger exige, literalmente, as quatro condições."""
    errors: list[str] = []
    ledger = schema.get("$defs", {}).get("auditLedger", {})
    ramo = None
    for clausula in ledger.get("allOf", []):
        se = clausula.get("if", {}).get("properties", {}).get("internal_verdict", {})
        if se.get("const") == "REPROVADO":
            ramo = clausula.get("else", {}).get("properties", {})
            break
    if ramo is None:
        return ["schema sem o ramo que deriva COMPLIANT de internal_verdict"]

    for campo, esperado in (
        ("governance_verdict", {"const": "COMPLIANT"}),
        ("violations", {"maxItems": 0}),
        ("capability_gaps", {"maxItems": 0}),
        ("dossier_missing", {"maxItems": 0}),
        ("assignments", {"minItems": 1}),
        ("method_executions", {"minItems": 1}),
    ):
        if ramo.get(campo) != esperado:
            errors.append(
                f"gate do COMPLIANT afrouxado em {campo}: esperado {esperado},"
                f" encontrado {ramo.get(campo)}"
            )

    verificacao = ramo.get("inspection_verification", {}).get("properties", {})
    for campo, esperado in GATE_DO_COMPLIANT.items():
        if verificacao.get(campo) != esperado:
            errors.append(
                f"gate do COMPLIANT afrouxado em inspection_verification.{campo}:"
                f" esperado {esperado}, encontrado {verificacao.get(campo)}"
            )

    identidade = ramo.get("candidate_identity", {}).get("properties", {})
    for campo, esperado in GATE_DA_IDENTIDADE.items():
        if identidade.get(campo) != esperado:
            errors.append(
                f"gate do COMPLIANT afrouxado em candidate_identity.{campo}:"
                f" esperado {esperado}, encontrado {identidade.get(campo)}"
            )

    # T71 — a independência do painel, na camada onde o painel existe.
    painel = ramo.get("panel", {}).get("items", {}).get("properties", {})
    for campo, esperado in GATE_DA_INDEPENDENCIA.items():
        if painel.get(campo) != esperado:
            errors.append(
                f"gate do COMPLIANT afrouxado em panel.items.{campo}: esperado"
                f" {esperado}, encontrado {painel.get(campo)} — sem esta"
                " exigência o campo volta a ser preenchido e jamais lido, e"
                " recibo não independente fecha COMPLIANT (FIND-REMED7-C08-CA-01)"
            )
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
        "evidenceAnchor",
        "inspectionMethod",
        "methodExecution",
        "inspectionVerification",
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
    cases.append(("todo pacote gerente tem validador que roda a trava global", True, validate_cobertura_de_validadores(STRUCTURE_ROOT)))
    cases.append(("contratos de gerente na anatomia canônica", True, validate_contratos_de_gerente(STRUCTURE_ROOT)))
    cases.append(("anatomia de contrato acusa raiz inexistente", False, validate_contratos_de_gerente(STRUCTURE_ROOT / "pacote-inexistente-t97")))
    cases.append(("a recusa de digest() dispara e ninguém tem cópia privada do motor", True, validate_trava_de_digest(STRUCTURE_ROOT)))
    cases.append(("nenhuma asserção é verdadeira por construção sobre valor produzido", True, validate_sem_check_tautologico(STRUCTURE_ROOT)))
    cases.append(("nenhum placar de pacote declara total de cadeia como estado corrente", True, validate_placar_nao_declara_cadeia(STRUCTURE_ROOT)))
    cases.append(("a contagem publicada aponta para o digest do instrumento vigente", True, validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)))
    cases.append(("as travas do modulo compartilhado nao estao neutralizadas", True, validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT)))
    cases.append(("toda pendencia declarada nomeia quem responde por ela", True, validate_pendencia_tem_dono(STRUCTURE_ROOT)))
    cases.append(("a fonte normativa confere com o valor declarado em ORIGEM.md", True, validate_fonte_normativa_conferida(STRUCTURE_ROOT)))
    cases.append(("call site de cada trava no fluxo real", True, validate_call_site()))
    cases.append(
        ("conferência de identidade não é opcional por aridade de argv", True,
         validate_identidade_nao_opcional())
    )
    cases.append(
        ("toda invocação publicada passa pelas travas", True,
         validate_documented_usage())
    )
    cases.append(
        ("o caminho documentado, executado, barra digest falso", True,
         validate_caminho_documentado_executado())
    )
    cases.append(
        ("gate de identidade escrito no schema do CEO", True,
         validate_ceo_gate_identidade())
    )
    cases.append(
        ("gate de independência do painel escrito no schema do CEO", True,
         validate_ceo_gate_independencia())
    )
    cases.append(
        ("o emissor real deriva a independência do painel", True,
         validate_emissor_deriva_independencia())
    )
    cases.append(
        ("anchors_total é contado da evidência, não lido", True,
         validate_numeros_contados())
    )
    cases.append(
        ("todo evidence_ref resolve contra a raiz auditada", True,
         validate_evidence_refs_resolvem())
    )
    cases.append(
        ("o ledger emitido é confrontado com os recibos em disco", True,
         validate_ledger_auditado_executado())
    )
    cases.append(
        ("os três limites alcançam o envelope da barreira", True,
         validate_limites_no_envelope())
    )
    cases.append(
        ("o passo 7 descreve os dois ramos, e os dois acontecem", True,
         validate_dois_ramos_do_passo_7())
    )
    # --- RODADA 5 -------------------------------------------------------
    cases.append(
        ("a matriz é RECONTADA da evidência, não lida para decidir", True,
         validate_matriz_recontada())
    )
    cases.append(
        ("a alegação de COMPLIANT viaja no envelope da barreira", True,
         validate_alegacao_no_envelope())
    )
    cases.append(
        ("a identidade é cruzada com fonte externa à linha", True,
         validate_cruzamento_externo())
    )
    cases.append(
        ("a bateria liga cada caso obrigatório à trava dele", True,
         validate_casos_ligados_a_travas())
    )
    # RODADA 7, ressalva do C02 — o par rótulo↔chamada não alcança o CORPO.
    cases.append(
        ("nenhuma trava deste arquivo está inerte", True,
         validate_nenhuma_trava_esta_inerte())
    )
    cases.append(
        ("o manifesto entregue descreve o próprio candidato", True,
         validate_manifesto_do_candidato())
    )
    cases.append(
        ("context_clean é booleano medido e o recibo honesto passa", True,
         validate_contexto_medido_no_schema())
    )
    cases.append(
        ("a receita do producer_digest é normativa no schema", True,
         validate_receita_do_producer_digest())
    )
    cases.append(("gate do COMPLIANT continua escrito no schema", True, validate_schema_gates(schema)))
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

    # --- RODADA 7, OI6-01: OS QUATRO LIMITES POR IGUALDADE EXATA -----------
    #
    # O ataque que `OI6-01` executou, dentro da bateria. Sob o prefixo aberto
    # `["R6 x", "R9 x", "R10 x", "R11 x"]` satisfazia schema E barreira; sob o
    # `const` ao lado do `pattern`, cada um cai — e há um caso por limite, porque
    # caso que viola quatro condições de uma vez continua vermelho quando três
    # são neutralizadas, e a mutação sai verde.
    prefixo_vazio = audit_ledger()
    prefixo_vazio["pending"] = ["R6 x", "R9 x", "R10 x", "R11 x"]
    cases.append(
        ("ledger rejeita os quatro limites por PREFIXO com texto qualquer", False,
         validate_schema(prefixo_vazio, schema, schema))
    )

    for _limite in ("R6", "R9", "R10", "R11"):
        _texto_trocado = audit_ledger()
        _texto_trocado["pending"] = [
            f"{_limite} — texto que respeita o prefixo e não é o limite"
            if linha.startswith(f"{_limite} ")
            else linha
            for linha in _texto_trocado["pending"]
        ]
        cases.append(
            (f"ledger rejeita {_limite} que respeita o prefixo mas não é o texto",
             False, validate_schema(_texto_trocado, schema, schema))
        )


    _origem_com_carimbo = audit_ledger()
    cases.append(
        ("ledger com os quatro carimbos de rodada e alvo é aceito", True,
         validate_schema(_origem_com_carimbo, schema, schema))
    )

    to_ceo = audit_ledger()
    to_ceo["return_to"] = "ceo-maestro"
    cases.append(
        ("ledger rejeita retorno fora do Diretor", False,
         validate_schema(to_ceo, schema, schema))
    )

    # --- inspeção executada: o schema exige âncora e método -----------------

    sem_metodo = audit_receipt()
    sem_metodo.pop("method")
    cases.append(
        ("recibo rejeita ausência do método executado", False,
         validate_schema(sem_metodo, schema, schema))
    )

    conforme_sem_ancora = audit_receipt(states={"INTENT": "CONFORME"})
    conforme_sem_ancora["dimension_states"][0]["evidence_anchors"] = []
    cases.append(
        ("recibo rejeita CONFORME sem âncora que reabra", False,
         validate_schema(conforme_sem_ancora, schema, schema))
    )

    na_sem_ancora = audit_receipt(states={"INTENT": "NAO_APLICAVEL"})
    na_sem_ancora["dimension_states"][0]["evidence_anchors"] = []
    cases.append(
        ("recibo rejeita NAO_APLICAVEL sem âncora (mitiga R7)", False,
         validate_schema(na_sem_ancora, schema, schema))
    )

    citacao_curta = audit_receipt(states={"INTENT": "CONFORME"})
    citacao_curta["dimension_states"][0]["evidence_anchors"][0]["quote"] = "{"
    cases.append(
        ("recibo rejeita citação curta demais para ancorar", False,
         validate_schema(citacao_curta, schema, schema))
    )

    linha_zero = audit_receipt(states={"INTENT": "CONFORME"})
    linha_zero["dimension_states"][0]["evidence_anchors"][0]["line"] = 0
    cases.append(
        ("recibo rejeita âncora sem número de linha válido", False,
         validate_schema(linha_zero, schema, schema))
    )

    nao_provado_sem_ancora = audit_receipt(states={"INTENT": "NAO_PROVADO"})
    cases.append(
        ("recibo aceita NAO_PROVADO sem âncora — é o estado que declara a ausência", True,
         validate_schema(nao_provado_sem_ancora, schema, schema))
    )

    modo_inventado = audit_receipt()
    modo_inventado["method"]["execution_mode"] = "GERENTE_AFIRMA"
    cases.append(
        ("recibo rejeita modo de execução fora dos dois declarados", False,
         validate_schema(modo_inventado, schema, schema))
    )

    # --- identidade do candidato: o campo que a rodada 1 não tinha ----------
    #
    # Sem estes casos, `candidate_identity` seria um campo bonito que nada
    # obriga. O primeiro é o gate; o segundo prova que o estado não pode mentir
    # sobre si mesmo; o terceiro prova que declarar a ausência continua sendo
    # emissão legítima — `NONCOMPLIANT` com a razão na cara.

    identidade_nao_conferida = audit_ledger(
        identity=candidate_identity("NAO_CONFERIDO")
    )
    cases.append(
        ("ledger rejeita COMPLIANT com identidade não conferida", False,
         validate_schema(identidade_nao_conferida, schema, schema))
    )




    alegacao_alargada = audit_ledger()
    alegacao_alargada["compliance_claim"]["does_not_certify"] = (
        "nenhum limite: este mecanismo certifica que a evidência não foi forjada"
    )
    cases.append(
        ("ledger rejeita alegação alargada por edição do envelope", False,
         validate_schema(alegacao_alargada, schema, schema))
    )

    sem_teto = audit_ledger()
    sem_teto["pending"] = [
        linha for linha in sem_teto["pending"] if not linha.startswith("R11 ")
    ]
    cases.append(
        ("ledger rejeita envelope sem o TETO R11 em pending", False,
         validate_schema(sem_teto, schema, schema))
    )

    identidade_incoerente = audit_ledger()
    identidade_incoerente["candidate_identity"]["status"] = "NAO_CONFERIDO"
    cases.append(
        ("ledger rejeita NAO_CONFERIDO exibindo a raiz que teria conferido", False,
         validate_schema(identidade_incoerente, schema, schema))
    )

    identidade_declarada = audit_ledger(
        {**{d: "CONFORME" for d in DIMENSIONS}, "EVIDENCIA": "NAO_PROVADO"},
        identity=candidate_identity("NAO_CONFERIDO"),
    )
    cases.append(
        ("ledger aceita NONCOMPLIANT declarando identidade não conferida", True,
         validate_schema(identidade_declarada, schema, schema))
    )

    # --- o ledger não fecha COMPLIANT sem inspeção reaberta ------------------

    sem_reabertura = audit_ledger(
        verification=inspection_verification(reverified=False, anchors_failed=3)
    )
    cases.append(
        ("ledger rejeita COMPLIANT com âncora que não reabriu", False,
         validate_schema(sem_reabertura, schema, schema))
    )

    # Isola `all_anchors_reverified`: as outras três condições da cláusula estão
    # satisfeitas, e só o booleano está falso. Sem este caso, afrouxar o `const`
    # passaria despercebido — foi assim que a mutação M12 escapou na primeira
    # rodada, com o caso vizinho pegando o artefato pelo `anchors_failed`.
    so_o_booleano = audit_ledger(
        verification=inspection_verification(reverified=False)
    )
    cases.append(
        ("ledger rejeita COMPLIANT com all_anchors_reverified false, sozinho", False,
         validate_schema(so_o_booleano, schema, schema))
    )

    poucas_ancoras = audit_ledger()
    poucas_ancoras["inspection_verification"]["anchors_total"] = 0
    cases.append(
        ("ledger rejeita COMPLIANT sem âncora nenhuma para reabrir", False,
         validate_schema(poucas_ancoras, schema, schema))
    )

    metodo_falho = audit_ledger(
        verification=inspection_verification(reverified=True, methods_failed=1)
    )
    cases.append(
        ("ledger rejeita COMPLIANT com método não conferido", False,
         validate_schema(metodo_falho, schema, schema))
    )

    sem_execucao = audit_ledger(with_methods=False)
    cases.append(
        ("ledger rejeita COMPLIANT sem registro de método executado", False,
         validate_schema(sem_execucao, schema, schema))
    )

    verificador_trocado = audit_ledger()
    verificador_trocado["inspection_verification"]["verified_by"] = "a gerente conferiu"
    cases.append(
        ("ledger rejeita verificação que não veio do motor", False,
         validate_schema(verificador_trocado, schema, schema))
    )

    reprovado_com_lacuna = audit_ledger(
        {**{d: "CONFORME" for d in DIMENSIONS}, "EVIDENCIA": "NAO_PROVADO"},
        verification=inspection_verification(reverified=False, anchors_failed=2),
    )
    cases.append(
        ("ledger aceita NONCOMPLIANT declarando que a inspeção não reabriu", True,
         validate_schema(reprovado_com_lacuna, schema, schema))
    )

    # --- reabertura de âncora, contra arquivos reais em disco ---------------
    #
    # Estes casos CHAMAM a trava. É o que impede que ela vire decoração: se
    # `reverificar_ancora` parar de reprovar, os negativos abaixo caem.

    boa = ancora_real()
    cases.append(
        ("âncora sobre arquivo real reabre", True,
         reverificar_ancora(boa, STRUCTURE_ROOT))
    )

    linha_errada = dict(boa, line=boa["line"] + 3)
    cases.append(
        ("âncora na linha errada não reabre", False,
         reverificar_ancora(linha_errada, STRUCTURE_ROOT))
    )

    digest_errado = dict(boa, file_digest=digest("c"))
    cases.append(
        ("âncora sobre versão errada do arquivo não reabre", False,
         reverificar_ancora(digest_errado, STRUCTURE_ROOT))
    )

    arquivo_ausente = dict(boa, artifact_ref="ceo-maestro/nao-existe-em-disco.md")
    cases.append(
        ("âncora para arquivo inexistente não reabre", False,
         reverificar_ancora(arquivo_ausente, STRUCTURE_ROOT))
    )

    fuga = dict(boa, artifact_ref="../fora-da-raiz-auditada.md")
    cases.append(
        ("âncora que escapa da raiz auditada não reabre", False,
         reverificar_ancora(fuga, STRUCTURE_ROOT))
    )

    citacao_falsa = dict(boa, quote="texto que nunca esteve nessa linha")
    cases.append(
        ("âncora com citação que não está na linha não reabre", False,
         reverificar_ancora(citacao_falsa, STRUCTURE_ROOT))
    )

    linha_fora = dict(boa, line=10**7)
    cases.append(
        ("âncora além do fim do arquivo não reabre", False,
         reverificar_ancora(linha_fora, STRUCTURE_ROOT))
    )

    # --- método: o contrato do agente foi mesmo aberto ----------------------

    metodo_ok = metodo_real("agente-conferir-evidencias-e-artefatos")
    cases.append(
        ("método sobre contrato de agente real confere", True,
         conferir_metodo(metodo_ok, STRUCTURE_ROOT))
    )

    metodo_nao_lido = dict(metodo_ok, obrigacoes_declaradas=999)
    cases.append(
        ("método com contagem de obrigações que não bate: contrato não foi lido", False,
         conferir_metodo(metodo_nao_lido, STRUCTURE_ROOT))
    )

    metodo_barreira = dict(metodo_ok, barreira_de_saida_declarada=0)
    cases.append(
        ("método com barreira de saída que não bate: contrato não foi lido", False,
         conferir_metodo(metodo_barreira, STRUCTURE_ROOT))
    )

    metodo_ausente = dict(
        metodo_ok, agent_contract_ref="ceo-maestro/agente-que-nao-existe/CONTRATO.md"
    )
    cases.append(
        ("método sem contrato em disco continua MISSING", False,
         conferir_metodo(metodo_ausente, STRUCTURE_ROOT))
    )

    # --- a regra de rebaixamento, e a direção única -------------------------

    rebaixa = [
        ("CONFORME sem âncora vira NAO_PROVADO",
         estado_efetivo("CONFORME", ancoras_validas=0, metodo_conferido=True)
         == "NAO_PROVADO"),
        ("RESSALVA sem âncora vira NAO_PROVADO",
         estado_efetivo("RESSALVA", ancoras_validas=0, metodo_conferido=True)
         == "NAO_PROVADO"),
        ("NAO_CONFORME sem âncora vira NAO_PROVADO",
         estado_efetivo("NAO_CONFORME", ancoras_validas=0, metodo_conferido=True)
         == "NAO_PROVADO"),
        ("NAO_APLICAVEL sem âncora vira NAO_PROVADO",
         estado_efetivo("NAO_APLICAVEL", ancoras_validas=0, metodo_conferido=True)
         == "NAO_PROVADO"),
        ("CONFORME com âncora permanece CONFORME",
         estado_efetivo("CONFORME", ancoras_validas=1, metodo_conferido=True)
         == "CONFORME"),
        ("método não conferido rebaixa mesmo com âncora",
         estado_efetivo("CONFORME", ancoras_validas=9, metodo_conferido=False)
         == "NAO_PROVADO"),
        ("NAO_PROVADO nunca é promovido, nem com âncora e método",
         estado_efetivo("NAO_PROVADO", ancoras_validas=9, metodo_conferido=True)
         == "NAO_PROVADO"),
        ("estado inventado cai para NAO_PROVADO",
         estado_efetivo("APROVADO", ancoras_validas=9, metodo_conferido=True)
         == "NAO_PROVADO"),
        ("os quatro estados que afirmam algo exigem âncora",
         set(ESTADOS_QUE_EXIGEM_ANCORA)
         == {"CONFORME", "RESSALVA", "NAO_CONFORME", "NAO_APLICAVEL"}),
    ]
    for name, passed in rebaixa:
        cases.append((name, True, [] if passed else ["condição comportamental falhou"]))

    # --- ponta a ponta: com inspeção e sem inspeção -------------------------

    executada = [audit_receipt(name) for name in AGENT_NAMES]
    relatorio_executada = verificar_inspecao_executada(executada, STRUCTURE_ROOT)
    estados_executada = {
        dim: relatorio_executada["effective_states"].get(dim, "NAO_PROVADO")
        for dim in DIMENSIONS
    }

    afirmada = copy.deepcopy(executada)
    for recibo in afirmada:
        for linha in recibo["dimension_states"]:
            linha["evidence_anchors"] = []
    relatorio_afirmada = verificar_inspecao_executada(afirmada, STRUCTURE_ROOT)
    estados_afirmada = {
        dim: relatorio_afirmada["effective_states"].get(dim, "NAO_PROVADO")
        for dim in DIMENSIONS
    }

    ponta_a_ponta = [
        ("inspeção executada reabre todas as âncoras",
         relatorio_executada["all_anchors_reverified"] is True
         and relatorio_executada["anchors_failed"] == 0),
        ("inspeção executada cobre as dez dimensões",
         set(relatorio_executada["effective_states"]) == set(DIMENSIONS)),
        ("inspeção executada fecha COMPLIANT",
         derivar_binario(decidir_veredito(estados_executada)) == "COMPLIANT"),
        ("inspeção apenas afirmada não reabre nada",
         relatorio_afirmada["all_anchors_reverified"] is False
         or relatorio_afirmada["anchors_total"] == 0),
        ("inspeção apenas afirmada rebaixa as dez dimensões",
         all(estado == "NAO_PROVADO" for estado in estados_afirmada.values())),
        ("inspeção apenas afirmada fecha NONCOMPLIANT",
         derivar_binario(decidir_veredito(estados_afirmada)) == "NONCOMPLIANT"),
        ("cada rebaixamento é nomeado, não silencioso",
         len(relatorio_afirmada["downgrades"]) == len(DIMENSIONS) + len(SECONDARY)),
    ]
    for name, passed in ponta_a_ponta:
        cases.append((name, True, [] if passed else ["condição comportamental falhou"]))

    # --- receita de candidate_digest: produtor e consumidor -----------------

    digest_do_pacote = candidate_digest_de_arvore(PACKAGE_ROOT)

    def _digest_de_arvore_reproduz_por_reimplementacao() -> bool:
        """A receita publicada, reescrita aqui do zero, chega ao MESMO valor.

        **O que estava nesta linha até 2026-08-05.** `re.fullmatch(
        r"sha256:[0-9a-f]{64}", digest_do_pacote)` — e `digest_do_pacote` sai de
        `candidate_digest_de_arvore`, que devolve sempre essa forma. Verdadeiro
        por construção: a linha não podia ficar vermelha, logo não media nada.

        **De onde ela veio.** Da rodada 1 desta mesma tarefa, que substituiu
        `digest_do_pacote.startswith("sha256:") and len(...) == 71` por um
        `re.fullmatch` sobre o mesmo sujeito produzido. Trocou a forma da
        tautologia, não a tautologia. Quem a encontrou foi o detector estrutural
        da rodada 2, um dia depois — nenhum dos seis juízes a tinha visto.

        **O que esta versão mede.** A única coisa que um digest publicado
        promete: que outra pessoa, lendo a receita, chegue ao mesmo número. Esta
        função é essa outra pessoa — reimplementa os oito passos do docstring de
        `digest_de_arvore` sem chamá-la, e compara. Se a receita mudar sem que o
        docstring mude, isto fica vermelho.
        """
        linhas: list[str] = []
        for caminho in PACKAGE_ROOT.rglob("*"):
            if not caminho.is_file():
                continue
            relativo = caminho.relative_to(PACKAGE_ROOT)
            if "__pycache__" in relativo.parts:
                continue
            linhas.append(
                f"{hashlib.sha256(caminho.read_bytes()).hexdigest()}  "
                f"{relativo.as_posix()}"
            )
        linhas.sort(key=lambda linha: linha.split("  ", 1)[1])
        manifesto = "".join(f"{linha}\n" for linha in linhas)
        recomputado = "sha256:" + hashlib.sha256(
            manifesto.encode("utf-8")
        ).hexdigest()
        return recomputado == digest_do_pacote
    def _digest_de_arvore_responde_a_conteudo() -> bool:
        """Duas árvores mínimas que diferem por UM byte têm de dar digests diferentes.

        Formato e determinismo não provam isto: uma função que devolvesse
        sempre a mesma constante passaria nos dois. O que faz o digest servir
        para alguma coisa é responder ao conteúdo, e isso só se prova mudando
        o conteúdo e olhando o valor.
        """
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a" / "sub"
            b = Path(tmp) / "b" / "sub"
            a.mkdir(parents=True)
            b.mkdir(parents=True)
            (a / "f.txt").write_bytes(b"conteudo")
            (b / "f.txt").write_bytes(b"conteudA")
            return candidate_digest_de_arvore(a.parent) != candidate_digest_de_arvore(
                b.parent
            )

    receita = [
        ("a receita publicada REPRODUZ por reimplementação independente",
         _digest_de_arvore_reproduz_por_reimplementacao()),
        ("a receita RESPONDE a conteúdo: um byte a mais muda o digest",
         _digest_de_arvore_responde_a_conteudo()),
        ("a receita é determinística: duas chamadas, um valor",
         candidate_digest_de_arvore(PACKAGE_ROOT) == digest_do_pacote),
        ("__pycache__ não entra na identidade",
         candidate_digest_de_arvore(PACKAGE_ROOT)
         == candidate_digest_de_arvore(PACKAGE_ROOT, excluir=("__pycache__",))),
    ]
    for name, passed in receita:
        cases.append((name, True, [] if passed else ["condição comportamental falhou"]))

    cases.append(
        ("consumidor aceita candidate_digest recomputado pela receita", True,
         conferir_candidate_digest(PACKAGE_ROOT, digest_do_pacote))
    )
    cases.append(
        ("consumidor rejeita candidate_digest de outra receita", False,
         conferir_candidate_digest(PACKAGE_ROOT, digest("d")))
    )
    cases.append(
        ("consumidor rejeita candidate_digest sem o prefixo sha256:", False,
         conferir_candidate_digest(PACKAGE_ROOT, digest_do_pacote[7:]))
    )
    cases.append(
        ("consumidor rejeita candidate_digest de árvore ausente", False,
         conferir_candidate_digest(PACKAGE_ROOT / "nao-existe", digest_do_pacote))
    )

    # --- a conferência de identidade, chamada de verdade --------------------
    #
    # Três desfechos, três casos. O do meio é o que a rodada 1 não tinha: sem
    # raiz declarada, o resultado é NAO_CONFERIDO — e não um envelope
    # indistinguível do conferido.

    momento = "2026-08-01T18:00:00-03:00"
    identidade_ok = conferir_identidade_do_candidato(
        PACKAGE_ROOT,
        "rodada.json::candidate_root",
        digest_do_pacote,
        momento,
        conferir_manifesto_do_candidato(PACKAGE_ROOT),
    )
    identidade_ma = conferir_identidade_do_candidato(
        PACKAGE_ROOT,
        "rodada.json::candidate_root",
        digest("d"),
        momento,
        conferir_manifesto_do_candidato(PACKAGE_ROOT),
    )
    identidade_sem_raiz = conferir_identidade_do_candidato(
        None,
        "ausente",
        digest_do_pacote,
        momento,
        conferir_manifesto_do_candidato(None),
    )
    ledger_conferido = audit_ledger()
    identidade_casos = [
        ("identidade confere quando o digest recomputa pela receita",
         identidade_ok["status"] == "CONFERIDO"),
        ("identidade divergente bloqueia e nomeia o erro",
         identidade_ma["status"] == "DIVERGENTE" and bool(identidade_ma["errors"])),
        ("sem raiz declarada a identidade sai NAO_CONFERIDO, nunca CONFERIDO",
         identidade_sem_raiz["status"] == "NAO_CONFERIDO"),
        ("a raiz sai de rodada.json quando o argv não a passa",
         resolver_raiz_do_candidato(
             ["x", "rodada", "raiz"], {"candidate_root": "ceo-maestro"}, STRUCTURE_ROOT
         )[1] == "rodada.json::candidate_root"),
        ("sem candidate_root e sem argv[3] não há raiz, e isso é declarado",
         resolver_raiz_do_candidato(["x", "rodada", "raiz"], {}, STRUCTURE_ROOT)
         == (None, "ausente")),
        ("o estado da identidade chega ao envelope que o CEO lê",
         derive_governance_report(ledger_conferido)["candidate_identity_status"]
         == ledger_conferido["candidate_identity"]["status"]),
    ]
    for name, passed in identidade_casos:
        cases.append((name, True, [] if passed else ["condição comportamental falhou"]))

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

    ceo_sem_identidade = derive_governance_report(approved_ledger)
    ceo_sem_identidade.pop("candidate_identity_status")
    cases.append(
        ("CEO rejeita COMPLIANT sem o estado da identidade", False,
         validate_schema(ceo_sem_identidade, governance_def, ceo_schema))
    )

    ceo_identidade_ausente = derive_governance_report(approved_ledger)
    ceo_identidade_ausente["candidate_identity_status"] = "NAO_CONFERIDO"
    cases.append(
        ("CEO rejeita COMPLIANT com identidade não conferida", False,
         validate_schema(ceo_identidade_ausente, governance_def, ceo_schema))
    )

    # --- T71: a independência do painel, nas duas camadas e no derivador -----
    #
    # A mesma mutação atravessa as duas: um inspetor não independente derruba o
    # ledger E o envelope. Antes desta frente as duas aceitavam.
    painel_sujo = copy.deepcopy(approved_ledger)
    painel_sujo["panel"][0]["independent"] = False
    cases.append(
        ("ledger rejeita COMPLIANT com inspetor não independente", False,
         validate_schema(painel_sujo, schema, schema))
    )
    cases.append(
        ("CEO rejeita COMPLIANT com painel não independente", False,
         validate_schema(
             derive_governance_report(painel_sujo), governance_def, ceo_schema
         ))
    )

    # `all([])` é True. Sem o guarda, painel vazio sairia INDEPENDENTE — trava
    # que se satisfaz com ZERO inspetor é o oposto do que o contrato promete.
    painel_vazio = copy.deepcopy(approved_ledger)
    painel_vazio["panel"] = []
    cases.append(
        ("painel vazio não é independência", True,
         [] if derive_governance_report(painel_vazio)["panel_independence_status"]
         == "NAO_INDEPENDENTE"
         else ["painel vazio saiu INDEPENDENTE: a armadilha do all([]) está aberta"])
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


    # --- rodada 4: as travas novas, chamadas de verdade --------------------
    #
    # Três eixos por trava. Aqui está o eixo COMPORTAMENTAL: a função é chamada
    # com entrada construída e o resultado é confrontado. Os outros dois são o
    # estático (`validate_numeros_contados`, sobre a AST) e o executado
    # (`validate_ledger_auditado_executado`, que roda o emissor como processo).
    recibo_com_duas = audit_receipt()
    recibo_sem_ancora = audit_receipt()
    for _linha in recibo_sem_ancora["dimension_states"]:
        _linha["evidence_anchors"] = []
    contagem_real = contar_ancoras_declaradas([recibo_com_duas])
    contagem_vazia = contar_ancoras_declaradas([recibo_sem_ancora])
    bloco_ok, divergencias_ok = consolidar_inspecao(
        [recibo_com_duas],
        {
            "anchors_total": contagem_real["anchors_total"],
            "anchors_failed": 0,
            "methods_total": 1,
            "methods_failed": 0,
        },
    )
    _bloco_mentiroso, divergencias_mentira = consolidar_inspecao(
        [recibo_sem_ancora],
        {
            "anchors_total": 12,
            "anchors_failed": 0,
            "methods_total": 1,
            "methods_failed": 0,
        },
    )
    ledger_para_auditar = audit_ledger()
    ledger_mentiroso = audit_ledger()
    ledger_mentiroso["inspection_verification"] = dict(
        ledger_mentiroso["inspection_verification"]
    )
    ledger_mentiroso["inspection_verification"]["anchors_total"] = 999
    recibos_do_ledger = [
        audit_receipt(auditor=_nome) for _nome in AGENT_NAMES
    ]
    cruzamento_ok = cruzar_identidade_dos_recibos(
        [recibo_com_duas],
        recibo_com_duas["candidate_digest"],
        recibo_com_duas["contract_digest"],
    )
    cruzamento_trocado = cruzar_identidade_dos_recibos(
        [recibo_com_duas], digest("e"), recibo_com_duas["contract_digest"]
    )

    comportamentais = [
        ("a contagem enxerga as âncoras que existem",
         contagem_real["anchors_total"] > 0),
        ("a contagem devolve zero quando não há âncora",
         contagem_vazia["anchors_total"] == 0),
        ("methods_total é o número de recibos, contado",
         contagem_real["methods_total"] == 1),
        ("o bloco consolidado publica o total CONTADO",
         bloco_ok["anchors_total"] == contagem_real["anchors_total"]),
        ("consolidação íntegra não acusa divergência", divergencias_ok == []),
        ("total declarado 12 sobre zero âncoras é ACUSADO",
         any("anchors_total" in linha for linha in divergencias_mentira)),
        ("all_anchors_reverified é derivado, não copiado",
         consolidar_inspecao(
             [recibo_com_duas],
             {"anchors_total": contagem_real["anchors_total"],
              "anchors_failed": 1, "methods_total": 1, "methods_failed": 0},
         )[0]["all_anchors_reverified"] is False),
        ("recibo do próprio candidato cruza", cruzamento_ok == []),
        ("recibo de outro candidato é ACUSADO no cruzamento",
         any("candidate_digest" in linha for linha in cruzamento_trocado)),
        ("ledger com anchors_total inflado é ACUSADO contra a evidência",
         any("anchors_total" in linha
             for linha in auditar_ledger_contra_evidencia(
                 ledger_mentiroso, recibos_do_ledger, STRUCTURE_ROOT))),
        ("a auditoria contra evidência não acusa o que não é acusável",
         all("anchors_total" not in linha
             for linha in auditar_ledger_contra_evidencia(
                 {**ledger_para_auditar,
                  "inspection_verification": {
                      **ledger_para_auditar["inspection_verification"],
                      "anchors_total": contar_ancoras_declaradas(
                          recibos_do_ledger)["anchors_total"],
                      "methods_total": len(recibos_do_ledger)}},
                 recibos_do_ledger, STRUCTURE_ROOT))),
    ]
    for name, passed in comportamentais:
        cases.append((name, True, [] if passed else ["condição comportamental falhou"]))

    # --- a bateria confere a si mesma, no ponto de entrada -----------------
    rotulos = {name for name, _, _ in cases}
    ausentes = [rotulo for rotulo in CASOS_OBRIGATORIOS if rotulo not in rotulos]
    cases.append(
        ("nenhum caso obrigatório sumiu da bateria", True,
         [f"caso obrigatório ausente: {rotulo}" for rotulo in ausentes])
    )
    cases.append(
        ("a bateria não encolheu abaixo do piso", True,
         [] if len(cases) >= MINIMO_DE_CASOS
         else [f"bateria com {len(cases)} casos, piso é {MINIMO_DE_CASOS}"])
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
