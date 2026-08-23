---
name: email-marketing-html
description: "Gera e-mails de marketing/propaganda em HTML bulletproof (só table/tr/td, CSS crítico inline, largura máxima 600px, CTA nunca é imagem, compatível com Outlook/Gmail/Apple Mail/Yahoo) com banner de cabeçalho clicável e rodapé com descadastro. Motor MJML é opcional (só quando `npx mjml -v` funcionar); a saída final é sempre HTML puro auditado por scripts/lint-email.py antes de entregar. Acione quando o usuário disser coisas como \"cria um e-mail de campanha\", \"preciso de um e-mail promocional com banner\", \"monta esse e-mail marketing em HTML\", \"gera o HTML do e-mail pra Mailchimp/RD Station/ActiveCampaign\", \"faz um e-mail responsivo bulletproof\", ou colar um exemplo de HTML de e-mail pra seguir o mesmo padrão. NÃO acione para e-mail transacional de sistema (confirmação de cadastro, redefinição de senha — trate como código de app, requisitos diferentes) nem para banner de anúncio display fora de e-mail (IAB 300x250/728x90 — fora do escopo desta skill)."
---

# Email Marketing HTML — e-mails promocionais bulletproof

> (Track Email Marketing HTML, proposta 2026-07-20 — a validar no primeiro envio real)

## Objetivo

Gerar um `.html` de e-mail promocional/propaganda autocontido — banner de
topo clicável, corpo de texto persuasivo, CTA e rodapé com descadastro —
que renderiza igual (ou pelo menos não quebra) em Outlook desktop, Gmail,
Apple Mail e Yahoo, sem depender de nenhum CSS que esses clientes não leem.

## Fronteira (quando usar / quando NÃO usar)

- **O artefato HTML do e-mail promocional (estrutura bulletproof + copy
  curta de campanha) → aqui.**
- **Conteúdo editorial sobre tecnologia/IA** (artigo, newsletter longa,
  explicador, tutorial) → `redator-tecnologia-ia` escreve o texto; se ele
  virar campanha de e-mail, **esta skill produz o HTML**. Esta cuida da
  *forma bulletproof*; o texto-fonte pode vir de lá.
- **E-mail transacional de sistema** (confirmação de cadastro, redefinição
  de senha) → é código de app, requisitos diferentes, fora desta skill.
- **Banner de anúncio display fora de e-mail** (IAB 300x250/728x90) → fora
  do escopo.

## Entradas obrigatórias

1. **Objetivo da campanha** (o quê está sendo anunciado/vendido/avisado) e
   **tom** (direto, institucional, urgente...).
2. **CTA principal**: texto do botão + URL de destino.
3. **Banner**: URL da imagem (ou descrição pra gerar/buscar) + URL de
   destino do clique + **texto alternativo descritivo** (nunca genérico tipo
   "banner" ou "imagem").
4. **Remetente**: nome da empresa/marca + motivo do envio (pra compor o
   rodapé de descadastro — RO-EM6).

## Entradas opcionais

- Pré-cabeçalho (texto de preview ao lado do assunto); paleta de cores da
  marca; segunda seção de texto/segundo CTA; se o e-mail deve ter mais de
  uma coluna (ativa a necessidade de ghost table — ver Convenções).

## Trava obrigatória

- **Não gerar sem CTA e sem banner definidos.** Sem os dois, não é um
  e-mail de marketing — é um rascunho; pare e pergunte em vez de inventar
  placeholder de conteúdo real.
- **Não gerar sem o alt text do banner.** Imagem sem `alt` é o defeito mais
  comum de e-mail marketing (RO-EM5) — se o usuário não fornecer, escreva um
  alt descritivo a partir do briefing, nunca deixe genérico.
- **Não entregar sem rodar `scripts/lint-email.py` no HTML final e mostrar
  o resultado.** 0 FAIL é o critério de "pronto" — ver Saída esperada.

## Leituras obrigatórias (RO-01)

Carregar sob demanda, antes do passo indicado:

1. **`template/template-base.html`** desta skill — é o ponto de partida
   sempre; nunca escrever a estrutura de tabelas do zero.
2. **`referencia/checklist-compatibilidade.md`** — por que cada regra existe
   (Outlook via motor Word, bloqueio de imagem por padrão, clipping do
   Gmail, dark mode não uniforme). Também é a fonte da checagem humana de
   entregabilidade (ver Verificação).
3. **`referencia/exemplos/`** — pares "isto entra → isto sai" reais:
   `exemplo-01` é banner único + texto (campanha simples); `exemplo-02` é
   multi-banner (hero + faixa de urgência + grade de 2 benefícios), para
   quando o pedido for "estilo banner"/campanha mais gráfica. Ler o briefing
   do exemplo mais próximo do pedido antes de gerar do zero.
4. Se o usuário colar um HTML de e-mail existente para servir de base/estilo
   — ler esse HTML real antes de adaptar (nunca reescrever de memória por
   cima do que já existe).

## Convenções obrigatórias — Fronteira bulletproof invariável (RO-EM, nunca cruzar)

**Fonte única do texto oficial: `Catalogo-Skills-Unificado/REGRAS-DE-OURO.md`
→ Track Email Marketing HTML.** Esta seção é remissão, não cópia (padrão
RO-15 — anti-duplicação, `PADRAO-DE-AUTORIA.md` §12 modo de falha 5); em
caso de divergência entre aqui e lá, o REGRAS-DE-OURO.md vale. Resumo de
1 linha por regra, pra consulta rápida durante a geração:

- **RO-EM1** — layout é só `<table role="presentation" cellspacing="0"
  cellpadding="0" border="0">`; nunca `<div>`/flexbox/grid/`position`
  (exceção única: `<div>` oculta de pré-cabeçalho).
- **RO-EM2** — CSS crítico (largura, cor de fundo, padding) sempre inline,
  nunca só no `<style>` do `<head>`.
- **RO-EM3** — CTA principal nunca é `<img>` sozinha; é tabela+link com
  texto real. Banner decorativo pode ser `<a><img>`.
- **RO-EM4** — ghost table MSO (`<!--[if mso]>...<![endif]-->`) em todo
  wrapper de largura fixa ou layout multi-coluna.
- **RO-EM5** — toda imagem com `alt` descritivo (nunca genérico) + fallback
  inline (`display:block`, `max-width`, `border:0`, `background-color`).
- **RO-EM6** — rodapé com identificação do remetente + descadastro visível
  é obrigatório (LGPD/política de ESP), nunca opcional.
- **RO-EM7** — motor MJML é opcional e **hoje não validado** neste ambiente
  (ver `referencia/mjml-guia.md`); saída final é sempre HTML puro.

## Fluxo

1. Confirmar as Entradas obrigatórias (Trava obrigatória acima).
2. Decidir o motor: rodar `npx --yes mjml -v`. Funcionou → seguir
   `referencia/mjml-guia.md`. Falhou/indisponível → copiar
   `template/template-base.html` como ponto de partida.
3. Preencher os placeholders (`[TÍTULO_PRINCIPAL]`, `[LINK_DO_BOTAO]` etc.)
   com o conteúdo real do briefing — nunca deixar placeholder sem
   substituir na entrega final.
4. Redigir o texto persuasivo: título direto, 1 ideia por parágrafo, CTA
   repetido no texto se o e-mail for longo.
5. Rodar `python3 scripts/lint-email.py caminho/email.html`.
   - **0 FAIL** → passo 6.
   - **Algum FAIL** → corrigir o que o linter apontou e rodar de novo. Nunca
     entregar com FAIL pendente.
6. Entregar o `.html` (+ `.mjml` fonte, se usado), colar a saída do linter
   como evidência e anexar o checklist de entregabilidade (Verificação).

## Regras de implementação

- O linter roda **sempre**, mesmo quando o motor foi o MJML — ele já é
  bulletproof por padrão, mas a skill audita a saída real em vez de confiar
  cegamente na ferramenta (RO-01: não presumir, verificar).
- Peso do HTML final abaixo de ~90KB (Gmail corta acima de 102KB — ver
  checklist-compatibilidade.md); se passar disso, é sinal de CSS duplicado.
- **Campanha "estilo banner" (multi-seção, mais de 1 imagem cheia de
  largura)**: cada banner é uma `<img>` de largura total na sua própria
  linha da tabela (ver `exemplo-02`) — nunca sobrepor banners com
  `position`. Para agrupar 2-3 itens lado a lado (ex.: grade de benefícios),
  usar `<td width="50%">`/`width="33%"` dentro de uma tabela interna: fluido
  por porcentagem, mas **não empilha** em telas muito estreitas — aceitável
  para bloco de apoio, nunca para o CTA principal (que fica sempre em linha
  própria, largura total).
- **Toda imagem do e-mail final vai por URL HTTPS absoluta**, nunca caminho
  relativo (`assets/...`) nem base64/data URI — cliente de e-mail não
  resolve nenhum dos dois de forma confiável. Caminho relativo só é
  aceitável em preview local de exemplo (ver aviso no
  `exemplo-02-briefing.md`), nunca na entrega final ao usuário.

## Guardrails

- Nunca gerar CTA como `<a><img></a>` sem texto visível ao lado (RO-EM3) —
  texto escondido com `display:none` não conta como texto real, o linter
  detecta esse disfarce.
- Nunca deixar `<div>` de layout (só a exceção do pré-cabeçalho — RO-EM1).
- Nunca entregar imagem sem `alt`, nem com `alt` genérico tipo "banner"/
  "imagem"/vazio (RO-EM5) — descreva o que a imagem transmite.
- Nunca omitir o rodapé de descadastro/identificação (RO-EM6) — o linter
  falha (**FAIL**, não aviso) se não encontrar. Rascunho de layout ainda
  precisa do placeholder explícito (`[LINK_DE_DESCADASTRO]`), nunca remover
  a seção inteira.
- Nunca entregar com placeholder de conteúdo (`[TÍTULO_PRINCIPAL]` etc.)
  esquecido — o linter falha (**FAIL**) se sobrar algum.
- Nunca `javascript:` em `href`/`src`, `<script>` ou atributo `on*=` inline
  — não funciona em cliente de e-mail real e o linter falha (**FAIL**).
- Nunca declarar "pronto" sem colar a saída do linter (RI-04 — prova, não
  promessa).

## Verificação — checklist de entregabilidade

Dois níveis, porque HTML válido não é o mesmo que "chega na caixa de
entrada e renderiza certo". O linter prova que a **estrutura** é
bulletproof; a segunda lista cobre o que ele **não consegue** ver e que só
revisão humana pega — e um e-mail errado, uma vez disparado em massa, não
tem rollback (RI-04: prova, não promessa).

**Automático — `scripts/lint-email.py` (0 FAIL, colar a saída):**

- [ ] Layout só em `<table>` (RO-EM1); CSS crítico inline (RO-EM2).
- [ ] CTA principal é tabela+link com texto real, não `<img>` (RO-EM3).
- [ ] Toda imagem tem `alt` descritivo + fallback (RO-EM5).
- [ ] Rodapé com identificação + descadastro presente (RO-EM6).
- [ ] Zero placeholder `[...]` esquecido; zero `javascript:`/`<script>`/`on*=`.

**Humano — antes do disparo em massa (o linter não cobre; ver
`referencia/checklist-compatibilidade.md`):**

- [ ] **Teste visual real** em Outlook desktop, Gmail (web+app), Apple Mail
  e Yahoo — não confiar só no preview.
- [ ] **Imagens desligadas:** a mensagem e o CTA continuam compreensíveis
  pelo texto/alt (muitos clientes bloqueiam imagem por padrão).
- [ ] **Peso final < ~90KB** (Gmail corta acima de 102KB e esconde o rodapé
  de descadastro — risco de compliance, não só estético).
- [ ] **Dark mode:** cores não somem em fundo escuro (dark mode não é
  uniforme entre clientes).
- [ ] **Palavras de spam / assunto:** revisar assunto e corpo contra
  gatilhos comuns de filtro.
- [ ] **Todos os links resolvem** (CTA, banner, descadastro) por URL HTTPS
  absoluta — o de descadastro precisa funcionar de verdade (LGPD/ESP).

## Saída esperada

- Um `.html` autocontido (subject sugerido em comentário no topo do
  arquivo), com **0 FAIL** no `scripts/lint-email.py` — esse é o critério de
  "pronto para revisão humana", não "pronto pra disparo em massa": os itens
  do checklist humano de entregabilidade (teste visual multi-cliente,
  palavra de spam, peso final) exigem revisão que o linter não cobre.
  Rodar o linter no `template/template-base.html` cru **deve** mostrar FAIL
  de placeholder — isso é esperado (é o scaffold, não um e-mail pronto).
- A saída do linter colada como evidência + o checklist de entregabilidade
  anexado, com o nível humano marcado como pendente de revisão.
- Se o motor foi MJML: também o `.mjml` fonte, salvo junto.

## Referências reais (RO-01)

- **Cerberus** (Ted Goas, MIT — templates fluid/responsive/hybrid,
  técnica de ghost table e `dir="ltr/rtl"`) — https://github.com/emailmonday/Cerberus
- **MJML** (Mailjet, MIT — motor opcional, ver `referencia/mjml-guia.md`) — https://github.com/mjmlio/mjml · https://documentation.mjml.io/
- **Email-Boilerplate** (Sean Powell, baseado no MailChimp Blueprints —
  resets clássicos; parte está datada, usar com critério) — https://github.com/seanpowell/Email-Boilerplate
- **Maizzle** (MIT — framework Tailwind completo; avaliado e **não
  adotado** como motor principal aqui por exigir scaffold de projeto inteiro,
  overkill para gerar um e-mail avulso) — https://github.com/maizzle/maizzle
- **Can I email** (suporte de CSS/HTML por cliente, equivalente ao caniuse
  para e-mail) — https://www.caniemail.com/
- **Litmus — guia de clipping do Gmail** — https://www.litmus.com/blog/how-to-keep-gmail-from-clipping-your-emails

## 🔗 Rede da skill

- **Lentes que ativam junto (RI-06):** `dev-senior` (qualidade do HTML/CSS
  gerado) · `designer-ux-ui` (hierarquia visual, contraste do CTA) ·
  `especialista-seguranca` (nunca injetar conteúdo de usuário sem escapar no
  HTML do e-mail — RO universal "Conteúdo do usuário em HTML/e-mail: escapar
  + validar destinatário") · `auditor-responsabilidades` (audita a aderência
  às RO-EM antes de qualquer envio real).
- **Vem antes:** `requisitos-descoberta` quando o briefing da campanha ainda
  não está claro (objetivo, público, oferta) · `redator-tecnologia-ia`
  quando a copy/texto-fonte da campanha é conteúdo editorial de tecnologia.
- **Vem depois:** `testador-real` quando o projeto tiver disparo automatizado
  (nunca disparar e-mail real de teste — regra já vale pro testador
  universal); revisão humana com `referencia/checklist-compatibilidade.md`
  antes do envio em massa.
- **Não confundir com:** `redator-tecnologia-ia` (escreve o conteúdo
  editorial; esta skill produz o HTML bulletproof) · e-mail transacional de
  sistema (código de app, não desta skill) · banner de anúncio display fora
  de e-mail (fora do escopo).

## Recursos desta skill (progressive disclosure)

Carregados sob demanda — não pesam no contexto até serem lidos:

- `template/template-base.html` — scaffold de tabelas, ponto de partida.
- `scripts/lint-email.py` — auditor bulletproof (roda sempre antes de entregar).
- `referencia/checklist-compatibilidade.md` — o porquê de cada regra + a
  checagem humana de entregabilidade.
- `referencia/exemplos/` — pares "entra → sai" (exemplo-01 simples, exemplo-02 multi-banner).
- `referencia/mjml-guia.md` — status e uso do motor MJML opcional.
- `referencia/historico.md` — histórico de versões, auditoria e roadmap da skill.
