# -*- coding: utf-8 -*-
"""Validador determinístico do `especialista-planejador` — variante Estrutura.

**Este validador é mínimo de propósito, e o mínimo tem dois deveres.**

1. **O gate estrutural.** `_compartilhado/verificacoes_estrutura.py` traz
   `COBERTURA_EXCECOES = ()` — tupla vazia. Todo pacote com `SKILL.md` fora de
   `agentes/` é pacote de topo para `validate_cobertura_de_validadores`, e um
   pacote de topo **sem** `evals/validate_workflow.py` que importe o módulo de
   estrutura e chame as funções obrigatórias **com efeito** reprova os vizinhos,
   não a si mesmo. Este arquivo existe primeiro por isso: para que a chegada
   deste pacote não derrube ninguém.
2. **A conferência estrutural do próprio pacote:** arquivos obrigatórios,
   frontmatter, interface de runtime, as doze seções canônicas do contrato,
   links internos que resolvem, e a fronteira que define este pacote — ele **não
   é nó de cadeia**.

**O que este validador deliberadamente NÃO faz.** Não recomputa digest, não
carrega manifesto, não declara classe de promessa e não tem portão de saída
próprio. Esse aparato foi removido por medição, e reintroduzi-lo aqui seria
trazê-lo de volta pela porta dos fundos. A paridade da região de doutrina com o
Catálogo é conferida pela receita publicada na própria `SKILL.md`, por quem
edita — não por hash congelado neste arquivo, que envelheceria em silêncio.

Receita: `python evals/validate_workflow.py`, a partir da **raiz do pacote**,
com `PYTHONIOENCODING=utf-8`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
STRUCTURE_ROOT = PACKAGE_ROOT.parent

SKILL_PATH = PACKAGE_ROOT / "SKILL.md"
CONTRACT_PATH = PACKAGE_ROOT / "CONTRATO-DE-COMPROMISSO.md"
OPENAI_PATH = PACKAGE_ROOT / "agents" / "openai.yaml"
REFERENCE_PATH = PACKAGE_ROOT / "referencia" / "origem-e-fundamentacao.md"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"

SKILL_NAME = "especialista-planejador"
DISPLAY_NAME = "Especialista Planejador"
RULES_LINK = "../regras-de-ouro/REGRAS-DE-OURO.md"

# O marcador é um comentário HTML de bloco, e é assim que ele é contado: no
# começo da linha. A alternativa — contar a substring solta — confundiria a
# marca com a menção a ela dentro do trecho de código que ensina a conferir a
# paridade, e o validador reprovaria a própria documentação da fronteira.
MARCA_INICIO = re.compile(r"^<!-- DOUTRINA:INICIO", re.M)
MARCA_FIM = re.compile(r"^<!-- DOUTRINA:FIM", re.M)

# Nós da cadeia executiva. Este pacote não é nenhum deles e não fala com nenhum
# deles: o canal é Jeremias, e é único. As pastas abaixo são a assinatura de um
# nó de cadeia — quem tem `agentes/` orquestra alguém, quem tem `schemas/`
# publica envelope. Este pacote não pode ganhar nenhuma das duas por descuido.
PASTAS_DE_NO_DE_CADEIA = ("agentes", "schemas", "references")

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        SECOES_CONTRATO_GERENTE,
        validate_contract_sections,
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
except ModuleNotFoundError as exc:  # pragma: no cover
    print(f"[FAIL] motor compartilhado ausente em {STRUCTURE_ROOT}: {exc}")
    raise SystemExit(1)
except ImportError as exc:  # pragma: no cover
    # `ModuleNotFoundError` é subclasse de `ImportError`: sem este segundo braço,
    # rodar com um `_compartilhado` que não expõe o que importamos mataria o
    # processo por traceback, sem sumário e sem dizer o que faltou.
    print(
        "[FAIL] OVERLAY_APLICADO_PELA_METADE: _compartilhado existe mas não "
        f"expõe o que este validador importa ({exc})."
    )
    raise SystemExit(1)


def validate_estrutura_do_pacote() -> list[str]:
    """Arquivos obrigatórios presentes, e nenhuma pasta de nó de cadeia."""
    erros = validate_required_files(
        [SKILL_PATH, CONTRACT_PATH, OPENAI_PATH, REFERENCE_PATH, RULES_PATH],
        "arquivo obrigatório",
    )
    for pasta in PASTAS_DE_NO_DE_CADEIA:
        if (PACKAGE_ROOT / pasta).is_dir():
            erros.append(
                f"fronteira: {pasta}/ existe neste pacote — ele não é nó da "
                "cadeia executiva, não orquestra ninguém e não publica envelope"
            )
    return erros


def validate_fronteira_declarada() -> list[str]:
    """A SKILL.md e o contrato declaram a posição fora da cadeia, e a fonte normativa.

    O texto exigido não é decorativo: é o que separa esta variante da do
    Catálogo. Se alguém apagar a declaração, o pacote deixa de dizer a quem
    responde — e o desenho inteiro (não tocar no `ceo-maestro`) perde o apoio.
    """
    erros: list[str] = []
    skill = SKILL_PATH.read_text(encoding="utf-8")
    contrato = CONTRACT_PATH.read_text(encoding="utf-8")

    for rotulo, texto in (("SKILL.md", skill), ("contrato", contrato)):
        if RULES_LINK not in texto:
            erros.append(f"{rotulo}: não cita a fonte normativa em {RULES_LINK}")
        if "EXECUTIVE_MISSION" not in texto:
            erros.append(
                f"{rotulo}: não diz nada sobre EXECUTIVE_MISSION — a recusa do "
                "envelope da cadeia é o que fixa a posição deste pacote"
            )
        if "Jeremias" not in texto:
            erros.append(f"{rotulo}: não nomeia Jeremias como canal único")

    if "fora da cadeia" not in skill.casefold():
        erros.append("SKILL.md: não declara a posição fora da cadeia de comando")
    if "Consultor direto de Jeremias" not in contrato:
        erros.append("contrato: a seção Papel não declara o consultor direto")
    if "return_to" not in contrato:
        erros.append(
            "contrato: não declara a ausência de return_to para o ceo-maestro"
        )
    return erros


def validate_regiao_de_doutrina() -> list[str]:
    """A região de fonte única está delimitada, uma vez só e na ordem certa.

    Aqui a conferência para na **forma**: os marcadores existem, são únicos e
    INICIO vem antes de FIM. A **identidade** de bytes com o Catálogo é conferida
    pela receita publicada na `SKILL.md`, por quem edita, e não por um digest
    congelado neste arquivo — número congelado em validador envelhece calado.
    """
    texto = SKILL_PATH.read_text(encoding="utf-8")
    erros: list[str] = []
    achados = {}
    for rotulo, marca in (("INICIO", MARCA_INICIO), ("FIM", MARCA_FIM)):
        posicoes = [m.start() for m in marca.finditer(texto)]
        achados[rotulo] = posicoes
        if len(posicoes) != 1:
            erros.append(
                f"doutrina: marcador DOUTRINA:{rotulo} abre "
                f"{len(posicoes)} linhas; a região é uma só"
            )
    if erros:
        return erros
    if achados["INICIO"][0] > achados["FIM"][0]:
        erros.append("doutrina: DOUTRINA:FIM aparece antes de DOUTRINA:INICIO")
    return erros


def run() -> int:
    casos: list[tuple[str, list[str]]] = []

    casos.append(("pacote completo e sem pasta de nó de cadeia", validate_estrutura_do_pacote()))
    casos.append(
        ("frontmatter canônico e dentro dos limites", validate_frontmatter(SKILL_PATH, SKILL_NAME))
    )
    casos.append(
        (
            "interface de runtime declara nome, resumo e token",
            validate_openai_yaml(OPENAI_PATH, DISPLAY_NAME, f"${SKILL_NAME}"),
        )
    )
    casos.append(
        (
            "contrato tem as doze seções canônicas, na ordem, e as contáveis contam",
            validate_contract_sections(
                CONTRACT_PATH, SECOES_CONTRATO_GERENTE, f"contrato {SKILL_NAME}"
            ),
        )
    )
    casos.append(("links internos do pacote resolvem", validate_links(PACKAGE_ROOT)))
    casos.append(("posição fora da cadeia declarada nos dois documentos", validate_fronteira_declarada()))
    casos.append(("região de doutrina delimitada uma única vez", validate_regiao_de_doutrina()))

    # --- as travas de ESTRUTURA INTEIRA -------------------------------------
    # Replicação é o mecanismo, não desperdício (ADR-015): cada validador varre
    # a árvore toda, e basta um rodar para a colisão do vizinho aparecer.
    casos.append(
        ("série global de ADR é única em toda a estrutura", validate_adr_series(STRUCTURE_ROOT))
    )
    casos.append(
        (
            "todo pacote gerente tem contrato canônico",
            validate_contratos_de_gerente(STRUCTURE_ROOT),
        )
    )
    casos.append(
        (
            "todo pacote gerente tem validador que roda a trava global",
            validate_cobertura_de_validadores(STRUCTURE_ROOT),
        )
    )
    casos.append(
        (
            "a recusa de digest() dispara e ninguém tem cópia privada do motor",
            validate_trava_de_digest(STRUCTURE_ROOT),
        )
    )
    casos.append(
        (
            "nenhuma asserção é verdadeira por construção sobre valor produzido",
            validate_sem_check_tautologico(STRUCTURE_ROOT),
        )
    )
    casos.append(
        (
            "nenhum placar de pacote declara total de cadeia como estado corrente",
            validate_placar_nao_declara_cadeia(STRUCTURE_ROOT),
        )
    )
    casos.append(
        (
            "a contagem publicada aponta para o digest do instrumento vigente",
            validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT),
        )
    )
    casos.append(
        (
            "as travas do modulo compartilhado nao estao neutralizadas",
            validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT),
        )
    )
    casos.append(
        (
            "toda pendencia declarada nomeia quem responde por ela",
            validate_pendencia_tem_dono(STRUCTURE_ROOT),
        )
    )
    casos.append(
        (
            "a fonte normativa confere com o valor declarado em ORIGEM.md",
            validate_fonte_normativa_conferida(STRUCTURE_ROOT),
        )
    )

    falhas = 0
    for nome, erros in casos:
        print(f"[{'PASS' if not erros else 'FAIL'}] {nome}")
        if erros:
            falhas += 1
            for erro in erros:
                print(f"       {erro}")

    print(f"\nResultado: {len(casos) - falhas}/{len(casos)} casos passaram.")
    return 1 if falhas else 0


if __name__ == "__main__":
    # T55: recusa medir a Estrutura a partir do runtime, onde a raiz
    # resolve para .claude/skills e as skills do Catalogo viram pacotes.
    recusar_execucao_fora_da_fonte(STRUCTURE_ROOT)
    sys.exit(run())
