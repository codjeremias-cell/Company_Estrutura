# Company_Estrutura — a empresa de skills

Uma estrutura organizacional completa para agentes de IA: **81 skills** distribuídas em CEO,
Diretoria, Departamentos e agentes executores, com contrato, schema JSON, validador determinístico
e placar de honestidade em cada pacote.

Não é um catálogo de skills soltas. É uma **cadeia de comando** onde cada unidade tem fronteira
exclusiva, cada envelope tem destinatário travado por schema, e nenhuma unidade valida a própria
entrega.

```text
Jeremias
  └── ceo-maestro                          decide rota e fechamento; não executa
      ├── departamento-negocios            estratégia, mercado, viabilidade
      ├── departamento-evolucao-skills     cria e evolui as skills da própria estrutura
      └── diretor-de-lentes                dirige a produção técnica
          ├── departamento-juizes          nota e veredito — camada paralela, sem canal lateral
          └── 10 departamentos operacionais
              └── 66 agentes executores    folhas: sem delegação, sem contato lateral
```

## Estado medido — 2026-07-26

| Bateria | Resultado |
|---|---|
| Cadeia canônica completa | **1531/1531 PASS · 0 FAIL** (motor compartilhado 61 + 15 validadores de pacote) |
| Links markdown da árvore | **1.002 checados · 0 quebrados** |
| Corpus adversarial (Inovação e Melhoria) | **45/45 mutações rejeitadas · 0 escapes** |
| `quick_validate.py` do `skill-creator` | PASS onde executado |
| Arquivos · tamanho | 409 · 4,5 MB |

Reproduzir:

```bash
PYTHONIOENCODING=utf-8 python "_compartilhado/teste_validador_schema.py"
for f in $(find . -name validate_workflow.py | sort); do
  d=$(dirname $(dirname "$f"))
  printf "%-42s " "$(basename "$d")"
  (cd "$d" && PYTHONIOENCODING=utf-8 python evals/validate_workflow.py 2>&1 | grep -oiE '[0-9]+/[0-9]+' | tail -1)
done
```

O terminal do autor é cp1252 e os validadores imprimem seta: **sempre** `PYTHONIOENCODING=utf-8`.
Cada validador roda a partir da **própria pasta do pacote** — ele infere a raiz pelo caminho do
próprio arquivo. Não há dependência de rede: só a biblioteca padrão do Python.

## O que este repositório NÃO prova

Esta seção existe porque a estrutura já foi mordida pela ausência dela. Em 2026-07-26, o
`departamento-inovacao-melhoria` passou uma rodada inteira com o validador imprimindo **59/59 PASS**
enquanto **39 de 45 mutações adversariais escapavam** — o verde media forma, não semântica. A lição
virou norma: *placar que só tem verde mente*.

**1. Num clone isolado, 5 dos 1531 checks falham — por desenho.**
Três pacotes (`inovacao-melhoria`, `qa-usabilidade`, `conteudo-marketing`) verificam por SHA-256 que
suas **fontes legadas** continuam intactas. Essas fontes vivem em `SKILL - Nova formula/`, fora desta
estrutura, e **não** foram publicadas aqui. Clonado sozinho, o repositório reporta **1526 PASS e 5
FAIL**, todos com a mensagem "legado ausente".

Isso é correto e deliberado: sem a árvore legada ao lado, a alegação "o legado não foi alterado"
**não pode ser feita**, e transformá-la em `SKIP` silencioso seria exatamente o antipadrão que o
resto da estrutura proíbe. O número 1531/1531 só se reproduz com o cofre completo.

**2. Nenhuma das 81 skills está instalada em runtime.**
Toda aderência medida até aqui foi sob **carga explícita de caminho**. Nada aqui prova que uma skill
**dispara sozinha** a partir da sua `description`. Todo forward comportamental desta estrutura tem
esse `SKIP` declarado.

**3. A conformidade normativa é parcial, e a lacuna é grande.**
O `GUIA-DE-EXPANSAO-E-MIGRACAO.md` prescreve 12 seções obrigatórias no contrato de gerente, 11 no de
agente e 6 tokens na SKILL de agente. Medido hoje:

| Dimensão | Conformes |
|---|---|
| Contratos de agente | **15 de 66** |
| SKILL.md de agente | **23 de 66** |
| Contratos de gerente | **8 de 15** |
| Protocolos (`Concluído quando:` + riscos residuais com `Teto`) | **5 de 15** |

Quatro anatomias rivais coexistem. Três pacotes estão 100% conformes e servem de referência:
`departamento-inovacao-melhoria`, `departamento-registros` e `departamento-seguranca`. A trava
anti-bypass que o guia chama de obrigatória **não existe em 30 dos 66 agentes**.

**4. Prova comportamental é escassa e parcial.**
A maioria dos pacotes tem catálogo de evals escrito e forward executado sob carga; alguns nunca
executaram nenhum. Onde executou, há asserções que falharam e estão nomeadas como pendência aberta
no `PLACAR.md` do pacote — não escondidas.

**5. Nada aqui foi julgado.**
Nenhum pacote passou pelo gate do `departamento-juizes`. Nenhuma nota foi atribuída.

## Como está organizado

| Caminho | O que é |
|---|---|
| `ORGANOGRAMA.md` | quem existe, quem manda em quem, e o estado real de cada migração |
| `AGENTS.md` | porta de entrada operacional — a hierarquia em uma página |
| `GUIA-DE-EXPANSAO-E-MIGRACAO.md` | manual único: criar, migrar, consolidar, expandir e evoluir um pacote |
| `regras-de-ouro/REGRAS-DE-OURO.md` | fonte normativa única — 6 regras inquebráveis (RI) e 53 de ouro (RO) |
| `_compartilhado/` | motor de validação de JSON Schema e verificações estruturais, importado por todos |
| `ceo-maestro/` | a árvore inteira: CEO, Diretor, Departamentos e agentes |
| `registros/` | pasta de saída de runtime para relatórios de aprendizagem |

Anatomia de um pacote de Departamento:

```text
departamento-<nome>/
├── SKILL.md                      identidade e workflow
├── CONTRATO-DE-COMPROMISSO.md    autoridade, obrigações, proibições, barreira de saída
├── agents/openai.yaml            interface de runtime
├── references/                   protocolo, ADR, fronteiras, proveniência da migração
├── schemas/<nome>.schema.json    envelopes internos, fechados
├── evals/                        evals.json, validate_workflow.py, PLACAR.md, FORWARD-TEST.md
└── agentes/<agente>/             SKILL.md + CONTRATO + agents/openai.yaml (folhas, sem subpastas)
```

## Os princípios que a estrutura tenta materializar

**Ninguém valida a própria entrega.** Nota e veredito são exclusivos do `departamento-juizes`,
acionado só pelo Diretor. Conformidade é do `departamento-auditoria-responsabilidades`, que fornece
prova e não nota. Um Departamento que se pontuasse seria juiz em causa própria.

**Gerente orquestra, não executa.** Cada Departamento planeja, delega aos seus agentes e integra —
mas não produz a análise especializada no lugar de um agente ausente. Quando falta capacidade, sai
um `CAPABILITY_GAP` com busca registrada, não um substituto silencioso.

**Agente é folha.** Não delega, não cria subagente, não fala com agente irmão, não recebe ordem de
fora da própria gerente. Pedido por bypass vira bloqueio registrado.

**Ausência de evidência permanece ausência.** `PENDING`, `UNVERIFIED`, `SKIP` e silêncio nunca viram
sucesso. `test_summary` de quem não executa bateria é `0/0/0`.

**A trava mora no código, não na prosa.** Aviso em documento já falhou repetidas vezes nesta base. O
que precisa valer vira caso no validador — inclusive a estrutura normativa dos contratos e a
honestidade do próprio placar.

**Booleano declarado não é prova.** O gate de uma iniciativa é **recalculado** a partir da evidência
real dos retornos e só passa se coincidir com o declarado. Referência sem digest recalculável é
tratada como referência inventada.

## Requisitos

**Python 3.9+** — o piso é `pathlib.Path.is_relative_to`; os 19 módulos que usam sintaxe moderna de
anotação declaram `from __future__ import annotations`, e não há `match`/`case`, `tomllib` nem
`ExceptionGroup` em lugar nenhum. Medido, não estimado. Validado em **3.14.6**.

**Nenhuma dependência externa** para a cadeia de validação: só a biblioteca padrão. O
`quick_validate.py` do `skill-creator`, que é ferramenta de fora deste repositório, precisa de PyYAML
e de `PYTHONUTF8=1` no Windows — sem isso ele lê os arquivos em cp1252 e quebra na primeira aspa
tipográfica.

## Estado

Migração em andamento. Estrutura materializada e mecanicamente verificada; **prova comportamental em
runtime é a dívida principal**. O `ORGANOGRAMA.md` mantém o estado por pacote e o `PLACAR.md` de cada
um mantém o que ele consegue e o que ele **não** consegue provar.

Repositório privado, de uso pessoal de Jeremias.
