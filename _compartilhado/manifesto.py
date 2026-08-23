#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manifesto verificável da Estrutura — o que existe, e o que mudou desde a última vez.

TAREFA 57, primeira pepita do garimpo dirigido à Estrutura (tarefa 56).

**O padrão, e de onde veio.** O `ruvnet/ruflo` (MIT) publica um *witness chain*
— manifesto por correção, com histórico temporal e **bidirecional**: prova que
a correção entrou **e alerta quando um commit posterior a desfaz em silêncio**.
Nada dele foi instalado aqui; o que se garimpou foi a **forma**, e ela responde
a quatro coisas que esta casa mediu doendo:

  T53  a lista de exceção que "só podia encolher" foi de 7 para 13 e nada notou.
  T48  os 23 contratos convertidos podiam voltar à prosa sem nada ficar vermelho.
  T54  minha verificação de paridade deixou de valer no merge seguinte.
  T52  1094 arquivos divergem entre fonte e runtime, TODOS só por fim de linha.

Um manifesto com predecessor responde às três primeiras por diferença. A quarta
é o motivo do parágrafo seguinte.

**Por que digest NORMALIZADO, e não bytes crus.** `sha256_file` mede os bytes do
checkout: o mesmo conteúdo em CRLF e em LF dá dois valores, e a conferência fica
vermelha num clone sem que um caractere tenha mudado. Medido em 2026-08-07:
**1532** dos digests declarados na Estrutura quebrariam se o `eol=lf` fosse
ligado, porque `sha256_file` tem 248 sítios de chamada e
`sha256_texto_normalizado` tinha **27, quase todos comentário — nenhum consumo
real**. Esse órfão é o item `T19-A3`, aberto desde 04/ago.

Este manifesto é o **primeiro consumidor de verdade** dele. É o que torna o
manifesto verificável num runner Linux a partir de uma árvore escrita no
Windows — e é o que permite provar a divergência de EOL por execução, numa
matriz de sistemas operacionais, **sem** migrar os 248 sítios antes.

**O que este arquivo NÃO faz, declarado:** não assina. Assinatura exige chave, e
chave não se gera nem se manuseia aqui. O caminho previsto é atestação por OIDC
no CI (`actions/attest-build-provenance`), que assina sem que ninguém guarde
segredo. Enquanto ela não existir, este manifesto prova **integridade e
diferença**, não **origem** — e essa distinção é a fronteira entre a tarefa 57 e
as tarefas 49 e 50.

Uso:
    python _compartilhado/manifesto.py gerar     [--saida MANIFESTO.json]
    python _compartilhado/manifesto.py verificar [--manifesto MANIFESTO.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from _compartilhado.validador_schema import sha256_texto_normalizado  # noqa: E402

NOME_PADRAO = "MANIFESTO-DA-ESTRUTURA.json"

RECEITA = (
    "_compartilhado/validador_schema.py::sha256_texto_normalizado sobre cada "
    "arquivo — BOM removido, CRLF trocado por LF, bytes UTF-8. Caminhos "
    "relativos à raiz da Estrutura, em POSIX, ordenados. O digest do manifesto "
    "cobre o bloco `arquivos`, nunca o arquivo inteiro, para que ele possa "
    "carregar o próprio valor sem virar autorreferência."
)

# O que o manifesto cobre: a árvore da Estrutura menos o que é gerado, temporário
# ou registro de execução. Cada exclusão tem motivo, porque exclusão sem motivo é
# onde a deriva se esconde.
EXCLUIR_PASTAS = {
    "__pycache__",          # bytecode, regerado a cada execução
    ".git",
    "fixtures",             # área de cópia temporária de campanha
}
EXCLUIR_NOMES = {
    NOME_PADRAO,            # o manifesto não se inclui: seria autorreferência
    NOME_PADRAO + ".bak",
}


def _arquivos(raiz: Path) -> list[Path]:
    return sorted(
        p for p in raiz.rglob("*")
        if p.is_file()
        and not EXCLUIR_PASTAS & set(p.parts)
        and p.name not in EXCLUIR_NOMES
    )


def inventariar(raiz: Path) -> dict[str, str]:
    """Caminho relativo POSIX -> digest normalizado. É o corpo do manifesto."""
    return {
        p.relative_to(raiz).as_posix(): sha256_texto_normalizado(p)
        for p in _arquivos(raiz)
    }


def digest_do_inventario(arquivos: dict[str, str]) -> str:
    """Digest do BLOCO de arquivos, não do arquivo do manifesto.

    Assim o manifesto pode carregar o próprio digest sem o paradoxo de precisar
    conter um valor que depende de si mesmo.
    """
    import hashlib

    corpo = json.dumps(arquivos, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(corpo).hexdigest()


def gerar(raiz: Path, gerado_em: str, predecessor: dict | None) -> dict:
    arquivos = inventariar(raiz)
    manifesto = {
        "artifact_type": "MANIFESTO_DA_ESTRUTURA",
        "versao_do_formato": 1,
        "gerado_em": gerado_em,
        "receita": RECEITA,
        "assinatura": {
            "estado": "NAO_ASSINADO",
            "motivo": (
                "assinatura exige chave; o caminho previsto é atestação por "
                "OIDC no CI (actions/attest-build-provenance), que assina sem "
                "que ninguém guarde segredo. Enquanto não existir, este "
                "manifesto prova integridade e diferença, não origem."
            ),
        },
        "total_de_arquivos": len(arquivos),
        "digest_do_inventario": digest_do_inventario(arquivos),
        "predecessor": None,
        "arquivos": arquivos,
    }
    if predecessor:
        manifesto["predecessor"] = {
            "gerado_em": predecessor.get("gerado_em"),
            "digest_do_inventario": predecessor.get("digest_do_inventario"),
            "total_de_arquivos": predecessor.get("total_de_arquivos"),
        }
        # TAREFA 57 — a diferença PERSISTE, e é isso que fecha a catraca.
        #
        # Até 2026-08-22 `comparar` era chamado aqui e o resultado apenas
        # IMPRESSO: `+N acrescentados, -N removidos, ~N alterados`. A linha some
        # com o terminal, nada a consome, e nenhum portão a lê. É a mesma forma
        # do retorno que cai num `lixo` que ninguém lê — evidência computada e
        # descartada.
        #
        # OS REMOVIDOS VÃO NOMEADOS, e o resto vai contado, e a assimetria é
        # deliberada: acrescentar e alterar são o trabalho normal e a lista
        # inteira incharia o arquivo; **remover é o que some em silêncio**, e é
        # exatamente o que a tarefa 53 não pegava.
        _d = comparar(predecessor.get("arquivos") or {}, arquivos)
        manifesto["mudancas_desde_o_predecessor"] = {
            "acrescentados": len(_d["acrescentados"]),
            "alterados": len(_d["alterados"]),
            "removidos": _d["removidos"],
        }
    return manifesto


def comparar(anterior: dict[str, str], atual: dict[str, str]) -> dict[str, list[str]]:
    """A diferença nos TRÊS sentidos. Só os três juntos fecham a catraca.

    `removidos` é o que a T53 não tinha: uma trava que só olha o que existe hoje
    nunca percebe o que sumiu, e sumir em silêncio é como uma exceção histórica
    perde objeto sem ninguém ver.
    """
    return {
        "acrescentados": sorted(set(atual) - set(anterior)),
        "removidos": sorted(set(anterior) - set(atual)),
        "alterados": sorted(k for k in set(anterior) & set(atual)
                            if anterior[k] != atual[k]),
    }


def remocoes_nao_declaradas(manifesto: dict) -> list[str]:
    """Arquivo que SUMIU entre um manifesto e o seguinte tem de ser declarado.

    Acrescentar e alterar são o trabalho normal. **Remover é o que desaparece em
    silêncio** — e um manifesto regenerado depois da remoção descreve a árvore
    nova com perfeição, então `verificar` passa e ninguém percebe. Foi assim que
    a tarefa 53 ficou sem catraca: uma trava que só olha o que existe hoje nunca
    nota o que deixou de existir.

    A declaração é um bloco `remocoes_declaradas` com uma linha por caminho. Não
    se pede justificativa longa: pede-se que alguém tenha ESCRITO que sabia.
    """
    mudancas = manifesto.get("mudancas_desde_o_predecessor")
    if not isinstance(mudancas, dict):
        return []
    removidos = mudancas.get("removidos") or []
    if not removidos:
        return []
    declaradas = manifesto.get("remocoes_declaradas")
    declaradas = declaradas if isinstance(declaradas, dict) else {}
    faltam = [c for c in removidos if not str(declaradas.get(c, "")).strip()]
    if not faltam:
        return []
    return [
        "REMOCAO_NAO_DECLARADA: %d arquivo(s) sumiram desde o manifesto anterior "
        "e não têm linha em `remocoes_declaradas`: %s%s. Regenerar o manifesto "
        "depois de apagar faz `verificar` passar — a árvore nova é descrita com "
        "perfeição, e o que sumiu não deixa rastro (tarefa 57)"
        % (len(faltam), ", ".join(faltam[:4]), " …" if len(faltam) > 4 else "")
    ]


def verificar(raiz: Path, manifesto: dict) -> list[str]:
    """O manifesto descreve a árvore de hoje? Devolve os problemas, nomeados."""
    erros: list[str] = list(remocoes_nao_declaradas(manifesto))
    declarados = manifesto.get("arquivos")
    if not isinstance(declarados, dict) or not declarados:
        return ["manifesto sem bloco `arquivos` — não há o que verificar"]

    esperado = manifesto.get("digest_do_inventario")
    recomputado = digest_do_inventario(declarados)
    if esperado != recomputado:
        erros.append(
            f"o manifesto contradiz a si mesmo: declara "
            f"digest_do_inventario {esperado} e o bloco `arquivos` "
            f"recomputa {recomputado}"
        )

    if manifesto.get("total_de_arquivos") != len(declarados):
        erros.append(
            f"o manifesto declara {manifesto.get('total_de_arquivos')} arquivos "
            f"e lista {len(declarados)}"
        )

    d = comparar(declarados, inventariar(raiz))
    for rotulo, itens in d.items():
        if itens:
            erros.append(
                f"{len(itens)} arquivo(s) {rotulo} desde o manifesto: "
                f"{itens[:5]}{' …' if len(itens) > 5 else ''}"
            )
    return erros


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("acao", choices=["gerar", "verificar"])
    ap.add_argument("--manifesto", default=str(RAIZ / NOME_PADRAO))
    ap.add_argument("--gerado-em", default="",
                    help="carimbo ISO; obrigatório em `gerar` para o valor não "
                         "vir do relógio do runner e virar ruído no diff")
    args = ap.parse_args(argv[1:])
    caminho = Path(args.manifesto)

    if args.acao == "gerar":
        if not args.gerado_em:
            print("gerar exige --gerado-em: carimbo do relógio local muda a "
                  "cada execução e polui o diff do manifesto")
            return 2
        anterior = (json.loads(caminho.read_text(encoding="utf-8"))
                    if caminho.is_file() else None)
        m = gerar(RAIZ, args.gerado_em, anterior)
        caminho.write_text(
            json.dumps(m, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n")
        print("manifesto gerado: %d arquivos, inventário %s"
              % (m["total_de_arquivos"], m["digest_do_inventario"][:23]))
        if anterior:
            d = comparar(anterior["arquivos"], m["arquivos"])
            print("  desde %s: +%d acrescentados, -%d removidos, ~%d alterados"
                  % (anterior.get("gerado_em", "?"), len(d["acrescentados"]),
                     len(d["removidos"]), len(d["alterados"])))
        return 0

    if not caminho.is_file():
        print("manifesto ausente em %s — gere antes de verificar" % caminho)
        return 2
    erros = verificar(RAIZ, json.loads(caminho.read_text(encoding="utf-8")))
    if erros:
        print("MANIFESTO NÃO CONFERE:")
        for e in erros:
            print("  " + e)
        return 1
    print("manifesto confere com a árvore.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
