# -*- coding: utf-8 -*-
"""Espelha a Estrutura na vitrine pública, pela regra declarada — e reprova a deriva.

    python publicar_vitrine.py conferir       # não escreve; sai != 0 se houver deriva
    python publicar_vitrine.py espelhar       # escreve, depois de conferir
    python publicar_vitrine.py numeros        # confere os números que o README declara
    python publicar_vitrine.py semear         # cria a lista de exclusões (uma vez só)

POR QUE ESTE ARQUIVO EXISTE, e a razão é uma medição, não uma preferência. A
vitrine foi montada à mão em 2026-08-23 e sincronizada à mão depois. Em
2026-09-02 mediu-se que **25 arquivos da fonte não estavam lá e não estavam
excluídos por regra nenhuma** — 18 adendos de `PLACAR`, um `ROLLBACK.md` e sete
peças de uma prova. Eles nasceram depois da montagem e ficaram para trás por dez
dias porque **não havia quem os trouxesse**. Um era alvo de link quebrado; outro
fazia um pacote reprovar `130/131`.

A lição não é "faltou disciplina": é que **a regra da vitrine só existia em
prosa**, no README, e prosa não recusa nada. Aviso em prosa não previne erro.

O QUE ESTE SCRIPT TRAVA, e cada trava tem um defeito real por trás:

  1. `arquivo sem destino declarado` — todo arquivo da fonte tem de estar **ou**
     publicado **ou** dentro de uma exclusão declarada. Foi o buraco por onde os
     25 sumiram: ausência não é categoria, e por isso não aparecia.
  2. `exclusão morta` — exclusão que aponta para pasta inexistente reprova. Lista
     que não é conferida contra a árvore envelhece e vira álibi.
  3. `órfão na vitrine` — arquivo publicado que não existe na fonte reprova.
     Vitrine é espelho; o que só existe lá é edição, e a regra da casa é editar a
     fonte.
  4. `auditoria de publicação` — 15 padrões de segredo, dado pessoal e caminho
     local sobre **tudo** que seria publicado. Um achado real bloqueia.
  5. `detector cego` — a auditoria roda também sobre um **braço de controle** (o
     conteúdo excluído, que sabidamente carrega caminho absoluto). Se o controle
     der ZERO, o script reprova: zero dos dois lados é suspeita de detector
     quebrado, **não** prova de árvore limpa.
  6. `remoção não aceita` — `espelhar` que apagaria arquivo da vitrine para e
     exige `--aceitar-remocoes`. Remover é o que some em silêncio.
  7. `número do README` — `numeros` confere o que o README **declara** contra o
     que a árvore **mede**, e reprova a divergência. Se a declaração nem for
     encontrada, também reprova: regex que não casa é cegueira, não aprovação.

O QUE ELE NÃO FAZ, declarado para não ser confundido com garantia: não faz
`git commit` nem `git push`. Publicar é ato de Jeremias, e um script que
publica sozinho transforma um erro de regra em erro público irreversível.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VITRINE_PADRAO = RAIZ.parent / "_github-publish-estrutura"
EXCLUSOES = RAIZ / "vitrine-exclusoes.json"

# Pastas que nunca entram em contagem nem em cópia: são artefato de execução.
IGNORAR_SEMPRE = {"__pycache__", ".git"}


# ----------------------------------------------------------------- detecção

# Os padrões da auditoria de publicação. A lista é a mesma de 2026-08-23,
# reescrita como código para poder ser executada em vez de lembrada.
PADROES: list[tuple[str, re.Pattern]] = [
    ("caminho absoluto Windows", re.compile(r"[A-Za-z]:[\\/]Users[\\/]", re.I)),
    ("conta de usuario local", re.compile(r"\bDuque\b")),
    ("caminho do cofre", re.compile(r"Curso-Java|Novos Projetos", re.I)),
    ("caminho absoluto POSIX",
     re.compile(r"(?<![\w.])/(?:home|Users|mnt/c)/[A-Za-z0-9_.-]+/")),
    ("AppData / Temp local", re.compile(r"AppData[\\/]|%TEMP%|%USERPROFILE%", re.I)),
    ("e-mail", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("telefone BR", re.compile(r"\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b")),
    ("CPF/CNPJ",
     re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")),
    ("chave privada PEM", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("token AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("token GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("token Anthropic/OpenAI", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Bearer / Authorization",
     re.compile(r"\b(?:Bearer|Authorization:)\s+[A-Za-z0-9._~+/=-]{16,}")),
    ("senha atribuida",
     re.compile(r"\b(?:password|passwd|senha|secret|api[_-]?key)\s*[:=]\s*['\"][^'\"]{4,}",
                re.I)),
    ("string de conexao",
     re.compile(r"\b(?:mongodb|postgres|postgresql|mysql|redis)://[^\s'\"]+")),
]

# Onde um casamento NÃO conta, e por quê. Isto corrige o DETECTOR, e é diferente
# de isentar um arquivo: a correção vale para qualquer arquivo, presente e
# futuro, enquanto a isenção vale para um conteúdo exato.
#
# Medido em 2026-09-02: `telefone BR` deu 144 casamentos, e **todos** eram dígitos
# dentro de digests, de nomes de arquivo e de uma URL da NASA. Isentar os arquivos
# um a um teria sido pior: o `MANIFESTO-DA-ESTRUTURA.json` muda de digest a cada
# regeneração, e a isenção morreria toda semana enquanto o falso positivo voltava.
# `re.I` não é detalhe: a primeira versão casava só hex minúsculo, e um SHA-256
# em MAIÚSCULO dentro de `fronteiras-e-fontes-canonicas.md` passou por telefone.
# Detector cego ao formato isenta — e isenta calado, que é o pior modo.
_HEX_LONGO = re.compile(r"[0-9a-fA-F]{32,}")
_URL = re.compile(r"https?://\S+")


def _regioes_neutras(texto: str) -> list[tuple[int, int]]:
    """Trechos onde um dígito não é dado pessoal: digest, URL, nome de arquivo."""
    regioes = [m.span() for m in _HEX_LONGO.finditer(texto)]
    regioes += [m.span() for m in _URL.finditer(texto)]
    return regioes


def _token_ao_redor(texto: str, pos: int) -> str:
    i = pos
    while i > 0 and not texto[i - 1].isspace() and texto[i - 1] not in '"\'':
        i -= 1
    j = pos
    while j < len(texto) and not texto[j].isspace() and texto[j] not in '"\'':
        j += 1
    return texto[i:j]


def _e_neutro(texto: str, m: re.Match, regioes: list[tuple[int, int]]) -> bool:
    for a, b in regioes:
        if a <= m.start() < b:
            return True
    tok = _token_ao_redor(texto, m.start())
    # nome de arquivo ou caminho: o dígito é identificador, não telefone
    return "/" in tok or "\\" in tok or re.search(r"\.[A-Za-z0-9]{2,5}$", tok) is not None


def varrer(caminhos: list[tuple[Path, str]]) -> dict[str, list[tuple[str, str, int]]]:
    """padrão -> [(relativo, trecho, posição)]. Só padrões com casamento aparecem.

    A posição vai junto porque uma isenção honesta precisa saber ONDE o
    casamento caiu — ver `_dentro_de_re_compile`.
    """
    achados: dict[str, list[tuple[str, str, int]]] = {}
    for p, rel in caminhos:
        try:
            t = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        neutras = _regioes_neutras(t)
        for nome, rx in PADROES:
            for m in rx.finditer(t):
                if nome in ("telefone BR", "CPF/CNPJ") and _e_neutro(t, m, neutras):
                    continue
                achados.setdefault(nome, []).append((rel, m.group(0)[:70], m.start()))
    return achados


def _dentro_de_re_compile(arquivo: Path) -> list[tuple[int, int]]:
    """Trechos que são literal passado a `re.compile(...)`, por AST.

    ISTO EXISTE PORQUE O DETECTOR CASA A SI MESMO. Este arquivo define os
    padrões, então contém, como literais, os mesmos textos que procura — e uma
    auditoria honesta não pode simplesmente pular o próprio código: seria a
    parte fiscalizada se isentando.

    A saída é uma PROVA, não uma permissão. A isenção só vale para casamentos que
    caem dentro de um literal de `re.compile`; um caminho de verdade escrito em
    qualquer outro ponto do arquivo continua reprovando. Por AST, e não por
    regex, para que comentar ou renomear não engane a conferência.
    """
    import ast
    try:
        texto = arquivo.read_text(encoding="utf-8")
        arvore = ast.parse(texto)
    except (SyntaxError, OSError, UnicodeDecodeError):
        return []
    # `col_offset` do ast conta BYTES UTF-8, não caracteres. Num arquivo com
    # acento — este — somar a coluna direto no texto decodificado desloca os
    # trechos e a isenção passa a cobrir o pedaço errado. Foi medido: com a
    # conta ingênua, das duas alternativas do MESMO literal de caminho local,
    # uma era isentada e a outra, poucas colunas adiante, continuava acusada.
    #
    # E este comentário não cita as alternativas por extenso de propósito: citar
    # colocaria o literal FORA de `re.compile`, e a trava — corretamente — o
    # acusaria. A prova cobre o padrão, nunca a prosa em volta dele.
    linhas_bytes = texto.encode("utf-8").splitlines(keepends=True)
    inicio_da_linha = [0]
    for lb in linhas_bytes:
        inicio_da_linha.append(inicio_da_linha[-1] + len(lb.decode("utf-8")))

    def deslocamento(lin: int, col: int) -> int:
        prefixo = linhas_bytes[lin - 1][:col].decode("utf-8", errors="ignore")
        return inicio_da_linha[lin - 1] + len(prefixo)

    spans: list[tuple[int, int]] = []
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Call):
            continue
        alvo = no.func
        nome = (alvo.attr if isinstance(alvo, ast.Attribute)
                else getattr(alvo, "id", ""))
        if nome != "compile":
            continue
        for arg in no.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                spans.append((deslocamento(arg.lineno, arg.col_offset),
                              deslocamento(arg.end_lineno, arg.end_col_offset)))
    return spans


# ----------------------------------------------------------------- inventário

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def arquivos_de(raiz: Path) -> list[str]:
    saida = []
    for base, dirs, files in os.walk(raiz):
        dirs[:] = [d for d in dirs if d not in IGNORAR_SEMPRE]
        for f in files:
            saida.append(Path(base, f).relative_to(raiz).as_posix())
    return sorted(saida)


def carregar_exclusoes() -> dict:
    if not EXCLUSOES.is_file():
        sys.exit("exclusões não declaradas: %s não existe. Rode `semear` uma vez "
                 "e revise o resultado antes de espelhar." % EXCLUSOES.name)
    return json.loads(EXCLUSOES.read_text(encoding="utf-8"))


def sob_exclusao(rel: str, pastas: list[str]) -> str | None:
    for pasta in pastas:
        if rel == pasta or rel.startswith(pasta + "/"):
            return pasta
    return None


# ----------------------------------------------------------------- conferência

class Relatorio:
    def __init__(self) -> None:
        self.erros: list[str] = []
        self.numeros: dict[str, int] = {}

    def falha(self, rotulo: str, detalhe: str) -> None:
        self.erros.append("%s: %s" % (rotulo, detalhe))


def conferir(vitrine: Path, verboso: bool = True) -> Relatorio:
    r = Relatorio()
    dados = carregar_exclusoes()
    pastas = sorted(dados.get("pastas", {}))
    so_da_vitrine = set(dados.get("arquivos_so_da_vitrine", []))
    isencoes = dados.get("isencoes", [])

    fonte = arquivos_de(RAIZ)
    publicados = arquivos_de(vitrine) if vitrine.is_dir() else []

    # (2) exclusão morta -------------------------------------------------
    for pasta in pastas:
        if not (RAIZ / pasta).is_dir():
            r.falha("EXCLUSAO_MORTA",
                    "`%s` está declarada e não existe na fonte. Lista que não é "
                    "conferida contra a árvore envelhece e vira álibi." % pasta)

    # exclusão aninhada em outra: redundância que esconde o que foi decidido
    for pasta in pastas:
        pai = sob_exclusao(pasta, [p for p in pastas if p != pasta])
        if pai:
            r.falha("EXCLUSAO_REDUNDANTE",
                    "`%s` já está coberta por `%s`." % (pasta, pai))

    # (1) arquivo da fonte sem destino declarado -------------------------
    conjunto_publicado = set(publicados)
    sem_destino = []
    a_publicar: list[str] = []
    for rel in fonte:
        if sob_exclusao(rel, pastas):
            continue
        a_publicar.append(rel)
        if rel not in conjunto_publicado:
            sem_destino.append(rel)
    if sem_destino:
        r.falha("SEM_DESTINO_DECLARADO",
                "%d arquivo(s) da fonte não estão publicados nem excluídos: %s%s. "
                "Foi por este buraco que 25 arquivos sumiram por dez dias em "
                "2026-09-02 — ausência não era categoria, então não aparecia."
                % (len(sem_destino), ", ".join(sem_destino[:5]),
                   " …" if len(sem_destino) > 5 else ""))

    # (3) órfão e divergente na vitrine ----------------------------------
    orfaos, divergentes = [], []
    for rel in publicados:
        if rel in so_da_vitrine:
            continue
        origem = RAIZ / rel
        if not origem.is_file() or sob_exclusao(rel, pastas):
            orfaos.append(rel)
        elif sha(origem) != sha(vitrine / rel):
            divergentes.append(rel)
    if orfaos:
        r.falha("ORFAO_NA_VITRINE",
                "%d arquivo(s) publicados sem par na fonte: %s%s. Vitrine é "
                "espelho; o que só existe lá é edição, e a regra é editar a fonte."
                % (len(orfaos), ", ".join(orfaos[:5]), " …" if len(orfaos) > 5 else ""))
    if divergentes:
        r.falha("DIVERGENTE",
                "%d arquivo(s) publicados com conteúdo diferente da fonte: %s%s."
                % (len(divergentes), ", ".join(divergentes[:5]),
                   " …" if len(divergentes) > 5 else ""))

    # (4) auditoria de publicação ----------------------------------------
    alvos = [(RAIZ / rel, rel) for rel in a_publicar]
    achados = varrer(alvos)
    isentos = _indexar_isencoes(isencoes, r)
    cache_spans: dict[str, list[tuple[int, int]]] = {}
    reais = 0
    for padrao, itens in sorted(achados.items()):
        for rel, trecho, pos in itens:
            if _isento(rel, padrao, pos, isentos, cache_spans):
                continue
            reais += 1
            r.falha("ACHADO_DE_PUBLICACAO", "[%s] %s :: %s" % (padrao, rel, trecho))

    # (5) braço de controle ----------------------------------------------
    controle = _amostra_de_controle(pastas)
    achados_controle = varrer(controle)
    n_controle = sum(len(v) for v in achados_controle.values())
    if not controle:
        r.falha("CONTROLE_VAZIO",
                "não há conteúdo excluído para servir de braço de controle; sem "
                "ele, o zero da auditoria não distingue árvore limpa de detector "
                "quebrado.")
    elif n_controle == 0:
        r.falha("DETECTOR_CEGO",
                "a auditoria deu ZERO também no braço de controle (%d arquivos "
                "sabidamente com caminho absoluto). Zero dos dois lados é "
                "suspeita de detector quebrado, não prova de árvore limpa."
                % len(controle))

    # (6) o custo da parcialidade, contado ------------------------------------
    links, quebrados = _links_da_vitrine(vitrine)

    r.numeros = {
        "fonte": len(fonte),
        "espelhados": len(a_publicar),
        "so_da_vitrine": len(so_da_vitrine),
        "excluidos": len(fonte) - len(a_publicar),
        "pastas_excluidas": len(pastas),
        "achados_reais": reais,
        "achados_no_controle": n_controle,
        "arquivos_no_controle": len(controle),
        "padroes": len(PADROES),
        "links": links,
        "links_quebrados": quebrados,
    }

    if verboso:
        _imprimir(r)
    return r


_LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")


def _links_da_vitrine(vitrine: Path) -> tuple[int, int]:
    """Conta links markdown relativos publicados, e quantos apontam para o nada.

    Este é o **custo declarado da parcialidade**: excluir uma campanha quebra
    todo link que apontava para dentro dela. O número não é uma falha — é uma
    consequência conhecida da regra —, então ele **não reprova**: só entra em
    `numeros`, para que o README não possa declará-lo errado. Reprovar aqui
    obrigaria a editar a fonte para agradar a vitrine, que é o inverso da regra.

    Só links relativos: URL externa não é conferível sem rede, e conferir com
    rede tornaria a auditoria dependente de estar on-line.
    """
    total = quebrados = 0
    for base, dirs, arqs in os.walk(vitrine):
        dirs[:] = [d for d in dirs if d not in IGNORAR_SEMPRE]
        for a in arqs:
            if not a.endswith(".md"):
                continue
            f = Path(base) / a
            texto = f.read_text(encoding="utf-8", errors="replace")
            for alvo in _LINK.findall(texto):
                if alvo.startswith(("http://", "https://", "mailto:")):
                    continue
                total += 1
                if not (f.parent / alvo.replace("%20", " ")).exists():
                    quebrados += 1
    return total, quebrados


def _sha_ou_none(p: Path) -> str | None:
    return sha(p) if p.is_file() else None


PROVAS = ("sha256", "dentro_de_re_compile")


def _indexar_isencoes(isencoes: list, r: Relatorio) -> dict[tuple[str, str], dict]:
    """Toda isenção declara COMO se prova, e nenhuma vale por alegação.

    `sha256`  — vale para um CONTEÚDO exato. Se o arquivo mudar, o digest não
                bate e a isenção morre sozinha: isenção que sobrevive à edição
                do arquivo isenta o que ninguém leu.
    `dentro_de_re_compile` — vale só para casamentos dentro de um literal de
                `re.compile`. Não é permissão por caminho: é uma propriedade
                conferida no arquivo, casamento a casamento.
    """
    idx: dict[tuple[str, str], dict] = {}
    for i, e in enumerate(isencoes):
        faltam = [c for c in ("arquivo", "padrao", "prova", "motivo") if not e.get(c)]
        if faltam:
            r.falha("ISENCAO_INCOMPLETA",
                    "isenção #%d sem %s. Isenção sem motivo escrito é isenção de "
                    "ninguém." % (i, "/".join(faltam)))
            continue
        if e["prova"] not in PROVAS:
            r.falha("ISENCAO_SEM_PROVA_CONHECIDA",
                    "isenção #%d declara prova `%s`, que este script não sabe "
                    "conferir. Prova que ninguém executa é alegação."
                    % (i, e["prova"]))
            continue
        if e["prova"] == "sha256" and not e.get("sha256"):
            r.falha("ISENCAO_INCOMPLETA",
                    "isenção #%d é do tipo sha256 e não traz o digest." % i)
            continue
        idx[(e["arquivo"], e["padrao"])] = e
    return idx


def _isento(rel: str, padrao: str, pos: int,
            isentos: dict[tuple[str, str], dict],
            cache: dict[str, list[tuple[int, int]]]) -> bool:
    e = isentos.get((rel, padrao))
    if not e:
        return False
    if e["prova"] == "sha256":
        return e["sha256"] == _sha_ou_none(RAIZ / rel)
    # dentro_de_re_compile: a prova é POR CASAMENTO, não pelo arquivo
    if rel not in cache:
        cache[rel] = _dentro_de_re_compile(RAIZ / rel)
    return any(a <= pos < b for a, b in cache[rel])


def _amostra_de_controle(pastas: list[str], teto: int = 400) -> list[tuple[Path, str]]:
    """Arquivos EXCLUÍDOS, para provar que o detector não está cego.

    Amostra e não tudo: o conjunto excluído tem 18 mil arquivos, e varrer todos
    a cada conferência trocaria uma trava barata por uma cara que ninguém roda.
    """
    saida: list[tuple[Path, str]] = []
    for pasta in pastas:
        base = RAIZ / pasta
        if not base.is_dir():
            continue
        for b, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in IGNORAR_SEMPRE]
            for f in files:
                p = Path(b, f)
                saida.append((p, p.relative_to(RAIZ).as_posix()))
                if len(saida) >= teto:
                    return saida
    return saida


def _imprimir(r: Relatorio) -> None:
    n = r.numeros
    print("fonte: %d arquivos" % n["fonte"])
    print("  espelhados na vitrine : %d  (+ %d só da vitrine)"
          % (n["espelhados"], n["so_da_vitrine"]))
    print("  excluídos             : %d, em %d pasta(s) declarada(s)"
          % (n["excluidos"], n["pastas_excluidas"]))
    print("auditoria: %d achado(s) real(is) no que seria publicado; "
          "%d no braço de controle (%d arquivos)"
          % (n["achados_reais"], n["achados_no_controle"], n["arquivos_no_controle"]))
    if r.erros:
        print("\n%d PROBLEMA(S):" % len(r.erros))
        for e in r.erros:
            print("  [FALHA] %s" % e)
    else:
        print("\nsem deriva: a vitrine descreve a fonte pela regra declarada.")


# ----------------------------------------------------------------- espelhar

def espelhar(vitrine: Path, aceitar_remocoes: bool) -> int:
    dados = carregar_exclusoes()
    pastas = sorted(dados.get("pastas", {}))
    so_da_vitrine = set(dados.get("arquivos_so_da_vitrine", []))

    fonte = [rel for rel in arquivos_de(RAIZ) if not sob_exclusao(rel, pastas)]
    publicados = arquivos_de(vitrine) if vitrine.is_dir() else []

    remover = [rel for rel in publicados
               if rel not in so_da_vitrine
               and (rel not in set(fonte))]
    if remover and not aceitar_remocoes:
        print("PARADO: espelhar apagaria %d arquivo(s) da vitrine." % len(remover))
        for rel in remover[:20]:
            print("   %s" % rel)
        if len(remover) > 20:
            print("   ... e mais %d" % (len(remover) - 20))
        print("\nRemover é o que some em silêncio: acrescentar e alterar são o\n"
              "trabalho normal, e um espelho regenerado depois de apagar descreve\n"
              "a árvore nova com perfeição. Confira a lista e repita com\n"
              "--aceitar-remocoes se for isso mesmo.")
        return 2

    escritos = apagados = 0
    for rel in fonte:
        origem, destino = RAIZ / rel, vitrine / rel
        if destino.is_file() and sha(origem) == sha(destino):
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origem, destino)
        if sha(origem) != sha(destino):        # cópia conferida, não presumida
            sys.exit("cópia divergiu logo após ser escrita: %s" % rel)
        escritos += 1
    for rel in remover:
        (vitrine / rel).unlink()
        apagados += 1

    # pastas que ficaram vazias depois das remoções
    for b, dirs, files in os.walk(vitrine, topdown=False):
        if Path(b) == vitrine:
            continue
        if not os.listdir(b) and ".git" not in Path(b).parts:
            os.rmdir(b)

    print("espelhado: %d arquivo(s) escrito(s), %d apagado(s)." % (escritos, apagados))
    print("\nconferindo o resultado:")
    r = conferir(vitrine)
    return 1 if r.erros else 0


# ----------------------------------------------------------------- números

# O README declara números sobre a própria vitrine. Cada entrada aqui diz onde
# lê-lo e o que ele tem de bater. Regex que NÃO casa reprova: declaração que
# sumiu do texto é declaração que ninguém mais confere.
DECLARACOES = [
    ("espelhados", re.compile(r"\*\*([\d.]+) arquivos espelhados\*\*")),
    ("fonte", re.compile(r"arquivos espelhados\*\* de um total de \*\*([\d.]+)\*\*")),
    ("pastas_excluidas", re.compile(r"são \*\*([\d.]+)\s*\n?pastas de campanha\*\*")),
    ("excluidos", re.compile(r"pastas de campanha\*\*, com\s*\n?\*\*([\d.]+) arquivos\*\*")),
    # Acrescentados em 2026-09-02. O README dizia "detector de 17 padrões" e a
    # lista tinha 15 — número em prosa que nenhum dos quatro anteriores conferia.
    # `achados_reais` entra pelo motivo oposto: ele TEM de ser zero, e declarar o
    # zero por extenso deixa a prosa reprovar junto com a trava se um dia não for.
    ("padroes", re.compile(r"detector de \*\*([\d.]+)\*\* padrões")),
    ("achados_reais",
     re.compile(r"Nos que entraram:\s*\n?\*\*([\d.]+) ocorrências? reais?\*\*")),
    # o custo da parcialidade: não reprova por si, mas o README não pode errá-lo
    ("links_quebrados",
     re.compile(r"Links quebrados: \*\*([\d.]+) de [\d.]+\*\*")),
    ("links", re.compile(r"Links quebrados: \*\*[\d.]+ de ([\d.]+)\*\*")),
]


def _num(s: str) -> int:
    return int(s.replace(".", "").replace(" ", ""))


def numeros(vitrine: Path) -> int:
    r = conferir(vitrine, verboso=False)
    readme = vitrine / "README.md"
    if not readme.is_file():
        print("README.md não encontrado em %s" % vitrine)
        return 2
    texto = readme.read_text(encoding="utf-8")

    print("o que a árvore MEDE, e o que o README DECLARA:\n")
    problemas = 0
    for chave, rx in DECLARACOES:
        medido = r.numeros[chave]
        m = rx.search(texto)
        if not m:
            print("  [FALHA] %-18s medido %-8s — declaração NÃO ENCONTRADA no "
                  "README. Regex que não casa é cegueira, não aprovação."
                  % (chave, medido))
            problemas += 1
            continue
        declarado = _num(m.group(1))
        if declarado == medido:
            print("  [ok]    %-18s %d" % (chave, medido))
        else:
            print("  [FALHA] %-18s medido %d, README declara %d"
                  % (chave, medido, declarado))
            problemas += 1

    if r.erros:
        print("\ne a conferência da própria vitrine tem %d problema(s) — "
              "rode `conferir`." % len(r.erros))
        problemas += len(r.erros)
    return 1 if problemas else 0


# ----------------------------------------------------------------- semear

def semear(vitrine: Path) -> int:
    """Deriva a lista de exclusões do estado ATUAL, uma vez, para ser revisada.

    Existe porque a lista nasceu de uma decisão humana em 2026-08-23 que nunca
    foi escrita como dado. Semear NÃO decide nada: fotografa o que já está fora
    e mede, por pasta, quantos arquivos carregam caminho absoluto — que é o
    motivo declarado da exclusão. Quem revisa vê o motivo com número ao lado.
    """
    if EXCLUSOES.exists():
        print("%s já existe. Semear de novo apagaria decisões já revisadas — "
              "edite o arquivo à mão." % EXCLUSOES.name)
        return 2
    if not vitrine.is_dir():
        print("vitrine não encontrada em %s" % vitrine)
        return 2

    publicados = set(arquivos_de(vitrine))
    candidatas: dict[str, str] = {}
    for base, dirs, _ in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in IGNORAR_SEMPRE]
        rel_base = Path(base).relative_to(RAIZ).as_posix() if Path(base) != RAIZ else ""
        # PODA: dentro de uma campanha já marcada não se procura outra. Sem isto
        # o resultado traz 96 entradas onde há 45 decisões — as 51 a mais são
        # campanhas ANINHADAS (candidatos, overlays, forjas), e cada uma seria
        # uma linha para revisar que não decide nada. A trava
        # EXCLUSAO_REDUNDANTE reprova exatamente isso; a poda é o conserto.
        if rel_base and sob_exclusao(rel_base, list(candidatas)):
            dirs[:] = []
            continue
        if Path(base).name != "evals":
            continue
        for d in list(dirs):
            rel = Path(base, d).relative_to(RAIZ).as_posix()
            if any(p.startswith(rel + "/") or p == rel for p in publicados):
                continue
            arquivos = [(Path(b, f), Path(b, f).relative_to(RAIZ).as_posix())
                        for b, _, fs in os.walk(RAIZ / rel) for f in fs]
            achados = varrer(arquivos)
            com_caminho = sum(len(v) for k, v in achados.items() if "caminho" in k
                              or "conta de usuario" in k)
            candidatas[rel] = (
                "campanha fora da vitrine: %d arquivo(s), %d casamento(s) de "
                "caminho absoluto ou conta local — reescrevê-los invalidaria "
                "custódia com SHA-256 chumbado." % (len(arquivos), com_caminho))
            dirs.remove(d)
    dados = {
        "motivo_geral": (
            "A vitrine publica a Estrutura MENOS as pastas de campanha. O motivo "
            "é único e verificável: elas carregam caminhos absolutos da máquina "
            "de origem, e parte delas é registro de custódia com SHA-256 "
            "chumbado — reescrever o caminho dentro deles alteraria evidência "
            "cujo digest está afirmado em outro lugar."),
        "arquivos_so_da_vitrine": ["README.md", ".gitignore"],
        "pastas": dict(sorted(candidatas.items())),
        "isencoes": [],
    }
    EXCLUSOES.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8", newline="\n")
    print("%s semeado com %d exclusão(ões). REVISE antes de espelhar."
          % (EXCLUSOES.name, len(candidatas)))
    return 0


# ----------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=["conferir", "espelhar", "numeros", "semear"])
    ap.add_argument("--vitrine", default=str(VITRINE_PADRAO))
    ap.add_argument("--aceitar-remocoes", action="store_true",
                    help="autoriza `espelhar` a apagar arquivos da vitrine")
    args = ap.parse_args(argv[1:])
    vitrine = Path(args.vitrine).resolve()

    if args.acao == "semear":
        return semear(vitrine)
    if args.acao == "numeros":
        return numeros(vitrine)
    if args.acao == "espelhar":
        return espelhar(vitrine, args.aceitar_remocoes)
    return 1 if conferir(vitrine).erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
