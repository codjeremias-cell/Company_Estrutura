# Histórico, evals e roadmap — redator-tecnologia-ia

Documento de apoio da skill `redator-tecnologia-ia`. Movido para fora do
SKILL.md (progressive disclosure): é conteúdo de rastreabilidade e
planejamento, consultado sob demanda, não a cada turno de redação. O
SKILL.md aponta pra cá em "Recursos desta skill".

## 💡 Sugestões de evolução (RO-07)

- ~~Bloco "Voz do autor"~~ — **v2 concluído em 2026-07-20** com corpus
  real de 3 textos (explicador, opinião, tutorial) fornecidos pelo
  Jeremias, em `referencia/voz-do-autor-corpus.md`. A previsão se
  confirmou: a voz real divergiu da declarada em 4 pontos, e o texto real
  prevaleceu. Evolução restante: adicionar novos textos aprovados ao
  corpus conforme surgirem (opcional — 3 formatos já cobrem as exceções).
- ~~Rodar o baseline §11~~ — **feito em 2026-07-20**, placar em
  `evals/placar-2026-07-20.md` (baseline falhou/parcial em 5 de 7;
  pós-skill 7/7 aderiu=S). Restam: observar o **acionamento em sessão
  real** (a coluna de bancada é simulada) e substituir os casos
  `origem: sintetico` por reais conforme o uso.
- **Patch recíproco em `conteudo-riqueza`:** adicionar à description dela
  a fronteira "tecnologia em si → redator-tecnologia-ia" (1 frase).
  Decisão do Jeremias — altera skill instalada.

## 📜 Histórico

- **2026-07-20 — Criação (rascunho do Jeremias) + auditoria do Comitê de
  Lentes na mesma data.** Rascunho v0 reprovado por 5 das 6 lentes
  (bloqueantes: frontmatter sem `---` de abertura — a skill nem
  registrava; leituras obrigatórias apontando pra arquivos inexistentes;
  description sem gatilhos; colisão sem fronteira com `conteudo-riqueza`;
  sem trava/recusa; sem evidência de pronto; nenhuma barreira de segurança
  de conteúdo). Refatorado como **Gerador** (§5b) com todas as correções —
  relatório completo em `referencia/auditoria-2026-07-20.md`; rascunho
  original preservado em `referencia/rascunho-v0-original.md`.
  **Degrau da escada (§6.10): 3 (skill nova), justificado** — domínio
  distinto de `conteudo-riqueza` (fatos mutáveis de tecnologia vs.
  biblioteca fixa de livros de finanças); degrau 1 mataria o disparo da
  skill existente ao inflar a description dela; degrau 2 não dispara
  sozinho pra um domínio que nenhuma skill cobre. **Lacunas declaradas
  (RI-04, não fabricadas):** placar baseline × pós-skill do §11 pendente;
  bloco Voz do autor pendente de insumo real do Jeremias; evals 100%
  sintéticos até o primeiro uso real.
- **2026-07-20 — Ciclo §11 rodado (baseline → reteste → placar):** baseline
  com 7 subagentes limpos **falhou/parcial em 5 de 7 casos geráveis**
  (sem títulos por estratégia nem bloco Fontes; entregou antes de perguntar;
  headline afirmativa sem lastro; placeholder em formato real de chave) —
  prova de que a skill ensina (§11.1). Reteste pós-skill: **7/7 aderiu=S,
  zero contorno**; acionamento **simulado** 8/8 (roteador-juiz sobre as 5
  descriptions reais — definitivo só em sessão real). Placar íntegro em
  `evals/placar-2026-07-20.md`. **Regra de corte §11.4 aplicada com exceção
  de segurança nomeada:** os guardrails de injeção-via-fonte e
  briefing-confidencial tiveram baseline PASSOU (caso flagrante único) e
  são mantidos mesmo assim — risco irreversível nomeado: publicação
  manipulada por terceiro e quebra de NDA/LGPD não têm rollback depois de
  publicadas; reavaliar com casos sutis `origem: real`. Roteador confirmou
  a fronteira unilateral com `conteudo-riqueza` (QA-6) — patch recíproco
  segue em Sugestões, decisão do Jeremias.
- **2026-07-20 — Voz do autor v1 (por questionário).** Jeremias definiu os
  4 eixos: leitor neutro-profissional (sem conversa direta) · autor
  invisível (zero primeira pessoa) · direto sem rodeio (conclusão
  primeiro, frases curtas) · traduzir quando há equivalente natural +
  leveza pontual sem piada. Bloco criado em Convenções, com as exceções de
  formato declaradas (tutorial = imperativo instrucional; página de
  produto fala com o comprador); item de voz adicionado ao checklist de
  revisão; exemplo entra→sai da `referencia/` realinhado à voz.
  **Proveniência declarada:** voz de questionário, não de corpus — refinar
  com 3–5 textos reais quando existirem (o texto real prevalece).
- **2026-07-20 — Voz do autor v2 (corpus real prevaleceu).** Jeremias
  forneceu 3 textos reais (explicador do SIN, opinião sobre IA, tutorial
  de ensino técnico) — salvos em `referencia/voz-do-autor-corpus.md` e
  promovidos a Leitura obrigatória. A voz observada **divergiu da
  declarada em 4 pontos**, todos ajustados a favor do texto real:
  (1) opinião usa primeira pessoa comedida ("acredito que"), o
  questionário dizia autor invisível; (2) "não apenas X. Significa Y" é
  assinatura deliberada do autor, não tique — liberada com parcimônia;
  (3) o fecho natural dele é síntese aforística, não próximo-passo;
  (4) "Imagine, por exemplo..." é convite de cenário legítimo em peça
  neutra. Confirmações fortes: zero anglicismo (mais rígido que o
  declarado), qualificadores honestos de precisão, sobriedade total.
  Lista de tiques banidos afinada pra não colidir com as assinaturas.
- **2026-07-20 — Progressive disclosure (polimento estrutural).** Movidos
  para `referencia/` os blocos pesados que não são consultados a cada
  turno: voz do autor detalhada + tiques banidos → `voz-e-tiques.md`;
  histórico + roadmap → este arquivo. Corpo do SKILL.md enxugado e
  ganhou seção explícita **Fronteira** (vs. `conteudo-riqueza` e
  `email-marketing-html`) e **Verificação — checklist editorial**. Voz,
  travas, guardrails e as 4 lentes preservados sem alteração de conteúdo.
