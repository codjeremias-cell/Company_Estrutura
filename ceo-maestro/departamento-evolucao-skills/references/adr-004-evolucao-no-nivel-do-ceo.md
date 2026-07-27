# ADR-004 — Evolução de Skills no nível do CEO, e por que "exponencial" é transversal

- **Data:** 2026-07-26
- **Status:** aceito por decisão de Jeremias
- **Decisores:** Jeremias
- **Contexto normativo:** [ADR-001 da hierarquia executiva](../../references/adr-001-hierarquia-executiva.md) ·
  [ADR-002 dos Juízes](../../diretor-de-lentes/departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md) ·
  [ADR-003 da Auditoria](../../diretor-de-lentes/departamentos-operacionais/departamento-auditoria-responsabilidades/references/adr-003-conformidade-sem-nota.md)

## Contexto

Jeremias pediu um Departamento novo, fora da lista do organograma, para **evoluir as próprias
skills**: captar aprendizagem, avaliar cada habilidade, mapear evoluções possíveis, evoluir "de
forma exponencial" e minerar habilidades novas em repositórios públicos e conceitos novos.

Duas evidências moldaram o desenho, e nenhuma delas é opinião.

**1. A evidência de casa.** O `Catalogo-Skills-Unificado/_evolucao-skills/PLANO-EVOLUCAO.md` já roda
um programa de evolução desde 2026-07-13, com tracker por rodada de 53 skills. A trajetória da
média é **8,45 → 8,58 → 9,03 → 9,17 → 9,25 → 9,27 → ≈9,27**. O próprio documento declara
**"REGIME DE TETO"**, com o diagnóstico escrito: *"variância entre avaliadores > ganho por
micro-onda"*, e cerca de 25 skills paradas em **"⏸️ teto honesto (aguarda material externo)"**. A
campanha C1 registra o mesmo padrão em escala: *"2 rodadas, medianas oscilando, cada painel fresco
acha defeitos novos"*, a 131 subagentes e ≈8,17M tokens.

**2. A evidência externa.** A literatura explica por que isso acontece e não é falha de execução:

- **Auto-refinamento iterativo produz reward hacking espontâneo** — a nota do avaliador **sobe
  enquanto a avaliação humana desce**, sem nenhuma atualização de peso, dentro de uma única janela
  ([arXiv:2407.04549](https://arxiv.org/pdf/2407.04549)).
- **Juiz sem referência pontua plausibilidade, não correção**, deixando bacias de falso-positivo
  para o otimizador explorar ([arXiv:2607.05904](https://arxiv.org/html/2607.05904)).
- **Avaliadores LLM preferem as próprias gerações**, com viés que humanos não confirmam
  ([NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/7f1f0218e45f5414c79c0679633e47bc-Paper-Conference.pdf)).
- **Laços evolutivos colapsam diversidade**, explorando o padrão de alta recompensa conhecido e
  perdendo o caminho que hoje parece pior ([arXiv:2606.29719](https://arxiv.org/pdf/2606.29719)).

Juntas: **mais rodadas de leitura sobre o mesmo material não produzem mais qualidade — produzem
mais concordância com o avaliador.** O teto de 9,27 não é falta de esforço; é a assinatura do
método.

## Decisão

**1. O Departamento responde diretamente ao `ceo-maestro`**, como terceiro par executivo ao lado de
`diretor-de-lentes` e `departamento-negocios`. Ele evolve **todas** as skills, inclusive as dos
Departamentos que ficam sob o CTO e a do próprio CTO. Pendurá-lo sob o Diretor o colocaria
evoluindo o próprio superior e os próprios irmãos — a mesma razão pela qual a Auditoria não audita
a si própria. Independência exige o nível acima.

**2. Nunca trabalha por conta própria.** Só opera com `EXECUTIVE_MISSION` do CEO. A demanda pode
**nascer** no `departamento-inovacao-melhoria`, mas o envelope que autoriza o trabalho é sempre o
do CEO: um Departamento sob o CTO não comanda um par executivo. Sem missão, o Departamento lê,
observa e propõe **nada** — nem varredura de rotina, nem mineração espontânea, nem "aproveitei que
estava aqui".

**3. Aprendizagem chega por relatório, não por leitura direta.** As lições vivem na memória dos
projetos e são consolidadas pelo `departamento-registros`. Este Departamento **não** lê memória de
projeto, junction nem transcript bruto: ele **requisita o relatório** e o lê **quando acionado**.
Isso mantém uma fonte única de aprendizagem e impede que dois Departamentos destilem a mesma
memória com resultados diferentes.

**4. "Exponencial" é transversal, não numérico.** A meta declarada **não** é subir a média das
notas — a evidência acima mostra que essa métrica satura e depois mente. A meta é **alcance
composto**: um achado adotado que serve a N skills vale N vezes um retoque que serve a uma. O
próprio ROADMAP da casa já dizia isso — *"evoluir por padrão transversal rende mais que skill a
skill"*. Portanto o Departamento mede, por rodada: **material novo admitido** (gems minerados,
lições convertidas em regra), **alcance** (quantas skills cada mudança toca) e **cobertura de
eval** — e trata nota como sinal secundário, sujeito a inflação.

**5. Fronteira de Pareto em vez de campeão único.** O programa de casa mantinha **uma** versão por
skill, substituída a cada rodada — otimização gulosa, que a literatura mostra colapsar em ótimo
local. Adotamos o mecanismo do **GEPA** ([arXiv:2507.19457](https://arxiv.org/abs/2507.19457),
ICLR 2026 Oral): manter, por skill, o conjunto de candidatos **não dominados** ao longo dos casos
de eval, e **combinar lições complementares** da fronteira em vez de descartar o perdedor. Um
candidato pior na média e melhor em um caso **permanece na fronteira** e é nomeado no relatório.
GEPA reporta superar GRPO em até 20% com **35× menos rollouts**, e superar o MIPROv2 em mais de
10% — o ganho vem de refletir sobre **trajetória** em linguagem natural, não de mais amostras.

**6. Reflexão sobre trajetória, não sobre o texto da skill.** O diagnóstico do gap sai do
**transcript do eval** — acionou, aderiu, onde contornou —, não da leitura crítica do arquivo. Ler
a skill e opinar é exatamente o laço que satura; observar a execução falhar é o que gera material
novo. Casa com o §11.5 do `PADRAO-DE-AUTORIA` (acionamento × aderência) e com o mecanismo do GEPA.

**7. Admissão só com vermelho→verde executado.** Nenhum candidato é recomendado sem o placar
**baseline × pós-skill** rodado: o caso falhava sem a mudança e passa com ela. É a referência que a
literatura aponta como ausente nos juízes que pontuam plausibilidade — e é o §11 do padrão da casa,
que a campanha C1 registrou como **inexistente no catálogo** até 2026-07-19.

**8. Quem seleciona é o `departamento-juizes`, não este Departamento.** Os candidatos vão à
comparação cega em **modo DISPUTA**, encaminhados pelo CEO ao Diretor. Este Departamento **produz e
prova**; nunca escolhe o vencedor da própria produção, nunca pontua e nunca promove. Promoção é
decisão do CEO, e acima dele de Jeremias.

**9. Anti-estagnação e teto honesto continuam valendo.** Duas rodadas sem ganho **verificado por
placar** encerram a frente e escalam ao CEO com "teto honesto" declarado. Forçar mais vira
inchaço — regra já escrita no programa da casa, agora com a explicação de por que ela é necessária.

## Consequências

- **Contrato do CEO muda.** `directExecutive`, o `producer` do cabeçalho causal e o
  `required_capability` do `CAPABILITY_GAP` passam a admitir `departamento-evolucao-skills`, e
  `recipients` da `EXECUTIVE_MISSION` sobe de 2 para 3 destinatários. É alteração aditiva num
  schema já aceito — declarada aqui, como manda a RI-01.
- `AGENTS.md` deixa de dizer que o CEO conversa "somente" com Diretor e Negócios.
- O **modo DISPUTA** do `departamento-juizes`, migrado do legado e até agora sem cliente, ganha seu
  consumidor natural.
- O Departamento nasce **bloqueado na entrada de aprendizagem**: `departamento-registros` ainda não
  existe no caminho canônico, então toda rodada que dependa de colheita abre `CAPABILITY_GAP`.
- A métrica pública do programa deixa de ser "média das notas" e passa a ser alcance + material
  admitido. Comparações com o tracker histórico exigem dizer qual régua está em uso.

## Alternativas consideradas

- **Pendurar sob o `diretor-de-lentes`, como décimo Departamento operacional.** Descartada: ele
  evoluiria o próprio superior e os próprios irmãos, e o Diretor passaria a dirigir quem reescreve
  as capacidades que ele dirige. Mesma razão do ADR-003 para a Auditoria não se auditar.
- **Deixar que o `departamento-inovacao-melhoria` acione diretamente.** Descartada: um Departamento
  sob o CTO comandando um par executivo quebraria a Lei de Ferro. A demanda nasce lá; o envelope
  vem do CEO. Custa um salto e preserva a cadeia inteira.
- **Ler a memória dos projetos direto, sem passar por registros.** Descartada: duplicaria a
  destilação de aprendizagem em dois Departamentos, com risco de conclusões divergentes sobre a
  mesma memória — e violaria a fronte única que o `COMO-COLHER.md` já estabelece.
- **Manter o campeão único e continuar rodando micro-ondas.** Descartada por evidência própria: seis
  rodadas levaram a média de 8,45 a 9,27 e a sétima não moveu. Repetir o método é comprar o mesmo
  teto por mais 8M tokens.
- **Deixar este Departamento pontuar e escolher o vencedor.** Descartada: seria exatamente o
  desenho que a literatura de auto-preferência e reward hacking descreve — o produtor avaliando a
  própria produção, com a nota subindo e a qualidade não.
- **Prometer ganho exponencial em nota.** Descartada por desonestidade: nenhuma evidência sustenta,
  e a evidência disponível contradiz. O exponencial que existe é de **alcance** — e esse é medível.
