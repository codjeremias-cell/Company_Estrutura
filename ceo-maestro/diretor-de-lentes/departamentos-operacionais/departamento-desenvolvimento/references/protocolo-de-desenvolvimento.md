# Protocolo do Departamento de Desenvolvimento

Fonte normativa única: [`REGRAS-DE-OURO.md`](../../../../../regras-de-ouro/REGRAS-DE-OURO.md).

## Envelopes

| Envelope | De → Para | Papel |
|---|---|---|
| `DEPARTMENT_MISSION` | Diretor → gerente | a demanda, com as decisões upstream anexadas |
| `DEV_PLAN` | gerente (interno) | track detectado, pacotes coerentes, ondas, agentes |
| `DEV_TASK` | gerente → agente | um pacote, um agente, com `forbidden_context` |
| `DEV_RETURN` | agente → gerente | o que produziu, com evidência e marcadores |
| `DEV_LEDGER` | gerente (interno) | consolidação, gate de bordas e evidência fresca |
| `DEV_CAPABILITY_GAP` | gerente → Diretor | track sem agente, dependência nova, conflito com decisão aceita |

O `DEPARTMENT_RETURN` entregue ao Diretor pertence ao schema do `diretor-de-lentes`. **Aqui o
`test_summary` carrega números reais** — é o único Departamento assim (ADR-012, decisão 1).

## Ondas

**Onda 0 — admissão.** A gerente confere escopo ([fronteiras](fronteiras-do-departamento.md)),
detecta o **track** ([tracks](tracks-e-geradores.md)) e confere se as decisões upstream chegaram:
contratos da Arquitetura, grão e plano de migração de Dados, tokens e estados de Design. Faltando
decisão que trave o pacote, sai `DEV_CAPABILITY_GAP` — implementar sem a decisão é inventá-la.

Track sem agente → `DEV_CAPABILITY_GAP`, sem improviso.

**Onda 1 — decomposição.** Pacotes por **mudança coerente**: arquivos, aceite, prova e parada.
Exatamente **um agente líder por pacote**. Escrita sobreposta é unida ou serializada — nunca
paralela.

**Onda 2 — implementação.** O agente de track (ou o de persistência) produz. Regra dura: **existe
gerador? ele conduz e o agente revisa**; não existe? implementa direto e declara. Cada trecho novo
declara o degrau da escada onde parou.

**Onda 3 — verificação independente.** Sobre a saída da onda 2, e **por quem não a produziu**:

- `agente-revisao-e-refatoracao` revisa Clean Code, complexidade, Chesterton, e colhe os `ponytail:`;
- `agente-testes-e-depuracao` escreve o que faltar de teste, **executa a bateria** e reporta
  `PASS/FAIL/SKIP` com evidência fresca.

É a separação do ADR-012, decisão 5.

**Onda 4 — consolidação.** A gerente monta o `DEV_LEDGER`, apura o gate de bordas, confere que a
evidência é do candidato entregue, reúne dependências e emite o retorno.

## Gates locais

| # | Gate | Falha |
|---|---|---|
| G1 | missão pertence a este Departamento — `$defs/departmentMissionAdmission` | devolve `BLOCKED_BYPASS_ATTEMPT` se o const do Diretor não casa |
| G2 | track tem agente declarado | `DEV_CAPABILITY_GAP` |
| G3 | decisões upstream presentes para o pacote | `DEV_CAPABILITY_GAP` |
| G4 | um agente líder por pacote, sem escrita sobreposta | plano rejeitado |
| G5 | gerador declarado, ou `n/a` **com motivo** | retorno rejeitado |
| G6 | **piso de bordas** — vazio, limite e erro cobertos | entrega `INCOMPLETA` |
| G7 | evidência **fresca**, contra o candidato entregue | entrega `INCOMPLETA` |
| G8 | quem implementou não revisou nem declarou o `PASS` | plano rejeitado |
| G9 | nenhum inegociável marcado como simplificado | retorno rejeitado |
| G10 | `fix_attempts < 3` — Regra dos Três | escala ao Diretor |

G6 e G7 são o gate de saída. Não admitem compensação: cem testes verdes não substituem a borda de
erro ausente.

## Riscos residuais declarados

- **R1 — verde não é correto.** A bateria prova que o que foi testado passa, não que o requisito foi
  atendido. Quem julga o mérito são os Juízes; quem caça o defeito de uso é o QA.
- **R2 — cobertura de borda é declarada, não medida.** O schema exige os três estados por unidade de
  mudança; não recomputa se o teste realmente exercita a borda que diz exercitar.
- **R3 — `generator_used` é autodeclarado.** Nada aqui prova que o gerador foi de fato invocado.
- **R4 — frescor depende de digest.** A evidência se liga ao candidato pelo digest declarado; digest
  errado passa despercebido.
- **R5 — a escada é julgamento.** "Parou no degrau certo" não é verificável mecanicamente; o que o
  schema garante é que o degrau foi **declarado** e que os cinco inegociáveis não foram marcados
  como simplificados.
- **R6 — existência das ondas.** Um `DEV_LEDGER` coerente é reproduzível sem nenhuma `DEV_TASK`
  emitida. Exigir registro de emissão encarece; não impede.
- **R7 — os tracks são cinco porque o acervo tem cinco.** Stack fora deles falha fechada, o que é
  correto, mas significa que a cobertura do Departamento é a cobertura do catálogo — não a do
  mercado.
