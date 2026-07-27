# Origem e recorte da consolidação híbrida

Congelamento anterior à escrita em 2026-07-26. As duas fontes permaneceram intactas. Hashes são
SHA-256; caminhos são relativos à raiz de cada skill no
`Catalogo-Skills-Unificado/skills/`.

## Fonte A — `redator-tecnologia-ia`

- arquivos: 11
- bytes: 74.115

| Arquivo | SHA-256 |
|---|---|
| `SKILL.md` | `5d31d497753fe126a0dc00e1660eebe0caf36e8f1fdb0404b934c71f71856fcd` |
| `agents/openai.yaml` | `cd747d703991451bf5bc0865e1bde1518b857c5d9531c15f2b32de75b5f0df5f` |
| `evals/evals.json` | `43cafbc5dbce6fb93d3165ac5d6259bbf5c7b07380c4329e7e87a77f13c2b67e` |
| `evals/placar-2026-07-20.md` | `2e2f1f8a57d91c3a4c4019ffa550dfa0476fe7cf244ea19da84d2a66a98eab98` |
| `referencia/auditoria-2026-07-20.md` | `ed567442150c00d5cab4e3a1a30f0f072f107a3967d915fd2cfbfc223d1d7cc8` |
| `referencia/confiabilidade-e-revisao.md` | `71b7277cb7b8f8e54608554952bec809bbfb37b400ddd0585b2819569528be28` |
| `referencia/headlines-e-formatos.md` | `c35e4ab38111863c1db71bff4d1c162d3baadbf07569b12ccba3bb4169e36eae` |
| `referencia/historico.md` | `86040bb2b82ea46f89fe5089b9f5926c81f0f5e4d9aa3d1f9be18c1d9e242286` |
| `referencia/rascunho-v0-original.md` | `d9106a1c5b4832783f5ce12b6e2c98085906ffffd2fea0315616ed8d041bbcf5` |
| `referencia/voz-do-autor-corpus.md` | `28a34ce1a7bb4a8f8e59df2c6f64b4b68bc2daf14ce0c435ecb96227322acbfb` |
| `referencia/voz-e-tiques.md` | `c8a7a7a34d0fde69b9acc836b2495c057dca1a3dd0add3ffffb6eb5c06577f72` |

## Fonte B — `email-marketing-html`

- arquivos: 17
- bytes: 154.008

| Arquivo | SHA-256 |
|---|---|
| `SKILL.md` | `249351c9e4e630536def50818eeab33e31990fcf079a81c8e3de4469d6cddc26` |
| `agents/openai.yaml` | `f7fb4eb352c62b51f6323c67ba770247a756fdb51864475bd5f9b84b00cd1fdd` |
| `referencia/auditoria-2026-07-20.md` | `a3566a0bb6eb6fee89f0da6f68be24f64f86d674db3099408f81d348926ba3ae` |
| `referencia/checklist-compatibilidade.md` | `ee7323b83face8914b0b81324dac274ee344fe65ba499c68d607113125b90e6c` |
| `referencia/exemplos/assets/beneficio-frete.png` | `f5047f83785e833a006137d8baf973486edc04af9cb279d5fb7c01b2c377f92d` |
| `referencia/exemplos/assets/beneficio-parcela.png` | `845fcc2cd254e9e31c774f88e76e24038188cf4c756fb5dbc4bc02e1be4b6efd` |
| `referencia/exemplos/assets/generate_banners.py` | `6697856833f07f47bd0ffe1f24477ebb7bdf0d84067302cf47d154945441d02a` |
| `referencia/exemplos/assets/hero-banner.png` | `a9bf32f6eeca9638783b2b7414a3d10af69db5a585277565bf19803a4507f3d2` |
| `referencia/exemplos/assets/urgencia-strip.png` | `f9fe1d80ced60aae1ccecc54891ff67ed039baccbce39bb970b3b563307856d5` |
| `referencia/exemplos/exemplo-01-briefing.md` | `4b1dfbe2058829ae513785b34d72ea69980bb67502514541dd2f991a51474eac` |
| `referencia/exemplos/exemplo-01-lancamento-curso.html` | `a4944d1436ec38b82f5624d076dbbe0489af15404b1d95c5b3b70f7153377c17` |
| `referencia/exemplos/exemplo-02-banner-promocional.html` | `3441aa106c51ce1233f6c21954284da3e65518595e627a5feb63fa2fc5cb9896` |
| `referencia/exemplos/exemplo-02-briefing.md` | `f3ba667dc188f702144c49e30a29ebc269811ef07ca296388b4439a8a6329c07` |
| `referencia/historico.md` | `0f5725294264112e605b69b1bb080c657894d42d6db37549babb0212c7e3910d` |
| `referencia/mjml-guia.md` | `cb35fa72dc532b96488a332d626301f3da2eb6e0d2fa1845675d74b4cc450ab5` |
| `scripts/lint-email.py` | `36fb94a0f70fe55927c4f6fa11ca586e15b3a9e5208fd0ef024517a5adb91687` |
| `template/template-base.html` | `534f0858fb623404bed01da6c30f745aaff31b7bc49dd7945976e2b57a57c841` |

## Recorte preservado

- pesquisa factual, data da apuração, confiabilidade, revisão e proibição de fabricação;
- narrativa em PT-BR, formato adequado ao canal e voz definida por briefing;
- HTML de e-mail em tabelas, CSS inline, CTA, alt, descadastro e teste de compatibilidade;
- `scripts/lint-email.py` e `template/template-base.html`, copiados byte a byte.

## Recorte reescrito

| Origem | Novo destino | Motivo |
|---|---|---|
| redator único de tecnologia | `agente-narrativa-redacao` | ampliar para produtos sem diluir sourcing e revisão |
| gerador isolado de e-mail | `agente-email-ciclo-de-vida` | cobrir estratégia, sequência, consentimento, entrega e HTML |
| gatilho direto da skill | `MARKETING_ASSIGNMENT` | impedir bypass e preservar gerente/agente |
| entrega autônoma | manifesto + gates + retorno ao Diretor | integrar canais e encaixar Juízes/CTO |

## Recorte não copiado

- metadata de interface das fontes: o pacote novo possui identidade própria;
- evals e placares históricos: medem gatilhos e saídas anteriores;
- auditorias e históricos: permanecem como evidência na origem;
- rascunhos, corpus de voz e exemplos de campanha: são específicos e não viram padrão universal;
- gerador visual e imagens de exemplo do e-mail: não constituem contrato do novo Departamento.

## Recorte criado

- estratégia de conteúdo e campanha;
- direção de arte/imagem;
- roteiro e produção de vídeo;
- publicidade e conversão;
- inteligência, UTM, experimentos e relatoria;
- governança de marca, direitos, IA, privacidade, acessibilidade e políticas;
- time elástico, oito gates e separação produção/ativação.

As capacidades criadas vêm da pesquisa primária registrada em
[fundamentos-pesquisa-2026-07-26.md](fundamentos-pesquisa-2026-07-26.md), não das skills legadas.

## Prova de não alteração

Ao final, recalcular as duas raízes e comparar arquivo a arquivo. Divergência bloqueia a alegação
de migração intacta. Cópias do lint e do template devem manter exatamente os hashes registrados.
