# Histórico, auditoria e roadmap — email-marketing-html

Documento de apoio da skill `email-marketing-html`. Movido para fora do
SKILL.md (progressive disclosure): é conteúdo de rastreabilidade e
planejamento, consultado sob demanda, não a cada geração de e-mail. O
SKILL.md aponta pra cá em "Recursos desta skill".

## 💡 Sugestões de evolução (RO-07)

- Rodar o **baseline antes do eval** (§11 do `PADRAO-DE-AUTORIA.md`) num
  primeiro uso real: hoje esta skill não tem `evals/evals.json` — foi
  construída e testada (linter + 2 exemplos preenchidos), mas o placar
  baseline × pós-skill descrito no padrão ainda não existe; não fabricar
  esse placar agora seria pior que declarar a lacuna (RI-04).
- Avaliar adotar a técnica **Cerberus hybrid** (`<div style="display:
  inline-block">` com ghost table MSO por coluna) para colunas que
  precisam empilhar de verdade no mobile — hoje a grade de 2 colunas do
  `exemplo-02` é fluida por % mas não empilha (trade-off aceito, ver
  `exemplo-02-briefing.md`). Adotar isso exige **revisar RO-EM1** (a
  exceção da `<div>` de layout deixaria de ser só o pré-cabeçalho) — não
  fazer sem decisão explícita, é mudança de governança compartilhada.
- Se o MJML for validado num ambiente com npm disponível, promover o guia
  de "documentação a validar" para "motor testado" e registrar a evidência.
- ~~Ensinar o `scripts/lint-email.py` a checar imagem por caminho
  relativo/base64~~ — feito na auditoria 2026-07-20 (`check_relative_image_paths`,
  severidade WARN de propósito, ver Histórico).
- Rodar o `scripts/lint-email.py` contra um corpus maior de e-mails reais
  (fora dos 2 exemplos desta skill) pra calibrar a heurística de
  `check_generic_alt` — hoje a lista de termos genéricos é um chute
  educado (auditoria 2026-07-20), não testada contra falso-positivo em
  volume.

## 📜 Histórico

- **2026-07-20 — Criação (garimpo Cerberus/MJML/Email-Boilerplate/Maizzle):**
  primeira versão. Motor padrão híbrido (MJML quando `npx mjml -v` funcionar,
  HTML puro sempre como saída e fallback). MJML **não pôde ser testado** no
  ambiente de criação (registro npm bloqueado por política de rede da sessão
  Cowork) — caminho hand-rolled é o único testado com evidência até aqui;
  ver `referencia/mjml-guia.md` para o status exato.
- **2026-07-20 — `exemplo-02` (multi-banner):** adicionado par "isto entra →
  isto sai" mais gráfico (hero + faixa de urgência + grade de 2 benefícios),
  com imagens reais geradas (não placeholder). Documentou o trade-off da
  grade fluida por % (não empilha no mobile) e o aviso de que caminho
  relativo de imagem não é bulletproof — só serve pro preview local.
- **2026-07-20 — Auditoria do Comitê de Lentes (6 lentes: arquiteto-software,
  designer-ux-ui, dev-senior, especialista-seguranca, qa-usabilidade,
  inovacao-melhorias) e correções aplicadas:**
  - **Designer UX-UI (reprovado → corrigido):** hero do `exemplo-02` violava
    o padrão banido "hero-metric" (número gigante isolado) e usava gradiente
    roxo→rosa sem justificativa de marca (teste anti-AI-slop). Refeito:
    fundo sólido `#9A3412` (terracota), composição em 2 níveis (selo +
    título com o desconto embutido no texto), contraste medido 7.31:1.
    Contraste do rodapé (`#888888` sobre `#eeeeee`, ≈3.06:1) e do CTA
    (`#EC4899` sobre branco, ≈3.53:1) falhavam WCAG 4.5:1 — recalculados
    programaticamente e corrigidos em `template-base.html` e nos 2 exemplos
    (`#666666` no rodapé; `#9A3412` no CTA/hero, 7.31:1).
  - **Dev Sênior:** `check_no_modern_layout_css` comparava substring literal
    e não pegava espaço/quebra de linha ao redor de `:` — trocado por regex
    tolerante. `check_cta_not_image` era enganável por texto oculto
    (`display:none`) entre `<img>` e `</a>` — agora remove elementos ocultos
    antes de avaliar se sobrou texto visível.
  - **Especialista de Segurança:** linter não detectava `javascript:` em
    href/src, `<script>` inline nem atributos `on*=` — nova checagem
    `check_dangerous_uri` (FAIL).
  - **QA Usabilidade / Designer:** conteúdo só existia dentro da imagem da
    faixa de urgência (bônus de frete grátis) — sem fallback textual para
    bloqueio de imagem; adicionado parágrafo de texto real repetindo a
    mensagem, e legenda em texto abaixo de cada imagem de benefício.
  - **Auditor de Responsabilidades:** `check_unsubscribe` era WARN — promovido
    a **FAIL** (descadastro é exigência LGPD/ESP, não preferência estética).
  - **Arquiteto de Software:** RO-EM1–7 duplicados na íntegra entre este
    SKILL.md e `REGRAS-DE-OURO.md` — seção "Convenções obrigatórias" reduzida
    a resumo de 1 linha + remissão (padrão RO-15); RO-EM7 agora marca
    "hoje não validado" na própria regra, não só no cabeçalho da seção.
  - **Novas checagens do linter (antes inexistentes):** placeholder de
    conteúdo esquecido (FAIL), `alt` genérico/vazio (WARN), caminho de
    imagem relativo (WARN — severidade deliberadamente branda para não
    invalidar retroativamente o `exemplo-02`, que usa caminho relativo só
    para preview local).
  - Também removidos 4 travessões (—) de textos voltados ao usuário final
    (alt text e corpo dos 2 exemplos) e 2 caracteres cirílicos por engano de
    digitação (`exemplo-02-briefing.md`).
  - Relatório completo das 6 lentes salvo em
    `referencia/auditoria-2026-07-20.md` para rastreabilidade (RI-04).
- **2026-07-20 — Progressive disclosure (polimento estrutural).** Histórico
  e roadmap movidos para este arquivo; corpo do SKILL.md enxugado. Adicionadas
  seção explícita **Fronteira** (vs. `redator-tecnologia-ia`, transacional e
  display) e **Verificação — checklist de entregabilidade** em dois níveis
  (automático via linter + humano pré-disparo). RO-EM, Trava, Fluxo e
  Guardrails preservados sem alteração de conteúdo.
