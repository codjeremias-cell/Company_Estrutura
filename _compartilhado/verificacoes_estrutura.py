"""Verificações que recebem a ESTRUTURA INTEIRA — não um pacote.

**A fronteira é o tipo do parâmetro, e por isso ela virou fronteira de módulo.**
Checagem que recebe um arquivo ou o diretório de *um* pacote fica em
`verificacoes_pacote.py`. Checagem que recebe `structure_root` e atravessa a
árvore inteira mora aqui. O critério não é temático nem estilístico: é legível
**na assinatura**, e por isso um validador não erra de lado por descuido.

`validate_links` continua do lado do pacote apesar de usar `rglob`, porque o
`package_root` que ela varre **é** o pacote — o parâmetro decide, não o verbo.
`digest_de_arvore` também fica lá: recebe uma raiz qualquer e não é checagem.

**A replicação é o mecanismo, não o desperdício.** Todo validador de pacote
chama os dois lados. Com N frentes paralelas, N validadores varrem a árvore
inteira e basta **um** rodar para a colisão do vizinho aparecer — inclusive a de
um pacote que ainda não tenha validador próprio. Centralizar num único validador
de raiz mataria isso e trocaria custo de CPU por dependência de disciplina
humana. O preço aceito está declarado no ADR-015: custo quadrático e raio de
explosão maior — um `adr-` duplicado reprova os quinze de uma vez.

**Pacote novo entra na trava por existir.** Quem é gerente é definido pela
posição na árvore (`rglob` + o teste `parent.name == "agentes"`), nunca por lista
cadastrada: não há onde esquecer de inscrever porque não há cadastro.

Fonte normativa: `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passos 4 e 7, e o
[ADR-015](../ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-arquitetura-software/references/adr-015-checagens-por-pacote-e-de-estrutura-inteira.md).

As constantes de anatomia (`SECOES_CONTRATO_GERENTE` e a `SECOES_CONTRATO_AGENTE`
derivada dela) continuam em `verificacoes_pacote.py`, junto da derivação que as
liga: são **dados normativos**, não checagens, e separá-las criaria import
circular entre os dois módulos. O ADR-015 decide sobre funções; esta é a única
escolha de detalhe que ele não cobre, e fica declarada aqui.

Três travas de digest — a rodada 2 da tarefa 19
-----------------------------------------------
A rodada 1 consertou **dez sítios** de `check` tautológico e deixou a afordância
de pé: nada impedia o décimo primeiro. As três funções abaixo trocam curadoria
de sítio por mecanismo, e moram aqui porque as três varrem a árvore inteira:

- `validate_trava_de_digest` — a recusa de `digest()` existe **e dispara**, e
  nenhum validador canônico redefine a superfície do motor compartilhado;
- `validate_sem_check_tautologico` — nenhuma asserção da casa tem por sujeito um
  valor **produzido** por uma função de digest e por predicado algo verdadeiro
  **por construção**;
- `validate_fonte_normativa_conferida` — a `REGRAS-DE-OURO.md` confere com o
  valor declarado na `ORIGEM.md`, em **todos** os quinze pacotes.

As três entram em `FUNCOES_OBRIGATORIAS`. Isso não é decoração: quem não as
chamar é reprovado por `validate_cobertura_de_validadores`, que **todo** validador
canônico é obrigado a chamar. Uma trava que só existe em quem quiser chamá-la
erode em silêncio — foi o que a rodada 1 provou ao deixar `DigestDeFixtureRecusado`
exigida por zero dos dez validadores.

As quatro portas que a rodada 3 fechou — nomeadas pelo julgamento da rodada 2
-----------------------------------------------------------------------------
1. **Cópia privada não é só `def`.** A trava passa a ver toda LIGAÇÃO de nome:
   `digest = lambda …`, `from hashlib import md5 as digest`, atribuição, classe,
   parâmetro, alvo de `for`/`with`/`except` e walrus. A única forma legítima de
   um nome do motor aparecer ligado num validador é o import do próprio motor.
   Ligação DINÂMICA (`globals()["digest"] = …`, `setattr`, monkeypatch em
   runtime) continua invisível para a AST — é teto declarado, com nome, no
   `manifest.json` do candidato.
2. **Alias transitivo.** `d = candidate_digest_de_arvore(r); d2 = d` escapava —
   a derivação agora é computada até PONTO FIXO, e `d2` (e `d3`, e o resto da
   cadeia) contam como produção. A regra «todas as atribuições, não alguma»
   continua valendo em cada passo do fecho.
3. **Efeito, não chamada.** `FUNCOES_OBRIGATORIAS` deixou de aceitar chamada com
   retorno descartado: o retorno precisa alimentar o agregado de erros do
   validador. É o terceiro degrau da progressão documentada nesta casa (trava
   sem call site → call site por nome → chamada sem efeito), fechado pelo efeito.
4. **Cada regra do detector tem fixture própria.** R1–R5 disparam uma a uma no
   autoteste, a cada chamada; apagar qualquer regra reprova os quinze
   validadores em vez de deixá-los verdes.

Cada porta tem autoteste executado a cada chamada e mutação publicada que a
apaga e exige vermelho (M8–M11 de `instrumentos-r3/31_medir_r3.py`).
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from _compartilhado.verificacoes_pacote import (
    SECOES_CONTRATO_GERENTE,
    validate_contract_sections,
)

__all__ = [
    "validate_adr_series",
    "validate_contratos_de_gerente",
    "validate_cobertura_de_validadores",
    "validate_trava_de_digest",
    "validate_sem_check_tautologico",
    "validate_fonte_normativa_conferida",
    "validate_contagem_ligada_ao_instrumento",
    "validate_travas_compartilhadas_com_efeito",
    "PISO_DE_FUNCOES_OBRIGATORIAS",
    "achar_corpo_neutralizado",
    "achar_checks_tautologicos",
    "ADR_FILE_PATTERN",
    "ADR_HISTORICAL_EXCEPTIONS",
    "FUNCOES_DE_ESTRUTURA",
    "FUNCOES_OBRIGATORIAS",
    "MODULO_DE_ESTRUTURA",
    "COBERTURA_EXCECOES",
    "PRODUTORAS_DE_DIGEST",
    "SUPERFICIE_MINIMA_DO_MOTOR",
]

ADR_FILE_PATTERN = re.compile(r"^adr-(\d+)-.+\.md$")

# Os três `ADR-001` que a `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 4, declara
# históricos: nasceram em camadas distintas antes da convenção da série global e
# "permanecem intactos como proveniência e **não** autorizam reuso". A isenção é
# por CAMINHO EXATO, não por número: um quarto `adr-001` em qualquer outro lugar
# quebra o grupo inteiro e é reprovado.
ADR_HISTORICAL_EXCEPTIONS = (
    "ceo-maestro/references/adr-001-hierarquia-executiva.md",
    "ceo-maestro/diretor-de-lentes/references/adr-001-diretoria-e-camada-de-juizes.md",
    "ceo-maestro/departamento-negocios/references/adr-001-rota-vigente-aos-juizes.md",
)

MODULO_DE_ESTRUTURA = "_compartilhado.verificacoes_estrutura"

FUNCOES_DE_ESTRUTURA = (
    "validate_adr_series",
    "validate_contratos_de_gerente",
    "validate_cobertura_de_validadores",
    "validate_trava_de_digest",
    "validate_sem_check_tautologico",
    "validate_fonte_normativa_conferida",
    "validate_placar_nao_declara_cadeia",
    "validate_contagem_ligada_ao_instrumento",
    "validate_travas_compartilhadas_com_efeito",
    "validate_pendencia_tem_dono",
)

# O gate exige a **própria** presença, e não só "alguma checagem de estrutura".
# A primeira versão pedia qualquer uma das três, e a mutação mostrou o buraco: um
# validador que apagasse a chamada de cobertura continuava verde, porque ainda
# chamava a série de ADR — a trava de cobertura sumiria sem nada acusar, que é
# exatamente o defeito que ela existe para impedir. Uma trava que não se
# autoexige erode em silêncio.
#
# As três de digest entram aqui pelo mesmo argumento, agora medido de novo: na
# rodada 1 da tarefa 19 a trava nova (`DigestDeFixtureRecusado`) aparecia em UM
# arquivo e era exigida por ZERO dos dez validadores — apagá-la deixava 1879
# casos verdes. Trava exigida por ninguém não é trava, é comentário executável.
#
# A recusa da T55 (`recusar_execucao_fora_da_fonte`) NÃO entra nesta lista, e o
# motivo é de contrato: aqui se exige que o RETORNO alcance o agregado de erros, e
# aquela função não devolve erro — ela aborta com `SystemExit(3)` antes de
# qualquer medição. A exigência dela vive dentro de
# `validate_cobertura_de_validadores`, com o mesmo peso e a mesma mensagem de
# arquivo e linha.
FUNCAO_DE_RECUSA = "recusar_execucao_fora_da_fonte"

FUNCOES_OBRIGATORIAS = (
    "validate_cobertura_de_validadores",
    # T39 — promovida em 2026-08-22. Estava so entre as COMPLEMENTARES, onde a
    # regra e "chama alguma das N": um validador que a largasse continuaria verde
    # chamando outra, e a trava sumiria em silencio. Medido antes de mover: os
    # 16 ja a chamam, e nenhum descarta o retorno -- promover nao quebra ninguem,
    # so passa a EXIGIR o que ja era pratica.
    "validate_placar_nao_declara_cadeia",
    "validate_trava_de_digest",
    "validate_sem_check_tautologico",
    "validate_fonte_normativa_conferida",
    "validate_contagem_ligada_ao_instrumento",
    "validate_travas_compartilhadas_com_efeito",
    "validate_pendencia_tem_dono",
)

# PISO da lista acima — tarefa 84, e ele existe por causa de um mutante que
# escapou. Tirar um nome de `FUNCOES_OBRIGATORIAS` deixava os dezesseis verdes:
# a lista era a única fonte, e encolhê-la encolhia a exigência junto. Agora são
# DUAS edições em dois lugares, e a segunda é conferida por
# `validate_travas_compartilhadas_com_efeito`.
#
# É o mesmo remédio do `MINIMO_DE_CASOS`: contagem — ou lista — que só existe num
# lugar cai sem produzir vermelho nenhum.
PISO_DE_FUNCOES_OBRIGATORIAS = (
    "validate_cobertura_de_validadores",
    "validate_placar_nao_declara_cadeia",
    "validate_trava_de_digest",
    "validate_sem_check_tautologico",
    "validate_fonte_normativa_conferida",
    "validate_contagem_ligada_ao_instrumento",
    "validate_travas_compartilhadas_com_efeito",
    "validate_pendencia_tem_dono",
)

# Isenção do gate de cobertura, no mesmo molde de ADR_HISTORICAL_EXCEPTIONS:
# caminho exato do pacote, relativo à raiz, com `/`. Vazia de propósito — hoje os
# 15 pacotes gerentes têm validador próprio, e uma isenção existente convida a
# próxima.
COBERTURA_EXCECOES: tuple[str, ...] = ()

# --- as três travas de digest ----------------------------------------------
#
# Toda função desta casa que FABRICA um valor com a forma de digest. O ponto não
# é o nome: é que o valor de retorno delas tem forma garantida, e por isso
# qualquer asserção sobre a FORMA desse retorno é verdadeira por construção.
PRODUTORAS_DE_DIGEST = (
    "digest",
    "sha256_file",
    "sha256_texto_normalizado",
    "digest_de_arvore",
    "candidate_digest_de_arvore",
    "digest_de_arvore_normalizado",
    "candidate_digest_normalizado_de_arvore",
)

# Piso da superfície pública do motor compartilhado. `validate_trava_de_digest`
# une isto ao `__all__` real do módulo em vez de confiar só no `__all__`: encolher
# o `__all__` não pode encolher a trava.
SUPERFICIE_MINIMA_DO_MOTOR = (
    "digest",
    "sha256_file",
    "sha256_texto_normalizado",
    "validate_schema",
    "json_pointer",
    "is_type",
    "find_const",
    "collect_property_names",
)

_MODULO_DO_MOTOR = "_compartilhado.validador_schema"
_ARQUIVO_DO_MOTOR = "_compartilhado/validador_schema.py"
_NOME_DA_TRAVA = "DigestDeFixtureRecusado"

# Amostra que o detector TEM de acusar, e amostra que ele NÃO pode acusar. Ficam
# aqui, no mesmo arquivo, e são rodadas a cada chamada: detector esvaziado passa
# a reprovar a si mesmo em vez de ficar verde varrendo nada. Verde de detector
# cego é o falso positivo mais caro desta casa — já custou dez pacotes
# publicando «digest é verificável» sobre um teste que não podia ficar vermelho.
_AMOSTRA_TAUTOLOGICA = '''
def amostra(caminho, raiz):
    check("digest das regras é verificável",
          caminho.is_file() and sha256_file(caminho).startswith("sha256:"))
    check("digest do próprio schema é verificável",
          digest(caminho.read_text()).startswith("sha256:"))
    do_pacote = candidate_digest_de_arvore(raiz)
    check("prefixo e tamanho", do_pacote.startswith("sha256:") and len(do_pacote) == 71)
'''

_AMOSTRA_LEGITIMA = '''
def amostra(caminho, declarado, envelope):
    check("recomputado bate com o declarado", sha256_file(caminho) == declarado)
    assinatura = envelope.get("sha256")
    check("forma do campo recebido",
          isinstance(assinatura, str) and assinatura.startswith("sha256:"))
    if sha256_texto_normalizado(caminho) != envelope["rules_digest"]:
        return ["divergente"]
    valor = declarado or digest("a")
    check({"pattern": "^sha256:[a-f0-9]{64}$"}, digest("a"), valid=True,
          name="pattern aceita digest válido")
    return [valor]
'''

# As duas últimas linhas da amostra legítima são os dois FALSOS POSITIVOS que a
# regra 5 produziu em 2026-08-05, no dia em que nasceu:
#
# 1. `declarado or digest("a")` — valor de FALLBACK, não condição. Fora de
#    asserção, um produtor num `or` é um default legítimo.
# 2. `check(<schema>, digest("a"), valid=True, name=…)` — outro `check`, de outra
#    família, em `_compartilhado/teste_validador_schema.py:200`. O sujeito da
#    asserção ali é o MOTOR DE SCHEMA; o digest é fixture.
#
# Ficam aqui porque trava que grita no inocente é desligada na semana seguinte, e
# o jeito de garantir que não volte a gritar é deixar o inocente medido a cada
# execução. Um detector que só prova o que acusa mede metade de si mesmo.

_ESPERADO_NA_AMOSTRA_TAUTOLOGICA = 4

# --- uma fixture POR REGRA, cada uma disparando a sua --------------------------
#
# A rodada 2 publicou cinco regras e um autoteste que exercitava DUAS: a amostra
# tautológica acima só contém as formas R1 e R2. `R3`, `R4` e `R5` nunca tinham
# disparado em lugar nenhum — e a R4 é a regra creditada pela descoberta da
# tautologia que a rodada 1 reescreveu. Apagar a R4 deixava os quinze verdes.
# Autoteste que cobre 2 de 5 autoriza apagar 3 de 5 em silêncio; agora cada
# regra tem o sítio que a exige, e o autoteste confere regra a regra, pela TAG
# `[R<n>]` que o detector carimba em cada acusação.
_FIXTURAS_POR_REGRA = {
    "R1": (
        'def amostra(caminho):\n'
        '    check("prefixo do digest", sha256_file(caminho).startswith("sha256:"))\n'
    ),
    "R2": (
        'def amostra():\n'
        '    check("tamanho do digest", len(digest("a")) == 71)\n'
    ),
    "R3": (
        'def amostra(raiz):\n'
        '    check("tipo do digest", isinstance(digest_de_arvore(raiz), str))\n'
    ),
    "R4": (
        'import re\n'
        'def amostra(raiz):\n'
        '    check("forma do digest",\n'
        '          re.fullmatch(r"sha256:[0-9a-f]{64}", candidate_digest_de_arvore(raiz)))\n'
    ),
    "R5": (
        'def amostra(raiz):\n'
        '    check("digest existe", digest_de_arvore_normalizado(raiz))\n'
    ),
}

# O desvio de DOIS saltos que o parecer da rodada 2 nomeou: a docstring da
# rodada 2 dizia ter fechado o desvio de uma linha (`d = produtora(...)`), e o
# segundo salto também custa uma linha. A fixture tem TRÊS saltos de propósito:
# prova o fecho, não um teto novo em n=2.
_AMOSTRA_ALIAS_TRANSITIVO = '''
def amostra(raiz):
    d = candidate_digest_de_arvore(raiz)
    d2 = d
    d3 = d2
    check("prefixo pelo alias", d3.startswith("sha256:"))
'''
_ESPERADO_NO_ALIAS = 1

# O alias que NÃO pode ser acusado: um nome da cadeia recebe também valor de
# outra origem. «Todas as atribuições» vale em cada passo do fecho.
_AMOSTRA_ALIAS_LEGITIMO = '''
def amostra(raiz, declarado):
    d = candidate_digest_de_arvore(raiz)
    d2 = d
    d2 = declarado
    check("recomputado bate com o declarado", d2.startswith("sha256:"))
'''

# --- as amostras da trava de cópia privada ------------------------------------
#
# A rodada 2 só via `def` — `digest = lambda c: "sha256:" + c*64` era invisível,
# e `from hashlib import md5 as digest` também. As quatro formas abaixo são as
# que o julgamento nomeou (def, lambda, import, atribuição); o autoteste exige
# cada uma com a FORMA certa, e exige silêncio na amostra legítima.
_AMOSTRA_COPIA_PRIVADA = '''
import hashlib
from hashlib import md5 as validate_schema
digest = lambda c: "sha256:" + c * 64

def sha256_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

json_pointer = sha256_file
'''
_ESPERADO_NA_AMOSTRA_DE_COPIA = {
    "digest": "lambda",
    "json_pointer": "atribuição",
    "sha256_file": "def",
    "validate_schema": "import",
}

_AMOSTRA_COPIA_LEGITIMA = '''
from _compartilhado.validador_schema import digest, sha256_file

def usa(caminho):
    return digest("a"), sha256_file(caminho)
'''

# --- as amostras da exigência de EFEITO ---------------------------------------
#
# Exigir a chamada não é exigir o efeito: `validate_trava_de_digest(ROOT)` numa
# linha solta satisfazia a cobertura da rodada 2 com o retorno no lixo. A amostra
# boa consome cada retorno nos idiomas reais da casa (argumento de `case`/
# `check`, tupla dentro de `cases.append`, variável intermediária consumida);
# a amostra ruim chama as quatro e descarta os quatro retornos.
_AMOSTRA_COBERTURA_COM_EFEITO = '''
from _compartilhado.verificacoes_estrutura import (
    validate_cobertura_de_validadores,
    validate_contagem_ligada_ao_instrumento,
    validate_fonte_normativa_conferida,
    validate_travas_compartilhadas_com_efeito,
    validate_pendencia_tem_dono,
    validate_placar_nao_declara_cadeia,
    validate_sem_check_tautologico,
    validate_trava_de_digest,
)

def run(cases, case, results, STRUCTURE_ROOT):
    cases.append(("cobertura", True, validate_cobertura_de_validadores(STRUCTURE_ROOT)))
    erros = validate_trava_de_digest(STRUCTURE_ROOT)
    results.check("trava de digest", not erros, " | ".join(erros))
    case("sem tautologia", True, validate_sem_check_tautologico(STRUCTURE_ROOT))
    case("fonte normativa", True, validate_fonte_normativa_conferida(STRUCTURE_ROOT))
    selo = validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)
    results.check("selo de contagem", not selo, " | ".join(selo))
    case("travas compartilhadas", True, validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT))
    case("placar nao declara cadeia", True, validate_placar_nao_declara_cadeia(STRUCTURE_ROOT))
    dono = validate_pendencia_tem_dono(STRUCTURE_ROOT)
    results.check("pendencia tem dono", not dono, " | ".join(dono))
'''

_AMOSTRA_COBERTURA_SEM_EFEITO = '''
from _compartilhado.verificacoes_estrutura import (
    validate_cobertura_de_validadores,
    validate_contagem_ligada_ao_instrumento,
    validate_fonte_normativa_conferida,
    validate_travas_compartilhadas_com_efeito,
    validate_pendencia_tem_dono,
    validate_placar_nao_declara_cadeia,
    validate_sem_check_tautologico,
    validate_trava_de_digest,
)

def run(STRUCTURE_ROOT):
    validate_cobertura_de_validadores(STRUCTURE_ROOT)
    validate_trava_de_digest(STRUCTURE_ROOT)
    ignorado = validate_sem_check_tautologico(STRUCTURE_ROOT)
    validate_fonte_normativa_conferida(STRUCTURE_ROOT)
    validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)
    validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT)
    validate_placar_nao_declara_cadeia(STRUCTURE_ROOT)
    validate_pendencia_tem_dono(STRUCTURE_ROOT)
'''


# Uma cópia congelada de fonte externa NÃO é um pacote desta estrutura. O
# snapshot da tarefa 36 (`fontes-legadas-pinadas/`) guarda skills do Catálogo
# byte a byte, `SKILL.md` inclusive — e o nome do arquivo é parte da prova, não
# pode ser mudado para escapar da varredura. Sem esta exclusão a descoberta por
# posição as adota como pacotes gerentes e cobra validador de cada uma; medido
# em 2026-08-08, foi o que aconteceu no minuto seguinte ao snapshot existir.
# `evals/` entra pelo MESMO motivo, medido em 2026-08-19: as campanhas de
# julgamento guardam árvores completas de pacote — `SKILL.md`,
# `CONTRATO-DE-COMPROMISSO.md` e `references/adr-*.md` — dentro de
# `evals/<campanha>/{custodia,isolamento}/…`. São **evidência congelada de
# rodada passada**, exatamente como o snapshot da T36, e a descoberta por posição
# as adotava como pacotes gerentes: 16 dos 41 FAIL da cadeia eram `cobertura:
# pacote …/root/otica sem evals/validate_workflow.py`, e outros 16 eram colisão
# de `adr-006`/`adr-015` entre o original e suas cópias de campanha.
#
# Excluir aqui não afrouxa a trava: **restaura o alvo dela**. Ela existe para
# pegar duas frentes cunhando o mesmo número (os dois `adr-005` de Registros e
# QA), e cópia de laboratório não é frente cunhando nada. Um pacote real nunca
# tem `evals` no caminho do próprio `SKILL.md` — ele tem `evals/` como filho.
_PASTAS_QUE_NAO_SAO_PACOTE = ("agentes", "fontes-legadas-pinadas", "evals")


# O arquivo que identifica a raiz da FONTE. O deploy não o leva para o runtime —
# conferido em 2026-08-22 —, e ele é a identidade da própria árvore, não um plano
# de frente que alguém apaga sem pensar.
_MARCA_DA_FONTE = "MANIFESTO-DA-ESTRUTURA.json"

# Os dois nomes que o deploy cria. Ver `deploy-estrutura.ps1` e o `$preservarSempre`
# do `deploy-skills.ps1` do Catálogo.
_PAIS_DE_RUNTIME = (".claude", ".agents")


def raiz_e_runtime(structure_root: Path) -> str | None:
    """Motivo pelo qual esta raiz **não** é a fonte da Estrutura — ou `None`.

    **Por que existe (T55, medida em 2026-08-08 e REMEDIDA em 2026-08-22).** Os
    validadores tomam `ROOT.parent` como raiz da estrutura. Na fonte isso é
    `Estrutura Final de Skills/`; no runtime é `.claude/skills/`, que **hospeda as
    60 skills do Catálogo**. Como `_pacotes_gerentes` descobre por posição
    (`root.rglob("SKILL.md")`), toda skill do Catálogo vira "pacote gerente" e é
    cobrada de contrato e de validador que ela nunca teve.

    O efeito não é "um número um pouco errado": é **medir outro objeto**. Medido
    hoje, com a mesma árvore: fonte `151/151`, runtime `148/151`; e o mesmo padrão
    nos aninhados — `diretor-de-lentes` `106/106` contra `104/106`,
    `departamento-juizes` `172/172` contra `170/172`.

    Das duas saídas que a tarefa nomeava, esta é a (a), e a própria tarefa explica
    por quê: *"número errado com cara de medida é pior que recusa declarada"*.
    O runtime existe para **invocação**, não para validação — e a paridade dele
    com a fonte já é provada por digest no deploy, não por rodar a cadeia de lá.

    Duas identificações POSITIVAS, nunca uma suposição:

    1. a raiz é `<algo>/.claude/skills` ou `<algo>/.agents/skills` — o layout que
       o deploy cria;
    2. falta a marca da fonte **e** há pacote estranho no primeiro nível (com
       `SKILL.md` e sem `CONTRATO-DE-COMPROMISSO.md`) — a assinatura de um runtime
       instalado noutro caminho.

    Fonte sadia não dispara nenhuma das duas: conferido em 2026-08-22, o primeiro
    nível da fonte tem apenas `ceo-maestro` e `especialista-planejador` com
    `SKILL.md`, e ambos têm contrato. **A regra 2 exige as duas condições de
    propósito** — só "há pacote sem contrato" seria o próprio defeito que
    `validate_contratos_de_gerente` existe para acusar, e recusar ali mascararia
    o achado em vez de reportá-lo.
    """
    root = Path(structure_root)
    try:
        root = root.resolve()
    except OSError:  # pragma: no cover — caminho inacessível
        return None

    if root.name == "skills" and root.parent.name in _PAIS_DE_RUNTIME:
        return (
            f"a raiz resolvida é {root}, que é um RUNTIME "
            f"({root.parent.name}/skills), não a fonte da Estrutura"
        )

    if (root / _MARCA_DA_FONTE).is_file():
        return None

    estranhos = sorted(
        filho.name
        for filho in root.iterdir()
        if filho.is_dir()
        and (filho / "SKILL.md").is_file()
        and not (filho / "CONTRATO-DE-COMPROMISSO.md").is_file()
    ) if root.is_dir() else []
    if estranhos:
        amostra = ", ".join(estranhos[:3])
        return (
            f"a raiz resolvida é {root}: falta {_MARCA_DA_FONTE} e há "
            f"{len(estranhos)} pacote(s) que não são da Estrutura no primeiro "
            f"nível ({amostra}…)"
        )
    return None


def recusar_execucao_fora_da_fonte(structure_root: Path) -> None:
    """Aborta com mensagem em vez de imprimir um placar que mede o alvo errado.

    Chamada no ponto de entrada de **todos** os validadores canônicos, e a
    presença dessa chamada é conferida por `validate_cobertura_de_validadores` —
    senão isto vira mais uma trava que ninguém exige, e trava que não se autoexige
    erode.

    Sai com **código 3**, distinto do `1` de "houve FAIL": quem automatiza precisa
    separar *reprovou* de *nem deveria ter rodado aqui*.
    """
    motivo = raiz_e_runtime(structure_root)
    if motivo is None:
        return
    print(
        "[RECUSA] este validador não roda a partir do runtime.\n"
        f"         {motivo}.\n"
        "         Aqui a descoberta por posição adotaria as skills do Catálogo\n"
        "         como pacotes da Estrutura e devolveria um número que mede outro\n"
        "         objeto. Rode a partir da FONTE:\n"
        "             Estrutura Final de Skills/<pacote>/  →  "
        "PYTHONIOENCODING=utf-8 python evals/validate_workflow.py\n"
        "         A paridade fonte↔runtime é provada por digest no deploy, não por\n"
        "         rodar a cadeia daqui.",
        file=sys.stderr,
    )
    raise SystemExit(3)


def _pacotes_gerentes(root: Path) -> list[Path]:
    """Todo diretório com `SKILL.md` que não seja pasta de agente nem cópia
    congelada de fonte externa.

    Descoberta por posição, não por cadastro: é o que faz pacote novo entrar na
    trava por existir.
    """
    return [
        skill.parent
        for skill in sorted(root.rglob("SKILL.md"))
        if skill.parent.parent.name != "agentes"
        and not set(_PASTAS_QUE_NAO_SAO_PACOTE) & set(skill.parts)
    ]


def _chama_recusa(fonte: str) -> bool:
    """O validador chama `recusar_execucao_fora_da_fonte(<algo>)`? (AST, não texto.)

    **Varredura própria, e o motivo é um erro cometido ao escrever esta trava.**
    A primeira versão perguntava `FUNCAO_DE_RECUSA not in chamadas`, e `chamadas`
    só recebe nomes que estão em `FUNCOES_DE_ESTRUTURA` — a recusa não está, e
    nunca estaria, porque o contrato dela é outro (aborta, não devolve erro).
    O `if` era **estruturalmente insatisfazível**: acusou os dezesseis validadores
    logo depois de os dezesseis terem sido fiados. Cláusula presente e
    inalcançável é o mesmo defeito que a `guarda-de-escopo` teve com o kill
    switch, no mesmo dia.

    Pô-la em `FUNCOES_DE_ESTRUTURA` resolveria o sintoma e afrouxaria outra
    trava: `funcoes_complementares` é derivada daquela tupla, e a recusa passaria
    a servir de "complementar", deixando um validador satisfazer aquela exigência
    sem chamar nenhuma checagem complementar de verdade.

    Conferência **estrutural**: `ast.Call` com `func` sendo o nome exato. Menção
    em comentário, docstring ou string não conta — validador de string aceita o
    token dentro de prosa, e é assim que gate vira teatro.
    """
    try:
        arvore = ast.parse(fonte)
    except SyntaxError:
        return False
    for no in ast.walk(arvore):
        if isinstance(no, ast.Call):
            alvo = no.func
            nome = getattr(alvo, "id", None) or getattr(alvo, "attr", None)
            if nome == FUNCAO_DE_RECUSA and no.args:
                return True
    return False


def _validadores_canonicos(root: Path) -> list[Path]:
    """Os `evals/validate_workflow.py` dos pacotes gerentes — e só eles.

    A árvore guarda dezenas de `validate_workflow.py` congelados dentro de
    `evals/<campanha>/candidatos/…`: são **evidência de rodadas passadas**, não
    código vigente, e reescrevê-los seria alterar o registro. A varredura segue a
    mesma descoberta por posição do resto do módulo — quem tem `SKILL.md` fora de
    `agentes/` é pacote gerente, e o validador dele é canônico.
    """
    return [
        pacote / "evals" / "validate_workflow.py"
        for pacote in _pacotes_gerentes(root)
        if (pacote / "evals" / "validate_workflow.py").is_file()
    ]


def validate_adr_series(
    structure_root: Path,
    *,
    historical_exceptions: tuple[str, ...] = ADR_HISTORICAL_EXCEPTIONS,
) -> list[str]:
    """A série `adr-<NNN>` é global e única em TODA a estrutura.

    O passo 4 do guia manda cunhar o próximo número livre olhando todos os
    `adr-*.md` da árvore, porque o arquivo mora na pasta do dono da decisão mas o
    número é da estrutura inteira. O aviso em prosa já falhou uma vez (dois
    `adr-005`, em Registros e em QA), então a regra vale aqui, mecanicamente.

    Roda sobre a estrutura inteira e não sobre o pacote: é isso que faz a trava
    valer com frentes paralelas — qualquer validador pega a colisão do vizinho,
    mesmo que o pacote do vizinho ainda não tenha validador próprio.

    `historical_exceptions` são caminhos relativos a `structure_root`, com `/`.
    Um número só é perdoado quando **todos** os arquivos dele estão na lista; um
    arquivo novo entrando no grupo reprova o grupo inteiro.
    """
    if not structure_root.is_dir():
        return [f"série de ADR: raiz da estrutura ausente em {structure_root}"]

    root = structure_root.resolve()
    exempt = set(historical_exceptions)
    by_number: dict[int, list[str]] = {}
    for path in root.rglob("adr-*.md"):
        if not path.is_file():
            continue
        # Cópia de laboratório não cunha número — a mesma exclusão de
        # `_pacotes_gerentes`, pelo mesmo motivo (2026-08-19). As campanhas em
        # `evals/<campanha>/{custodia,isolamento}/…` guardam `references/` inteiros
        # do pacote julgado; sem isto, o original colide com a própria evidência e
        # a trava reprova a casa por ter registro do passado. Ela continua pegando
        # colisão real, que por definição mora fora de `evals/`.
        if set(_PASTAS_QUE_NAO_SAO_PACOTE) & set(path.parts):
            continue
        match = ADR_FILE_PATTERN.match(path.name)
        if not match:
            continue
        relative = path.resolve().relative_to(root).as_posix()
        by_number.setdefault(int(match.group(1)), []).append(relative)

    errors: list[str] = []
    for number in sorted(by_number):
        paths = sorted(by_number[number])
        if len(paths) < 2 or set(paths) <= exempt:
            continue
        errors.append(
            f"série de ADR: número {number:03d} duplicado em "
            + " e ".join(paths)
        )
    return errors


def validate_contratos_de_gerente(structure_root: Path) -> list[str]:
    """Todo pacote com `SKILL.md` fora de `agentes/` tem contrato de gerente canônico.

    O passo 7 do guia prescreve as 12 seções do contrato de gerente, e até
    2026-07-27 **nenhum** validador as conferia: a medição encontrou 8 de 15
    conformes, com quatro anatomias rivais convivendo — e os dois nós de topo,
    `ceo-maestro` e `diretor-de-lentes`, entre os que faltavam. Prosa
    prescrevendo anatomia não impediu a divergência; esta função impede.
    """
    if not structure_root.is_dir():
        return [f"contratos de gerente: raiz da estrutura ausente em {structure_root}"]

    root = structure_root.resolve()
    errors: list[str] = []
    for pacote in _pacotes_gerentes(root):
        relative = pacote.resolve().relative_to(root).as_posix()
        errors.extend(
            validate_contract_sections(
                pacote / "CONTRATO-DE-COMPROMISSO.md",
                SECOES_CONTRATO_GERENTE,
                f"contrato de gerente {relative}",
            )
        )
    return errors


# Os nomes por que esta casa AGREGA erros num caso: as quatro assertivas do
# idioma (`check`, `case`, `condition`, `require`) e os métodos de coleção com
# que os validadores registram casos (`cases.append((nome, True, erros))`,
# `cases.extend([...])`). `assert` e `return` também contam: o primeiro é o
# agregado da linguagem, o segundo entrega o valor a quem agrega.
# TAREFA 98 — o QUARTO degrau: exigir efeito não é reconhecer o efeito.
#
# Até 2026-08-22 esta lista tinha NOVE nomes e decidia sozinha: um retorno só
# "alcançava o agregado" se quem o recebia se chamasse `check`, `case`,
# `append`, `extend`… Medido, o erro saía nos DOIS sentidos:
#
#   - `placar.registrar(validate_x(R))` — agregador legítimo com outro nome —
#     era acusado de `COBERTURA_SEM_EFEITO`, **inocente**;
#   - `lixo.append(validate_x(R))`, com `lixo` que ninguém lê depois, contava
#     como efeito, **vácuo**.
#
# A pergunta certa não é COMO SE CHAMA quem recebe, e sim SE O RECIPIENTE É
# LIDO. `cases.append(...)` tem efeito porque alguém faz `len(cases)`;
# `lixo.append(...)` não tem porque ninguém toca em `lixo` de novo. Isso é
# estrutura da linguagem, não convenção da casa, e é o que a tarefa 19 pedia:
# "a lista passa a ser derivada da própria estrutura do validador".
#
# POR QUE A LISTA NÃO MORREU DE VEZ: chamada de FUNÇÃO LIVRE (`check(...)`,
# `case(...)`) descarta o resultado e não tem recipiente — é indistinguível de
# `print(...)` por fluxo de dados puro. Para essas, e SÓ para essas, o idioma
# continua sendo reconhecido por nome. Cinco nomes em vez de nove, e a forma
# dominante (`X.append(...)`) saiu do alcance da lista.
#
# MEDIDO ANTES DE INSTALAR: a regra nova concorda com a antiga em 16 de 16
# validadores vivos — divergência ZERO nos dois sentidos — e as duas amostras
# do autoteste continuam em 8/0 e 0/8.
_AGREGADORES_LIVRES = (
    "check",
    "case",
    "condition",
    "require",
    "warn",
)


def _parametros_de_funcao(arvore: ast.AST) -> set[str]:
    """Nomes que chegam por parâmetro — o recipiente é do CHAMADOR.

    Sem isto, um `def acrescenta(cases): cases.append(validate_x(R))` seria
    acusado, porque quem faz `len(cases)` está fora do arquivo. Acusar o idioma
    legítimo é `gate-que-barra-evidencia-boa`, e na dúvida entre permissivo e
    injusto esta casa escolhe permissivo e declara.
    """
    nomes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = no.args
            for a in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs):
                nomes.add(a.arg)
            if args.vararg:
                nomes.add(args.vararg.arg)
            if args.kwarg:
                nomes.add(args.kwarg.arg)
    return nomes


def _recipiente_e_lido(
    arvore: ast.AST, pais: dict, parametros: set[str], nome: str
) -> bool:
    """Alguém LÊ este nome — e escrever nele não conta como ler.

    `lixo.append(x)` é ESCRITA em `lixo`; se for a única aparição, o valor não
    alcança ninguém. `len(cases)`, `for c in cases`, `return cases` são leituras.
    """
    if nome in parametros:
        return True
    for no in ast.walk(arvore):
        if not (isinstance(no, ast.Name) and no.id == nome
                and isinstance(no.ctx, ast.Load)):
            continue
        pai = pais.get(no)
        if isinstance(pai, ast.Attribute) and isinstance(pais.get(pai), ast.Call):
            continue
        return True
    return False


def _consumo_alcanca_alguem(
    chamada: ast.Call, arvore: ast.AST, pais: dict, parametros: set[str]
) -> bool:
    """O valor virou argumento desta chamada — o consumo chega a alguém?"""
    alvo = chamada.func
    if isinstance(alvo, ast.Attribute) and isinstance(alvo.value, ast.Name):
        return _recipiente_e_lido(arvore, pais, parametros, alvo.value.id)
    return _nome_chamado(chamada) in _AGREGADORES_LIVRES


def _alias_de_funcao(arvore: ast.AST) -> tuple[dict[str, str], list[tuple[str, int]]]:
    """(apelido → nome canônico, sombras). TAREFA 99 — a outra ponta do alias.

    O fecho de alias já existia do lado do **valor** — o retorno atribuído a um
    nome e esse nome consumido adiante. Faltava do lado da **função**, que é a
    fronteira da chamada: `g = validate_trava_de_digest; check(g(ROOT))` chamava
    a trava e era lido como **não chamando**, porque `_nome_chamado` devolve `g`.

    Medido em 2026-08-22, QUATRO formas, e as quatro acusavam quem cumpriu:
    apelido por atribuição, `import … as`, `getattr(m, "nome")` e cadeia de
    apelidos (`g = f; h = g`). Nenhuma delas é rota de fuga — quem aliasa está
    chamando —, então o defeito era **inteiramente** de falso positivo.

    **A SOMBRA é a porta que resolver alias abriria, e ela fecha junto.** Se um
    nome de trava for reatribuído a outra coisa — `validate_trava_de_digest =
    lambda *a: []` —, a chamada passaria a ser reconhecida enquanto executa um
    stub. Por isso toda reatribuição de um nome de trava para algo que não é a
    própria trava entra em `sombras` e vira acusação: aqui, ao contrário do
    alias, a intenção é indistinguível do acidente e o risco é de falso
    NEGATIVO.

    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo (tarefa 100).
    """
    mapa: dict[str, str] = {}
    sombras: list[tuple[str, int]] = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.ImportFrom) and no.module == MODULO_DE_ESTRUTURA:
            for apelido in no.names:
                if apelido.name in FUNCOES_DE_ESTRUTURA and apelido.asname:
                    mapa[apelido.asname] = apelido.name
    mudou = True
    while mudou:                       # fecho transitivo: g = f; h = g
        mudou = False
        for no in ast.walk(arvore):
            if not isinstance(no, ast.Assign) or len(no.targets) != 1:
                continue
            alvo = no.targets[0]
            if not isinstance(alvo, ast.Name):
                continue
            valor = no.value
            canonico = None
            if isinstance(valor, ast.Name):
                canonico = (valor.id if valor.id in FUNCOES_DE_ESTRUTURA
                            else mapa.get(valor.id))
            elif (isinstance(valor, ast.Call)
                  and _nome_chamado(valor) == "getattr"
                  and len(valor.args) >= 2
                  and isinstance(valor.args[1], ast.Constant)
                  and valor.args[1].value in FUNCOES_DE_ESTRUTURA):
                canonico = valor.args[1].value
            if canonico is not None:
                if mapa.get(alvo.id) != canonico:
                    mapa[alvo.id] = canonico
                    mudou = True
            elif alvo.id in FUNCOES_DE_ESTRUTURA:
                if (alvo.id, no.lineno) not in sombras:
                    sombras.append((alvo.id, no.lineno))
    return mapa, sombras


def _canonico_da_chamada(no: ast.Call, mapa: dict[str, str]) -> str:
    """O nome CANÔNICO que esta chamada aciona — apelido resolvido."""
    nome = _nome_chamado(no)
    if nome in FUNCOES_DE_ESTRUTURA:
        return nome
    if nome in mapa:
        return mapa[nome]
    if (nome == "getattr" and len(no.args) >= 2
            and isinstance(no.args[1], ast.Constant)
            and no.args[1].value in FUNCOES_DE_ESTRUTURA):
        return str(no.args[1].value)
    return nome


def travas_sombreadas(fonte: str) -> list[str]:
    """Nome de trava reatribuído a outra coisa — reconhecimento sobre um stub."""
    try:
        arvore = ast.parse(fonte)
    except SyntaxError:
        return []
    _, sombras = _alias_de_funcao(arvore)
    return [
        f"TRAVA_SOMBREADA: `{nome}` é reatribuído na linha {linha} a algo que "
        "não é a própria trava. Depois disso a chamada continua sendo "
        "RECONHECIDA e passa a executar outra coisa — resolver apelido sem "
        "fechar esta porta trocaria um falso positivo por um falso negativo "
        "(tarefa 99)"
        for nome, linha in sorted(sombras)
    ]


def _chamadas_com_efeito(
    fonte: str,
) -> tuple[bool, set[str], set[str], list[tuple[str, int]]]:
    """(importa, chamadas, obrigatórias COM efeito, chamadas com retorno descartado).

    A conferência é **estrutural, não textual**, e o motivo é caro: validador de
    string aceita o token dentro de um comentário, de uma docstring ou de uma
    lista de nomes que ninguém chama. A AST distingue `ImportFrom` de prosa e
    `Call` de menção.

    **O degrau que a rodada 3 fecha: exigir a chamada não é exigir o efeito.**
    A rodada 2 contava `Call` — e `validate_trava_de_digest(ROOT)` numa linha
    solta, com o retorno no lixo, satisfazia a cobertura sem travar nada. É o
    terceiro degrau da progressão documentada nesta casa: trava sem call site →
    call site por nome → chamada sem efeito. Aqui, uma chamada de função
    obrigatória só conta quando o RETORNO alcança o agregado de erros:

    - o valor (ou uma expressão que o contém) é argumento de um agregador
      (`check`/`case`/`condition`/`require`/`cases.append`/`.extend`), ou de um
      `assert`/`return`; ou
    - o valor é atribuído a um nome e esse nome (ou um alias dele, pelo mesmo
      fecho transitivo da trava de tautologia) é usado como argumento de um
      agregador em qualquer ponto do arquivo.

    Chamada cujo retorno não alcança o agregado entra em `sem_efeito`, com a
    linha, e vira `COBERTURA_SEM_EFEITO` no chamador.

    **Teto declarado:** o rastreio é sintático e global ao arquivo — não prova
    que o valor DECIDE o veredito (um retorno usado só como detalhe de mensagem
    conta como consumido), e consumo via fluxo de controle (`if erros: ...` sem
    return) não é reconhecido. O primeiro lado é permissivo e o segundo é
    estrito; os quatro estão nomeados em `TETOS_DO_MECANISMO` (tarefa 100).
    """
    arvore = ast.parse(fonte)
    importa = False
    chamadas: set[str] = set()
    alias, _sombras = _alias_de_funcao(arvore)
    pais: dict[ast.AST, ast.AST] = {}
    for no in ast.walk(arvore):
        for filho in ast.iter_child_nodes(no):
            pais.setdefault(filho, no)
        if isinstance(no, ast.ImportFrom) and no.module == MODULO_DE_ESTRUTURA:
            importa = True
        elif isinstance(no, ast.Import):
            importa = importa or any(
                alias.name == MODULO_DE_ESTRUTURA for alias in no.names
            )
        elif isinstance(no, ast.Call):
            nome = _canonico_da_chamada(no, alias)
            if nome in FUNCOES_DE_ESTRUTURA:
                chamadas.add(nome)

    parametros = _parametros_de_funcao(arvore)

    def consumo_direto(valor: ast.AST) -> tuple[bool, list[str]]:
        """Sobe a árvore a partir do valor: (alcançou o agregado?, alvos de atribuição)."""
        atual: ast.AST = valor
        alvos: list[str] = []
        while atual in pais:
            pai = pais[atual]
            if isinstance(pai, ast.Call) and atual is not pai.func:
                if _consumo_alcanca_alguem(pai, arvore, pais, parametros):
                    return True, alvos
            if isinstance(pai, (ast.Assert, ast.Return)):
                return True, alvos
            if isinstance(pai, ast.Assign):
                for alvo in pai.targets:
                    alvos.extend(
                        n.id for n in ast.walk(alvo) if isinstance(n, ast.Name)
                    )
                return False, alvos
            if isinstance(pai, ast.AnnAssign):
                if isinstance(pai.target, ast.Name):
                    alvos.append(pai.target.id)
                return False, alvos
            if isinstance(pai, ast.NamedExpr):
                if isinstance(pai.target, ast.Name):
                    alvos.append(pai.target.id)
                atual = pai
                continue
            if isinstance(pai, ast.stmt):
                return False, alvos
            atual = pai
        return False, alvos

    # atribuições nome→nome, para o fecho de alias do fluxo do retorno
    atribuicoes_de_nome: list[tuple[str, str]] = [
        (alvo.id, no.value.id)
        for no in ast.walk(arvore)
        if isinstance(no, ast.Assign) and isinstance(no.value, ast.Name)
        for alvo in no.targets
        if isinstance(alvo, ast.Name)
    ]

    com_efeito: set[str] = set()
    sem_efeito: list[tuple[str, int]] = []
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Call):
            continue
        nome = _canonico_da_chamada(no, alias)
        if nome not in FUNCOES_OBRIGATORIAS:
            continue
        consumida, alvos = consumo_direto(no)
        if consumida:
            com_efeito.add(nome)
            continue
        fluxo = set(alvos)
        mudou = True
        while mudou:
            mudou = False
            for destino, origem in atribuicoes_de_nome:
                if origem in fluxo and destino not in fluxo:
                    fluxo.add(destino)
                    mudou = True
        consumido_por_nome = False
        if fluxo:
            for uso in ast.walk(arvore):
                if (
                    isinstance(uso, ast.Name)
                    and isinstance(uso.ctx, ast.Load)
                    and uso.id in fluxo
                    and consumo_direto(uso)[0]
                ):
                    consumido_por_nome = True
                    break
        if consumido_por_nome:
            com_efeito.add(nome)
        else:
            sem_efeito.append((nome, no.lineno))
    return importa, chamadas, com_efeito, sem_efeito


def _autoteste_da_cobertura() -> list[str]:
    """A análise de efeito prova que enxerga, a cada chamada.

    Sem isto, a mutação que devolve a cobertura ao estado da rodada 2 (chamada
    basta, efeito não é conferido) deixaria os quinze verdes — e a amostra que
    descarta os retornos passaria a ser aceitável de novo. A amostra boa está
    junto pelo motivo de sempre: análise que grita nos idiomas legítimos da
    casa é desligada na semana seguinte.
    """
    try:
        _, _, com_bom, sem_bom = _chamadas_com_efeito(_AMOSTRA_COBERTURA_COM_EFEITO)
        _, _, com_ruim, sem_ruim = _chamadas_com_efeito(_AMOSTRA_COBERTURA_SEM_EFEITO)
    except Exception as exc:  # noqa: BLE001
        return [
            f"DETECTOR_DE_EFEITO_QUEBRADO: o autoteste da análise de efeito "
            f"levantou {exc.__class__.__name__}: {exc}"
        ]
    erros: list[str] = []
    consumidas_faltando = sorted(set(FUNCOES_OBRIGATORIAS) - com_bom)
    if consumidas_faltando or sem_bom:
        erros.append(
            "DETECTOR_DE_EFEITO_GRITA_NO_INOCENTE: a amostra que consome os "
            "retornos nos idiomas reais da casa saiu com "
            f"faltando={consumidas_faltando} e descartadas={sem_bom}; análise "
            "que reprova o idioma legítimo é desligada, não obedecida"
        )
    descartadas_vistas = {nome for nome, _ in sem_ruim}
    nao_acusadas = sorted(set(FUNCOES_OBRIGATORIAS) - descartadas_vistas)
    if nao_acusadas or (com_ruim & set(FUNCOES_OBRIGATORIAS)):
        erros.append(
            "DETECTOR_DE_EFEITO_CEGO: a amostra que descarta os quatro retornos "
            f"não foi acusada por inteiro (não acusadas={nao_acusadas}, "
            f"tidas como com efeito={sorted(com_ruim)}); análise que não acusa "
            "o descarte conhecido não autoriza concluir nada sobre a árvore"
        )
    erros.extend(_autoteste_do_agregador())
    erros.extend(_autoteste_do_alias())
    erros.extend(_autoteste_do_teto())
    erros.extend(_autoteste_do_digest_truncado())
    erros.extend(_autoteste_da_exclusao())
    return erros


# TAREFA 98 — as amostras que a ÁRVORE REAL NÃO TEM.
#
# Medido em 2026-08-22: os dezesseis validadores vivos usam um único idioma
# (`cases.append(...)` com `len(cases)` no relato), e por isso a árvore inteira
# não contém **nenhum** dos quatro casos que decidem esta regra. Mutante que só
# a árvore real exercitaria sobrevive — padrão que já custou quatro rodadas a
# esta casa. Cada amostra isola UMA decisão.
_AMOSTRAS_DO_AGREGADOR = (
    (
        "agregador de nome DESCONHECIDO, com recipiente lido — inocente",
        """from _compartilhado.verificacoes_estrutura import validate_trava_de_digest

def run():
    placar = Placar()
    placar.registrar(validate_trava_de_digest(STRUCTURE_ROOT))
    return placar
""",
        True,
    ),
    (
        "recipiente de nome CONHECIDO que ninguém lê — vácuo",
        """from _compartilhado.verificacoes_estrutura import validate_trava_de_digest

def run():
    lixo = []
    lixo.append(validate_trava_de_digest(STRUCTURE_ROOT))
    cases = []
    return len(cases)
""",
        False,
    ),
    (
        "print() não agrega, e o nome dele nunca esteve na lista",
        """from _compartilhado.verificacoes_estrutura import validate_trava_de_digest

def run():
    print(validate_trava_de_digest(STRUCTURE_ROOT))
""",
        False,
    ),
    (
        "o recipiente é PARÂMETRO — quem lê está fora do arquivo",
        """from _compartilhado.verificacoes_estrutura import validate_trava_de_digest

def acrescenta(cases):
    cases.append(validate_trava_de_digest(STRUCTURE_ROOT))
""",
        True,
    ),
    (
        "função livre do idioma da casa continua valendo",
        """from _compartilhado.verificacoes_estrutura import validate_trava_de_digest

def run():
    check("trava de digest", validate_trava_de_digest(STRUCTURE_ROOT))
""",
        True,
    ),
    (
        "valor atribuído a nome MORTO não alcança ninguém",
        """from _compartilhado.verificacoes_estrutura import validate_trava_de_digest

def run():
    ignorado = validate_trava_de_digest(STRUCTURE_ROOT)
    return 0
""",
        False,
    ),
)


def _autoteste_do_agregador() -> list[str]:
    """A regra do efeito sabe decidir sem consultar o nome de quem recebe."""
    erros: list[str] = []
    for nome, fonte, espera_efeito in _AMOSTRAS_DO_AGREGADOR:
        try:
            _, _, com, _sem = _chamadas_com_efeito(fonte)
        except Exception as exc:  # noqa: BLE001
            erros.append(
                f"DETECTOR_DE_EFEITO_QUEBRADO: a amostra {nome!r} levantou "
                f"{exc.__class__.__name__}"
            )
            continue
        obtido = "validate_trava_de_digest" in com
        if obtido != espera_efeito:
            erros.append(
                "DETECTOR_DE_EFEITO_DECIDE_POR_NOME: a amostra %r saiu como %s "
                "e devia sair como %s — o reconhecimento voltou a depender de "
                "COMO SE CHAMA quem recebe, em vez de SE O RECIPIENTE É LIDO"
                % (nome, "COM EFEITO" if obtido else "SEM EFEITO",
                   "COM EFEITO" if espera_efeito else "SEM EFEITO")
            )
    return erros


# TAREFA 99 — as QUATRO formas de apelido, e a sombra.
#
# Medido em 2026-08-22: os dezesseis validadores vivos chamam tudo pelo nome
# direto, então a árvore inteira não contém **nenhuma** destas formas. Mutante
# que só a árvore real exercitaria sobrevive.
_AMOSTRAS_DO_ALIAS = (
    ("chamada direta continua reconhecida",
     "from _compartilhado.verificacoes_estrutura import validate_trava_de_digest\n\ndef run():\n    cases = []\n"
     "    cases.append(validate_trava_de_digest(STRUCTURE_ROOT))\n    return len(cases)\n",
     True, False),
    ("apelido por atribuição",
     "from _compartilhado.verificacoes_estrutura import validate_trava_de_digest\n\ndef run():\n    g = validate_trava_de_digest\n    cases = []\n"
     "    cases.append(g(STRUCTURE_ROOT))\n    return len(cases)\n",
     True, False),
    ("apelido no import (`as`)",
     "from _compartilhado.verificacoes_estrutura import validate_trava_de_digest as vtd"
     "\n\ndef run():\n    cases = []\n"
     "    cases.append(vtd(STRUCTURE_ROOT))\n    return len(cases)\n",
     True, False),
    ("getattr com nome literal",
     "import _compartilhado.verificacoes_estrutura as m\n\ndef run():\n    cases = []\n"
     "    cases.append(getattr(m, \"validate_trava_de_digest\")(STRUCTURE_ROOT))\n"
     "    return len(cases)\n",
     True, False),
    ("cadeia em ordem INVERSA — só o fecho transitivo alcança",
     'from _compartilhado.verificacoes_estrutura import validate_trava_de_digest\n\ndef run():\n    cases = []\n    def usar():\n        return cases.append(h(STRUCTURE_ROOT))\n    h = g\n    g = validate_trava_de_digest\n    return len(cases)\n',
     True, False),
    ("cadeia de apelidos (`g = f; h = g`)",
     "from _compartilhado.verificacoes_estrutura import validate_trava_de_digest\n\ndef run():\n    g = validate_trava_de_digest\n    h = g\n    cases = []\n"
     "    cases.append(h(STRUCTURE_ROOT))\n    return len(cases)\n",
     True, False),
    ("SOMBRA: o nome da trava vira um stub",
     "from _compartilhado.verificacoes_estrutura import validate_trava_de_digest\n\ndef run():\n    validate_trava_de_digest = lambda *a: []\n    cases = []\n"
     "    cases.append(validate_trava_de_digest(STRUCTURE_ROOT))\n    return len(cases)\n",
     True, True),
    ("quem não chama continua não chamando",
     "from _compartilhado.verificacoes_estrutura import validate_trava_de_digest\n\ndef run():\n    cases = []\n    return len(cases)\n",
     False, False),
)


def _autoteste_do_alias() -> list[str]:
    """O apelido é resolvido na fronteira da chamada, e a sombra é acusada."""
    erros: list[str] = []
    for nome, fonte, espera_chamada, espera_sombra in _AMOSTRAS_DO_ALIAS:
        try:
            _, chamadas, _com, _sem = _chamadas_com_efeito(fonte)
            sombras = travas_sombreadas(fonte)
        except Exception as exc:  # noqa: BLE001
            erros.append(
                f"DETECTOR_DE_ALIAS_QUEBRADO: a amostra {nome!r} levantou "
                f"{exc.__class__.__name__}"
            )
            continue
        if ("validate_trava_de_digest" in chamadas) != espera_chamada:
            erros.append(
                "DETECTOR_DE_ALIAS_CEGO: a amostra %r %s reconhecida como "
                "chamada — o fecho de apelido não alcança a fronteira da "
                "chamada, e quem cumpriu é acusado" % (
                    nome, "NÃO foi" if espera_chamada else "foi")
            )
        if bool(sombras) != espera_sombra:
            erros.append(
                "DETECTOR_DE_SOMBRA_%s: a amostra %r %s acusada de sombra — "
                "resolver apelido sem fechar esta porta troca falso positivo "
                "por falso NEGATIVO" % (
                    "CEGO" if espera_sombra else "GRITA_NO_INOCENTE", nome,
                    "NÃO foi" if espera_sombra else "foi")
            )
    return erros


# ---------------------------------------------------------------------------
# TAREFA 100 — o teto declarado morava numa FIXTURE
# ---------------------------------------------------------------------------
#
# Até 2026-08-22 duas funções deste módulo declaravam o próprio teto apontando
# para fora do pacote: `_ligacoes_locais` dizia *"Teto declarado no
# `manifest.json::o_que_este_mecanismo_NAO_pega`"* e `_chamadas_com_efeito`
# fechava com *"os dois estão nomeados no manifest do candidato"*.
#
# Medido: essa chave **não existe em nenhum artefato de pacote**. Ela só aparece
# em manifestos de CANDIDATO de duas campanhas, todos dentro de `evals/`. O
# código de produção apontava o próprio teto para um arquivo que não é dele — e
# quem lesse a docstring não tinha onde chegar. É
# `clausula-presente-mas-inalcancavel` outra vez.
#
# **E o teto encolhia sem vermelho.** A rodada 2 daquela campanha REMOVEU itens
# da chave, e isso só foi apanhado por leitura humana. Teto que só encolhe em
# silêncio não é limite declarado: é orçamento.
#
# Duas coisas mudam aqui. O teto passa a viver **no pacote**, nomeado, ao lado
# do código que ele limita; e o número de limites vira **derivado** com piso
# explícito, no molde da tarefa 94 — baixar exige editar o piso, que é uma linha
# comentada que alguém lê, e não uma remoção silenciosa.
#
# ATUALIZADO PELO QUE AS TAREFAS 98 E 99 MEDIRAM, e é por isso que a tarefa 100
# esperava por elas: os limites de hoje não são os de 2026-08-05.
TETOS_DO_MECANISMO: dict[str, tuple[str, ...]] = {
    "_chamadas_com_efeito": (
        "o rastreio é sintático e global ao arquivo: não prova que o valor "
        "DECIDE o veredito — um retorno usado só como detalhe de mensagem conta "
        "como consumido",
        "consumo por fluxo de controle (`if erros: ...` sem return) não é "
        "reconhecido — este lado é estrito, o de cima é permissivo",
        "chamada de FUNÇÃO LIVRE continua reconhecida por NOME, contra uma lista "
        "de cinco: ela descarta o resultado e não tem recipiente, logo é "
        "indistinguível de `print(...)` por fluxo de dados puro (tarefa 98)",
        "recipiente que chega por PARÂMETRO é tratado como lido, porque quem o "
        "consome está fora do arquivo — permissivo por escolha declarada, para "
        "não acusar o idioma legítimo (tarefa 98)",
    ),
    "_ligacoes_locais": (
        "a primeira ligação de cada nome é a registrada — a linha serve para o "
        "leitor achar o sítio, não para contar ocorrências",
    ),
    "_alias_de_funcao": (
        "`getattr` só é resolvido com nome LITERAL: nome computado em tempo de "
        "execução não é alcançável por análise estática (tarefa 99)",
        "a sombra é detectada por arquivo — um nome de trava reatribuído em "
        "outro módulo e importado daqui não é visto (tarefa 99)",
    ),
}

# DERIVADO, nunca digitado — e com PISO explícito, que é o que torna o encolher
# vermelho. Baixar o piso é uma edição visível e comentada; remover um limite em
# silêncio deixa de ser possível.
LIMITES_DECLARADOS = sum(len(v) for v in TETOS_DO_MECANISMO.values())
PISO_DE_LIMITES_DECLARADOS = 7


def validate_tetos_no_pacote(fonte: str) -> list[str]:
    """Todo teto declarado mora AQUI, e a lista não encolhe em silêncio.

    Três perguntas, e cada uma nasceu de um defeito medido:

    1. **Alguma docstring aponta o teto para fora do pacote?** Era o defeito de
       origem — `manifest.json::o_que_este_mecanismo_NAO_pega` não existe em
       artefato de pacote nenhum.
    2. **Toda função que declara teto tem entrada?** Senão o limite existe na
       prosa e não na estrutura, e ninguém consegue contá-lo.
    3. **A lista encolheu abaixo do piso?** É a catraca da tarefa 94 aplicada a
       limites em vez de dívida.
    """
    erros: list[str] = []
    try:
        arvore = ast.parse(fonte)
    except SyntaxError as exc:
        return [f"TETOS_NAO_AVALIADOS: o módulo não parseia ({exc.__class__.__name__})"]

    declaram: set[str] = set()
    for no in ast.walk(arvore):
        if not isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        doc = ast.get_docstring(no) or ""
        if "Teto declarado" not in doc:
            continue
        declaram.add(no.name)
        if "manifest.json" in doc or "manifest do candidato" in doc:
            erros.append(
                f"TETO_FORA_DO_PACOTE: `{no.name}` aponta o próprio teto para um "
                "`manifest.json` de candidato. Essa chave não existe em artefato "
                "de pacote nenhum — quem lê a docstring não tem onde chegar "
                "(tarefa 100)"
            )
        if no.name not in TETOS_DO_MECANISMO:
            erros.append(
                f"TETO_SEM_ENTRADA: `{no.name}` declara teto na prosa e não tem "
                "entrada em TETOS_DO_MECANISMO — limite que não está na "
                "estrutura não pode ser contado nem vigiado"
            )
    for nome in sorted(set(TETOS_DO_MECANISMO) - declaram):
        erros.append(
            f"TETO_DECLARADO_SEM_DONO: `{nome}` tem entrada em "
            "TETOS_DO_MECANISMO e a função não declara teto na docstring — "
            "entrada que aponta para o vazio dá sensação de cobertura"
        )
    if not TETOS_DO_MECANISMO:
        erros.append(
            "VARREDURA_DE_TETO_CEGA: TETOS_DO_MECANISMO está vazio, e a casa "
            "tem limites medidos. Zero de detector é suspeita, não conformidade"
        )
    if LIMITES_DECLARADOS < PISO_DE_LIMITES_DECLARADOS:
        erros.append(
            f"TETO_ENCOLHEU: os limites declarados caíram para "
            f"{LIMITES_DECLARADOS} e o piso é {PISO_DE_LIMITES_DECLARADOS}. "
            "Limite não some porque alguém apagou a linha: ou o mecanismo "
            "melhorou e o piso desce POR EDIÇÃO EXPLÍCITA, ou o limite continua "
            "valendo. A rodada 2 de `producao-honesta` removeu itens desta "
            "chave e só foi apanhada por leitura humana (tarefa 100)"
        )
    return erros


_AMOSTRAS_DO_TETO = (
    ('as três declaram e as três têm entrada — silêncio',
     'def _chamadas_com_efeito():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\ndef _ligacoes_locais():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\ndef _alias_de_funcao():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\n',
     False),
    ('teto apontando para manifest de candidato — o defeito de origem',
     'def _chamadas_com_efeito():\n    """resumo.\n\n    Teto declarado no `manifest.json::o_que_este_mecanismo_NAO_pega`.\n    """\n\n\ndef _ligacoes_locais():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\ndef _alias_de_funcao():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\n',
     True),
    ('função declara teto e NÃO tem entrada',
     'def _chamadas_com_efeito():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\ndef _ligacoes_locais():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\ndef _alias_de_funcao():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\ndef _funcao_que_nao_esta_na_lista():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\n',
     True),
    ('entrada sem dono: a função sumiu do módulo',
     'def _chamadas_com_efeito():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\ndef _ligacoes_locais():\n    """resumo.\n\n    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo.\n    """\n\n\n',
     True),
)


def _autoteste_do_teto() -> list[str]:
    """A trava do teto sabe reprovar, e sabe não reprovar quem cumpriu."""
    erros: list[str] = []
    for nome, fonte, espera in _AMOSTRAS_DO_TETO:
        obtido = bool(validate_tetos_no_pacote(fonte))
        if obtido != espera:
            erros.append(
                "DETECTOR_DE_TETO_%s: a amostra %r saiu como %s"
                % ("CEGO" if espera else "GRITA_NO_INOCENTE", nome,
                   "acusação" if obtido else "silêncio")
            )
    if LIMITES_DECLARADOS != sum(len(v) for v in TETOS_DO_MECANISMO.values()):
        erros.append("o número de limites deixou de ser derivado da estrutura")
    return erros



# ---------------------------------------------------------------------------
# TAREFA 102 — digest publicado como ALEGAÇÃO CORRENTE aparece por inteiro
# ---------------------------------------------------------------------------
#
# `departamento-seguranca` publicava *"154 arquivos · 956.235 bytes · digest
# `d92607a3…1d83` **idêntico**"* numa linha de tabela marcada **executado: sim**,
# e o valor completo não existia em lugar nenhum do arquivo. Pior: o objeto da
# alegação **não está no pacote** — os arquivos legados vivem fora da Estrutura e
# o validador não carrega manifesto de legado. Quem lesse a linha não tinha o que
# executar.
#
# Reexecutado em 2026-08-22, o número estava **certo** — 154 arquivos, 956.235
# bytes, mesmo digest. O defeito nunca foi o número: era não poder conferi-lo.
#
# O DISCRIMINADOR É LINHA DE TABELA versus PROSA, e ele foi medido antes de
# existir: dos cinco digests truncados sem forma completa nos dezesseis pacotes,
# QUATRO são citação narrativa — duas comparando o mesmo conteúdo em LF e em CRLF
# (onde o ponto É que diferem), uma citando o valor que o `departamento-registros`
# **rejeitou** por irreprodutível, e uma sobre uma árvore restaurada. Acusá-las
# seria `gate-que-barra-evidencia-boa`. Só a linha de tabela afirma **agora**.
_DIGEST_TRUNCADO = re.compile(r"`?([0-9a-f]{8})[0-9a-f]*[…]{1,3}[0-9a-f]{0,8}`?")
_DIGEST_COMPLETO = re.compile(r"[0-9a-f]{64}")


def digests_truncados_sem_original(texto: str) -> list[str]:
    """Digest truncado numa LINHA DE TABELA cujo valor inteiro não está no arquivo.

    Prosa que cita um digest truncado é narrativa e não pede reprodução; linha de
    tabela de placar é **alegação corrente**, e alegação que ninguém pode conferir
    não é evidência.
    """
    completos = {m.group(0)[:8] for m in _DIGEST_COMPLETO.finditer(texto)}
    erros: list[str] = []
    for numero, linha in enumerate(texto.splitlines(), 1):
        if not linha.lstrip().startswith("|"):
            continue
        for achado in _DIGEST_TRUNCADO.finditer(linha):
            prefixo = achado.group(1)
            if prefixo in completos:
                continue
            erros.append(
                f"DIGEST_TRUNCADO_SEM_ORIGINAL: a linha {numero} publica "
                f"`{prefixo}…` como alegação corrente e o valor inteiro não "
                "aparece no arquivo. Quem lê não tem o que conferir — publique o "
                "digest completo e a receita que o reproduz (tarefa 102)"
            )
    return erros


_AMOSTRAS_DO_DIGEST = (
    ("linha de tabela com digest truncado e sem o inteiro — acusa",
     "| item | digest `d92607a3…1d83` | **sim** |\n", True),
    ("a mesma linha, com o valor inteiro em outro ponto do arquivo — silêncio",
     "| item | digest `d92607a3…1d83` | **sim** |\n\nreceita: "
     "d92607a3fa32f80c44b9a9b18bfce20b16a7c8b69bc5d0756b24754fc3ad1d83\n", False),
    ("PROSA citando digest truncado — narrativa, não alegação",
     "Doze variantes foram testadas e nenhuma reproduziu `7a6809ac…`.\n", False),
    ("linha de tabela sem digest nenhum — silêncio",
     "| item | 154 arquivos | **sim** |\n", False),
)


def _autoteste_do_digest_truncado() -> list[str]:
    """A trava separa alegação corrente de citação narrativa."""
    erros: list[str] = []
    for nome, texto, espera in _AMOSTRAS_DO_DIGEST:
        obtido = bool(digests_truncados_sem_original(texto))
        if obtido != espera:
            erros.append(
                "DETECTOR_DE_DIGEST_%s: a amostra %r saiu como %s"
                % ("CEGO" if espera else "GRITA_NO_INOCENTE", nome,
                   "acusação" if obtido else "silêncio")
            )
    return erros



# ---------------------------------------------------------------------------
# TAREFA 60 — todo gate publica suas exclusões, ou declara que não tem
# ---------------------------------------------------------------------------
#
# A pepita veio do `/cso` do gstack, que roda OWASP+STRIDE **declarando 17
# exclusões de falso positivo e corte de confiança em 8/10**. É a resposta deles
# ao defeito que mordeu esta casa em 2026-08-07: um detector de mojibake que
# acusava `NÃO`, `DECLARAÇÃO` e `SUPOSIÇÃO` e fechava o portão sobre saída
# íntegra — `gate-que-barra-evidencia-boa`.
#
# **A MEDIÇÃO CORRIGIU O MEU PRIMEIRO DETECTOR, e isso vale mais que a trava.**
# Comecei procurando gates que contêm `continue` e achei SETE que "excluem sem
# declarar". Lendo cada `continue`, a maioria é **mecânica de laço** — `not
# path.is_file()`, `not match`, `not isinstance(...)` — e não política. Uma
# trava construída sobre aquele proxy exigiria declaração para mecânica pura, e
# seria ruído com cara de rigor: o mesmo defeito que ela existe para combater.
#
# O que é POLÍTICA e é checável sem ambiguidade: **consultar uma constante de
# exclusão NOMEADA**. Medido, são QUATRO funções, e é sobre elas que a
# declaração passa a ser obrigatória.
#
# **O LIMIAR: esta casa não tem, e declarar isso É a resposta.** Os gates daqui
# são binários — passa ou não passa —, sem corte de confiança e sem taxa de
# falso positivo publicada. A forma que a tarefa pede admite as duas saídas
# ("ou declara que não tem nenhum"), e a honesta aqui é a segunda.
LIMIAR_DE_CONFIANCA_DA_CASA = None  # binário, e declarado — ver acima

# AS CONSTANTES DE EXCLUSÃO SÃO DECLARADAS AQUI, E NÃO DERIVADAS DO REGISTRO.
#
# A primeira versão desta trava derivava o conjunto de constantes conhecidas das
# próprias entradas de `EXCLUSOES_DO_GATE` — e o mutante M1 mostrou o buraco:
# apagar uma entrada apagava JUNTO a evidência da falta dela, porque a constante
# saía do conjunto e a função deixava de contar como "consulta exclusão". O
# registro definia o que conta, então não conseguia notar a própria ausência.
#
# É a mesma cegueira auto-referencial do mutante M10 da tarefa 104: lista que
# vigia os detectores e ninguém vigia a lista. Aqui a lista de CONSTANTES é
# independente, e as ENTRADAS são conferidas contra ela.
CONSTANTES_DE_EXCLUSAO = (
    "_PASTAS_QUE_NAO_SAO_PACOTE",
    "ADR_HISTORICAL_EXCEPTIONS",
    "COBERTURA_EXCECOES",
    "_AGREGADORES_LIVRES",
)

EXCLUSOES_DO_GATE: dict[str, dict] = {
    "_pacotes_gerentes": {
        "constantes": ("_PASTAS_QUE_NAO_SAO_PACOTE",),
        "deixa_de_fora": (
            "`agentes/` — agente é folha e não é pacote gerente",
            "`fontes-legadas-pinadas/` — cópia byte-exata de fonte externa, "
            "congelada por `.gitattributes`, não é pacote desta casa",
            "`evals/` — campanha guarda `references/` inteiros do pacote "
            "julgado; sem isto o original colide com a própria evidência",
        ),
    },
    "validate_adr_series": {
        "constantes": ("_PASTAS_QUE_NAO_SAO_PACOTE", "ADR_HISTORICAL_EXCEPTIONS"),
        "deixa_de_fora": (
            "as mesmas três pastas acima — cópia de laboratório não cunha número",
            "os TRÊS `adr-001` de `ceo-maestro`, `diretor-de-lentes` e "
            "`departamento-negocios`, isentos POR CAMINHO EXATO e nunca por "
            "número: um quarto `adr-001` em qualquer outro lugar reprova o grupo",
        ),
    },
    "_consumo_alcanca_alguem": {
        "constantes": ("_AGREGADORES_LIVRES",),
        "deixa_de_fora": (
            "chamada de FUNÇÃO LIVRE fora dos cinco nomes do idioma da casa — "
            "ela descarta o resultado e não tem recipiente, logo é "
            "indistinguível de `print(...)` por fluxo de dados puro (tarefa 98)",
        ),
    },
    "validate_cobertura_de_validadores": {
        "constantes": ("COBERTURA_EXCECOES",),
        "deixa_de_fora": (
            "os validadores nomeados em `COBERTURA_EXCECOES` — hoje a tupla "
            "está VAZIA, e uma exclusão vazia é o estado mais honesto que ela "
            "pode ter: a estrutura existe, ninguém a usa, e o dia em que "
            "alguém usar terá de escrever o nome",
        ),
    },
}


def validate_exclusoes_declaradas(fonte: str) -> list[str]:
    """Quem consulta constante de exclusão publica o que deixa de fora.

    A conferência é nos DOIS sentidos, como a da tarefa 104: função que consulta
    e não declara acusa; entrada que nomeia função inexistente ou constante que
    a função não consulta também acusa — lista que aponta para o vazio dá
    sensação de cobertura sem cobrir nada.
    """
    try:
        arvore = ast.parse(fonte)
    except SyntaxError as exc:
        return [f"EXCLUSOES_NAO_AVALIADAS: o módulo não parseia "
                f"({exc.__class__.__name__})"]

    conhecidas = set(CONSTANTES_DE_EXCLUSAO)
    consulta: dict[str, set[str]] = {}
    for no in ast.walk(arvore):
        if not isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        usadas = {x.id for x in ast.walk(no)
                  if isinstance(x, ast.Name) and x.id in conhecidas}
        if usadas:
            consulta[no.name] = usadas

    erros: list[str] = []
    for nome, usadas in sorted(consulta.items()):
        entrada = EXCLUSOES_DO_GATE.get(nome)
        if entrada is None:
            erros.append(
                f"EXCLUSAO_NAO_DECLARADA: `{nome}` consulta "
                f"{', '.join(sorted(usadas))} e não tem entrada em "
                "EXCLUSOES_DO_GATE. Gate que exclui em silêncio não é gate "
                "calibrado — é gate com ponto cego não publicado (tarefa 60)"
            )
            continue
        faltam = usadas - set(entrada["constantes"])
        if faltam:
            erros.append(
                f"EXCLUSAO_PARCIALMENTE_DECLARADA: `{nome}` consulta "
                f"{', '.join(sorted(faltam))} e a entrada não a nomeia"
            )
        if not entrada.get("deixa_de_fora"):
            erros.append(
                f"EXCLUSAO_SEM_CONTEUDO: `{nome}` tem entrada e não diz O QUE "
                "deixa de fora — nomear a constante sem dizer o efeito é "
                "publicar o rótulo e esconder a decisão"
            )
    for nome in sorted(set(EXCLUSOES_DO_GATE) - set(consulta)):
        erros.append(
            f"EXCLUSAO_DECLARADA_SEM_USO: `{nome}` está em EXCLUSOES_DO_GATE e "
            "não consulta nenhuma constante de exclusão — entrada que aponta "
            "para o vazio dá sensação de cobertura"
        )
    if not EXCLUSOES_DO_GATE:
        erros.append(
            "VARREDURA_DE_EXCLUSAO_CEGA: EXCLUSOES_DO_GATE está vazio e esta "
            "casa tem exclusões medidas. Zero de detector é suspeita, não "
            "conformidade"
        )
    return erros


def _fonte_de_amostra(consulta: str | None, declara: bool) -> str:
    corpo = ("    for p in alvos:\n        if %s:\n            continue\n"
             % (consulta or "not p.is_file()"))
    return "def %s(alvos):\n%s" % (
        "validate_adr_series" if declara else "_gate_inedito", corpo)


_AMOSTRAS_DA_EXCLUSAO = (
    ("gate que consulta constante NOMEADA e tem entrada — silêncio",
     "def validate_adr_series(a):\n    for p in a:\n"
     "        if set(_PASTAS_QUE_NAO_SAO_PACOTE) & set(p.parts):\n"
     "            continue\n        if p in ADR_HISTORICAL_EXCEPTIONS:\n"
     "            continue\n"
     "def _pacotes_gerentes(r):\n    return _PASTAS_QUE_NAO_SAO_PACOTE\n"
     "def _consumo_alcanca_alguem(c):\n    return _AGREGADORES_LIVRES\n"
     "def validate_cobertura_de_validadores(r):\n    return COBERTURA_EXCECOES\n",
     False),
    ("gate NOVO que consulta e não declara — acusa",
     "def _gate_inedito(a):\n    for p in a:\n"
     "        if set(_PASTAS_QUE_NAO_SAO_PACOTE) & set(p.parts):\n"
     "            continue\n"
     "def validate_adr_series(a):\n    return (_PASTAS_QUE_NAO_SAO_PACOTE,"
     " ADR_HISTORICAL_EXCEPTIONS)\n"
     "def _pacotes_gerentes(r):\n    return _PASTAS_QUE_NAO_SAO_PACOTE\n"
     "def _consumo_alcanca_alguem(c):\n    return _AGREGADORES_LIVRES\n"
     "def validate_cobertura_de_validadores(r):\n    return COBERTURA_EXCECOES\n",
     True),
    ("mecânica de laço NÃO é exclusão e não é cobrada",
     "def _gate_inedito(a):\n    for p in a:\n"
     "        if not p.is_file():\n            continue\n"
     "def validate_adr_series(a):\n    return (_PASTAS_QUE_NAO_SAO_PACOTE,"
     " ADR_HISTORICAL_EXCEPTIONS)\n"
     "def _pacotes_gerentes(r):\n    return _PASTAS_QUE_NAO_SAO_PACOTE\n"
     "def _consumo_alcanca_alguem(c):\n    return _AGREGADORES_LIVRES\n"
     "def validate_cobertura_de_validadores(r):\n    return COBERTURA_EXCECOES\n",
     False),
    ("entrada declarada cuja função sumiu — acusa",
     "def validate_adr_series(a):\n    return (_PASTAS_QUE_NAO_SAO_PACOTE,"
     " ADR_HISTORICAL_EXCEPTIONS)\n"
     "def _consumo_alcanca_alguem(c):\n    return _AGREGADORES_LIVRES\n"
     "def validate_cobertura_de_validadores(r):\n    return COBERTURA_EXCECOES\n",
     True),
)


def _autoteste_da_exclusao() -> list[str]:
    """A trava separa POLÍTICA de mecânica, e cobra os dois sentidos."""
    erros: list[str] = []
    for nome, fonte, espera in _AMOSTRAS_DA_EXCLUSAO:
        obtido = bool(validate_exclusoes_declaradas(fonte))
        if obtido != espera:
            erros.append(
                "DETECTOR_DE_EXCLUSAO_%s: a amostra %r saiu como %s"
                % ("CEGO" if espera else "GRITA_NO_INOCENTE", nome,
                   "acusação" if obtido else "silêncio")
            )
    if LIMIAR_DE_CONFIANCA_DA_CASA is not None:
        erros.append(
            "a casa passou a ter limiar de confiança e ninguém o publicou como "
            "taxa: gate com corte precisa dizer o corte E a taxa de falso "
            "positivo que ele aceita (tarefa 60)"
        )
    return erros



_AMOSTRA_RECUSA_CHAMA = '''
from _compartilhado.verificacoes_estrutura import recusar_execucao_fora_da_fonte

if __name__ == "__main__":
    recusar_execucao_fora_da_fonte(STRUCTURE_ROOT)
    sys.exit(run())
'''

_AMOSTRA_RECUSA_SO_MENCIONA = '''
"""Este validador fala sobre recusar_execucao_fora_da_fonte na docstring."""
# TODO: chamar recusar_execucao_fora_da_fonte(STRUCTURE_ROOT) algum dia
TEXTO = "recusar_execucao_fora_da_fonte(STRUCTURE_ROOT)"

if __name__ == "__main__":
    sys.exit(run())
'''


def _autoteste_da_recusa() -> list[str]:
    """`_chama_recusa` prova que enxerga — e que não enxerga demais — a cada chamada.

    Mesmo remédio do `_autoteste_da_cobertura`, e pelo mesmo motivo medido duas
    vezes num dia só: **detector cego ao formato isenta em silêncio**. Se a
    detecção quebrar, a exigência da T55 vira verde universal e ninguém vê — a
    trava sumiria exatamente como o defeito que ela persegue.

    A amostra que só MENCIONA está aqui junto de propósito: validador de string
    aceitaria o nome dentro de docstring, comentário ou literal, e um gate que
    aprova prosa é gate que não trava nada.
    """
    try:
        chama = _chama_recusa(_AMOSTRA_RECUSA_CHAMA)
        menciona = _chama_recusa(_AMOSTRA_RECUSA_SO_MENCIONA)
    except Exception as exc:  # noqa: BLE001
        return [
            f"DETECTOR_DE_RECUSA_QUEBRADO: o autoteste levantou "
            f"{exc.__class__.__name__}: {exc}"
        ]
    erros: list[str] = []
    if not chama:
        erros.append(
            "DETECTOR_DE_RECUSA_CEGO: a amostra que CHAMA "
            f"{FUNCAO_DE_RECUSA} no ponto de entrada não foi reconhecida; "
            "detector que não vê a chamada real isenta a árvore inteira"
        )
    if menciona:
        erros.append(
            "DETECTOR_DE_RECUSA_GRITA_NO_INOCENTE: a amostra que apenas MENCIONA "
            f"{FUNCAO_DE_RECUSA} em docstring, comentário e literal foi contada "
            "como chamada; gate que aceita prosa não trava nada"
        )
    return erros


def validate_cobertura_de_validadores(
    structure_root: Path,
    *,
    excecoes: tuple[str, ...] = COBERTURA_EXCECOES,
) -> list[str]:
    """Todo pacote gerente tem validador próprio, e ele exercita a trava global.

    **A lacuna que este gate fecha.** A trava de estrutura inteira só vale se
    alguém a rodar. Em 2026-07-27, `departamento-desenvolvimento` era o único dos
    quinze fora dela — e ninguém percebeu, porque não havia nada que percebesse:
    a cobertura era combinada em prosa, e prosa não reprova. Pacote criado sem
    validador, ou com validador que não chama o tipo estrutura-inteira, agora vira
    FAIL do mesmo jeito que contrato sem seção vira FAIL.

    **O gate deriva a lista de pacotes da árvore**, pela mesma descoberta por
    posição de `validate_contratos_de_gerente`; não há registro central onde
    esquecer de inscrever o pacote novo. Gate declarado vira gate contornável.

    Conferimos **import, chamada e EFEITO**, não só o import que o ADR-015 pede:
    import sem chamada é dependência morta, e chamada com retorno descartado é o
    degrau seguinte da mesma erosão — a rodada 2 exigia a chamada, e
    `validate_trava_de_digest(ROOT)` numa linha solta satisfazia a cobertura com
    o retorno no lixo. Agora o retorno de cada função obrigatória precisa
    alcançar o agregado de erros (`_chamadas_com_efeito`), e retorno descartado
    vira `COBERTURA_SEM_EFEITO`, com arquivo e linha.

    `excecoes` são caminhos de pacote relativos a `structure_root`, com `/`, no
    molde fechado de `ADR_HISTORICAL_EXCEPTIONS`: nomeiam o pacote exato, nunca um
    padrão.
    """
    if not structure_root.is_dir():
        return [f"cobertura de validadores: raiz da estrutura ausente em {structure_root}"]

    root = structure_root.resolve()
    isentos = set(excecoes)
    errors: list[str] = _autoteste_da_cobertura() + _autoteste_da_recusa()
    for pacote in _pacotes_gerentes(root):
        relative = pacote.resolve().relative_to(root).as_posix()
        if relative in isentos:
            continue
        validador = pacote / "evals" / "validate_workflow.py"
        if not validador.is_file():
            errors.append(
                f"cobertura: pacote {relative} sem evals/validate_workflow.py"
            )
            continue
        try:
            importa, chamadas, com_efeito, sem_efeito = _chamadas_com_efeito(
                validador.read_text(encoding="utf-8")
            )
        except SyntaxError as exc:
            errors.append(f"cobertura: {relative}/evals/validate_workflow.py não parseia: {exc}")
            continue
        # TAREFA 99 — resolver apelido sem fechar a sombra trocaria um falso
        # positivo por um falso NEGATIVO, que é infinitamente pior.
        for sombra in travas_sombreadas(validador.read_text(encoding="utf-8")):
            errors.append(f"cobertura: {relative} — {sombra}")
        if not importa:
            errors.append(
                f"cobertura: {relative} não importa {MODULO_DE_ESTRUTURA}"
            )
        obrigatorias_ausentes = sorted(set(FUNCOES_OBRIGATORIAS) - chamadas)
        if obrigatorias_ausentes:
            errors.append(
                f"cobertura: {relative} não chama funções obrigatórias de estrutura: "
                f"{obrigatorias_ausentes}"
            )
        # T55 — a recusa de rodar do runtime só vale se TODO validador a chamar.
        # Ela é conferida aqui, e não em `FUNCOES_OBRIGATORIAS`, porque aquela
        # lista exige que o RETORNO alcance o agregado de erros — e esta função
        # não devolve erro: ela aborta com `SystemExit(3)` antes de qualquer
        # medição. Contrato diferente, exigência no mesmo lugar.
        #
        # Sem isto, bastaria alguém remover a chamada de um validador para ele
        # voltar a imprimir, do runtime, um placar que mede as skills do Catálogo
        # como se fossem pacotes da Estrutura — e nada acusaria. Trava que não se
        # autoexige erode em silêncio.
        if not _chama_recusa(validador.read_text(encoding="utf-8")):
            errors.append(
                f"RECUSA_AUSENTE: {relative}/evals/validate_workflow.py não chama "
                f"{FUNCAO_DE_RECUSA}(<raiz da estrutura>) no ponto de entrada. "
                "Sem ela, rodar a partir de .claude/skills ou .agents/skills "
                "devolve um número que mede outro objeto (T55)"
            )
        for nome, linha in sorted(sem_efeito):
            errors.append(
                f"COBERTURA_SEM_EFEITO: {relative}/evals/validate_workflow.py:"
                f"{linha} chama {nome} e DESCARTA o retorno; exigir a chamada "
                "não é exigir o efeito — o retorno precisa alimentar o agregado "
                "de erros do validador (argumento de check/case/condition/"
                "require/cases.append, assert ou return)"
            )
        funcoes_complementares = set(FUNCOES_DE_ESTRUTURA) - set(
            FUNCOES_OBRIGATORIAS
        )
        if not (chamadas & funcoes_complementares):
            errors.append(
                f"cobertura: {relative} não chama nenhuma função complementar de "
                f"estrutura: {sorted(funcoes_complementares)}"
            )
    return errors


# ---------------------------------------------------------------------------
# TRAVA 1 — a recusa de digest() existe, dispara, e ninguém a contorna por cópia
# ---------------------------------------------------------------------------


def _motor_compartilhado():
    """Devolve `(modulo, erros)`. Ausência vira NOME, nunca traceback.

    O import fica dentro da função de propósito. A rodada 1 provou o custo do
    contrário: os validadores importavam nomes que só existem no candidato, e
    aplicar o overlay pela metade levantava `ImportError` — que o
    `except ModuleNotFoundError` dos validadores **não captura**, porque é a
    subclasse tentando pegar o pai. Dez validadores morriam por traceback, sem
    sumário e sem dizer qual condição faltou.
    """
    try:
        from _compartilhado import validador_schema  # noqa: PLC0415
    except ImportError as exc:
        return None, [
            f"AUSENTE_MOTOR_COMPARTILHADO: não foi possível importar "
            f"{_MODULO_DO_MOTOR} ({exc.__class__.__name__}: {exc})"
        ]
    return validador_schema, []


def _superficie_do_motor(motor) -> tuple[set[str], list[str]]:
    """Nomes públicos do motor = `__all__` ∪ piso declarado.

    Derivar só do `__all__` faria a trava encolher junto com ele: bastaria tirar
    `digest` da lista para uma cópia privada de `digest` deixar de ser cópia. O
    piso é a defesa contra isso, e a divergência é acusada com nome.
    """
    declarados = getattr(motor, "__all__", None)
    erros: list[str] = []
    if not isinstance(declarados, (list, tuple)):
        erros.append(
            f"MOTOR_SEM___ALL__: {_ARQUIVO_DO_MOTOR} não declara __all__; "
            "a superfície pública passa a ser só o piso mínimo"
        )
        declarados = ()
    faltando = sorted(set(SUPERFICIE_MINIMA_DO_MOTOR) - set(declarados))
    if faltando:
        erros.append(
            f"MOTOR_COM_SUPERFICIE_ENCOLHIDA: {_ARQUIVO_DO_MOTOR} deixou de "
            f"declarar em __all__ {faltando}; o piso continua valendo"
        )
    superficie = {
        nome
        for nome in set(declarados) | set(SUPERFICIE_MINIMA_DO_MOTOR)
        if callable(getattr(motor, nome, None)) or nome in SUPERFICIE_MINIMA_DO_MOTOR
    }
    return superficie, erros


# Os módulos de onde importar um nome do motor é LEGÍTIMO: o próprio motor.
# Importar `digest` de qualquer outro lugar é cópia privada com outro carimbo.
_IMPORTS_LEGITIMOS_DO_MOTOR = ("_compartilhado.validador_schema", "validador_schema")


def _ligacoes_locais(fonte: str) -> dict[str, tuple[int, str]]:
    """`{nome LIGADO no arquivo: (linha, forma)}` — em qualquer profundidade.

    A rodada 2 só via `def`, e o parecer da rodada 2 nomeou o custo, com o
    exemplo pronto: `digest = lambda c: "sha256:" + c*64` era invisível, e
    `from hashlib import md5 as digest` e `d2 = d` também. Sombrear um nome não
    exige `def`: qualquer LIGAÇÃO de nome sombreia — lambda, import, atribuição,
    classe, parâmetro, alvo de `for`/`with`/`except`, walrus. Esta função
    enumera todas as formas estáticas de ligação que a AST descreve.

    O que fica de fora, com nome: ligação DINÂMICA (`globals()["digest"] = …`,
    `setattr(mod, "digest", …)`, monkeypatch em runtime) não aparece na AST.
    Teto declarado em `TETOS_DO_MECANISMO`, neste módulo (tarefa 100).

    A primeira ligação de cada nome é a registrada — a linha serve para o
    leitor achar o sítio, não para contar ocorrências.
    """
    achados: dict[str, tuple[int, str]] = {}

    def liga(nome: str, linha: int, forma: str) -> None:
        achados.setdefault(nome, (linha, forma))

    arvore = ast.parse(fonte)
    for no in ast.walk(arvore):  # toda LIGAÇÃO de nome, não só def
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            liga(no.name, no.lineno, "def")
            argumentos = no.args
            for p in (
                argumentos.posonlyargs + argumentos.args + argumentos.kwonlyargs
                + ([argumentos.vararg] if argumentos.vararg else [])
                + ([argumentos.kwarg] if argumentos.kwarg else [])
            ):
                liga(p.arg, no.lineno, "parâmetro")
        elif isinstance(no, ast.Lambda):
            argumentos = no.args
            for p in argumentos.posonlyargs + argumentos.args + argumentos.kwonlyargs:
                liga(p.arg, no.lineno, "parâmetro")
        elif isinstance(no, ast.ClassDef):
            liga(no.name, no.lineno, "class")
        elif isinstance(no, ast.Assign):
            forma = "lambda" if isinstance(no.value, ast.Lambda) else "atribuição"
            for alvo in no.targets:
                for interno in ast.walk(alvo):
                    if isinstance(interno, ast.Name):
                        liga(interno.id, no.lineno, forma)
        elif isinstance(no, (ast.AnnAssign, ast.AugAssign)):
            if isinstance(no.target, ast.Name):
                valor = getattr(no, "value", None)
                forma = "lambda" if isinstance(valor, ast.Lambda) else "atribuição"
                liga(no.target.id, no.lineno, forma)
        elif isinstance(no, ast.NamedExpr):
            if isinstance(no.target, ast.Name):
                liga(no.target.id, no.lineno, "atribuição")
        elif isinstance(no, (ast.For, ast.AsyncFor)):
            for interno in ast.walk(no.target):
                if isinstance(interno, ast.Name):
                    liga(interno.id, no.lineno, "alvo de for")
        elif isinstance(no, (ast.With, ast.AsyncWith)):
            for item in no.items:
                if item.optional_vars is not None:
                    for interno in ast.walk(item.optional_vars):
                        if isinstance(interno, ast.Name):
                            liga(interno.id, no.lineno, "alvo de with")
        elif isinstance(no, ast.ExceptHandler):
            if no.name:
                liga(no.name, no.lineno, "alvo de except")
        elif isinstance(no, ast.ImportFrom):
            if (no.module or "") in _IMPORTS_LEGITIMOS_DO_MOTOR:
                continue
            for alias in no.names:
                liga(alias.asname or alias.name, no.lineno, "import")
        elif isinstance(no, ast.Import):
            for alias in no.names:
                liga(alias.asname or alias.name.split(".")[0], no.lineno, "import")
    return achados


def _autoteste_da_trava_de_copia() -> list[str]:
    """A varredura de ligações prova que enxerga as quatro formas, a cada chamada.

    Sem isto, a mutação que devolve a varredura ao estado da rodada 2 (só `def`)
    deixaria os quinze validadores verdes — lambda, import e atribuição voltariam
    a ser invisíveis sem nada acusar. Com isto, apagar uma forma reprova o módulo
    em toda chamada. A amostra legítima está junto pelo motivo de sempre: trava
    que grita no inocente é desligada na semana seguinte.
    """
    erros: list[str] = []
    try:
        ligacoes = _ligacoes_locais(_AMOSTRA_COPIA_PRIVADA)
        legitimas = _ligacoes_locais(_AMOSTRA_COPIA_LEGITIMA)
    except Exception as exc:  # noqa: BLE001
        return [
            f"DETECTOR_DE_COPIA_QUEBRADO: o autoteste da trava de cópia levantou "
            f"{exc.__class__.__name__}: {exc}"
        ]
    superficie = set(SUPERFICIE_MINIMA_DO_MOTOR)
    for nome, forma_esperada in sorted(_ESPERADO_NA_AMOSTRA_DE_COPIA.items()):
        achado = ligacoes.get(nome)
        if achado is None:
            erros.append(
                f"DETECTOR_DE_COPIA_CEGO: a amostra de referência liga {nome} "
                f"(forma: {forma_esperada}) e a varredura não viu; varredura que "
                "não acusa o caso conhecido não autoriza concluir nada sobre a árvore"
            )
        elif achado[1] != forma_esperada:
            erros.append(
                f"DETECTOR_DE_COPIA_COM_FORMA_ERRADA: {nome} na amostra de "
                f"referência é {forma_esperada} e a varredura classificou como "
                f"{achado[1]}"
            )
    inocentes = sorted(set(legitimas) & superficie)
    if inocentes:
        erros.append(
            "DETECTOR_DE_COPIA_GRITA_NO_INOCENTE: a amostra legítima importa do "
            f"próprio motor e a varredura acusou {inocentes}; import do motor é a "
            "forma CERTA de usar o motor"
        )
    return erros


def validate_trava_de_digest(structure_root: Path) -> list[str]:
    """A recusa de `digest()` existe, **dispara**, e nenhum validador a contorna.

    Três coisas, porque a rodada 1 fechou uma e deixou as outras duas abertas.

    1. **A trava existe.** `DigestDeFixtureRecusado` é uma classe de exceção
       própria no motor compartilhado. Classe própria e não `ValueError` genérico
       porque mutante que morre por exceção qualquer é mutante creditado errado —
       7 de 11 saíram assim numa medição desta casa.
    2. **A trava dispara.** `digest()` recebe algo que não é um caractere e a
       recusa é conferida por comportamento, não por presença do nome. Presença
       de trava não é efeito de trava: a casa já viu trava sem call site, call
       site por nome e instrução de uso que desvia da trava, nessa ordem, em três
       frentes seguidas.
    3. **Ninguém tem cópia privada do motor.** Uma trava que mora no compartilhado
       não alcança quem redefine a função no próprio arquivo. Em 2026-08-05,
       `departamento-negocios/evals/validate_workflow.py` carregava `digest`,
       `json_pointer`, `is_type` e `validate_schema` próprios — a forma
       pré-conserto, byte a byte, fora do alcance de qualquer conserto no
       compartilhado. Sombrear um nome do motor passa a ser FAIL nomeado.

    Devolve lista de erros; **nunca levanta**. O chamador é um caso de eval e a
    morte precisa aparecer como caso vermelho, não como traceback que derruba o
    validador inteiro sem dizer qual condição falhou.
    """
    if not structure_root.is_dir():
        return [f"trava de digest: raiz da estrutura ausente em {structure_root}"]

    motor, erros = _motor_compartilhado()
    if motor is None:
        return erros

    # --- 1 e 2: a trava existe e dispara -----------------------------------
    trava = getattr(motor, _NOME_DA_TRAVA, None)
    if trava is None:
        erros.append(
            f"TRAVA_DIGEST_AUSENTE: {_ARQUIVO_DO_MOTOR} não expõe {_NOME_DA_TRAVA}; "
            "sem classe própria a recusa não é distinguível de uma explosão qualquer"
        )
    elif not (isinstance(trava, type) and issubclass(trava, BaseException)):
        erros.append(
            f"TRAVA_DIGEST_NAO_E_EXCECAO: {_NOME_DA_TRAVA} é {type(trava).__name__}, "
            "e uma trava que não é exceção não interrompe nada"
        )
        trava = None

    gerador = getattr(motor, "digest", None)
    if not callable(gerador):
        erros.append(
            f"AUSENTE_GERADOR_DE_FIXTURE: {_ARQUIVO_DO_MOTOR} não expõe digest()"
        )
    else:
        for rotulo, entrada in (
            ("string de 77 caracteres", "x" * 77),
            ("string vazia", ""),
            ("valor que não é str", 7),
        ):
            try:
                devolvido = gerador(entrada)
            except BaseException as exc:  # noqa: BLE001 — o tipo É a medida
                if trava is not None and isinstance(exc, trava):
                    continue
                erros.append(
                    f"TRAVA_DIGEST_CLASSE_ERRADA: digest({rotulo}) levantou "
                    f"{exc.__class__.__name__}, e não {_NOME_DA_TRAVA}; exceção "
                    "genérica se confunde com defeito acidental"
                )
            else:
                # Truncado: `digest("x" * 77)` devolve 4 935 caracteres, e uma
                # linha de FAIL desse tamanho torna a saída crua ilegível — o
                # oposto do que uma mensagem de erro existe para fazer.
                amostra = (
                    devolvido if len(str(devolvido)) <= 32
                    else str(devolvido)[:32] + f"…[{len(str(devolvido))} chars]"
                )
                erros.append(
                    f"TRAVA_DIGEST_INERTE: digest({rotulo}) devolveu {amostra!r} "
                    "em vez de recusar; com isso "
                    'digest(<qualquer coisa>).startswith("sha256:") volta a ser '
                    "verdadeiro por construção"
                )
        # A recusa não pode ser recusa de tudo: o uso legítimo continua de pé.
        try:
            legitimo = gerador("a")
        except BaseException as exc:  # noqa: BLE001
            erros.append(
                f'TRAVA_DIGEST_EXCESSIVA: digest("a") levantou '
                f"{exc.__class__.__name__}; o gerador de fixture precisa continuar gerando"
            )
        else:
            if legitimo != "sha256:" + "a" * 64:
                erros.append(
                    f'TRAVA_DIGEST_MUDOU_A_FORMA: digest("a") devolveu {legitimo!r}, '
                    'esperado "sha256:" + "a"*64'
                )

    # --- 3: nenhuma cópia privada do motor, em NENHUMA forma de ligação ----
    erros.extend(_autoteste_da_trava_de_copia())
    superficie, erros_superficie = _superficie_do_motor(motor)
    erros.extend(erros_superficie)

    root = structure_root.resolve()
    for validador in _validadores_canonicos(root):
        relativo = validador.resolve().relative_to(root).as_posix()
        try:
            ligacoes = _ligacoes_locais(validador.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:
            erros.append(f"cópia privada: {relativo} não parseia: {exc}")
            continue
        for nome in sorted(set(ligacoes) & superficie):
            linha, forma = ligacoes[nome]
            erros.append(
                f"COPIA_PRIVADA_DO_MOTOR: {relativo}:{linha} liga {nome} por "
                f"conta própria (forma: {forma}), sombreando {_ARQUIVO_DO_MOTOR}; "
                "conserto no compartilhado não alcança cópia privada, e sombrear "
                "não exige def — lambda, import e atribuição sombreiam igual"
            )
    return erros


# ---------------------------------------------------------------------------
# TRAVA 2 — nenhuma asserção verdadeira por construção sobre valor produzido
# ---------------------------------------------------------------------------


def _nome_chamado(no: ast.AST) -> str:
    """Nome simples de uma chamada: `f(...)` → `f`; `m.f(...)` → `f`."""
    if not isinstance(no, ast.Call):
        return ""
    alvo = no.func
    if isinstance(alvo, ast.Name):
        return alvo.id
    if isinstance(alvo, ast.Attribute):
        return alvo.attr
    return ""


def _e_producao(no: ast.AST, derivados: set[str]) -> bool:
    """O nó É um valor com forma de digest garantida pela própria produção?

    Duas formas contam: a chamada direta a uma produtora, e o `Name` que só foi
    atribuído a partir de uma produtora dentro do mesmo escopo. A segunda existe
    porque o desvio mais barato é uma linha: `d = candidate_digest_de_arvore(r)`
    e depois `d.startswith("sha256:")` — foi assim que um sítio tautológico
    sobreviveu à leitura humana da rodada 1.
    """
    if isinstance(no, ast.Call):
        nome = _nome_chamado(no)
        if nome in PRODUTORAS_DE_DIGEST:
            return True
        if nome == "hexdigest":
            return True
        return False
    if isinstance(no, ast.Name):
        return no.id in derivados
    return False


def _derivados_de_producao(escopo: ast.AST) -> set[str]:
    """Nomes cuja TODA atribuição vem de uma produtora — pelo FECHO TRANSITIVO.

    «Todas» e não «alguma»: um nome que às vezes recebe dado lido de disco não é
    produção garantida, e acusá-lo seria reprovar código legítimo. Trava que
    grita no inocente é desligada na semana seguinte.

    **O que a rodada 3 fechou.** A rodada 2 classificava cada atribuição com
    `_e_producao(valor, set())` — um salto só. A docstring dizia ter fechado o
    desvio de uma linha (`d = produtora(...)`), e o parecer respondeu que o
    segundo salto também custa uma linha: `d2 = d` escapava. Aqui a derivação é
    computada até PONTO FIXO — a cada volta, um nome já derivado conta como
    produção para o próximo, e `d2`, `d3` e o resto da cadeia entram. A regra
    «todas as atribuições» é reavaliada em cada volta: um nome da cadeia que
    também recebe valor de outra origem sai, e derruba quem só deriva dele.
    Termina porque o conjunto cresce monotonicamente e é limitado pelos nomes
    atribuídos no escopo.
    """
    atribuicoes: list[tuple[str, ast.expr | None]] = []
    for no in ast.walk(escopo):
        alvos: list[ast.expr] = []
        valor: ast.expr | None = None
        if isinstance(no, ast.Assign):
            alvos, valor = list(no.targets), no.value
        elif isinstance(no, (ast.AnnAssign, ast.AugAssign)):
            alvos, valor = [no.target], no.value
        elif isinstance(no, (ast.For, ast.comprehension)):
            alvos = [no.target]
            valor = None
        for alvo in alvos:
            if isinstance(alvo, ast.Name):
                atribuicoes.append((alvo.id, valor))

    derivados: set[str] = set()
    while True:  # ponto fixo: alias de alias também é produção
        de_producao: set[str] = set()
        de_outra_origem: set[str] = set()
        for nome, valor in atribuicoes:
            if valor is not None and _e_producao(valor, derivados):
                de_producao.add(nome)
            else:
                de_outra_origem.add(nome)
        proximos = de_producao - de_outra_origem
        if proximos == derivados:
            return derivados
        derivados = proximos


_PREDICADOS_DE_FORMA = ("startswith", "endswith")
_RE_MODULO = ("fullmatch", "match", "search")

# Os cinco nomes com que esta casa registra um caso. A regra 5 — «valor produzido
# usado cru como condição» — só vale DENTRO de uma asserção, e a restrição foi
# comprada com um falso positivo: `declared = declared or digest("a")` é um valor
# de FALLBACK, não uma condição, e a primeira versão do detector reprovou o
# `departamento-evolucao-skills` por causa dele. Fora de asserção, um produtor
# num `or` é um valor default legítimo.
_ASSERTIVAS = ("check", "case", "condition", "require")


def _condicoes_de_assercao(escopo: ast.AST) -> list[ast.AST]:
    """As expressões que são CONDIÇÃO de um caso, no idioma desta casa.

    O idioma é `check("<nome do caso>", <condição>)` — nome primeiro, string
    literal. A exigência de que o primeiro argumento seja string não é
    formalidade: `_compartilhado/teste_validador_schema.py` tem um `check` de
    outra família, `check(<schema>, <valor>, valid=…, name=…)`, e sem esta
    condição o detector lia `digest("a")` ali como asserção sobre o digest. Não
    é: é fixture alimentando um teste do MOTOR DE SCHEMA, e o que fica vermelho
    quando o motor quebra é o caso, não a fixture. Segundo falso positivo desta
    regra em um dia; ambos viraram fixture permanente logo abaixo.
    """
    alvos: list[ast.AST] = []
    for no in ast.walk(escopo):
        if isinstance(no, ast.Assert):
            alvos.append(no.test)
        elif (
            isinstance(no, ast.Call)
            and _nome_chamado(no) in _ASSERTIVAS
            and no.args
            and isinstance(no.args[0], ast.Constant)
            and isinstance(no.args[0].value, str)
        ):
            alvos.extend(no.args[1:])
    return alvos


def _achar_no_escopo(escopo: ast.AST, relativo: str) -> list[str]:
    derivados = _derivados_de_producao(escopo)
    achados: list[str] = []

    def acusa(no: ast.AST, regra: str, forma: str) -> None:
        # A TAG `[R<n>]` não é decoração: é o que permite ao autoteste conferir
        # REGRA A REGRA que cada uma dispara na própria fixture. Sem a tag, o
        # autoteste só contaria o total — e regra apagada se esconderia atrás
        # do total das outras, que foi exatamente o furo da rodada 2.
        achados.append(
            f"CHECK_TAUTOLOGICO[{regra}]: {relativo}:{getattr(no, 'lineno', 0)} — {forma}; "
            "o sujeito é um valor PRODUZIDO por uma função de digest desta casa, "
            "logo a asserção é verdadeira por construção e a linha não pode ficar "
            "vermelha. Compare com um valor DECLARADO em outro lugar"
        )

    for no in ast.walk(escopo):
        # R1: <produção>.startswith("sha256:") / .endswith(...)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute):
            if no.func.attr in _PREDICADOS_DE_FORMA and _e_producao(
                no.func.value, derivados
            ):
                acusa(no, "R1", f"{no.func.attr}() sobre valor produzido")
                continue
            # R4: re.fullmatch(<literal>, <produção>)
            if no.func.attr in _RE_MODULO and len(no.args) >= 2:
                if _e_producao(no.args[1], derivados) and isinstance(
                    no.args[0], ast.Constant
                ):
                    acusa(no, "R4", f"re.{no.func.attr}() com padrão fixo sobre valor produzido")
                    continue
        # R2 e R3: len(<produção>) == N ; isinstance(<produção>, str)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name):
            if no.func.id == "isinstance" and no.args and _e_producao(
                no.args[0], derivados
            ):
                acusa(no, "R3", "isinstance() sobre valor produzido")
                continue
        if isinstance(no, ast.Compare) and isinstance(no.left, ast.Call):
            if (
                _nome_chamado(no.left) == "len"
                and no.left.args
                and _e_producao(no.left.args[0], derivados)
                and all(isinstance(c, ast.Constant) for c in no.comparators)
            ):
                acusa(no, "R2", "len() de valor produzido comparado a constante")
                continue
    # R5: a produção usada crua como condição — só DENTRO de uma asserção
    for condicao in _condicoes_de_assercao(escopo):
        if _e_producao(condicao, derivados):
            acusa(condicao, "R5", "valor produzido é a condição inteira da asserção")
            continue
        for no in ast.walk(condicao):
            if isinstance(no, ast.BoolOp):
                for operando in no.values:
                    if _e_producao(operando, derivados):
                        acusa(no, "R5", "valor produzido usado cru como condição booleana")
            elif isinstance(no, ast.UnaryOp) and isinstance(no.op, ast.Not):
                if _e_producao(no.operand, derivados):
                    acusa(no, "R5", "negação de valor produzido cru")
    return achados


def achar_checks_tautologicos(fonte: str, relativo: str = "<fonte>") -> list[str]:
    """Toda asserção verdadeira por construção sobre um valor produzido.

    Exposta no `__all__` porque é o que torna a trava **auditável**: quem
    duvidar do número roda esta função sobre a mesma árvore e chega ao mesmo
    conjunto, sem depender de quem leu os arquivos.
    """
    arvore = ast.parse(fonte)
    escopos: list[ast.AST] = [arvore]
    escopos.extend(
        no
        for no in ast.walk(arvore)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    achados: list[str] = []
    vistos: set[str] = set()
    for escopo in escopos:
        for achado in _achar_no_escopo(escopo, relativo):
            if achado not in vistos:
                vistos.add(achado)
                achados.append(achado)
    return sorted(achados)


def _autoteste_do_detector() -> list[str]:
    """O detector prova que enxerga, a cada chamada.

    Sem isto, esvaziar `achar_checks_tautologicos` para `return []` deixaria os
    quinze validadores verdes — o mesmo defeito que esta trava existe para
    impedir, uma camada acima. Mutação verde é pergunta, não aprovação.
    """
    erros: list[str] = []
    try:
        positivos = achar_checks_tautologicos(_AMOSTRA_TAUTOLOGICA, "<amostra-tautologica>")
        negativos = achar_checks_tautologicos(_AMOSTRA_LEGITIMA, "<amostra-legitima>")
    except Exception as exc:  # noqa: BLE001
        return [
            f"DETECTOR_QUEBRADO: o autoteste do detector levantou "
            f"{exc.__class__.__name__}: {exc}"
        ]
    if len(positivos) < _ESPERADO_NA_AMOSTRA_TAUTOLOGICA:
        erros.append(
            f"DETECTOR_CEGO: a amostra tautológica de referência tem "
            f"{_ESPERADO_NA_AMOSTRA_TAUTOLOGICA} sítios e o detector achou "
            f"{len(positivos)}; detector que não acusa o caso conhecido não "
            "autoriza concluir nada sobre a árvore"
        )
    if negativos:
        erros.append(
            "DETECTOR_GRITA_NO_INOCENTE: a amostra legítima de referência não "
            f"tem sítio tautológico e o detector acusou {len(negativos)}: "
            f"{negativos}"
        )

    # --- rodada 3: CADA regra dispara na própria fixture -------------------
    # A amostra tautológica acima só exercita R1 e R2. O julgamento da rodada 2
    # mediu o resto: R3, R4 e R5 nunca tinham disparado em lugar nenhum — e a R4
    # é a regra creditada pela descoberta da tautologia reescrita da rodada 1.
    # Apagar qualquer uma delas deixava os quinze verdes. Aqui, apagar reprova.
    for regra in sorted(_FIXTURAS_POR_REGRA):
        try:
            achados = achar_checks_tautologicos(
                _FIXTURAS_POR_REGRA[regra], f"<fixture-{regra}>"
            )
        except Exception as exc:  # noqa: BLE001
            erros.append(
                f"DETECTOR_QUEBRADO: a fixture da {regra} levantou "
                f"{exc.__class__.__name__}: {exc}"
            )
            continue
        da_regra = [a for a in achados if f"[{regra}]" in a]
        de_outras = [a for a in achados if f"[{regra}]" not in a]
        if not da_regra:
            erros.append(
                f"DETECTOR_SEM_A_REGRA: a fixture da {regra} existe para "
                f"disparar a {regra} e o detector devolveu "
                f"{len(achados)} acusação(ões), nenhuma da {regra}; regra que "
                "nunca dispara pode ser apagada sem que nada acuse — era o "
                "estado de R3, R4 e R5 na rodada 2"
            )
        if de_outras:
            erros.append(
                f"DETECTOR_COM_REGRA_TRANSBORDANDO: a fixture da {regra} "
                f"disparou também outra(s) regra(s): {de_outras}; fixture que "
                "dispara mais de uma regra não isola o que diz isolar"
            )

    # --- rodada 3: o fecho transitivo de alias enxerga a cadeia ------------
    try:
        alias = achar_checks_tautologicos(
            _AMOSTRA_ALIAS_TRANSITIVO, "<amostra-alias-transitivo>"
        )
        alias_legitimo = achar_checks_tautologicos(
            _AMOSTRA_ALIAS_LEGITIMO, "<amostra-alias-legitima>"
        )
    except Exception as exc:  # noqa: BLE001
        return erros + [
            f"DETECTOR_QUEBRADO: o autoteste do alias transitivo levantou "
            f"{exc.__class__.__name__}: {exc}"
        ]
    if len(alias) < _ESPERADO_NO_ALIAS:
        erros.append(
            "DETECTOR_CEGO_PARA_ALIAS: a amostra de alias transitivo tem "
            f"{_ESPERADO_NO_ALIAS} sítio a três saltos da produtora e o detector "
            f"achou {len(alias)}; d2 = d custa uma linha, e detector de um salto "
            "só é detector com o desvio publicado"
        )
    if alias_legitimo:
        erros.append(
            "DETECTOR_GRITA_NO_INOCENTE: na amostra de alias legítima o nome da "
            "cadeia também recebe valor de outra origem, e o detector acusou "
            f"{alias_legitimo}; «todas as atribuições» vale em cada passo do fecho"
        )
    return erros


def validate_sem_check_tautologico(structure_root: Path) -> list[str]:
    """Nenhum validador canônico afirma o que é verdadeiro por construção.

    **Por que por padrão e não por sítio.** A rodada 1 da tarefa 19 apagou dez
    `check` tautológicos, um a um, e a afordância ficou intacta: copiar
    `sha256_file(X).startswith("sha256:")` para um pacote novo continuava
    passando verde. Curar sítio não impede o próximo sítio. Esta função descreve
    a **forma** do defeito — sujeito produzido, predicado verdadeiro por
    construção — e por isso alcança o sítio que ainda não existe.

    Varre os `evals/validate_workflow.py` dos quinze pacotes gerentes e os
    módulos de `_compartilhado/`. Não varre os validadores congelados dentro de
    `evals/<campanha>/`: aqueles são registro de rodadas passadas, e reescrever
    registro para ficar verde é falsificar evidência.
    """
    if not structure_root.is_dir():
        return [f"check tautológico: raiz da estrutura ausente em {structure_root}"]

    erros = _autoteste_do_detector()

    root = structure_root.resolve()
    alvos = list(_validadores_canonicos(root))
    alvos.extend(sorted((root / "_compartilhado").glob("*.py")))
    for alvo in alvos:
        relativo = alvo.resolve().relative_to(root).as_posix()
        try:
            erros.extend(
                achar_checks_tautologicos(
                    alvo.read_text(encoding="utf-8"), relativo
                )
            )
        except (SyntaxError, UnicodeDecodeError) as exc:
            erros.append(f"check tautológico: {relativo} não parseia: {exc}")
    return erros


# ---------------------------------------------------------------------------
# TRAVA 4 — placar de pacote não declara total de cadeia no presente
# ---------------------------------------------------------------------------


_RE_TOTAL_DE_CADEIA = re.compile(
    r"cadeia[^.\n]{0,80}?(\d{3,})\s*/\s*(\d{3,})", re.I
)
_MARCAS_DE_PRESENTE = ("hoje", "atualmente", "no momento", "vigente")
_MARCAS_DE_PASSADO = ("naquela", "somava", "à época", "a época", "era de")


def achar_cadeia_no_presente(texto: str, origem: str) -> list[str]:
    """Acha alegação **corrente** de total de cadeia dentro de um placar.

    A forma do defeito: um número que só a cadeia inteira produz, afirmado no
    **presente**, dentro de um documento que mede **um pacote**. Nenhum pacote
    consegue rodar os quinze validadores, então nenhum pode saber o total de
    hoje — e o que ele escreve envelhece na primeira rodada que muda qualquer
    contagem.

    Citar o total no **passado, com data**, é legítimo: vira registro histórico.
    """
    erros = []
    for numero, linha in enumerate(texto.splitlines(), 1):
        achado = _RE_TOTAL_DE_CADEIA.search(linha)
        if not achado:
            continue
        baixa = linha.lower()
        if not any(marca in baixa for marca in _MARCAS_DE_PRESENTE):
            continue
        if any(marca in baixa for marca in _MARCAS_DE_PASSADO):
            continue
        erros.append(
            f"total de cadeia no presente: {origem}:{numero} afirma "
            f"{achado.group(1)}/{achado.group(2)} como estado corrente — "
            f"um placar de pacote não consegue medir a cadeia. Reescreva no "
            f"passado, com a data da medição."
        )
    return erros


def _declaradores_de_contagem(evals: Path) -> list[Path]:
    """Os arquivos VIGENTES que declaram contagem num pacote: placar e adendos.

    `glob` e não `rglob` de propósito — os congelados em `evals/<campanha>/` são
    registro de rodada passada e ficam de fora. O que muda de dono é a família:
    desde a tarefa 25 o número vive no adendo datado, não no placar, então varrer
    só o placar é varrer o arquivo que a casa já parou de usar para isso.
    """
    if not evals.is_dir():
        return []
    achados = [p for p in (evals / "PLACAR.md",) if p.is_file()]
    achados += sorted(evals.glob("PLACAR-ADENDO-*.md"))
    return achados


def _varrer_declaradores(root: Path) -> list[str]:
    """A varredura, separada do autoteste para o autoteste poder chamá-la.

    Sem esta separação o autoteste de sítio chamaria a função pública, que
    chama o autoteste, que chama a função pública — recursão infinita. O corte
    é aqui: esta parte só varre; quem decide se a varredura presta é o
    autoteste, e quem soma os dois é `validate_placar_nao_declara_cadeia`.
    """
    erros = []
    for pacote in _pacotes_gerentes(root):
        for declarador in _declaradores_de_contagem(pacote / "evals"):
            relativo = declarador.resolve().relative_to(root).as_posix()
            try:
                erros.extend(
                    achar_cadeia_no_presente(
                        declarador.read_text(encoding="utf-8"), relativo
                    )
                )
            except UnicodeDecodeError as exc:
                erros.append(f"total de cadeia: {relativo} não decodifica: {exc}")
    return erros


_FRASE_DE_AUTOTESTE = "A cadeia canônica hoje soma **1991/1991 PASS**.\n"


def _autoteste_de_sitio() -> list[str]:
    """A varredura se testa em SÍTIO, não só em forma (tarefa 51).

    O detector de forma já se testava e continuava verde enquanto a varredura
    olhava um arquivo de dois. Testar o detector e não o alcance é o mesmo
    `verificar-presenca-nao-e-verificar-efeito`: a peça funciona e não é
    chamada onde importa.

    Monta um pacote de mentira com a **mesma** frase em três lugares e exige o
    veredito de cada um — os dois vigentes acusam, o congelado não. O terceiro
    é o que impede o conserto de virar exagero: varrer `evals/<campanha>/`
    forçaria reescrita de registro de rodada passada, que é falsificar
    evidência.
    """
    import tempfile

    erros = []
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        evals = raiz / "pacote-de-mentira" / "evals"
        (evals / "campanha-congelada").mkdir(parents=True)
        (raiz / "pacote-de-mentira" / "SKILL.md").write_text(
            "# pacote de mentira\n", encoding="utf-8")
        alvos = {
            "PLACAR.md": evals / "PLACAR.md",
            "PLACAR-ADENDO-2026-01-01-teste.md":
                evals / "PLACAR-ADENDO-2026-01-01-teste.md",
            "congelado": evals / "campanha-congelada" / "PLACAR-ADENDO-2026-01-01-teste.md",
        }
        for alvo in alvos.values():
            alvo.write_text(_FRASE_DE_AUTOTESTE, encoding="utf-8")

        achados = " ".join(_varrer_declaradores(raiz.resolve()))
        for rotulo, deve in (("PLACAR.md", True),
                             ("PLACAR-ADENDO-2026-01-01-teste.md", True)):
            if (rotulo in achados) is not deve:
                erros.append(
                    f"autoteste de sítio: a varredura NÃO alcança {rotulo} — "
                    f"a mesma alegação passa em branco ali, que foi exatamente "
                    f"o buraco da tarefa 51"
                )
        if "campanha-congelada" in achados:
            erros.append(
                "autoteste de sítio: a varredura entrou em evals/<campanha>/ — "
                "registro de rodada passada não se reescreve para ficar verde"
            )
    return erros


def _autoteste_da_cadeia() -> list[str]:
    """O detector se testa antes de julgar os outros.

    Sem isto, um detector que nunca acha nada devolve verde para sempre — foi
    assim que esta casa publicou "digest é verificável" num teste que não podia
    ficar vermelho.
    """
    erros = []
    deve_pegar = "A cadeia canônica hoje soma **1531/1531 PASS** (motor 61 + 15)."
    if not achar_cadeia_no_presente(deve_pegar, "autoteste"):
        erros.append("autoteste da cadeia: alegação no presente não foi detectada")

    # T39, parte (b) — a SEGUNDA METADE do detector não era exercitada por ninguém.
    #
    # A amostra logo abaixo ("Naquela medição… somava…") parece testar
    # `_MARCAS_DE_PASSADO`, e não testa: ela não tem marca de PRESENTE, então sai
    # no primeiro `continue` e nunca alcança o teste de passado. O mesmo vale para
    # "| vigente em 2026-08-06 |", que morre antes, na regex, por não conter a
    # palavra "cadeia". Duas amostras que pareciam cobrir e cobriam outra coisa.
    #
    # O caso que EXERCITA a segunda metade precisa das DUAS marcas na mesma linha,
    # e ele é real: prosa histórica que usa uma palavra de presente. Sem esta
    # amostra, apagar `_MARCAS_DE_PASSADO` inteiro deixaria a bateria verde — foi
    # o que a tarefa 39 nomeou como "código morto", e o conserto honesto não é
    # remover a metade (ela resgata um caso legítimo), é passar a prová-la.
    deve_escapar_pelo_passado = "Em 2026-08-06 a cadeia hoje vigente era de **1531/1531 PASS**."
    if achar_cadeia_no_presente(deve_escapar_pelo_passado, "autoteste"):
        erros.append(
            "autoteste da cadeia: a linha com marca de presente E de passado foi "
            "acusada — a segunda metade do detector (_MARCAS_DE_PASSADO) não está "
            "resgatando o registro histórico legítimo"
        )

    nao_deve_pegar = [
        "Naquela medição, a cadeia canônica somava **1531/1531 PASS**.",
        "O número próprio deste pacote foi remedido e vale **57/57 PASS**.",
        "| vigente em 2026-08-06 | **105/106** |",
        # A sonda que não provava nada: sem a forma NNN/NNN o detector não pega
        # em sítio nenhum, então usá-la para "medir" ausência de trava dá um
        # falso negativo garantido. Fica como caso para ninguém repetir.
        "a cadeia hoje soma 1991 casos.",
    ]
    for amostra in nao_deve_pegar:
        if achar_cadeia_no_presente(amostra, "autoteste"):
            erros.append(
                f"autoteste da cadeia: falso positivo em {amostra[:52]!r}"
            )
    return erros + _autoteste_de_sitio()


def validate_placar_nao_declara_cadeia(structure_root: Path) -> list[str]:
    """Nenhum `PLACAR.md` de pacote afirma o total da cadeia como estado de hoje.

    **Por que por forma e não por sítio.** Em 2026-08-06 mediu-se: onze dos
    quinze placares diziam *"a cadeia canônica **hoje** soma 1531/1531 PASS"*
    enquanto a rodada daquele dia tinha FAIL em quatro pacotes. Dois placares
    **já haviam sido corrigidos** para o passado — e a correção **não
    propagou** para os outros onze. Conserto em prosa, num arquivo, sem trava
    que force os demais: é o `aviso-em-prosa-nao-previne-erro` pela quinta vez.

    Varre os declaradores **vigentes** de contagem dos pacotes gerentes. Não
    varre os congelados em `evals/<campanha>/`: aqueles são registro de rodada
    passada, e reescrever registro para ficar verde é falsificar evidência.

    **Por que dois sítios e não um (tarefa 51, 2026-08-07).** A versão de origem
    lia `evals/PLACAR.md` e mais nada — nunca os `evals/PLACAR-ADENDO-*.md`, que
    são **onde as contagens moram desde a tarefa 25**, criados pela própria casa
    justamente para carregar o número quando o placar envelhece. Havia 26 deles
    quando o buraco foi medido. É o `conserto-de-instancia-nao-e-conserto-de-mecanismo`
    um degrau adiante: a T34 consertou os onze placares que reclamavam e a trava
    nasceu cega para a família de arquivos vizinha.

    A medição foi de dois lados, com a **mesma** frase — *"A cadeia canônica hoje
    soma 1991/1991 PASS"* — plantada em cada sítio: acusava no `PLACAR.md` e
    passava em branco no adendo. Logo o buraco era de **sítio**, não de forma.
    (A primeira sonda usou *"a cadeia hoje soma 1991 casos"*, sem a forma
    `NNN/NNN`, que o detector não pega em lugar nenhum — não provava nada. Sonda
    que não avermelha o caso conhecido não mede ausência de trava.)
    """
    if not structure_root.is_dir():
        return [f"total de cadeia: raiz da estrutura ausente em {structure_root}"]

    return _autoteste_da_cadeia() + _varrer_declaradores(structure_root.resolve())


# ---------------------------------------------------------------------------
# TRAVA — a contagem publicada está LIGADA ao instrumento que a produziu
# ---------------------------------------------------------------------------
#
# Achado `EA-01` da remedição de 2026-08-03, BLOQUEANTE nos sete pacotes
# reprovados: o `evals/PLACAR.md` publica a contagem do validador como número
# corrente sem ligar a contagem à versão do instrumento que a produziu. A
# condição corretiva escrita pela Auditoria é literal — *"fechada quando um
# terceiro reabrir o PLACAR e conseguir ligar a contagem ao digest do
# instrumento vigente"*.
#
# Medido em 2026-08-08, por execução, antes de escrever esta trava: dos 16
# pacotes, 15 publicam número próprio e **os 15 estão defasados**. Nenhum bate.
# `ceo-maestro` publicava 55/55 contra 148/148 vivos; `departamento-juizes`
# 88/88 contra 169/169; `inovacao-melhoria` 59/59 contra 136/136; a própria
# Auditoria 65/65 contra 175/175. O defeito nunca foi dos sete: é de forma, e a
# forma está em toda a casa. Consertar os seis que reclamavam repetiria o
# `conserto-de-instancia-nao-e-conserto-de-mecanismo` pela quarta vez.
#
# O digest é o NORMALIZADO (BOM fora, CRLF→LF), pelo mesmo motivo que a fonte
# normativa usa: digest de bytes crus muda com o fim de linha do checkout, e
# vermelho que mente custa tanto quanto verde que mente.
# O `sha256:` do prefixo NÃO é decoração: é o que `sha256_texto_normalizado`
# devolve, e a primeira versão desta expressão exigia 64 hexadecimais puros. Ela
# não casava com nenhum dos 16 selos gerados, e o efeito foi o pior possível — o
# autoteste acusou o selo CORRETO, e a trava reprovou os 16 pacotes por ausência
# de algo que estava lá. Gate que barra evidência boa se disfarça de rigor.
SELO_DE_CONTAGEM = re.compile(
    r"(?m)^CONTAGEM-VIGENTE:\s*(\d+)/(\d+)\s*\|\s*instrumento:\s*"
    r"`?evals/validate_workflow\.py`?\s*\|\s*sha256-normalizado:\s*"
    r"`?(sha256:[a-f0-9]{64})`?\s*\|\s*medido-em:\s*(\d{4}-\d{2}-\d{2})\s*$"
)

_MODELO_DO_SELO = (
    "CONTAGEM-VIGENTE: {ok}/{total} | instrumento: `evals/validate_workflow.py` |"
    " sha256-normalizado: `{sha}` | medido-em: {data}"
)


def _selos_do_pacote(pacote: Path) -> list[tuple[str, Path]]:
    """Os selos encontrados nos declaradores VIGENTES do pacote."""
    return [
        (m.group(3), declarador)
        for declarador in _declaradores_de_contagem(pacote / "evals")
        for m in [SELO_DE_CONTAGEM.search(declarador.read_text(encoding="utf-8"))]
        if m
    ]


def _numeros_do_pacote(pacote: Path) -> list[tuple[int, int, Path]]:
    """`(aprovados, total, declarador)` de cada selo — os grupos que se descartavam.

    A expressão `SELO_DE_CONTAGEM` já capturava `N/M` nos grupos 1 e 2, e
    `_selos_do_pacote` ficava só com o grupo 3, o digest. Metade da informação era
    extraída e jogada fora — e é justamente a metade que a tarefa 27 pede.
    """
    numeros: list[tuple[int, int, Path]] = []
    for declarador in _declaradores_de_contagem(pacote / "evals"):
        m = SELO_DE_CONTAGEM.search(declarador.read_text(encoding="utf-8"))
        if m:
            numeros.append((int(m.group(1)), int(m.group(2)), declarador))
    return numeros


def selo_bate_com_execucao(
    selo: tuple[int, int], execucao: tuple[int, int]
) -> bool:
    """`(aprovados, total)` do selo e da execucao coincidem? Regra em UM lugar so.

    Extraida antes de escrever o autoteste, e nao depois, porque escrever o
    autoteste em cima de uma COPIA do `!=` e o erro que esta casa ja catalogou
    como teste-que-exercita-a-reimplementacao -- e que eu repeti tres vezes num
    dia so. Mutar a funcao de producao tem de avermelhar o autoteste; se o
    autoteste tiver a sua propria copia da regra, nao avermelha.
    """
    return selo == execucao


def conferir_contagem_declarada(
    pacote: Path, aprovados: int, total: int
) -> list[str]:
    """O número PUBLICADO é o que o validador ACABOU de produzir (tarefa 27).

    **O buraco que isto fecha, medido em 2026-08-22.** O selo já amarrava a
    contagem ao DIGEST do instrumento, o que prova PROCEDÊNCIA: aquele número saiu
    daquela versão do validador. Não provava CORREÇÃO. Testado por mutação: trocar
    `17/17` por `999/999` no `PLACAR.md`, mantendo o digest intacto, **passava em
    silêncio** — o validador rodava, produzia 17/17, e ninguém comparava.

    Um selo assim responde "quem produziu este número?" e não responde "este
    número é o número?". As duas perguntas são necessárias, e só a primeira tinha
    trava.

    **APROVADOS e TOTAL, não `len(cases)`** — e a distinção é o coração da tarefa
    27. Comparar só o total diz que a suíte tem N casos; comparar os aprovados diz
    que N casos PASSARAM. Se um caso começar a reprovar de verdade, o total não se
    move e a divergência some; os aprovados caem e a linha deixa de bater na hora.
    É a diferença entre contar cadeiras e contar quem sentou.

    Cada pacote confere o PRÓPRIO número, e o motivo é que não há outro jeito sem
    recursão: quem sabe quantos casos passaram é o validador que acabou de rodar.
    Um conferente externo teria de executá-lo, e executá-lo dispararia a mesma
    conferência de novo.
    """
    # FRONTEIRA COM A TRAVA VIZINHA, e ela custou um falso positivo antes de ficar
    # clara. A primeira versão acusava `CONTAGEM_NAO_DECLARADA` quando não havia
    # selo — e isso (a) duplica `CONTAGEM_SEM_INSTRUMENTO`, que
    # `validate_contagem_ligada_ao_instrumento` já emite, e (b) fechava o portão do
    # coletor sobre o pacote-de-mentira do próprio teste, que não tem selo por não
    # ser pacote de verdade.
    #
    # A divisão certa: aquela trava responde "existe selo, e ele aponta para este
    # instrumento?"; esta responde "o número declarado é o número produzido?".
    # Sem selo não há alegação a contradizer, e policiar presença aqui seria contar
    # o mesmo defeito duas vezes.
    numeros = _numeros_do_pacote(pacote)
    # TAREFA 98 — o autoteste desta comparação estava ÓRFÃO desde que nasceu,
    # em 2026-08-22 de manhã, e foi a varredura de alcance da própria tarefa 98
    # que o encontrou: definido, correto, e chamado por NINGUÉM na árvore
    # inteira. O registro da tarefa 27 dizia que um mutante morrera "pelo
    # autoteste"; o que o matava era outra coisa, e a frase ficou corrigida no
    # ledger. Agora ele roda junto com a conferência que ele existe para provar.
    erros: list[str] = list(_autoteste_da_contagem())
    for ok, tot, declarador in numeros:
        if not selo_bate_com_execucao((ok, tot), (aprovados, total)):
            erros.append(
                f"CONTAGEM_DIVERGENTE: {pacote.name} publica {ok}/{tot} em"
                f" {declarador.name}, e esta execução produziu {aprovados}/{total}."
                " O selo prova de qual instrumento o número veio; isto prova que o"
                " número é o número. Regenere com"
                " `_compartilhado/selar_contagem.py`"
            )
    return erros


_AMOSTRAS_DA_CONTAGEM = (
    # (rótulo, selo publicado, execução, deve_reprovar)
    ("selo bate com a execução", (17, 17), (17, 17), False),
    ("selo com TOTAL inflado", (999, 999), (17, 17), True),
    ("selo com APROVADOS a mais, total igual", (17, 17), (16, 17), True),
    ("selo com APROVADOS a menos, total igual", (16, 17), (17, 17), True),
    ("selo de outra suíte, mesmo aprovados", (17, 18), (17, 17), True),
)


def _autoteste_da_contagem() -> list[str]:
    """A comparação prova que enxerga a divergência — inclusive a de APROVADOS.

    A terceira e a quarta amostras existem por causa do ponto da tarefa 27: com
    total igual e aprovados diferentes, uma comparação que só olhasse o total
    ficaria verde. São elas que separam contar cadeiras de contar quem sentou.
    """
    erros: list[str] = []
    for rotulo, (sok, stot), (eok, etot), deve_reprovar in _AMOSTRAS_DA_CONTAGEM:
        reprovou = not selo_bate_com_execucao((sok, stot), (eok, etot))
        if reprovou != deve_reprovar:
            erros.append(
                "AUTOTESTE_DA_CONTAGEM: a amostra %r %s e devia %s — a comparação"
                " de contagem declarada deixou de distinguir o caso conhecido"
                % (rotulo, "reprovou" if reprovou else "passou",
                   "reprovar" if deve_reprovar else "passar")
            )
    return erros


def _conferir_selo(pacote: Path, instrumento: Path, motor) -> list[str]:
    """A conferência de UM pacote, separada para o autoteste poder chamá-la."""
    selos = _selos_do_pacote(pacote)
    if not selos:
        return [
            f"CONTAGEM_SEM_INSTRUMENTO: {pacote.name} publica contagem sem ligá-la"
            " ao instrumento que a produziu. Nenhum declarador vigente traz a"
            " linha `CONTAGEM-VIGENTE: N/M | instrumento: … | sha256-normalizado:"
            " … | medido-em: …`, então quem reabre o placar não tem como saber se"
            " o número descreve o validador de hoje (achado EA-01)"
        ]

    vigente = motor.sha256_texto_normalizado(instrumento)
    erros: list[str] = []
    divergentes = {sha for sha, _ in selos if sha != vigente}
    for sha in sorted(divergentes):
        onde = [d.name for s, d in selos if s == sha]
        erros.append(
            f"CONTAGEM_ENVELHECIDA: {pacote.name} declara contagem contra o"
            f" instrumento {sha[:12]}… em {onde}, e o instrumento vigente é"
            f" {vigente[:12]}…. A contagem publicada descreve outra versão do"
            " validador — é prova envelhecida, e é exatamente o que o selo"
            " existe para tornar visível. Regenere com"
            " `_compartilhado/selar_contagem.py`"
        )
    return erros


def validate_contagem_ligada_ao_instrumento(structure_root: Path) -> list[str]:
    """Toda contagem publicada aponta para o digest do instrumento que a produziu.

    **Por que trava e não conserto.** A condição corretiva do `EA-01` pode ser
    satisfeita à mão, num arquivo, e envelhecer no dia seguinte — o número volta
    a descrever um validador que já mudou, sem que nada fique vermelho. Foi assim
    que os 15 chegaram defasados: cada um esteve certo no dia em que foi escrito.
    Aqui o selo **amarra** o número ao digest, e editar o validador sem
    regenerar o selo derruba a bateria do próprio pacote.

    O autoteste vem antes do julgamento: a trava recusa passar se não acusar o
    pacote sem selo, se não acusar o selo com digest de outra versão, e se acusar
    o selo correto. Detector que não avermelha o caso conhecido não mede ausência
    de nada.
    """
    if not structure_root.is_dir():
        return [f"contagem ligada ao instrumento: raiz ausente em {structure_root}"]

    motor, erros = _motor_compartilhado()
    if motor is None:
        return erros
    if not callable(getattr(motor, "sha256_texto_normalizado", None)):
        return erros + [
            "OVERLAY_APLICADO_PELA_METADE: o motor compartilhado não expõe"
            " sha256_texto_normalizado(), e sem ele o selo não tem contra o que"
            " ser conferido"
        ]

    erros.extend(_autoteste_do_selo(motor))
    root = structure_root.resolve()
    for instrumento in _validadores_canonicos(root):
        erros.extend(_conferir_selo(instrumento.parents[1], instrumento, motor))
    return erros


def _autoteste_do_selo(motor) -> list[str]:
    """Planta os três casos conhecidos e exige o veredito certo em cada um."""
    import tempfile  # noqa: PLC0415 — só o autoteste precisa

    erros: list[str] = []
    with tempfile.TemporaryDirectory(prefix="selo-autoteste-") as tmp:
        pacote = Path(tmp) / "pacote-de-mentira"
        evals = pacote / "evals"
        evals.mkdir(parents=True)
        (pacote / "SKILL.md").write_text("# de mentira\n", encoding="utf-8")
        instrumento = evals / "validate_workflow.py"
        instrumento.write_text("# instrumento de mentira\n", encoding="utf-8")
        placar = evals / "PLACAR.md"

        placar.write_text("# Placar\n\n| Validador | 42/42 PASS |\n", encoding="utf-8")
        if not _conferir_selo(pacote, instrumento, motor):
            erros.append(
                "AUTOTESTE FALHOU: contagem publicada SEM selo passou — a trava"
                " não mede a ausência que existe para medir"
            )

        sha = motor.sha256_texto_normalizado(instrumento)
        selo = _MODELO_DO_SELO.format(ok=42, total=42, sha=sha, data="2026-08-08")
        placar.write_text(f"# Placar\n\n{selo}\n", encoding="utf-8")
        if _conferir_selo(pacote, instrumento, motor):
            erros.append(
                "AUTOTESTE FALHOU: selo CORRETO foi acusado — trava que barra"
                " evidência boa é tão inútil quanto a que deixa passar a ruim"
            )

        instrumento.write_text("# instrumento MUDOU\n", encoding="utf-8")
        if not _conferir_selo(pacote, instrumento, motor):
            erros.append(
                "AUTOTESTE FALHOU: selo de OUTRA versão do instrumento passou — é"
                " a prova envelhecida, e é o achado EA-01 inteiro"
            )
    return erros


# ---------------------------------------------------------------------------
# TAREFA 71 — pendência declarada sem dono é pendência de ninguém
# ---------------------------------------------------------------------------
#
# Achados `CA-01` e `GR-01`/`GR-02` da remedição de 2026-08-03, abertos em todos
# os sete pacotes reprovados: os itens de "O que ainda não foi provado" descrevem
# a pendência e não dizem **quem responde por fechá-la**.
#
# Medido em 2026-08-08, antes de escrever: **52 itens abertos na casa, UM com
# dono**. Como nas outras duas formas desta campanha, o defeito nunca foi dos
# sete — era de forma, e estava em toda a Estrutura.
#
# CUIDADO DE INSTRUMENTO, e ele me pegou duas vezes aqui. (1) A primeira
# varredura era sensível a caixa e não achou a seção do `especialista-planejador`,
# escrita `O que ainda NÃO foi provado`; declarar "não tem seção" teria isentado
# um pacote que tinha quatro pendências. (2) A segunda contava só itens
# numerados, e aquele pacote usa traço — a contagem saiu 4 pacotes onde eram 5.
# Detector que não vê o formato do vizinho produz isenção, não conformidade.
_SECAO_DE_PENDENCIA = re.compile(r"(?i)^##+\s+.*n[ãa]o\s+foi\s+provado")
_ITEM_DE_PENDENCIA = re.compile(r"^(?:\d+\.|[-*])\s+\S")
_LINHA_DA_TABELA = re.compile(r"^\|\s*(\d+)\s*\|([^|]*)\|")


def achar_pendencia_sem_dono(texto: str, origem: str) -> list[str]:
    """Itens da seção de pendências que não têm linha na tabela de donos.

    Pública, no molde de `achar_cadeia_no_presente`: é o que permite ao validador
    de um pacote escrever o **caso negativo** desta trava, plantando a forma
    proibida e exigindo que ela seja acusada.

    Seção ausente não é violação — três pacotes de topo não a têm, e inventar a
    exigência para eles seria cobrar formulário, não conteúdo.
    """
    linhas = texto.split("\n")
    inicio = next((i for i, l in enumerate(linhas) if _SECAO_DE_PENDENCIA.match(l)), None)
    if inicio is None:
        return []
    fim = next((i for i in range(inicio + 1, len(linhas))
                if linhas[i].startswith("## ")), len(linhas))
    corpo = linhas[inicio:fim]

    itens = [l for l in corpo if _ITEM_DE_PENDENCIA.match(l)]
    if not itens:
        return []
    donos: dict[int, str] = {}
    for linha in corpo:
        casado = _LINHA_DA_TABELA.match(linha)
        if casado:
            donos[int(casado.group(1))] = casado.group(2).strip()

    erros = []
    for indice in range(1, len(itens) + 1):
        if indice not in donos:
            erros.append(
                f"PENDENCIA_SEM_DONO: {origem} — o item {indice} de"
                " \"O que ainda não foi provado\" não tem linha na tabela de donos."
                " Pendência declarada sem dono é pendência de ninguém: quem lê"
                " sabe o que falta e não sabe a quem cobrar (CA-01, GR-01/GR-02)"
            )
        elif not donos[indice]:
            erros.append(
                f"PENDENCIA_SEM_DONO: {origem} — o item {indice} tem linha na"
                " tabela e a célula do dono está VAZIA. Linha em branco satisfaz"
                " a forma e não nomeia ninguém"
            )
    return erros


def _autoteste_do_dono() -> list[str]:
    """Planta os três casos conhecidos e exige o veredito certo em cada um."""
    cabeca = "# Placar\n\n## O que ainda não foi provado\n\n"
    tabela = "| item | dono | fecha quando |\n|---:|---|---|\n| 1 | `x` | quando |\n"
    completo = cabeca + tabela + "\n1. **Um.** texto\n"
    faltando = cabeca + "\n1. **Um.** texto\n2. **Dois.** texto\n" + tabela
    vazio = cabeca + "| item | dono | fecha quando |\n|---:|---|---|\n| 1 |  | quando |\n\n1. **Um.** t\n"
    erros = []
    if achar_pendencia_sem_dono(completo, "fixture"):
        erros.append(
            "AUTOTESTE FALHOU: seção COMPLETA foi acusada — trava que barra"
            " evidência boa se disfarça de rigor"
        )
    if not achar_pendencia_sem_dono(faltando, "fixture"):
        erros.append(
            "AUTOTESTE FALHOU: item sem linha na tabela passou — é o achado"
            " CA-01 inteiro"
        )
    if not achar_pendencia_sem_dono(vazio, "fixture"):
        erros.append(
            "AUTOTESTE FALHOU: célula de dono VAZIA passou — a forma satisfeita"
            " sem ninguém nomeado é a erosão seguinte"
        )
    if achar_pendencia_sem_dono("# Placar\n\n## Resultado\n\ntexto\n", "fixture"):
        erros.append(
            "AUTOTESTE FALHOU: placar SEM a seção foi acusado — seção ausente"
            " não é violação, e cobrar formulário não é cobrar conteúdo"
        )
    return erros


def validate_pendencia_tem_dono(structure_root: Path) -> list[str]:
    """Todo item de "O que ainda não foi provado" nomeia quem responde por ele.

    A condição corretiva escrita pela Auditoria é literal — *"conferível lendo a
    seção e achando um dono por item"*. Aqui ela vira execução: a seção precisa
    carregar uma tabela cuja primeira coluna cubra todos os itens, e a célula do
    dono não pode estar vazia.

    O que esta trava **não** faz: julgar se o dono é o certo. Isso é mérito, e
    mérito não é dela. Ela impede o estado anterior — 52 pendências abertas e uma
    com dono —, não garante boa atribuição.
    """
    if not structure_root.is_dir():
        return [f"pendência sem dono: raiz da estrutura ausente em {structure_root}"]

    erros = _autoteste_do_dono()
    root = structure_root.resolve()
    for instrumento in _validadores_canonicos(root):
        placar = instrumento.parents[1] / "evals" / "PLACAR.md"
        if not placar.is_file():
            continue
        relativo = placar.resolve().relative_to(root).as_posix()
        erros.extend(
            achar_pendencia_sem_dono(placar.read_text(encoding="utf-8"), relativo)
        )
    return erros


# ---------------------------------------------------------------------------
# TAREFA 84 — as travas DESTE módulo também têm de decidir alguma coisa
# ---------------------------------------------------------------------------
#
# O buraco, medido em 2026-08-08 por três mutantes que escaparam:
# `validate_nenhuma_trava_esta_inerte` varre APENAS o
# `evals/validate_workflow.py` do próprio pacote. Este módulo — que hospeda as
# funções de `FUNCOES_OBRIGATORIAS`, chamadas pelos dezesseis validadores — não
# era varrido por nada. Fazer uma delas devolver `[]` sempre mantinha a bateria
# em 176/176; descartar o retorno do autoteste dela, idem; e tirar o nome de
# `FUNCOES_OBRIGATORIAS` também.
#
# E não era defeito da trava nova: mutar `validate_placar_nao_declara_cadeia`,
# que é da tarefa 34, escapou igual. Valia para as cinco.
#
# É o `gate-que-nao-se-autoexige-erode` com raio dezesseis: a casa fechou este
# defeito um nível abaixo na rodada 7 (OI6-04) e deixou aberto o nível onde moram
# as travas que valem para todos.


def _corpo_neutralizado(funcao: ast.FunctionDef) -> str | None:
    """Motivo pelo qual este corpo não decide mais nada — ou `None`.

    Duas formas, e as duas foram vistas em mutante real:

    1. **código morto** depois de um `return`/`raise` no mesmo bloco. É a forma
       barata de desligar sem apagar: a função continua inteira, o `git diff`
       mostra uma linha, e tudo abaixo vira enfeite;
    2. **todo `return` devolve lista vazia literal** — a função virou constante.
    """
    for no in ast.walk(funcao):
        corpo = getattr(no, "body", None)
        if not isinstance(corpo, list):
            continue
        for indice, comando in enumerate(corpo[:-1]):
            if isinstance(comando, (ast.Return, ast.Raise)):
                seguinte = corpo[indice + 1]
                return (
                    f"há código MORTO depois do {type(comando).__name__.lower()}"
                    f" da linha {comando.lineno} (a partir da linha"
                    f" {seguinte.lineno}): desligar uma trava com um return"
                    " precoce deixa o corpo inteiro de enfeite"
                )
    retornos = [no for no in ast.walk(funcao) if isinstance(no, ast.Return)]
    if retornos and all(
        isinstance(no.value, ast.List) and not no.value.elts for no in retornos
    ):
        return (
            "todo `return` devolve lista vazia literal: a função virou constante"
            " e não pode mais acusar nada"
        )
    # Terceira forma, e ela também saiu de um mutante que escapou: o CAMINHO
    # PRINCIPAL vira `return []` e as guardas de erro ficam de pé. A regra 2 não
    # pega, porque ainda existe um `return` com conteúdo — o da guarda —, e a
    # função parece viva. Foi assim que `validate_placar_nao_declara_cadeia`
    # sobreviveu ao primeiro conserto desta trava.
    #
    # A regra é segura: medida sobre este módulo antes de ser adotada, NENHUMA
    # das nove funções varridas termina em lista vazia literal. Quem acumula erro
    # devolve o acumulador; quem não acumula devolve comprehension. Terminar em
    # `[]` literal é a assinatura de quem foi desligado.
    ultimo = funcao.body[-1]
    if (
        isinstance(ultimo, ast.Return)
        and isinstance(ultimo.value, ast.List)
        and not ultimo.value.elts
    ):
        return (
            f"o caminho principal termina em `return []` literal (linha"
            f" {ultimo.lineno}): as guardas de erro continuam de pé e a função"
            " parece viva, mas o veredito dela é constante"
        )
    return None


def achar_corpo_neutralizado(fonte: str, origem: str) -> list[str]:
    """Aplica `_corpo_neutralizado` a todas as funções de um fonte em texto.

    Pública, e no mesmo molde de `achar_cadeia_no_presente`: é o que permite a um
    validador de pacote escrever o **caso negativo** da trava — plantar a forma
    proibida e exigir que ela seja acusada. Trava provada só pelo lado verde é
    trava provada pela metade.
    """
    try:
        arvore = ast.parse(fonte)
    except SyntaxError as exc:
        return [f"{origem}: não parseia ({exc})"]
    return [
        f"{origem}:{no.name} — {motivo}"
        for no in ast.walk(arvore)
        if isinstance(no, ast.FunctionDef)
        for motivo in [_corpo_neutralizado(no)]
        if motivo
    ]


def _autotestes_descartados(funcao: ast.FunctionDef) -> list[str]:
    """Chamadas a `_autoteste*` cujo retorno é jogado fora dentro desta função."""
    descartados = []
    for no in ast.walk(funcao):
        if not (isinstance(no, ast.Expr) and isinstance(no.value, ast.Call)):
            continue
        alvo = no.value.func
        nome = alvo.id if isinstance(alvo, ast.Name) else getattr(alvo, "attr", "")
        if nome.startswith("_autoteste"):
            descartados.append(f"{nome} (linha {no.lineno})")
    return descartados


def validate_travas_compartilhadas_com_efeito(structure_root: Path) -> list[str]:
    """As funções obrigatórias DESTE módulo não estão neutralizadas.

    Confere quatro coisas, e cada uma nasceu de um mutante que escapou:

    1. cada nome de `FUNCOES_OBRIGATORIAS` **existe** como função aqui;
    2. o corpo de cada uma **decide** — sem código morto, sem virar constante;
    3. o retorno de todo `_autoteste*` chamado dentro delas é **consumido**;
    4. `FUNCOES_OBRIGATORIAS` cobre o `PISO_DE_FUNCOES_OBRIGATORIAS`, para que
       encolher a exigência custe duas edições em vez de uma.

    Ela **se inclui** na varredura: uma trava que não se autoexige erode, e a
    lição já está registrada nesta casa.

    O TETO, declarado porque não dá para fechá-lo aqui
    --------------------------------------------------
    Alguém que neutralize **esta** função continua passando: quem confere é ela
    mesma, e o laço não fecha de dentro. O mesmo vale para apontar o `sys.path`
    para outra cópia do módulo — o item 5 abaixo reduz esse caso comparando o
    arquivo importado com o que está na árvore auditada, mas quem controla os
    dois controla a comparação. Fechar isto exige executor **externo** ao pacote,
    que é a tarefa 50 (CI externo) e a 57 (manifesto verificável). Este limite é
    da mesma natureza do `R11` do envelope da Auditoria: está medido, nomeado, e
    não é fechado por mais uma trava do lado de dentro.
    """
    erros: list[str] = []

    faltando = sorted(set(PISO_DE_FUNCOES_OBRIGATORIAS) - set(FUNCOES_OBRIGATORIAS))
    if faltando:
        erros.append(
            f"PISO_DE_OBRIGATORIAS_ROMPIDO: {faltando} está no piso e sumiu de"
            " FUNCOES_OBRIGATORIAS. Encolher a exigência é decisão, não descuido:"
            " se for para valer, o piso muda junto, no mesmo ato e com o motivo"
            " escrito"
        )

    modulo = Path(__file__).resolve()
    try:
        arvore = ast.parse(modulo.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        return erros + [f"TRAVAS_COMPARTILHADAS_ILEGIVEIS: {exc}"]

    definidas = {
        no.name: no
        for no in ast.walk(arvore)
        if isinstance(no, ast.FunctionDef)
    }
    # A varredura cobre AS DUAS listas, e isso saiu de um mutante que escapou na
    # primeira versão: `validate_placar_nao_declara_cadeia` — a trava da tarefa
    # 34, chamada pelos dezesseis — vive em `FUNCOES_DE_ESTRUTURA`, não em
    # `FUNCOES_OBRIGATORIAS`. Varrer só as obrigatórias deixava justamente a
    # trava que abriu esta investigação de fora. Cobertura pela pegada do
    # conserto é o defeito que a `validate_fonte_normativa_conferida` já
    # registrou nesta casa.
    for nome in sorted(set(FUNCOES_OBRIGATORIAS) | set(FUNCOES_DE_ESTRUTURA)):
        funcao = definidas.get(nome)
        if funcao is None:
            erros.append(
                f"TRAVA_DE_ESTRUTURA_AUSENTE: {nome} é declarada nas listas deste"
                f" módulo e não existe em {modulo.name}"
            )
            continue
        motivo = _corpo_neutralizado(funcao)
        if motivo:
            erros.append(
                f"TRAVA_COMPARTILHADA_INERTE: {nome} não decide mais nada —"
                f" {motivo}. Ela é chamada pelos dezesseis, e até 2026-08-08"
                " desligá-la mantinha todos verdes"
            )
        for descartado in _autotestes_descartados(funcao):
            erros.append(
                f"AUTOTESTE_DESLIGADO: {nome} chama {descartado} e DESCARTA o"
                " retorno. Autoteste cujo resultado não alcança o agregado é"
                " autoteste desligado — a trava para de se provar e continua"
                " parecendo íntegra"
            )

    # 5. o módulo importado é o que está na árvore auditada.
    if structure_root.is_dir():
        na_arvore = structure_root.resolve() / "_compartilhado" / modulo.name
        if na_arvore.is_file() and na_arvore != modulo:
            motor, erros_do_motor = _motor_compartilhado()
            erros.extend(erros_do_motor)
            if motor is not None and callable(
                getattr(motor, "sha256_texto_normalizado", None)
            ):
                if motor.sha256_texto_normalizado(na_arvore) != (
                    motor.sha256_texto_normalizado(modulo)
                ):
                    erros.append(
                        "MODULO_IMPORTADO_DIVERGE_DA_ARVORE: o"
                        f" {modulo.name} que este processo carregou não é o que"
                        f" está em {na_arvore}. Cópia local não é a que carrega,"
                        " e a bateria estaria medindo outro arquivo"
                    )
    return erros


# ---------------------------------------------------------------------------
# TRAVA 3 — a fonte normativa confere, nos quinze
# ---------------------------------------------------------------------------


def validate_fonte_normativa_conferida(structure_root: Path) -> list[str]:
    """`REGRAS-DE-OURO.md` confere com o valor declarado em `ORIGEM.md`.

    **O limite que isto fecha.** Depois da rodada 1, dez pacotes recomputavam a
    fonte normativa e cinco — `ceo-maestro`, `conteudo-marketing`,
    `inovacao-melhoria`, `negocios` e `qa-usabilidade` — não tinham verificação
    nenhuma. A cobertura era a **pegada do conserto**: quem tinha sítio
    tautológico ganhou conferência, quem não tinha ficou sem. Mutar a fonte
    normativa passava despercebido em um terço da casa.

    Aqui a cobertura vira regra: a função está em `FUNCOES_OBRIGATORIAS`, todo
    validador canônico é obrigado a chamá-la por `validate_cobertura_de_validadores`,
    e quem não chamar reprova. Não há lista de pacotes cobertos porque não há
    onde esquecer de inscrever o pacote novo.

    A conferência usa o digest **normalizado** (BOM fora, CRLF→LF): identidade de
    conteúdo, não de bytes do checkout. Digest de arquivo cru muda com o fim de
    linha do clone, e vermelho que mente é tão inútil quanto verde que mente.
    """
    if not structure_root.is_dir():
        return [f"fonte normativa: raiz da estrutura ausente em {structure_root}"]

    motor, erros = _motor_compartilhado()
    if motor is None:
        return erros

    conferir = getattr(motor, "conferir_digest_das_regras", None)
    if not callable(conferir):
        return erros + [
            "OVERLAY_APLICADO_PELA_METADE: "
            f"{_ARQUIVO_DO_MOTOR} não expõe conferir_digest_das_regras(). Esta "
            "trava e o motor compartilhado são indivisíveis: aplicar os "
            "validadores sem o motor atualizado (ou o contrário) deixa a fonte "
            "normativa sem conferência nenhuma"
        ]

    root = structure_root.resolve()
    regras = root / "regras-de-ouro" / "REGRAS-DE-OURO.md"
    origem = root / "regras-de-ouro" / "ORIGEM.md"
    try:
        erros.extend(conferir(regras, origem))
    except Exception as exc:  # noqa: BLE001
        erros.append(
            f"CONFERENCIA_DA_FONTE_NORMATIVA_QUEBRADA: "
            f"{exc.__class__.__name__}: {exc}"
        )
    return erros
