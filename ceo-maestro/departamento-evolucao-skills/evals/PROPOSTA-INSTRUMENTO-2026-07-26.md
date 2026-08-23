# Proposta de instrumento — trio de fundação Java

**Data:** 2026-07-26
**Origem:** achados 1 e 2 do [PILOTO-2026-07-26.md](PILOTO-2026-07-26.md)
**Natureza:** **proposta**, não edição. Nada aqui foi gravado no catálogo — o departamento não
edita skill viva, e casos de eval moram na pasta da skill. Promover é decisão do CEO com Jeremias.

## 1. O problema a resolver

O piloto mediu: a fronteira de Pareto não tem poder de separação nestes alvos.

| Skill | Casos que separam hoje | Meta |
|---|---:|---:|
| `java-service-usecase` | 2 | 4 |
| `java-db-foundation` | **1** | 4 |
| `java-logging-log4j2` | 2 | 4 |

**Meta 4, não 3.** O mínimo aritmético para dois candidatos não dominados é 2; para três, 3. Com 4
há folga para a fronteira sustentar 2–3 candidatos sem que um empate acidental a colapse.

## 2. A regra de projeto, extraída da própria evidência

Os três casos não discriminantes da amostra falham pelo **mesmo motivo**, e os autores o
declararam: *"o próprio prompt já entrega o padrão a seguir"*. O baseline acerta porque a resposta
está na pergunta.

> **Um caso só separa quando obriga o modelo a IR BUSCAR o padrão real.** Prompt que entrega a
> convenção mede leitura, não comportamento. Caso que o baseline já passa é **controle** — vale ter,
> mas não conta como medida.

## 3. Os eixos, e o que já está coberto

| Eixo | O que exercita | service | db | logging |
|---|---|:-:|:-:|:-:|
| **A** — espelhar o projeto real (SIGO) | reflexo genérico × padrão da casa | ✅ | ✅ | ✅ |
| **B** — espelhar **outra casa** sem impor SIGO | importar gabarito onde não cabe | ✅ | ⚠️ entrega no prompt | ⚠️ entrega no prompt |
| **C** — greenfield sem projeto-irmão | declarar `SUPOSIÇÃO:` e escolher o simples | ❌ | 🔴 falha nos dois | ✅ |
| **D** — código **já conforme** | reescrever à toa × reportar "nada a mudar" (RO-02) | ❌ | ❌ | ⚠️ embutido no A |
| **E** — acionamento orgânico | a skill dispara sem ser nomeada | ❌ | ❌ | ❌ |

**Eixos distintos são o que permite candidatos divergirem.** Um candidato que ataca a description
move o eixo E; um que ataca o corpo move C e D. É essa divergência que dá conteúdo à fronteira.

## 4. Casos propostos

Cada caso declara a **hipótese de falha do baseline**. Nenhum é "discriminante" até o baseline
rodar — a classificação abaixo é projeto, não resultado.

### `java-service-usecase` (+2 → 4)

**S4 · eixo C · greenfield**
> Estou começando um sistema de reservas do zero, em Java puro, sem nenhum projeto parecido na
> empresa. Preciso do serviço que confirma uma reserva. Como você monta?

- *Hipótese de falha do baseline:* apresenta um desenho como decisão fechada, sem rotular
  `SUPOSIÇÃO:` as escolhas arbitrárias (pacote, forma de sinalizar falha, PT-BR × EN).
- *Assertions:* (1) abre com `SUPOSIÇÃO:` explícita sobre as escolhas sem padrão a espelhar;
  (2) **não** importa o padrão SIGO (campo direto, `br.com.cot`, PT-BR) como se fosse regra;
  (3) escolhe o desenho mais simples que atende, e diz por quê.
- *Por que separa:* é o ramo em que o `db-foundation` já falhou. Candidatos que enfraquecem a
  gravidade do gabarito passam; os que só melhoram a prosa, não.

**S5 · eixo D · código já conforme**
> Dá uma melhorada nesse serviço aqui. *(anexar `AutenticacaoService.java` do SIGO, já no padrão)*

- *Hipótese de falha do baseline:* "melhorar" dispara reescrita — injeta por construtor, extrai
  interface, adiciona logger e try/catch.
- *Assertions:* (1) reconhece que o serviço já está no padrão da casa; (2) reporta **"nada a
  mudar"** em vez de reescrever (RO-02); (3) se sugerir algo, marca como opcional e fora do padrão
  vigente.
- *Por que separa:* mede o freio, não o impulso. Nenhum caso atual mede isso no service.

### `java-db-foundation` (+2 discriminantes → 3, +1 regressão)

**D4 · eixo D · fundação já conforme**
> Revisa a camada de banco desse projeto e melhora o que der. *(anexar o `Database.java` do SIGO,
> com retry e trava de 2 níveis)*

- *Hipótese de falha do baseline:* propõe pool de conexões, `DataSource`, refactor para
  `ConnectionFactory` — "melhorias" que quebram a trava de 2 níveis que o UCanAccess exige.
- *Assertions:* (1) identifica a serialização em 2 níveis como **invariante**, não legado;
  (2) não propõe pool sobre conexão única; (3) reporta o que já está conforme antes de sugerir.

**D5 · eixo B · outra casa, sem entregar o padrão**
> Monta a fundação de banco de um projeto web com Postgres. É um sistema novo do time de vendas.

- *Hipótese de falha do baseline:* importa o mecanismo SIGO (retry manual, `FileLock`) num contexto
  com pool, **ou** inventa um genérico sem declarar a divergência.
- *Assertions:* (1) **não** aplica trava de 2 níveis onde há pool; (2) declara explicitamente que o
  padrão SIGO não se aplica e por quê (RI-01); (3) segredo por variável de ambiente, sem
  `config.properties` do SIGO.
- *Diferença para o caso 2 atual:* o prompt **não** informa o padrão. É a mesma pergunta com a
  resposta retirada.

**D6 · eixo C · greenfield — reformulação do caso 3 atual (regressão pendente)**
> Sistema de estoque novo, Java desktop, sem projeto de referência. Preciso da camada de acesso a
> dados. Só isso, sem firula.

- *Estado atual:* o caso 3 vigente é **vermelho nos dois lados** — não separa. O placar registra a
  causa: *"o gabarito SIGO tem gravidade forte demais no prompt"*, e a execução pós-skill inverteu o
  próprio mandato da skill citando governança para parecer conforme.
- *Assertions:* (1) `SUPOSIÇÃO:` declarada; (2) **não** importa `ReentrantLock`+`FileLock`;
  (3) a justificativa não invoca RI-01/RO-01 para adotar o gabarito.
- *Classificação:* **caso de regressão pendente**, não discriminante. Ele é o vermelho do TDD
  esperando o verde: só vira medida **depois** que a skill for corrigida. Contá-lo como
  discriminante hoje seria inflar o instrumento.

### `java-logging-log4j2` (+2 → 4)

**L4 · eixo D · já conforme, isolado**
> Revisa o tratamento de erro dessa classe. *(anexar `ColaboradorFormController.java` do SIGO, já
> usando `Log.erro(msg, e)`)*

- *Hipótese de falha do baseline:* troca a fachada por `LoggerFactory.getLogger(Classe.class)` e
  introduz placeholder `{}` que a fachada não tem.
- *Assertions:* (1) reconhece a fachada `Log` como padrão da casa; (2) mantém o logger nomeado
  `"COT"`; (3) reporta "nada a mudar".
- *Diferença para o caso 1 atual:* lá o "já conforme" está embutido num pedido de correção; aqui é
  o objeto do caso, medido sozinho.

**L5 · eixo B · outra casa, sem entregar o padrão**
> Preciso padronizar o log num projeto Spring Boot que já está rodando. Como faço?

- *Hipótese de falha do baseline:* impõe a fachada `Log` do SIGO, **ou** propõe padrão genérico sem
  antes ler o que o projeto já pratica.
- *Assertions:* (1) manda **inspecionar** o padrão vigente antes de propor; (2) não impõe a fachada
  SIGO; (3) `Throwable` como último argumento, sem concatenar dado sensível.

## 5. Mudança de protocolo — eixo E, acionamento

O eixo E **não é um caso novo**: é como o pós-skill roda. Os três placares registram que ele rodou
por *"carga forçada da skill (não disparo orgânico)"*, o que torna o sinal `acionou` indisponível.

**Requisito:** a execução pós-skill roda com a skill **disponível mas não nomeada**, e o transcript
registra se ela foi invocada. Sem isso, `acionou` fica `—` e o diagnóstico de description continua
sendo inferência.

Isso vale para **todos** os casos, novos e antigos, e é a mudança de maior alcance desta proposta:
atinge qualquer skill do catálogo que use este formato.

## 6. Estado projetado

| Skill | Hoje | Com a proposta | Fronteira |
|---|---:|---:|---|
| `java-service-usecase` | 2 | **4** | sustenta 2–3 candidatos |
| `java-db-foundation` | 1 | **3** + 1 regressão pendente | sustenta 2 |
| `java-logging-log4j2` | 2 | **4** | sustenta 2–3 |

## 7. O que esta proposta **não** prova

- **Nenhum caso foi executado.** "Discriminante" é hipótese de projeto até o baseline rodar. Um caso
  que o baseline já passe vira controle, e a contagem cai.
- **Os anexos precisam existir.** S5, D4 e L4 dependem de arquivo real do SIGO chegar ao prompt; sem
  o anexo, o caso não é o mesmo caso.
- **Não mede a hipótese central.** Isto conserta o instrumento; se fronteira + material destrava o
  teto de 9,27 só se sabe depois, com a Fase 2.
- **R6** — nada aqui saiu de uma `EVOLUTION_TASK`: é proposta escrita fora de rodada do
  Departamento, e está declarada como tal.
