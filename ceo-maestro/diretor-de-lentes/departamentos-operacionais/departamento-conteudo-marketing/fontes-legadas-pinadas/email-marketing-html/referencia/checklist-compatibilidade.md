# Checklist de compatibilidade — clientes de e-mail

Referência rápida de por que cada regra do `SKILL.md` existe. Use antes de
declarar um e-mail "pronto para envio real" (não só "estrutura passou no
linter" — o linter audita estrutura, não os pontos abaixo).

## Os 4 comportamentos que mais quebram campanha

1. **Outlook desktop (Windows) renderiza com o motor do Word, não um
   navegador.** Não entende `flexbox`/`grid`/`position`, ignora `max-width`
   em `<div>` (por isso não existe `<div>` de layout aqui), e precisa do
   comentário condicional `<!--[if mso]>` pra forçar largura fixa (ghost
   table). É a razão de quase toda regra "estranha" deste catálogo.
2. **Gmail e Outlook.com/webmail bloqueiam imagem por padrão** na primeira
   abertura. Todo `<img>` precisa de `alt` descritivo e, quando possível,
   `background-color` de fallback — sem isso o e-mail vira uma caixa vazia
   até o destinatário clicar em "mostrar imagens".
3. **Gmail corta (clipping) e-mails acima de ~102KB de HTML.** Acima disso
   o Gmail mostra "Ver mensagem inteira" e o rastreamento de abertura (pixel
   no fim) para de funcionar. Mantenha o HTML enxuto; se passar de 90KB,
   é sinal de CSS/comentário duplicado sobrando.
4. **Dark mode não é uniforme.** Alguns clientes (Gmail app, Outlook.com)
   invertem cores automaticamente mesmo com `color-scheme`/
   `supported-color-schemes` declarado; outros (Apple Mail, Outlook
   desktop) respeitam o meta. Teste manualmente com tema escuro ativo antes
   de assumir que ficou legível — cor de texto sobre fundo transparente/PNG
   é o caso que mais quebra.

## Antes de marcar como pronto para envio (não coberto pelo linter)

- [ ] Testei com imagens bloqueadas — o texto sozinho ainda comunica a oferta?
- [ ] Testei/simulei modo escuro — texto continua legível?
- [ ] Assunto + pré-cabeçalho combinam e não repetem a mesma frase.
- [ ] Nenhuma palavra-gatilho óbvia de spam em excesso no assunto ("grátis",
      "urgente", "clique aqui" repetidos, excesso de `!!!` ou caixa alta).
- [ ] Todos os links (banner, botão, rodapé) apontam pra URL real, não
      `[LINK_DO_BOTAO]` esquecido de um placeholder.
- [ ] Peso do HTML abaixo de ~90KB (Gmail clipping).
- [ ] Testei numa ferramenta real de renderização multi-cliente (Litmus,
      Email on Acid, ou o preview do próprio ESP) antes do disparo em massa
      — este catálogo não tem acesso a essas ferramentas pagas; a validação
      aqui é estrutural (linter), não visual entre clientes.

## Fontes

- Can I email — suporte de CSS/HTML por cliente de e-mail (equivalente ao
  caniuse para e-mail) — https://www.caniemail.com/
- Litmus — guia de clipping do Gmail — https://www.litmus.com/blog/how-to-keep-gmail-from-clipping-your-emails
