# Motor MJML (opcional) — guia + trava de disponibilidade

> **Status honesto (RI-04 — não fabricar resultado):** este guia foi escrito a
> partir da documentação oficial do MJML (mjml.io, MIT License). **Não** foi
> possível instalar/compilar MJML de verdade na sessão em que esta skill foi
> criada — o ambiente de nuvem (Cowork) bloqueia o registro `npmjs.org` por
> política de rede (`x-deny-reason: host_not_allowed`). O caminho hand-rolled
> (`template/template-base.html`) é o único motor **testado com evidência**
> nesta skill — ver `referencia/exemplos/`. Trate os comandos abaixo como
> documentação a validar no primeiro uso real num ambiente com acesso ao npm
> (ex.: Claude Code local na máquina do Jeremias), não como caminho já provado.

## Por que considerar MJML

MJML é uma linguagem de marcação semântica (`<mjml><mj-body><mj-section><mj-column>...`)
que compila para o mesmo tipo de HTML bulletproof que este catálogo escreve à
mão — mas testado contra dezenas de clientes de e-mail pela comunidade Mailjet.
Ele resolve por padrão coisas que o template manual precisa lembrar toda vez:
ghost tables do Outlook, `mso-*` resets, comportamento fluido em coluna única
no mobile. Ganho real: menos chance de esquecer um detalhe bulletproof numa
campanha grande com várias seções/colunas.

## Trava obrigatória antes de usar

Nunca assuma que o motor está disponível. Primeiro passo sempre:

```bash
npx --yes mjml -v
```

- **Funcionou (imprimiu versão)** → pode usar MJML para este e-mail.
- **Falhou** (sem Node, sem rede, `403`/`ENOTFOUND`, timeout) → **não insista** —
  caia direto no `template/template-base.html` (HTML puro) sem perguntar de
  novo nem bloquear a entrega. A saída final para o usuário é sempre HTML puro
  de qualquer forma (ver abaixo).

## Fluxo quando disponível

1. Escrever o `.mjml` (não o `.html` final):

```xml
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Arial, sans-serif" />
    </mj-attributes>
    <mj-preview>[Pré-cabeçalho — texto de preview]</mj-preview>
  </mj-head>
  <mj-body background-color="#f4f4f4">
    <mj-section padding="0">
      <mj-column>
        <mj-image src="[URL_DO_BANNER]" alt="[ALT_DESCRITIVO]" href="[LINK_DO_BANNER]" />
      </mj-column>
    </mj-section>
    <mj-section background-color="#ffffff" padding="40px 30px 20px 30px">
      <mj-column>
        <mj-text font-size="24px" font-weight="bold" color="#111111">[TÍTULO]</mj-text>
        <mj-text font-size="16px" line-height="24px" color="#333333">[PARÁGRAFO]</mj-text>
      </mj-column>
    </mj-section>
    <mj-section background-color="#ffffff" padding="0 30px 40px 30px">
      <mj-column>
        <mj-button background-color="#0056b3" border-radius="4px" href="[LINK_DO_BOTAO]">
          [TEXTO_DO_BOTAO]
        </mj-button>
      </mj-column>
    </mj-section>
    <mj-section background-color="#eeeeee" padding="24px 30px">
      <mj-column>
        <mj-text font-size="12px" color="#888888" align="center">
          [NOME_DA_EMPRESA] · [ENDEREÇO]<br/>
          <a href="[LINK_DE_DESCADASTRO]" style="color:#888888;">Cancelar inscrição</a>
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
```

2. Compilar:

```bash
npx --yes mjml caminho/para/email.mjml -o caminho/para/email.html
```

3. **Rodar o mesmo `scripts/lint-email.py` no HTML compilado** — MJML já é
   bulletproof por padrão, mas a skill audita igual (Prova, não promessa —
   nunca confiar cegamente numa ferramenta externa sem checar a saída real).
   Se algo do MJML mudar em versão futura e passar a gerar `<div>`/CSS moderno
   em algum componente, o linter pega.
4. Guardar o `.mjml` fonte junto do `.html` gerado (mesma pasta, mesmo nome) —
   rastreabilidade (RI-04): quem for editar depois edita o `.mjml`, não o HTML
   compilado à mão.

## Componentes mj-* mais usados aqui

| Tag MJML | Equivalente bulletproof manual |
|---|---|
| `mj-section` | `<table><tr><td>` de largura 100% |
| `mj-column` | coluna que empilha sozinha no mobile (sem precisar escrever a media query) |
| `mj-image` | `<img>` com `display:block` + `max-width` já aplicados |
| `mj-button` | botão tabela+link bulletproof (equivalente ao bloco CTA manual) |
| `mj-text` | `<td>` de texto com os resets de fonte já aplicados |

## Quando NÃO usar MJML mesmo se disponível

- E-mail de 1 coluna simples (banner + texto + botão) — o `template-base.html`
  já resolve sem a dependência extra; usar MJML aqui é peso sem ganho.
- Ambiente sem certeza de acesso a npm no momento do envio real (ex.: alguém
  vai copiar o `.html` final direto pra um ESP) — nesse caso o HTML já
  compilado é o que importa, e o hand-rolled evita a dependência de o
  destinatário do arquivo ter Node instalado para reproduzir.

## Referência oficial

- Documentação MJML — https://documentation.mjml.io/
- Repositório (MIT License) — https://github.com/mjmlio/mjml
