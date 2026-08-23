# Exemplo 02 — banner promocional (multi-banner, estilo "propaganda") → e-mail

Par "isto entra → isto sai" mais rico que o exemplo 01: mostra o e-mail
quando o pedido é "estilo banner" — mais gráfico, mais seções, mais perto do
que uma loja manda numa campanha de oferta relâmpago/Black Friday.

## Entrada (o que o usuário pediu)

> "Quero um e-mail de oferta relâmpago, 40% de desconto até domingo à
> meia-noite. Precisa parecer campanha de verdade — banner grande no topo,
> uma faixa de urgência avisando que as 100 primeiras compras ganham frete
> grátis, e destacar dois benefícios (frete grátis acima de R$150 e
> parcelamento em 12x). CTA: 'Aproveitar agora'."

## O que mudou em relação ao exemplo 01 (lançamento de curso)

- **Multi-banner, não banner único.** Hero banner (topo) + faixa de urgência
  (banner secundário, mais estreito) — os dois são `<img>` cheias de largura,
  cada uma na sua própria linha da tabela (RO-EM1: continua sendo só
  table/tr/td, só que com mais linhas).
- **Grade de 2 colunas para os benefícios.** Aqui está o trade-off que vale
  registrar: as duas colunas usam `<td width="50%">` dentro de uma tabela
  interna — **fluida por porcentagem**, então em qualquer tela ela encolhe
  proporcionalmente, mas **não empilha** (não vira 1 coluna) em telas muito
  estreitas (~320px), diferente do banner de largura total que sempre ocupa
  100%. Para um bloco de apoio (like ícones de benefício) isso é aceitável
  — continua legível encolhido. **Nunca use esse padrão de coluna fixa para
  o CTA principal** — o botão continua em linha própria, largura total.
  (A técnica que faria as colunas empilharem de verdade sem media query
  duplicada usa `<div style="display:inline-block">`, tipo Cerberus hybrid —
  deliberadamente **não adotada aqui** ainda, porque contradiz a regra atual
  RO-EM1 "nunca `<div>` de layout"; ver Sugestões de evolução no `SKILL.md`.)
- **Imagens geradas de verdade**, não placeholder quebrado — ver
  `assets/generate_banners.py` (script auxiliar, não faz parte da skill:
  a skill recebe URL de imagem pronta do usuário/design, não gera imagem).

## Saída

Arquivo gerado: [`exemplo-02-banner-promocional.html`](./exemplo-02-banner-promocional.html),
com os assets em [`assets/`](./assets/).

## ⚠️ Antes de usar em produção

Este exemplo referencia as imagens por **caminho relativo**
(`assets/hero-banner.png`) só para o preview local funcionar sem servidor.
**Isso não é bulletproof de verdade** — nenhum cliente de e-mail resolve
caminho relativo de arquivo. Antes de enviar de verdade: subir os PNGs para
um host HTTPS real (CDN do ESP, S3, etc.) e trocar os 4 `src="assets/..."`
pela URL absoluta. Desde a auditoria de 2026-07-20 o `scripts/lint-email.py`
**já checa isso** (`check_relative_image_paths`, severidade **WARN** de
propósito — um FAIL aqui invalidaria este próprio exemplo, que usa caminho
relativo para preview local por decisão documentada, não por descuido).

## Redesenho do hero (auditoria 2026-07-20)

A versão original do hero (fundo gradiente roxo→rosa + número "-40% OFF"
gigante isolado) foi **reprovada pela lente `designer-ux-ui`**: violava a
proibição nominal do padrão "hero-metric" e falhou no teste anti-AI-slop
(paleta sem justificativa própria de marca). Redesenhado para fundo sólido
`#9A3412` (terracota) + título de 1 frase com o desconto embutido no texto
(sem número isolado) — contraste branco/`#9A3412` = 7.31:1. Relatório
completo das 6 lentes em [`../auditoria-2026-07-20.md`](../auditoria-2026-07-20.md).

## Evidência (RI-04 / Selo Lendário §10.3)

```
$ python3 scripts/lint-email.py referencia/exemplos/exemplo-02-banner-promocional.html
============================================================
[PASS] DOCTYPE
[PASS] Viewport
[PASS] Sem <div> de layout
[PASS] Sem CSS moderno (flex/grid/position)
[PASS] Tabelas bulletproof
[PASS] Imagens bulletproof (4 imagens)
[PASS] Sem placeholder de conteúdo sobrando
[PASS] Sem URI perigosa / script inline
[PASS] Link de descadastro
[WARN] CTA não é imagem pura   (esperado: é o hero banner clicável, não o botão)
[PASS] alt text não genérico
[PASS] Wrapper max-width:600px
[PASS] Ghost table MSO (Outlook)
[WARN] Imagens com URL absoluta   (esperado: caminho relativo é só para preview local, ver aviso acima)
============================================================
RESULTADO: 0 FAIL — estrutura bulletproof aprovada (WARN acima é revisão de conteúdo, não bloqueia).
```

Renderização real (Chromium headless, `screenshot2.js`) confirma visualmente,
pós-redesenho: hero terracota sem gradiente, faixa de urgência, grade de 2
benefícios com legenda em texto, CTA e rodapé todos legíveis e com contraste
WCAG conforme.
