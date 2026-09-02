# -*- coding: utf-8 -*-
"""Prova que as travas do `publicar_vitrine.py` reprovam — mutando cada uma.

    python prova_mutacao_vitrine.py

POR QUE ESTA PROVA EXISTE. Um validador verde não prova que a trava funciona:
prova que nada a acionou. O jeito de saber é quebrar a trava de propósito e
confirmar que a bateria fica VERMELHA. Mutante que sobrevive é buraco no teste,
não qualidade do código.

DUAS REGRAS QUE ESTA BATERIA SEGUE, e as duas vieram de erro medido:

  * **Uma condição por caso.** Um caso negativo que viola duas condições morre
    pela vizinha, e o mutante da condição que ele diz testar sobrevive. Em
    2026-09-01 isso custou 3 mutantes vivos de 7 numa prova irmã. Aqui cada
    fixture quebra **uma** coisa.
  * **Caso positivo não mata mutante que cala.** A árvore limpa serve para
    provar que a bateria não acusa o inocente; ela nunca conta como morte.

As fixtures são árvores minúsculas em pasta temporária, não a Estrutura real: a
bateria tem de ser barata o bastante para rodar sempre, e hermética o bastante
para que o resultado não dependa do estado do cofre naquele dia.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ALVO = AQUI / "publicar_vitrine.py"

# Um caminho absoluto de mentira, montado em pedaços para que ESTE arquivo não
# case o próprio padrão que usa como isca. A isca precisa ser real para o
# detector; o arquivo que a carrega, não.
ISCA = "C:" + "\\" + "Users" + "\\" + "alguem" + "\\" + "x.md"


# ----------------------------------------------------------------- carregar

def carregar(fonte_texto: str | None = None):
    """Importa o alvo, opcionalmente com o código mutado em memória."""
    texto = fonte_texto if fonte_texto is not None else ALVO.read_text(encoding="utf-8")
    spec = importlib.util.spec_from_loader("pv_sob_prova", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = str(ALVO)
    exec(compile(texto, str(ALVO), "exec"), mod.__dict__)
    return mod


# ----------------------------------------------------------------- fixtures

def montar(base: Path, *, arquivos_fonte: dict[str, str],
           arquivos_vitrine: dict[str, str], exclusoes: dict) -> tuple[Path, Path]:
    fonte, vitrine = base / "fonte", base / "vitrine"
    for raiz, arquivos in ((fonte, arquivos_fonte), (vitrine, arquivos_vitrine)):
        for rel, conteudo in arquivos.items():
            p = raiz / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(conteudo, encoding="utf-8", newline="\n")
    # A lista de exclusões é arquivo DA FONTE, então também tem de estar
    # publicada — senão `SEM_DESTINO_DECLARADO` acende em toda fixture e
    # nenhum caso isola condição nenhuma. Foi assim na primeira rodada desta
    # prova: 9 de 10 casos acusaram duas travas, e a culpa era da fixture.
    texto = json.dumps(exclusoes, ensure_ascii=False, indent=2) + "\n"
    for raiz in (fonte, vitrine):
        (raiz / "vitrine-exclusoes.json").write_text(
            texto, encoding="utf-8", newline="\n")
    return fonte, vitrine


def base_limpa() -> tuple[dict, dict, dict]:
    """Árvore que passa: tudo publicado ou excluído, e o controle acusa."""
    fonte = {
        "SKILL.md": "conteudo qualquer\n",
        "pacote/evals/PLACAR.md": "placar\n",
        # a campanha excluída carrega a isca: é o braço de controle
        "pacote/evals/campanha-2026-01-01/nota.md": "veja %s\n" % ISCA,
    }
    vitrine = {
        "SKILL.md": "conteudo qualquer\n",
        "pacote/evals/PLACAR.md": "placar\n",
        "README.md": "so da vitrine\n",
    }
    exc = {
        "arquivos_so_da_vitrine": ["README.md"],
        "pastas": {"pacote/evals/campanha-2026-01-01": "campanha"},
        "isencoes": [],
    }
    return fonte, vitrine, exc


# Cada caso devolve (fonte, vitrine, exclusoes, rotulo_esperado).
# O rótulo é a trava que aquele caso — e SÓ aquele — deve acionar.
def casos() -> list[tuple[str, callable, str]]:
    def sem_destino():
        f, v, e = base_limpa()
        f["pacote/evals/ADENDO.md"] = "adendo que ninguem publicou\n"
        return f, v, e

    def exclusao_morta():
        f, v, e = base_limpa()
        e["pastas"]["pacote/evals/campanha-que-nao-existe"] = "campanha"
        return f, v, e

    def exclusao_redundante():
        f, v, e = base_limpa()
        # a pasta aninhada TEM de existir: se não existir, o caso aciona
        # EXCLUSAO_MORTA junto e deixa de isolar a redundância.
        f["pacote/evals/campanha-2026-01-01/dentro/x.md"] = "aninhado\n"
        e["pastas"]["pacote/evals/campanha-2026-01-01/dentro"] = "aninhada"
        return f, v, e

    def orfao():
        f, v, e = base_limpa()
        v["pacote/so-na-vitrine.md"] = "editado direto na vitrine\n"
        return f, v, e

    def divergente():
        f, v, e = base_limpa()
        v["pacote/evals/PLACAR.md"] = "placar DIFERENTE\n"
        return f, v, e

    def achado():
        f, v, e = base_limpa()
        f["pacote/evals/PLACAR.md"] = "placar com %s\n" % ISCA
        v["pacote/evals/PLACAR.md"] = f["pacote/evals/PLACAR.md"]
        return f, v, e

    def detector_cego():
        f, v, e = base_limpa()
        f["pacote/evals/campanha-2026-01-01/nota.md"] = "campanha limpa\n"
        return f, v, e

    def isencao_incompleta():
        f, v, e = base_limpa()
        # falta SO o motivo: com o digest presente, a segunda checagem de
        # completude nao dispara e o caso isola a condicao que diz testar.
        e["isencoes"] = [{"arquivo": "SKILL.md", "padrao": "e-mail",
                          "prova": "sha256", "sha256": "00" * 32}]
        return f, v, e

    def isencao_sem_prova():
        f, v, e = base_limpa()
        e["isencoes"] = [{"arquivo": "SKILL.md", "padrao": "e-mail",
                          "prova": "confie-em-mim", "motivo": "porque sim"}]
        return f, v, e

    def isencao_com_digest_velho():
        f, v, e = base_limpa()
        f["pacote/evals/PLACAR.md"] = "placar com %s\n" % ISCA
        v["pacote/evals/PLACAR.md"] = f["pacote/evals/PLACAR.md"]
        e["isencoes"] = [{
            "arquivo": "pacote/evals/PLACAR.md",
            "padrao": "caminho absoluto Windows",
            "prova": "sha256",
            "sha256": hashlib.sha256(b"outro conteudo").hexdigest(),
            "motivo": "digest de um conteudo que nao e mais este",
        }]
        return f, v, e

    return [
        ("arquivo da fonte sem destino declarado", sem_destino, "SEM_DESTINO_DECLARADO"),
        ("exclusao que aponta para pasta inexistente", exclusao_morta, "EXCLUSAO_MORTA"),
        ("exclusao aninhada em outra", exclusao_redundante, "EXCLUSAO_REDUNDANTE"),
        ("arquivo publicado sem par na fonte", orfao, "ORFAO_NA_VITRINE"),
        ("arquivo publicado com bytes diferentes", divergente, "DIVERGENTE"),
        ("caminho absoluto no que seria publicado", achado, "ACHADO_DE_PUBLICACAO"),
        ("braco de controle sem nenhum achado", detector_cego, "DETECTOR_CEGO"),
        ("isencao sem motivo escrito", isencao_incompleta, "ISENCAO_INCOMPLETA"),
        ("isencao com prova que ninguem confere", isencao_sem_prova,
         "ISENCAO_SEM_PROVA_CONHECIDA"),
        ("isencao cujo digest nao bate mais", isencao_com_digest_velho,
         "ACHADO_DE_PUBLICACAO"),
    ]


# ----------------------------------------------------------------- execução

def rodar_bateria(mod) -> tuple[list[str], list[str]]:
    """Devolve (casos que passaram, casos que falharam)."""
    passaram, falharam = [], []
    with tempfile.TemporaryDirectory() as tmp:
        # caso positivo: arvore limpa nao pode acusar nada
        base = Path(tmp) / "positivo"
        f, v, e = base_limpa()
        fonte, vitrine = montar(base, arquivos_fonte=f, arquivos_vitrine=v, exclusoes=e)
        mod.RAIZ, mod.EXCLUSOES = fonte, fonte / "vitrine-exclusoes.json"
        r = mod.conferir(vitrine, verboso=False)
        if r.erros:
            falharam.append("POSITIVO acusou arvore limpa: %s" % r.erros[:2])
        else:
            passaram.append("POSITIVO: arvore limpa nao acusa")

        for i, (nome, monta, rotulo) in enumerate(casos()):
            base = Path(tmp) / ("caso%02d" % i)
            f, v, e = monta()
            fonte, vitrine = montar(base, arquivos_fonte=f, arquivos_vitrine=v,
                                    exclusoes=e)
            mod.RAIZ, mod.EXCLUSOES = fonte, fonte / "vitrine-exclusoes.json"
            r = mod.conferir(vitrine, verboso=False)
            acionadas = {er.split(":", 1)[0] for er in r.erros}
            if rotulo not in acionadas:
                falharam.append("%s: esperava %s, veio %s"
                                % (nome, rotulo, sorted(acionadas) or "nada"))
            elif len(acionadas) > 1:
                # uma condicao por caso: se duas acendem, o caso nao isola nada
                falharam.append("%s: acionou MAIS DE UMA trava (%s) — caso que "
                                "viola duas condicoes morre pela vizinha"
                                % (nome, sorted(acionadas)))
            else:
                passaram.append(nome)
    return passaram, falharam


# Cada mutante quebra UMA trava. O texto trocado tem de existir uma única vez.
MUTANTES = [
    ("nao acusa arquivo sem destino",
     'if sem_destino:', 'if False and sem_destino:'),
    ("nao acusa exclusao morta",
     'if not (RAIZ / pasta).is_dir():', 'if False:'),
    ("nao acusa exclusao aninhada",
     'if pai:', 'if False and pai:'),
    ("nao acusa orfao",
     'if orfaos:', 'if False and orfaos:'),
    ("nao acusa divergente",
     'if divergentes:', 'if False and divergentes:'),
    # mutar `reais += 1` NAO quebra nada: a acusacao e o `r.falha` da linha
    # seguinte, e o contador so alimenta o relatorio. O mutante certo desliga a
    # decisao, nao a estatistica.
    ("nao acusa achado de publicacao",
     'if _isento(rel, padrao, pos, isentos, cache_spans):', 'if True:'),
    ("nao acusa detector cego",
     'elif n_controle == 0:', 'elif False:'),
    ("aceita isencao incompleta",
     'if faltam:', 'if False and faltam:'),
    ("aceita prova desconhecida",
     'if e["prova"] not in PROVAS:', 'if False:'),
    ("isencao sha256 passa a valer sem conferir o digest",
     'return e["sha256"] == _sha_ou_none(RAIZ / rel)', 'return True'),
]


def main() -> int:
    print("=" * 68)
    print("BATERIA SOBRE O CODIGO INTACTO")
    print("=" * 68)
    mod = carregar()
    passaram, falharam = rodar_bateria(mod)
    for p in passaram:
        print("  [ok]    %s" % p)
    for f in falharam:
        print("  [FALHA] %s" % f)
    if falharam:
        print("\nA bateria nao fecha verde no codigo intacto. Sem isso, nenhuma "
              "morte de mutante significa coisa alguma.")
        return 1

    print("\n" + "=" * 68)
    print("MUTACAO — cada trava quebrada de proposito")
    print("=" * 68)
    original = ALVO.read_text(encoding="utf-8")
    mortos, vivos = 0, []
    for nome, velho, novo in MUTANTES:
        if original.count(velho) != 1:
            vivos.append("%s (trecho ausente ou repetido: %r)" % (nome, velho))
            print("  [ERRO ] %-52s trecho nao unico" % nome)
            continue
        mutado = original.replace(velho, novo, 1)
        try:
            mod_mut = carregar(mutado)
            _, falhou = rodar_bateria(mod_mut)
        except Exception as exc:                      # mutante que nem carrega
            falhou = ["mutante nao executa: %s" % exc]
        if falhou:
            mortos += 1
            print("  [MORTO] %-52s a bateria acusou" % nome)
        else:
            vivos.append(nome)
            print("  [VIVO ] %-52s NINGUEM PERCEBEU" % nome)

    print("\n%d/%d mutantes mortos." % (mortos, len(MUTANTES)))
    if vivos:
        print("\nSOBREVIVERAM — e cada um e um buraco no TESTE, nao no codigo:")
        for v in vivos:
            print("   %s" % v)
        return 1
    print("Toda trava tem pelo menos um caso que a aciona, e nenhum caso "
          "depende de outra para acender.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
