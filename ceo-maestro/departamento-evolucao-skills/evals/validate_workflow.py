"""Validador determinístico do Departamento de Evolução de Skills.

Verifica o pacote (arquivos, metadata, links), o schema interno, os artefatos
internos e o envelope EXECUTIVE_SUBMISSION contra o schema-raiz do CEO
(nao $def extraida), com fixture em disco, MISSION fail-closed (nao-dict
e invalida; helper em run()) e cobertura que isenta isolamento*/root/otica.
C02_PACKAGE_ROOT so desvia o pacote na prova; o default e o diretorio pai.

Uso: python evals/validate_workflow.py
"""

from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(
    os.environ.get(
        "C02_PACKAGE_ROOT", str(Path(__file__).resolve().parents[1])
    )
)
SKILL_PATH = PACKAGE_ROOT / "SKILL.md"
CONTRACT_PATH = PACKAGE_ROOT / "CONTRATO-DE-COMPROMISSO.md"
OPENAI_PATH = PACKAGE_ROOT / "agents" / "openai.yaml"
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-evolucao-skills.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
AGENTS_ROOT = PACKAGE_ROOT / "agentes"

CEO_ROOT = PACKAGE_ROOT.parent
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(CEO_ROOT.parent))
).resolve()
CEO_SCHEMA_PATH = CEO_ROOT / "schemas" / "ceo-maestro.schema.json"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"

DEPARTMENT = "departamento-evolucao-skills"
AGENT_NAMES = [
    "agente-colheita-e-diagnostico",
    "agente-mineracao-externa",
    "agente-curador-de-candidatos",
    "agente-prova-de-evolucao",
]
AGENT_KIND = {
    "agente-colheita-e-diagnostico": "DIAGNOSTICO",
    "agente-mineracao-externa": "GEM",
    "agente-curador-de-candidatos": "CANDIDATO",
    "agente-prova-de-evolucao": "PROVA",
}
RULES_LINK_DEPARTMENT = "../../regras-de-ouro/REGRAS-DE-OURO.md"
RULES_LINK_AGENT = "../../../../regras-de-ouro/REGRAS-DE-OURO.md"

# ADR-004: aqui não se promove, não se pontua e não se escolhe vencedor.
FORBIDDEN_KEYS = {
    "score",
    "nota",
    "minimum_score",
    "absolute_score",
    "verdict",
    "winner",
    "promoted",
    "promotion",
    "selo",
}

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        collect_property_names,
        conferir_digest_das_regras,
        digest,
        find_const,
        sha256_file,
        sha256_texto_normalizado,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        cruzar_identidade_externa,
        montar_linha_de_cruzamento,
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
        COBERTURA_EXCECOES,
        validate_adr_series,
        validate_cobertura_de_validadores,
        validate_fonte_normativa_conferida,
        validate_placar_nao_declara_cadeia,
        SELO_DE_CONTAGEM,
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

def dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """`a` domina `b`: nunca pior em nenhum caso comparável, melhor em pelo menos um.

    Caso em que qualquer um dos dois deu `skip` não é comparável e fica fora.
    """
    comparable = [
        case
        for case in set(a) & set(b)
        if not str(a[case]).startswith("skip") and not str(b[case]).startswith("skip")
    ]
    if not comparable:
        return False
    value = {"passou": 1, "falhou": 0}
    if any(value[a[case]] < value[b[case]] for case in comparable):
        return False
    return any(value[a[case]] > value[b[case]] for case in comparable)


def frontier(candidates: dict[str, dict[str, Any]]) -> list[str]:
    """Não dominados. Empate mantém os dois — não há desempate aqui."""
    return sorted(
        name
        for name in candidates
        if not any(
            dominates(candidates[other], candidates[name])
            for other in candidates
            if other != name
        )
    )


def mean(results: dict[str, Any]) -> float:
    value = {"passou": 1.0, "falhou": 0.0}
    scored = [value[v] for v in results.values() if not str(v).startswith("skip")]
    return sum(scored) / len(scored) if scored else 0.0


def accepts_candidate(delta_lines: int, removed_text: str) -> bool:
    """Anti-sedimento: candidato que cresce sem remover nada é rejeitado."""
    return delta_lines <= 0 or len(removed_text) >= 20


def prover_is_independent(writer: str, prover: str) -> bool:
    return writer != prover


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

CONTRACT = digest("0")
PRODUCER = digest("1")


def causal(producer: str = DEPARTMENT) -> dict[str, Any]:
    return {
        "work_item_id": "work-002",
        "front_id": "front-evolucao",
        "handoff_id": "handoff-002",
        "message_id": "message-evolucao-001",
        "causation_message_ids": ["message-ceo-002"],
        "contract_id": "contract-002",
        "contract_version": 1,
        "contract_digest": CONTRACT,
        "candidate_digest": "n/a",
        "round": 1,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": PRODUCER,
        "producer_digest_recipe": (
            "_compartilhado/validador_schema.py::sha256_file sobre o SKILL.md do produtor"
        ),
        "created_at": "2026-07-26T22:00:00-03:00",
    }


GAP_TEXT = (
    "A skill não dispara sem ser nomeada quando o pedido usa a palavra do usuário."
)
EXCERPT = (
    "trecho do transcript: o agente respondeu direto, sem invocar a skill, e resumiu"
    " o passo de verificação"
)


def front(material: str = "mineracao") -> dict[str, Any]:
    return {
        "front_ref": "front-acionamento",
        "gap": GAP_TEXT,
        "evidence_excerpt": EXCERPT,
        "targets": ["skills/java-jdbc-dao/SKILL.md", "skills/java-service-usecase/SKILL.md"],
        "reach": 2,
        "denominator": 4,
        "material": material,
    }


def evolution_plan(mode: str = "EVOLUCAO") -> dict[str, Any]:
    return {
        "artifact_type": "EVOLUTION_PLAN",
        "evolution_plan_id": "evolution-plan-001",
        "causal": causal(),
        "executive_mission_ref": "mission-002",
        "mode": mode,
        "fronts": [front()],
        "created_at": "2026-07-26T22:05:00-03:00",
    }


def evolution_task(worker: str = "agente-colheita-e-diagnostico") -> dict[str, Any]:
    kind = AGENT_KIND[worker]
    task: dict[str, Any] = {
        "artifact_type": "EVOLUTION_TASK",
        "task_id": f"task-{worker}",
        "causal": causal(),
        "worker_id": worker,
        "kind": kind,
        "front_ref": "front-acionamento",
        "gap": GAP_TEXT,
        "targets": ["skills/java-jdbc-dao/SKILL.md"],
        "inputs": ["evidencia/transcript-eval-01.md"],
        "forbidden_context": [
            "preferência da gerente ou candidato favorito",
            "retornos dos outros agentes",
            "veredito ou nota desejada",
            "identidade de quem escreveu o candidato",
        ],
        "stop_when": ["A frente tem todos os alvos cobertos ou em SKIP."],
        "return_to": DEPARTMENT,
        "issued_at": "2026-07-26T22:10:00-03:00",
    }
    if kind == "PROVA":
        task["candidate_labels"] = ["cand-A", "cand-B"]
    return task


def gap_item() -> dict[str, Any]:
    return {
        "gap": GAP_TEXT,
        "evidence_excerpt": EXCERPT,
        "signals": {"acionou": "N", "aderiu": "—", "contorno": "skill não invocada"},
        "targets_affected": ["skills/java-jdbc-dao/SKILL.md"],
        "reach": 2,
        "denominator": 4,
    }


def gem_item(licenca: str = "MIT", degrau: int = 2) -> dict[str, Any]:
    return {
        "gem_id": "gem-001",
        "gap_alvo": GAP_TEXT,
        "fonte_url": "https://arxiv.org/abs/2507.19457",
        "fonte_titulo": "GEPA: Reflective Prompt Evolution",
        "fonte_versao": "v1 / 2026-07",
        "acessado_em": "2026-07-26T21:00:00-03:00",
        "licenca": licenca,
        "o_que_e": "Manter fronteira de Pareto em vez de campeão único, por instância.",
        "limite_declarado": "Números medidos com métrica automática, ausente aqui.",
        "degrau_proposto": degrau,
        "adaptacao": "Aplicar a fronteira sobre casos de eval desta casa.",
    }


def candidate_item(
    candidate_id: str = "cand-descricao",
    delta_lines: int = -4,
    removed: str = "removida a frase genérica de acionamento e o parágrafo duplicado",
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "gap_ref": GAP_TEXT,
        "abordagem": "atacar a description, para corrigir acionamento",
        "change_summary": "Description passa a citar as frases reais observadas no transcript.",
        "removed_text": removed,
        "delta_lines": delta_lines,
    }


def scoreboard_line(
    label: str = "cand-A",
    case_id: str = "eval-01",
    baseline: str = "falhou",
    pos: str = "passou",
) -> dict[str, Any]:
    return {
        "candidate_label": label,
        "case_id": case_id,
        "origem": "real",
        "baseline": baseline,
        "pos": pos,
        "acionou": "S" if pos == "passou" else "N",
        "aderiu": "S" if pos == "passou" else "—",
        "excerpt": "trecho do transcript da execução",
    }


def evolution_return(kind: str = "DIAGNOSTICO", status: str = "COMPLETED") -> dict[str, Any]:
    worker = next(name for name, k in AGENT_KIND.items() if k == kind)
    result: dict[str, Any] = {
        "artifact_type": "EVOLUTION_RETURN",
        "task_id": f"task-{worker}",
        "worker_id": worker,
        "kind": kind,
        "gaps": [gap_item()] if kind == "DIAGNOSTICO" else [],
        "gems": [gem_item()] if kind == "GEM" else [],
        "candidates": (
            [candidate_item("cand-descricao"), candidate_item("cand-corpo")]
            if kind == "CANDIDATO"
            else []
        ),
        "scoreboard": (
            [scoreboard_line("cand-A"), scoreboard_line("cand-B", pos="falhou")]
            if kind == "PROVA"
            else []
        ),
        "pending": ["R6 — a existência das tarefas não é verificável pelo runtime."],
        "status": status,
        "return_to": DEPARTMENT,
        "issued_at": "2026-07-26T22:40:00-03:00",
    }
    if kind == "GEM":
        result["saturation"] = "2 rodadas com menos de 2 gems líquidos-novos: saturado."
    if status == "BLOCKED":
        result["gaps"] = []
        result["gems"] = []
        result["candidates"] = []
        result["scoreboard"] = []
        result["blocked_reason"] = "Candidato escrito por este agente: conflito de prova."
    return result


def candidate_set() -> dict[str, Any]:
    return {
        "artifact_type": "CANDIDATE_SET",
        "candidate_set_id": "candidate-set-001",
        "causal": causal(),
        "front_ref": "front-acionamento",
        "items": [
            {
                "candidate_id": "cand-descricao",
                "candidate_label": "cand-A",
                "status": "FRONTEIRA",
                "dominated_by": "n/a",
                "diversidade": False,
            },
            {
                "candidate_id": "cand-corpo",
                "candidate_label": "cand-B",
                "status": "FRONTEIRA",
                "dominated_by": "n/a",
                "diversidade": True,
            },
        ],
        "created_at": "2026-07-26T23:00:00-03:00",
    }


def capability_gap() -> dict[str, Any]:
    return {
        "artifact_type": "EVOLUTION_CAPABILITY_GAP",
        "capability": "Colheita de aprendizagem sem produtor no caminho canônico.",
        "worker_id": "n/a",
        "fronts": ["front-acionamento"],
        "expected_contract": "Relatório de aprendizagem do departamento-registros.",
        "discovery_evidence": "departamento-registros ausente do caminho canônico.",
        "impact": "A frente perde a fonte de lições e abre com TETO_PROVAVEL.",
        "status": "OPEN",
        "owner": "ceo-maestro",
    }



def identity_crosscheck(
    candidate: str = "cand-D-derivado-nao-declarado",
    declared: str | None = None,
    recomputed: str | None = None,
    rodada: int = 4,
    plan_round: int | None = None,
    mission_round: int | None = None,
) -> dict[str, Any]:
    """O cruzamento de identidade, montado como o emissor o monta.

    A `line` e derivada dos campos, e nao digitada ao lado deles: e ela que o
    schema cruza, por retrovisor. Divergiu qualquer um dos tres pares — candidato
    e pasta, declarado e recomputado, as tres rodadas —, o pattern nao casa.
    """
    declared = declared or digest("a")
    recomputed = recomputed if recomputed is not None else declared
    plan_round = rodada if plan_round is None else plan_round
    mission_round = rodada if mission_round is None else mission_round
    linha = (
        f"candidate={candidate}"
        f" root=candidatos/{candidate}"
        f" declared={declared}"
        f" recomputed={recomputed}"
        f" round={rodada}"
        f" plan_round={plan_round}"
        f" mission_round={mission_round}"
    )
    erros: list[str] = []
    if declared != recomputed:
        erros.append(
            f"candidate_digest divergente: declarado {declared}, recomputado {recomputed}"
        )
    if not (rodada == plan_round == mission_round):
        erros.append(
            f"rodada divergente: ledger {rodada}, plano {plan_round}, missao {mission_round}"
        )
    return {
        "status": "CONFERIDO" if not erros else "DIVERGENTE",
        "line": linha,
        "recipe": "_compartilhado/verificacoes_pacote.py::digest_de_arvore",
        "candidate_id": candidate,
        "candidate_root_ref": f"candidatos/{candidate}",
        "declared_digest": declared,
        "recomputed_digest": recomputed,
        "round_declared": rodada,
        "plan_round": plan_round,
        "mission_round": mission_round,
        "mission_ref": "45-EXECUTIVE-MISSION-R4.json",
        "errors": erros,
        "checked_at": "2026-08-02T10:00:00-03:00",
    }



# Os objetos são os SETE da seção 8 do retorno da rodada 6. Os números são de
# FIXTURE — este arquivo é o validador, não o envelope, e número publicado sai
# de execução, não daqui.
_OBJETOS_DAS_AUTODECLARACOES = {
    "AD-1": "classificar() do próprio instrumento decidia por substring",
    "AD-2": "obrigação 7 do contrato: dois candidatos por gap",
    "AD-3": "origem independente da rodada é HERDADA",
    "AD-4": "OI5-05 e OI5-07 alcançam as travas que eu acrescentei",
    "AD-5": "N3 prova que a referência RESOLVE, não que é PERTINENTE",
    "AD-6": "a trava do candidate_producer fecha a OMISSÃO, não a MENTIRA",
    "AD-7": "sobre a minha própria vivacidade eu não afirmo nada",
}






def evolution_ledger(
    mode: str = "EVOLUCAO",
    deliverable: str = "proposal",
    with_assignments: bool = True,
    with_scoreboard: bool = True,
) -> dict[str, Any]:
    return {
        "artifact_type": "EVOLUTION_LEDGER",
        "evolution_ledger_id": "evolution-ledger-001",
        "causal": causal(),
        "executive_mission_ref": "mission-002",
        "mode": mode,
        "deliverable_type": deliverable,
        "plan": evolution_plan(mode),
        "assignments": (
            [
                {
                    "task_id": f"task-{name}",
                    "worker_id": name,
                    "kind": AGENT_KIND[name],
                    "issued_at": "2026-07-26T22:10:00-03:00",
                    "destination": f"evolucao/task-{name}/",
                }
                for name in AGENT_NAMES
            ]
            if with_assignments
            else []
        ),
        "panel": [
            {
                "worker_id": name,
                "kind": AGENT_KIND[name],
                "status": "COMPLETED",
                "substrate": "desconhecido",
                "tier": "desconhecido",
            }
            for name in AGENT_NAMES
        ],
        "scoreboard": (
            [scoreboard_line("cand-A"), scoreboard_line("cand-B", pos="falhou")]
            if with_scoreboard
            else []
        ),
        "candidate_sets": [candidate_set()] if deliverable == "proposal" else [],
        "gems": [gem_item()],
        "metrics": {
            "alcance_total": 2,
            "denominador": 4,
            "material_admitido": 1,
            "casos_novos": 1,
            "vermelho_verde": 1,
        },
        "capability_gaps": [capability_gap()],
        "frentes_encerradas": [],
        "pending": [
            "R6 — a existência das tarefas não é verificável pelo runtime; emissão anexada.",
            "TETO_PROVAVEL não se aplica: a rodada teve material minerado.",
        ],
        "candidate_identity": identity_crosscheck(),
        "return_to": "ceo-maestro",
        "recorded_at": "2026-07-26T23:10:00-03:00",
    }



def _caminho_fixture_de_fronteira() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "executive-submission.json"


def _carregar_fixture_de_fronteira() -> tuple[dict[str, Any] | None, list[str]]:
    """Envelope de fronteira em disco — não é submissão real."""
    caminho = _caminho_fixture_de_fronteira()
    if not caminho.is_file():
        return None, [
            "fixture de fronteira ausente: evals/fixtures/executive-submission.json"
        ]
    try:
        return json.loads(caminho.read_text(encoding="utf-8")), []
    except (OSError, ValueError) as erro:
        return None, [f"fixture de fronteira ilegivel: {erro}"]


def _caminho_fixture_de_missao() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "executive-mission.json"


def _carregar_fixture_de_missao() -> tuple[dict[str, Any] | None, list[str]]:
    """MISSION de fronteira em disco — não é missão real."""
    caminho = _caminho_fixture_de_missao()
    if not caminho.is_file():
        return None, [
            "fixture de fronteira ausente: evals/fixtures/executive-mission.json"
        ]
    try:
        return json.loads(caminho.read_text(encoding="utf-8")), []
    except (OSError, ValueError) as erro:
        return None, [f"fixture de fronteira ilegivel: {erro}"]


def _erros_se_missao_nao_for_objeto(valor: object) -> list[str]:
    """Fail-closed: ausencia ou nao-dict nao vira lista vazia."""
    if not isinstance(valor, dict):
        return ["executive_mission ausente ou nao e objeto"]
    return []

def _excecoes_otica_de_isolamento(root: Path) -> tuple[str, ...]:
    """Arenas de julgamento nao sao pacote gerente.

    A descoberta por SKILL.md as conta, e a trava global falha por
    ausencia de validate_workflow.py. Excecao por caminho exato, nunca
    por padrao: a API de cobertura so aceita paths relativos POSIX.
    """
    extras: list[str] = []
    raiz = root.resolve()
    for skill in raiz.rglob("SKILL.md"):
        pacote = skill.parent
        try:
            rel = pacote.resolve().relative_to(raiz).as_posix()
        except ValueError:
            continue
        parts = rel.split("/")
        if parts and parts[-1] == "otica" and "root" in parts:
            if any(p.startswith("isolamento") for p in parts):
                extras.append(rel)
    return tuple(sorted(set(extras)))




def _conferir_selo_do_instrumento_local() -> list[str]:
    """O PLACAR ao lado deste validador aponta para o digest deste arquivo."""
    placar = Path(__file__).resolve().parent / "PLACAR.md"
    if not placar.is_file():
        return ["PLACAR.md ausente ao lado do validador"]
    achado = SELO_DE_CONTAGEM.search(placar.read_text(encoding="utf-8"))
    if not achado:
        return ["PLACAR.md ao lado do validador nao traz CONTAGEM-VIGENTE"]
    declarado = achado.group(3)
    vigente = sha256_texto_normalizado(Path(__file__))
    if declarado != vigente:
        return [
            "selo do PLACAR local "
            + declarado[:18]
            + "... nao e o digest deste validador "
            + vigente[:18]
            + "..."
        ]
    return []


# --------------------------------------------------------------------------
# Verificações de pacote
# --------------------------------------------------------------------------

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
                PACKAGE_ROOT / "evals" / "PLACAR.md",
                PACKAGE_ROOT / "references" / "protocolo-de-evolucao.md",
                PACKAGE_ROOT / "references" / "metodo-e-fronteira-de-pareto.md",
                PACKAGE_ROOT / "references" / "mineracao-e-proveniencia.md",
                PACKAGE_ROOT / "references" / "origem-e-fundamentacao.md",
                PACKAGE_ROOT / "references" / "adr-004-evolucao-no-nivel-do-ceo.md",
            ],
            "arquivo local",
        )
    )
    errors.extend(
        validate_required_files(
            [
                CEO_SCHEMA_PATH,
                RULES_PATH,
                CEO_ROOT / "SKILL.md",
                STRUCTURE_ROOT / "ORGANOGRAMA.md",
                STRUCTURE_ROOT / "AGENTS.md",
                STRUCTURE_ROOT / "GUIA-DE-EXPANSAO-E-MIGRACAO.md",
                STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
            ],
            "vínculo externo",
        )
    )
    if PACKAGE_ROOT.parent.name != "ceo-maestro":
        errors.append(
            "o Departamento deve responder direto ao CEO, sob ceo-maestro/, "
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
            OPENAI_PATH, "Departamento de Evolução de Skills", f"${DEPARTMENT}"
        )
    )
    displays = {
        "agente-colheita-e-diagnostico": "Colheita e Diagnóstico",
        "agente-mineracao-externa": "Mineração Externa",
        "agente-curador-de-candidatos": "Curador de Candidatos",
        "agente-prova-de-evolucao": "Prova de Evolução",
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
        "ceo-maestro",
        "departamento-inovacao-melhoria",
        "departamento-registros",
        "departamento-juizes",
        "EVOLUTION_TASK",
        "EXECUTIVE_MISSION",
        "fronteira de Pareto",
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


def validate_no_promotion(schema: dict[str, Any]) -> list[str]:
    """ADR-004: aqui não se promove, não se pontua e não se escolhe vencedor."""
    found: set[str] = set()
    collect_property_names(schema, found)
    offenders = sorted(found.intersection(FORBIDDEN_KEYS))
    if offenders:
        return [f"schema contém campo proibido pelo ADR-004: {offenders}"]
    return []


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "evolutionPlan",
        "evolutionTask",
        "evolutionReturn",
        "candidateSet",
        "evolutionCapabilityGap",
        "evolutionLedger",
    }
    missing = expected.difference(schema.get("$defs", {}))
    if missing:
        errors.append(f"schema sem defs: {sorted(missing)}")
    worker_enum = schema.get("$defs", {}).get("workerId", {}).get("enum", [])
    if sorted(worker_enum) != sorted(AGENT_NAMES):
        errors.append(f"workerId divergente das pastas de agentes/: {worker_enum}")
    return errors


def validate_ceo_contract() -> list[str]:
    """O contrato do CEO precisa admitir este Departamento como par executivo."""
    if not CEO_SCHEMA_PATH.is_file():
        return ["schema do CEO ausente"]
    ceo = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))
    defs = ceo.get("$defs", {})
    errors: list[str] = []

    if DEPARTMENT not in defs.get("directExecutive", {}).get("enum", []):
        errors.append("directExecutive do CEO não admite este Departamento")
    mission = defs.get("executiveMission", {}).get("properties", {})
    if mission.get("recipients", {}).get("maxItems", 0) < 3:
        errors.append("recipients da EXECUTIVE_MISSION ainda limita a 2 destinatários")
    producer = (
        defs.get("causalHeader", {}).get("properties", {}).get("producer", {}).get("enum", [])
    )
    if DEPARTMENT not in producer:
        errors.append("producer causal do CEO não admite este Departamento")
    gap = (
        defs.get("capabilityGap", {})
        .get("properties", {})
        .get("required_capability", {})
        .get("enum", [])
    )
    if DEPARTMENT not in gap:
        errors.append("CAPABILITY_GAP do CEO não admite este Departamento")

    # o que NÃO pode ter mudado
    if not find_const(defs.get("judgeReport", {}), "producer", "departamento-juizes"):
        errors.append("a nota continua sendo dos Juízes: contrato alterado")
    if not find_const(defs.get("exceptionAuthorization", {}), "authorized_by", "jeremias"):
        errors.append("só Jeremias autoriza exceção: contrato alterado")
    if not find_const(defs.get("executiveDecision", {}), "producer", "ceo-maestro"):
        errors.append("a decisão executiva continua sendo do CEO: contrato alterado")

    agents_md = (STRUCTURE_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    if DEPARTMENT not in agents_md:
        errors.append("AGENTS.md não reconhece este Departamento na hierarquia")
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
    if len({case["id"] for case in cases}) != len(cases):
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

    return errors


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

def run() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    ceo_schema = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))

    cases: list[tuple[str, bool, list[str]]] = []

    # --- fronteira r4: r3-B + helper + nao-dict/invalida + otica isenta ----
    sub_ceo, erros_fx = _carregar_fixture_de_fronteira()
    missao_ceo, erros_missao_fx = _carregar_fixture_de_missao()
    cases.append(
        (
            "fixture de fronteira EXECUTIVE_SUBMISSION presente",
            True,
            list(erros_fx),
        )
    )
    cases.append(
        (
            "fixture de fronteira EXECUTIVE_MISSION presente",
            True,
            list(erros_missao_fx),
        )
    )
    if sub_ceo is None:
        cases.append(
            ("schema do CEO aceita EXECUTIVE_SUBMISSION", True, erros_fx)
        )
        cases.append(
            ("schema do CEO rejeita EXECUTIVE_SUBMISSION forjada", True, erros_fx)
        )
    else:
        forged_ceo = json.loads(json.dumps(sub_ceo))
        forged_ceo["submitted_by"] = "departamento-juizes"
        forged_ceo["causal"]["producer"] = "departamento-juizes"
        cases.append(
            (
                "schema do CEO aceita EXECUTIVE_SUBMISSION",
                True,
                validate_schema(sub_ceo, ceo_schema, ceo_schema),
            )
        )
        cases.append(
            (
                "schema do CEO rejeita EXECUTIVE_SUBMISSION forjada",
                False,
                validate_schema(forged_ceo, ceo_schema, ceo_schema),
            )
        )
    if missao_ceo is None:
        cases.append(
            ("schema do CEO aceita EXECUTIVE_MISSION", True, erros_missao_fx)
        )
        cases.append(
            ("schema do CEO rejeita EXECUTIVE_MISSION nao-dict", True, erros_missao_fx)
        )
        cases.append(
            ("schema do CEO rejeita EXECUTIVE_MISSION invalida", True, erros_missao_fx)
        )
    else:
        erros_missao = _erros_se_missao_nao_for_objeto(missao_ceo)
        if not erros_missao:
            erros_missao = validate_schema(missao_ceo, ceo_schema, ceo_schema)
        missao_nao_dict = "nao-e-objeto"
        missao_invalida = {"artifact_type": "NOT_A_MISSION"}
        cases.append(
            (
                "schema do CEO aceita EXECUTIVE_MISSION",
                True,
                erros_missao,
            )
        )
        cases.append(
            (
                "schema do CEO rejeita EXECUTIVE_MISSION nao-dict",
                False,
                _erros_se_missao_nao_for_objeto(missao_nao_dict)
                or validate_schema(missao_nao_dict, ceo_schema, ceo_schema),
            )
        )
        cases.append(
            (
                "schema do CEO rejeita EXECUTIVE_MISSION invalida",
                False,
                validate_schema(missao_invalida, ceo_schema, ceo_schema),
            )
        )
    cases.append(
        (
            "PLACAR local aponta para o digest deste validador",
            True,
            _conferir_selo_do_instrumento_local(),
        )
    )

    cases.append(("pacote, agentes e vínculos externos", True, validate_structure()))
    cases.append(("metadata da gerente e dos quatro agentes", True, validate_metadata()))
    cases.append(("fonte normativa única e tokens de contrato", True, validate_normative_source()))
    cases.append(
        (
            "links internos do pacote resolvem",
            True,
            validate_links(
                PACKAGE_ROOT,
                exclude=[
                    PACKAGE_ROOT
                    / "evals"
                    / "regularizacao-dados7-2026-07-29",
                    # Dossiês de candidato são cópias CONGELADAS de pacotes que vivem
                    # noutro lugar da árvore: os links relativos deles resolvem na
                    # posição canônica, não na posição do dossiê. Validá-los aqui mede
                    # o deslocamento da cópia, não a saúde do pacote — mesma razão da
                    # exclusão acima. Acrescentado em 2026-07-31 para a campanha criada
                    # pelo commit 447b5f0, que introduziu 16 falsos quebrados (57/58).
                    PACKAGE_ROOT
                    / "evals"
                    / "retrabalho-c09-c12-2026-07-30"
                    / "candidatos",
                ],
            ),
        )
    )
    cases.append(("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT)))
    cases.append(
        (
            "todo pacote gerente tem validador que roda a trava global",
            True,
            validate_cobertura_de_validadores(
                STRUCTURE_ROOT,
                excecoes=COBERTURA_EXCECOES
                + _excecoes_otica_de_isolamento(STRUCTURE_ROOT),
            ),
        )
    )
    cases.append(("a recusa de digest() dispara e ninguém tem cópia privada do motor", True, validate_trava_de_digest(STRUCTURE_ROOT)))
    cases.append(("nenhuma asserção é verdadeira por construção sobre valor produzido", True, validate_sem_check_tautologico(STRUCTURE_ROOT)))
    cases.append(("nenhum placar de pacote declara total de cadeia como estado corrente", True, validate_placar_nao_declara_cadeia(STRUCTURE_ROOT)))
    cases.append(("a contagem publicada aponta para o digest do instrumento vigente", True, validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)))
    cases.append(("as travas do modulo compartilhado nao estao neutralizadas", True, validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT)))
    cases.append(("toda pendencia declarada nomeia quem responde por ela", True, validate_pendencia_tem_dono(STRUCTURE_ROOT)))
    cases.append(("a fonte normativa confere com o valor declarado em ORIGEM.md", True, validate_fonte_normativa_conferida(STRUCTURE_ROOT)))
    cases.append(("schema interno e workerId", True, validate_schema_shape(schema)))
    cases.append(("ADR-004: sem promoção, nota ou vencedor no schema", True, validate_no_promotion(schema)))
    cases.append(("contrato do CEO admite o par executivo", True, validate_ceo_contract()))
    cases.append(("catálogo de evals", True, validate_evals()))

    fixtures = [
        ("EVOLUTION_PLAN", evolution_plan()),
        ("EVOLUTION_TASK de diagnóstico", evolution_task()),
        ("EVOLUTION_TASK de prova", evolution_task("agente-prova-de-evolucao")),
        ("EVOLUTION_RETURN de diagnóstico", evolution_return("DIAGNOSTICO")),
        ("EVOLUTION_RETURN de gem", evolution_return("GEM")),
        ("EVOLUTION_RETURN de candidato", evolution_return("CANDIDATO")),
        ("EVOLUTION_RETURN de prova", evolution_return("PROVA")),
        ("CANDIDATE_SET", candidate_set()),
        ("EVOLUTION_CAPABILITY_GAP", capability_gap()),
        ("EVOLUTION_LEDGER", evolution_ledger()),
    ]
    for label, fixture in fixtures:
        cases.append((f"schema aceita {label}", True, validate_schema(fixture, schema, schema)))

    # --- tarefa: kind, capacidade e cegueira -------------------------------

    wrong_worker = evolution_task()
    wrong_worker["worker_id"] = "agente-curador-de-candidatos"
    cases.append(
        ("tarefa rejeita capacidade trocada para o kind", False,
         validate_schema(wrong_worker, schema, schema))
    )

    candidate_no_gap = evolution_task("agente-curador-de-candidatos")
    candidate_no_gap["gap"] = "n/a"
    cases.append(
        ("tarefa de candidato exige gap nomeado", False,
         validate_schema(candidate_no_gap, schema, schema))
    )

    prova_sem_rotulo = evolution_task("agente-prova-de-evolucao")
    prova_sem_rotulo.pop("candidate_labels")
    cases.append(
        ("tarefa de prova exige candidatos rotulados", False,
         validate_schema(prova_sem_rotulo, schema, schema))
    )

    prova_um_so = evolution_task("agente-prova-de-evolucao")
    prova_um_so["candidate_labels"] = ["cand-A"]
    cases.append(
        ("tarefa de prova exige dois ou mais rótulos", False,
         validate_schema(prova_um_so, schema, schema))
    )

    leaky = evolution_task()
    leaky["forbidden_context"] = [
        "preferência da gerente",
        "retornos dos outros agentes",
        "veredito desejado",
        "rodada anterior",
    ]
    cases.append(
        ("tarefa exige proibir a identidade de quem escreveu", False,
         validate_schema(leaky, schema, schema))
    )

    wrong_return = evolution_task()
    wrong_return["return_to"] = "ceo-maestro"
    cases.append(
        ("tarefa rejeita retorno fora da gerente", False,
         validate_schema(wrong_return, schema, schema))
    )

    # --- retorno: carga por kind -------------------------------------------

    one_candidate = evolution_return("CANDIDATO")
    one_candidate["candidates"] = [candidate_item("cand-unico")]
    cases.append(
        ("retorno de candidato exige dois ou mais", False,
         validate_schema(one_candidate, schema, schema))
    )

    grew_without_removing = evolution_return("CANDIDATO")
    grew_without_removing["candidates"] = [
        candidate_item("cand-a", delta_lines=12, removed="nada"),
        candidate_item("cand-b"),
    ]
    cases.append(
        ("candidato que cresce sem remover é rejeitado", False,
         validate_schema(grew_without_removing, schema, schema))
    )

    gem_no_saturation = evolution_return("GEM")
    gem_no_saturation.pop("saturation")
    cases.append(
        ("retorno de gem exige saturação declarada", False,
         validate_schema(gem_no_saturation, schema, schema))
    )

    unlicensed_deep = evolution_return("GEM")
    unlicensed_deep["gems"] = [gem_item(licenca="desconhecida", degrau=3)]
    cases.append(
        ("licença desconhecida trava o degrau em 0 ou 1", False,
         validate_schema(unlicensed_deep, schema, schema))
    )

    unlicensed_shallow = evolution_return("GEM")
    unlicensed_shallow["gems"] = [gem_item(licenca="desconhecida", degrau=1)]
    cases.append(
        ("licença desconhecida aceita degrau 1", True,
         validate_schema(unlicensed_shallow, schema, schema))
    )

    prova_com_candidato = evolution_return("PROVA")
    prova_com_candidato["candidates"] = [candidate_item()]
    cases.append(
        ("quem prova não devolve candidato escrito", False,
         validate_schema(prova_com_candidato, schema, schema))
    )

    blocked = evolution_return("PROVA", status="BLOCKED")
    cases.append(
        ("retorno BLOCKED com motivo é válido", True,
         validate_schema(blocked, schema, schema))
    )

    blocked_mute = evolution_return("PROVA", status="BLOCKED")
    blocked_mute.pop("blocked_reason")
    cases.append(
        ("retorno BLOCKED exige motivo declarado", False,
         validate_schema(blocked_mute, schema, schema))
    )

    incoerente = evolution_return("DIAGNOSTICO")
    incoerente["gaps"][0]["signals"]["acionou"] = "N"
    incoerente["gaps"][0]["signals"]["aderiu"] = "S"
    cases.append(
        ("acionou N obriga aderiu em travessão", False,
         validate_schema(incoerente, schema, schema))
    )

    # --- fronteira ----------------------------------------------------------

    dominated_no_dominator = candidate_set()
    dominated_no_dominator["items"][1]["status"] = "DOMINADO"
    cases.append(
        ("dominado exige dominador nomeado", False,
         validate_schema(dominated_no_dominator, schema, schema))
    )

    dominated_ok = candidate_set()
    dominated_ok["items"][1]["status"] = "DOMINADO"
    dominated_ok["items"][1]["dominated_by"] = "cand-descricao"
    dominated_ok["items"][1]["diversidade"] = False
    cases.append(
        ("dominado com dominador é aceito", True,
         validate_schema(dominated_ok, schema, schema))
    )

    single = candidate_set()
    single["items"] = [single["items"][0]]
    cases.append(
        ("fronteira exige comparar ao menos dois", False,
         validate_schema(single, schema, schema))
    )

    # --- ledger -------------------------------------------------------------

    proposal_no_scoreboard = evolution_ledger(with_scoreboard=False)
    cases.append(
        ("proposta sem placar é rejeitada", False,
         validate_schema(proposal_no_scoreboard, schema, schema))
    )

    proposal_no_assignments = evolution_ledger(with_assignments=False)
    cases.append(
        ("proposta sem registro de emissão é rejeitada (R6)", False,
         validate_schema(proposal_no_assignments, schema, schema))
    )

    analysis_with_candidates = evolution_ledger(mode="AVALIACAO", deliverable="proposal")
    cases.append(
        ("modo AVALIACAO não devolve proposta", False,
         validate_schema(analysis_with_candidates, schema, schema))
    )

    analysis_ok = evolution_ledger(mode="AVALIACAO", deliverable="analysis")
    analysis_ok["candidate_sets"] = []
    cases.append(
        ("modo AVALIACAO devolve análise sem candidatos", True,
         validate_schema(analysis_ok, schema, schema))
    )


    # --- rodada 4: o schema CRUZA identidade ------------------------------
    #
    # Em 2026-08-01 o `37-EVOLUTION-LEDGER-R3.json` declarou o digest do
    # `cand-B` com `round: 2` no plano, enquanto o candidato julgado era o
    # `cand-C` com `round: 3` — e VALIDOU COM ZERO ERROS, porque nada no schema
    # cruzava um campo com outro. JSON Schema nao compara dois campos; um
    # retrovisor de expressao regular compara. A `line` do cruzamento carrega os
    # tres pares, e o `pattern` os obriga a serem iguais.
    #
    # Tres eixos: o schema (estrutural), estes casos (comportamental) e a
    # reproducao do artefato real reprovado (executado, em 42-CRUZAMENTO-*.json).
    cruzado = evolution_ledger()
    cases.append(
        ("ledger com identidade cruzada e coerente é aceito", True,
         validate_schema(cruzado, schema, schema))
    )

    outro_candidato = evolution_ledger()
    outro_candidato["candidate_identity"] = identity_crosscheck(
        candidate="cand-D-derivado-nao-declarado",
        declared=digest("2"),
        recomputed=digest("4"),
    )
    cases.append(
        ("ledger com digest de OUTRO candidato é rejeitado", False,
         validate_schema(outro_candidato, schema, schema))
    )

    rodada_do_plano = evolution_ledger()
    rodada_do_plano["candidate_identity"] = identity_crosscheck(
        rodada=3, plan_round=2
    )
    cases.append(
        ("ledger cujo plano declara outra rodada é rejeitado", False,
         validate_schema(rodada_do_plano, schema, schema))
    )

    rodada_da_missao = evolution_ledger()
    rodada_da_missao["candidate_identity"] = identity_crosscheck(
        rodada=4, mission_round=3
    )
    cases.append(
        ("ledger cuja rodada diverge da missão é rejeitado", False,
         validate_schema(rodada_da_missao, schema, schema))
    )

    # A forma mais barata de burlar: dizer CONFERIDO e mentir na linha. O
    # retrovisor pega, porque a linha e' o objeto conferido, nao um rotulo.
    linha_forjada = evolution_ledger()
    linha_forjada["candidate_identity"] = dict(identity_crosscheck())
    linha_forjada["candidate_identity"]["line"] = (
        "candidate=cand-D-derivado-nao-declarado"
        " root=candidatos/cand-B-travas-por-efeito"
        f" declared={digest('2')} recomputed={digest('2')}"
        " round=4 plan_round=4 mission_round=4"
    )
    cases.append(
        ("CONFERIDO cuja linha aponta para outra pasta é rejeitado", False,
         validate_schema(linha_forjada, schema, schema))
    )

    # --- RODADA 5: O CRUZAMENTO SAI DE DENTRO DA LINHA --------------------
    #
    # `OI-03`, por origem independente, mediu o limite dos casos acima: o
    # `pattern` obriga a linha a ser coerente CONSIGO MESMA, e uma linha
    # coerente sobre outro candidato, outra rodada ou outro digest passa. Os
    # Juízes escreveram a frase: enquanto o confronto viver na função que DERIVA
    # a linha — e `identity_crosscheck`, acima, é exatamente essa função —, o
    # instrumento testa o produtor honesto, não a trava.
    #
    # Os casos abaixo usam `cruzar_identidade_externa`, que confronta a linha
    # com os CAMPOS IRMÃOS do ledger, com a MISSÃO EM DISCO e com a ÁRVORE EM
    # DISCO. Cada um deles é aceito pelo schema e rejeitado aqui, e é onde o
    # ganho da rodada 5 se mede.
    def _com_linha(**campos: Any) -> dict[str, Any]:
        bloco = {
            "status": "CONFERIDO",
            "recipe": "_compartilhado/verificacoes_pacote.py::digest_de_arvore",
            "candidate_id": "cand-E-alegacao-reduzida",
            "candidate_root_ref": "candidatos/cand-E-alegacao-reduzida",
            "declared_digest": digest("a"),
            "recomputed_digest": digest("a"),
            "round_declared": 5,
            "plan_round": 5,
            "mission_round": 5,
            "mission_ref": "62-EXECUTIVE-MISSION-R5.json",
            "errors": [],
            "checked_at": "2026-08-02T16:00:00-03:00",
        }
        bloco.update(campos)
        bloco["line"] = montar_linha_de_cruzamento(bloco)
        return bloco

    def _ledger_para_cruzar(bloco: dict[str, Any], **causal_extra: Any) -> dict[str, Any]:
        return {
            "causal": {
                "candidate_digest": causal_extra.get("candidate_digest", digest("a")),
                "round": causal_extra.get("round", 5),
            },
            "plan": {"causal": {"round": causal_extra.get("plan_round", 5)}},
            "candidate_identity": bloco,
        }

    honesto_externo = _ledger_para_cruzar(_com_linha())
    cases.append(
        ("CONTROLE: identidade honesta passa no cruzamento externo", True,
         cruzar_identidade_externa(
             honesto_externo, rodada_da_missao=5, digest_em_disco=digest("a")))
    )

    # ISOLAMENTO — cada caso mata UMA fonte externa, e só ela.
    #
    # A prova de mutação desta rodada mostrou por que isso importa: um caso que
    # viole duas fontes ao mesmo tempo continua vermelho quando UMA delas é
    # neutralizada, e a mutação sai verde. Caso que não isola não prova a trava
    # que diz provar.
    #
    # Aqui só o CAMPO IRMÃO diverge: a árvore em disco bate com o recomputado e
    # com o causal, e as três rodadas batem.
    so_o_irmao = _ledger_para_cruzar(
        _com_linha(declared_digest=digest("z"))
    )
    cases.append(
        ("SÓ o campo irmão diverge: declared_digest x causal.candidate_digest",
         False,
         cruzar_identidade_externa(
             so_o_irmao, rodada_da_missao=5, digest_em_disco=digest("a")))
    )

    # Aqui só o RECOMPUTADO diverge da árvore: o causal bate com o disco.
    so_o_recomputado = _ledger_para_cruzar(
        _com_linha(recomputed_digest=digest("z"))
    )
    cases.append(
        ("SÓ o recomputado diverge da árvore em disco", False,
         cruzar_identidade_externa(
             so_o_recomputado, rodada_da_missao=5, digest_em_disco=digest("a")))
    )

    # Aqui só a ÁRVORE diverge do que o artefato diz julgar — é a comparação que
    # rejeita o 37-EVOLUTION-LEDGER-R3 real mesmo com a linha forjada coerente.
    so_a_arvore = _ledger_para_cruzar(
        _com_linha(recomputed_digest=digest("z")),
        candidate_digest=digest("a"),
    )
    cases.append(
        ("SÓ a árvore em disco não é o candidato declarado", False,
         cruzar_identidade_externa(
             so_a_arvore, rodada_da_missao=5, digest_em_disco=digest("z")))
    )

    linha_sobre_outro_digest = _ledger_para_cruzar(
        _com_linha(declared_digest=digest("z"), recomputed_digest=digest("z"))
    )
    cases.append(
        ("linha auto-consistente sobre digest que o irmão não declara é acusada",
         False,
         cruzar_identidade_externa(
             linha_sobre_outro_digest, rodada_da_missao=5,
             digest_em_disco=digest("a")))
    )

    linha_sobre_outra_rodada = _ledger_para_cruzar(
        _com_linha(round_declared=2, plan_round=2, mission_round=2)
    )
    cases.append(
        ("linha auto-consistente sobre outra rodada é acusada", False,
         cruzar_identidade_externa(
             linha_sobre_outra_rodada, rodada_da_missao=5,
             digest_em_disco=digest("a")))
    )

    arvore_divergente = _ledger_para_cruzar(_com_linha())
    cases.append(
        ("digest que a ÁRVORE EM DISCO não produz é acusado", False,
         cruzar_identidade_externa(
             arvore_divergente, rodada_da_missao=5, digest_em_disco=digest("z")))
    )

    linha_livre = _ledger_para_cruzar(_com_linha())
    linha_livre["candidate_identity"]["line"] = linha_livre["candidate_identity"][
        "line"
    ].replace("cand-E-alegacao-reduzida", "cand-B-travas-por-efeito", 1)
    cases.append(
        ("linha que não é a composição dos campos irmãos é acusada", False,
         cruzar_identidade_externa(
             linha_livre, rodada_da_missao=5, digest_em_disco=digest("a")))
    )

    # AUSÊNCIA DE FONTE EXTERNA É ERRO NOMEADO, e não desligamento silencioso —
    # é o achado A1 aplicado à trava nova antes que ele volte a acontecer.
    cases.append(
        ("missão que não abre em disco é ausência declarada, não silêncio", False,
         cruzar_identidade_externa(
             honesto_externo, rodada_da_missao=None, digest_em_disco=digest("a")))
    )
    cases.append(
        ("árvore que não abre em disco é ausência declarada, não silêncio", False,
         cruzar_identidade_externa(
             honesto_externo, rodada_da_missao=5, digest_em_disco=None))
    )

    sem_cruzamento = evolution_ledger()
    sem_cruzamento.pop("candidate_identity")
    cases.append(
        ("proposta sem bloco de cruzamento é rejeitada", False,
         validate_schema(sem_cruzamento, schema, schema))
    )

    divergente_sem_motivo = evolution_ledger()
    divergente_sem_motivo["candidate_identity"] = dict(identity_crosscheck())
    divergente_sem_motivo["candidate_identity"]["status"] = "DIVERGENTE"
    divergente_sem_motivo["candidate_identity"]["errors"] = []
    cases.append(
        ("DIVERGENTE sem motivo escrito é rejeitado", False,
         validate_schema(divergente_sem_motivo, schema, schema))
    )

    nao_conferido_com_numero = evolution_ledger()
    nao_conferido_com_numero["deliverable_type"] = "analysis"
    nao_conferido_com_numero["mode"] = "AVALIACAO"
    nao_conferido_com_numero["candidate_sets"] = []
    nao_conferido_com_numero["candidate_identity"] = dict(identity_crosscheck())
    nao_conferido_com_numero["candidate_identity"]["status"] = "NAO_CONFERIDO"
    cases.append(
        ("NAO_CONFERIDO publicando digest recomputado é rejeitado", False,
         validate_schema(nao_conferido_com_numero, schema, schema))
    )

    no_r6 = evolution_ledger()
    no_r6["pending"] = ["fingerprint residual anotado"]
    cases.append(
        ("ledger exige R6 nomeado em pending", False,
         validate_schema(no_r6, schema, schema))
    )

    # --- RODADA 7, C06: AS SETE AUTODECLARAÇÕES NO ENVELOPE ----------------
    #
    # Cada caso mata UMA condição. Caso que viola duas ao mesmo tempo continua
    # vermelho quando UMA é neutralizada, e a mutação sai verde — foi a lição da
    # prova de mutação da rodada 5, e ela vale para as travas novas também.

    to_director = evolution_ledger()
    to_director["return_to"] = "diretor-de-lentes"
    cases.append(
        ("ledger rejeita retorno fora do CEO", False,
         validate_schema(to_director, schema, schema))
    )

    forged = evolution_ledger()
    forged["causal"]["producer"] = "diretor-de-lentes"
    cases.append(
        ("ledger rejeita produtor forjado", False,
         validate_schema(forged, schema, schema))
    )

    # --- fronteira de Pareto, recalculada em código -------------------------

    a = {"c1": "passou", "c2": "passou", "c3": "falhou"}
    b = {"c1": "falhou", "c2": "falhou", "c3": "passou"}
    c = {"c1": "passou", "c2": "passou", "c3": "passou"}
    d = {"c1": "passou", "c2": "falhou", "c3": "falhou"}
    equal = {"c1": "passou", "c2": "passou", "c3": "falhou"}
    skipped = {"c1": "skip:sem ambiente", "c2": "skip:sem ambiente", "c3": "skip:sem ambiente"}

    checks = [
        ("dominância: melhor em tudo domina", dominates(c, a)),
        ("dominância: pior em um caso não domina", not dominates(a, b)),
        ("dominância: empate não domina", not dominates(a, equal)),
        ("dominância: caso em skip não conta", not dominates(a, skipped)),
        ("fronteira mantém os dois complementares", frontier({"a": a, "b": b}) == ["a", "b"]),
        ("fronteira remove o dominado", frontier({"a": a, "c": c, "d": d}) == ["c"]),
        (
            "candidato pior na média e melhor em um caso permanece",
            mean(b) < mean(a) and "b" in frontier({"a": a, "b": b}),
        ),
        ("fronteira de um elemento é detectável", len(frontier({"a": a, "d": d})) == 1),
        ("anti-sedimento: cresce sem remover é rejeitado", not accepts_candidate(12, "nada")),
        ("anti-sedimento: encolher é aceito", accepts_candidate(-4, "n/a")),
        (
            "anti-sedimento: cresce removendo o equivalente é aceito",
            accepts_candidate(3, "removida a seção duplicada de acionamento"),
        ),
        (
            "independência: quem escreve não prova",
            not prover_is_independent("agente-curador-de-candidatos", "agente-curador-de-candidatos")
            and prover_is_independent("agente-curador-de-candidatos", "agente-prova-de-evolucao"),
        ),
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
