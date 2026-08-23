# Auditoria — Comitê de Lentes (2026-07-20) — skill `redator-tecnologia-ia`

> Registro de rastreabilidade (RI-04) da revisão do rascunho v0 escrito pelo
> Jeremias, pelo Comitê de Lentes real (6 lentes em paralelo, cada uma com o
> texto verbatim do seu próprio SKILL.md como briefing). Relatório no
> **Formato de entrega** da lente `auditor-responsabilidades`. O rascunho
> original está preservado em `referencia/rascunho-v0-original.md`.

## Padrão aplicado

- `PADRAO-DE-AUTORIA.md` — §3 anatomia, §4 descrição, §5b estrutura de
  Gerador, §6 princípios, §9 DoD, §10 Selo Lendário, §11 baseline antes do
  eval, §12 modos de falha.
- `REGRAS-DE-OURO.md` — RI-01..06, RO-01, RO-07, RO-15, hierarquia de
  confiança de canal.

## Vereditos por lente (rascunho v0)

| Lente | Veredito | Achados |
|---|---|---|
| arquiteto-software | REPROVADO | ARQ-1..13 |
| designer-ux-ui | REPROVADO | DES-1..12 |
| dev-senior | REPROVADO | DEV-1..14 |
| especialista-seguranca | REPROVADO | SEG-1..8 |
| qa-usabilidade | REPROVADO | QA-1..9 + 6 casos de teste desenhados |
| inovacao-melhorias | APROVADO COM RESSALVAS | INO-C1..C6 (cortes) + INO-A1..A5 (adições) |

Convergência forte: os 5 achados bloqueantes apareceram de forma
independente em 4 a 6 lentes cada — não são opinião de uma lente isolada.

## Não conformidades consolidadas → ação corretiva → status

1. **Frontmatter sem `---` de abertura** (ARQ-1, DES-1, DEV-1, QA-5,
   INO-A2). Verificado mecanicamente (`od -c`, parse padrão de frontmatter):
   sem o delimitador, `name`/`description` viram corpo e a skill **nunca
   registra nem dispara**. Severidade: alta. **Corrigido:** bloco
   `--- ... ---` válido, description entre aspas.

2. **Leituras obrigatórias apontando para arquivos inexistentes**
   (`references/headlines-e-formatos.md`, `references/confiabilidade-e-revisao.md`
   — citados, não entregues; ARQ-2, DES-3, DEV-2, SEG-2, QA-1, INO-C5).
   Viola RO-01 (controle citado que não existe), RI-04 e §12.4. A "lista de
   verificação de confiabilidade" — controle central da skill — era
   promessa, não entrega. Severidade: alta. **Corrigido:** os dois arquivos
   foram **criados de verdade** nesta refatoração, na pasta `referencia/`
   (convenção PT-BR do catálogo, não `references/` — ARQ-11/DEV-11).

3. **Description sem mecanismo de disparo** (infinitivos, zero frases-gatilho,
   sem "NÃO acione"; ARQ-3, DES-2, DEV-3, QA-8). Severidade: alta.
   **Corrigido:** reescrita no modelo §4 — 3ª pessoa, frases reais entre
   aspas, "Acione sempre que", exclusões explícitas. 1024 chars respeitados
   (contado, não estimado).

4. **Colisão de fronteira com `conteudo-riqueza` sem tratamento** (ARQ-4,
   QA-6; caso de teste CT-04: "post sobre como IA está mudando os
   investimentos" casa com as duas). Severidade: alta. **Corrigido:**
   critério decidível na description e na Rede — o **assunto-núcleo**
   decide: dinheiro/riqueza/investimento → `conteudo-riqueza`, mesmo
   citando IA; a tecnologia em si → esta skill; híbrido real → perguntar.
   **Pendente (decisão do Jeremias):** patch recíproco na description de
   `conteudo-riqueza` (altera skill instalada — fora do mandato desta
   auditoria; registrado em Sugestões de evolução).

5. **Sem Trava obrigatória nem caminho de recusa** (ARQ-13, DEV-4; Selo
   §10.4 "o caminho triste está escrito"). Severidade: alta. **Corrigido:**
   seção `## Trava obrigatória` com 3 casos nomeados de parada/recusa.

6. **Sem evidência de pronto + modificadores fail-open** ("quando
   relevante", "quando for material" — DEV-5, DES-10, QA-3, QA-4, SEG-5,
   SEG-6; §12.1 caso especial dos modificadores de obrigatoriedade).
   Severidade: alta. **Corrigido:** peça factual **sempre** sai com bloco
   alegação → fonte → data; revisão final vira checklist binário (em
   `referencia/confiabilidade-e-revisao.md`); divulgação de uso de IA
   deixa de ser juízo do agente — a decisão é do usuário, o agente sempre
   informa e pergunta.

7. **Nenhuma barreira de segurança de conteúdo** (SEG-1 injeção via fonte
   web; SEG-3 tutorial ensinando prática insegura; SEG-4 vazamento de dado
   confidencial do briefing; SEG-7 plágio/limite de citação; SEG-8 escape
   em HTML). Severidade: alta (SEG-1/3/4) e média (SEG-7/8).
   **Corrigido:** 5 guardrails novos com o texto proposto pela lente,
   ancorados na hierarquia de canal das REGRAS-DE-OURO e no padrão
   universal de escape.

8. **Corpo híbrido Lente+Gerador, fora do §5b** (ARQ-6, DEV-9).
   Severidade: média. **Corrigido:** reestruturado como **Gerador** no
   esqueleto §5b (gabarito `web-component`), com o tipo declarado.

9. **Duplicação interna ×3/×4** (anti-clickbait em 3 seções, "não inventar"
   em 3, fontes em 4 — ARQ-7, DEV-12, INO-C4; §12.5). Severidade: média.
   **Corrigido:** fonte única por regra — "não inventar" mora na tabela de
   lentes (coluna "Reprova se"); atenção honesta mora em Convenções;
   o resto referencia.

10. **Tabela das 4 lentes meio decorativa** (coluna "Contribuição" era
    prosa no-op — DES-6, INO-A3). Severidade: média. **Corrigido:** ganhou
    coluna **"Reprova se"** e virou o gate de revisão do Fluxo (passo 7):
    1 reprovação = corrige e repassa; entrega só com 4 aprovadas.

11. **Fluxo sem critérios de conclusão checáveis** (2 de 8 passos tinham —
    levantamento passo a passo do DEV-6; DES-8, INO-C6). Severidade: média.
    **Corrigido:** cada passo do Fluxo novo termina com critério checável;
    o antigo passo 8 ("conferir 7 substantivos") virou checklist binário.

12. **"5 títulos" sem porquê e sem variação garantida** (DES-7).
    Severidade: média. **Corrigido:** 5 títulos, cada um por estratégia
    nomeada distinta (as 5 estratégias estão em
    `referencia/headlines-e-formatos.md`), com recomendação e porquê em 1
    linha — títulos da mesma fórmula não dão escolha de verdade.

13. **Contradição interna sobre títulos entre 3 seções** (DEV-8).
    Severidade: média. **Corrigido:** regra única — título de trabalho
    sempre; as 5 opções sempre que a peça for titulável.

14. **Acessibilidade do conteúdo era palavra solta** (DES-9). Severidade:
    média. **Corrigido:** 4 critérios binários no checklist de revisão
    (alt text em toda imagem sugerida; headings sem salto de nível; texto
    de link que diz o destino; sigla expandida na 1ª ocorrência).

15. **Sem identidade editorial / anti-AI-slop** (DES-4: "um artigo sobre IA
    seguindo só este rascunho sai com a cara de qualquer LLM"). Severidade:
    alta. **Corrigido parcialmente:** seção **"Voz e tiques banidos"** com
    os tiques de IA em PT-BR nomeados um a um + substituto obrigatório
    (padrão match-and-refuse da lente designer). **Pendente (insumo do
    Jeremias, RO-01 — não se inventa a voz dele):** bloco "Voz do autor"
    extraído de 3–5 textos reais aprovados; registrado em Sugestões.

16. **Zero exemplos entra→sai** (ARQ-9, DES-5; §6.3). Severidade: alta
    (designer) / baixa (arquiteto). **Corrigido:** pares título-ruim→bom e
    abertura-ruim→boa no corpo + 1 exemplo completo pedido→peça em
    `referencia/headlines-e-formatos.md` (sintético, declarado como tal).

17. **Sem eval/baseline §11** (ARQ-8, QA-2, INO-A5). Severidade: alta para
    o Selo. **Corrigido parcialmente:** `evals/evals.json` criado com 8
    casos (acionamento + 4 adversariais de segurança desenhados pela lente
    SEG), todos marcados `origem: sintetico` (§11.6 — honestidade de
    proveniência). **Pendente e declarado:** rodar o baseline SEM a skill
    e registrar o placar baseline × pós-skill — não fabricado aqui (RI-04);
    mesmo tratamento dado à skill `email-marketing-html`.

18. **Sem Rede da skill, sem Histórico, degrau da escada não declarado**
    (ARQ-5/10/12, DES-11, QA-9, DEV-10). Severidade: média. **Corrigido:**
    bloco 🔗 Rede (deep-research vem antes; docx/pdf/dataviz vêm depois;
    "Não confundir com" conteudo-riqueza/designer-ux-ui/email-marketing-html),
    Histórico com a criação e esta auditoria, degrau 3 declarado com a
    justificativa da lente Inovação (domínio distinto; degraus 1–2 não
    bastam porque inflar a description de `conteudo-riqueza` mataria o
    disparo dela, e `referencia/` não dispara sozinha).

19. **Prosa no-op cortada** (INO-C1/C2/C3; lista da DES): "Entregar o
    conteúdo no formato pedido", o lema da abertura, "voz ativa, verbos
    concretos" e afins — cortados ou substituídos por critério checável.
    O que o baseline §11 provar redundante no futuro também cai (§11.4).

20. **Bordas de execução** (DEV-13: sem pesquisa web disponível; QA-7:
    régua pergunta-vs-segue indecidível). Severidade: média/baixa.
    **Corrigido:** fallback declarado (rotular "não verificado —
    conhecimento até <data>" ou recusar como factual) e régua enumerada
    (peça sobre produto/empresa do usuário sem público E sem objetivo →
    perguntar, máx. 2 perguntas; senão prosseguir com bloco Premissas fixo).

21. **Entrega sem RO-07** (DEV-14). Severidade: baixa. **Corrigido:** a
    Saída esperada fecha com 2–3 sugestões de evolução da peça.

## Rastreabilidade

- Verificações mecânicas do rascunho v0 (frontmatter, contagem de chars da
  description, ausência dos arquivos referenciados): comandos rodados pela
  lente dev-senior no sandbox (od/grep/ls/PyYAML) — números contados, não
  estimados.
- Casos de teste CT-01..CT-06 (qa-usabilidade) viraram semente do
  `evals/evals.json`.
- Cobertura declarada: STRIDE 5/5 aplicáveis (seguranca); 6/12 dimensões
  de teste aplicáveis com as não-aplicáveis nomeadas (qa); saturação
  RO-15 declarada pelas lentes inovacao e qa.

## Veredito de prontidão (pós-correção)

**APROVADO COM RESSALVAS.**

Todos os bloqueantes do rascunho v0 têm correção aplicada nesta entrega.
Ressalvas que seguem para o próximo ciclo, declaradas e com dono:

- **Placar baseline × pós-skill (§11) não rodado** — obrigatório antes de
  qualquer Selo Lendário; os evals existem, o placar não (não fabricado).
- **Bloco "Voz do autor" pendente de insumo do Jeremias** (3–5 textos reais
  aprovados) — sem isso a skill melhora estrutura e confiabilidade, mas a
  identidade de voz fica no genérico-bom.
- **Patch recíproco de fronteira na description de `conteudo-riqueza`** —
  decisão do Jeremias (altera skill instalada).
- Casos do eval são 100% sintéticos até o primeiro uso real substituí-los
  por `origem: real`.
