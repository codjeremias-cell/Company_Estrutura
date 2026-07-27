# Fundamentos pesquisados — Conteúdo e Marketing

Baseline de pesquisa para a criação do Departamento. Especificações e políticas de plataforma são
voláteis: cada execução confirma a fonte oficial atual e registra data. A pesquisa não substitui
revisão jurídica para caso concreto.

## Método e saturação

Foram priorizadas fontes primárias: legislação, regulador, autorregulação, padrões e documentação
oficial de plataforma.

| Rodada | Foco | Requisitos líquidos novos |
|---:|---|---:|
| 1 | imagem, vídeo, formatos, acessibilidade e políticas de anúncio | 5 |
| 2 | privacidade, publicidade identificável, e-mail, mensuração e proveniência | 5 |
| 3 | acessibilidade audiovisual, experimentos e leitura contextual de métricas | 2 |
| 4 | direitos autorais e confirmação das políticas | 1 |
| 5 | ativos responsivos e confirmação de acessibilidade | 1 |

As duas últimas rodadas trouxeram menos de dois requisitos novos; a pesquisa parou por saturação,
conforme RO-15. Pesquisa futura abre por canal ou risco concreto, não por coleta infinita.

## Requisitos adotados

### Conteúdo e confiança

- Priorizar conteúdo útil para pessoas, original, com fonte, autoria, experiência demonstrável e
  títulos descritivos; SEO não justifica conteúdo feito para manipular ranking.
- Registrar **quem**, **como** e **por quê**; divulgar automação/IA quando for razoavelmente
  esperado pelo público.
- Tratar alegações verificáveis como claims: fonte, data, escopo e responsável.

Fonte: [Google Search — conteúdo útil e confiável](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).

### Imagens, banners e publicidade

- Imagens informativas exigem alternativa textual; decorativas usam `alt=""`; imagem funcional
  descreve a função; evitar texto dentro de imagem; gráfico complexo exige equivalente completo.
- Especificação pertence ao canal e à data. No Google Ads, tamanhos comuns incluem 1200×628
  (1,91:1) e 1200×1200 (1:1), mas a execução confirma o formato vigente.
- Ativos responsivos precisam funcionar em combinações: evitar texto, logo ou botão falsamente
  sobreposto; manter oferta e destino coerentes.
- Anúncio e destino devem ser claros, funcionais, relevantes e honestos; alegação irreal,
  cobrança obscura, oferta indisponível e destino divergente bloqueiam.
- Aplicar princípios LEAN do IAB: leve, criptografado, compatível com escolha do usuário e não
  invasivo.

Fontes:

- [W3C WAI — Images Tutorial](https://www.w3.org/WAI/tutorials/images/)
- [Google Ads — formatos e tamanhos](https://support.google.com/google-ads/answer/13676244?hl=en)
- [Google Ads — boas práticas de display responsivo](https://support.google.com/google-ads/answer/9823397?hl=en)
- [Google Ads — políticas](https://support.google.com/google-ads/answer/6008942?hl=en)
- [IAB — Guidelines](https://www.iab.com/guidelines/)

### Vídeo e audiovisual

- Planejar acessibilidade antes de filmar: legendas para fala e sons relevantes, transcrição,
  descrição de informação visual e player acessível quando aplicável.
- Preparar variantes 16:9, 9:16 e 1:1 quando o canal exigir, com safe zones verificadas na fonte
  atual; não presumir que um corte serve para todos.
- Avaliar thumbnail, título, retenção e tempo assistido em conjunto; CTR isolado pode enganar.

Fontes:

- [W3C WAI — áudio e vídeo acessíveis](https://www.w3.org/WAI/media/av/)
- [Google Ads — especificações de vídeo](https://support.google.com/google-ads/answer/13547298?hl=en)
- [YouTube — impressões e watch time](https://support.google.com/youtube/answer/9314486?hl=en)

### E-mail e ciclo de vida

- Enviar somente a destinatários esperados/consentidos; manter identidade e assunto verdadeiros.
- Autenticar domínio. Para envio em massa ao Gmail, a documentação vigente exige SPF, DKIM e
  DMARC, alinhamento e descadastro em um clique; monitorar reputação e spam.
- Corpo deve ter alternativa textual, HTML robusto, CTA claro, identificação, descadastro e
  compatibilidade testada. Não comprar lista nem usar opt-in pré-marcado.

Fonte: [Gmail — Email sender guidelines](https://support.google.com/mail/answer/81126?hl=en).

### Privacidade, consentimento e dados

- Toda coleta/segmentação registra finalidade, hipótese legal, necessidade, balanceamento,
  salvaguardas, transparência, retenção e direitos.
- Legítimo interesse não se aplica a dados sensíveis e não é atalho universal.
- Cookies analíticos e publicidade comportamental exigem análise contextual; preferir agregação e
  minimização, sem colocar dado pessoal em UTM.

Fontes:

- [ANPD — Guia de legítimo interesse](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia_orientativo_hipoteses_legais_tratamento_de_dados_pessoais_legitimo_interesse)
- [ANPD — Cookies e proteção de dados](https://www.gov.br/anpd/pt-br/assuntos/noticias-periodo-eleitoral/anpd-lanca-guia-orientativo-201ccookies-e-protecao-de-dados-pessoais201d)

### Publicidade identificável e claims

- Anúncio deve ser honesto, verdadeiro, socialmente responsável e distinguível de conteúdo
  editorial. Influenciador, afiliado, embaixador ou parceiro deve tornar a natureza comercial
  ostensiva.
- Setores e públicos sensíveis exigem revisão específica; o gate genérico não autoriza campanha
  regulada.

Fonte: [CONAR — Código Brasileiro de Autorregulamentação Publicitária](https://www.conar.org.br/codigo/codigo.php).

### Direitos e proveniência

- Texto, fotografia, desenho, música e audiovisual são protegidos. Reprodução, adaptação,
  distribuição e inclusão audiovisual normalmente dependem de autorização; licença é registrada
  por modalidade, território, prazo e canal.
- Registrar ingredientes, criação, edição e uso de IA. Content Credentials/C2PA prova integridade
  da proveniência declarada, não verdade factual; ausência de credencial não prova falsidade.

Fontes:

- [Lei nº 9.610/1998 — direitos autorais](https://www.planalto.gov.br/ccivil_03/leis/l9610.htm)
- [C2PA — Content Credentials Explainer](https://spec.c2pa.org/specifications/specifications/2.2/explainer/Explainer.html)

### Mensuração e experimentos

- Usar convenção UTM estável e em minúsculas; no mínimo `utm_source`, `utm_medium` e
  `utm_campaign`; `utm_content` distingue criativos. Nunca incluir PII.
- Começar por objetivo de negócio, hipótese, métrica primária, guardrails e janela. Testar uma
  variável por vez quando a inferência depender dela; registrar resultados inconclusivos.
- Não atribuir causalidade a métrica observacional. Declarar modelo, janela, cobertura e limites.

Fontes:

- [Google Analytics — custom campaign URLs](https://support.google.com/analytics/answer/10917952?hl=en)
- [Google Ads — Experiments](https://support.google.com/google-ads/answer/7281575?hl=en)

## O que a pesquisa não decidiu

- política jurídica aplicável a produto/setor concreto;
- plataforma, orçamento, público e oferta de uma missão;
- ferramenta de geração ou publicação disponível no runtime;
- licença efetiva de um ativo;
- resultado esperado de uma campanha.

Esses itens vêm do contrato, de Negócios, da autorização ou da evidência de execução.

