# Headlines e formatos — fórmulas, aberturas e exemplo entra→sai

> Leitura obrigatória antes do passo 7 do Fluxo (títulos) e do passo 4
> (estrutura). Material pesado fora do corpo da skill (Selo §10.5).

## As 5 estratégias de título (uma por opção — nunca 5 da mesma)

Cada entrega propõe 5 títulos, **um por estratégia**, porque 5 variações
da mesma fórmula não dão escolha real ao usuário.

| # | Estratégia | Fórmula | Exemplo ruim → bom |
|---|---|---|---|
| 1 | **Benefício direto** | [resultado concreto] + [condição/contexto] | "Conheça o poder da automação" → "Automatize os boletos da sua escola e recupere 6 horas por semana" *(o "sua" dirigido é aceitável em título de conversão/página de produto; em peça editorial, preferir a forma neutra: "Automação de boletos devolve horas por semana a escolas de médio porte")* |
| 2 | **Como-fazer** | Como [resultado] + [restrição que qualifica] | "Tutorial de IA" → "Como rodar um LLM local num notebook com 16 GB de RAM" |
| 3 | **Dado/número** | [número verificado] + [contexto que o torna significativo] | "IA cresce muito no Brasil" → "62% das PMEs brasileiras já usam alguma IA — mas só 8% medem o retorno" *(números ilustrativos — no uso real, só número com fonte no bloco Fontes)* |
| 4 | **Pergunta real do público** | a pergunta como o público digita | "Reflexões sobre LLMs locais" → "Vale a pena rodar IA local em vez de pagar API?" |
| 5 | **Contraste/tensão honesta** | [expectativa] vs [realidade verificada] | "A verdade sobre no-code" → "Montamos o mesmo app em no-code e em código: o barato saiu caro em 3 dos 5 critérios" |

**Regra dura:** o título só promete o que o texto entrega no primeiro
terço. Estratégia 5 exige que o contraste exista de verdade na peça
(evidência no bloco Fontes), senão é clickbait com verniz.

## Modelos de abertura (escolher 1, nunca misturar 2 no mesmo lead)

1. **BLUF (conclusão primeiro):** a resposta/insight essencial na primeira
   frase; o resto do texto sustenta. Padrão pra notícia, explicador e
   análise.
2. **Problema do leitor:** abrir com a dor específica que o público
   digitaria na busca; a peça é a saída. Padrão pra tutorial e página de
   produto.
3. **Cena ancorada em fato:** pessoa/equipe real (ou anonimizada
   declarada), obstáculo, decisão — rastreável a fonte ou briefing (lente
   Autor reprova cena inventada). Padrão pra estudo de caso e newsletter.
4. **Dado que reordena:** um número verificado que muda como o leitor vê o
   assunto, seguido do "e daí" em 1 frase.

**Anti-aberturas (banidas — ver tiques na SKILL.md):** cenário genérico
("Em um mundo cada vez mais digital..."), definição de dicionário ("IA é
a capacidade de..." quando o público já sabe), pergunta retórica vazia
("Você já parou pra pensar...?").

## Exemplo entra→sai (sintético, declarado — substituir pelo primeiro caso real)

**Entra (pedido):** "escreve um explicador sobre RAG pro blog, público é
gestor não técnico que ouviu o termo em reunião"

**Sai (esqueleto aprovado + lead — já na Voz do autor: neutro, sem
conversa direta com o leitor):**

> **Título recomendado (estratégia 4):** "O que é RAG e por que chatbots
> corporativos precisam dele?"
>
> **Lead (BLUF):** RAG é o que impede um chatbot corporativo de inventar
> resposta: em vez de responder de memória, o sistema consulta os
> documentos internos da empresa antes de gerar o texto. A diferença
> prática: menos resposta errada com cara de certa, e respostas que citam
> a fonte interna.
>
> **Esqueleto (linha "Explicador" da tabela de formatos):**
> 1. O que é — a analogia da prova com consulta (2 parágrafos)
> 2. Como funciona — busca + geração, sem jargão de embedding no corpo
>    (nota de rodapé pra quem quiser o termo técnico)
> 3. Por que importa — o custo de um chatbot que alucina política interna
> 4. Exemplo — atendimento com base de conhecimento (anonimizado)
> 5. Limites — RAG não conserta documento desatualizado; qualidade da
>    base é teto da qualidade da resposta

O par mostra o padrão: promessa cumprida no lead, jargão contido,
limites declarados. A peça completa seguiria o Fluxo (fontes, 4 lentes,
checklist).

## Estruturas por formato — notas de execução

A tabela da SKILL.md é a fonte única da ordem das seções. Notas que não
cabem lá:

- **Tutorial:** toda etapa fecha com "resultado esperado" observável
  ("o terminal mostra X"); pré-requisitos com versão ("Node 20+, testado
  na 20.11"). Sem isso a lente Redator técnico reprova.
- **Notícia:** data de verificação no corpo, não só no bloco Fontes —
  notícia envelhece em dias.
- **Página de produto:** a seção "prova" só aceita evidência verificável
  (número com fonte, depoimento real autorizado); sem prova real, a seção
  sai com placeholder declarado ao usuário, nunca com prova inventada.
- **Newsletter/roteiro:** 1 ideia central por edição — segunda ideia boa
  vira a próxima edição, não um segundo bloco.
