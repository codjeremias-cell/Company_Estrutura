# Exemplo 01 — briefing → e-mail (par "isto entra → isto sai")

## Entrada (o que o usuário pediu)

> "Preciso de um e-mail avisando que a turma nova do curso de JavaFX abre hoje.
> Tom direto, sem enrolação. CTA: 'Garantir minha vaga', linkando pra
> `/curso-javafx/matricula`. Banner: `banner-curso-javafx.jpg`. Desconto de 20%
> até sexta à meia-noite. Remetente: Curso-Java Escola de Programação, São Paulo."

## Entradas obrigatórias que a skill precisou confirmar antes de gerar

1. Objetivo da campanha → avisar abertura de turma + gerar matrícula.
2. Público/tom → quem já demonstrou interesse (lista de espera); tom direto.
3. CTA principal → "Garantir minha vaga" → `/curso-javafx/matricula`.
4. Banner → URL da imagem + link de destino + alt text descritivo (a skill
   *recusou* seguir sem o alt text — ver Trava obrigatória do SKILL.md).
5. Remetente/rodapé → nome + cidade, para compor a identificação obrigatória
   (RO-EM6).

## Saída

Arquivo gerado: [`exemplo-01-lancamento-curso.html`](./exemplo-01-lancamento-curso.html).

## Evidência (RI-04 / Selo Lendário §10.3)

```
$ python3 scripts/lint-email.py referencia/exemplos/exemplo-01-lancamento-curso.html
============================================================
[PASS] DOCTYPE
[PASS] Viewport
[PASS] Sem <div> de layout
[PASS] Sem CSS moderno (flex/grid/position)
[PASS] Tabelas bulletproof
[PASS] Imagens bulletproof
[PASS] Sem placeholder de conteúdo sobrando
[PASS] Sem URI perigosa / script inline
[PASS] Link de descadastro
[WARN] CTA não é imagem pura   (esperado: é o banner clicável, não o botão)
[PASS] alt text não genérico
[PASS] Wrapper max-width:600px
[PASS] Ghost table MSO (Outlook)
[PASS] Imagens com URL absoluta
============================================================
RESULTADO: 0 FAIL — estrutura bulletproof aprovada (WARN acima é revisão de conteúdo, não bloqueia).
```

(Saída atualizada em 2026-07-20 após a auditoria do Comitê de Lentes — ver
[`../auditoria-2026-07-20.md`](../auditoria-2026-07-20.md); rodapé recalculado
para `#666666` por contraste WCAG, e a lista de regras do linter cresceu com
3 checagens novas.)

0 FAIL é o critério de pronto (§ Saída esperada do SKILL.md). O WARN de
CTA-como-imagem é esperado e correto aqui: quem virou `<a><img></a>` sem
texto foi o banner clicável do topo (que pode ser imagem — é decorativo),
não o botão principal (que já é tabela + texto, RO-EM3).
