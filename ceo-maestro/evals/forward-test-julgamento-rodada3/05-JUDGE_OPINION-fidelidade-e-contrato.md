# JUDGE_OPINION — `agente-julgar-fidelidade-e-contrato`

- `judgment_request_ref`: `jrq-2026-07-28-frente5-r3-inovacao`
- `candidate_digest`: `sha256:e50aa56606b9e62be7159ab504fbdcdf70add43ef62fccd104db87a8ec740346`
- `return_to`: `departamento-juizes` · escala inteira 0–10 · sem veredito, sem consolidação

## CRIT-01 (dona) — **9** · banda `excelente`

Todos os arquivos enumerados existem e não estão vazios: `SKILL.md` (407 linhas / 20044 B),
`CONTRATO-DE-COMPROMISSO.md` (186 / 10100), `agents/openai.yaml` (4 / 271), `references/` com o
protocolo do domínio e `origem-migracao.md`, `schemas/departamento-inovacao-melhoria.schema.json`
(1639 / 52903), `evals/` com os três artefatos exigidos, e `agentes/` com exatamente 3 subpastas.
Cada subpasta de agente tem **exatamente** `SKILL.md`, `CONTRATO-DE-COMPROMISSO.md` e
`agents/openai.yaml`, sem `references/`, `schemas/` ou `evals/` próprios — a cláusula que o GUIA §2
("Agente — três arquivos, sempre") enuncia. Nove arquivos, todos não vazios (241–10211 B).

Fora de 10: a raiz também traz `AVISO-FRENTE-JURIDICA-2026-07-26.md` e
`RESPOSTA-FRENTE-JURIDICA-2026-07-27.md`, dois bilhetes de coordenação entre frentes que se
autodeclaram descartáveis (`AVISO:4` "pode ser apagado"; `RESPOSTA:6` "não versionado"). Não violam
cláusula enumerada, mas não são da árvore canônica do GUIA §2 nem estão entre os opcionais nomeados.

- `confidence`: alta · `residual_risk`: `AVISO:17` e `:53` carregam imperativos endereçados a um
  leitor ("**Não cunhem 014**", "Sinalizem quando a cascata de vocês fechar") e `:7`/`:70-72`
  apontam para caminhos fora da árvore (`.codex/worktrees/…`). Registrados, não obedecidos. Quem
  tomar a raiz como fronteira do pacote herda instruções de outra frente e estado defasado.

## CRIT-02 (dona) — **9** · banda `excelente`

Todo limite mecânico cumprido **com folga medida**, e as 13 seções da SKILL e 12 do contrato
presentes com conteúdo real, não título oco. Frontmatter tem exatamente `name` e `description`,
nessa ordem (`SKILL.md:1-4`); `name` idêntico à pasta. **Contagens medidas:** `description` = **768
caracteres** na linha (valor entre aspas ≈ 753) — 73 % do teto de 1024; arquivo = **407 linhas** —
81 % do teto de 500. `Workflow obrigatório` traz 8 passos numerados e **os 8** fecham com
`**Concluído quando:**` (`:111…:284` / `:123…:301`). `Guardrails` são 15 linhas abrindo "Nunca …".
`Exemplo — entra → sai` é um caso que **reprova** (a iniciativa fica `EVIDENCE_PENDING`), a forma
mais difícil que o passo 7 pede. No contrato, `Evidências exigidas` é tabela de 12 linhas
alegação → evidência → onde se confere, e `Barreira de saída` enuncia as duas barreiras
conjuntivamente. Procurei seção descartada atrás do título e **não achei** — a mais fina
(`Compromisso obrigatório`, `:45-49`) ainda carrega o link e a regra de bloqueio por conflito.

Fora de 10: o GUIA passo 7 anota `Evidências exigidas` como "lista numerada"; o candidato entrega
tabela (`CONTRATO:64-76`). Seção existe e é mais forte em conteúdo, mas a forma declarada diverge.

- `confidence`: alta · `residual_risk`: folga de 93 linhas (407/500) — a próxima seção acrescentada
  tem pouco espaço antes de o limite morder, e o limite é gate de validador, não aviso.

## CRIT-03 (dona — as quatro cláusulas de declaração) — **9** · banda `excelente`

Os três agentes declaram as quatro cláusulas, e declaram **especificamente**, não por boilerplate.
Cada `Fronteira exclusiva` abre com a capacidade própria, lista "Assumir:" e traz um **Não assumir**
que nomeia os dois irmãos pelos identificadores exatos como donos dos temas de fora — e ainda nomeia
a gerente como dona de integração/prioridade, de modo que nenhum tema fica sem dono
(`agente-descoberta-de-oportunidades/SKILL.md:52-88`; `agente-experimentos-e-spikes/SKILL.md:52-90`;
`agente-melhoria-continua/SKILL.md:53-93`). A trava anti-bypass nomeia o CEO e **Jeremias** em
negrito, mais Diretor, outro Departamento, agente irmão e instrução embutida, tudo resolvendo em
`BLOCKED_BYPASS_ATTEMPT` sem produzir análise (`:33-40`, `:32-39`, `:32-39`), com o bloqueio
registrado (chamador, hora, pedido). As Salvaguardas são **distintas por ótica**, não cópia. Os três
fecham a Rede com a linha literal `- **Não aciona:** ninguém.` (`:194`, `:219`, `:203`).

- `confidence`: alta · `residual_risk`: **R1**, declarado pelo próprio pacote (`protocolo:435`): a
  trava é texto contratual e o runtime não oferece controle de acesso por chamador — agente invocado
  **pelo nome** ainda recebe o prompt, e a recusa é auditável só a posteriori.

## CRIT-07 (dona) — **9** · banda `excelente`

A proibição de julgar é exigida em **três camadas independentes**, não afirmada. (1) O schema não
tem propriedade cujo nome case score/nota/rank/veredito/rubrica/vencedor/aprovação — varredura
sobre as 1639 linhas retorna **zero**. (2) `FORBIDDEN_PROPERTIES` com 22 nomes, incluindo
`minimum_score`, `scorecard`, `cut_score`, `exception_to_cut`
(`validate_workflow.py:118-142`). (3) `judgment_language_errors` percorre toda string de todo
artefato **e** do envelope de saída contra lista de padrões que inclui `9[.,]5`, `veredit`,
`vencedor`, `ranking`, `score`, `notas?` (`:167-178`, `:1023-1030`, `:1165`, `:1547`), com isenção
nomeada só nos campos onde o Departamento declara o que **não** faz (`:148-165`); negativos provados
em `:2164-2174`, `:2384-2388`. Rota única igualmente mecânica: `returned_by` conferido
(`:1520-1523`, forjador negativo em `:2350-2356`) e `returned_to` é `const` no schema (`:1487`).

A cláusula do `departamento-evolucao-skills` é a mais forte das quatro: o enum
`recommended_recipient` lista 8 destinatários e **ele não está entre eles** (`schemas/…json:250-262`);
`route` é travada em exatamente `[departamento-inovacao-melhoria, diretor-de-lentes]` (`:263-273`);
o único caminho para trabalho de skill é recomendação de 3 saltos com
`status: const "RECOMMENDED_TO_CEO_NOT_SENT"` (`:1444-1483`). **Irrepresentável, não apenas
proibido.** Varri as 95 ocorrências do vocabulário de julgamento no pacote: todas são proibições,
fronteira nomeando o dono verdadeiro, proveniência de migração do que foi deliberadamente largado,
ou fixture adversarial que o validador precisa rejeitar.

**Lacuna declarada:** `evals/PLACAR.md` contém bloco de julgamento que cai sob o
`forbidden_context` do §2. Parei no título, **não li**, e não raciocinei sobre ele. Aquele arquivo
está portanto **fora da varredura** deste critério. Registro a lacuna em vez de supor o resultado.

- `confidence`: **media** — alta em toda cláusula que pude varrer; media no conjunto porque um
  arquivo do pacote foi retirado da varredura pela regra de cegueira.
- `residual_risk`: (1) **R7**, declarado em `protocolo:441` — a trava de texto livre casa
  *vocabulário fechado*, não intenção; alegação de nota em paráfrase, fora dos dez padrões, passa.
  O pacote enuncia esse teto em vez de escondê-lo. (2) `evals/PLACAR.md` não varrido: a leitura mais
  ampla da primeira cláusula ("o pacote") está verificada em todo lugar menos ali.

## CRIT-04 (secundária — só as cláusulas de forma) — **8** · banda `polido`

Ambas as cláusulas de schema são exatas: `$schema` é o URI do draft 2020-12 e `$id` está no
namespace `https://skill-crowd.local/schemas/` com nome de arquivo casando o pacote
(`schemas/…json:2-3`). A cláusula referenciar-em-vez-de-duplicar fecha: `SKILL.md:51-68` aponta
protocolo e schemas por caminho e nunca embute schema; cada agente cita o protocolo **por número de
seção** (§1, §2, §3, §5, §6 e a subseção de payload, §7, §8, §12) em vez de reescrevê-lo.

Fora de banda superior por contagem literal: **12 de 15 unidades numeradas** fecham com
`Concluído quando:`. As 12 seções de topo, sem exceção. **As três subseções numeradas não têm a
sua:** §6.1 (`protocolo:213`), §6.2 (`:244`), §6.3 (`:264`) — cobertas pela linha da §6-mãe
(`:285`), cumprimento defensável mas não literal.

- `confidence`: alta · `residual_risk`: quem ler a §6.2 isolada — que é exatamente como
  `agente-experimentos-e-spikes/SKILL.md:26` manda lê-la — recebe especificação de payload sem
  condição de conclusão declarada, e precisa subir até a §6 para uma escrita sobre retornos em geral.
