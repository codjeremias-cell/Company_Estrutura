# Relatórios de aprendizagem — pasta de saída de runtime

Caminho canônico fixado pela **decisão 5** do
[ADR-005](../../../ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-registros/references/adr-005-quatro-agentes-e-relatorios-de-registros.md).
Esta pasta é **saída de runtime**, não fonte de método: nada aqui é lido por carregamento
progressivo de skill nenhuma.

## O que mora aqui

Os **relatórios de aprendizagem** produzidos por rodada — o artefato que transforma lição colhida em
material minerável pelo método. Cada relatório é um arquivo datado, estável por hash, com as lições e
suas fontes que resolvem.

O que **não** mora aqui: memória durável, estado, pendência, documento de produto, guia e ideia. Esses
são registros do **projeto-alvo** e ficam nele, pela separação `method_root` × `target_root` que a
decisão 4 do ADR-005 preserva. Relatório de aprendizagem é artefato **cross-projeto do método** — por
isso está ancorado na raiz da estrutura, e não dentro do pacote do produtor nem do consumidor.

Irmãs futuras (integridade, conservação e outras naturezas de relatório) nascem ao lado, sob
`registros/relatorios/`, sem renomear nada — é a razão de a pasta ser `relatorios/` com
`aprendizagem/` dentro.

## Quem produz

O [`departamento-registros`](../../../ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-registros/SKILL.md),
sob missão do `diretor-de-lentes`, delegando a gravação ao agente dono da capacidade:
[`agente-aprendizados-e-relatorios`](../../../ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-registros/agentes/agente-aprendizados-e-relatorios/SKILL.md),
sempre por `RECORD_TASK` assinada pela gerente. Nenhum outro agente escreve aqui: a natureza
`aprendizagem` (regra `R6`) tem **dona única**.

## Quem consome

O [`departamento-evolucao-skills`](../../../ceo-maestro/departamento-evolucao-skills/SKILL.md), que
minera as lições e as converte em candidatos de skill. A forma do relatório é definida pelo
consumidor — `gap_alvo`, `fonte_url`, `fonte_titulo`, `fonte_versao`, `acessado_em`, `licenca`,
`o_que_e`, `limite_declarado`, `degrau_proposto` de 0 a 4 e `adaptacao`, em
[`mineracao-e-proveniencia.md`](../../../ceo-maestro/departamento-evolucao-skills/references/mineracao-e-proveniencia.md).
O produtor **consome** esse formato; não o redefine.

## Esta pasta NÃO cria canal de leitura direta

A existência do caminho **não** autoriza o consumidor a vir buscar arquivo aqui. A requisição continua
passando pelo **CEO**:

- [ADR-005](../../../ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-registros/references/adr-005-quatro-agentes-e-relatorios-de-registros.md),
  decisão 5, seção *O que esta pasta NÃO é*: a pasta torna o artefato **localizável, datado e estável
  por hash**, satisfazendo RI-04; o **acesso** segue pelo canal hierárquico, e a referência viaja no
  envelope.
- [ADR-004](../../../ceo-maestro/departamento-evolucao-skills/references/adr-004-evolucao-no-nivel-do-ceo.md),
  decisão 3 — *"Aprendizagem chega por relatório, não por leitura direta"*: o Departamento de Evolução
  **não** lê memória de projeto, junction nem transcript bruto; ele **requisita o relatório**. A
  obrigação 6 do
  [contrato dele](../../../ceo-maestro/departamento-evolucao-skills/CONTRATO-DE-COMPROMISSO.md) diz o
  destinatário com todas as letras: requisitar ao `departamento-registros` **através do CEO**, e abrir
  lacuna quando não vier.

Departamento que vai buscar arquivo na pasta de outro, sem missão, é **bypass**. O ganho de pular o
salto é nenhum: a referência do artefato já viaja no envelope de retorno.

## Estado

Pasta **vazia de artefatos** em 2026-07-26: o caminho é **contrato**, e nenhuma rodada gravou
relatório ainda. Este `README.md` declara o contrato; ele não é relatório e não conta como um.

**Governada por:** [regras-de-ouro/REGRAS-DE-OURO.md](../../../regras-de-ouro/REGRAS-DE-OURO.md),
fonte normativa única · posição em [ORGANOGRAMA.md](../../../ORGANOGRAMA.md).
