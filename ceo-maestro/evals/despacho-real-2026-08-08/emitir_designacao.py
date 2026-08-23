#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emite uma `JUDGE_ASSIGNMENT` que o SCHEMA aceita, e só então despacha.

PROVA DE CAPACIDADE — tarefa 65, aberta em 2026-08-08.

**O que esta rodada existe para provar, e o que ela NÃO prova.** Oito tarefas
estão paradas atrás de uma frase: *"não há worker runtime reconciliado que
devolva o parecer pelo protocolo"* (`CAPABILITY_GAP` da R6). A casa tem o
protocolo inteiro — designação, custódia, caminho exclusivo, gate — e nunca
teve a execução. Esta rodada faz **uma** designação nascer válida, ser
despachada de verdade e voltar como parecer conferível.

Ela **não** produz veredito que valha para promoção, e o motivo está na
própria casa: *quem despacha não pode ser parte, e juiz criado pelo desvio não
absolve o desvio*. Em 2026-08-06, seis de seis instâncias relataram vontade de
**endurecer** com quem as despachou — o viés existe e tem direção medida. Por
isso o resultado aqui é **prova de mecanismo**, e o campo `mode` diz
`VERIFICACAO`, não `VALIDACAO`.

**Por que a designação de hoje falharia no schema.** Medido em 2026-08-08: as
oito designações da rodada 2 têm `pacotes`, `contract_id`, `issued_by` e
`required_level` no topo, e o `$defs/judgeAssignment` declara
`additionalProperties: false`. Faltam-lhes `causal`, `contract_excerpt`,
`evidence_index`, `forbidden_context` e `anonymized_candidate`, todos
obrigatórios. É o achado da tarefa 38, aqui virado em código: este emissor
**valida antes de emitir e aborta se o schema recusar**, para que a primeira
designação da casa nasça conforme em vez de ser corrigida depois.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CEO = AQUI.parents[1]
ESTRUTURA = CEO.parent
JUIZES = CEO / "diretor-de-lentes" / "departamento-juizes"
CAMPANHA_ALVO = CEO / "evals" / "contagem-exigida-2026-08-05"
CANDIDATO = CAMPANHA_ALVO / "candidatos" / "cand-contagem-exigida"

sys.path.insert(0, str(ESTRUTURA))
from _compartilhado.validador_schema import validate_schema  # noqa: E402

AGORA = "2026-08-08T12:40:00-03:00"
CUSTODIA_EM = "2026-08-08T12:39:00-03:00"   # estritamente anterior a AGORA
HANDOFF = "HANDOFF-T27-CAPACIDADE-R1"
ASSIGNMENT_ID = "ASSIGN-T27-CAP-R1-ROB-I1"


def custody_digest(alvo: Path) -> tuple[str, int]:
    """A receita publicada na tarefa 42, sem reimplementar de cabeça.

    Arquivo: sha256 do conteúdo normalizado em LF. Diretório: sha256 da
    concatenação de (caminho relativo POSIX + conteúdo) na ordem crescente do
    caminho; `bytes` soma APENAS os conteúdos — o hash inclui os nomes e o
    `bytes` não, e essa diferença é a armadilha que custou 1440 tentativas a um
    juiz.
    """
    if alvo.is_file():
        c = alvo.read_bytes().replace(b"\r\n", b"\n")
        return hashlib.sha256(c).hexdigest(), len(c)
    arquivos = sorted((p for p in alvo.rglob("*") if p.is_file()),
                      key=lambda p: p.relative_to(alvo).as_posix())
    blob, soma = b"", 0
    for p in arquivos:
        c = p.read_bytes().replace(b"\r\n", b"\n")
        blob += p.relative_to(alvo).as_posix().encode("utf-8") + c
        soma += len(c)
    return hashlib.sha256(blob).hexdigest(), soma


def sha_texto(p: Path) -> str:
    d = p.read_bytes()
    if d.startswith(b"\xef\xbb\xbf"):
        d = d[3:]
    return "sha256:" + hashlib.sha256(d.replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    missao = json.loads((CAMPANHA_ALVO / "01-EXECUTIVE-MISSION.json")
                        .read_text(encoding="utf-8"))
    contrato = CAMPANHA_ALVO / "00-CONTRATO.md"

    # --- 1. CUSTÓDIA ANTES DA EMISSÃO (ADR-016, trava 3) -------------------
    sha_cand, bytes_cand = custody_digest(CANDIDATO)
    print("custódia do candidato: %d arquivos, %d bytes, sha %s…"
          % (len([p for p in CANDIDATO.rglob('*') if p.is_file()]),
             bytes_cand, sha_cand[:16]))

    # --- 2. os critérios saem do CONTRATO julgado, não da minha cabeça -----
    criterios = [
        {"criterion_id": "AC-%02d" % i, "criterion_text": t, "role": "owner"}
        for i, t in enumerate(missao["acceptance_criteria"], 1)
    ]

    designacao = {
        "artifact_type": "JUDGE_ASSIGNMENT",
        "assignment_id": ASSIGNMENT_ID,
        "causal": {
            "work_item_id": "TASK-27",
            "front_id": "FRONT-CONTAGEM-EXIGIDA",
            "handoff_id": HANDOFF,
            "message_id": "MSG-T27-CAP-R1",
            "causation_message_ids": ["MSG-T27-MISSAO"],
            "contract_id": "CONTRATO-CONTAGEM-EXIGIDA-20260805",
            "contract_version": 1,
            "contract_digest": sha_texto(contrato),
            "candidate_digest": "sha256:" + sha_cand,
            "round": 1,
            "attempt": 1,
            "producer": "departamento-juizes",
            # string, não inteiro — o schema pediu e o portão recusou a
            # primeira tentativa antes de despachar, que é o que ele existe
            # para fazer.
            "producer_version": "1",
            "producer_digest": sha_texto(JUIZES / "SKILL.md"),
            "producer_digest_recipe": (
                "_compartilhado/validador_schema.py::sha256_texto_normalizado "
                "sobre o SKILL.md do departamento-juizes"),
            "created_at": AGORA,
        },
        "judge_id": "agente-julgar-robustez-e-evidencia",
        "lens": "robustez-e-evidencia",
        "instance": 1,
        "write_path": "julgamento/%s/a1/%s/" % (HANDOFF, ASSIGNMENT_ID),
        "custody_copy": {
            "path": "evals/contagem-exigida-2026-08-05/candidatos/cand-contagem-exigida",
            "sha256": "sha256:" + sha_cand,
            "bytes": bytes_cand,
            "taken_at": CUSTODIA_EM,
            # ERRATA DA RODADA 1, e o defeito foi meu. A primeira emissão OMITIU
            # este campo, e o juiz despachado gastou OITO tentativas de receita
            # antes de concluir — errado — que a custódia não conferia. Ele mediu
            # 676534 bytes crus contra os 675080 normalizados que eu declarei; a
            # diferença de 1454 é exatamente o número de CRLF na árvore.
            #
            # A receita foi canonizada na tarefa 42 justamente para ninguém mais
            # adivinhar, e o campo existe no schema desde então. Publicá-la no
            # `$comment` do schema não bastou: **quem lê o envelope não lê o
            # schema**. É o `aviso-em-prosa-nao-previne-erro` num degrau novo —
            # a receita estava normativa, acessível e ausente de onde importava.
            "digest_recipe": (
                "_compartilhado/manifesto.py::custody_digest sobre conteudo "
                "normalizado em LF; diretorio hasheia a concatenacao de "
                "(caminho relativo POSIX + conteudo) ordenada por caminho, e "
                "bytes soma APENAS os conteudos"),
        },
        # VERIFICACAO, e nao VALIDACAO: esta rodada prova mecanismo. Quem
        # despacha e parte, e a casa proibe que isso vire veredito.
        "mode": "VERIFICACAO",
        "candidate_digest": "sha256:" + sha_cand,
        "anonymized_candidate": (
            "evals/contagem-exigida-2026-08-05/candidatos/cand-contagem-exigida"),
        "criteria": criterios,
        "rubric_ref": "rubrica-corte-v2",
        "contract_excerpt": {
            "intent": missao["objective"],
            "done": missao["acceptance_criteria"],
            "scope_in": missao["scope_in"],
            "scope_out": missao["scope_out"],
            "constraints": missao["constraints"],
            "decisions": missao["decisions_binding"],
            "not_applicable": [
                "rubric_overrides: esta campanha nao altera rubrica nem corte",
            ],
        },
        "evidence_index": [
            "evals/contagem-exigida-2026-08-05/00-CONTRATO.md",
            "evals/contagem-exigida-2026-08-05/01-EXECUTIVE-MISSION.json",
            "evals/contagem-exigida-2026-08-05/saida-crua",
            "evals/contagem-exigida-2026-08-05/candidatos/cand-contagem-exigida/MANIFESTO-DE-LINHAS.txt",
        ],
        "forbidden_context": [
            "autoria e departamento produtor",
            "pareceres dos outros agentes",
            "nota desejada, veredito esperado ou preferência da gerente",
            "rodada anterior e histórico de retrabalho",
        ],
        "return_to": "departamento-juizes",
        "issued_at": AGORA,
    }

    # --- 3. FAIL-CLOSED: o schema decide se isto pode ser despachado -------
    schema = json.loads((JUIZES / "schemas" / "departamento-juizes.schema.json")
                        .read_text(encoding="utf-8"))
    erros = validate_schema(designacao, schema["$defs"]["judgeAssignment"], schema)
    if erros:
        print("\nDESIGNAÇÃO RECUSADA PELO SCHEMA — nada foi despachado:")
        for e in erros:
            print("   " + e)
        return 1

    # custody_copy.taken_at estritamente anterior a issued_at — o schema não
    # ordena timestamps, então a ordem é conferida aqui, em código.
    if not (designacao["custody_copy"]["taken_at"] < designacao["issued_at"]):
        print("\nCUSTÓDIA NÃO É ANTERIOR À EMISSÃO — nada foi despachado.")
        return 1

    destino = AQUI / "01-JUDGE-ASSIGNMENT.json"
    destino.write_text(json.dumps(designacao, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8", newline="\n")
    print("\nDESIGNAÇÃO VÁLIDA pelo $defs/judgeAssignment.")
    print("  %d critérios, write_path %s" % (len(criterios), designacao["write_path"]))
    print("  gravada em %s" % destino.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
