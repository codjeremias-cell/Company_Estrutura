#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coletor de saída crua dos validadores — o instrumento de medição do CEO.

Este arquivo existe porque, em 2026-08-06, o CEO publicou a oito juízes uma
evidência com **quatro defeitos, todos do coletor e nenhum do objeto medido**.
Os juízes acharam os quatro; o CEO não achou nenhum. Cada um vira aqui uma
regra, e cada regra tem o defeito que a originou escrito ao lado.

    1. SUMÁRIO DO VIZINHO. A receita era "sumário = ÚLTIMO da saída", e o
       `departamento-negocios` sub-executa vizinhos e **ecoa** a cauda deles
       (`combined[-500:]`). O 99/100 publicado como dele era do Diretor.
       -> Regra: token próprio, e RECUSA de adivinhar quando ambíguo.

    2. MOJIBAKE. `PYTHONIOENCODING=utf-8` foi setado no ambiente do FILHO, mas
       a chamada era `subprocess.run(..., text=True)` SEM `encoding="utf-8"`:
       o filho emitiu UTF-8 e o pai decodificou em cp1252. Todo acento das
       quatro saídas saiu quebrado.
       -> Regra: `encoding="utf-8"` explícito, e conferência de acento.

    3. INVENTÁRIO CONTRA O CONTRATO. `subordinados_diretos` listou quatro onde
       o contrato diz três, incluindo o `departamento-juizes`, que o
       `SKILL.md:49` proíbe o CEO de chamar.
       -> Regra: o inventário é conferido contra o esperado, e diverge alto.

    4. AUTOCONTRADIÇÃO. O JSON publicou `3 FAIL` ao lado de `99/100`, que
       implica 1 falha. Uma conferência de uma linha teria pego. Não foi feita.
       -> Regra: coerência interna é GATE, não relatório.

RODADA 2 (2026-08-07, tarefas 40 e 41). A rodada 2 do núcleo de comando julgou
o próprio conserto acima e achou nele **cinco defeitos, todos confirmados por
execução antes de qualquer linha ser mudada**:

    5. GATE QUE NÃO FECHA NO CASO MAIS PROVÁVEL. `coerencia()` devolvia `[]`
       quando o sumário era `SEM_SUMARIO` ou `AMBIGUO` — exatamente os dois
       estados que o defeito 1 produz. Medido: saída com três `[FAIL]` e
       sumário `AMBIGUO` devolvia zero problema, e a evidência saía publicada
       com `problemas_do_coletor: []`.
       -> Regra: sumário não determinado É o problema, não a ausência dele.

    6. EXIT GRAVADO E NUNCA LIDO. `"exit": proc.returncode` era publicado e
       `returncode` não era comparado em lugar nenhum do arquivo (medido: zero
       ocorrências). Validador que morre saía como medição limpa — o esqueleto
       de `contagem-que-cai-sem-fail`. E o exit não é opinião: o validador faz
       `return 1 if failures else 0`, logo é uma codificação **redundante e
       independente** do sumário.
       -> Regra: `exit == 0` ⟺ `passou == total`. Divergência é contradição.

    7. NÃO-PUBLICAÇÃO PROMETIDA EM PROSA. O `00-RESUMO.json` era escrito na
       linha 197, no diretório de publicação, e o gate só era testado na 211.
       O campo `gate` dizia "este arquivo NÃO é publicado com problemas" —
       enquanto o arquivo já estava lá.
       -> Regra: com gate fechado o `00-RESUMO.json` NÃO EXISTE; sai um
          `00-BLOQUEADO.json` no lugar, nomeando o defeito.

    8. TRAVA REDUNDANTE, MUTAÇÃO CEGA. Os cinco casos da suíte exercitavam um
       fixture em que os DOIS ramos de `coerencia()` disparavam. Medido:
       matando `RE_FAIL_DECL` a função ainda devolvia 1 erro e os cinco casos
       seguiam verdes. Trava sem caso que só ela avermelhe não está provada.
       -> Regra: cada ramo tem fixture em que SÓ ele dispara.

    9. TABELA DE EXPECTATIVA COM UMA CHAVE DE QUINZE. `SUBORDINADOS_ESPERADOS`
       cobria só o `ceo-maestro`, e `inventario()` olhava UM nível
       (`glob("*/SKILL.md")`). Medido: 13 dos 15 pacotes publicavam
       `subordinados_diretos: []` — lista vazia com cara de medida — e o
       `diretor-de-lentes` publicava 1 onde tem 11. Publicar zero como se
       fosse medida é pior que não publicar.
       -> Regra: a expectativa nasce com as QUINZE chaves, cada uma ancorada
          na linha do contrato que a sustenta, e a busca segue as três formas
          reais de subordinação (irmão, `agentes/`, `departamentos-operacionais/`).

   10. FALSO POSITIVO DE MOJIBAKE, achado ao rodar o conserto acima nos quinze
       pela primeira vez. A classe era `[\x80-\xbf -ÿ]`, e o traço entre `\xbf`
       e `ÿ` cria um intervalo de ' ' (0x20) a 'ÿ' (0xFF): 'Ã' seguido de
       QUALQUER imprimível. Maiúscula normal de PT-BR bastava — "NÃO",
       "DECLARAÇÃO", "SUPOSIÇÃO". Medido: fechava o gate sobre `ceo-maestro` e
       `departamento-desenvolvimento`, os dois com saída perfeitamente íntegra.
       É o mesmo esqueleto do `RE_FAIL_DECL` de origem, do outro lado: gate que
       bloqueia evidência boa é tão inútil quanto gate que deixa passar
       evidência ruim, e é pior de achar, porque parece rigor.
       -> Regra: mojibake é 'Ã' antes de Latin-1 alto (U+0080–U+00FF), nunca
          antes de ASCII — e o caso carrega as três palavras que o quebraram.

Uso:
    python evals/coletar_saida_crua.py <destino> [pacote ...]
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]          # ceo-maestro/
ESTRUTURA = ROOT.parent                              # Estrutura Final de Skills/

# Receita publicada = receita executada. Se divergirem, ninguém reproduz.
AMBIENTE = {"PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
RECEITA = (
    'python evals/validate_workflow.py, cwd na raiz do pacote, '
    'env PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1, '
    'subprocess.run(..., encoding="utf-8"). '
    "Sumário próprio: token delimitado; ambiguidade vira AMBIGUO, nunca palpite. "
    "Gate: exit ⟺ sumário, sumário determinado, inventário contra o contrato."
)

# --- defeito 9: a expectativa nasce com as QUINZE chaves ----------------------
#
# A expectativa NÃO é derivada da árvore — isso seria tautologia, o defeito que
# `gate-declarado-vira-gate-derivado` condena: a árvore concordaria consigo
# mesma. Cada entrada é derivada do CONTRATO do pacote e carrega a `ancora`, a
# linha verbatim que a sustenta. Se o contrato mudar, a âncora some e a
# expectativa vira ÓRFÃ — problema alto, não silêncio.
#
# Os contratos declaram em CINCO dialetos (medido em 2026-08-07, nos 15):
#   a) cardinal por extenso + local .... "os seis agentes de `agentes/`"      x10
#   b) enumeração após "Subordinados diretos:" ........................... x2
#   c) enumeração após "Pares executivos diretos:" ....................... x1
#   d) enumeração após "Gerencio apenas:" ................................ x1
#   e) grupo sem cardinal ... "`departamento-juizes` e os Departamentos
#      operacionais" — o único que NÃO fecha um número. Fica declarado como
#      expectativa ABERTA, com o que dá para conferir separado do que não dá.
CONTRATO = "CONTRATO-DE-COMPROMISSO.md"


def _agentes(n: int, cardinal: str) -> dict:
    """Dialeto (a): o contrato dá o cardinal por extenso, não os nomes."""
    return {
        "quantidade": n,
        "fonte": CONTRATO,
        "ancora": f"- **Subordinados diretos:** os {cardinal} agentes de `agentes/`,",
    }


SUBORDINADOS_ESPERADOS: dict[str, dict] = {
    # (c) O CEO tem TRÊS pares executivos. `departamento-juizes` não é um deles,
    #     e `SKILL.md:49` proíbe o CEO de chamá-lo. Ver defeito 3.
    "ceo-maestro": {
        "nomes": {"diretor-de-lentes", "departamento-negocios",
                  "departamento-evolucao-skills"},
        "fonte": CONTRATO,
        "ancora": ("- **Pares executivos diretos:** `diretor-de-lentes`, "
                   "`departamento-negocios` e"),
    },
    # (f) A Diretoria Agentica e o departamento-de-treinamento SAIRAM da arvore
    #     em 2026-09-01, por decisao de Jeremias: sao do projeto Empresa GradUP,
    #     onde a copia viva esta em dados/biblioteca/agente/<nome>/<hash>/.
    #
    #     A decisao de hoje REVERTE a de 2026-08-27, que os havia devolvido ao
    #     master -- e que este mesmo comentario registrava. As expectativas deles
    #     saem junto: expectativa declarada para pacote que nao existe e
    #     declaracao orfa, e este arquivo existe justamente para que arvore e
    #     declaracao nao divirjam em silencio.
    #
    #     Historico completo: criados em 2026-08-19, removidos em 2026-08-20 pela
    #     T90 (as 4 pecas de prova estao no commit dela), devolvidos em 2026-08-27,
    #     julgados na T117 (ambos REPROVED), removidos em 2026-09-01.
    # (e) Único com expectativa ABERTA: o contrato nomeia um subordinado e
    #     remete o resto a um grupo, sem cardinal. Conferível: que os Juízes
    #     estejam lá, e que todo o resto venha do container — não o total.
    "diretor-de-lentes": {
        "contem": {"departamento-juizes"},
        "resto_em": "departamentos-operacionais",
        "fonte": CONTRATO,
        "ancora": ("- **Subordinados diretos:** `departamento-juizes` e os "
                   "Departamentos operacionais."),
        "nota": ("expectativa ABERTA: o contrato não declara cardinal, então o "
                 "total não é conferível contra ele — só a presença dos Juízes "
                 "e a procedência do resto"),
    },
    # (d)
    "departamento-negocios": {
        "nomes": {"agente-estrategia-de-produto", "agente-mercado-e-cliente",
                  "agente-viabilidade-e-monetizacao"},
        "fonte": CONTRATO,
        "ancora": "3. Gerencio apenas:",
    },
    # (b)
    "departamento-inovacao-melhoria": {
        "nomes": {"agente-descoberta-de-oportunidades",
                  "agente-experimentos-e-spikes", "agente-melhoria-continua"},
        "fonte": CONTRATO,
        "ancora": ("- **Subordinados diretos:** "
                   "`agente-descoberta-de-oportunidades`,"),
    },
    "departamento-qa-usabilidade": {
        "nomes": {"agente-testes-funcionais", "agente-testes-nao-funcionais",
                  "agente-usabilidade-e-acessibilidade"},
        "fonte": CONTRATO,
        "ancora": "- **Subordinados diretos:** `agente-testes-funcionais`,",
    },
    # (a) — cardinal por extenso; a âncora carrega a palavra, então trocar
    #       "seis" por "sete" no contrato quebra a âncora e acusa.
    "departamento-arquitetura-dados": _agentes(6, "seis"),
    "departamento-arquitetura-software": _agentes(6, "seis"),
    "departamento-auditoria-responsabilidades": _agentes(3, "três"),
    "departamento-conteudo-marketing": _agentes(8, "oito"),
    "departamento-desenvolvimento": _agentes(8, "oito"),
    "departamento-design-ux-ui": _agentes(7, "sete"),
    "departamento-evolucao-skills": _agentes(4, "quatro"),
    "departamento-juizes": _agentes(3, "três"),
    "departamento-registros": _agentes(4, "quatro"),
    "departamento-seguranca": _agentes(8, "oito"),
    # Consultor direto de Jeremias, FORA da cadeia: nao e par executivo
    # do CEO nem subordinado de ninguem. Entra na tabela porque tem
    # validador proprio (exigencia do gate de cobertura), nao porque a
    # cadeia o comande. Expectativa: ZERO subordinados.
    # RENOMEADO EM 2026-09-02 (era `especialista-planejador`). A chave desta
    # tabela e o NOME DA PASTA, entao renomear o pacote a quebra: o gate de
    # cobertura acusou `expectativa declarada` no ato, e foi assim que o
    # renome apareceu aqui. Nome antigo colidia com uma lente homonima do
    # Catalogo; a decisao de renomear e de Jeremias, em 2026-09-02.
    "planejador-estrutura": {
        "nomes": set(),
        "fonte": CONTRATO,
        "ancora": ("- **Subordinados diretos:** nenhum. "
                   "Não tem `agentes/`, não delega e não convoca."),
    },
}

# As três formas reais de subordinação na árvore (defeito 9). `glob` de um
# nível só enxergava a primeira, e é por isso que 13 pacotes publicavam [].
CONTAINERES_DE_SUBORDINADO = ("agentes", "departamentos-operacionais")

RE_MAIUSCULO = re.compile(r"^RESULTADO:\s*(\d+)\s*/\s*(\d+)\s*PASS", re.M)
RE_MINUSCULO = re.compile(r"^Resultado:\s*(\d+)\s*/\s*(\d+)", re.M)
# Só a DECLARAÇÃO na linha de sumário conta. A primeira versão casava `(\d+)\s*FAIL`
# em qualquer texto e acusou o próprio `ceo-maestro`, porque um caso da tarefa 33 se
# chama "coerência interna é gate: 3 FAIL não convive com 99/100" — o título virou
# declaração. Gate que confunde nome de caso com resultado bloqueia evidência boa.
RE_FAIL_DECL = re.compile(r"^RESULTADO:.*?;\s*(\d+)\s*FAIL", re.M)


def sumario_proprio(saida: str) -> dict:
    """Extrai o sumário DO PACOTE. Recusa adivinhar quando ambíguo.

    O token em caixa alta é exclusivo de quem o usa; o em caixa baixa é o
    dialeto comum, então múltiplas ocorrências significam eco de vizinho — e
    aí a resposta honesta é AMBIGUO, não a última linha.
    """
    alta = RE_MAIUSCULO.findall(saida)
    if len(alta) == 1:
        return {"passou": int(alta[0][0]), "total": int(alta[0][1]),
                "token": "RESULTADO: (exclusivo)"}
    if len(alta) > 1:
        return {"estado": "AMBIGUO",
                "motivo": f"{len(alta)} sumários em caixa alta na mesma saída"}

    baixa = RE_MINUSCULO.findall(saida)
    if len(baixa) == 1:
        return {"passou": int(baixa[0][0]), "total": int(baixa[0][1]),
                "token": "Resultado: (dialeto comum, ocorrência única)"}
    if len(baixa) > 1:
        return {"estado": "AMBIGUO",
                "motivo": (f"{len(baixa)} linhas 'Resultado:' na saída — o pacote "
                           f"ecoa sumário de vizinho e o próprio não é "
                           f"distinguível por token"),
                "candidatos": [f"{p}/{t}" for p, t in baixa]}
    return {"estado": "SEM_SUMARIO"}


def coerencia(saida: str, sum_: dict, exit_code: int | None = None) -> list[str]:
    """GATE, não relatório. Foi a ausência disto que deixou 3 FAIL conviver
    com 99/100 num JSON publicado como evidência.

    Defeito 5: sumário não determinado devolvia `[]` e o gate ficava ABERTO
    justamente no estado que o defeito 1 produz. Agora o estado É o problema.
    """
    erros = []

    if "estado" in sum_:
        erros.append(
            f"sumário não determinado ({sum_['estado']}): o coletor não sabe "
            f"o resultado deste pacote — {sum_.get('motivo', 'nenhuma linha de sumário')}"
        )
        if exit_code not in (None, 0):
            erros.append(
                f"sem sumário determinado e exit={exit_code}: o validador pode "
                f"ter morrido antes de imprimir o resultado"
            )
        return erros

    fails_contados = len([l for l in saida.splitlines() if l.startswith("[FAIL]")])
    esperado = sum_["total"] - sum_["passou"]
    if fails_contados != esperado:
        erros.append(
            f"incoerência interna: sumário diz {sum_['passou']}/{sum_['total']} "
            f"(-> {esperado} falha(s)) mas há {fails_contados} linha(s) [FAIL]"
        )
    declarado = RE_FAIL_DECL.search(saida)
    if declarado and int(declarado.group(1)) != esperado:
        erros.append(
            f"incoerência interna: a saída declara {declarado.group(1)} FAIL "
            f"e o sumário implica {esperado}"
        )
    # Defeito 6: o exit é `return 1 if failures else 0` — codificação redundante
    # e independente do sumário, então divergir dele é contradição, não ruído.
    if exit_code is not None:
        exit_esperado = 1 if esperado else 0
        if exit_code != exit_esperado:
            erros.append(
                f"incoerência interna: sumário {sum_['passou']}/{sum_['total']} "
                f"(-> exit {exit_esperado}) mas o processo saiu com exit={exit_code}"
            )
    return erros


# Defeito 10: a classe era `[\x80-\xbf -ÿ]`, e o traço entre `\xbf` e `ÿ` cria
# um intervalo de ' ' (0x20) a 'ÿ' (0xFF) — ou seja, 'Ã' seguido de QUALQUER
# imprimível. Maiúscula normal de PT-BR virava mojibake: "NÃO", "DECLARAÇÃO" e
# "SUPOSIÇÃO" fechavam o gate. Medido em 2026-08-07: bloqueava `ceo-maestro` e
# `departamento-desenvolvimento`, ambos com saída perfeitamente íntegra. É o
# mesmo esqueleto do `RE_FAIL_DECL` de origem — gate que bloqueia evidência boa
# é tão inútil quanto gate que deixa passar evidência ruim.
#
# Mojibake real de UTF-8 lido como cp1252 põe 'Ã' antes de um caractere do
# Latin-1 suplementar: `único`→`Ãºnico`, `é`→`Ã©`, `ção`→`Ã§Ã£o`. Nunca antes de
# um ASCII.
RE_MOJIBAKE = re.compile(r"Ã[\u0080-\u00ff]")


def acentos_intactos(saida: str) -> bool:
    """Mojibake de UTF-8 lido como cp1252 produz Ã seguido de Latin-1 alto.
    `único` vira `Ãºnico`. Ver defeitos 2 e 10 no cabeçalho."""
    return not RE_MOJIBAKE.search(saida)


def subordinados_diretos(pasta: Path) -> dict[str, str]:
    """As TRÊS formas de subordinação, e de onde cada achado veio.

    Defeito 9: `glob("*/SKILL.md")` via só a primeira forma, então 13 dos 15
    pacotes publicavam lista vazia e o Diretor publicava 1 onde tem 11.
    """
    achados = {p.parent.name: "irmão" for p in pasta.glob("*/SKILL.md")}
    for container in CONTAINERES_DE_SUBORDINADO:
        for p in (pasta / container).glob("*/SKILL.md"):
            achados[p.parent.name] = container
    return dict(sorted(achados.items()))


def conferir_expectativa(nome: str, pasta: Path, diretos: dict[str, str]) -> dict:
    """Confere a árvore contra o CONTRATO, e a âncora contra o contrato.

    Devolve sempre um dicionário com `problemas` (lista) — nunca silêncio.
    """
    exp = SUBORDINADOS_ESPERADOS.get(nome)
    if exp is None:
        return {"estado": "SEM_EXPECTATIVA_DECLARADA",
                "problemas": [f"{nome} não tem expectativa em "
                              f"SUBORDINADOS_ESPERADOS — a tabela nasce com as "
                              f"quinze chaves ou o campo não é publicável"]}

    resultado: dict = {"fonte": f"{exp['fonte']} :: {exp['ancora']}",
                       "problemas": []}
    if exp.get("nota"):
        resultado["nota"] = exp["nota"]

    # (i) A âncora ainda existe no contrato? Expectativa órfã é pior que ausente:
    #     parece conferida e não está mais ligada a nada.
    arq = pasta / exp["fonte"]
    texto = arq.read_text(encoding="utf-8") if arq.is_file() else ""
    if exp["ancora"] not in texto:
        resultado["problemas"].append(
            f"expectativa ÓRFÃ: a âncora {exp['ancora']!r} não existe mais em "
            f"{exp['fonte']} — o contrato mudou e a expectativa não foi refeita"
        )
        resultado["estado"] = "ANCORA_ORFA"
        return resultado

    achados = set(diretos)

    if "nomes" in exp:
        faltando = [n for n in sorted(exp["nomes"]) if n not in texto]
        if faltando:
            resultado["problemas"].append(
                f"expectativa ÓRFÃ: {faltando} não aparecem em {exp['fonte']}"
            )
        sobra, falta = achados - exp["nomes"], exp["nomes"] - achados
        if sobra or falta:
            resultado["problemas"].append(
                f"inventário diverge do contrato: sobra={sorted(sobra)} "
                f"falta={sorted(falta)}"
            )
        resultado["esperado"] = sorted(exp["nomes"])

    elif "quantidade" in exp:
        if len(achados) != exp["quantidade"]:
            resultado["problemas"].append(
                f"inventário diverge do contrato: o contrato declara "
                f"{exp['quantidade']} subordinado(s) e a árvore tem "
                f"{len(achados)} — {sorted(achados)}"
            )
        resultado["esperado"] = f"{exp['quantidade']} (cardinal do contrato)"

    else:  # expectativa aberta (dialeto e)
        falta = exp["contem"] - achados
        if falta:
            resultado["problemas"].append(
                f"inventário diverge do contrato: o contrato nomeia "
                f"{sorted(falta)} e a árvore não tem"
            )
        fora = sorted(n for n, origem in diretos.items()
                      if n not in exp["contem"] and origem != exp["resto_em"])
        if fora:
            resultado["problemas"].append(
                f"inventário diverge do contrato: {fora} não vem de "
                f"{exp['resto_em']}/ nem é nomeado no contrato"
            )
        resultado["esperado"] = (f"contém {sorted(exp['contem'])}; "
                                 f"o resto vem de {exp['resto_em']}/")

    return resultado


def inventario(pasta: Path, nome: str) -> dict:
    diretos = subordinados_diretos(pasta)
    conferencia = conferir_expectativa(nome, pasta, diretos)
    return {
        "subordinados_diretos": sorted(diretos),
        "subordinados_por_origem": diretos,
        "conferencia_contra_o_contrato": conferencia,
        "PLACAR.md": (pasta / "evals" / "PLACAR.md").is_file(),
        "adendos_de_contagem": sorted(
            p.name for p in (pasta / "evals").glob("PLACAR-ADENDO-*.md")
        ),
    }


def _selo_confere_com_execucao(pacote: Path, sum_: dict) -> list[str]:
    """O número PUBLICADO é o que o validador ACABOU de produzir (tarefa 27).

    **O buraco, medido em 2026-08-22 por mutação.** O selo `CONTAGEM-VIGENTE`
    amarra a contagem ao DIGEST do instrumento, o que prova PROCEDÊNCIA — aquele
    número saiu daquela versão do validador. Não prova CORREÇÃO. Trocar `17/17`
    por `999/999` no `PLACAR.md`, mantendo o digest intacto, **passava em
    silêncio**: o validador rodava, produzia 17/17, e ninguém comparava.

    Duas perguntas diferentes, e só a primeira tinha trava: *"quem produziu este
    número?"* e *"este número é o número?"*.

    **Por que aqui, e não dentro de cada validador.** A tarefa 27 foi escrita em
    2026-08-05, quando eram NOVE validadores uniformes. Hoje são dezesseis, em
    QUATRO formas distintas de acumular e imprimir — `cases`/`failures` em treze,
    `PASS`/`FAIL` na Inovação, `results.pass_count` em Negócios, `PASSED`/`total`
    em QA, `casos`/`falhas` no Planejador. Fiar dezesseis arquivos heterogêneos à
    mão é onde âncora erra, e âncora que erra não é cobertura.
    O coletor já roda os dezesseis e já captura o par `passou/total` REAL de cada
    um — comparar aqui é um lugar só, sem recursão, e é exatamente o ponto por onde
    o número é PUBLICADO. Se ele mentir, mente aqui.

    **Limite declarado:** rodar um validador isolado, na mão, não passa por esta
    conferência. O que ela protege é a evidência publicada — e é essa que vira
    parecer.
    """
    if sum_.get("estado"):
        # SEM_SUMARIO / AMBIGUO: já são problema por si, acusados pela coerência.
        # Acusar de novo aqui seria contar o mesmo defeito duas vezes.
        return []
    passou, total = sum_.get("passou"), sum_.get("total")
    if passou is None or total is None:
        return []
    try:
        import sys as _sys
        if str(ESTRUTURA) not in _sys.path:
            _sys.path.insert(0, str(ESTRUTURA))
        from _compartilhado.verificacoes_estrutura import (
            conferir_contagem_declarada,
        )
    except Exception as exc:  # noqa: BLE001
        return [
            "CONTAGEM_NAO_CONFERIDA: o motor compartilhado não pôde ser carregado "
            f"({exc.__class__.__name__}: {exc}), então a contagem publicada NÃO foi "
            "comparada com a execução. Ausência de conferência não é conformidade"
        ]
    return conferir_contagem_declarada(pacote, passou, total)


def coletar(pacotes: dict[str, Path], destino: Path) -> int:
    destino.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, **AMBIENTE)
    resumo, bloqueios = {}, []

    for nome, pasta in pacotes.items():
        proc = subprocess.run(
            [sys.executable, "evals/validate_workflow.py"],
            cwd=str(pasta), capture_output=True, text=True,
            encoding="utf-8", errors="replace",          # defeito 2
            timeout=600, env=env,
        )
        saida = proc.stdout or ""

        # Delimitação explícita: o arquivo diz onde cada saída começa e acaba,
        # para nenhum leitor futuro precisar adivinhar de quem é a última linha.
        (destino / f"{nome}.stdout.txt").write_text(
            f"===== INICIO {nome} =====\n{saida}\n===== FIM {nome} =====\n",
            encoding="utf-8", newline="\n",
        )
        if proc.stderr:
            (destino / f"{nome}.stderr.txt").write_text(
                proc.stderr, encoding="utf-8", newline="\n"
            )

        sum_ = sumario_proprio(saida)
        problemas = coerencia(saida, sum_, proc.returncode)   # defeitos 5 e 6
        if not acentos_intactos(saida):
            problemas.append("mojibake na saída capturada — decodificação errada")
        inv = inventario(pasta, nome)
        problemas.extend(inv["conferencia_contra_o_contrato"]["problemas"])
        problemas.extend(_selo_confere_com_execucao(pasta, sum_))   # tarefa 27

        resumo[nome] = {
            "sumario_proprio": sum_,
            "exit": proc.returncode,
            "fails": [l.strip() for l in saida.splitlines() if l.startswith("[FAIL]")],
            "inventario": inv,
            "problemas_do_coletor": problemas,
        }
        bloqueios.extend(f"{nome}: {p}" for p in problemas)

        st = (sum_.get("estado")
              or f"{sum_.get('passou')}/{sum_.get('total')}")
        print(f"{nome:<26}{st:>14}  fails={len(resumo[nome]['fails'])}"
              f"  {'OK' if not problemas else 'PROBLEMA'}")

    corpo = {
        "receita": RECEITA,
        "coletado_por": "ceo-maestro/evals/coletar_saida_crua.py",
        "pacotes": resumo,
    }

    # Defeito 7: a não-publicação é FATO, não prosa. Com gate fechado o
    # 00-RESUMO.json não chega a existir — quem consome procura por ele.
    resumo_json = destino / "00-RESUMO.json"
    bloqueado_json = destino / "00-BLOQUEADO.json"
    for antigo in (resumo_json, bloqueado_json):
        if antigo.exists():
            antigo.unlink()

    if bloqueios:
        corpo["gate"] = ("FECHADO — o coletor tem defeito. Não existe "
                         "00-RESUMO.json nesta pasta, e esta evidência não "
                         "é publicável.")
        corpo["bloqueios"] = bloqueios
        bloqueado_json.write_text(
            json.dumps(corpo, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )
        print("\nGATE FECHADO — o coletor tem defeito; a evidência NÃO sai:")
        for b in bloqueios:
            print(f"  {b}")
        print(f"\n00-RESUMO.json NÃO foi escrito; ver {bloqueado_json.name}")
        return 1

    corpo["gate"] = ("ABERTO — nenhum problema do coletor. A existência deste "
                     "arquivo é o que atesta o gate aberto.")
    resumo_json.write_text(
        json.dumps(corpo, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(f"\ngravado em {destino}")
    return 0


def _e_pacote_real(validador: Path) -> bool:
    """Pacote da cadeia, ou cópia de campanha? A diferença é ESTRUTURAL.

    **O defeito que isto conserta (tarefa 49, 2026-08-22).** A descoberta anterior
    excluía por LISTA DE NOMES — `candidatos`, `instrumentos`, `lab`, `fontes`, mais
    `backup-` no caminho. Lista de nomes não alcança a pasta que ninguém previu, e
    era exatamente o que estava acontecendo: quatro fixtures entravam como pacote,
    todas por `custodia/` e `isolamento/`, que não estavam na lista.

    Efeito medido: o coletor achava **20** pacotes onde há **16**. As quatro
    intrusas — `C07-lf`, `C07-lf-baseline`, `c02-vivo` e `candidato` — não têm
    sumário próprio, saíam como `SEM_SUMARIO … PROBLEMA`, e o portão do coletor
    fechava. O CI ficou **vermelho por 21 corridas seguidas, desde 2026-08-08**,
    com os dezesseis pacotes reais TODOS verdes o tempo inteiro.

    É a mesma correção que o validador do CEO já tinha recebido, e que este arquivo
    não recebeu: conserto-de-instancia-nao-e-conserto-de-mecanismo, com o defeito
    sobrevivendo no arquivo vizinho.

    **O critério, e por que ele não tem lista:** um pacote real tem `evals/` como
    FILHO — o `evals` aparece uma vez só, no fim, e nunca dentro do caminho do
    próprio pacote. Cópia de campanha tem `evals/` como ANCESTRAL, porque ela mora
    dentro de `evals/<campanha>/…`. Some-se a isso a anatomia que a casa exige de
    todo pacote gerente: `SKILL.md` e `CONTRATO-DE-COMPROMISSO.md` na raiz.
    Fixture nova, com nome que ninguém imaginou, cai fora por posição.
    """
    pacote = validador.parents[1]
    try:
        relativo = pacote.relative_to(ESTRUTURA)
    except ValueError:
        return False
    if "evals" in relativo.parts:          # evals é ANCESTRAL: cópia de campanha
        return False
    return (pacote / "SKILL.md").is_file() and (pacote / CONTRATO).is_file()


def _autoteste_da_descoberta() -> list[str]:
    """As DUAS metades do critério provam que veem, a cada execução.

    **Por que existe.** A prova de mutação do conserto acima matou a metade do
    `evals` ancestral (M1: o coletor volta a achar 20 pacotes e o portão fecha) e
    deixou VIVA a da anatomia (M2: continua achando 16). O motivo é legítimo — na
    árvore de hoje o primeiro teste já basta, e o segundo é defesa em profundidade.
    Mas mutante que sobrevive porque a regra vizinha cobre o caso **não prova regra
    nenhuma**, e uma anatomia que ninguém exercita é a próxima a ser apagada por
    parecer inútil.

    Cada amostra abaixo só pode ser reprovada por UMA das metades. Se a anatomia
    for removida, a terceira passa a ser aceita e este autoteste fica vermelho —
    que é o que faltava para o M2 ser matável.
    """
    import tempfile
    erros: list[str] = []
    global ESTRUTURA
    original = ESTRUTURA
    raiz = Path(tempfile.mkdtemp(prefix="autoteste-descoberta-"))
    try:
        ESTRUTURA = raiz

        def plantar(rel: str, com_anatomia: bool) -> Path:
            pac = raiz / rel
            (pac / "evals").mkdir(parents=True, exist_ok=True)
            v = pac / "evals" / "validate_workflow.py"
            v.write_text("# fixture\n", encoding="utf-8")
            if com_anatomia:
                (pac / "SKILL.md").write_text("x", encoding="utf-8")
                (pac / CONTRATO).write_text("x", encoding="utf-8")
            return v

        real = plantar("pacote-real", True)
        copia = plantar("pacote-real/evals/campanha-x/custodia/copia", True)
        sem_anatomia = plantar("pasta-qualquer", False)

        if not _e_pacote_real(real):
            erros.append("DESCOBERTA_CEGA: pacote com anatomia e evals como FILHO "
                         "foi recusado; o coletor perderia cadeia de verdade")
        if _e_pacote_real(copia):
            erros.append("DESCOBERTA_ACEITA_COPIA: caminho com `evals` como "
                         "ANCESTRAL foi aceito como pacote — é a metade que o "
                         "mutante M1 mata, e ela precisa acusar")
        if _e_pacote_real(sem_anatomia):
            erros.append("DESCOBERTA_IGNORA_ANATOMIA: pasta sem SKILL.md e sem "
                         + CONTRATO + " foi aceita como pacote gerente — é a "
                         "metade que o mutante M2 mata, e sem esta amostra ela "
                         "sobrevive por a regra vizinha cobrir o caso")
    except Exception as exc:  # noqa: BLE001
        erros.append("DESCOBERTA_QUEBRADA: o autoteste levantou "
                     f"{exc.__class__.__name__}: {exc}")
    finally:
        ESTRUTURA = original
        shutil.rmtree(raiz, ignore_errors=True)
    return erros


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    destino = Path(argv[1])

    # O detector prova que enxerga ANTES de julgar a árvore. Detector quebrado
    # devolve lista curta em silêncio, e lista curta lê-se como "não há mais nada".
    problemas_do_detector = _autoteste_da_descoberta()
    if problemas_do_detector:
        print("AUTOTESTE DA DESCOBERTA FALHOU — o coletor não mede nada assim:")
        for p in problemas_do_detector:
            print("  " + p)
        return 2
    encontrados = sorted(ESTRUTURA.rglob("evals/validate_workflow.py"))
    todos = {
        p.parents[1].name: p.parents[1]   # .../<pacote>/evals/validate_workflow.py
        for p in encontrados
        if _e_pacote_real(p)
    }
    # CONTE OS DESCARTADOS. Corte silencioso lê-se como "cobri tudo", e foi assim
    # que a cadeia já foi contada de 16 para 101 uma vez. Quem lê o log precisa ver
    # o que ficou de fora, não só o que entrou.
    descartados = [p for p in encontrados if not _e_pacote_real(p)]
    print(f"pacotes reais: {len(todos)} | descartados por não serem cadeia: "
          f"{len(descartados)}")
    for p in descartados[:8]:
        print(f"  descartado: {p.parents[1].relative_to(ESTRUTURA)}")
    if len(descartados) > 8:
        print(f"  … e mais {len(descartados) - 8}")

    pedidos = argv[2:] or sorted(todos)
    faltando = [n for n in pedidos if n not in todos]
    if faltando:
        print(f"pacote sem validador: {', '.join(faltando)}")
        return 2
    return coletar({n: todos[n] for n in pedidos}, destino)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
