# As dez dimensões, os estados e o veredito

Fonte única da matriz de conformidade. A gerente resolve esta referência **antes** de emitir a
primeira `AUDIT_TASK` e a aplica sem variação; agente nunca inventa dimensão, estado ou mapeamento.

## 1. As dez dimensões e suas donas

O conjunto é **fixo em dez**. Não se acrescenta, não se remove e não se funde dimensão: mudança
aqui exige ADR. Cada uma tem exatamente uma **dona**; duas têm um **segundo inspetor**, porque o
fato observado cai legitimamente em duas fronteiras.

| # | Dimensão | Dona | Segundo inspetor | Bloqueia quando |
|---:|---|---|---|---|
| 1 | `INTENT` | contrato-e-autoridade | — | entrega, documentação ou teste contradiz o contrato |
| 2 | `AUTH` | contrato-e-autoridade | — | ação externa ou irreversível ocorreu sem autorização exata **anterior** |
| 3 | `ESCOPO` | contrato-e-autoridade | — | item tocado excede o autorizado |
| 4 | `PENDING` | contrato-e-autoridade | governanca-e-responsabilidades | obrigação bloqueante segue aberta |
| 5 | `RACI` | governanca-e-responsabilidades | — | decisão, entrega, prova ou correção não tem exatamente um `A`, ou o aceite não é demonstrável |
| 6 | `RI_RO` | governanca-e-responsabilidades | — | regra aplicável foi violada, ou skill aplicável foi pulada (RI-06) |
| 7 | `SURPRESAS_BYPASS` | governanca-e-responsabilidades | contrato-e-autoridade | houve correção sem autoridade, bypass de gerente ou falta de encaminhamento |
| 8 | `EVIDENCIA` | evidencias-e-artefatos | — | conclusão não possui prova fresca, independente e conferida |
| 9 | `ARTEFATOS_TWINS` | evidencias-e-artefatos | — | artefato real não sustenta o relato, ou gêmeos divergem |
| 10 | `RASTREABILIDADE` | evidencias-e-artefatos | — | não existe cadeia veredito → finding → critério → evidência → artefato |

**Por que `PENDING` tem dois inspetores.** Contrato-e-autoridade responde se a promessa **está
aberta** — foi fechada por prova ou por renegociação explícita? Governança responde se ela **tem
dono** — existe um `A` que responde pelo fechamento? Uma pendência com prova de fechamento e sem
dono continua sendo achado, e vice-versa.

**Por que `SURPRESAS_BYPASS` tem dois inspetores.** Governança é dona porque o bypass é falha de
cadeia de comando. Contrato-e-autoridade entra como segundo inspetor porque a **surpresa de
escopo** — o item que apareceu e ninguém pediu — é observada no diff, não no organograma.

## 2. Os cinco estados

| Estado | Significa | Efeito |
|---|---|---|
| `CONFORME` | a dimensão foi verificada e atende, com prova conferida | não bloqueia |
| `NAO_APLICAVEL` | a dimensão não incide neste candidato, **com justificativa específica** | não bloqueia |
| `RESSALVA` | achado real, **comprovadamente não bloqueante** | não bloqueia, mas vira `pending` obrigatório |
| `NAO_CONFORME` | a dimensão foi verificada e **não** atende | **bloqueia** |
| `NAO_PROVADO` | não foi possível verificar: falta insumo, prova, acesso ou independência | **bloqueia** |

`NAO_PROVADO` **não é neutro**. Ele bloqueia tanto quanto `NAO_CONFORME`, e é a razão de o
Departamento nunca devolver "não consegui auditar": dossiê incompleto vira `NAO_PROVADO` na
dimensão afetada, com o insumo faltante nomeado.

`NAO_APLICAVEL` exige **justificativa específica daquele candidato**. "Não se aplica" genérico é
`NAO_PROVADO`: se ninguém consegue dizer por que a dimensão não incide, ninguém a verificou.

### Regra anti-rebaixamento

Falha bloqueante de `AUTH`, `ESCOPO`, `INTENT`, prova fresca, `ARTEFATOS_TWINS` ou RI/RO aplicável
é `NAO_CONFORME`. **Nenhum rótulo a rebaixa** para `RESSALVA` ou `NAO_APLICAVEL`: mudar o nome não
muda o efeito do contrato. Rebaixamento observado é, ele próprio, achado bloqueante na dimensão
`SURPRESAS_BYPASS`.

## 3. Consolidação: o estado mais grave vence

Dimensão com dois inspetores recebe dois estados. O da matriz é o **mais grave** dos dois, e o
outro fica registrado como linha própria com a divergência preservada. Ordem total, aplicada uma
vez e sem exceção:

```text
NAO_CONFORME  >  NAO_PROVADO  >  RESSALVA  >  CONFORME  >  NAO_APLICAVEL
```

`CONFORME` vence `NAO_APLICAVEL` de propósito: se um inspetor achou a dimensão aplicável e
conforme, a aplicabilidade está demonstrada, e declarar não-aplicável apagaria uma verificação que
existiu. **Proibido** mediar, tirar "consenso" ou escolher o estado mais favorável.

## 4. Veredito interno e binário de fronteira

Aplicar **uma única vez, nesta ordem; a primeira regra que casar decide** e nenhuma posterior é
avaliada:

1. existe qualquer dimensão `NAO_CONFORME` ou `NAO_PROVADO` → **`REPROVADO`**;
2. não existe bloqueio e existe ao menos uma `RESSALVA` → **`APROVADO_COM_RESSALVAS`**;
3. não existe bloqueio nem ressalva → **`APROVADO`**.

Os três estados são mutuamente exclusivos, e é o veredito que a **RI-05** exige. A tradução para o
`GOVERNANCE_REPORT` que atravessa ao CEO é determinística:

| Veredito interno | `verdict` | `violations[]` | `pending` |
|---|---|---|---|
| `REPROVADO` | `NONCOMPLIANT` | **uma por dimensão bloqueada**, nomeando dimensão, achado e dono | o que houver |
| `APROVADO_COM_RESSALVAS` | `COMPLIANT` | **vazio** | **uma por ressalva**, com dono, impacto e condição de fechamento |
| `APROVADO` | `COMPLIANT` | **vazio** | pode ser vazio |

`COMPLIANT` com `violations` não vazio, ou `NONCOMPLIANT` com `violations` vazio, é envelope
inválido — o schema do CEO rejeita os dois.

**Nenhuma nota.** Não existe soma, média, percentual de dimensões conformes ou corte de 9,5 neste
Departamento. Quem pontua o candidato é o `departamento-juizes`
([ADR-003](adr-003-conformidade-sem-nota.md)).

## 5. Fronteira com o Departamento de Juízes

A dimensão `EVIDENCIA` e a ótica `robustez-e-evidencia` dos Juízes olham para o mesmo artefato com
perguntas diferentes. A linha é **processo × mérito**:

| Pergunta | De quem |
|---|---|
| A prova existe, é fresca, é independente e a cadeia de custódia fecha? | **Auditoria** |
| A prova sustenta tecnicamente a alegação, e o candidato trata as bordas? | **Juízes** |
| Quem respondeu por esta decisão, e o aceite é demonstrável? | **Auditoria** |
| A decisão foi boa? | **Juízes** |
| A regra aplicável foi cumprida? | **Auditoria** |
| Quanto vale o resultado, de 0 a 10? | **Juízes** |

Na dúvida sobre um achado: se a correção passa por **conseguir ou reorganizar prova, autorização
ou responsável**, é Auditoria. Se passa por **mudar o artefato**, é Juízes.

**Concluído quando:** as dez dimensões têm estado com prova, o estado de cada dimensão com dois
inspetores é o mais grave dos dois com a divergência registrada, o veredito interno casa exatamente
uma das três regras, e o binário de fronteira foi derivado pela tabela — sem nota em lugar nenhum.
