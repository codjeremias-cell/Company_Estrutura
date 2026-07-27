# Origem e recorte da migração

## Fonte legada

- origem lógica: `SKILL - Nova formula/maestro/comite-de-lentes`;
- `SKILL.md`:
  `sha256:bb2bb34a7fdb2d23c188246a79bfb35b407ffd50f2d0ea1a07d753bbc8c83c38`;
- `agents/openai.yaml`:
  `sha256:37cd78481177a38f74bc1d2824462235337814eb119a007a41e039057dd4a072`;
- `evals/evals.json`:
  `sha256:318f2ed95f7a16c0ee0a32ce90d87c41d570cf3bcd3e7e11a8c4b78bf8be601a`;
- `evals/placar.md`:
  `sha256:0241381b2d455cf63984e917d1ade4923c3fd277ecf3bbf3a8eac3f11f2d5654`.

Snapshot observado no início da seleção, em 2026-07-26: 729 arquivos e 37.413.184 bytes.
Essa contagem é contexto de escala, não identidade: os filhos legados podem evoluir em
paralelo. A proveniência do núcleo é fixada pelos quatro hashes acima.

## Recorte preservado

- direção entre CEO e gerentes;
- reconciliação de intenção, escopo, `DONE`, evidência e decisões;
- classificação integral das áreas;
- contratos de missão, dependências, handoffs e estados;
- bloqueio diante de capacidade ou evidência ausente;
- preservação de pareceres, dissensos e autoridade de domínio;
- retorno executivo estruturado.

## Recorte não copiado

As pastas `lente-*` e `orquestrador-*` não foram copiadas porque são os futuros
Departamentos, com nomes e contratos ainda legados. Seus candidatos, fixtures, imagens,
placares e relatórios de eval permanecem na fonte como evidência histórica.

*Atualização de 2026-07-26:* já foram materializados, com proveniência própria,
`departamento-juizes`, `departamento-arquitetura-software`,
`departamento-design-ux-ui`, `departamento-qa-usabilidade`,
`departamento-auditoria-responsabilidades`, `departamento-registros`,
`departamento-desenvolvimento` (origem `lente-dev-senior`) e
`departamento-seguranca` (origem `lente-especialista-seguranca`). No mesmo dia,
por frente paralela, `departamento-inovacao-melhoria` (origem
`orquestrador-inovacao-melhoria`) também passou a existir no caminho canônico e
**fechou a cascata do passo 10 na rodada 3**: 122/122 no pacote, **1531/1531 na
cadeia**, 45/45 mutações adversariais rejeitadas e legado intacto em 22/22 e
101.022 bytes. Com ele, **nenhuma** origem `lente-*` ou `orquestrador-*` deste
recorte continua apenas legada, e os onze Departamentos operacionais sob este
Diretor têm pasta, contrato, schema e validador próprios.

A pendência que sobra ali é comportamental, não estrutural: o acionamento
espontâneo em runtime está declarado `SKIP` no placar daquele pacote, porque as
instâncias do forward receberam a skill por carga explícita de caminho.

O `evals/placar.md` legado não foi promovido: ele registra um hash diferente do
`SKILL.md` atual da fonte. Os cenários foram reescritos para a nova hierarquia e executados
novamente.

## Mudanças contratuais

- `comite-de-lentes` → `diretor-de-lentes`;
- `maestro` → superior `ceo-maestro`;
- Negócios passa a par matricial;
- dez Departamentos operacionais substituem as lentes nomeadas;
- Juízes deixam de ser opcionais e passam a avaliar toda entrega;
- Auditoria fornece prova; Juízes emite veredito;
- o corte operacional passa a ser a menor nota aplicável `>= 9,5`;
- somente o CEO pede a Jeremias uma exceção verificável.

## Política de rollback

O pacote legado permanece intacto. Ele é fonte histórica e rollback manual; nunca fallback
automático em runtime.
