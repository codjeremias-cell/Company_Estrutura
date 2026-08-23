# Auditoria — Comitê de Lentes (2026-07-20)

> Registro de rastreabilidade (RI-04) da revisão da skill `email-marketing-html`
> pelo Comitê de Lentes real, feita a pedido do Jeremias logo após a criação
> da v1 + `exemplo-02`. 6 lentes ativadas em paralelo, cada uma com o texto
> verbatim do seu próprio `SKILL.md` como briefing (não é revisão
> improvisada — RO-01). Este relatório segue o **Formato de entrega** da
> lente `auditor-responsabilidades`.

## Padrão aplicado

- `PADRAO-DE-AUTORIA.md` (Selo Lendário §10, anti-duplicação §12).
- `REGRAS-DE-OURO.md` — RO-01 (nunca inventar), RO-15 (fonte única +
  referência), Track Email Marketing HTML (RO-EM1–7, proposta 2026-07-20).
- WCAG 2.2 — contraste 4.5:1 (texto normal) / 3:1 (texto grande), via lente
  `designer-ux-ui`.

## Lentes ativadas

`arquiteto-software` · `designer-ux-ui` · `dev-senior` ·
`especialista-seguranca` · `qa-usabilidade` · `inovacao-melhorias`.
(`qa-usabilidade` e `especialista-seguranca` avaliaram sobretudo o linter,
já que não há produto rodando para testar em runtime.)

## Aderência às regras (RO/RI) — antes da auditoria

| Regra | Conforme? | Evidência |
|---|---|---|
| RO-EM1 (só table) | Conforme | `check_no_div_layout`, `check_tables_bulletproof` — 0 FAIL |
| RO-EM3 (CTA não é imagem) | **Falha silenciosa** | heurística bypassável por texto oculto |
| RO-EM5 (alt descritivo) | **Parcial** | linter só checava presença de `alt`, não conteúdo genérico |
| RO-EM6 (descadastro) | **Falha de severidade** | regra existe nos 2 exemplos, mas linter só dava WARN |
| RO-01 (nunca inventar) | Conforme | MJML documentado como "não testado", não inflado |
| RO-15 (fonte única) | **Não conforme** | RO-EM1–7 duplicado na íntegra em SKILL.md e REGRAS-DE-OURO.md |
| WCAG 4.5:1 | **Não conforme** | rodapé `#888888`/`#eeeeee` ≈3.06:1; CTA `#EC4899`/branco ≈3.53:1 |
| Teste anti-AI-slop (Designer) | **Reprovado** | hero com gradiente roxo→rosa genérico + padrão banido "hero-metric" |

## Não conformidades confirmadas → ação corretiva → status

1. **[Designer UX-UI] Hero do `exemplo-02` reprovado** — padrão "hero-metric"
   (número gigante isolado, 3 níveis empilhados) é proibição nominal da
   lente; paleta roxo→rosa sem justificativa de marca reprovou no teste
   anti-AI-slop. Severidade: alta (é o elemento mais visível do e-mail).
   **Corrigido:** hero redesenhado — fundo sólido `#9A3412` (terracota),
   composição em 2 níveis (selo "OFERTA DA SEMANA" + título de 1 frase com
   o desconto embutido no texto + 1 linha de apoio), sem número isolado.
   Contraste branco/`#9A3412` = 7.31:1. `urgencia-strip` e os 2
   `beneficio-*` recoloridos pra harmonizar com a mesma paleta. **Verificado**
   via `generate_banners.py` + screenshot Playwright pós-redesenho.

2. **[Designer UX-UI] Contraste WCAG abaixo do mínimo** — rodapé
   `color:#888888` sobre `background-color:#eeeeee` ≈3.06:1 (mínimo 4.5:1)
   nos 2 exemplos e no `template-base.html`; CTA `#EC4899` sobre branco
   ≈3.53:1 no `exemplo-02`. Severidade: alta (acessibilidade). **Corrigido:**
   rodapé → `#666666` (recalculado); CTA/hero → `#9A3412` (7.31:1) nos 3
   arquivos (`template-base.html`, `exemplo-01`, `exemplo-02`). **Verificado**
   via script Python de luminância relativa/contraste, não por inspeção
   visual.

3. **[Dev Sênior] `check_no_modern_layout_css` com bug de whitespace** —
   comparação por substring literal (`"display:flex" in html`) não detecta
   `display : flex` ou `display:\n  flex`. Severidade: média (falso
   negativo em CSS malformado/copiado). **Corrigido:** regex tolerante a
   espaço/quebra de linha ao redor de `:`. **Verificado** com caso sintético
   (`display  :   flex` → agora pega).

4. **[Dev Sênior / Especialista de Segurança] `check_cta_not_image`
   bypassável por texto oculto** — a heurística original exigia que não
   houvesse *nada* além do `<img>` entre `<a>` e `</a>`; um
   `<span style="display:none">texto</span>` ao lado do `<img>` escapava da
   checagem mesmo continuando invisível pra quem tem imagem bloqueada.
   Severidade: média (o CTA real pode sumir sem o linter perceber).
   **Corrigido:** a checagem agora remove elementos `display:none` antes de
   avaliar se sobrou texto visível. **Verificado** com caso sintético.

5. **[Especialista de Segurança] Linter não detectava conteúdo perigoso** —
   nenhuma checagem cobria `javascript:` em `href`/`src`, `<script>` inline
   ou atributos `on*=`. Severidade: média (nenhum destes funciona em
   cliente de e-mail real, e a presença costuma indicar copy-paste de
   template web ou injeção). **Corrigido:** nova regra `check_dangerous_uri`
   (FAIL). **Verificado** com 4 casos sintéticos (`javascript:` em href/src,
   `<script>`, `onclick=`).

6. **[QA Usabilidade / Designer] Conteúdo só dentro de imagem, sem
   fallback textual** — a faixa de urgência (bônus "frete grátis nas 100
   primeiras compras") só existia como texto dentro do PNG; com imagem
   bloqueada, a oferta some. Severidade: média (mensagem de negócio some
   silenciosamente). **Corrigido:** parágrafo de texto real repetindo a
   mensagem adicionado ao corpo, e legenda em texto real abaixo de cada
   imagem de benefício (mesmo conteúdo do `alt`, visível com imagem
   bloqueada). **Verificado** por leitura do HTML resultante.

7. **[Auditor de Responsabilidades] `check_unsubscribe` era WARN** —
   descadastro é exigência LGPD/política de ESP, não preferência estética;
   WARN não bloqueia a saída "0 FAIL aprovado", o que permitiria (em tese)
   entregar um e-mail sem opção de descadastro como "aprovado". Severidade:
   alta (compliance). **Corrigido:** promovido a FAIL. **Verificado**:
   linter atualizado, `RULES` reflete a severidade nova.

8. **[Arquiteto de Software] Duplicação RO-EM1–7 entre SKILL.md e
   REGRAS-DE-OURO.md** — violação do modo de falha 5 (Duplicação,
   `PADRAO-DE-AUTORIA.md` §12) e do padrão RO-15 (fonte única +
   referência). Severidade: baixa-média (risco de divergência futura entre
   as duas cópias, não bug funcional imediato). **Corrigido:** seção
   "Convenções obrigatórias" do SKILL.md reduzida a resumo de 1 linha por
   regra + remissão explícita ao REGRAS-DE-OURO.md como fonte única.

9. **[Arquiteto de Software] RO-EM7 sem marcação de status na própria
   regra** — "MJML opcional" descrito no cabeçalho da seção do
   REGRAS-DE-OURO.md como "não validado", mas a regra RO-EM7 em si não
   repetia isso — risco de alguém citar só RO-EM7 fora de contexto e
   perder o aviso. Severidade: baixa. **Corrigido:** RO-EM7 agora traz
   "hoje não validado" na própria frase, tanto no SKILL.md quanto no
   REGRAS-DE-OURO.md.

10. **[Inovação e Melhorias] Placeholder de conteúdo podia vazar pra
    entrega final sem detecção mecânica** — o Fluxo já instruía "nunca
    deixar placeholder sem substituir", mas nada verificava isso
    automaticamente; dependia só de disciplina humana. Severidade: média
    (é o tipo de erro que passa despercebido em revisão apressada).
    **Corrigido:** nova regra `check_no_leftover_placeholders` (FAIL) —
    roda contra o HTML final; contra o `template-base.html` cru, o FAIL é
    esperado (é o scaffold).

11. **[Inovação e Melhorias] `alt` genérico não era penalizado** — a
    checagem original só exigia que `alt="..."` existisse, aceitando
    `alt="banner"` ou `alt=""`. Severidade: baixa-média (acessibilidade
    real, não só formal). **Corrigido:** nova regra `check_generic_alt`
    (WARN — heurística de lista de termos, pode ter falso positivo, por
    isso não é FAIL).

12. **[Inovação e Melhorias, com correção do próprio Comitê] Proposta
    inicial de checar caminho relativo de imagem como FAIL foi rebaixada
    para WARN** — um FAIL retroativo invalidaria o `exemplo-02`, que usa
    caminho relativo **de propósito** pra preview local (documentado em
    `exemplo-02-briefing.md`). Fechamento checável: *se* um e-mail de
    produção sair com caminho relativo, *então* a imagem quebra em 100%
    dos clientes reais — a checagem existe pra alertar, não pra travar um
    padrão de preview legítimo. **Aplicado:** `check_relative_image_paths`
    (WARN).

13. **[Vários — achado transversal] Travessões (—) em texto voltado ao
    usuário final** — convenção de escrita do padrão evita travessão em
    copy de produto. Severidade: baixa (estilo, não função). **Corrigido:**
    removidos de `alt` e corpo dos 2 exemplos (3 no `exemplo-01`, 1 no
    `exemplo-02`).

14. **[Achado incidental, não das lentes] Caracteres cirílicos por erro de
    digitação** — "telас" em `exemplo-02-briefing.md` continha "а" (U+0430)
    e "с" (U+0441) cirílicos em vez de latinos. **Corrigido** via detecção
    programática de faixa Unicode + substituição.

## Rastreabilidade

- Cálculo de contraste: script Python ad-hoc (luminância relativa CIE,
  fórmula WCAG), não incluído no repositório da skill — refazer se precisar
  validar nova cor.
- Redesenho do hero: `referencia/exemplos/assets/generate_banners.py`
  (comentários no próprio código apontam o achado da lente que motivou cada
  mudança).
- Testes sintéticos dos 8 comportamentos novos/corrigidos do linter: rodados
  ad-hoc nesta sessão, não persistidos como suíte de teste formal — lacuna
  declarada (ver `SKILL.md` § Sugestões de evolução).
- Placar baseline × pós-skill (§11 `PADRAO-DE-AUTORIA.md`) continua **não
  existente** — já declarado como lacuna na v1, não fabricado aqui.

## Veredito de prontidão

**Aprovado com ressalvas.**

Todas as 14 não conformidades identificadas nesta rodada têm ação corretiva
aplicada e verificada nesta mesma entrega (critério objetivo de reprovação
do Auditor — nada foi "corrigido" sem re-execução). As ressalvas que
seguem para o próximo ciclo, não bloqueiam esta entrega:

- Sem `evals/evals.json` nem placar baseline × pós-skill — primeiro envio
  real ainda vai gerar essa evidência.
- MJML continua não testado neste ambiente (bloqueio de rede, fora do
  controle da skill).
- Heurística de `check_generic_alt` não validada contra corpus maior —
  risco de falso positivo/negativo não medido.
- Grade de 2 colunas do `exemplo-02` não empilha em telas muito estreitas
  (trade-off aceito e documentado, não é um bug).
