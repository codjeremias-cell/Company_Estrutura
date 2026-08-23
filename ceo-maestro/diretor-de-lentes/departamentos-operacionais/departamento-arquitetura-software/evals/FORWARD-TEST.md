# Forward comportamental — Departamento de Arquitetura de Software

Data: 2026-07-26
Instâncias: **16 independentes**, uma por caso

## Método

Uma instância por caso, com apenas o caminho do `SKILL.md` e o prompt. Resposta completa gravada em
`scratchpad/forward/arq-NN.md`; retorno compacto do que **recusou**, do que **entregou** e de **toda
afirmação numérica, de API ou de regra**. Os `assertions` não foram mostrados às instâncias.

## Resultado

| Medida | Resultado |
|---|---|
| Casos rodados | **16 de 16** |
| Asserções | **60/65 PASS** |
| Contorno de contrato | **zero** |
| Casos com nota cheia | **11 de 16** |

## Dois defeitos reais no pacote — corrigidos

Três instâncias independentes (casos **1, 12 e 16**) reportaram que os gabaritos de
`delegated_dependency` da referência produziam artefato que o próprio schema recusa:

| Gabarito | Defeito | Confirmado |
|---|---|---|
| **Regra D** | 4 campos; faltava `decision_rule`, que é `required` | sim |
| **Regra S** | tinha `design:`, inexistente no schema (`additionalProperties: false`); faltavam `blocks` e `architectural_constraint` | sim |

O caso 2 **reproduziu o defeito na prática** — copiou o gabarito e usou `design:` no bloco que
emitiu. Não era pedantismo de conformidade: uma instância seguindo a documentação à risca produzia
um artefato inválido.

**Correção aplicada:** os dois gabaritos agora têm exatamente os cinco campos do schema. E foi
adicionada uma **guarda no validador** que compara os gabaritos da referência com o
`delegatedDependency` — provada removendo `decision_rule` e confirmando que o validador reprova
(`71/72`) e volta a passar com a linha restaurada (`72/72`).

O vão era este: o validador conferia o schema, conferia os links, e **nunca conferia se o exemplo em
prosa era válido contra o schema**. Duas verificações corretas com um buraco entre elas.

## As cinco asserções que não fecharam

**Quatro são defeito do catálogo** (casos 1, 10, 11, 15). Todas pedem variações de *"fixa a
restrição arquitetural"*, mas os prompts são pedidos crus, sem missão e sem os nove drivers. A
restrição **não existe para ser fixada** — e as instâncias marcaram `PENDING` em vez de inventar,
que é exatamente o que o caso 2 do mesmo catálogo exige delas. A asserção pressupõe contexto que o
prompt não fornece.

É o terceiro pacote em que esse padrão aparece (caso 1 dos Juízes, caso 3 do Design, quatro aqui).

**Uma é lacuna de cobertura** (caso 7, *"a trava vale mesmo vindo de Jeremias"*): a instância não
tratou a cláusula. O caso 8, do mesmo pacote, tratou — *"ordem de Jeremias mudaria o contrato por
ADR, não a rodada"*.

## Comportamentos notáveis

- **Caso 3** recusou a moda *e* o erro espelhado: *"não respondi 'faz monolito'"*.
- **Caso 5** resolveu o problema real do cliente mudando o **formato**, não omitindo a perda —
  *"recomendação sem perda declarada é propaganda"*.
- **Caso 6** **testou a válvula de escape da própria RI-01** e a descartou com argumento: síncrono ×
  assíncrono *é* a decisão, não detalhe de execução dentro dela.
- **Caso 8** verificou suas afirmações direto no schema do Diretor antes de afirmá-las.
- **Caso 13** citou duas coisas sobre o código do pacote; ambas verificadas: `acumulo_proibido()`
  com `frozenset({"ALTERNATIVAS","ADR_C4"})` existe na linha 134, e `ADR_C4` tem `wave: {const: 4}`.
- **Caso 15** entregou o acoplamento como pergunta operacional: *"qual fluxo quebra primeiro se os
  dois escreverem o mesmo cliente ao mesmo tempo?"*.
- **Caso 16** recusou ratificar: *"ratificar é aprovar, e julgar é dos Juízes"*.

## Lacuna estrutural detectada de fora

O caso 15 verificou e reportou: **oito departamentos operacionais no disco e zero diretórios
`*desenvolvimento*`**, embora o nome conste dos enums `operationalDepartment` e `delegationTarget`.
Consistente com o achado dos roteadores cegos no forward do Design. As dependências que este
Departamento emite para o Desenvolvimento continuam sem destinatário no caminho canônico.

## O que este forward NÃO prova

1. **Disparo orgânico** e **acionamento por roteamento cego** — não medidos aqui.
2. **Operação com missão íntegra.** Como na Auditoria, quase todos os casos foram resolvidos no
   portão: os prompts não chegam como `DEPARTMENT_MISSION`. O que está bem medido é a recusa.
3. **Baseline do legado** — a `lente-arquiteto-software` não foi submetida aos mesmos cenários.
4. **Auditoria independente e parecer dos Juízes** — pendentes.
