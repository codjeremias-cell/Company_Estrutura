# Parecer — `experiencia-e-risco`, instância 1 — recoleta de `C05` e `C06`

- **Rodada:** `recoleta-c03-c05-c06` · **Nível exigido:** `INTERNO`
- **Commit julgado:** `ab5882cf09a95d841168fd52faf656ac55997287`
- **Contrato desta rodada:** [`../../../00-CONTRATO.md`](../../../00-CONTRATO.md), selado em 2026-08-05,
  antes deste parecer existir. Ele sela a árvore como `4446786`; julguei `ab5882c` por instrução do
  despacho, e declaro isso contra mim ao final.
- **Não executei nada.** O executor é o CEO. Tudo que afirmo sobre trava foi **lido** no fonte do
  validador e no schema — nunca observado rodando.

## As cinco notas

| Pacote | Critério | Nota | Razão em uma linha |
|---|---|---:|---|
| `departamento-arquitetura-dados` | `C05` | **7** | O retorno é validado contra o schema do consumidor lido do disco, com negativos; mas o `architectural_constraint` que o pacote diz receber na missão não existe no `departmentMission` do Diretor, que é `additionalProperties:false`. |
| `departamento-desenvolvimento` | `C05` | **8** | As três pernas passam fora do próprio fixture, e o validador abre o schema de dois vizinhos em runtime para provar que a delegação deles aponta para cá; sobram o upstream declarado por booleano e o gerador autodeclarado. |
| `departamento-conteudo-marketing` | `C05` | **7** | O retorno derivado passa no `oneOf` inteiro do Diretor e a matriz com Negócios é conferida no schema do vizinho; falta prova da entrada, e o repasse a Registros não tem campo no envelope do vizinho. |
| `departamento-conteudo-marketing` | `C06` | **7** | Confessa muito e com teto por risco, mas os limites do próprio pacote não têm dono, e o dono que existe é string livre de `minLength 3`. |
| `departamento-qa-usabilidade` | `C06` | **8** | Dono e retomada são exigidos por schema em cada `SKIP` e em cada lacuna, e o pacote nomeia até o limite do envelope do vizinho; sobra a lista do placar sem dono, com um item que contradiz a própria tabela. |

**Mínimo dos meus critérios: 7.**

Nenhuma nota é comparativa. Cada pacote foi medido contra o critério declarado e observado nele
mesmo.

## O FAIL da série de ADR — descontado

Os quatro pacotes acusam **um** `FAIL`, sempre o mesmo: a série global de ADR com o número `020`
duplicado por duas cópias de laboratório em
`ceo-maestro/evals/producao-honesta-2026-08-04/origem-independente-R1/lab/mech/{A,B}/`
(`saida-crua/00-RESUMO.json:121`). É evidência de outra frente. **Descontei nos quatro** e nenhuma
das cinco notas o considera.

## `C05` — uso pela cadeia

O critério pergunta três coisas: se o gerente sabe o que despachar, se o agente sabe a quem
responder, e se o retorno cabe no envelope do vizinho — e avisa que verde no próprio teste não
prova travessia. Foi por esse aviso que li, em cada pacote, o que ele faz **contra o schema do
vizinho**, e não o que ele afirma sobre si.

### `departamento-arquitetura-dados` — 7

O que atravessa, e está provado contra o consumidor:

- o `DATA_LEDGER` é convertido em `DEPARTMENT_RETURN` e validado contra
  `director["$defs"]["departmentReturn"]`, carregado do arquivo real do Diretor, com negativos de
  autor divergente e de retorno endereçado ao CEO (`…/departamento-arquitetura-dados/evals/validate_workflow.py:998-1017`);
- o Diretor reconhece o Departamento em `operationalDepartment` e `knownCapability`, e o
  `delegationTarget` da Arquitetura de Software é lido do schema dela e conferido — a dependência
  que ela emite tem destinatário real (`…:1019-1030`);
- a `DATA_TASK` trava capacidade, agente e onda por `const`, um par por vez
  (`…/schemas/departamento-arquitetura-dados.schema.json:811-934`);
- o agente declara canal único: superior e retorno são a gerente, e não há subordinado
  (`…/agentes/agente-modelo-e-grao/CONTRATO-DE-COMPROMISSO.md:10-11`).

O defeito que segura a nota em 7:

> `protocolo-de-dados.md:10` lista, na tabela de envelopes, que a `DEPARTMENT_MISSION` **pode trazer
> `architectural_constraint`**; o contrato repete que ela é vinculante (`CONTRATO-DE-COMPROMISSO.md:43-46`)
> e o gate G7 depende dela (`protocolo-de-dados.md:71`). O `departmentMission` do Diretor é
> `additionalProperties: false` e **não tem esse campo**
> (`diretor-de-lentes.schema.json:503-567`). O campo existe apenas no `DATA_PLAN` **interno**
> (`…/schemas/departamento-arquitetura-dados.schema.json:632-676`).

Consequência prática: a restrição só viaja como prosa dentro de `inputs`, e nada no pacote valida
uma missão de entrada contra o envelope do vizinho — a fronteira está provada **em uma direção só**.

Dois riscos menores somam-se: `scope_touched`, `artifact_refs` e `candidate_digest` são constantes
escritas no conversor, sem campo correspondente no `DATA_LEDGER` (`validate_workflow.py:390-410`),
e o `candidate_digest` interno admite `"n/a"` (`schema:151-159`) enquanto o envelope do Diretor
exige digest real (`diretor-de-lentes.schema.json:598`) — a conversão está provada na forma, não na
derivabilidade.

### `departamento-desenvolvimento` — 8

- o `DEV_LEDGER` vira `DEPARTMENT_RETURN` **com número real de teste** e passa no schema do Diretor,
  com negativo de autor divergente (`…/departamento-desenvolvimento/evals/validate_workflow.py:544-551`);
- o validador **abre os schemas de dois vizinhos em runtime** e confere que o `delegationTarget`
  deles aponta para cá (`…:557-564`);
- a `DEV_TASK` fixa `return_to` na gerente por `const`
  (`…/schemas/departamento-desenvolvimento.schema.json:674-680`);
- o gate de entrada é mecânico: `upstream_present: false` obriga nomear o que falta **e** zera as
  atribuições (`schema:602-626`), com dois casos negativos (`validate_workflow.py:425-429`);
- ao contrário do vizinho de dados, o conversor deriva `candidate_digest` e `test_summary` do
  próprio livro-razão (`validate_workflow.py:262-276`).

Não achei contradição com o envelope do consumidor: o protocolo fala das decisões upstream
"anexadas" em prosa, sem nomear um campo que não exista.

Riscos que sobram: o upstream chega como booleano mais texto livre (`schema:674-677`), sem `ref` que
amarre a decisão ao artefato de quem a produziu; `generator_used` é autodeclarado e nada prova que o
gerador exista ou tenha sido invocado (R3, `protocolo-de-desenvolvimento.md:71`); e `scope_touched`
e `artifact_refs` continuam constantes do conversor.

### `departamento-conteudo-marketing` — 7

- o `DEPARTMENT_RETURN` derivado é validado contra o schema do Diretor **inteiro**, que é um `oneOf`
  de dez envelopes (`…/departamento-conteudo-marketing/evals/validate_workflow.py:736-737` ·
  `diretor-de-lentes.schema.json:6-17`) — não é checagem vazia: o objeto tem de casar com exatamente
  um dos dez;
- `validate_inherited_authority` confere, **no schema do vizinho**, que o Diretor reconhece este
  Departamento, que o retorno aponta ao Diretor, que a troca matricial com Negócios existe nos dois
  sentidos e que o pedido aos Juízes é exclusivo do Diretor (`validate_workflow.py:568-601`);
- o `MARKETING_ASSIGNMENT` fixa `return_to` na gerente, com caso negativo que rejeita retorno
  endereçado ao Diretor (`…:751-753`);
- a lacuna aberta **viaja ao vizinho**: `open_gap_refs` entra em `pending_refs` do retorno (`…:402`).

Riscos: nenhuma missão de entrada é validada contra o `departmentMission` do Diretor — a admissão do
§1 do `SKILL.md` existe só em prosa; a fronteira com Registros manda "registrar no
`DEPARTMENT_RETURN` a necessidade, natureza provável e evidência"
(`protocolo-conteudo-marketing.md:124-139`), e esse envelope é `additionalProperties:false`
(`diretor-de-lentes.schema.json:568-604`), de modo que a passagem só cabe sobrecarregando
`pending_refs`, sem caso que a prove; e `scope_touched`/`artifact_refs` são constantes
(`validate_workflow.py:387-389`).

## `C06` — limites declarados

O critério cobra três coisas juntas: **o que não fecha**, o **dono** e a **condição de fechamento
verificável** — e nomeia o defeito: confessar o que passa e calar o que não passa.

### `departamento-conteudo-marketing` — 7

O que está declarado, e bem:

- oito riscos residuais em que **cada linha traz um teto** dizendo o que a mitigação não resolve —
  "documento falso requer verificação externa", "runtime sem canal autenticado não elimina
  falsificação" (`protocolo-conteudo-marketing.md:155-169`);
- sete itens de placar como `SKIP` com motivo, e a regra "SKIP não é PASS"
  (`evals/PLACAR.md:51-63`);
- um veredito de auditoria que **delimita para que a aprovação não vale** — publicar, comprar mídia,
  enviar e-mail, declarar resultado comercial (`PLACAR.md:65-72`);
- a lacuna de runtime é mecanizada: `MARKETING_CAPABILITY_GAP` exige `recovery_owner` e
  `recovery_condition`, e trava `status` em `OPEN` — a gerente não fecha a lacuna que abriu
  (`schemas/departamento-conteudo-marketing.schema.json:799-843`).

O que falta, e é exatamente o que o critério pede:

1. os limites **do próprio pacote** — os oito riscos e os sete `SKIP` — **não têm dono nenhum**; e o
   que o risco traz é *teto*, que é o oposto de condição de fechamento: diz que aquilo não fecha;
2. onde o dono existe, ele é **string livre de `minLength 3`**, assim como a condição
   (`schema:835-842`). `"TBD"` satisfaz o schema. Dono declarado não é dono verificável, e a palavra
   do critério é **verificável**.

Não encontrei confissão seletiva: o pacote não esconde o inconveniente. A nota é 7 porque metade da
exigência — dono e condição verificáveis — só existe para a lacuna de runtime.

### `departamento-qa-usabilidade` — 8

O critério está atendido no nível em que o pacote opera, e por schema, não por prosa:

- **todo `SKIP`** carrega `skipDetail` com `reason`, `impact`, **`owner`** e **`resume_when`**,
  `additionalProperties:false` (`schemas/departamento-qa-usabilidade.schema.json:441-456`), imposto
  pelo ramo condicional do resultado (`:533-546`), com a mutação `SKIP sem detalhe` para provar a
  trava (`evals/validate_workflow.py:1658-1660`);
- a `QA_CAPABILITY_GAP` fixa `owner` em `const: diretor-de-lentes` e exige `recovery_condition`,
  `impact`, `blocked_criterion_ids` e `safe_state: Q_BLOCKED` (`schema:1229-1262`);
- sete riscos residuais com teto por linha (`protocolo-qa-usabilidade.md:390-403`);
- e o mais raro: o pacote **nomeia um limite do envelope do vizinho** — o `DEPARTMENT_RETURN` não
  tem campo para `UNVERIFIED` nem `MISSING` —, declara o transporte conservador como skip rotulado e
  pendência (`SKILL.md:238-240`), e o validador confere que a incerteza continua visível na fronteira
  e **rejeita zerá-la** (`validate_workflow.py:2035-2054`).

O risco que sobra, em três pontos:

1. a lista "O que ainda não foi provado" do placar não tem dono nem condição de fechamento em
   nenhum dos três itens (`evals/PLACAR.md:51-57`);
2. o terceiro item — `quick_validate.py` com PyYAML — **contradiz a mesma tabela**, que declara
   `4/4 Skill is valid!` com PyYAML 6.0.3 instalado (`PLACAR.md:24`) e depois afirma que "a limitação
   ambiental permanece declarada" (`PLACAR.md:40-42`). É um limite declarado aberto que o próprio
   documento diz fechado;
3. o adendo afirma que o FAIL da série de ADR "está registrada como tarefa aberta com dono"
   **sem nomear o dono** (`PLACAR-ADENDO-2026-08-05-contagem-do-validador.md:42`).

Fiquei em 8 porque a contradição é conservadora — declara aberto o que já fechou, nunca o contrário,
que é o defeito que o critério persegue.

## O que não consegui avaliar, e por quê

- **Disparo e uso reais.** Nenhum dos quatro é skill invocável no runtime — a porta é o
  `ceo-maestro` — e não há forward de acionamento vigente nos pacotes que julguei. Onde `C05` pede
  uso pela cadeia, o que medi foi **operabilidade de fronteira**, e digo isso em vez de fingir que
  medi uso.
- **Execução.** Não rodei validador nenhum. As travas que descrevo foram lidas no fonte; caso lido
  não é caso executado. Os números vigentes são os da saída crua do CEO
  (`saida-crua/00-RESUMO.json`), e não os reproduzi.
- **Cobertura dos agentes.** Li **um** contrato de agente por pacote. A perna "o agente sabe a quem
  responder" está amostrada e complementada pelos `const` de `return_to` nos schemas — não varrida
  nos 25 contratos.
- **Diff entre `4446786` e `ab5882c`.** Não o conferi. Minha leitura vale para `ab5882c`.

## O que declaro contra mim

1. **Não executei nada.** Se alguma das travas que descrevo estiver morta em runtime, o 8 do
   Desenvolvimento e o 8 do QA caem — e eu não teria como perceber pela leitura.
2. **Amostrei contratos de agente** (um por pacote) e inferi o resto por `const` de schema.
3. **No `arquitetura-dados` hesitei entre 6 e 7.** Uma leitura mais dura de "acionado pela cadeia"
   trata o `architectural_constraint` sem campo no `departmentMission` como lacuna de cobertura, e
   não como risco — e aí a nota seria 6, que muda o veredito do pacote. Fiquei em 7 porque as três
   perguntas literais do critério passam e a restrição ainda chega como prosa em `inputs`. O leitor
   tem o direito de saber que ficou a um argumento do corte.
4. **No `qa-usabilidade` hesitei entre 7 e 8, pelo motivo inverso.** A contradição do
   `quick_validate.py` é defeito observado dentro do documento onde o critério se lê, e a banda 7–8
   pede "sem defeito observado". Quem der peso maior à literalidade da banda chega a 7.
5. **Dei 7 a três pares distintos.** Não foi por comparação: cada 7 tem evidência e defeito
   próprios, e as razões são diferentes entre si. Mas registro o risco de uma lente que vê quatro
   pacotes da mesma casa escorregar para uma média implícita.
6. **A árvore que julguei não é a que o contrato selou.** O contrato diz `4446786`; julguei
   `ab5882c` por instrução do despacho, sem conferir o diff.
