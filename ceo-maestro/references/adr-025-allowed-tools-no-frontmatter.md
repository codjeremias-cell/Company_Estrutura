# ADR-025 — `allowed-tools` é campo válido e opcional do frontmatter

- **Data:** 2026-08-11
- **Status:** **ACEITO** — decisão de Jeremias em 2026-08-11, executada pelo
  `departamento-evolucao-skills` sob `EXECUTIVE_MISSION` do `ceo-maestro`.
- **Decisores:** **Jeremias** decidiu canonizar; o `ceo-maestro` despachou; a execução e a prova
  são do `departamento-evolucao-skills`. A conformidade da adoção é da Auditoria.
- **Dono pela posição:** `ceo-maestro` — a anatomia do frontmatter vale para os **84 `SKILL.md`
  vivos** da Estrutura (contados em 2026-08-11, fora de `evals/`) e não pertence a nenhum
  Departamento isolado.
- **Número conferido contra a árvore em 2026-08-11:** a série global ocupa **001–018 e 021–024**
  em `references/` vivos. **019 e 020 não são livres**: 019 está reservado pelos
  `adr-019-*.md.candidate` da frente `contrato-analysis-2026-07-31` (renumeração decidida pelo
  CEO em 2026-08-03) e 020 pelos `adr-020-producao-honesta.md.candidate` da frente
  `producao-honesta-2026-08-04`. **025 é o primeiro número sem nenhuma ocorrência na árvore** —
  zero menções em qualquer arquivo, incluindo candidatos e material de laboratório.
- **Prova:** [`../evals/canonizacao-allowed-tools-2026-08-11/PROVA-DE-MUTACAO.txt`](../evals/canonizacao-allowed-tools-2026-08-11/PROVA-DE-MUTACAO.txt)

## Contexto — a trava reprovava uma decisão já tomada

Em 2026-08-10 o commit `7a30b0d`, da frente GradUP e a convite do dono, declarou `allowed-tools`
no frontmatter de **13 `SKILL.md`** da Estrutura — a gerente de Desenvolvimento e doze agentes de
Desenvolvimento, Arquitetura de Software, Registros e Evolução de Skills. O commit **não tocou em
nenhum validador**, e a prova publicada — `ceo-maestro/evals/validate_workflow.py` → 148/148 — não
cobre o frontmatter daqueles arquivos: o CEO confere o próprio `SKILL.md` com um regex local, e
quem confere o dos Departamentos é o validador de cada pacote.

A trava que reprovava estava num único ponto do módulo compartilhado,
[`_compartilhado/verificacoes_pacote.py`](../../_compartilhado/verificacoes_pacote.py), na
`validate_frontmatter`:

```python
if keys != ["name", "description"]:
```

Comparação de **lista exata**: qualquer chave a mais reprova. Medido em 2026-08-11, antes da
mudança: **2076/2081**, com **5 FAIL em 4 pacotes** — `departamento-evolucao-skills`,
`departamento-desenvolvimento` (2), `departamento-arquitetura-software` e
`departamento-registros`. A cadeia de consequências era mecânica e cara: o `deploy-estrutura.ps1`
bloqueia no gate pré-deploy, o runtime fica defasado, e sete pacotes passam a reprovar por
`ARTEFATOS_TWINS`. Uma decisão de fronteira já tomada ficava travada por um validador que ninguém
atualizou junto.

## Decisão

**`allowed-tools` passa a ser campo válido e opcional do frontmatter de `SKILL.md`.** A ordem
canônica é `name`, `description` e, **se presente**, `allowed-tools` depois. Os 13 arquivos
**não** são revertidos: quem estava desatualizado era o validador, não eles.

A conferência deixa de ser lista fixa e passa a ser **allowlist ordenada**, em
`verificacoes_pacote.py`:

```python
CHAVES_FRONTMATTER_OBRIGATORIAS = ("name", "description")
CHAVES_FRONTMATTER_OPCIONAIS = ("allowed-tools",)

esperadas = list(CHAVES_FRONTMATTER_OBRIGATORIAS) + [
    opcional for opcional in CHAVES_FRONTMATTER_OPCIONAIS if opcional in keys
]
if keys != esperadas:
    ...
```

Monta-se a sequência esperada com as obrigatórias e acrescenta-se cada opcional que o arquivo **de
fato declarou**. Continuar comparando a lista inteira preserva de graça as três garantias da
versão anterior — chave desconhecida reprova, chave repetida reprova, ordem fora do canônico
reprova — e abre a porta **apenas** para os nomes de `CHAVES_FRONTMATTER_OPCIONAIS`.

### Por que canonizar, e não reverter

Restringir a ferramenta de um agente **é mecanismo de fronteira**, não metadado decorativo. A casa
já escreve fronteira exclusiva em prosa no `CONTRATO-DE-COMPROMISSO.md` de cada pacote — "não
aciona ninguém", "não executa a especialidade" — e a lição registrada nesta casa é que **aviso em
prosa não previne erro**: a proibição documentada repetiu-se até ser travada em código.
`allowed-tools` é exatamente essa promoção: a proibição que hoje mora
no contrato passa a ser **executada pelo runtime**, que simplesmente não entrega a ferramenta.

Isso está alinhado à **T68**, aberta a partir do garimpo da T67: o `VoltAgent/awesome-claude-code-subagents`
publica 154 subagentes com **restrição de ferramenta por agente** e roteamento de modelo, e foi
triado como material que "serve muito" justamente para fechar esta fronteira. Reverter os 13
arquivos seria mover a régua para caber o validador — o oposto do que esta casa faz.

## Consequências

- **Medido em 2026-08-11, depois da mudança: `2081/2081`, 0 FAIL nos 16 validadores canônicos.**
  Os 5 FAIL fecharam e **nenhum denominador mudou** — a contagem por pacote é idêntica à de antes
  em todos os 16, então nenhum `PLACAR.md` precisa de adendo de contagem por esta decisão.
- **O que continua proibido, e este é o ponto central da decisão:** **campo desconhecido no
  frontmatter continua reprovando.** A mudança é uma allowlist, não um afrouxamento. Um
  `foo: bar` — ou qualquer chave fora de `name`, `description` e `allowed-tools` — segue sendo
  erro, com ou sem `allowed-tools` presente. A **ordem** também segue conferida: `allowed-tools`
  antes de `description` reprova.
- **Provado por mutação nas duas direções**, e não só pelo verde. Registro cru em
  [`PROVA-DE-MUTACAO.txt`](../evals/canonizacao-allowed-tools-2026-08-11/PROVA-DE-MUTACAO.txt):
  (a) plantado `foo: bar` em `SKILL.md` **com** e **sem** `allowed-tools`, e `allowed-tools` fora
  de ordem — os três reprovam, e os três arquivos foram restaurados byte a byte com SHA-256
  conferido antes e depois; (b) revertida a comparação para a lista exata, os 4 pacotes voltam a
  **5 FAIL**, e restaurada volta a **0** — o verde é causado por esta mudança, não por outra coisa.
- **Alcance:** a decisão vale para o frontmatter de `SKILL.md` de **qualquer** pacote da Estrutura
  conferido por `validate_frontmatter`. Ela **não** obriga ninguém a declarar `allowed-tools`, e
  **não** diz qual conjunto de ferramentas cada agente deve ter — isso é matéria da T68 e do
  contrato de cada pacote, não desta ADR.
- **Teto declarado, porque não dá para fechá-lo aqui:** o `ceo-maestro` confere o **próprio**
  `SKILL.md` com um regex local em `evals/validate_workflow.py`, que extrai `name` e `description`
  e **não** aplica allowlist de chaves. Um campo desconhecido no `SKILL.md` do CEO passaria hoje.
  A lacuna é anterior a esta decisão e não foi criada por ela; fica nomeada como pendência.
- **Trava permanente ainda ausente, e isto foi MEDIDO, não suposto.** O motor compartilhado
  `_compartilhado/teste_validador_schema.py` é **cego** para esta regra: zero ocorrências da
  palavra "frontmatter", e **66/66 PASS tanto com o módulo canonizado quanto com o mutante
  aplicado** — o mutante escapa dele inteiro (Prova C do registro cru). Quem avermelha hoje é
  apenas o efeito colateral nos 16 validadores de pacote, através dos 13 `SKILL.md` reais.
  Consequência assimétrica: **reverter** a canonização é auto-detectável (os 16 ficam vermelhos),
  mas **afrouxar** — passar a ignorar chave desconhecida — não seria pego por nada. Fechar isso
  exige caso próprio num validador, com o adendo de contagem no mesmo ato. **Não foi feito nesta
  rodada**, de propósito: acrescentar caso mexe no denominador dos 16, que é exatamente o número
  que esta rodada foi encarregada de medir. Fica como pendência nomeada, não como coisa provada.

## Alternativas recusadas

- **Reverter os 13 `SKILL.md`.** Desfaria uma decisão de fronteira correta para preservar um
  validador desatualizado. A restrição de ferramenta é o mecanismo que a casa quer; o obstáculo
  era a trava, e trava se atualiza.
- **Aceitar qualquer chave extra** (trocar a igualdade por "contém `name` e `description`").
  Resolveria os 5 FAIL com uma linha e destruiria a garantia inteira: erro de digitação, campo
  inventado e chave de outra camada entrariam calados. Foi explicitamente recusado — a decisão é
  canonizar **um** campo nomeado, não abrir o frontmatter.
- **Conferir só o conjunto de chaves, sem ordem** (`set(keys) <= permitidas`). Perderia a ordem
  canônica e a detecção de chave repetida, que a comparação de lista dá de graça.
- **Declarar `allowed-tools` obrigatório.** Medido em 2026-08-11: a árvore tem **84 `SKILL.md`
  vivos** (fora de `evals/`) e **13** declaram o campo — exigi-lo reprovaria os **71** restantes de
  uma vez, e forçaria a T68 a acontecer hoje por efeito colateral de uma trava, em vez de por
  decisão medida.

---

**Fonte normativa:** [`../../regras-de-ouro/REGRAS-DE-OURO.md`](../../regras-de-ouro/REGRAS-DE-OURO.md) ·
**Anatomia do pacote:** [`../../GUIA-DE-EXPANSAO-E-MIGRACAO.md`](../../GUIA-DE-EXPANSAO-E-MIGRACAO.md) ·
**Fronteira do módulo alterado:** [ADR-015](../diretor-de-lentes/departamentos-operacionais/departamento-arquitetura-software/references/adr-015-checagens-por-pacote-e-de-estrutura-inteira.md)
