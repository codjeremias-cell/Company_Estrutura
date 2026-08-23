# AGENTS.md — Estrutura Final de Skills

## Entrada obrigatória

Para qualquer trabalho nesta árvore, carregue primeiro
`ceo-maestro/SKILL.md`. O CEO Maestro é a entrada operacional da estrutura;
Jeremias permanece como autoridade humana final.

A porta continua sendo **uma só**. `especialista-planejador/`, no topo desta
árvore, não é uma segunda porta da cadeia: é consultor direto de Jeremias, fora
dela — ver *Fora da cadeia de comando*.

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

## Fora da cadeia de comando

Existe **uma** skill no topo desta árvore que não é nó da cadeia:
`especialista-planejador/`, irmã de `ceo-maestro/`, instalada em 2026-08-08.

- É **consultor direto de Jeremias**. Canal único, nos dois sentidos:
  `Jeremias → especialista → Jeremias → ceo-maestro`. O último passo é decisão
  de Jeremias, não repasse do especialista.
- **Não tem superior e não tem subordinado.** Não responde ao CEO, ao Diretor
  nem a Departamento nenhum, e não tem `agentes/`.
- **Não emite nem recebe `EXECUTIVE_MISSION`**, `DEPARTMENT_MISSION` ou
  `JUDGMENT_REQUEST`. Não tem `return_to` e não fala com departamentos.
- **Não é um quarto par executivo.** Os pares executivos do CEO continuam sendo
  três, e só três — `diretor-de-lentes`, `departamento-negocios` e
  `departamento-evolucao-skills`. Nem `ceo-maestro/SKILL.md`, nem o contrato do
  CEO, nem a `description`, nem a matriz de rota foram alterados por causa dele.
- A única linha que a instalação acrescentou dentro de `ceo-maestro/` está em
  `evals/coletar_saida_crua.py`: uma chave em `SUBORDINADOS_ESPERADOS`
  declarando **zero subordinados**. É tabela de inventário de `evals/`, não
  cadeia de comando, e entrou com autorização explícita de Jeremias.
- Anatomia reduzida de propósito, e **verificada**: sem `agentes/`, sem
  `schemas/`, sem `references/`. O validador do próprio pacote reprova se
  qualquer uma das três aparecer, porque seria a primeira assinatura de um nó de
  cadeia. Mecânica: 14/14 PASS.
- A fonte normativa é a mesma de todos: `regras-de-ouro/REGRAS-DE-OURO.md`.

Detalhes, diagrama e a exceção ao *Contrato estrutural obrigatório* estão em
`ORGANOGRAMA.md`, seção *Fora da cadeia de comando*.

## Gate executivo

Produto ou proposta final exige relatório vigente do Departamento de Juízes,
ausência de falha crítica e de pendência bloqueante, e veredito derivado da
menor nota aplicável: `10 → VALIDATED`, `7–9 → ACEITO_USO_INTERNO`,
`0–6 → REPROVED`. Não usar média, nota fracionária, arredondamento nem
compensação entre critérios.

Toda `EXECUTIVE_MISSION` declara `required_level`: `PRODUCAO` exige
`VALIDATED`; `INTERNO` aceita `VALIDATED` ou `ACEITO_USO_INTERNO`. O nível é
propagado pelo Diretor no `JUDGMENT_REQUEST` e conferido no fechamento.
Missão sem nível falha fechada como `PRODUCAO`.

Veredito abaixo do nível exigido volta para retrabalho. O CEO somente pode
pedir autorização explícita a Jeremias após receber relatório verificável de
impossibilidade ou limite objetivo para o mesmo nível. Se Jeremias autorizar,
registrar `VALIDATED_BY_EXCEPTION`, preservar a nota real e vincular
candidato, riscos, relatório e autorização. A exceção nunca elimina gates
inegociáveis. `ACEITO_USO_INTERNO` não autoriza produção, publicação nem
exposição a terceiro.

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
