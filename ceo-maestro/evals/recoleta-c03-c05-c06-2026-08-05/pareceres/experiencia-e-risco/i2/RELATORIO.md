# Parecer — `experiencia-e-risco`, instância 2 — recoleta de `C05` e `C06`

- **Juiz:** `agente-julgar-experiencia-e-risco`, instância **2**
- **Rodada:** `recoleta-c03-c05-c06`
- **Commit julgado:** `ab5882cf09a95d841168fd52faf656ac55997287`
- **Nível exigido:** `INTERNO`
- **Rubrica:** `rubrica-corte-v2` (bandas 0–3 · 4–6 · 7–8 · 9 · 10)
- **Não executei nada.** O CEO é o executor; a saída crua de
  [`saida-crua/`](../../../saida-crua/) foi lida como fato, não reproduzida.

## As cinco notas

| pacote | critério | nota | razão em uma linha |
|---|---|---:|---|
| `departamento-arquitetura-dados` | `C05` | **8** | Travessia provada contra o schema do consumidor e a restrição do vizinho entra no envelope da tarefa; a única conversão definida descarta `delegated_dependencies` e a missão de entrada nunca é materializada. |
| `departamento-desenvolvimento` | `C05` | **7** | Saída tipada e aceita pelo consumidor, dois vizinhos delegam para cá; a decisão upstream chega como booleano autodeclarado e a `DEV_TASK` não tem campo para transportá-la ao agente. |
| `departamento-conteudo-marketing` | `C05` | **8** | Verifica a estrutura do vizinho em mais pontos do que o retorno exige e leva pendência e lacuna como dado; a necessidade de custódia não tem campo no envelope do Diretor e a missão de entrada não é materializada. |
| `departamento-conteudo-marketing` | `C06` | **8** | Dono obrigatório por schema na lacuna e nas oito linhas de prontidão, oito riscos com coluna **Teto**; os limites do próprio placar não nomeiam dono nem condição. |
| `departamento-qa-usabilidade` | `C06` | **7** | Dono e `resume_when` obrigatórios em todo `SKIP` e pendência, tetos declarados e a confissão do que o envelope do vizinho não carrega; o placar se contradiz sobre um dos próprios limites. |

**Mínimo dos meus critérios: 7.**

Nunca comparei um Departamento com outro. Cada nota é contra o critério declarado e observado
naquele pacote.

## O desconto que declaro

**Descontei o FAIL da série global de ADR nos quatro.** Ele acusa o número `020` duplicado em duas
cópias de laboratório sob
`ceo-maestro/evals/producao-honesta-2026-08-04/origem-independente-R1/lab/mech/A|B/`, evidência de
outra frente. Não é defeito de nenhum destes quatro pacotes, e nenhuma nota subiu nem desceu por
causa dele.

## `C05` — uso pela cadeia

O critério faz três perguntas: o gerente sabe o que despachar, o agente sabe a quem responder, o
retorno cabe no envelope do vizinho. E avisa que verde no próprio teste não prova travessia. Foi
esse aviso que orientou a leitura: procurei prova **contra o schema do consumidor**, e depois fui
ler a conversão linha a linha.

### `departamento-arquitetura-dados` — 8

O que sustenta a banda:

- o `DATA_LEDGER` é convertido e validado contra
  `diretor-de-lentes.schema.json#/$defs/departmentReturn` — não contra o próprio schema —, com
  negativos para autor divergente do produtor e para retorno endereçado ao CEO
  (`.../departamento-arquitetura-dados/evals/validate_workflow.py:999`);
- o validador confere o outro lado: o Diretor reconhece este Departamento em
  `operationalDepartment` e em `knownCapability`, e o `delegationTarget` da Arquitetura de Software
  aponta para cá (`.../evals/validate_workflow.py:1019` e `:1025`);
- o gerente sabe o que despachar por `const`, não por convenção: o par capacidade↔agente é travado
  na `DATA_TASK`, e o agente devolve por `return_to` travado na gerente
  (`.../schemas/departamento-arquitetura-dados.schema.json:785`);
- a restrição do vizinho **entra no envelope**: `architectural_constraint` no `DATA_PLAN` e
  `inherited_constraint` na `DATA_TASK` (`.../schemas/...:673` e `:781`); e a dependência ao
  Desenvolvimento só é válida com `attached_constraint` de no mínimo 20 caracteres
  (`.../schemas/...:212`).

Os dois riscos que impedem o 9:

1. **A conversão perde a dependência.** `to_department_return`
   (`.../evals/validate_workflow.py:390`) monta o envelope sem `delegated_dependencies` e fixa
   `pending_refs: []`, mesmo com o `DATA_LEDGER` da fixture trazendo uma dependência preenchida
   (`:352`). As dependências para Desenvolvimento e Segurança cruzam a fronteira apenas como
   conteúdo do ledger citado em `evidence_refs` — sem sinal tipado que o Diretor possa ler para
   saber que há trabalho esperando do outro lado. E não há tabela de mapeamento em lugar nenhum: o
   protocolo diz que a conversão é "mecânica" (`references/protocolo-de-dados.md:21`) e essa
   função é a única definição dela na árvore.
2. **A entrada não é materializada.** `DEPARTMENT_MISSION` nunca é instanciada nem validada contra
   `#/$defs/departmentMission`; aparece só como `department_mission_ref`. A recusa de missão de
   origem indevida, que o contrato promete, permanece em prosa.

### `departamento-desenvolvimento` — 7

O que sustenta a banda:

- o `DEV_LEDGER` vira `DEPARTMENT_RETURN` **com número real de teste** e é validado contra o schema
  do Diretor, com negativo para autor divergente
  (`.../departamento-desenvolvimento/evals/validate_workflow.py:544`);
- o validador confere que Arquitetura de Software **e** Arquitetura de Dados delegam para cá
  (`.../evals/validate_workflow.py:557`);
- o que sai daqui sai tipado: `delegationTarget` com cinco vizinhos reais e `attached_context`
  obrigatório na dependência (`.../schemas/departamento-desenvolvimento.schema.json:109` e `:451`).

O que o mantém no piso:

1. **A decisão do vizinho não entra no envelope.** A chegada do upstream é um booleano
   autodeclarado, `upstream_present` (`.../schemas/...:544`), sem referência nem digest do artefato
   que a produziu. E a `DEV_TASK` não tem nenhum campo para a decisão herdada
   (`.../schemas/...:632`) — o agente pode implementar sem que grão, plano de migração ou token
   tenham entrado no envelope, e o schema não percebe. Este é o Departamento cuja função declarada é
   materializar o que três vizinhos decidiram; é justamente aí que a fronteira de entrada fica sem
   mecanismo.
2. **A travessia de dependência e pendência não é exercitada.** A fixture do ledger tem
   `delegated_dependencies: []` e `capability_gaps: []` (`.../evals/validate_workflow.py:254`) e a
   conversão fixa `pending_refs: []` (`:274`). O caminho existe no schema interno; a passagem dele
   pela fronteira não tem caso.

### `departamento-conteudo-marketing` — 8

O que sustenta a banda — este pacote verifica a estrutura do vizinho em mais pontos do que o próprio
retorno exigiria (`.../departamento-conteudo-marketing/evals/validate_workflow.py:568`):

- matriz do Diretor com exatamente dez Departamentos; `departmentReturn` aceitando este produtor e
  apontando ao Diretor; troca matricial Diretor↔Negócios provada nos dois sentidos por `const`;
  `judgmentRequest` exclusivo do Diretor na origem e no retorno; parecer independente com produtor
  travado nos Juízes; Registros reconhecido como custódia;
- tokens de fronteira externa exigidos na `SKILL.md`, no contrato, no protocolo e no `SKILL.md` do
  agente de inteligência (`.../evals/validate_workflow.py:602`);
- retorno derivado aceito pelo Diretor e três negativos: autoaceite `ACCEPTED`, produtor causal
  forjado e retorno pulando o Diretor (`:737`, `:819`–`:829`);
- **pendência bloqueante e lacuna aberta cruzam a fronteira como dado**, não como prosa:
  `pending_refs = blocking_pending_refs + open_gap_refs` (`:402`);
- o agente sabe a quem responder, com negativo para atribuição que devolve fora da gerente
  (`agentes/agente-narrativa-redacao/CONTRATO-DE-COMPROMISSO.md:9`).

Os dois riscos:

1. **Um handoff mandado sem campo para caber.** O protocolo manda registrar no `DEPARTMENT_RETURN` a
   necessidade de custódia institucional, sua natureza provável e a evidência
   (`references/protocolo-conteudo-marketing.md:132`). O envelope do Diretor é
   `additionalProperties: false` com quinze campos fixos
   (`diretor-de-lentes.schema.json:568`) e não tem nenhum para isso. A necessidade só pode viajar
   como referência sem tipo, e nenhuma conversão conservadora é declarada para ela.
2. **A entrada não é materializada.** A `SKILL.md` manda consumir a `DEPARTMENT_MISSION` do schema
   do Diretor, mas nenhum caso instancia uma missão nem prova a recusa de missão endereçada a outro.

## `C06` — limites declarados

O critério pede três coisas: dizer o que **não** fecha, com **dono**, e com **condição de fechamento
verificável**. E nomeia o defeito: confessar o que passa e calar o que não passa.

### `departamento-conteudo-marketing` — 8

O que sustenta a banda:

- **dono obrigatório por schema, em dois lugares.** Toda `MARKETING_CAPABILITY_GAP` exige
  `recovery_owner` e `recovery_condition` entre os campos obrigatórios
  (`.../schemas/departamento-conteudo-marketing.schema.json:799`); e cada uma das oito linhas de
  prontidão exige `reason`, `evidence_refs` e `owner` (`.../schemas/...:697`);
- **`NOT_PROVEN` é status próprio** (`.../schemas/...:714`), o que impede que o não provado se
  esconda dentro de `NOT_APPLICABLE`;
- **oito riscos residuais com coluna `Teto`** dizendo o que a mitigação não alcança — mudança de
  política entre consulta e publicação, autodeclaração que não prova a cadeia de proveniência,
  documento de licença falso, fingerprint sobrevivendo à higienização, ação externa fora do runtime
  sem recibo (`references/protocolo-conteudo-marketing.md:155`);
- o placar lista sete `SKIP` com motivo, afirma que `SKIP` não é `PASS`, e o veredito de
  materialização é `APROVADO_COM_RESSALVAS` com as ressalvas nomeadas (`evals/PLACAR.md:51` e `:65`).

Não confessa só o que passa. Os dois riscos:

1. **A camada em que o pacote fala de si é a que não tem dono.** Nem os sete `SKIP` do placar nem as
   oito linhas de risco residual nomeiam dono ou condição de fechamento. Quem fecha `R4`, quem
   executa o forward comportamental — sem resposta.
2. **Verificável não é verificado.** `recovery_condition` e `reason` são strings de `minLength: 3`
   (`.../schemas/...:839` e `:717`): o schema garante a **presença** da condição, nunca que ela seja
   checável.

### `departamento-qa-usabilidade` — 7

Este pacote tem a declaração de limite mais mecanizada que li nele:

- `skipDetail` exige `reason`, `impact`, `owner` e `resume_when` como obrigatórios
  (`.../schemas/departamento-qa-usabilidade.schema.json:441`); `pendingItem` exige `owner`,
  `impact`, `resume_when` e `blocking` (`:327`); o defeito exige `owner` (`:633`). **Nenhum limite
  que surja em operação existe sem dono e sem condição de retomada;**
- a tabela de estados declara, coluna a coluna, o que cada estado **nunca significa** — `PASS` nunca
  significa ausência de defeito, `SKIP` nunca é passe, `UNVERIFIED` nunca é conformidade
  (`references/protocolo-qa-usabilidade.md:73`);
- sete riscos residuais com coluna `Teto` (`references/protocolo-qa-usabilidade.md:390`);
- e uma confissão rara, que é o oposto exato do defeito que o critério caça: o protocolo declara que
  **o envelope genérico do Diretor não possui campos próprios para `UNVERIFIED` e `MISSING`** e, em
  vez de calar, descreve o transporte conservador — contagem em `skip` com motivo rotulado,
  pendências preservadas e referência ao relatório que mantém os estados originais
  (`references/protocolo-qa-usabilidade.md:361`).

O que impede a banda superior é **um defeito observado**, e ele está dentro da própria confissão:

> `evals/PLACAR.md:24` — *"`quick_validate.py` nas 4 skills | **PASS — 4/4 `Skill is valid!`**,
> executado em 2026-07-26. O bloqueio anterior (`ModuleNotFoundError: yaml`) caiu: PyYAML 6.0.3 está
> instalado."*
>
> `evals/PLACAR.md:40-42` — *"Isso não transforma a execução bloqueada de `quick_validate.py` em
> PASS; a limitação ambiental permanece declarada."*
>
> `evals/PLACAR.md:57` — *"`quick_validate.py` com sua dependência PyYAML disponível"* — na lista
> **"O que ainda não foi provado"**.

Um limite cuja condição de fechamento o próprio documento declara cumprida, e que segue listado como
aberto, não é condição de fechamento verificável. A direção do erro é confessar **a mais**, não a
menos — foi por isso que a nota ficou em 7 e não caiu de banda —, mas o efeito é que a seção que diz
o que não fecha deixa de ser confiável como estado.

Some-se o risco: os três limites próprios do placar não nomeiam dono, e `resume_when` e `Teto` são
strings livres.

## O que não consegui avaliar

- **A metade de entrada da fronteira, nos quatro.** `DEPARTMENT_MISSION` não é materializada nem
  validada em nenhum dos validadores que li. Contei como risco nomeado, não como lacuna que rebaixa
  a banda — leitura minha do `C05`, que enumera três perguntas voltadas para dentro e para a saída.
  Leitura mais dura rebaixaria os quatro.
- **Comportamento.** Nenhuma travessia real: toda prova de `C05` é compatibilidade de forma entre um
  fixture do próprio pacote e o schema do consumidor. Não é `n/a` — é o teto do que se pode ler sem
  executar, e o CEO é quem executa nesta rodada.
- **Os agentes um a um.** Amostrei um contrato de agente em `arquitetura-dados` e um em
  `conteudo-marketing`; nos demais confiei no `enum` de `workerId` e nos pares capacidade↔agente
  relatados no placar.
- **O candidato da T27** não está na árvore e não foi julgado, como o contrato manda.

## O que declaro contra mim

1. **A árvore.** O contrato desta recoleta declara a árvore julgada como o commit `4446786`; meu
   worktree, após `git reset --hard master`, está em `ab5882c` — o commit que sela a própria
   recoleta. Julguei `ab5882c` e declarei `ab5882c`. Se a intenção era medir `4446786`, minhas cinco
   notas saíram de uma árvore diferente da contratada. Não troquei de árvore para o número bater.
2. **Não executei nada e me apoiei na saída crua exatamente onde ela me favorece.** Se algum dos
   casos de fronteira que sustentam meus `8` estiver quebrado e contado como `PASS`, o parecer cai
   junto.
3. **Prova de forma, não de comportamento.** Os converters que li — `to_department_return`,
   `derive_department_return` — são fixtures escritos pelo próprio pacote que testam. Estou julgando
   que a cadeia **atravessaria**. O critério me avisa que verde no próprio teste não prova travessia;
   aceitei validação cruzada contra o schema do consumidor como o teto do possível por leitura, e
   essa aceitação é minha, não do contrato.
4. **Ordem de busca enviesada.** Achei o descarte de `delegated_dependencies` no `arquitetura-dados`
   porque abri o converter linha a linha — e fui abrir o converter do pacote que já estava indo para
   nota alta. Apliquei o mesmo escrutínio aos outros dois **depois**, não antes.
5. **Minhas notas caíram durante a análise.** `arquitetura-dados` e `conteudo-marketing` estavam em
   `9` até eu achar o segundo risco em cada um. A fronteira 8/9 aqui depende de quanto eu cavei, não
   de uma regra estável: outra instância que cave menos devolve `9` nos dois, e não teria como ser
   acusada de erro.
6. **A contradição do PyYAML podia valer 6.** Mantive `7` porque a banda 7–8 pede "sem defeito
   observado" e eu observei um — mas argumentei que a direção do defeito é confessar a mais. Um juiz
   que leia ao pé da letra tem base para `6`, e eu não teria como refutar.
7. **Não li todos os agentes.** Se algum agente individual declarar canal lateral com outro
   Departamento, eu não teria visto.
