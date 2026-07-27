# AGENTS.md — Estrutura Final de Skills

## Entrada obrigatória

Para qualquer trabalho nesta árvore, carregue primeiro
`ceo-maestro/SKILL.md`. O CEO Maestro é a entrada operacional da estrutura;
Jeremias permanece como autoridade humana final.

## Hierarquia vigente

- O CEO Maestro conversa diretamente somente com seus três pares executivos:
  `diretor-de-lentes`, `departamento-negocios` e `departamento-evolucao-skills`.
- O Diretor de Lentes orquestra os Departamentos; os Departamentos orquestram
  seus agentes executores.
- O Departamento de Juízes valida ou reprova todas as entregas, mas **não tem
  canal lateral com produtor nenhum**: recebe `JUDGMENT_REQUEST` somente do
  `diretor-de-lentes` e devolve o parecer somente a ele. Entrega de Negócios
  chega ao julgamento pela matriz Negócios↔Diretor; entrega de Departamento
  operacional chega pelo próprio Diretor. Ele ocupa camada **paralela** aos dez
  Departamentos operacionais, não é um deles.
- O `departamento-evolucao-skills` evolui as skills de toda a estrutura,
  inclusive as do Diretor e dos Departamentos abaixo dele — por isso responde ao
  CEO, e não ao Diretor. **Só opera sob missão do CEO**: não tem rotina, ronda
  nem iniciativa própria. A demanda pode nascer no
  `departamento-inovacao-melhoria`, mas o envelope que autoriza é sempre do CEO.
  Ele produz e prova candidatos; **não promove, não pontua e não escolhe
  vencedor** — selecionar é do `departamento-juizes` e promover é do CEO com
  Jeremias.
- O CEO Maestro não chama Departamento operacional nem agente executor
  diretamente.

## Gate executivo

Produto ou proposta final exige relatório vigente do Departamento de Juízes,
menor nota aplicável maior ou igual a 9,5, ausência de falha crítica e de
pendência bloqueante. Não usar média nem arredondamento.

Abaixo de 9,5, o CEO somente pode pedir autorização explícita a Jeremias após
receber relatório verificável de impossibilidade ou limite objetivo. Se
Jeremias autorizar, registrar `VALIDATED_BY_EXCEPTION`, preservar a nota real
e vincular candidato, riscos, relatório e autorização. A exceção nunca elimina
gates inegociáveis.

## Governança

A fonte normativa única desta estrutura é
`regras-de-ouro/REGRAS-DE-OURO.md`. CEO, Diretor, Departamentos e Agentes
referenciam esse arquivo; não copiam regras para dentro das skills.

## Expansão e migração

Para migrar uma lente legada, criar um Departamento novo, acrescentar um agente
ou evoluir o contrato de um pacote existente, seguir
`GUIA-DE-EXPANSAO-E-MIGRACAO.md`: anatomia canônica, tabela de caminhos
relativos por profundidade, passo a passo com critérios de conclusão, o que o
validador precisa provar, checklist de aceite e ordem recomendada das frentes.

O guia organiza a aplicação das regras; não cria regra nova. Em conflito com
este `AGENTS.md`, com `ORGANOGRAMA.md` ou com as Regras de Ouro, vencem estes e
o guia é corrigido.
