# ADR-013 — Inovação sem autojulgamento e com três agentes

- **Status:** aceito para esta migração
- **Data:** 2026-07-26
- **Autoridade:** organograma vigente e solicitação de Jeremias

## Contexto

O legado `orquestrador-inovacao-melhoria` era candidato não vinculado, descobria
capacidades dinamicamente e combinava `GERENCIAR | JULGAR`, rubrica absoluta e
corte 9,5. Não possuía agentes, schema nem validador executável.

A nova empresa já possui `departamento-juizes`, usa o Diretor como única
fronteira dos Departamentos operacionais e fixa três agentes de Inovação no
organograma. Também criou `departamento-evolucao-skills` no nível do CEO:
Inovação melhora produto/processo; Evolução modifica skills.

## Decisão

1. Criar `departamento-inovacao-melhoria` como gerente sob o Diretor.
2. Retirar integralmente o modo `JULGAR`, rubrica, nota, corte e veredito.
3. Criar exatamente:
   - `agente-descoberta-de-oportunidades`;
   - `agente-experimentos-e-spikes`;
   - `agente-melhoria-continua`.
4. Manter integração, gate e priorização do portfólio na gerente.
5. Fazer Experimentos **desenhar**, não executar, código/PoC/benchmark/teste;
   execução é dependência roteada pelo Diretor.
6. Permitir que uma demanda de evolução de skill nasça aqui, mas exigir a rota
   Inovação → Diretor → CEO → `EXECUTIVE_MISSION` → Evolução. A Evolução de
   Skills **não** é destinatário admissível de `execution_request`.
7. Preservar o legado intacto como rollback histórico, nunca fallback.
8. **Cortar Descoberta × Melhoria Contínua pelo enquadramento, não pelo
   vocabulário.** Toil, dívida, retrabalho, tarefa emperrada e marcador
   `ponytail:` não pertencem a uma capacidade pela palavra que os nomeia:
   - **sem job, sem dor localizada ou sem baseline** → Descoberta enquadra;
   - **já enquadrado**, ou **ciclo com evidência operacional autenticada** →
     Melhoria Contínua trabalha, declarando `intake_basis`.

   *Motivo:* a primeira auditoria adversarial encontrou as duas capacidades
   reivindicando o mesmo item de dívida. Fronteira que depende de sinônimo não
   é fronteira; o enquadramento é verificável no artefato, o vocabulário não.

## Prova de suficiência

| Domínio | Dona |
|---|---|
| dor, JTBD, baseline inicial, dedupe, RO-15 e **enquadramento de item novo** — inclusive toil/dívida/`ponytail:` ainda sem job ou baseline | Descoberta |
| alternativas, tecnologia, hipótese, PoC/spike e regra de decisão | Experimentos |
| DORA, Kaizen, PDCA, `Check`, aprendizado e **ciclo de item já enquadrado ou já em evidência operacional** | Melhoria Contínua |
| gate derivado, prioridade, proveniência, contexto confiável e portfólio | gerente |

Não há responsabilidade órfã dentro do domínio, e nenhuma responsabilidade tem
duas donas. Implementação, prova, negócio, arquitetura, segurança,
conformidade e julgamento já possuem donos fora dele.

## Consequências

- A gerente não pode compensar capacidade ausente.
- Os três agentes possuem fronteiras verificáveis e exclusivas.
- Tecnologia permanece dentro de Experimentos; não nasce um quarto agente
  sobreposto.
- Juízes preservam independência.
- Evolução de Skills não pode ser comandada por subordinado do Diretor.
- Expansão futura exige gap recorrente, novo ADR e organograma atualizado.

## Alternativas descartadas

### Copiar e renomear o legado

Descartada: manteria rota antiga, candidatura, modo duplo e autojulgamento.

### Manter `JULGAR` como segunda opinião

Descartada: duplicaria Juízes e permitiria ao domínio pontuar sua linhagem.

### Criar agente de tecnologia

Descartada: tecnologia é variação do dossiê experimental e fecha com PoC.

### Criar agente de baseline

Descartada: baseline faz parte do enquadramento; separar quebraria a unidade da
Descoberta.

### Criar agente de portfólio

Descartada: integração e prioridade são responsabilidade indelegável da
gerente.

### Permitir execução de spike pelo agente

Descartada: mistura desenho com produção de evidência e duplica
Desenvolvimento/QA. O agente pode reconciliar prova externa, não produzi-la.

## Critério de revisão

Revisar somente quando missão real ou eval revelar capacidade órfã recorrente,
volume que comprometa qualidade ou conflito de independência impossível de
resolver com a divisão atual.

## Concluído quando

Contrato, schema, três agentes e validação mecânica impedem gerente/agentes de
pontuar, executar por bypass ou chamar Evolução diretamente, e o
`DEPARTMENT_RETURN` é aceito pelo Diretor.

**Verificado em 2026-07-26, rodada 3:** validador local 122/122 PASS, corpus
adversarial 45/45 rejeitadas com 0 escapes, cadeia canônica 1531/1531 PASS e
legado intacto em 22/22 e 101.022 bytes. A rodada 2 fechara com 59/59 PASS e 39
escapes em 45 mutações — prova de que "validação mecânica" só vale enquanto o
que ela mede for semântica, não forma.
