# Bootstrap do Departamento de Negócios

## 1. Resolver a raiz

Localize o diretório que contém este `SKILL.md`. Não presuma caminho absoluto, runtime ou ferramenta.

Confirme:

- `CONTRATO-DE-COMPROMISSO.md`;
- `agents/openai.yaml`;
- `references/`;
- `schemas/departamento-negocios.schema.json`;
- exatamente três pastas em `agentes/`, cada uma com skill, contrato e metadata.

## 2. Carregar governança

Leia, nesta ordem:

1. `../../regras-de-ouro/REGRAS-DE-OURO.md`;
2. `CONTRATO-DE-COMPROMISSO.md`;
3. `references/workflow-avaliacao-proposta.md`;
4. `references/protocolo-de-handoff.md`;
5. `references/regua-de-avaliacao.md`;
6. `references/comunicacao-matricial-cto.md`;
7. `references/adr-001-rota-vigente-aos-juizes.md`;
8. [`ADR-014 — dois níveis de veredito`](../../diretor-de-lentes/departamento-juizes/references/adr-014-dois-niveis-de-veredito.md).

Carregue `references/origem-sintese.md` apenas para auditoria de proveniência, nunca para buscar executor.

## 3. Descobrir o time

Enumere somente:

- `agentes/agente-estrategia-de-produto/SKILL.md`;
- `agentes/agente-mercado-e-cliente/SKILL.md`;
- `agentes/agente-viabilidade-e-monetizacao/SKILL.md`.

Para cada um, verifique:

- nome canônico;
- fronteira exclusiva;
- contrato;
- `return_to: departamento-negocios`;
- metadata;
- ausência de sobreposição que permita bypass.

Qualquer pasta extra, agente ausente ou contrato inválido gera `BUSINESS_CAPABILITY_GAP` e `B_BLOCKED`.

## 4. Verificar integrações

Resolva, sem editar:

- `../SKILL.md` e `../schemas/ceo-maestro.schema.json`;
- `../diretor-de-lentes/SKILL.md`;
- `../diretor-de-lentes/schemas/diretor-de-lentes.schema.json`;
- `../diretor-de-lentes/departamento-juizes/SKILL.md`.

Se a rota dos Juízes mudar, reabra o ADR antes de alterar o comportamento.

## 5. Validar a missão

Antes de qualquer delegação, confira:

- produtor `ceo-maestro`;
- `departamento-negocios` entre destinatários;
- `required_level: PRODUCAO|INTERNO` explícito;
- identidade causal completa;
- artefatos e evidências acessíveis;
- critérios observáveis;
- matriz coerente com os destinatários;
- permissões de leitura, escrita e efeitos externos.

Conversa informal ou proposta avulsa não substitui `EXECUTIVE_MISSION`.
Nível ausente falha fechado: bloqueie e peça missão revisada; nunca reduza silenciosamente a
exigência para `INTERNO`.

## 6. Falha fechada

Não use skills canônicas, pastas legadas, agentes de outro Departamento ou conhecimento improvisado como fallback. Informe o recurso ausente, a evidência da ausência, o impacto e a condição de recuperação.
