"""Validador determinístico do Departamento de Inovação e Melhoria.

Prova estrutura, schema fechado, três agentes exclusivos, gates de inovação,
RO-15, anti-bypass, anti-julgamento, fronteira com Evolução de Skills, ponte
para o schema real do Diretor e integridade dos 22 arquivos legados.

Além do schema, este validador fecha três classes que o schema sozinho não
alcança e que o corpus adversarial de 2026-07-26 provou abertas:

1. **Contexto confiável.** Missão → plano → assignment → retorno → relatório →
   fronteira compartilham um contexto derivado da `DEPARTMENT_MISSION` e
   autenticado por digest canônico. Referência inventada não sobrevive.
2. **Gate derivado.** `gate_checks` é recalculado a partir dos retornos reais;
   o booleano declarado só passa se coincidir com o derivado.
3. **Estrutura normativa.** Seções obrigatórias de contrato, tokens das Skills
   dos agentes, `Concluído quando:` por seção do protocolo, tabela única de
   riscos residuais e honestidade do placar são conferidos aqui — antes, a
   auditoria de governança os encontrava e o validador não.

Uso:
  python evals/validate_workflow.py

O terminal do Jeremias é cp1252; rodar com `PYTHONIOENCODING=utf-8`.

Em staging, definir SKILL_STRUCTURE_ROOT para a raiz canônica da Estrutura
Final de Skills. Depois da promoção, a raiz é inferida automaticamente.
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
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-inovacao-melhoria.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
PLACAR_PATH = PACKAGE_ROOT / "evals" / "PLACAR.md"
AUDIT_PATH = PACKAGE_ROOT / "evals" / "ADVERSARIAL-AUDIT.md"
AGENTS_ROOT = PACKAGE_ROOT / "agentes"
REFERENCES_ROOT = PACKAGE_ROOT / "references"
PROTOCOL_PATH = REFERENCES_ROOT / "protocolo-inovacao-melhoria.md"

if "SKILL_STRUCTURE_ROOT" in os.environ:
    STRUCTURE_ROOT = Path(os.environ["SKILL_STRUCTURE_ROOT"]).resolve()
else:
    # pacote canônico: estrutura/ceo/diretor/operacionais/departamento
    STRUCTURE_ROOT = PACKAGE_ROOT.parents[3]

DIRECTOR_ROOT = STRUCTURE_ROOT / "ceo-maestro" / "diretor-de-lentes"
DIRECTOR_SCHEMA_PATH = DIRECTOR_ROOT / "schemas" / "diretor-de-lentes.schema.json"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"
CANONICAL_PACKAGE_ROOT = (
    DIRECTOR_ROOT
    / "departamentos-operacionais"
    / "departamento-inovacao-melhoria"
)
LEGACY_ROOT = Path(
    os.environ.get(
        "INNOVATION_LEGACY_ROOT",
        str(
            STRUCTURE_ROOT.parent
            / "SKILL - Nova formula"
            / "maestro"
            / "comite-de-lentes"
            / "orquestrador-inovacao-melhoria"
        ),
    )
).resolve()

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        collect_property_names,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_adr_series,
        validate_agents_folder,
        validate_frontmatter,
        validate_openai_yaml,
        validate_required_files,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print(f"[FAIL] motor compartilhado ausente em {STRUCTURE_ROOT}: {exc}")
    raise SystemExit(1)


DEPARTMENT = "departamento-inovacao-melhoria"
NOW = "2026-07-26T12:00:00-03:00"
LATER = "2026-07-27T12:00:00-03:00"
DIGEST = "sha256:" + "a" * 64
CANDIDATE = "sha256:" + "b" * 64
CONTRACT_DIGEST = "sha256:" + "c" * 64
EVIDENCE_DIGEST = "sha256:" + "d" * 64
TARGET = "artifact-product-v1"

AGENT_CAPABILITY = {
    "agente-descoberta-de-oportunidades": "OPPORTUNITY_DISCOVERY",
    "agente-experimentos-e-spikes": "EXPERIMENT_DESIGN",
    "agente-melhoria-continua": "CONTINUOUS_IMPROVEMENT",
}
CAPABILITY_AGENT = {value: key for key, value in AGENT_CAPABILITY.items()}
AGENT_DISPLAY = {
    "agente-descoberta-de-oportunidades": "Agente de Descoberta de Oportunidades",
    "agente-experimentos-e-spikes": "Agente de Experimentos e Spikes",
    "agente-melhoria-continua": "Agente de Melhoria Contínua",
}
FORBIDDEN_PROPERTIES = {
    "score",
    "scores",
    "nota",
    "notas",
    "minimum_score",
    "absolute_score",
    "scorecard",
    "rubrica",
    "rubric",
    "peso",
    "pesos",
    "ranking",
    "winner",
    "vencedor",
    "verdict",
    "veredito",
    "approval",
    "aprovacao",
    "approved",
    "cut_score",
    "corte",
    "exception_to_cut",
    "innovation_judgment_result",
}

# Campos onde o Departamento DECLARA o que não faz. Proibir vocabulário de
# julgamento aqui inverteria a regra: é exatamente nestes campos que "nota" e
# "veredito" precisam aparecer, como exclusão. O restante do artefato é
# afirmação, e lá o vocabulário é proibido.
NEGATIVE_DECLARATION_FIELDS = {
    "scope_out",
    "stop_when",
    "vetoes",
    "binding_decisions",
    "claims_unverified",
    "risks",
    "limitations",
    "check_limitations",
    "violations",
    "prevented_effect",
    "expected_route",
    "blocked_scope",
    "negative_evidence",
    "trade_offs",
    "refuted_when",
    "inconclusive_when",
}

JUDGMENT_PATTERNS = (
    (r"\bnotas?\b", "nota"),
    (r"\b9[.,]5\b", "corte 9,5"),
    (r"\bvencedor", "vencedor"),
    (r"\bveredit", "veredito"),
    (r"\branking\b", "ranking"),
    (r"\bscore\b", "score"),
    (r"\brubrica\b", "rubrica"),
    (r"\bpontua(?:ç|c)(?:ão|ao)\b", "pontuação"),
    (r"\baprovad[oa]s?\b", "aprovação"),
    (r"\bPASS\b|\bFAIL\b|\bSKIP\b", "contagem de QA apropriada"),
)

LEGACY_MANIFEST = {
    "agents/openai.yaml": "0D8B4946CFA23481EE13FDD87710412696A2CC9BE07EF1B92FBAA2B86460BDBE",
    "evals/baseline-sem-skill.md": "FA72B3ACD9AA4337E64D719A308EBBE502A369D53BC3409E26EC1F179C2AB68E",
    "evals/candidatos/a/SKILL.md": "10D9BC2F8CE25522E4C9788A3BC9E92327202EB0AB620EBD03F8147EA7BC89FE",
    "evals/candidatos/b/SKILL.md": "CE8217262B152CA95A878A5E6817FDDBDEBF7C63792BB163F06F60E19E44D1E2",
    "evals/comite-final.md": "26F5463E15D0693D780B81C7CAB11F1626A0A0BD2A4CAA41081094F6C13C4AEE",
    "evals/criterio-comite.md": "FFFC87901B3A8BC7A80BA1BF4CE63F596EA3D4FAC8303760A865E2E090CD3DE7",
    "evals/criterio-painel.md": "F8D8B56C039189464E1AA8D57BCB1DB39CC39F2A0A722ED6FA9BA732B5DA7C9E",
    "evals/evals.json": "4EFD5A050F21B6FE68B8D6CC1BDFB413E10CFF6FEDCF2FE8CB8ECBE1C0F87FBB",
    "evals/forward-test/outputs-1-2.md": "D82EB2445867854140D43732E61091CFEBFFC9E16D1A202E8AD078C851E6E35A",
    "evals/forward-test/outputs-3-5.md": "996E51841352B3EF5C3AB58B668EBE5FFFB6681D86F25CD4CAEFE25E8A2075CA",
    "evals/forward-test/outputs-6-7.md": "4D5EA6002F36588884B2D8F9B1BF696450139367BDCB7D76AAC96999F81335DF",
    "evals/forward-test/round-2-outputs-1-2.md": "E49FF62251B17F6B2F32513AA9B728398ACE68D0B5463BB1563D69D0A7A72605",
    "evals/forward-test/round-2-outputs-5-7.md": "336C0FC8B54886C10A0B6DA107DFB9EFC1309A9E428D877817AEF7535749967E",
    "evals/forward-test/round-5-output-5.md": "B2CAF1FE3097B2B3768F06EDCD87F530B5E17C3C81F9A2CB62E87F08D8BD847F",
    "evals/manifest-sha256.txt": "57DA9CA6F4BB06585B4EF0D7B41C26E0187001ADFF76D2DEEA01FD50A1AB982B",
    "evals/painel-final.md": "F81DB8673D5F78B93BD2640F1BC104F2379418FFF0537E118C7B1944FD3961E8",
    "evals/placar.md": "DD4BC3EB0B4BAA0E250203E4D332D02A70C73183AA2F80891A20069A7486E805",
    "references/contratos.md": "54D48CB6E5B80D0152EBFD12901FD17199DFC490661DC7E1172CCCE5C2BFF1BC",
    "references/fundamentos-do-dominio.md": "92AA2879E03A4ADCFF5BB801E500F1A6B8C2DBB2F155B6FBF584D89C9D5D33DE",
    "references/modelo-operacional-do-time.md": "EA76BABB72690E8D47AC62AB9A3B0D19C17B7B68CCC68B9A79E6C9871951F165",
    "references/rubrica-inovacao-melhoria.md": "395C3B6B21553EF679DB3BADF3922123D1922FE6FB80EE3973643643D6C3D72E",
    "SKILL.md": "9ED52040555A93779DD2E9EC18227BFE5FFF7A3C6436A685957213C32D023926",
}

# --- Estrutura normativa exigida pela GUIA-DE-EXPANSAO-E-MIGRACAO -----------

DEPARTMENT_CONTRACT_SECTIONS = (
    "## Papel",
    "## Compromisso",
    "## Autoridade",
    "## Entradas aceitas",
    "## Saídas obrigatórias",
    "## Evidências exigidas",
    "## Obrigações",
    "## Proibições",
    "## Barreira de saída",
    "## Fonte normativa",
    "## Bloqueio por conflito",
    "## Quebra de contrato",
)
AGENT_CONTRACT_SECTIONS = (
    "## Papel",
    "## Autoridade",
    "## Entradas aceitas",
    "## Saídas obrigatórias",
    "## Evidências exigidas",
    "## Obrigações",
    "## Proibições",
    "## Barreira de saída",
    "## Fonte normativa",
    "## Bloqueio por conflito",
    "## Quebra de contrato",
)
RESIDUAL_HEADING = re.compile(
    r"^## (?:\d+\.\s*)?Riscos residuais declarados\s*$", flags=re.MULTILINE
)
AGENT_SKILL_TOKENS = (
    "## Protocolo e trava anti-bypass",
    "## Fronteira exclusiva",
    "Assumir:",
    "**Não assumir**",
    "## Salvaguardas",
    "- **Não aciona:** ninguém.",
)


def canonical_digest(value: Any) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def authenticated(identifier: str, value: Any) -> str:
    return f"{identifier}@{canonical_digest(value)}"


# --------------------------------------------------------------------------
# Fixtures: um bundle coerente da missão à fronteira
# --------------------------------------------------------------------------


def director_permissions() -> dict[str, Any]:
    """Forma do schema do Diretor — fechada e fora do alcance desta frente."""
    return {
        "default_policy": "deny",
        "allowed_tools": ["read-only-inspection"],
        "allowed_resources": [TARGET],
        "expires_at": LATER,
    }


def permissions(environment: str = "READ_ONLY") -> dict[str, Any]:
    return {
        "default_policy": "deny",
        "environment": environment,
        "production_access": False,
        "allowed_tools": ["read-only-inspection"],
        "allowed_resources": [TARGET],
        "expires_at": LATER,
    }


def director_mission(mode: str = "ATUA") -> dict[str, Any]:
    return {
        "artifact_type": "DEPARTMENT_MISSION",
        "department_mission_id": "department-mission-innovation-001",
        "causal": {
            "work_item_id": "work-innovation-001",
            "front_id": "front-innovation-001",
            "handoff_id": "handoff-innovation-001",
            "message_id": "message-director-001",
            "causation_message_ids": ["message-ceo-001"],
            "contract_id": "contract-innovation-001",
            "contract_version": 1,
            "contract_digest": CONTRACT_DIGEST,
            "candidate_digest": CANDIDATE,
            "round": 1,
            "attempt": 1,
            "producer": "diretor-de-lentes",
            "producer_version": "1.0.0",
            "producer_digest": DIGEST,
            "created_at": NOW,
        },
        "recipient": DEPARTMENT,
        "mode": mode,
        "objective": "Reduzir retrabalho com hipótese e evidência.",
        "scope_in": ["Fluxo de publicação."],
        "scope_out": ["Produção e julgamento."],
        "inputs": [TARGET],
        "deliverables": ["Portfólio e relatório de inovação."],
        "done": ["Gate, evidências e pendências reconciliados."],
        "required_evidence": ["Artefatos rastreáveis e relatório autenticado."],
        "depends_on": [],
        "handoff_to": ["diretor-de-lentes"],
        "decision_authority": ["Planejar e recomendar dentro do escopo."],
        "permissions": director_permissions(),
        "stop_when": ["Alvo ou autoridade divergir."],
        "return_to": "diretor-de-lentes",
        "issued_at": NOW,
    }


CONTEXT_CAUSAL_FIELDS = (
    "work_item_id",
    "front_id",
    "handoff_id",
    "contract_id",
    "contract_version",
    "contract_digest",
    "candidate_digest",
    "round",
    "attempt",
)


def trusted_context(mission: dict[str, Any]) -> dict[str, Any]:
    """O contexto confiável nasce da missão, não da autodeclaração do pacote."""
    source = mission["causal"]
    context = {field: source[field] for field in CONTEXT_CAUSAL_FIELDS}
    context["mission_message_id"] = source["message_id"]
    context["mission_ref"] = mission["department_mission_id"]
    context["mission_digest"] = canonical_digest(mission)
    context["mode"] = mission["mode"]
    context["inputs"] = list(mission["inputs"])
    return context


def causal(
    context: dict[str, Any],
    producer: str = DEPARTMENT,
    *,
    message: str,
    causes: list[str],
) -> dict[str, Any]:
    block = {field: context[field] for field in CONTEXT_CAUSAL_FIELDS}
    block.update(
        {
            "message_id": message,
            "causation_message_ids": causes,
            "producer": producer,
            "producer_version": "1.0.0",
            "producer_digest": DIGEST,
            "created_at": NOW,
        }
    )
    return block


def pending(
    pid: str = "pending-measurement-001",
    *,
    blocking: bool = True,
    description: str = "Executar medição da baseline com método definido.",
) -> dict[str, Any]:
    return {
        "pending_id": pid,
        "description": description,
        "impact": "Iniciativa não pode avançar ao gate seguinte.",
        "owner": "diretor-de-lentes",
        "resume_when": "Relatório de medição autenticado estiver disponível.",
        "blocking": blocking,
    }


def external_evidence(
    ref: str = "qa-report-001",
    producer: str = "departamento-qa-usabilidade",
) -> dict[str, Any]:
    return {
        "evidence_ref": ref,
        "producer_ref": producer,
        "producer_digest": EVIDENCE_DIGEST,
        "authorized_by": "diretor-de-lentes",
        "observed_at": NOW,
    }


def plan(context: dict[str, Any], selected: tuple[str, ...] | None = None) -> dict[str, Any]:
    chosen = selected if selected is not None else tuple(AGENT_CAPABILITY)
    return {
        "artifact_type": "INNOVATION_PLAN",
        "plan_id": "innovation-plan-001",
        "causal": causal(
            context,
            message="message-innovation-001",
            causes=[context["mission_message_id"]],
        ),
        "department_mission_ref": context["mission_ref"],
        "department_mission_digest": context["mission_digest"],
        "mode": context["mode"],
        "objective": "Reduzir retrabalho observado no fluxo de publicação.",
        "target_ref": context["inputs"][0],
        "candidate_digest": context["candidate_digest"],
        "scope_in": ["Fluxo de publicação e evidências existentes."],
        "scope_out": ["Produção, implementação, nota e veredito."],
        "binding_decisions": ["Nenhuma alteração em produção nesta missão."],
        "agent_roster": [
            {
                "agent": agent,
                "capability": capability,
                "selected": agent in chosen,
                "reason": (
                    "Capacidade necessária ao ciclo contratado."
                    if agent in chosen
                    else "Capacidade fora do recorte desta missão."
                ),
            }
            for agent, capability in AGENT_CAPABILITY.items()
        ],
        "dependencies": [],
        "stop_when": ["Permissão expirar ou alvo/digest divergir."],
        "return_to": "diretor-de-lentes",
        "issued_at": NOW,
    }


def assignment(
    context: dict[str, Any],
    source_plan: dict[str, Any],
    agent: str = "agente-descoberta-de-oportunidades",
) -> dict[str, Any]:
    capability = AGENT_CAPABILITY[agent]
    return {
        "artifact_type": "INNOVATION_ASSIGNMENT",
        "assignment_id": f"assignment-{capability.lower()}-001",
        "causal": causal(
            context,
            message=f"message-assignment-{capability.lower()}-001",
            causes=[source_plan["causal"]["message_id"]],
        ),
        "department_mission_ref": context["mission_ref"],
        "department_mission_digest": context["mission_digest"],
        "plan_ref": source_plan["plan_id"],
        "plan_digest": canonical_digest(source_plan),
        "mode": source_plan["mode"],
        "assigned_agent": agent,
        "capability": capability,
        "objective": "Produzir entrega exclusiva e verificável da capacidade.",
        "target_ref": source_plan["target_ref"],
        "candidate_digest": source_plan["candidate_digest"],
        "scope_in": ["Análise delimitada no contrato."],
        "scope_out": ["Implementação, contato lateral, nota e veredito."],
        "inputs": [TARGET],
        "deliverables": [f"Entrega da capacidade {capability}."],
        "done": ["Todos os campos obrigatórios têm prova ou lacuna declarada."],
        "required_evidence": ["Fontes, método, limitações e saída íntegra."],
        "depends_on": [],
        "decision_authority": ["Análise consultiva dentro da capacidade."],
        "permissions": permissions(),
        "stop_when": ["Alvo, contrato, permissão ou digest divergir."],
        "return_to": DEPARTMENT,
        "issued_at": NOW,
    }


def return_envelope(
    context: dict[str, Any],
    task: dict[str, Any],
    *,
    return_id: str,
    message: str,
) -> dict[str, Any]:
    agent = task["assigned_agent"]
    return {
        "artifact_type": "INNOVATION_AGENT_RETURN",
        "agent_return_id": return_id,
        "causal": causal(
            context,
            agent,
            message=message,
            causes=[task["causal"]["message_id"]],
        ),
        "department_mission_ref": task["department_mission_ref"],
        "department_mission_digest": task["department_mission_digest"],
        "assignment_ref": task["assignment_id"],
        "assignment_digest": canonical_digest(task),
        "target_ref": task["target_ref"],
        "mode": task["mode"],
        "producer_agent": agent,
        "capability": task["capability"],
        "status": "COMPLETED",
        "deliverables": [],
        "evidence_refs": [],
        "claims_unverified": [],
        "assumptions": [],
        "risks": [],
        "pending": [],
        "execution_requests": [],
        "payload": {},
        "returned_to": DEPARTMENT,
        "returned_at": NOW,
    }


def measured_baseline() -> dict[str, Any]:
    return {
        "status": "MEASURED",
        "metric": "Retrabalhos por publicação",
        "value": "8 por semana",
        "method": "Contagem de reaberturas no tracker por sete dias.",
        "source_ref": "evidence-baseline-001",
        "recorded_at": NOW,
        "limitations": ["Janela curta de sete dias."],
    }


def opportunity() -> dict[str, Any]:
    return {
        "opportunity_id": "opportunity-001",
        "job_when": "Quando publico uma nova versão do material",
        "job_want": "quero detectar campos incompletos antes do envio",
        "job_so_that": "para evitar reabertura e retrabalho editorial",
        "pain_or_waste": "Oito reaberturas semanais por campo ausente.",
        "location": "Etapa de revisão anterior à publicação.",
        "affected_users": ["Equipe editorial e revisores."],
        "observable_outcome": "Redução de reaberturas por publicação.",
        "facts": ["O tracker registrou oito reaberturas na janela."],
        "evidence_refs": ["evidence-baseline-001"],
        "inferences": ["Validação antecipada pode reduzir parte do retrabalho."],
        "assumptions": ["A janela observada representa uma semana típica."],
        "pending": [],
        "baseline": measured_baseline(),
        "classification": "NEW",
        "base_opportunity_ref": "n/a",
        "risk_of_inaction": "Retrabalho e atraso permanecem sem controle.",
    }


def saturation_round(
    number: int,
    *,
    candidates: int,
    net_new: int,
    refs: list[str],
) -> dict[str, Any]:
    return {
        "round": number,
        "candidate_count": candidates,
        "net_new_count": net_new,
        "opportunity_refs": refs,
        "search_scope": "Tracker, feedback e fluxo de publicação.",
        "sources_checked": ["tracker-report-001"],
        "queries_or_methods": [
            f"Rodada {number}: buscar reaberturas e agrupar por causa."
        ],
        "dedupe_method": "Mesma dor/job vira DUPLICATE; detalhe novo vira EXTENSION.",
    }


def discovery_return(
    context: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, Any]:
    value = return_envelope(
        context,
        task,
        return_id="agent-return-discovery-001",
        message="message-return-discovery-001",
    )
    value.update(
        {
            "deliverables": ["opportunity-brief-001"],
            "evidence_refs": ["evidence-baseline-001"],
            "assumptions": ["A janela representa uma semana típica."],
            "risks": ["Baseline tem janela curta."],
            "payload": {
                "deliverable_type": "OPPORTUNITY_BRIEF",
                "opportunities": [opportunity()],
                "saturation": {
                    "rounds": [
                        saturation_round(
                            1, candidates=5, net_new=1, refs=["opportunity-001"]
                        ),
                        saturation_round(2, candidates=2, net_new=0, refs=[]),
                        saturation_round(3, candidates=1, net_new=0, refs=[]),
                    ],
                    "declared": True,
                },
            },
        }
    )
    return value


def technology_evaluation(applicable: bool = False) -> dict[str, Any]:
    if applicable:
        return {
            "applicable": True,
            "maturity_stability": "Versão estável e histórico de releases verificado.",
            "community_support": "Mantenedores e canais de suporte identificados.",
            "maintenance_cost": "Custo de atualização e operação estimado com fonte.",
            "lock_in_exit": "Exportação e reversão documentadas.",
            "current_baseline_comparison": "Comparação com o fluxo atual medido.",
            "poc": "PoC isolada mede tempo e falhas contra limiares prévios.",
            "source_refs": ["source-tech-docs-001"],
            "disposition": "DEFER_FOR_EVIDENCE",
        }
    return {
        "applicable": False,
        "maturity_stability": "Não aplicável ao experimento geral.",
        "community_support": "Não aplicável ao experimento geral.",
        "maintenance_cost": "Não aplicável ao experimento geral.",
        "lock_in_exit": "Não aplicável ao experimento geral.",
        "current_baseline_comparison": "Não aplicável ao experimento geral.",
        "poc": "Não aplicável ao experimento geral.",
        "source_refs": [],
        "disposition": "NOT_APPLICABLE",
    }


def alternative(n: int) -> dict[str, Any]:
    return {
        "alternative_id": f"alternative-{n:03d}",
        "description": f"Alternativa reversível {n} para validação antecipada.",
        "impact": f"Redução esperada de reaberturas na opção {n}, não comprovada.",
        "effort": "Faixa pequena, estimativa declarada como suposição.",
        "risk": "Pode introduzir falso positivo no fluxo editorial.",
        "basis_or_assumption": "Hipótese baseada no tracker; exige PoC.",
        "reversible": True,
        "trade_offs": [f"Mais prevenção na opção {n} em troca de uma etapa curta."],
    }


def experiment(subject: str = "GENERAL") -> dict[str, Any]:
    tech = subject == "TECHNOLOGY"
    questions = (
        ["A latência cabe no orçamento?", "A reversão preserva os dados?"]
        if subject == "SPIKE"
        else []
    )
    return {
        "experiment_id": "experiment-001",
        "opportunity_ref": "opportunity-001",
        "subject_kind": subject,
        "alternatives": [alternative(1), alternative(2)],
        "hypothesis": {
            "statement": "Se validar campos antes do envio, então as reaberturas caem 30% em quatro semanas.",
            "change": "Validar campos obrigatórios antes do envio.",
            "expected_effect": "Reduzir reaberturas em 30%.",
            "timebox": "Quatro semanas.",
        },
        "metric": {
            "name": "Retrabalhos por publicação",
            "baseline": "8 por semana",
            "target": "5 ou menos por semana",
            "window": "Quatro semanas",
            "method": "Contagem de reaberturas no tracker.",
            "source_ref": "evidence-baseline-001",
        },
        "protocol": {
            "given": "Amostra isolada de publicações com baseline conhecida.",
            "when": "Executor autorizado aplica a validação candidata.",
            "then": "Contar reaberturas e comparar com os limiares.",
        },
        "thresholds": ["Sucesso: redução de pelo menos 30% sem falha crítica."],
        "vetoes": ["Qualquer perda de conteúdo ou bloqueio irreversível."],
        "decision_rule": {
            "supported_when": "Alvo atingido e nenhum veto observado.",
            "refuted_when": "Resultado não melhora a baseline ou aciona veto.",
            "inconclusive_when": "Amostra ou evidência não sustentam comparação.",
        },
        "smallest_test": "PoC isolada sobre dez publicações sintéticas.",
        "expected_raw_evidence": ["Log e contagem por publicação."],
        "environment": "Ambiente isolado sem produção.",
        "data_policy": "Dados sintéticos, sem conteúdo real.",
        "cleanup": "Remover artefatos da PoC ao final.",
        "rollback": "Descartar a PoC e manter o fluxo atual.",
        "pdca_check": "Após quatro semanas ou vinte publicações.",
        "owner": "diretor-de-lentes",
        "spike_questions": questions,
        "technology_evaluation": technology_evaluation(tech),
    }


def experiment_return(
    context: dict[str, Any],
    task: dict[str, Any],
    subject: str = "GENERAL",
) -> dict[str, Any]:
    value = return_envelope(
        context,
        task,
        return_id="agent-return-experiment-001",
        message="message-return-experiment-001",
    )
    value.update(
        {
            "deliverables": ["experiment-dossier-001"],
            "evidence_refs": ["evidence-baseline-001"],
            "claims_unverified": ["Efeito da alternativa ainda não foi executado."],
            "assumptions": ["Dez casos sintéticos bastam para triagem inicial."],
            "risks": ["Amostra pode ser insuficiente."],
            "pending": [
                pending(
                    "pending-execution-001",
                    blocking=False,
                    description="Execução externa da PoC ainda não autorizada.",
                )
            ],
            "execution_requests": [
                {
                    "request_id": "request-qa-001",
                    "need": "QA_EVIDENCE",
                    "recommended_recipient": "departamento-qa-usabilidade",
                    "route": [DEPARTMENT, "diretor-de-lentes"],
                    "reason": "Executar a PoC e produzir evidência independente.",
                    "evidence_refs": ["experiment-dossier-001"],
                    "status": "RECOMMENDED_NOT_SENT",
                }
            ],
            "payload": {
                "deliverable_type": "EXPERIMENT_DOSSIER",
                "experiments": [experiment(subject)],
                "evidence_reconciliation": {
                    "performed": False,
                    "external_producer_ref": "n/a",
                    "external_evidence": [],
                    "conclusion": "NOT_PERFORMED",
                    "limitations": ["Execução depende de missão separada de QA."],
                },
            },
        }
    )
    return value


def improvement_return(
    context: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, Any]:
    value = return_envelope(
        context,
        task,
        return_id="agent-return-improvement-001",
        message="message-return-improvement-001",
    )
    value.update(
        {
            "deliverables": ["continuous-improvement-report-001"],
            "evidence_refs": ["qa-report-001"],
            "risks": ["Janela ainda curta para padronização global."],
            "payload": {
                "deliverable_type": "CONTINUOUS_IMPROVEMENT_REPORT",
                "reports": [
                    {
                        "improvement_id": "improvement-001",
                        "opportunity_ref": "opportunity-001",
                        "intake_basis": "FRAMED_OPPORTUNITY",
                        "operational_evidence": [],
                        "waste_or_debt": "Reabertura por campo obrigatório ausente.",
                        "source_ref": "tracker-report-001",
                        "current_flow": "Revisor detecta ausência após envio.",
                        "proposed_future_flow": "Proposta de validação anterior ao envio.",
                        "priority": {
                            "impact": "Oito reaberturas semanais na baseline.",
                            "effort": "Pequeno, ainda estimado.",
                            "risk": "Falso positivo pode atrasar envio.",
                            "basis_or_assumption": "Impacto medido; esforço e risco são suposições.",
                        },
                        "metric": {
                            "name": "Retrabalhos por publicação",
                            "baseline": "8 por semana",
                            "target": "5 ou menos por semana",
                            "window": "Quatro semanas",
                            "method": "Contagem no tracker.",
                            "source_ref": "evidence-baseline-001",
                        },
                        "pdca": {
                            "plan": "Aplicar validação reversível na amostra.",
                            "do_external_evidence": [external_evidence()],
                            "check_event": "Após vinte publicações.",
                            "check_observed": "Quatro reaberturas na janela observada.",
                            "check_limitations": ["Amostra pequena."],
                            "act": "NEXT_CYCLE",
                        },
                        "kaizen_action": {
                            "action": "Ampliar a amostra isolada antes de padronizar.",
                            "owner": "diretor-de-lentes",
                            "due_or_event": "Ao completar quarenta publicações.",
                            "acceptance": "Relatório autenticado compara alvo e baseline.",
                            "reversible": True,
                        },
                        "rollback": "Manter o fluxo atual se surgir veto.",
                        "scaffolds_to_review": ["Checklist manual duplicado após automação."],
                    }
                ],
            },
        }
    )
    return value


def consolidated_report(
    context: dict[str, Any],
    source_plan: dict[str, Any],
    tasks: list[dict[str, Any]],
    returns: list[dict[str, Any]],
) -> dict[str, Any]:
    deliverables = [item for value in returns for item in value["deliverables"]]
    evidence = sorted({item for value in returns for item in value["evidence_refs"]})
    claims = sorted({item for value in returns for item in value["claims_unverified"]})
    assumptions = sorted({item for value in returns for item in value["assumptions"]})
    risks = sorted({item for value in returns for item in value["risks"]})
    pendings = [item for value in returns for item in value["pending"]]
    requests = [item for value in returns for item in value["execution_requests"]]
    return {
        "artifact_type": "INNOVATION_CONSOLIDATED_REPORT",
        "report_id": "innovation-report-001",
        "causal": causal(
            context,
            message="message-report-001",
            causes=[value["causal"]["message_id"] for value in returns],
        ),
        "department_mission_ref": context["mission_ref"],
        "department_mission_digest": context["mission_digest"],
        "plan_ref": source_plan["plan_id"],
        "plan_digest": canonical_digest(source_plan),
        "mode": source_plan["mode"],
        "target_ref": source_plan["target_ref"],
        "candidate_digest": source_plan["candidate_digest"],
        "accepted_assignment_refs": [
            authenticated(task["assignment_id"], task) for task in tasks
        ],
        "accepted_return_refs": [
            authenticated(value["agent_return_id"], value) for value in returns
        ],
        "portfolio": [
            {
                "initiative_id": "initiative-001",
                "opportunity_ref": "opportunity-001",
                "state": "READY_FOR_EXPERIMENT",
                "priority_band": "NEXT",
                "gate_checks": derive_gate_checks("opportunity-001", returns),
                "gate_source_refs": deliverables,
                "blocking_pending_refs": [],
                "priority_basis": "Impacto medido; esforço e risco declarados.",
                "artifact_refs": deliverables,
                "evidence_refs": evidence,
                "next_event": "Diretor decide se autoriza missão externa de execução.",
            }
        ],
        "artifact_refs": deliverables,
        "evidence_refs": evidence,
        "claims_unverified": claims,
        "assumptions": assumptions,
        "risks": risks,
        "pending": pendings,
        "dissent_refs": [],
        "execution_requests": requests,
        "skill_evolution_recommendations": [],
        "test_summary": {
            "pass": 0,
            "fail": 0,
            "skip": 0,
            "skip_reasons": [],
            "critical_fail": False,
        },
        "technical_recommendation": "Autorizar prova externa ou manter pendente.",
        "returned_to": "diretor-de-lentes",
        "returned_at": NOW,
    }


def route_rejection(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": "INNOVATION_ROUTE_REJECTION",
        "rejection_id": "innovation-rejection-001",
        "causal": causal(
            context,
            message="message-rejection-001",
            causes=[context["mission_message_id"]],
        ),
        "code": "BLOCKED_BYPASS_ATTEMPT",
        "observed_sender": "ceo-maestro",
        "expected_route": "diretor-de-lentes → departamento-inovacao-melhoria",
        "violations": ["Pedido direto ao agente sem assignment da gerente."],
        "prevented_effect": "Nenhuma análise ou ação foi iniciada.",
        "resume_when": "Diretor emitir DEPARTMENT_MISSION íntegra.",
        "returned_to": "diretor-de-lentes",
        "detected_at": NOW,
    }


def capability_gap(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": "INNOVATION_CAPABILITY_GAP",
        "gap_id": "innovation-gap-001",
        "causal": causal(
            context,
            message="message-gap-001",
            causes=[context["mission_message_id"]],
        ),
        "required_capability": "EXPERIMENT_DESIGN",
        "expected_agent": "agente-experimentos-e-spikes",
        "search_sources": ["agents-directory", "agent-contracts"],
        "queries_or_ids_checked": ["Pasta e metadata do agente esperado."],
        "negative_evidence": ["Metadata ausente na descoberta runtime."],
        "blocked_scope": ["Desenho do experimento."],
        "impact": "Iniciativa não pode avançar ao gate experimental.",
        "reversible_planning_allowed": True,
        "owner": "diretor-de-lentes",
        "resume_when": "Restaurar agente íntegro ou reduzir escopo por autoridade.",
        "status": "OPEN",
        "returned_to": "diretor-de-lentes",
        "detected_at": NOW,
    }


def to_department_return(report: dict[str, Any]) -> dict[str, Any]:
    source = report["causal"]
    return {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "department-return-innovation-001",
        "causal": {
            **source,
            "message_id": "message-department-return-innovation-001",
            "causation_message_ids": [source["message_id"]],
            "producer": DEPARTMENT,
            "created_at": report["returned_at"],
        },
        "department_mission_ref": report["department_mission_ref"],
        "returned_by": DEPARTMENT,
        "state": "RETURNED",
        "scope_touched": ["Fluxo de publicação."],
        "artifact_refs": [
            authenticated(report["report_id"], report),
            report["plan_ref"],
        ],
        "evidence_refs": copy.deepcopy(report["evidence_refs"]),
        "candidate_digest": report["candidate_digest"],
        "test_summary": copy.deepcopy(report["test_summary"]),
        "pending_refs": [item["pending_id"] for item in report["pending"]],
        "dissent_refs": copy.deepcopy(report["dissent_refs"]),
        "returned_to": "diretor-de-lentes",
        "returned_at": report["returned_at"],
    }


def build_bundle(
    *,
    mode: str = "ATUA",
    subject: str = "GENERAL",
    with_improvement: bool = False,
) -> dict[str, Any]:
    """Uma rodada inteira e coerente: é sobre ela que a reconciliação roda."""
    mission = director_mission(mode)
    context = trusted_context(mission)
    source_plan = plan(context)

    discovery_task = assignment(context, source_plan, "agente-descoberta-de-oportunidades")
    experiment_task = assignment(context, source_plan, "agente-experimentos-e-spikes")
    tasks = [discovery_task, experiment_task]
    returns = [
        discovery_return(context, discovery_task),
        experiment_return(context, experiment_task, subject),
    ]
    if with_improvement:
        improvement_task = assignment(context, source_plan, "agente-melhoria-continua")
        tasks.append(improvement_task)
        returns.append(improvement_return(context, improvement_task))

    report = consolidated_report(context, source_plan, tasks, returns)
    return {
        "mission": mission,
        "context": context,
        "plan": source_plan,
        "tasks": tasks,
        "returns": returns,
        "report": report,
        "boundary": to_department_return(report),
    }


# --------------------------------------------------------------------------
# Camada semântica
# --------------------------------------------------------------------------


def walk_strings(value: Any, field: str | None = None) -> list[tuple[str, str]]:
    """Todas as strings do artefato, com o campo de origem, pulando exclusões."""
    if field in NEGATIVE_DECLARATION_FIELDS:
        return []
    if isinstance(value, str):
        return [(field or "$", value)]
    if isinstance(value, list):
        found: list[tuple[str, str]] = []
        for item in value:
            found.extend(walk_strings(item, field))
        return found
    if isinstance(value, dict):
        found = []
        for key, item in value.items():
            found.extend(walk_strings(item, key))
        return found
    return []


def judgment_language_errors(value: dict[str, Any]) -> list[str]:
    """Anti-julgamento também no texto livre, não só no nome da propriedade."""
    errors: list[str] = []
    for field, text in walk_strings(value):
        for pattern, label in JUDGMENT_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                errors.append(f"julgamento em texto livre ({label}) no campo {field}")
    return errors


def saturation_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    saturation = payload.get("saturation", {})
    rounds = saturation.get("rounds", [])
    opportunities = payload.get("opportunities", [])
    new_ids = {
        item.get("opportunity_id")
        for item in opportunities
        if item.get("classification") == "NEW"
    }

    numbers = [item.get("round") for item in rounds]
    if numbers != list(range(1, len(rounds) + 1)):
        errors.append("saturação: rodadas devem ser sequenciais a partir de 1")

    seen: list[str] = []
    for item in rounds:
        if item.get("net_new_count", 0) > item.get("candidate_count", 0):
            errors.append("saturação: líquidos novos excedem candidatos")
        refs = item.get("opportunity_refs", [])
        if len(refs) != item.get("net_new_count", -1):
            errors.append(
                f"saturação: rodada {item.get('round')} conta "
                f"{item.get('net_new_count')} líquidos e lista {len(refs)}"
            )
        seen.extend(refs)

    if len(seen) != len(set(seen)):
        errors.append("saturação: mesma oportunidade contada em duas rodadas")
    if set(seen) != new_ids:
        errors.append("saturação: ledger não reconstrói as oportunidades NEW")

    qualifies = (
        len(rounds) >= 2
        and rounds[-1].get("net_new_count", 99) < 2
        and rounds[-2].get("net_new_count", 99) < 2
    )
    if saturation.get("declared") != qualifies:
        errors.append("saturação: declaração diverge das duas rodadas finais")
    if saturation.get("declared") and len(rounds) >= 2:
        if rounds[-1].get("search_scope") != rounds[-2].get("search_scope"):
            errors.append("saturação: duas rodadas finais têm escopo incomparável")
        if set(rounds[-1].get("sources_checked", [])) != set(
            rounds[-2].get("sources_checked", [])
        ):
            errors.append("saturação: duas rodadas finais têm fontes incomparáveis")
    return errors


def technology_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    reconciliation = payload.get("evidence_reconciliation", {})
    supported = (
        reconciliation.get("performed") is True
        and reconciliation.get("conclusion") == "HYPOTHESIS_SUPPORTED"
        and bool(reconciliation.get("external_evidence"))
    )
    for item in payload.get("experiments", []):
        subject = item.get("subject_kind")
        questions = item.get("spike_questions", [])
        tech = item.get("technology_evaluation", {})
        if subject == "SPIKE" and not 2 <= len(questions) <= 5:
            errors.append("spike: exige duas a cinco perguntas")
        if subject != "SPIKE" and questions:
            errors.append("experimento não-spike não deve inventar perguntas de spike")
        if subject == "TECHNOLOGY":
            if not tech.get("applicable"):
                errors.append("tecnologia: avaliação deve ser aplicável")
            if not tech.get("source_refs"):
                errors.append("tecnologia: avaliação exige fontes")
            if tech.get("disposition") == "NOT_APPLICABLE":
                errors.append("tecnologia: disposição NOT_APPLICABLE é contraditória")
        elif tech.get("applicable") or tech.get("disposition") != "NOT_APPLICABLE":
            errors.append("não-tecnologia: bloco tecnológico deve ser não aplicável")
        if tech.get("disposition") == "ADOPT" and not supported:
            errors.append(
                "tecnologia: ADOPT exige reconciliação externa com hipótese sustentada"
            )
    return errors


def pdca_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for item in payload.get("reports", []):
        pdca = item.get("pdca", {})
        evidence = pdca.get("do_external_evidence", [])
        act = pdca.get("act")
        if act != "INSUFFICIENT_EVIDENCE" and not evidence:
            errors.append(f"PDCA: {act} exige evidência externa autenticada do Do")
        if act == "INSUFFICIENT_EVIDENCE" and evidence:
            errors.append("PDCA: INSUFFICIENT_EVIDENCE não convive com Do provado")
        if item.get("intake_basis") == "OPERATIONAL_EVIDENCE" and not item.get(
            "operational_evidence"
        ):
            errors.append("melhoria: intake operacional exige evidência autenticada")
    return errors


def request_route_errors(request: dict[str, Any]) -> list[str]:
    """A rota é sempre gerente → Diretor: não existe destino direto."""
    errors: list[str] = []
    expected = [DEPARTMENT, "diretor-de-lentes"]
    if request.get("route") != expected:
        errors.append(
            f"pedido {request.get('request_id')}: rota {request.get('route')} "
            f"deve ser {expected}"
        )
    if request.get("status") != "RECOMMENDED_NOT_SENT":
        errors.append("pedido: status deve preservar que o contato não ocorreu")
    if request.get("recommended_recipient") == "departamento-negocios":
        authorization = request.get("matrix_authorization")
        if not authorization:
            errors.append("pedido a Negócios: falta autorização matricial do CEO")
        elif authorization.get("granted_by") != "ceo-maestro":
            errors.append("pedido a Negócios: autorização matricial não é do CEO")
    return errors


def semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    kind = value.get("artifact_type")

    expected_producer = {
        "INNOVATION_PLAN": DEPARTMENT,
        "INNOVATION_ASSIGNMENT": DEPARTMENT,
        "INNOVATION_CONSOLIDATED_REPORT": DEPARTMENT,
        "INNOVATION_ROUTE_REJECTION": DEPARTMENT,
        "INNOVATION_CAPABILITY_GAP": DEPARTMENT,
    }.get(kind)
    if expected_producer and value.get("causal", {}).get("producer") != expected_producer:
        errors.append(f"{kind}: produtor causal deve ser {expected_producer}")

    errors.extend(judgment_language_errors(value))

    if kind == "INNOVATION_PLAN":
        roster = value.get("agent_roster", [])
        mapping = {item.get("agent"): item.get("capability") for item in roster}
        if len(mapping) != 3 or mapping != AGENT_CAPABILITY:
            errors.append("plano: roster deve conter os três pares agente/capability exatos")
        if not any(item.get("selected") for item in roster):
            errors.append("plano: roster sem nenhum agente selecionado não contrata nada")

    if kind == "INNOVATION_ASSIGNMENT":
        agent = value.get("assigned_agent")
        capability = value.get("capability")
        if AGENT_CAPABILITY.get(agent) != capability:
            errors.append("assignment: agente e capability não correspondem")
        if value.get("mode") == "CONSULTA":
            environment = value.get("permissions", {}).get("environment")
            if environment != "READ_ONLY":
                errors.append("assignment: CONSULTA não concede ambiente além de leitura")

    if kind == "INNOVATION_AGENT_RETURN":
        agent = value.get("producer_agent")
        capability = value.get("capability")
        if AGENT_CAPABILITY.get(agent) != capability:
            errors.append("retorno: agente e capability não correspondem")
        if value.get("causal", {}).get("producer") != agent:
            errors.append("retorno: produtor causal deve ser o agente declarado")
        payload = value.get("payload", {})

        for request in value.get("execution_requests", []):
            errors.extend(request_route_errors(request))

        if capability == "OPPORTUNITY_DISCOVERY":
            errors.extend(saturation_errors(payload))
            for item in payload.get("opportunities", []):
                cls = item.get("classification")
                base = item.get("base_opportunity_ref")
                if cls == "NEW" and base != "n/a":
                    errors.append("oportunidade NEW não deve apontar item-base")
                if cls in {"EXTENSION", "DUPLICATE"} and base == "n/a":
                    errors.append(f"oportunidade {cls} exige item-base")

        if capability == "EXPERIMENT_DESIGN":
            errors.extend(technology_errors(payload))

        if capability == "CONTINUOUS_IMPROVEMENT":
            errors.extend(pdca_errors(payload))

    if kind == "INNOVATION_CONSOLIDATED_REPORT":
        advanced = {
            "READY_FOR_EXPERIMENT",
            "IN_EXPERIMENT",
            "IN_MEASUREMENT",
            "LEARNED",
        }
        for item in value.get("portfolio", []):
            state = item.get("state")
            band = item.get("priority_band")
            gates = item.get("gate_checks", {})
            blocking = item.get("blocking_pending_refs", [])
            if state in advanced and not all(gates.values()):
                errors.append(f"portfólio: {state} exige todos os gates")
            if state == "EVIDENCE_PENDING" and all(gates.values()):
                errors.append("portfólio: EVIDENCE_PENDING contradiz gate completo")
            if blocking and state != "BLOCKED":
                errors.append("portfólio: pendência bloqueante exige estado BLOCKED")
            if band == "NOW" and not all(gates.values()):
                errors.append("portfólio: faixa NOW exige gate completo")
            if band == "BLOCKED" and state != "BLOCKED":
                errors.append("portfólio: faixa e estado de bloqueio divergem")
        for request in value.get("execution_requests", []):
            errors.extend(request_route_errors(request))
        expected_evolution_route = [
            DEPARTMENT,
            "diretor-de-lentes",
            "ceo-maestro",
        ]
        for item in value.get("skill_evolution_recommendations", []):
            if item.get("route") != expected_evolution_route:
                errors.append("evolução: rota deve terminar no CEO, sem chamada direta")
            if item.get("status") != "RECOMMENDED_TO_CEO_NOT_SENT":
                errors.append("evolução: recomendação não pode alegar envio/execução")
            if not item.get("evidence_refs"):
                errors.append("evolução: recomendação sem evidência não sai daqui")
        summary = value.get("test_summary", {})
        for key in ("pass", "fail", "skip"):
            count = summary.get(key)
            if not isinstance(count, int) or isinstance(count, bool) or count != 0:
                errors.append("relatório: Inovação não apropria contagens de QA")

    return errors


# --------------------------------------------------------------------------
# Contexto confiável e reconciliação da cadeia
# --------------------------------------------------------------------------


def context_errors(
    artifact: dict[str, Any],
    context: dict[str, Any],
    *,
    label: str,
) -> list[str]:
    errors: list[str] = []
    block = artifact.get("causal", {})
    for field in CONTEXT_CAUSAL_FIELDS:
        if block.get(field) != context[field]:
            errors.append(f"{label}: campo causal fora do contexto confiável: {field}")
    if artifact.get("department_mission_ref") != context["mission_ref"]:
        errors.append(f"{label}: missão declarada não é a missão recebida")
    if artifact.get("department_mission_digest") != context["mission_digest"]:
        errors.append(f"{label}: digest da missão não confere")
    if "mode" in artifact and artifact["mode"] != context["mode"]:
        errors.append(f"{label}: mode divergente do autorizado pela missão")
    if "target_ref" in artifact and artifact["target_ref"] not in context["inputs"]:
        errors.append(f"{label}: alvo fora dos insumos da missão")
    if "candidate_digest" in artifact and artifact["candidate_digest"] != context[
        "candidate_digest"
    ]:
        errors.append(f"{label}: candidato divergente do contexto confiável")
    return errors


def assignment_return_errors(
    task: dict[str, Any],
    result: dict[str, Any],
) -> list[str]:
    """Fecha assignment→retorno sem confiar em ids declarados isoladamente."""
    errors: list[str] = []
    if result.get("assignment_ref") != task.get("assignment_id"):
        errors.append("correlação: assignment_ref divergente")
    if result.get("assignment_digest") != canonical_digest(task):
        errors.append("correlação: assignment_digest divergente")
    if result.get("producer_agent") != task.get("assigned_agent"):
        errors.append("correlação: produtor não é o agente contratado")
    if result.get("capability") != task.get("capability"):
        errors.append("correlação: capability diverge da assignment")
    if result.get("mode") != task.get("mode"):
        errors.append("correlação: mode não foi preservado da assignment")
    if result.get("target_ref") != task.get("target_ref"):
        errors.append("correlação: alvo divergente da assignment")
    task_causal = task.get("causal", {})
    result_causal = result.get("causal", {})
    if result_causal.get("causation_message_ids") != [task_causal.get("message_id")]:
        errors.append("correlação: causa direta não é a assignment")
    for field in CONTEXT_CAUSAL_FIELDS:
        if result_causal.get(field) != task_causal.get(field):
            errors.append(f"correlação: campo causal divergente: {field}")
    return errors


def derive_gate_checks(
    opportunity_ref: str,
    returns: list[dict[str, Any]],
) -> dict[str, bool]:
    """O gate é recalculado dos retornos; o booleano declarado só confirma."""
    found_opportunity: dict[str, Any] | None = None
    found_experiment: dict[str, Any] | None = None
    for value in returns:
        payload = value.get("payload", {})
        for item in payload.get("opportunities", []):
            if item.get("opportunity_id") == opportunity_ref:
                found_opportunity = item
        for item in payload.get("experiments", []):
            if item.get("opportunity_ref") == opportunity_ref:
                found_experiment = item

    o = found_opportunity or {}
    e = found_experiment or {}
    hypothesis = e.get("hypothesis", {})
    metric = e.get("metric", {})
    alternatives = e.get("alternatives", [])
    distinct = {
        json.dumps(item, ensure_ascii=False, sort_keys=True) for item in alternatives
    }
    return {
        "job": bool(o.get("job_when") and o.get("job_want") and o.get("job_so_that")),
        "pain_location": bool(o.get("pain_or_waste") and o.get("location")),
        "baseline": o.get("baseline", {}).get("status") == "MEASURED",
        "hypothesis": bool(
            hypothesis.get("change")
            and hypothesis.get("expected_effect")
            and hypothesis.get("timebox")
        ),
        "metric_target_window": bool(
            metric.get("baseline")
            and metric.get("target")
            and metric.get("window")
            and metric.get("source_ref")
        ),
        "two_alternatives": len(distinct) >= 2,
        "smallest_test": bool(e.get("smallest_test")),
        "owner": bool(e.get("owner")),
        "rollback": bool(e.get("rollback")),
        "pdca_check": bool(e.get("pdca_check")),
        "evidence_dependencies_vetoes": bool(e.get("vetoes") and o.get("evidence_refs")),
    }


def chain_errors(bundle: dict[str, Any]) -> list[str]:
    """Reconcilia missão → plano → assignments → retornos → relatório."""
    context = bundle["context"]
    source_plan = bundle["plan"]
    tasks = bundle["tasks"]
    returns = bundle["returns"]
    report = bundle["report"]
    errors: list[str] = []

    errors.extend(context_errors(source_plan, context, label="plano"))
    if source_plan["causal"]["causation_message_ids"] != [context["mission_message_id"]]:
        errors.append("plano: causa direta não é a missão do Diretor")

    selected = {
        item["agent"] for item in source_plan.get("agent_roster", []) if item.get("selected")
    }
    plan_digest = canonical_digest(source_plan)
    issued: dict[str, dict[str, Any]] = {}
    for task in tasks:
        label = f"assignment {task['assignment_id']}"
        errors.extend(context_errors(task, context, label=label))
        if task.get("plan_ref") != source_plan["plan_id"]:
            errors.append(f"{label}: plano declarado não é o plano da rodada")
        if task.get("plan_digest") != plan_digest:
            errors.append(f"{label}: digest do plano não confere")
        if task.get("assigned_agent") not in selected:
            errors.append(f"{label}: agente não foi selecionado no roster")
        issued[task["assignment_id"]] = task

    accepted: dict[str, dict[str, Any]] = {}
    for value in returns:
        label = f"retorno {value['agent_return_id']}"
        errors.extend(context_errors(value, context, label=label))
        task = issued.get(value.get("assignment_ref"))
        if task is None:
            errors.append(f"{label}: cita assignment que a rodada nunca emitiu")
            continue
        errors.extend(f"{label}: {item}" for item in assignment_return_errors(task, value))
        accepted[value["agent_return_id"]] = value

    errors.extend(context_errors(report, context, label="relatório"))
    if report.get("plan_ref") != source_plan["plan_id"]:
        errors.append("relatório: plano declarado não é o plano da rodada")
    if report.get("plan_digest") != plan_digest:
        errors.append("relatório: digest do plano não confere")

    expected_tasks = {authenticated(task["assignment_id"], task) for task in tasks}
    if set(report.get("accepted_assignment_refs", [])) - expected_tasks:
        errors.append("relatório: aceita assignment inexistente ou com digest forjado")
    expected_returns = {
        authenticated(value["agent_return_id"], value) for value in returns
    }
    if set(report.get("accepted_return_refs", [])) - expected_returns:
        errors.append("relatório: aceita retorno inexistente ou com digest forjado")

    accepted_ids = {
        item.split("@", 1)[0] for item in report.get("accepted_return_refs", [])
    }
    accepted_task_ids = {
        item.split("@", 1)[0] for item in report.get("accepted_assignment_refs", [])
    }
    for return_id in accepted_ids:
        value = accepted.get(return_id)
        if value and value.get("assignment_ref") not in accepted_task_ids:
            errors.append(
                f"relatório: retorno {return_id} não tem assignment aceito correspondente"
            )

    delivered = {item for value in returns for item in value["deliverables"]}
    evidence = {item for value in returns for item in value["evidence_refs"]}
    claims = {item for value in returns for item in value["claims_unverified"]}
    pending_ids = {item["pending_id"] for value in returns for item in value["pending"]}
    blocking_ids = {
        item["pending_id"]
        for value in returns
        for item in value["pending"]
        if item.get("blocking")
    }
    opportunities = {
        item["opportunity_id"]
        for value in returns
        for item in value.get("payload", {}).get("opportunities", [])
    }

    if set(report.get("artifact_refs", [])) - delivered:
        errors.append("relatório: cita artefato que nenhum agente entregou")
    if set(report.get("evidence_refs", [])) - evidence:
        errors.append("relatório: cita evidência que nenhum agente produziu")
    if claims - set(report.get("claims_unverified", [])):
        errors.append("relatório: silenciou alegação não verificada de um agente")
    report_pendings = {item["pending_id"] for item in report.get("pending", [])}
    if pending_ids - report_pendings:
        errors.append("relatório: silenciou pendência de um agente")

    for item in report.get("portfolio", []):
        initiative = item.get("initiative_id")
        reference = item.get("opportunity_ref")
        if reference not in opportunities:
            errors.append(
                f"portfólio {initiative}: oportunidade não existe em nenhum retorno"
            )
            continue
        derived = derive_gate_checks(reference, returns)
        if item.get("gate_checks") != derived:
            divergent = sorted(
                key
                for key, expected in derived.items()
                if item.get("gate_checks", {}).get(key) != expected
            )
            errors.append(
                f"portfólio {initiative}: gate declarado diverge do derivado em {divergent}"
            )
        if set(item.get("gate_source_refs", [])) - delivered:
            errors.append(f"portfólio {initiative}: prova de gate não foi entregue")
        if set(item.get("blocking_pending_refs", [])) - report_pendings:
            errors.append(f"portfólio {initiative}: bloqueio cita pendência inexistente")

    listed_blocking = {
        ref for item in report.get("portfolio", []) for ref in item.get("blocking_pending_refs", [])
    }
    if blocking_ids - listed_blocking:
        errors.append("relatório: pendência bloqueante não afeta nenhuma iniciativa")

    known_refs = delivered | evidence
    for request in report.get("execution_requests", []):
        if set(request.get("evidence_refs", [])) - known_refs:
            errors.append(
                f"pedido {request.get('request_id')}: evidência citada não existe na rodada"
            )
    for item in report.get("skill_evolution_recommendations", []):
        if set(item.get("evidence_refs", [])) - known_refs:
            errors.append("evolução: evidência citada não existe na rodada")

    return errors


def bridge_errors(
    report: dict[str, Any],
    boundary: dict[str, Any],
    director_schema: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    errors.extend(
        f"fonte local: {item}"
        for item in validate_schema(report, LOCAL_SCHEMA, LOCAL_SCHEMA)
    )
    errors.extend(f"fonte local: {item}" for item in semantic_errors(report))
    errors.extend(
        f"schema consumidor: {item}"
        for item in validate_schema(
            boundary,
            director_schema["$defs"]["departmentReturn"],
            director_schema,
        )
    )
    if boundary.get("returned_by") != DEPARTMENT:
        errors.append("ponte: returned_by divergente")
    if boundary.get("causal", {}).get("producer") != DEPARTMENT:
        errors.append("ponte: produtor causal divergente")
    if boundary.get("department_mission_ref") != report.get("department_mission_ref"):
        errors.append("ponte: missão divergente")
    if boundary.get("candidate_digest") != report.get("candidate_digest"):
        errors.append("ponte: candidato divergente")
    if boundary.get("causal", {}).get("causation_message_ids") != [
        report.get("causal", {}).get("message_id")
    ]:
        errors.append("ponte: causa direta não é o relatório")
    expected_ref = authenticated(report["report_id"], report)
    if expected_ref not in boundary.get("artifact_refs", []):
        errors.append("ponte: relatório não está autenticado por digest")
    if report.get("plan_ref") not in boundary.get("artifact_refs", []):
        errors.append("ponte: plano da rodada não aparece no envelope")
    if boundary.get("evidence_refs") != report.get("evidence_refs"):
        errors.append("ponte: evidências divergentes")
    if boundary.get("pending_refs") != [
        item["pending_id"] for item in report.get("pending", [])
    ]:
        errors.append("ponte: pendências divergentes")
    if boundary.get("dissent_refs") != report.get("dissent_refs"):
        errors.append("ponte: dissensos divergentes")
    if boundary.get("test_summary") != report.get("test_summary"):
        errors.append("ponte: test_summary diverge da fonte")
    errors.extend(f"ponte: {item}" for item in judgment_language_errors(boundary))
    return errors


# --------------------------------------------------------------------------
# Estrutura normativa (o que a auditoria de governança encontrava sozinha)
# --------------------------------------------------------------------------


def ordered_sections_errors(
    path: Path,
    expected: tuple[str, ...],
    label: str,
) -> list[str]:
    if not path.is_file():
        return [f"{label}: arquivo ausente"]
    lines = path.read_text(encoding="utf-8").splitlines()
    found = [line.strip() for line in lines if line.startswith("## ")]
    missing = [item for item in expected if item not in found]
    if missing:
        return [f"{label}: seções ausentes {missing}"]
    positions = [found.index(item) for item in expected]
    if positions != sorted(positions):
        return [f"{label}: seções fora da ordem canônica"]
    return []


def tokens_errors(path: Path, tokens: tuple[str, ...], label: str) -> list[str]:
    if not path.is_file():
        return [f"{label}: arquivo ausente"]
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    return [f"{label}: tokens obrigatórios ausentes {missing}"] if missing else []


def protocol_errors() -> list[str]:
    """Cada seção fecha com `Concluído quando:` e os riscos moram num lugar só."""
    if not PROTOCOL_PATH.is_file():
        return ["protocolo: arquivo ausente"]
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    errors: list[str] = []

    blocks = re.split(r"^## ", text, flags=re.MULTILINE)[1:]
    for block in blocks:
        title = block.splitlines()[0].strip()
        if "**Concluído quando:**" not in block:
            errors.append(f"protocolo: seção sem `Concluído quando:` — {title}")

    if not RESIDUAL_HEADING.search(text):
        errors.append("protocolo: falta a tabela única de riscos residuais")
    else:
        section = text[RESIDUAL_HEADING.search(text).end() :]
        header = next(
            (line for line in section.splitlines() if line.startswith("| Id ")),
            "",
        )
        if "Teto" not in header:
            errors.append("protocolo: tabela de riscos residuais sem coluna `Teto`")
        rows = [
            line
            for line in section.splitlines()
            if line.startswith("| **R") and line.count("|") >= 6
        ]
        if len(rows) < 4:
            errors.append(
                f"protocolo: riscos residuais declarados de menos ({len(rows)})"
            )

    declaring = [
        path.relative_to(PACKAGE_ROOT).as_posix()
        for path in sorted(PACKAGE_ROOT.rglob("*.md"))
        if RESIDUAL_HEADING.search(path.read_text(encoding="utf-8"))
    ]
    if declaring != ["references/protocolo-inovacao-melhoria.md"]:
        errors.append(f"riscos residuais declarados em mais de um lugar: {declaring}")
    return errors


def placar_errors() -> list[str]:
    if not PLACAR_PATH.is_file():
        return ["placar: arquivo ausente"]
    text = PLACAR_PATH.read_text(encoding="utf-8")
    errors: list[str] = []
    if "Executado?" not in text:
        errors.append("placar: tabela mecânica sem coluna `Executado?`")
    if "## O que ainda não foi provado" not in text:
        errors.append("placar: falta a seção `O que ainda não foi provado`")
    if "pendente de execução" in text:
        errors.append("placar: ainda declara bateria pendente de execução")
    if not re.search(r"\bPASS\b", text) or not re.search(r"\bSKIP\b", text):
        errors.append("placar: não declara PASS/FAIL/SKIP com honestidade")
    return errors


def audit_errors() -> list[str]:
    if not AUDIT_PATH.is_file():
        return ["auditoria: arquivo ausente"]
    text = AUDIT_PATH.read_text(encoding="utf-8")
    errors: list[str] = []
    if "PENDING_EXECUTION" in text:
        errors.append("auditoria adversarial ainda está PENDING_EXECUTION")
    if "mutações" not in text and "mutacoes" not in text:
        errors.append("auditoria adversarial sem corpus de mutações registrado")
    if "escape" not in text.lower():
        errors.append("auditoria adversarial sem contagem de escapes")
    return errors


def link_errors() -> list[str]:
    """Resolve links no local atual e, em staging, no destino canônico."""
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    errors: list[str] = []
    for path in sorted(PACKAGE_ROOT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        relative_file = path.relative_to(PACKAGE_ROOT)
        canonical_file = CANONICAL_PACKAGE_ROOT / relative_file
        for target in pattern.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            raw = target.split("#", 1)[0]
            local = (path.parent / raw).resolve()
            canonical = (canonical_file.parent / raw).resolve()
            if not local.exists() and not canonical.exists():
                errors.append(f"link quebrado em {relative_file}: {target}")
    return errors


def adr_errors() -> list[str]:
    """A serie de ADR e global: o numero deste pacote nao pode ser usado por outro.

    O numero e derivado do proprio arquivo, nao fixado em literal — frentes
    paralelas mudam o proximo livre, e cheque com numero cravado quebra sozinho.

    A norma e **unicidade, nao maximalidade**. "Cunhar o proximo livre" e regra
    do momento da criacao (GUIA, passo 4); virar cheque permanente de
    `nosso > max(todos)` seria um gate que proibe o futuro: no dia em que uma
    frente vizinha cunhar um numero maior, este pacote reprovaria sozinho, com o
    proprio ADR intacto e unico. Por isso a colisao e verificada aqui e a serie
    global fica com o motor compartilhado, que ja trata as excecoes historicas.
    """
    locais = sorted(REFERENCES_ROOT.glob("adr-*.md"))
    if len(locais) != 1:
        return [f"esperado exatamente um ADR local, encontrados {len(locais)}"]
    ours = locais[0]
    match = re.match(r"adr-(\d+)-", ours.name)
    if not match:
        return [f"nome de ADR fora do padrao: {ours.name}"]
    nosso = int(match.group(1))

    errors: list[str] = []
    outros: dict[int, list[str]] = {}
    for path in STRUCTURE_ROOT.rglob("adr-*.md"):
        if path.resolve() == ours.resolve():
            continue
        m = re.match(r"adr-(\d+)-", path.name)
        if m:
            outros.setdefault(int(m.group(1)), []).append(path.name)

    if nosso in outros:
        errors.append(f"ADR-{nosso:03d} colide com {outros[nosso]}")
    errors.extend(validate_adr_series(STRUCTURE_ROOT))
    return errors


def legacy_errors() -> list[str]:
    errors: list[str] = []
    if not LEGACY_ROOT.is_dir():
        return [f"legado ausente em {LEGACY_ROOT}"]
    found = sorted(
        path.relative_to(LEGACY_ROOT).as_posix()
        for path in LEGACY_ROOT.rglob("*")
        if path.is_file()
    )
    if found != sorted(LEGACY_MANIFEST):
        errors.append(
            f"legado: esperados {len(LEGACY_MANIFEST)} arquivos, encontrados {len(found)}"
        )
    for relative, expected in LEGACY_MANIFEST.items():
        path = LEGACY_ROOT / relative
        if not path.is_file():
            errors.append(f"legado: arquivo ausente {relative}")
        elif sha256_file(path) != expected:
            errors.append(f"legado: hash divergente {relative}")
    total = sum(path.stat().st_size for path in LEGACY_ROOT.rglob("*") if path.is_file())
    if total != 101_022:
        errors.append(f"legado: tamanho total divergente ({total})")
    return errors


def eval_errors() -> list[str]:
    errors: list[str] = []
    data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    if len(cases) < 12:
        errors.append("evals: menos de 12 casos")
    if not any(case.get("origem") == "real" for case in cases):
        errors.append("evals: nenhum caso real")
    if not any(case.get("origem") == "sintetica" for case in cases):
        errors.append("evals: nenhum caso sintético")
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        errors.append("evals: ids duplicados")
    for case in cases:
        if len(case.get("assertions", [])) < 3:
            errors.append(f"evals: {case.get('id')} tem menos de 3 assertions")
        prompt = case.get("prompt", "").lower()
        if DEPARTMENT in prompt or f"${DEPARTMENT}" in prompt:
            errors.append(f"evals: {case.get('id')} nomeia a skill")
        if case.get("origem") not in {"real", "sintetica"}:
            errors.append(f"evals: origem inválida em {case.get('id')}")
    return errors


LOCAL_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
DIRECTOR_SCHEMA = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))

PASS = 0
FAIL = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"[PASS] {label}")
    else:
        FAIL += 1
        suffix = f": {detail}" if detail else ""
        print(f"[FAIL] {label}{suffix}")


def expect_valid(label: str, value: dict[str, Any]) -> None:
    errors = validate_schema(value, LOCAL_SCHEMA, LOCAL_SCHEMA) + semantic_errors(value)
    check(label, not errors, " | ".join(errors))


def expect_invalid(label: str, value: dict[str, Any]) -> None:
    errors = validate_schema(value, LOCAL_SCHEMA, LOCAL_SCHEMA) + semantic_errors(value)
    check(label, bool(errors), "fixture negativa foi aceita")


def expect_chain_invalid(label: str, bundle: dict[str, Any]) -> None:
    errors = chain_errors(bundle) + validate_schema(
        bundle["report"], LOCAL_SCHEMA, LOCAL_SCHEMA
    ) + semantic_errors(bundle["report"])
    check(label, bool(errors), "contraprova de cadeia foi aceita")


def main() -> int:
    required = [
        SKILL_PATH,
        CONTRACT_PATH,
        OPENAI_PATH,
        SCHEMA_PATH,
        EVALS_PATH,
        PLACAR_PATH,
        PACKAGE_ROOT / "evals" / "FORWARD-TEST.md",
        AUDIT_PATH,
        PROTOCOL_PATH,
        REFERENCES_ROOT / "fronteiras-e-fontes-canonicas.md",
        REFERENCES_ROOT / "origem-migracao.md",
        REFERENCES_ROOT / "adr-013-tres-agentes-e-inovacao-sem-julgamento.md",
        DIRECTOR_SCHEMA_PATH,
        RULES_PATH,
    ]
    errors = validate_required_files(required, "arquivo obrigatório")
    check("arquivos obrigatórios presentes", not errors, " | ".join(errors))

    errors = validate_frontmatter(SKILL_PATH, DEPARTMENT, max_lines=500)
    check("frontmatter da gerente", not errors, " | ".join(errors))
    errors = validate_openai_yaml(
        OPENAI_PATH,
        "Departamento de Inovação e Melhoria",
        "$departamento-inovacao-melhoria",
        expected_short="Orquestra inovação e melhoria com prova",
    )
    check("metadata da gerente", not errors, " | ".join(errors))

    expected_agents = list(AGENT_CAPABILITY)
    errors = validate_agents_folder(AGENTS_ROOT, expected_agents)
    check("pasta contém exatamente três agentes completos", not errors, " | ".join(errors))
    for agent in expected_agents:
        errors = validate_frontmatter(AGENTS_ROOT / agent / "SKILL.md", agent, max_lines=300)
        check(f"frontmatter {agent}", not errors, " | ".join(errors))
        errors = validate_openai_yaml(
            AGENTS_ROOT / agent / "agents" / "openai.yaml",
            AGENT_DISPLAY[agent],
            f"${agent}",
        )
        check(f"metadata {agent}", not errors, " | ".join(errors))

    # --- estrutura normativa ---
    errors = ordered_sections_errors(
        CONTRACT_PATH, DEPARTMENT_CONTRACT_SECTIONS, "contrato da gerente"
    )
    check("contrato da gerente tem as 12 seções na ordem", not errors, " | ".join(errors))
    for agent in expected_agents:
        errors = ordered_sections_errors(
            AGENTS_ROOT / agent / "CONTRATO-DE-COMPROMISSO.md",
            AGENT_CONTRACT_SECTIONS,
            f"contrato {agent}",
        )
        check(f"contrato {agent} segue as seções canônicas", not errors, " | ".join(errors))
        errors = tokens_errors(
            AGENTS_ROOT / agent / "SKILL.md", AGENT_SKILL_TOKENS, f"skill {agent}"
        )
        check(f"skill {agent} tem os tokens normativos", not errors, " | ".join(errors))

    errors = protocol_errors()
    check("protocolo fecha cada seção e declara riscos residuais", not errors, " | ".join(errors))
    errors = placar_errors()
    check("placar declara execução e o que não foi provado", not errors, " | ".join(errors))
    errors = audit_errors()
    check("auditoria adversarial está executada e contada", not errors, " | ".join(errors))

    errors = link_errors()
    check("links internos resolvem", not errors, " | ".join(errors))
    errors = adr_errors()
    check("ADR-013 é globalmente livre", not errors, " | ".join(errors))
    errors = eval_errors()
    check("evals têm 16 casos, origem e assertions", not errors, " | ".join(errors))
    errors = legacy_errors()
    check("legado permanece 22/22 e 101.022 bytes", not errors, " | ".join(errors))

    property_names: set[str] = set()
    collect_property_names(LOCAL_SCHEMA, property_names)
    forbidden_found = sorted(property_names & FORBIDDEN_PROPERTIES)
    check(
        "schema não materializa nota, rubrica, ranking ou veredito",
        not forbidden_found,
        ", ".join(forbidden_found),
    )
    check(
        "schema tem $id como URI absoluta",
        str(LOCAL_SCHEMA.get("$id", "")).startswith("https://"),
        str(LOCAL_SCHEMA.get("$id")),
    )

    base = build_bundle(with_improvement=True)
    context = base["context"]
    source_plan = base["plan"]
    report = base["report"]

    # Fixtures positivas.
    positive: list[tuple[str, dict[str, Any]]] = [
        ("plano válido", source_plan),
        *[
            (f"assignment {task['capability']} válido", task)
            for task in base["tasks"]
        ],
        *[
            (f"retorno {value['capability']} válido", value)
            for value in base["returns"]
        ],
        (
            "retorno Tecnologia válido",
            build_bundle(subject="TECHNOLOGY")["returns"][1],
        ),
        ("retorno Spike válido", build_bundle(subject="SPIKE")["returns"][1]),
        ("rejeição de bypass válida", route_rejection(context)),
        ("capability gap comprovado válido", capability_gap(context)),
    ]
    for label, value in positive:
        expect_valid(label, value)

    expect_valid("relatório consolidado válido", report)

    mission_errors = validate_schema(
        base["mission"],
        DIRECTOR_SCHEMA["$defs"]["departmentMission"],
        DIRECTOR_SCHEMA,
    )
    check(
        "missão do Diretor para Inovação é aceita pelo schema real",
        not mission_errors,
        " | ".join(mission_errors),
    )

    errors = chain_errors(base)
    check(
        "cadeia missão→plano→assignment→retorno→relatório reconcilia",
        not errors,
        " | ".join(errors),
    )
    errors = bridge_errors(report, base["boundary"], DIRECTOR_SCHEMA)
    check(
        "ponte relatório → DEPARTMENT_RETURN é íntegra e aceita",
        not errors,
        " | ".join(errors),
    )
    consulta = build_bundle(mode="CONSULTA")
    errors = chain_errors(consulta) + bridge_errors(
        consulta["report"], consulta["boundary"], DIRECTOR_SCHEMA
    )
    check("rodada em CONSULTA reconcilia com ambiente de leitura", not errors, " | ".join(errors))

    # ------------------------------------------------------------------
    # Fixtures negativas de artefato
    # ------------------------------------------------------------------
    negative: list[tuple[str, dict[str, Any]]] = []

    bad = copy.deepcopy(source_plan)
    bad["agent_roster"][2] = copy.deepcopy(bad["agent_roster"][0])
    negative.append(("rejeita roster duplicado", bad))

    bad = copy.deepcopy(source_plan)
    for item in bad["agent_roster"]:
        item["selected"] = False
    negative.append(("rejeita roster sem nenhum agente selecionado", bad))

    bad = copy.deepcopy(base["tasks"][0])
    bad["capability"] = "EXPERIMENT_DESIGN"
    negative.append(("rejeita capability atribuída ao agente errado", bad))

    bad = copy.deepcopy(base["tasks"][0])
    bad["permissions"]["allowed_tools"] = ["deploy-to-production"]
    negative.append(("rejeita permissão de deploy no assignment", bad))

    bad = copy.deepcopy(base["tasks"][0])
    bad["permissions"]["allowed_tools"] = ["write-repository"]
    negative.append(("rejeita permissão de escrita no assignment", bad))

    bad = copy.deepcopy(base["tasks"][0])
    bad["permissions"]["production_access"] = True
    negative.append(("rejeita acesso a produção no assignment", bad))

    bad = copy.deepcopy(base["tasks"][0])
    bad["mode"] = "CONSULTA"
    bad["permissions"]["environment"] = "ISOLATED_SANDBOX"
    negative.append(("rejeita CONSULTA com ambiente além de leitura", bad))

    bad = copy.deepcopy(base["returns"][0])
    bad["producer_agent"] = "agente-experimentos-e-spikes"
    negative.append(("rejeita produtor de retorno forjado", bad))

    bad = copy.deepcopy(base["returns"][0])
    bad["causal"]["producer"] = DEPARTMENT
    negative.append(("rejeita gerente como produtora do trabalho do agente", bad))

    bad = copy.deepcopy(base["returns"][0])
    del bad["payload"]["saturation"]
    negative.append(("rejeita payload de descoberta sem ledger", bad))

    bad = copy.deepcopy(base["returns"][0])
    bad["payload"]["ganho_estimado"] = "30%"
    negative.append(("rejeita payload aberto com campo inventado", bad))

    bad = copy.deepcopy(base["returns"][0])
    bad["payload"]["saturation"]["rounds"] = bad["payload"]["saturation"]["rounds"][-1:]
    bad["payload"]["saturation"]["declared"] = True
    negative.append(("rejeita saturação com uma única rodada", bad))

    bad = copy.deepcopy(base["returns"][0])
    bad["payload"]["saturation"]["rounds"][-1]["candidate_count"] = 0
    bad["payload"]["saturation"]["rounds"][-1]["net_new_count"] = 1
    negative.append(("rejeita líquidos novos acima dos candidatos", bad))

    bad = copy.deepcopy(base["returns"][0])
    bad["payload"]["saturation"]["rounds"][-1]["search_scope"] = "Busca superficial diferente."
    negative.append(("rejeita saturação com escopos incomparáveis", bad))

    bad = copy.deepcopy(base["returns"][0])
    bad["payload"]["saturation"]["rounds"].append(
        copy.deepcopy(bad["payload"]["saturation"]["rounds"][-1])
    )
    negative.append(("rejeita rodada de saturação duplicada", bad))

    bad = copy.deepcopy(base["returns"][0])
    bad["payload"]["saturation"]["rounds"][0]["net_new_count"] = 3
    bad["payload"]["saturation"]["rounds"][0]["candidate_count"] = 5
    negative.append(("rejeita contagem líquida sem oportunidade correspondente", bad))

    bad = copy.deepcopy(base["returns"][0])
    bad["payload"]["saturation"]["rounds"][1]["opportunity_refs"] = ["opportunity-001"]
    bad["payload"]["saturation"]["rounds"][1]["net_new_count"] = 1
    negative.append(("rejeita a mesma oportunidade contada duas vezes", bad))

    bad = copy.deepcopy(base["returns"][0])
    opp = bad["payload"]["opportunities"][0]
    opp["classification"] = "DUPLICATE"
    opp["base_opportunity_ref"] = "n/a"
    negative.append(("rejeita duplicata sem item-base", bad))

    bad = copy.deepcopy(base["returns"][0])
    bad["payload"]["opportunities"][0]["baseline"]["status"] = "MEASURED"
    bad["payload"]["opportunities"][0]["evidence_refs"] = []
    negative.append(("rejeita baseline medida sem evidência", bad))

    tech_bundle = build_bundle(subject="TECHNOLOGY")
    bad = copy.deepcopy(tech_bundle["returns"][1])
    bad["payload"]["experiments"][0]["technology_evaluation"]["source_refs"] = []
    negative.append(("rejeita tecnologia sem fontes", bad))

    bad = copy.deepcopy(tech_bundle["returns"][1])
    bad["payload"]["experiments"][0]["technology_evaluation"]["disposition"] = "ADOPT"
    negative.append(("rejeita ADOPT sem reconciliação externa", bad))

    bad = copy.deepcopy(tech_bundle["returns"][1])
    bad["payload"]["experiments"][0]["technology_evaluation"]["disposition"] = "ADOPT"
    bad["payload"]["evidence_reconciliation"] = {
        "performed": True,
        "external_producer_ref": "departamento-qa-usabilidade",
        "external_evidence": [],
        "conclusion": "HYPOTHESIS_SUPPORTED",
        "limitations": [],
    }
    negative.append(("rejeita ADOPT com reconciliação sem evidência", bad))

    bad = copy.deepcopy(base["returns"][1])
    bad["payload"]["experiments"][0]["technology_evaluation"]["applicable"] = True
    negative.append(("rejeita bloco tecnológico contraditório", bad))

    bad = copy.deepcopy(base["returns"][1])
    bad["payload"]["experiments"][0]["alternatives"][1] = copy.deepcopy(
        bad["payload"]["experiments"][0]["alternatives"][0]
    )
    negative.append(("rejeita duas alternativas idênticas", bad))

    spike_bundle = build_bundle(subject="SPIKE")
    bad = copy.deepcopy(spike_bundle["returns"][1])
    bad["payload"]["experiments"][0]["spike_questions"] = ["Só uma pergunta?"]
    negative.append(("rejeita spike com menos de duas perguntas", bad))

    bad = copy.deepcopy(base["returns"][1])
    bad["payload"]["experiments"][0]["spike_questions"] = ["Pergunta indevida."]
    negative.append(("rejeita perguntas de spike em experimento geral", bad))

    bad = copy.deepcopy(base["returns"][1])
    bad["payload"]["evidence_reconciliation"]["performed"] = True
    negative.append(("rejeita reconciliação alegada sem produtor nem evidência", bad))

    bad = copy.deepcopy(base["returns"][1])
    bad["execution_requests"][0]["route"] = [DEPARTMENT, "ceo-maestro"]
    negative.append(("rejeita bypass do Diretor em dependência", bad))

    bad = copy.deepcopy(base["returns"][1])
    bad["execution_requests"][0]["recommended_recipient"] = "departamento-negocios"
    bad["execution_requests"][0]["need"] = "BUSINESS"
    negative.append(("rejeita pedido a Negócios sem autorização matricial", bad))

    bad = copy.deepcopy(base["returns"][1])
    bad["execution_requests"][0]["evidence_refs"] = []
    negative.append(("rejeita pedido de execução sem evidência", bad))

    bad = copy.deepcopy(base["returns"][2])
    pdca = bad["payload"]["reports"][0]["pdca"]
    pdca["act"] = "STANDARDIZE"
    pdca["do_external_evidence"] = []
    negative.append(("rejeita padronização sem evidência do Do", bad))

    bad = copy.deepcopy(base["returns"][2])
    pdca = bad["payload"]["reports"][0]["pdca"]
    pdca["act"] = "ADJUST"
    pdca["do_external_evidence"] = []
    negative.append(("rejeita ajuste com Check sem evidência do Do", bad))

    bad = copy.deepcopy(base["returns"][2])
    bad["payload"]["reports"][0]["pdca"]["do_external_evidence"] = [
        {
            "evidence_ref": "auto-relato-001",
            "producer_ref": DEPARTMENT,
            "producer_digest": EVIDENCE_DIGEST,
            "authorized_by": "diretor-de-lentes",
            "observed_at": NOW,
        }
    ]
    negative.append(("rejeita Do produzido pelo próprio Departamento", bad))

    bad = copy.deepcopy(base["returns"][2])
    bad["payload"]["reports"][0]["pdca"]["do_external_evidence"] = [
        {
            "evidence_ref": "qa-report-001",
            "producer_ref": "departamento-qa-usabilidade",
            "producer_digest": EVIDENCE_DIGEST,
            "authorized_by": "departamento-inovacao-melhoria",
            "observed_at": NOW,
        }
    ]
    negative.append(("rejeita Do autoautorizado", bad))

    bad = copy.deepcopy(base["returns"][2])
    bad["payload"]["reports"][0]["intake_basis"] = "OPERATIONAL_EVIDENCE"
    negative.append(("rejeita intake operacional sem evidência autenticada", bad))

    bad = copy.deepcopy(base["returns"][2])
    bad["payload"]["reports"][0]["kaizen_action"]["reversible"] = False
    negative.append(("rejeita ação Kaizen irreversível", bad))

    bad = copy.deepcopy(report)
    bad["portfolio"][0]["gate_checks"]["baseline"] = False
    negative.append(("rejeita READY_FOR_EXPERIMENT sem baseline", bad))

    bad = copy.deepcopy(report)
    bad["portfolio"][0]["state"] = "EVIDENCE_PENDING"
    negative.append(("rejeita EVIDENCE_PENDING com gate completo", bad))

    bad = copy.deepcopy(report)
    bad["portfolio"][0]["blocking_pending_refs"] = ["pending-execution-001"]
    negative.append(("rejeita estado avançado com pendência bloqueante", bad))

    bad = copy.deepcopy(report)
    bad["portfolio"][0]["state"] = "BLOCKED"
    negative.append(("rejeita BLOCKED sem faixa nem pendência de bloqueio", bad))

    bad = copy.deepcopy(report)
    bad["portfolio"][0]["priority_band"] = "NOW"
    bad["portfolio"][0]["gate_checks"]["rollback"] = False
    negative.append(("rejeita faixa NOW com gate incompleto", bad))

    bad = copy.deepcopy(report)
    bad["test_summary"]["pass"] = 1
    negative.append(("rejeita apropriação de PASS de QA", bad))

    bad = copy.deepcopy(report)
    bad["test_summary"]["pass"] = False
    negative.append(("rejeita False no lugar de zero em test_summary", bad))

    bad = copy.deepcopy(report)
    bad["technical_recommendation"] = "Alternativa vencedora aprovada com nota 9,8."
    negative.append(("rejeita nota e vencedora em texto livre", bad))

    bad = copy.deepcopy(report)
    bad["portfolio"][0]["next_event"] = "Emitir o veredito final da iniciativa."
    negative.append(("rejeita veredito em texto livre", bad))

    bad = copy.deepcopy(report)
    bad["portfolio"][0]["priority_basis"] = "Bateria de QA fechou 12 PASS e 0 FAIL."
    negative.append(("rejeita alegação de QA em texto livre", bad))

    bad = copy.deepcopy(report)
    bad["skill_evolution_recommendations"] = [
        {
            "recommendation_id": "evolution-001",
            "skill_ref": "some-skill",
            "observed_gap": "A skill não dispara no caso medido.",
            "evidence_refs": ["opportunity-brief-001"],
            "route": [DEPARTMENT, "diretor-de-lentes", "diretor-de-lentes"],
            "status": "RECOMMENDED_TO_CEO_NOT_SENT",
        }
    ]
    negative.append(("rejeita rota de evolução que não termina no CEO", bad))

    bad = copy.deepcopy(report)
    bad["skill_evolution_recommendations"] = [
        {
            "recommendation_id": "evolution-001",
            "skill_ref": "some-skill",
            "observed_gap": "A skill não dispara no caso medido.",
            "evidence_refs": [],
            "route": [DEPARTMENT, "diretor-de-lentes", "ceo-maestro"],
            "status": "RECOMMENDED_TO_CEO_NOT_SENT",
        }
    ]
    negative.append(("rejeita recomendação de evolução sem evidência", bad))

    bad = copy.deepcopy(report)
    bad["execution_requests"].append(
        {
            "request_id": "request-evolution-001",
            "need": "IMPLEMENTATION",
            "recommended_recipient": "departamento-evolucao-skills",
            "route": [DEPARTMENT, "diretor-de-lentes"],
            "reason": "Alterar a skill diretamente.",
            "evidence_refs": ["opportunity-brief-001"],
            "status": "RECOMMENDED_NOT_SENT",
        }
    )
    negative.append(("rejeita Evolução de Skills como destino de pedido", bad))

    bad = copy.deepcopy(report)
    bad["accepted_return_refs"] = ["agent-return-discovery-001"]
    negative.append(("rejeita retorno aceito sem digest autenticado", bad))

    bad = copy.deepcopy(report)
    bad["score"] = 9.8
    negative.append(("rejeita campo score", bad))

    bad = route_rejection(context)
    bad["returned_to"] = "ceo-maestro"
    negative.append(("rejeita retorno lateral da rejeição", bad))

    bad = capability_gap(context)
    bad["search_sources"] = []
    negative.append(("rejeita capability gap sem busca real", bad))

    bad = capability_gap(context)
    bad["expected_agent"] = "agente-melhoria-continua"
    negative.append(("rejeita capability gap com agente incoerente", bad))

    check(
        "fixtures negativas >= positivas",
        len(negative) >= len(positive),
        f"{len(negative)} negativas, {len(positive)} positivas",
    )
    for label, value in negative:
        expect_invalid(label, value)

    # ------------------------------------------------------------------
    # Contraprovas de cadeia: o artefato é válido sozinho e mente no conjunto
    # ------------------------------------------------------------------
    chain_negative: list[tuple[str, dict[str, Any]]] = []

    bundle = build_bundle(with_improvement=True)
    bundle["report"]["accepted_assignment_refs"] = [
        authenticated("assignment-fantasma-001", {"forjado": True})
    ]
    chain_negative.append(("cadeia rejeita assignment inventado", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["report"]["accepted_return_refs"][0] = authenticated(
        "agent-return-discovery-001", {"forjado": True}
    )
    chain_negative.append(("cadeia rejeita digest de retorno forjado", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["report"]["portfolio"][0]["opportunity_ref"] = "opportunity-999"
    chain_negative.append(("cadeia rejeita oportunidade que nenhum agente produziu", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["report"]["artifact_refs"].append("analise-da-gerente-001")
    bundle["report"]["portfolio"][0]["artifact_refs"].append("analise-da-gerente-001")
    chain_negative.append(("cadeia rejeita análise fabricada pela gerente", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["report"]["evidence_refs"] = ["evidence-inventada-001"]
    chain_negative.append(("cadeia rejeita evidência que ninguém produziu", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["report"]["claims_unverified"] = []
    chain_negative.append(("cadeia rejeita alegação não verificada silenciada", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["report"]["pending"] = []
    chain_negative.append(("cadeia rejeita pendência silenciada", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["report"]["portfolio"][0]["gate_checks"] = {
        key: True for key in bundle["report"]["portfolio"][0]["gate_checks"]
    }
    bundle["returns"][0]["payload"]["opportunities"][0]["baseline"] = {
        "status": "MEASUREMENT_REQUIRED",
        "metric": "Retrabalhos por publicação",
        "value": "desconhecido",
        "method": "Medição ainda não executada.",
        "source_ref": "n/a",
        "recorded_at": NOW,
        "limitations": ["Sem janela observada."],
    }
    chain_negative.append(("cadeia rejeita gate declarado sem baseline real", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["returns"][1]["payload"]["experiments"][0]["opportunity_ref"] = "opportunity-002"
    chain_negative.append(("cadeia rejeita gate sem experimento da oportunidade", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["plan"]["mode"] = "CONSULTA"
    chain_negative.append(("cadeia rejeita plano em modo diferente da missão", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["tasks"][0]["plan_digest"] = DIGEST
    chain_negative.append(("cadeia rejeita assignment com digest de plano forjado", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["plan"]["agent_roster"][0]["selected"] = False
    chain_negative.append(("cadeia rejeita assignment a agente não selecionado", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["returns"][0]["department_mission_digest"] = DIGEST
    chain_negative.append(("cadeia rejeita retorno com missão não autenticada", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["returns"][0]["target_ref"] = "artifact-outro-produto"
    chain_negative.append(("cadeia rejeita retorno com alvo fora da missão", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["returns"][0]["mode"] = "CONSULTA"
    chain_negative.append(("cadeia rejeita retorno que não preserva o mode", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["returns"][0]["causal"]["round"] = 2
    chain_negative.append(("cadeia rejeita retorno de outra rodada", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["returns"][0]["causal"]["causation_message_ids"] = ["message-unrelated-001"]
    chain_negative.append(("cadeia rejeita causa direta divergente", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["returns"][1]["pending"][0]["blocking"] = True
    chain_negative.append(("cadeia rejeita bloqueio que não afeta iniciativa nenhuma", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["report"]["portfolio"][0]["gate_source_refs"] = ["prova-inexistente-001"]
    chain_negative.append(("cadeia rejeita prova de gate não entregue", bundle))

    bundle = build_bundle(with_improvement=True)
    bundle["report"]["execution_requests"][0]["evidence_refs"] = ["dossie-inexistente-001"]
    chain_negative.append(("cadeia rejeita pedido com evidência inexistente", bundle))

    for label, value in chain_negative:
        expect_chain_invalid(label, value)

    # ------------------------------------------------------------------
    # Contraprovas de ponte
    # ------------------------------------------------------------------
    bad_boundary = to_department_return(report)
    bad_boundary["returned_by"] = "departamento-desenvolvimento"
    check(
        "ponte rejeita returned_by forjado",
        bool(bridge_errors(report, bad_boundary, DIRECTOR_SCHEMA)),
    )

    bad_boundary = to_department_return(report)
    bad_boundary["test_summary"]["skip"] = 1
    bad_boundary["test_summary"]["skip_reasons"] = ["Alegação indevida."]
    check(
        "ponte rejeita resumo divergente da fonte",
        bool(bridge_errors(report, bad_boundary, DIRECTOR_SCHEMA)),
    )

    bad_boundary = to_department_return(report)
    bad_boundary["causal"]["causation_message_ids"] = ["message-unrelated-001"]
    check(
        "ponte rejeita causalidade divergente",
        bool(bridge_errors(report, bad_boundary, DIRECTOR_SCHEMA)),
    )

    bad_boundary = to_department_return(report)
    bad_boundary["artifact_refs"] = [
        authenticated(report["report_id"], report),
        "innovation-plan-999",
    ]
    check(
        "ponte rejeita plano divergente no envelope",
        bool(bridge_errors(report, bad_boundary, DIRECTOR_SCHEMA)),
    )

    bad_boundary = to_department_return(report)
    bad_boundary["scope_touched"] = ["Produção liberada com nota 9,6."]
    check(
        "ponte rejeita julgamento em texto livre do envelope",
        bool(bridge_errors(report, bad_boundary, DIRECTOR_SCHEMA)),
    )

    print(f"\nRESULTADO: {PASS}/{PASS + FAIL} PASS; {FAIL} FAIL")
    print(
        f"FIXTURES: {len(positive)} positivas + relatório; "
        f"{len(negative)} negativas de artefato; "
        f"{len(chain_negative)} contraprovas de cadeia; 5 negativas de ponte"
    )
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
