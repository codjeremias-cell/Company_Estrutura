"""Verificações que recebem UM PACOTE da Estrutura Final de Skills.

Implementa, uma vez só, os itens mecânicos do checklist de aceite da
`GUIA-DE-EXPANSAO-E-MIGRACAO.md`: frontmatter, limites de tamanho, interface do
runtime, arquivos obrigatórios, pasta de agentes e links internos.

Cada função devolve uma **lista de erros**; lista vazia significa conforme. Elas
não decidem o que é obrigatório — quem decide é o validador de cada pacote, que
passa os nomes, caminhos e limites.

**A fronteira com `verificacoes_estrutura.py` é o tipo do parâmetro** (ADR-015):
aqui entra um arquivo ou o diretório de um pacote; lá entra `structure_root` e a
travessia é da árvore inteira. `validate_links` fica deste lado apesar do
`rglob`, porque o `package_root` que ela varre **é** o pacote — o parâmetro
decide, não o verbo. `digest_de_arvore` também: recebe uma raiz qualquer e não é
checagem, é identidade.

As constantes de anatomia moram aqui, inclusive `SECOES_CONTRATO_GERENTE`, que só
o módulo de estrutura consome: são dados normativos, e mantê-las juntas preserva
a derivação `AGENTE = GERENTE - Compromisso` num lugar só, sem import circular.
"""

from __future__ import annotations

import hashlib
import ast
import json
import re
from pathlib import Path

__all__ = [
    "read_frontmatter",
    "validate_frontmatter",
    "validate_openai_yaml",
    "validate_required_files",
    "validate_agents_folder",
    "validate_links",
    "digest_de_arvore",
    "candidate_digest_de_arvore",
    "conferir_candidate_digest",
    "conferir_manifesto_do_candidato",
    "conferir_caminhos_alvo",
    "validate_contract_sections",
    "validate_skill_tokens",
    "SECOES_CONTRATO_GERENTE",
    "SECOES_CONTRATO_AGENTE",
    "TOKENS_SKILL_AGENTE",
    "chaves_do_frontmatter_conferem",
    "CHAVES_FRONTMATTER_OBRIGATORIAS",
    "CHAVES_FRONTMATTER_OPCIONAIS",
    "CAMPOS_DO_CRUZAMENTO",
    "montar_linha_de_cruzamento",
    "ler_rodada_da_missao",
    "cruzar_identidade_externa",
    "conferir_identidade_do_ledger",
]

AGENT_REQUIRED_FILES = ("SKILL.md", "CONTRATO-DE-COMPROMISSO.md", "agents/openai.yaml")

# Chaves do frontmatter de um `SKILL.md`, na ordem canônica.
#
# `name` e `description` são obrigatórias e nesta ordem. `allowed-tools` é
# **opcional** e, quando presente, vem depois — canonizado por decisão de
# Jeremias em 2026-08-11 ([ADR-025](../ceo-maestro/references/adr-025-allowed-tools-no-frontmatter.md)),
# porque restringir a ferramenta de um agente é **mecanismo de fronteira**: a
# proibição que hoje mora em prosa no contrato passa a ser executada pelo
# runtime. Antes disso a trava comparava a lista exata `["name", "description"]`
# e reprovava os 13 `SKILL.md` que a frente GradUP já havia declarado.
#
# O que **não** mudou, e é o ponto: qualquer chave fora desta lista continua
# reprovando. Isto é uma allowlist, não um afrouxamento — campo desconhecido no
# frontmatter segue sendo erro, e a ordem segue sendo conferida.
CHAVES_FRONTMATTER_OBRIGATORIAS = ("name", "description")
CHAVES_FRONTMATTER_OPCIONAIS = ("allowed-tools",)

# Estrutura normativa dos passos 7 e 8 da `GUIA-DE-EXPANSAO-E-MIGRACAO.md`.
#
# Ela existiu só em prosa até 2026-07-27, e a auditoria daquele dia mediu o
# preço disso: **15 de 66** contratos de agente conformes, e a trava anti-bypass
# que o guia chama de obrigatória ausente em **30** deles. Quatro anatomias
# rivais conviviam sem que nenhum validador percebesse — porque nenhum olhava.
#
# Estas constantes são o padrão; a *conferência* mora aqui, mas quem decide o
# que é obrigatório continua sendo o validador de cada pacote, que passa a lista.
SECOES_CONTRATO_GERENTE = (
    "Papel",
    "Compromisso",
    "Autoridade",
    "Entradas aceitas",
    "Saídas obrigatórias",
    "Evidências exigidas",
    "Obrigações",
    "Proibições",
    "Barreira de saída",
    "Fonte normativa",
    "Bloqueio por conflito",
    "Quebra de contrato",
)

# O agente não tem "Compromisso": o compromisso é da gerente, que responde pela
# entrega. O agente tem Papel e fronteira.
SECOES_CONTRATO_AGENTE = tuple(
    secao for secao in SECOES_CONTRATO_GERENTE if secao != "Compromisso"
)

TOKENS_SKILL_AGENTE = (
    "## Protocolo e trava anti-bypass",
    "## Fronteira exclusiva",
    "Assumir:",
    "**Não assumir**",
    "## Salvaguardas",
    "- **Não aciona:** ninguém.",
)


def read_frontmatter(path: Path) -> tuple[str, list[str]]:
    """Devolve (bloco do frontmatter, chaves na ordem em que aparecem)."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, flags=re.DOTALL)
    if not match:
        return "", []
    block = match.group(1)
    keys = [line.split(":", 1)[0].strip() for line in block.splitlines() if ":" in line]
    return block, keys


def chaves_do_frontmatter_conferem(chaves: list[str]) -> bool:
    """A regra da allowlist ordenada, em UM lugar so.

    Extraida de `validate_frontmatter` na tarefa 86 para poder ser EXERCITADA. Antes
    ela vivia embutida na leitura do arquivo, entao so era testavel contra a arvore
    real -- onde todo `SKILL.md` e conforme. Regra que so ve exemplo valido nunca
    reprova, e o verde dela nao significa nada.

    O autoteste chama ESTA funcao, e nao uma copia do `!=`: testar a copia mediria a
    reimplementacao, e mutar a de producao deixaria a bateria verde.
    """
    esperadas = list(CHAVES_FRONTMATTER_OBRIGATORIAS) + [
        opcional for opcional in CHAVES_FRONTMATTER_OPCIONAIS if opcional in chaves
    ]
    return chaves == esperadas


_AMOSTRAS_DO_FRONTMATTER = (
    # (rótulo, chaves lidas, deve_reprovar)
    ("obrigatórias na ordem, sem opcional", ["name", "description"], False),
    ("obrigatórias + a opcional canônica", ["name", "description", "allowed-tools"], False),
    ("chave DESCONHECIDA no fim", ["name", "description", "inventada"], True),
    ("chave desconhecida no MEIO", ["name", "inventada", "description"], True),
    ("chave REPETIDA", ["name", "description", "description"], True),
    ("ordem TROCADA nas obrigatórias", ["description", "name"], True),
    ("opcional ANTES das obrigatórias", ["allowed-tools", "name", "description"], True),
    ("obrigatória AUSENTE", ["name"], True),
)


def _autoteste_do_frontmatter() -> list[str]:
    """A allowlist prova que é allowlist — a cada chamada.

    **A assimetria que isto fecha (tarefa 86, medida em 2026-08-11 pelo próprio
    executor da canonização e declarada em vez de escondida atrás do verde).**
    REVERTER a canonização do ADR-025 é auto-detectável: os `SKILL.md` que
    declaram `allowed-tools` ficariam vermelhos na hora. Mas AFROUXÁ-LA — passar a
    ignorar chave desconhecida — não seria pego por nada, e o motor compartilhado
    devolvia o mesmo número com o módulo canonizado e com o mutante.

    O motivo é simples e vale para toda trava desta casa: `validate_frontmatter`
    só era exercitada contra a ÁRVORE REAL, onde todo arquivo é conforme. Uma
    regra que só vê exemplos válidos não pode reprovar nada — ela está sempre
    verde, e o verde não significa nada.

    O comentário de `CHAVES_FRONTMATTER_OPCIONAIS` promete, em prosa, que "campo
    desconhecido no frontmatter segue sendo erro, e a ordem segue sendo
    conferida". Prosa não reprova. Estas amostras reprovam.

    Cada uma isola UMA garantia: desconhecida no fim e no meio, repetida, ordem
    trocada, opcional fora de lugar, obrigatória ausente. Se a comparação virar
    `set()` ou `issubset()`, as quatro primeiras passam a ser aceitas e este
    autoteste fica vermelho — que é exatamente o mutante que hoje escapa.
    """
    erros: list[str] = []
    for rotulo, chaves, deve_reprovar in _AMOSTRAS_DO_FRONTMATTER:
        reprovou = not chaves_do_frontmatter_conferem(chaves)
        if reprovou != deve_reprovar:
            erros.append(
                "AUTOTESTE_DO_FRONTMATTER: a amostra %r %s, e devia %s — a "
                "allowlist deixou de ser allowlist, e chave desconhecida ou fora "
                "de ordem passaria a entrar em silêncio (ADR-025, tarefa 86)"
                % (rotulo, "reprovou" if reprovou else "passou",
                   "reprovar" if deve_reprovar else "passar")
            )
    return erros


def validate_frontmatter(
    path: Path,
    expected_name: str,
    *,
    max_lines: int = 500,
    max_description: int = 1024,
) -> list[str]:
    """Frontmatter com name/description (+ allowed-tools opcional), nome canônico e tamanho.

    A conferência é por **allowlist ordenada**, não por lista fixa: monta-se a
    sequência esperada com as obrigatórias e acrescenta-se cada opcional que o
    arquivo de fato declarou, na ordem canônica. Comparar a lista inteira mantém
    de graça as três garantias que a versão anterior tinha — chave desconhecida
    reprova, chave repetida reprova e ordem fora do canônico reprova — e só
    abre a porta para os nomes de `CHAVES_FRONTMATTER_OPCIONAIS`.
    """
    if not path.is_file():
        return [f"{expected_name}: SKILL.md ausente em {path}"]
    block, keys = read_frontmatter(path)
    if not block:
        return [f"{expected_name}: SKILL.md sem frontmatter válido"]

    # O detector prova que sabe reprovar ANTES de julgar este arquivo. Sem isto,
    # `validate_frontmatter` so ve `SKILL.md` conformes e fica verde por nao ter o
    # que acusar -- que e como afrouxar a allowlist passaria despercebido.
    errors: list[str] = list(_autoteste_do_frontmatter())
    if not chaves_do_frontmatter_conferem(keys):
        obrigatorias = "/".join(CHAVES_FRONTMATTER_OBRIGATORIAS)
        opcionais = "/".join(CHAVES_FRONTMATTER_OPCIONAIS)
        errors.append(
            f"{expected_name}: frontmatter deve ter {obrigatorias} nesta ordem, "
            f"opcionalmente seguidas de {opcionais}, recebeu {keys}"
        )
    if f"name: {expected_name}" not in block:
        errors.append(f"{expected_name}: name divergente do nome canônico")

    description = re.search(
        r'^description:\s*"(.*)"$', block, flags=re.MULTILINE | re.DOTALL
    )
    if not description:
        errors.append(f"{expected_name}: description deve ser string entre aspas")
    elif len(description.group(1)) > max_description:
        errors.append(
            f"{expected_name}: description excede {max_description} caracteres "
            f"({len(description.group(1))})"
        )

    line_count = len(path.read_text(encoding="utf-8").splitlines())
    if line_count > max_lines:
        errors.append(
            f"{expected_name}: SKILL.md excede {max_lines} linhas ({line_count})"
        )
    return errors


def validate_openai_yaml(
    path: Path,
    display_name: str,
    token: str,
    *,
    expected_short: str | None = None,
    min_length: int = 25,
    max_length: int = 64,
) -> list[str]:
    """Interface do runtime: display_name, short_description e token no prompt."""
    label = path.parent.parent.name
    if not path.is_file():
        return [f"{label}: agents/openai.yaml ausente"]

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if f'display_name: "{display_name}"' not in text:
        errors.append(f"{label}: display_name divergente")
    if token not in text:
        errors.append(f"{label}: default_prompt sem {token}")

    match = re.search(r'short_description:\s*"([^"]+)"', text)
    if not match:
        errors.append(f"{label}: sem short_description")
        return errors

    short = match.group(1)
    if not min_length <= len(short) <= max_length:
        errors.append(
            f"{label}: short_description fora de {min_length}–{max_length} "
            f"({len(short)})"
        )
    if expected_short is not None and short != expected_short:
        errors.append(f"{label}: short_description divergente do contrato")
    return errors


def validate_required_files(paths: list[Path], label: str = "arquivo") -> list[str]:
    return [f"{label} ausente: {path}" for path in paths if not path.is_file()]


def validate_agents_folder(
    agents_root: Path,
    expected_names: list[str],
    *,
    required_files: tuple[str, ...] = AGENT_REQUIRED_FILES,
) -> list[str]:
    """A pasta de agentes contém exatamente os nomes canônicos, cada um completo."""
    if not agents_root.is_dir():
        return [f"pasta {agents_root.name}/ ausente"]

    errors: list[str] = []
    found = sorted(item.name for item in agents_root.iterdir() if item.is_dir())
    if found != sorted(expected_names):
        errors.append(
            f"{agents_root.name}/ deve conter exatamente {sorted(expected_names)}, "
            f"contém {found}"
        )
    for name in expected_names:
        root = agents_root / name
        for required in required_files:
            if not (root / required).is_file():
                errors.append(f"agente {name} sem {required}")
    return errors


def digest_de_arvore(
    raiz: Path,
    *,
    excluir: tuple[str, ...] = ("__pycache__",),
) -> str:
    """Identidade reproduzível de uma árvore de arquivos — a receita, em código.

    **Por que existe.** Digest de árvore só serve como identidade se duas pessoas
    chegarem ao mesmo número. Em 2026-07-26 o `departamento-registros` publicou um
    digest de manifesto que ninguém reproduziu: doze variantes testadas, nenhuma
    bateu, porque a receita dizia "ordenadas por caminho" mas ordenava a linha
    formatada, sob comparador sensível a cultura. Em 2026-07-27, na primeira rodada
    de julgamento da frente 5, o operador repetiu o erro — fixou um
    `candidate_tree_sha256` calculado por receita ad-hoc, os Juízes não conseguiram
    reproduzi-lo e **barraram o candidato na porta**. O gate agiu certo; o número é
    que não era conferível. Número que ninguém consegue recalcular não é evidência.

    **A receita, fixada aqui e em nenhum outro lugar:**

    1. percorre `raiz` recursivamente, somente arquivos;
    2. descarta qualquer caminho que contenha um componente de `excluir`;
    3. **chave** = caminho relativo a `raiz`, com `/` como separador — nunca `\\`;
    4. **comparador** = ordinal, byte a byte, sobre a chave (o `sorted` do Python
       sobre `str` já é ordinal; nada de `locale`);
    5. **linha** = `f"{sha256_hex_do_conteudo}  {chave}"` — dois espaços, no formato
       do `sha256sum`, hash **antes** do caminho;
    6. **separador** = `\\n` entre linhas, e **terminador** `\\n` ao final da última;
    7. **codificação** do manifesto = UTF-8 sem BOM;
    8. o digest é o SHA-256 desse manifesto.

    O conteúdo de cada arquivo entra **em bytes crus**, sem normalizar fim de linha:
    a mesma árvore com CRLF e com LF dá digests diferentes, e isso é deliberado —
    quem precisa comparar entre cópias com EOL distinto tem um problema de
    normalização a resolver antes, não um digest a afrouxar.

    Retorna o hex de 64 caracteres, sem o prefixo `sha256:`.
    """
    if not raiz.is_dir():
        raise NotADirectoryError(f"digest de árvore: raiz ausente em {raiz}")

    linhas: list[str] = []
    for caminho in raiz.rglob("*"):
        if not caminho.is_file():
            continue
        relativo = caminho.relative_to(raiz)
        if any(parte in excluir for parte in relativo.parts):
            continue
        conteudo = hashlib.sha256(caminho.read_bytes()).hexdigest()
        linhas.append(f"{conteudo}  {relativo.as_posix()}")

    linhas.sort(key=lambda linha: linha.split("  ", 1)[1])
    manifesto = "".join(f"{linha}\n" for linha in linhas)
    return hashlib.sha256(manifesto.encode("utf-8")).hexdigest()


def candidate_digest_de_arvore(
    raiz: Path,
    *,
    excluir: tuple[str, ...] = ("__pycache__",),
) -> str:
    """O `candidate_digest` de um candidato multiarquivo — **a** receita, com prefixo.

    `digest_de_arvore` já fixava a receita em código desde 2026-07-27. O que
    faltava era **amarrar o campo à receita**: nada obrigava quem preenche
    `candidate_digest` a usá-la, e em 2026-08-01 a tarefa 14 fechou com **dois
    valores em disputa para o mesmo candidato** —

    - `sha256:93b3f7b1…` de `prova/emitir_ledger.py::digest_do_overlay`, que
      digere as **linhas declaradas do manifesto** (`caminho_alvo` +
      `sha256_depois`), não os bytes da árvore. É reprodutível, e mede outro
      objeto: a promessa, não a coisa.
    - `sha256:bfa279fb…` de um `os.walk` ad hoc do emissor de
      `08-EXECUTIVE-MISSION-JULGAMENTO.json`, sem receita publicada.

    Nenhum dos dois é o digest de árvore. Esta função é o endereço único do
    campo: produtor preenche com ela, consumidor confere com
    `conferir_candidate_digest`. Quem quiser digerir o manifesto em vez da
    árvore usa outro nome de campo — `manifest_digest` —, porque medir a
    declaração e medir os bytes são medidas diferentes e empatar os nomes foi
    o que produziu a disputa.

    Retorna com o prefixo `sha256:`, que é a forma que os schemas exigem.
    """
    return "sha256:" + digest_de_arvore(raiz, excluir=excluir)



def _conteudo_normalizado(caminho: Path) -> str:
    """SHA-256 hex do CONTEÚDO de um arquivo: BOM fora, `CRLF` vira `LF`.

    Arquivo que não decodifica como UTF-8 é binário e entra em bytes crus — a
    regra é fechada e não depende de extensão nem de lista.
    """
    dados = caminho.read_bytes()
    if dados.startswith(b"\xef\xbb\xbf"):
        dados = dados[3:]
    try:
        dados.decode("utf-8")
    except UnicodeDecodeError:
        return hashlib.sha256(dados).hexdigest()
    return hashlib.sha256(dados.replace(b"\r\n", b"\n")).hexdigest()


def digest_de_arvore_normalizado(
    raiz: Path,
    *,
    excluir: tuple[str, ...] = ("__pycache__",),
) -> str:
    """Identidade de árvore que **sobrevive ao checkout**.

    `digest_de_arvore` mede bytes crus de propósito, e por isso não serve como
    identidade de candidato num repositório com `core.autocrlf` ligado: em
    2026-08-05 a mesma árvore, no MESMO commit, deu `4abadd31…` na cópia de
    trabalho onde foi gerada (7 de 12 arquivos em CRLF) e `bc429bb4…` num
    worktree novo (12 de 12 em CRLF). O `.gitattributes` do cofre fixa `eol=lf`
    para os três espelhos de skills e **não** para `Estrutura Final de Skills/`.

    Um digest que muda sem que um caractere mude não endereça nada. Esta receita
    é idêntica à de `digest_de_arvore` em tudo — chave relativa com `/`,
    comparador ordinal sobre a chave, linha `f"{{hash}}  {{chave}}"`, separador e
    terminador `\n`, manifesto UTF-8 sem BOM — **exceto** no conteúdo de cada
    arquivo, que entra normalizado por `_conteudo_normalizado`.

    As duas continuam existindo porque medem coisas diferentes, e empatar os
    nomes foi o que produziu a disputa de 2026-08-01: esta mede **conteúdo**,
    aquela mede **os bytes deste checkout**. Identidade de candidato é a de cima.
    """
    if not raiz.is_dir():
        raise NotADirectoryError(f"digest de árvore: raiz ausente em {raiz}")

    linhas: list[str] = []
    for caminho in raiz.rglob("*"):
        if not caminho.is_file():
            continue
        relativo = caminho.relative_to(raiz)
        if any(parte in excluir for parte in relativo.parts):
            continue
        linhas.append(f"{_conteudo_normalizado(caminho)}  {relativo.as_posix()}")

    linhas.sort(key=lambda linha: linha.split("  ", 1)[1])
    manifesto = "".join(f"{linha}\n" for linha in linhas)
    return hashlib.sha256(manifesto.encode("utf-8")).hexdigest()


def candidate_digest_normalizado_de_arvore(
    raiz: Path,
    *,
    excluir: tuple[str, ...] = ("__pycache__",),
) -> str:
    """O `candidate_digest` de um candidato, na receita que sobrevive ao clone."""
    return "sha256:" + digest_de_arvore_normalizado(raiz, excluir=excluir)


def conferir_candidate_digest_normalizado(
    raiz: Path,
    declarado: str,
    *,
    excluir: tuple[str, ...] = ("__pycache__",),
) -> list[str]:
    """Lado do CONSUMIDOR, na receita normalizada. Divergência é erro nomeado."""
    if not isinstance(declarado, str) or not declarado.startswith("sha256:"):
        return [f"candidate_digest declarado sem o prefixo sha256:: {declarado!r}"]
    if not raiz.is_dir():
        return [f"candidate_digest não conferível: raiz ausente em {raiz}"]
    recomputado = candidate_digest_normalizado_de_arvore(raiz, excluir=excluir)
    if recomputado != declarado:
        return [
            "candidate_digest divergente: declarado "
            f"{declarado}, recomputado {recomputado} pela receita "
            "verificacoes_pacote.py::digest_de_arvore_normalizado"
        ]
    return []

def conferir_candidate_digest(
    raiz: Path,
    declarado: str,
    *,
    excluir: tuple[str, ...] = ("__pycache__",),
) -> list[str]:
    """Lado do CONSUMIDOR: recomputa sobre a árvore aberta e compara.

    Recomputar é obrigação de quem recebe, não cortesia. Divergência é **erro
    nomeado**, nunca ajuste silencioso e nunca conferência afirmada que não
    houve: o protocolo de auditoria proíbe as duas coisas.

    Devolve lista vazia quando confere; uma linha por defeito quando não.
    """
    erros: list[str] = []
    if not isinstance(declarado, str) or not declarado.startswith("sha256:"):
        erros.append(
            f"candidate_digest declarado sem o prefixo sha256:: {declarado!r}"
        )
        return erros
    if not raiz.is_dir():
        erros.append(f"candidate_digest não conferível: raiz ausente em {raiz}")
        return erros
    recomputado = candidate_digest_de_arvore(raiz, excluir=excluir)
    if recomputado != declarado:
        erros.append(
            "candidate_digest divergente: declarado "
            f"{declarado}, recomputado {recomputado} pela receita "
            "verificacoes_pacote.py::digest_de_arvore"
        )
    return erros


# TAREFA 48 — a seção existir não é a seção ser contável.
#
# Em 2026-08-03, 23 dos 66 contratos de agente tinham a `## Barreira de saída`
# escrita em PROSA. A consequência: um recibo honesto, com agente real e
# contagens exatas pela receita publicada, recebia `DENOMINADOR_ZERO` e
# `NONCOMPLIANT` — porque `contar_itens_do_contrato` conta LINHAS DE LISTA, e
# prosa conta zero. Os 23 foram convertidos e canonizados em 03/ago.
#
# **E o mecanismo ficou desprotegido.** Medido por execução em 2026-08-08:
# plantei uma barreira em prosa no `agente-modelagem-de-ameacas` e o validador
# do `departamento-seguranca` seguiu **190/190 verde**. A conversão dos 23 era
# reversível sem nada acusar — `conserto-de-instancia-nao-e-conserto-de-mecanismo`
# outra vez, e desta a instância já estava consertada e só o mecanismo faltava.
#
# O escopo desta exigência foi **medido antes de ser escrito**, nos 81 contratos:
# estas três seções, e só estas, já estão em lista em TODOS. As demais são prosa
# legítima em muitos — `Papel` é descrição em 81 de 81, `Fonte normativa` também.
# Uma trava que exigisse as doze não seria trava, seria campanha de trabalho
# disfarçada de trava. Aqui ela fixa o estado bom que já existe.
SECOES_CONTAVEIS = ("Autoridade", "Obrigações", "Barreira de saída")

_ITEM_DE_LISTA = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+\S")


def contar_itens_da_secao(texto: str, secao: str) -> int:
    """Itens de lista dentro de uma seção `## `, aceitando prefixo numerado."""
    dentro, itens = False, 0
    for linha in texto.splitlines():
        if linha.startswith("## "):
            dentro = (re.sub(r"^\d+\.\s*", "", linha[3:].strip()).casefold()
                      == secao.casefold())
            continue
        if dentro and _ITEM_DE_LISTA.match(linha):
            itens += 1
    return itens


def validate_contract_sections(
    path: Path,
    expected: tuple[str, ...],
    label: str,
) -> list[str]:
    """O contrato tem as seções canônicas, todas, **na ordem**, e as contáveis
    de fato contam.

    Conjunto certo em ordem errada ainda é contrato ilegível: quem lê procura a
    Barreira de saída depois das Proibições, não no meio das Entradas. Por isso
    a ordem é conferida, não só a presença.

    Numeração de prefixo (`## 3. Autoridade`) é aceita — a `GUIA` permite as
    duas formas e o que importa é o nome da seção.

    E presença não basta para as de `SECOES_CONTAVEIS`: a auditoria conta itens
    ali, então uma seção em prosa é substantiva para quem lê e **zero** para
    quem mede — ver o bloco acima.
    """
    if not path.is_file():
        return [f"{label}: CONTRATO-DE-COMPROMISSO.md ausente"]

    texto = path.read_text(encoding="utf-8")
    encontradas = [
        re.sub(r"^\d+\.\s*", "", linha[3:].strip())
        for linha in texto.splitlines()
        if linha.startswith("## ")
    ]

    faltando = [secao for secao in expected if secao not in encontradas]
    if faltando:
        return [f"{label}: seções ausentes no contrato: {faltando}"]

    posicoes = [encontradas.index(secao) for secao in expected]
    if posicoes != sorted(posicoes):
        fora = [
            secao
            for secao, anterior, atual in zip(expected[1:], posicoes, posicoes[1:])
            if atual < anterior
        ]
        return [f"{label}: seções fora da ordem canônica, a partir de {fora}"]

    em_prosa = [
        secao for secao in expected
        if secao in SECOES_CONTAVEIS and contar_itens_da_secao(texto, secao) == 0
    ]
    if em_prosa:
        return [
            f"{label}: seção(ões) {em_prosa} em prosa, sem itens contáveis — "
            f"a auditoria conta itens ali e prosa conta ZERO, então o recibo "
            f"honesto deste agente receberia DENOMINADOR_ZERO"
        ]
    return []


def validate_skill_tokens(
    path: Path,
    tokens: tuple[str, ...],
    label: str,
) -> list[str]:
    """A `SKILL.md` traz os tokens literais que a `GUIA` exige.

    A conferência é por string exata **de propósito**: variante de um caractere
    — `**Não assumir:**` com os dois-pontos dentro do negrito, `ninguém;` no
    lugar de `ninguém.` — passa despercebida na leitura e some na conferência
    mecânica. Foram 28 casos assim em quatro pacotes, todos corrigidos em
    2026-07-27.
    """
    if not path.is_file():
        return [f"{label}: SKILL.md ausente"]

    texto = path.read_text(encoding="utf-8")
    faltando = [token for token in tokens if token not in texto]
    return [f"{label}: tokens normativos ausentes: {faltando}"] if faltando else []


def validate_links(
    package_root: Path,
    *,
    exclude: list[Path] | None = None,
) -> list[str]:
    """Todo link markdown interno do pacote resolve em arquivo existente.

    `exclude` pula subárvores que são pacotes próprios, com validador próprio —
    assim um Departamento filho quebrado não reprova o pacote do superior.
    """
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    skipped = [item.resolve() for item in (exclude or [])]
    errors: list[str] = []
    for path in sorted(package_root.rglob("*.md")):
        if any(path.resolve().is_relative_to(item) for item in skipped):
            continue
        text = path.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                errors.append(f"link quebrado em {path.name}: {target}")
    return errors


# ---------------------------------------------------------------------------
# RODADA 5 — o cruzamento de identidade não pode cruzar a linha CONSIGO MESMA
# ---------------------------------------------------------------------------
#
# `OI-03`, produzido por origem independente em 2026-08-02, mediu o defeito: o
# `candidateIdentityCrosscheck` do schema da Evolução carrega a identidade numa
# linha só e o `pattern` obriga três pares a serem iguais **dentro da linha**.
# Isso rejeita uma linha incoerente. Não rejeita uma linha COERENTE que fale de
# outro candidato, de outra rodada ou de outro digest — e uma linha é escrita
# por quem quiser, não é derivada de nada.
#
# Os Juízes disseram a frase que fecha o assunto: *enquanto o confronto viver na
# função que DERIVA a linha, o instrumento testa o produtor honesto, não a
# trava.* Aqui o confronto vive fora dela. A linha é confrontada com:
#
#   1. os CAMPOS IRMÃOS do próprio ledger — `causal.round`, `plan.causal.round`,
#      `causal.candidate_digest`. São TRÊS campos, e o custo de forjar sobe de
#      uma edição para quatro — a linha mais os três irmãos;
#   2. a MISSÃO EM DISCO, que declara a rodada. Externa ao artefato inteiro;
#   3. a ÁRVORE DO CANDIDATO EM DISCO, redigerida pela receita oficial. Externa
#      ao artefato inteiro.
#
# RODADA 6 — AFIRMAÇÃO DE CUSTO CORRIGIDA, POR ACHADO DE ORIGEM INDEPENDENTE.
#
# Este parágrafo dizia, em (1), que "o forjador teria de editar o artefato
# inteiro, não uma string". `OI5-08` (c1) mostrou que era exagero: o cruzamento
# confronta a linha com TRÊS campos irmãos, e editar três campos não é editar o
# artefato inteiro. A afirmação também era de CUSTO SEM NÚMERO, na mesma rodada
# em que `inspecao_executada.py` declara que "medida sem número é opinião" e em
# que "encarece muito" foi retirada por esse exato motivo. O número entra e o
# exagero sai.
#
# Limite declarado, e ele é o teto desta frente: (2) e (3) são arquivos da mesma
# árvore que o produtor escreve. Isso não é âncora fora do pacote — é fonte fora
# da LINHA, que é o que a rodada 5 se propôs a fechar. O teto é `R11`, publicado
# no envelope da Auditoria em `compliance_claim.ceiling_ref`.
#
# RODADA 6 — REFERÊNCIA CORRIGIDA. Esta linha citava `L1`, identificador que não
# existe em lugar nenhum do overlay: uma única ocorrência, e o leitor que a
# seguisse para achar o limite não achava nada. `OI5-08` (c2). O teto publicado
# sempre foi `R11`.

CAMPOS_DO_CRUZAMENTO = (
    "candidate_id",
    "candidate_root_ref",
    "declared_digest",
    "recomputed_digest",
    "round_declared",
    "plan_round",
    "mission_round",
)


def montar_linha_de_cruzamento(bloco: dict) -> str:
    """A forma canônica da `line`, montada a partir dos CAMPOS do bloco.

    Existe para que a linha deixe de ser texto livre: se ela não for exatamente
    a composição dos campos irmãos, `cruzar_identidade_externa` acusa. Sem isso
    a linha pode afirmar uma coisa e os campos ao lado, outra — e o `pattern`
    do schema, que só olha a linha, aprova.
    """
    return (
        f"candidate={bloco.get('candidate_id')}"
        f" root={bloco.get('candidate_root_ref')}"
        f" declared={bloco.get('declared_digest')}"
        f" recomputed={bloco.get('recomputed_digest')}"
        f" round={bloco.get('round_declared')}"
        f" plan_round={bloco.get('plan_round')}"
        f" mission_round={bloco.get('mission_round')}"
    )


def ler_rodada_da_missao(caminho: Path) -> tuple[int | None, str]:
    """Abre a missão EM DISCO e devolve a rodada que ela declara.

    Fonte externa ao ledger inteiro. Devolve `(rodada, motivo)`; `rodada` é
    `None` quando não há missão para abrir, e o motivo diz por quê — ausência
    permanece ausência, nunca vira número.
    """
    if not caminho.is_file():
        return None, f"missão ausente em disco: {caminho}"
    try:
        artefato = json.loads(caminho.read_text(encoding="utf-8"))
    except (ValueError, OSError) as erro:
        return None, f"missão ilegível em {caminho}: {erro}"
    rodada = (artefato.get("causal") or {}).get("round")
    if not isinstance(rodada, int) or isinstance(rodada, bool):
        return None, f"missão sem causal.round inteiro em {caminho}"
    return rodada, "lida do disco"


def cruzar_identidade_externa(
    ledger: dict,
    *,
    rodada_da_missao: int | None,
    digest_em_disco: str | None,
    motivo_da_missao: str = "",
    motivo_do_digest: str = "",
) -> list[str]:
    """Confronta `candidate_identity` com fontes EXTERNAS À LINHA.

    Nenhum argumento é opcional por aridade: `rodada_da_missao` e
    `digest_em_disco` são obrigatórios como palavra-chave, e `None` neles é um
    **erro nomeado**, não um desligamento silencioso. Foi a opcionalidade por
    aridade que produziu o achado `A1` da rodada 1 desta frente.

    Devolve lista vazia quando tudo cruza; uma linha por divergência.
    """
    erros: list[str] = []
    bloco = ledger.get("candidate_identity")
    if not isinstance(bloco, dict):
        return ["candidate_identity ausente ou não é objeto"]

    faltando = [campo for campo in CAMPOS_DO_CRUZAMENTO if campo not in bloco]
    if faltando:
        erros.append(f"candidate_identity incompleto, faltam {faltando}")

    # (0) a LINHA tem de ser a composição dos campos irmãos. Linha que afirma
    #     algo que os campos não afirmam é a forma pura do defeito.
    canonica = montar_linha_de_cruzamento(bloco)
    if bloco.get("line") != canonica:
        erros.append(
            "LINHA NÃO É A COMPOSIÇÃO DOS CAMPOS — grava"
            f" {bloco.get('line')!r} e os campos irmãos compõem {canonica!r}"
        )

    causal = ledger.get("causal") or {}
    plano = (ledger.get("plan") or {}).get("causal") or {}

    # (1) campos irmãos do próprio artefato
    if bloco.get("declared_digest") != causal.get("candidate_digest"):
        erros.append(
            "DIVERGE DO CAMPO IRMÃO — declared_digest"
            f" {bloco.get('declared_digest')!r} e causal.candidate_digest"
            f" {causal.get('candidate_digest')!r}"
        )
    if bloco.get("round_declared") != causal.get("round"):
        erros.append(
            "DIVERGE DO CAMPO IRMÃO — round_declared"
            f" {bloco.get('round_declared')!r} e causal.round"
            f" {causal.get('round')!r}"
        )
    if bloco.get("plan_round") != plano.get("round"):
        erros.append(
            "DIVERGE DO CAMPO IRMÃO — plan_round"
            f" {bloco.get('plan_round')!r} e plan.causal.round"
            f" {plano.get('round')!r}"
        )

    # (2) missão em disco — externa ao artefato inteiro
    if rodada_da_missao is None:
        erros.append(
            "MISSÃO NÃO CONFERIDA — a rodada declarada não foi confrontada com a"
            f" missão em disco: {motivo_da_missao or 'sem motivo declarado'}"
        )
    elif bloco.get("mission_round") != rodada_da_missao:
        erros.append(
            "DIVERGE DA MISSÃO EM DISCO — mission_round"
            f" {bloco.get('mission_round')!r} e a missão declara"
            f" {rodada_da_missao!r}"
        )
    elif bloco.get("round_declared") != rodada_da_missao:
        erros.append(
            "DIVERGE DA MISSÃO EM DISCO — round_declared"
            f" {bloco.get('round_declared')!r} e a missão declara"
            f" {rodada_da_missao!r}"
        )

    # (3) árvore do candidato em disco — externa ao artefato inteiro
    if digest_em_disco is None:
        erros.append(
            "ÁRVORE NÃO CONFERIDA — o digest recomputado não foi confrontado com"
            f" a árvore em disco: {motivo_do_digest or 'sem motivo declarado'}"
        )
    else:
        if bloco.get("recomputed_digest") != digest_em_disco:
            erros.append(
                "DIVERGE DA ÁRVORE EM DISCO — recomputed_digest"
                f" {bloco.get('recomputed_digest')!r} e a receita"
                " verificacoes_pacote.py::digest_de_arvore sobre"
                f" {bloco.get('candidate_root_ref')!r} dá {digest_em_disco!r}"
            )
        # A AFIRMAÇÃO MAIS FORTE, e a que rejeita o ledger real da rodada 3:
        # a ÁRVORE que está na raiz declarada tem de ser o candidato que o
        # artefato diz julgar. Aqui não há linha nenhuma no meio — de um lado
        # os bytes em disco, do outro `causal.candidate_digest`.
        #
        # O `37-EVOLUTION-LEDGER-R3` declarava o digest do `cand-B` enquanto o
        # julgado era o `cand-C`, e VALIDAVA COM ZERO ERROS porque nada cruzava.
        # Com a linha derivada honestamente, o `pattern` o pega; com a linha
        # FORJADA e auto-consistente, o `pattern` o aceita e só esta comparação
        # o recusa.
        if digest_em_disco != causal.get("candidate_digest"):
            erros.append(
                "ÁRVORE EM DISCO NÃO É O CANDIDATO DECLARADO —"
                f" {bloco.get('candidate_root_ref')!r} redigere"
                f" {digest_em_disco!r} e causal.candidate_digest declara"
                f" {causal.get('candidate_digest')!r}"
            )
    return erros


def conferir_identidade_do_ledger(ledger: dict, raiz_da_campanha: Path) -> list[str]:
    """Driver de disco de `cruzar_identidade_externa`.

    Abre a missão que o bloco nomeia e a pasta do candidato que ele aponta, as
    duas sob `raiz_da_campanha`, e chama o confronto. Fuga de diretório é
    recusada aqui como em toda a frente: referência absoluta ou que escape da
    raiz não vira leitura.
    """
    bloco = ledger.get("candidate_identity")
    if not isinstance(bloco, dict):
        return ["candidate_identity ausente ou não é objeto"]

    raiz_da_campanha = Path(raiz_da_campanha).resolve()

    def sob_a_raiz(referencia) -> tuple[Path | None, str]:
        if not isinstance(referencia, str) or not referencia.strip():
            return None, f"referência vazia: {referencia!r}"
        bruto = Path(referencia)
        if bruto.is_absolute():
            return None, f"referência absoluta não é aceita: {referencia}"
        alvo = (raiz_da_campanha / bruto).resolve()
        try:
            alvo.relative_to(raiz_da_campanha)
        except ValueError:
            return None, f"referência escapa da raiz da campanha: {referencia}"
        return alvo, ""

    caminho_da_missao, motivo_missao = sob_a_raiz(bloco.get("mission_ref"))
    if caminho_da_missao is None:
        rodada_da_missao = None
    else:
        rodada_da_missao, motivo_missao = ler_rodada_da_missao(caminho_da_missao)

    caminho_do_candidato, motivo_digest = sob_a_raiz(bloco.get("candidate_root_ref"))
    if caminho_do_candidato is None:
        digest_em_disco = None
    elif not caminho_do_candidato.is_dir():
        digest_em_disco = None
        motivo_digest = f"pasta do candidato ausente: {bloco.get('candidate_root_ref')}"
    else:
        digest_em_disco = candidate_digest_de_arvore(caminho_do_candidato)
        motivo_digest = "recomputado sobre a árvore em disco"

    return cruzar_identidade_externa(
        ledger,
        rodada_da_missao=rodada_da_missao,
        digest_em_disco=digest_em_disco,
        motivo_da_missao=motivo_missao,
        motivo_do_digest=motivo_digest,
    )


# ---------------------------------------------------------------------------
# RODADA 8 — O MANIFESTO TEM DE DESCREVER O PRÓPRIO CANDIDATO
# ---------------------------------------------------------------------------
#
# `C07` da rodada 7, com falha crítica: o `manifest.json` entregue como `cand-G`
# era **byte-idêntico ao do `cand-F`**, declarava `candidate_id` do F e 8 dos 13
# `sha256_depois` eram do overlay do F. E a árvore do `cand-G` **reproduzia** —
# porque o manifesto mentiroso é membro dela. `digest_de_arvore` autentica o
# conjunto de bytes entregue, inclusive a declaração falsa que viaja dentro dele.
#
# Esta trava é de FAMÍLIA `recomputacao`: ela não confere o conjunto, confere o
# VALOR. Para cada entrada do manifesto reabre o arquivo entregue, recomputa o
# SHA-256 e exige igualdade com `sha256_depois`; e exige que `candidate_id` seja
# o nome do diretório que contém o manifesto — nome que a trava DERIVA do
# caminho, nunca lê do artefato conferido.
#
# O irmão desta rodada fecha o mesmo buraco por BIJEÇÃO de conjuntos. Os dois
# mecanismos são diferentes de propósito: um defeito no denominador de um não é
# um defeito no outro, e é isso que dá raio de discriminação.
MANIFESTO_SEM_MANIFESTO = "SEM_MANIFESTO"
MANIFESTO_CONFERIDO = "CONFERIDO"
MANIFESTO_DIVERGENTE = "DIVERGENTE"


# ---------------------------------------------------------------------------
# RODADA 9 — `caminho_alvo` É O CAMPO COM AUTORIDADE DE ESCRITA, E NINGUÉM O LIA
# ---------------------------------------------------------------------------
#
# `C03` da rodada 8, medido pelos Juízes: *"`caminho_alvo`, o campo que o próprio
# manifesto define como destino de escrita na Estrutura viva, não é conferido por
# nenhuma das duas famílias, e `candidate_manifest_status: CONFERIDO` viaja ao
# CEO por cima dele."* A `regra_de_aplicacao` do manifesto diz, com todas as
# letras, *"copiar cada `arquivo_no_candidato` para `caminho_alvo` na raiz da
# Estrutura"* — é o campo que decide o que será SOBRESCRITO. O ataque que passou:
# trocar o `caminho_alvo` do ADR-017 por `regras-de-ouro/REGRAS-DE-OURO.md` e
# emitir COMPLIANT.
#
# Campo com autoridade que ninguém lê é autoridade sem conferência.
#
# O que se confere é DERIVADO, não declarado: a própria regra de aplicação diz
# que `arquivo_no_candidato` é `<overlay>/<caminho_alvo><sufixo>`. Isso é uma
# BIJEÇÃO, e bijeção se confere sem acreditar em ninguém.
PASTA_DO_OVERLAY = "overlay"
SUFIXO_DO_CANDIDATO = ".candidate"
CAMINHO_ALVO_AUSENTE = "CAMINHO_ALVO_AUSENTE"
CAMINHO_ALVO_ESCAPA_DA_ESTRUTURA = "CAMINHO_ALVO_ESCAPA_DA_ESTRUTURA"
CAMINHO_ALVO_NAO_DERIVA_DO_ENTREGUE = "CAMINHO_ALVO_NAO_DERIVA_DO_ENTREGUE"
CAMINHO_ALVO_DUPLICADO = "CAMINHO_ALVO_DUPLICADO"


def _destino_escapa(normal: str) -> bool:
    """Destino que sai da raiz da Estrutura — a forma pura do abuso de escrita."""
    if not normal or normal.startswith("/") or normal.startswith("\\"):
        return True
    if len(normal) > 1 and normal[1] == ":":
        return True
    return ".." in normal.split("/")


def conferir_caminhos_alvo(
    entradas: list, raiz_do_candidato: Path
) -> list[str]:
    """O destino de escrita, conferido por RECOMPUTAÇÃO do valor.

    Família `recomputacao`: para cada entrada, RECOMPÕE o `arquivo_no_candidato`
    que o `caminho_alvo` implica, pela regra de aplicação do próprio manifesto, e
    exige igualdade com o entregue. Um `caminho_alvo` trocado deixa de compor o
    arquivo que está no pacote, e a igualdade cai.

    A irmã fecha o mesmo buraco por BIJEÇÃO de conjuntos. Um defeito no
    denominador de uma não é defeito na outra — é isso que dá raio.
    """
    erros: list[str] = []
    vistos: dict[str, str] = {}
    for entrada in entradas:
        if not isinstance(entrada, dict):
            continue
        entregue = entrada.get("arquivo_no_candidato")
        destino = entrada.get("caminho_alvo")
        if not isinstance(destino, str) or not destino.strip():
            erros.append(
                f"{CAMINHO_ALVO_AUSENTE}: {entregue!r} não declara para ONDE"
                " será escrito na Estrutura viva"
            )
            continue
        normal = destino.replace("\\", "/")
        if _destino_escapa(normal):
            erros.append(
                f"{CAMINHO_ALVO_ESCAPA_DA_ESTRUTURA}: {destino!r} sai da raiz da"
                " Estrutura — destino com autoridade de escrita fora do alvo"
            )
            continue
        # As DUAS formas do entregue, e a tolerância é só quanto ao SUFIXO.
        # O pacote real usa `.candidate`; o pacote mínimo da bateria, não. O
        # caminho em si não tem tolerância nenhuma: trocar o destino continua
        # caindo nas duas formas, e foi o controle honesto da própria bateria
        # que mediu isto — `cand-P-honesto` saiu DIVERGENTE na primeira versão
        # desta função, por um sufixo que eu havia fixado sem olhar.
        esperados = (
            f"{PASTA_DO_OVERLAY}/{normal}{SUFIXO_DO_CANDIDATO}",
            f"{PASTA_DO_OVERLAY}/{normal}",
        )
        real = entregue.replace("\\", "/") if isinstance(entregue, str) else entregue
        if real not in esperados:
            erros.append(
                f"{CAMINHO_ALVO_NAO_DERIVA_DO_ENTREGUE}: o destino {destino!r}"
                f" implica {esperados[0]!r} pela regra de aplicação, e o pacote"
                f" entrega {real!r}"
            )
        if normal in vistos:
            erros.append(
                f"{CAMINHO_ALVO_DUPLICADO}: {destino!r} é destino de"
                f" {vistos[normal]!r} e de {real!r} — dois arquivos escrevendo"
                " no mesmo lugar da Estrutura viva"
            )
        vistos[normal] = real
    return erros


def conferir_manifesto_do_candidato(raiz_do_candidato: Path | None) -> dict:
    """O manifesto entregue descreve o próprio candidato? Por RECOMPUTAÇÃO.

    Três desfechos, todos nomeados:

    - `SEM_MANIFESTO` — a raiz não é um pacote de candidato entregue (é o caso da
      rodada de prova, cuja raiz é uma subárvore viva). **Não é conformidade**, e
      o limite está declarado em `LIMITES-DECLARADOS-EM-PROSA.md`;
    - `CONFERIDO` — todo `sha256_depois` recomputa igual sobre os bytes
      entregues, e `candidate_id` é o nome do diretório;
    - `DIVERGENTE` — qualquer das duas falha, com o erro nomeado arquivo a
      arquivo. O emissor bloqueia e não grava nada.
    """
    if raiz_do_candidato is None or not raiz_do_candidato.is_dir():
        return {
            "status": MANIFESTO_SEM_MANIFESTO,
            "reason": (
                "não há raiz de candidato aberta: nada a conferir, e ausência de"
                " conferência permanece ausência"
            ),
            "receita": "_compartilhado/verificacoes_pacote.py::conferir_manifesto_do_candidato",
            "mecanismo": "recomputacao",
            "arquivos_conferidos": 0,
            "errors": [],
        }
    manifesto = raiz_do_candidato / "manifest.json"
    if not manifesto.is_file():
        return {
            "status": MANIFESTO_SEM_MANIFESTO,
            "reason": (
                f"{raiz_do_candidato.name} não traz manifest.json: a raiz não é um"
                " pacote de candidato entregue, e nada foi conferido"
            ),
            "receita": "_compartilhado/verificacoes_pacote.py::conferir_manifesto_do_candidato",
            "mecanismo": "recomputacao",
            "arquivos_conferidos": 0,
            "errors": [],
        }
    erros: list[str] = []
    try:
        dados = json.loads(manifesto.read_text(encoding="utf-8"))
    except (OSError, ValueError) as erro:
        return {
            "status": MANIFESTO_DIVERGENTE,
            "reason": f"manifest.json ilegível: {erro}",
            "receita": "_compartilhado/verificacoes_pacote.py::conferir_manifesto_do_candidato",
            "mecanismo": "recomputacao",
            "arquivos_conferidos": 0,
            "errors": [f"manifest.json ilegível: {erro}"],
        }

    # O nome é DERIVADO do caminho. Ler o nome do próprio artefato conferido
    # seria compará-lo consigo mesmo, que é o defeito que a rodada 5 fechou em
    # `cruzar_identidade_externa`.
    esperado = raiz_do_candidato.name
    declarado = dados.get("candidate_id")
    if declarado != esperado:
        erros.append(
            f"candidate_id declarado {declarado!r} não é o nome do diretório"
            f" entregue {esperado!r}: o manifesto descreve OUTRO candidato"
        )

    entradas = dados.get("arquivos")
    if not isinstance(entradas, list) or not entradas:
        erros.append("manifest.arquivos: lista obrigatória e não vazia")
        entradas = []

    conferidos = 0
    for entrada in entradas:
        if not isinstance(entrada, dict):
            erros.append(f"entrada de arquivo inválida: {entrada!r}")
            continue
        relativo = entrada.get("arquivo_no_candidato")
        declarado_hash = entrada.get("sha256_depois")
        if not isinstance(relativo, str) or not isinstance(declarado_hash, str):
            erros.append(f"entrada sem arquivo_no_candidato/sha256_depois: {entrada!r}")
            continue
        alvo = raiz_do_candidato / relativo
        if not alvo.is_file():
            erros.append(f"{relativo}: declarado no manifesto e AUSENTE do pacote")
            continue
        real = "sha256:" + hashlib.sha256(alvo.read_bytes()).hexdigest()
        conferidos += 1
        if real != declarado_hash:
            erros.append(
                f"{relativo}: sha256_depois declarado {declarado_hash[:23]}… e os"
                f" bytes entregues dão {real[:23]}…"
            )

    erros.extend(conferir_caminhos_alvo(entradas, raiz_do_candidato))

    if erros:
        return {
            "status": MANIFESTO_DIVERGENTE,
            "reason": (
                f"o manifesto de {esperado} não descreve o próprio candidato:"
                f" {len(erros)} divergência(s)"
            ),
            "receita": "_compartilhado/verificacoes_pacote.py::conferir_manifesto_do_candidato",
            "mecanismo": "recomputacao",
            "arquivos_conferidos": conferidos,
            "errors": erros,
        }
    return {
        "status": MANIFESTO_CONFERIDO,
        "reason": (
            f"o manifesto de {esperado} descreve o próprio candidato:"
            f" {conferidos} arquivo(s) recomputado(s) e idênticos ao declarado"
        ),
        "receita": "_compartilhado/verificacoes_pacote.py::conferir_manifesto_do_candidato",
        "mecanismo": "recomputacao",
        "arquivos_conferidos": conferidos,
        "errors": [],
    }


# ---------------------------------------------------------------------------
# TAREFA 103 — overlay de arquivo inteiro é um diff com data de validade
# ---------------------------------------------------------------------------
#
# Nesta casa, promover um candidato SUBSTITUI ARQUIVOS INTEIROS. Isso é seguro
# enquanto a promoção é imediata. Candidato que espera vira **reversão vestida
# de promoção**, e nada no modelo avisa.
#
# O CASO QUE REVELOU, medido em 2026-08-22: o `cand-A2-analysis-return-rebase`
# da tarefa 46 foi rebaseado em 2026-08-03 e o próprio manifesto declara
# `arquivos[].sha256_antes` para cada um dos nove alvos. A base bate hoje em
# **zero de nove** — e aplicar o overlay do `ceo-maestro` (+714 −1528 linhas)
# apagaria OITO travas instaladas depois, cinco delas do mesmo dia da medição.
#
# A LACUNA É PEQUENA E O ESTRAGO É GRANDE: o manifesto **carrega** a base e
# **nada a confere**. A evidência existe, está correta, e nunca é lida — mesmo
# esqueleto de `contrato-no-schema-nao-chega-a-quem-cumpre`.
#
# DIMENSÃO MEDIDA, e ela decide o desenho: 2846 arquivos `.candidate` na
# árvore, 989 com alvo vivo, e **333 apagariam ao menos uma trava viva**. Um
# portão que reprovasse os 333 seria parede, não portão — e seria o
# `gate-que-barra-evidencia-boa`, porque esses 333 são **fixtures de campanha**,
# não fila de promoção. O critério estrutural da tarefa 96 já separa os dois.
#
# Por isso o que mora aqui é o **instrumento**, executável e exercitado, para
# quem vai promover rodar ANTES. A política ("não promova com base morta") é
# do protocolo; o número que a sustenta é este código.
def conferir_base_do_candidato(
    arquivos: list[dict],
    digest_atual,
) -> tuple[list[str], list[str], list[str]]:
    """(bases vivas, bases mortas, alvos sem base declarada).

    `digest_atual` recebe o `caminho_alvo` e devolve o digest de hoje, ou
    `None` se o alvo não existe mais. É injetado de propósito: é o que permite
    o autoteste exercitar ESTA função em vez de reimplementá-la — o defeito
    `teste-que-exercita-a-reimplementacao`, que custou três repetições num só
    dia a esta casa.

    Comparação por PERTINÊNCIA, não por igualdade de string: o manifesto pode
    declarar `sha256:abc…` e o instrumento devolver `abc…` cru ou normalizado.
    Quem chama passa o conjunto de leituras plausíveis; aqui basta uma bater.
    """
    vivas: list[str] = []
    mortas: list[str] = []
    sem_base: list[str] = []
    for item in arquivos:
        if not isinstance(item, dict):
            continue
        alvo = item.get("caminho_alvo")
        if not isinstance(alvo, str):
            continue
        declarado = item.get("sha256_antes")
        if item.get("estado") == "NOVO" or not declarado:
            sem_base.append(alvo)
            continue
        esperado = str(declarado).split(":")[-1]
        hoje = digest_atual(alvo)
        candidatos_de_hoje = (
            set() if hoje is None
            else {str(h).split(":")[-1] for h in
                  (hoje if isinstance(hoje, (set, list, tuple)) else [hoje])}
        )
        (vivas if esperado in candidatos_de_hoje else mortas).append(alvo)
    return vivas, mortas, sem_base


def promocao_e_segura(
    arquivos: list[dict],
    digest_atual,
) -> list[str]:
    """Erros que IMPEDEM promover este candidato. Vazio = pode promover."""
    vivas, mortas, sem_base = conferir_base_do_candidato(arquivos, digest_atual)
    erros: list[str] = []
    if mortas:
        erros.append(
            "BASE MORTA em %d de %d alvo(s) com base declarada: %s. Promover "
            "agora não é promover — é REVERTER o alvo para o estado de quando "
            "o candidato nasceu, apagando tudo que entrou depois sem que nada "
            "acuse."
            % (len(mortas), len(mortas) + len(vivas), ", ".join(sorted(mortas)[:4])
               + (" …" if len(mortas) > 4 else ""))
        )
    if not vivas and not mortas:
        erros.append(
            "NENHUMA BASE DECLARADA: o manifesto não traz `sha256_antes` em "
            "alvo nenhum, então não há como saber contra o que este overlay "
            "foi construído. Ausência de base não é base intacta."
        )
    return erros


def travas_que_o_overlay_apagaria(
    texto_vivo: str,
    texto_do_overlay: str,
    marcas: tuple[str, ...],
) -> list[str]:
    """Marcas presentes no arquivo VIVO e ausentes no overlay que o substitui.

    É a segunda metade do estrago, e ela é independente da base: um overlay
    pode ter base viva num alvo e mesmo assim apagar uma trava noutro.
    """
    return [m for m in marcas if m in texto_vivo and m not in texto_do_overlay]


_AMOSTRAS_DA_BASE = (
    # (nome, arquivos, digest_de_hoje, espera_erro)
    (
        "base intacta não impede promoção",
        [{"caminho_alvo": "a.py", "sha256_antes": "sha256:aaa"}],
        {"a.py": "aaa"},
        False,
    ),
    (
        "base morta impede",
        [{"caminho_alvo": "a.py", "sha256_antes": "sha256:aaa"}],
        {"a.py": "bbb"},
        True,
    ),
    (
        "alvo que sumiu conta como base morta, não como silêncio",
        [{"caminho_alvo": "a.py", "sha256_antes": "sha256:aaa"}],
        {},
        True,
    ),
    (
        "UMA base morta entre várias vivas já impede",
        [{"caminho_alvo": "a.py", "sha256_antes": "sha256:aaa"},
         {"caminho_alvo": "b.py", "sha256_antes": "sha256:bbb"},
         {"caminho_alvo": "c.py", "sha256_antes": "sha256:ccc"}],
        {"a.py": "aaa", "b.py": "bbb", "c.py": "XXX"},
        True,
    ),
    (
        "alvo NOVO não tem base e não é acusado por isso",
        [{"caminho_alvo": "a.py", "sha256_antes": "sha256:aaa"},
         {"caminho_alvo": "novo.md", "estado": "NOVO"}],
        {"a.py": "aaa"},
        False,
    ),
    (
        "manifesto SEM base nenhuma impede — ausência não é intacta",
        [{"caminho_alvo": "novo.md", "estado": "NOVO"}],
        {},
        True,
    ),
    (
        "o digest de hoje pode chegar cru OU normalizado; basta um bater",
        [{"caminho_alvo": "a.py", "sha256_antes": "sha256:norm"}],
        {"a.py": ["cru", "norm"]},
        False,
    ),
)


def _autoteste_da_base_do_candidato() -> list[str]:
    """As amostras isolam UMA regra cada, e chamam a função de PRODUÇÃO.

    Sintéticas de propósito: a árvore real não contém o caso "base intacta"
    (os 86 manifestos com base são todos históricos), e mutante que só a árvore
    real exercitaria sobreviveria — padrão que já custou quatro rodadas aqui.
    """
    erros: list[str] = []
    for nome, arquivos, mapa, espera_erro in _AMOSTRAS_DA_BASE:
        obtido = bool(promocao_e_segura(arquivos, lambda a: mapa.get(a)))
        if obtido != espera_erro:
            erros.append(
                "autoteste da base do candidato — %s: esperava %s e veio %s"
                % (nome, "erro" if espera_erro else "silêncio",
                   "erro" if obtido else "silêncio")
            )
    # a segunda metade: o overlay que apaga trava
    if travas_que_o_overlay_apagaria("tem X e Y", "tem X e Y", ("X", "Y")):
        erros.append("autoteste: overlay idêntico foi acusado de apagar trava")
    if travas_que_o_overlay_apagaria("tem X e Y", "tem X", ("X", "Y")) != ["Y"]:
        erros.append("autoteste: a trava que o overlay apaga não foi nomeada")
    if travas_que_o_overlay_apagaria("tem X", "tem X e Y", ("X", "Y")):
        erros.append("autoteste: overlay que ACRESCENTA foi lido como apagando "
                     "— acréscimo não é remoção")
    return erros


# ---------------------------------------------------------------------------
# TAREFA 104 — o denominador diz 5 e o numerador vale 4
# ---------------------------------------------------------------------------
#
# Dois achados da reconciliação da tarefa 14, medidos em 2026-07-31, e eles são
# a mesma classe: **suíte que conta casos que não medem coisas diferentes**.
#
#   #3 — `prova/07-BASELINE-VERMELHO-VERDE.json` publicava 5 casos com o MESMO
#        `_erro_no_candidato` (`"$: oneOf esperava 1 alternativa, obteve 0"`).
#        Cinco casos com a mesma explicação são um caso contado cinco vezes.
#   #4 — as travas `T3` e `T5` eram A MESMA SONDA: mesmas duas chamadas sobre o
#        mesmo `atribuicao_base`. O denominador dizia 5 travas e valia 4.
#
# A INSTÂNCIA JÁ FOI SANADA em `reconciliacao-r3/sanacao/`, e bem — o instrumento
# novo até publica `erros_no_candidato_dois_a_dois_distintos`. O que faltava é o
# MECANISMO: nada impede a próxima campanha de repetir. É
# `conserto-de-instancia-nao-e-conserto-de-mecanismo`.
#
# O DESENHO FOI DECIDIDO POR MEDIÇÃO, em três degraus, e cada um derrubou uma
# classe de falso positivo contada nos 16 pacotes vivos:
#
#   | refino                          | acusações nos 16 |
#   |---------------------------------|-----------------:|
#   | assinatura de expressão, cru    |              134 |
#   | + ignorar laço                  |              128 |
#   | + ignorar rebind entre os dois  |                4 |
#   | + ignorar fallback              |            **0** |
#
# O segundo degrau é o que quase me enganou: `bad`, `bundle`, `forbidden` são
# variáveis REATRIBUÍDAS entre um `append` e o seguinte — mesma expressão, valor
# diferente. Texto de AST não distingue as duas coisas; só o rebind distingue.
#
# O terceiro é mais fino, e saiu de um caso real do `departamento-evolucao-skills`
# que eu por pouco não publiquei como defeito: um ramo `if fixture is None:`
# publica os dois nomes de caso carregando o MESMO erro de carga. Não é sonda
# duplicada — é **fallback fail-closed**, e ele fica vermelho pelo motivo certo.
# O discriminador é limpo: sonda duplicada tem **nomes distintos e uma prova**;
# fallback tem **o mesmo nome e duas provas**.
#
# ESPÉCIME REAL, e é ele que torna isto prova em vez de opinião: o par
# antes/depois da própria sanação lê **1** no arquivo com o defeito e **0** no
# corrigido, sem que nenhuma amostra sintética participe dessa leitura.
_LACOS = (
    ast.For, ast.AsyncFor, ast.While, ast.comprehension,
    ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
)


def evidencias_que_nao_discriminam(evidencias: list[str]) -> dict[str, int]:
    """Valor de evidência → quantas vezes se repete, só os repetidos.

    Evidência vazia não conta: caso que passou não tem explicação a dar, e
    exigir que ela seja única transformaria o silêncio em defeito.
    """
    contagem: dict[str, int] = {}
    for e in evidencias:
        chave = str(e).strip()
        if not chave:
            continue
        contagem[chave] = contagem.get(chave, 0) + 1
    return {k: n for k, n in contagem.items() if n > 1}


def _assinatura_de_prova(no: "ast.AST") -> str | None:
    """A EXPRESSÃO que produz o veredito de um `<lista>.append((...))`.

    Nome e descrição são literais de texto e NÃO entram: dois casos podem (e
    devem) ter nomes diferentes — é justamente o par "nomes diferentes, prova
    igual" que se quer achar.
    """
    if not (isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute)):
        return None
    if no.func.attr not in ("append", "extend") or len(no.args) != 1:
        return None
    alvo = no.args[0]
    if not isinstance(alvo, (ast.Tuple, ast.List)):
        return None
    partes = [
        ast.unparse(e) for e in alvo.elts
        if not (isinstance(e, ast.Constant) and isinstance(e.value, str))
    ]
    return " | ".join(partes) if partes else None


def _nome_do_caso(no: "ast.Call") -> str:
    return next(
        (e.value for e in no.args[0].elts
         if isinstance(e, ast.Constant) and isinstance(e.value, str)),
        "",
    )


def _nomes_usados(no: "ast.Call") -> set[str]:
    usados: set[str] = set()
    for e in no.args[0].elts:
        if isinstance(e, ast.Constant) and isinstance(e.value, str):
            continue
        for x in ast.walk(e):
            if isinstance(x, ast.Name):
                usados.add(x.id)
    return usados


def _linhas_de_rebind(arvore: "ast.AST") -> dict[str, list[int]]:
    """Nome → linhas onde ele passa a valer outra coisa.

    Sem isto o detector acusa 134 vezes nos 16 pacotes vivos, quase tudo
    `bad = ...; append(bad); bad = ...; append(bad)`.
    """
    mapa: dict[str, list[int]] = {}

    def marcar(alvo, linha: int) -> None:
        for x in ast.walk(alvo):
            if isinstance(x, ast.Name):
                mapa.setdefault(x.id, []).append(linha)

    for no in ast.walk(arvore):
        if isinstance(no, ast.Assign):
            for t in no.targets:
                marcar(t, no.lineno)
        elif isinstance(no, (ast.AugAssign, ast.AnnAssign)) and no.target is not None:
            marcar(no.target, no.lineno)
        elif isinstance(no, (ast.For, ast.AsyncFor)):
            marcar(no.target, no.lineno)
        elif isinstance(no, ast.NamedExpr):
            marcar(no.target, no.lineno)
        elif isinstance(no, ast.ExceptHandler) and no.name:
            mapa.setdefault(no.name, []).append(no.lineno)
        elif isinstance(no, ast.comprehension):
            marcar(no.target, getattr(no.target, "lineno", 0))
        elif isinstance(no, ast.withitem) and no.optional_vars is not None:
            marcar(no.optional_vars, getattr(no.optional_vars, "lineno", 0))
    return mapa


def sondas_duplicadas_em_casos(fonte: str) -> list[tuple[str, tuple[str, ...]]]:
    """(assinatura, nomes dos casos) para cada grupo que mede a MESMA coisa."""
    try:
        arvore = ast.parse(fonte)
    except SyntaxError:
        return []
    rebind = _linhas_de_rebind(arvore)
    por_assinatura: dict[str, list[tuple[str, int, set[str]]]] = {}
    provas_por_nome: dict[str, set[str]] = {}
    for no in ast.walk(arvore):
        assinatura = _assinatura_de_prova(no)
        if assinatura is None:
            continue
        nome = _nome_do_caso(no)
        por_assinatura.setdefault(assinatura, []).append(
            (nome, no.lineno, _nomes_usados(no))
        )
        provas_por_nome.setdefault(nome, set()).add(assinatura)

    achados: set[tuple[str, tuple[str, ...]]] = set()
    for assinatura, ocorrencias in por_assinatura.items():
        if len(ocorrencias) < 2:
            continue
        ocorrencias = sorted(ocorrencias, key=lambda x: x[1])
        grupo = [ocorrencias[0]]
        for atual in ocorrencias[1:]:
            anterior = grupo[-1]
            mudou = any(
                any(anterior[1] < linha <= atual[1] for linha in rebind.get(nome, ()))
                for nome in (anterior[2] | atual[2])
            )
            grupo = [atual] if mudou else grupo + [atual]
            if len(grupo) > 1 and all(
                len(provas_por_nome[g[0]]) == 1 for g in grupo
            ):
                achados.add((assinatura, tuple(g[0] for g in grupo)))
    return sorted(achados)


_AMOSTRAS_DA_SONDA = (
    # (nome, fonte, espera_acusacao)
    (
        "duas provas idênticas com nomes distintos — o defeito de origem",
        "c.append(('T3', v(base, s, s)))\nc.append(('T5', v(base, s, s)))\n",
        True,
    ),
    (
        "provas distintas não são acusadas",
        "c.append(('T3', v(sem_write, s, s)))\nc.append(('T5', v(sem_custodia, s, s)))\n",
        False,
    ),
    (
        "rebind entre os dois: mesma expressão, valor novo",
        "bad = um()\nc.append(('a', bad))\nbad = outro()\nc.append(('b', bad))\n",
        False,
    ),
    (
        "sem rebind, a mesma variável nos dois É sonda duplicada",
        "bad = um()\nc.append(('a', bad))\nc.append(('b', bad))\n",
        True,
    ),
    (
        "laço: uma linha de append, N valores",
        "for bad in maus:\n    c.append(('x', v(bad)))\n",
        False,
    ),
    (
        "o laço REBINDA: append antes e append dentro não são a mesma sonda",
        ("c.append(('antes', v(bad)))\n"
         "for bad in maus:\n"
         "    c.append(('dentro', v(bad)))\n"),
        False,
    ),
    (
        "fallback fail-closed: MESMO nome, duas provas em ramos opostos",
        ("if fx is None:\n"
         "    c.append(('aceita', erros_fx))\n"
         "    c.append(('rejeita', erros_fx))\n"
         "else:\n"
         "    c.append(('aceita', v(bom)))\n"
         "    c.append(('rejeita', v(ruim)))\n"),
        False,
    ),
    (
        "nome do caso não entra na assinatura — senão nada seria achado",
        "c.append(('nome bem diferente', p))\nc.append(('outro nome', p))\n",
        True,
    ),
)


def _autoteste_das_sondas() -> list[str]:
    """As amostras são SINTÉTICAS por necessidade, não por preguiça.

    Medido em 2026-08-22: com os três refinos, os 16 pacotes vivos têm **zero**
    ocorrências. Uma árvore sem o caso não mata mutante nenhum — é o padrão que
    já sobreviveu quatro rodadas nesta casa.
    """
    erros: list[str] = []
    for nome, fonte, espera in _AMOSTRAS_DA_SONDA:
        obtido = bool(sondas_duplicadas_em_casos(fonte))
        if obtido != espera:
            erros.append(
                "autoteste da sonda — %s: esperava %s e veio %s"
                % (nome, "acusação" if espera else "silêncio",
                   "acusação" if obtido else "silêncio")
            )
    # a outra metade: evidência que não discrimina
    if evidencias_que_nao_discriminam(["a", "a", "a", "b", "c"]) != {"a": 3}:
        erros.append("autoteste: a evidência repetida não foi contada")
    if evidencias_que_nao_discriminam(["a", "b", "c"]):
        erros.append("autoteste: evidências todas distintas foram acusadas")
    if evidencias_que_nao_discriminam(["", "", "  "]):
        erros.append("autoteste: evidência VAZIA foi tratada como repetida — "
                     "caso que passou não tem explicação a dar, e exigir "
                     "unicidade do silêncio transforma silêncio em defeito")
    if evidencias_que_nao_discriminam([]):
        erros.append("autoteste: lista vazia acusou — zero de detector é "
                     "suspeita, não conformidade")
    return erros
