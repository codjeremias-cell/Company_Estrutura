# Origem e proveniência da migração

## Fonte legada

- origem lógica:
  `SKILL - Nova formula/maestro/comite-de-lentes/orquestrador-inovacao-melhoria`;
- inventário relido duas vezes em 2026-07-26;
- **22 arquivos**, **101.022 bytes**;
- nenhum agente subordinado;
- nenhum JSON Schema;
- nenhum validador executável;
- nenhum `CONTRATO-DE-COMPROMISSO.md`.

O legado permanece intacto. Ele serve como proveniência/rollback histórico,
nunca como fallback operacional.

## Manifesto vivo antes da migração

Formato: `SHA-256 | bytes | arquivo`.

```text
0D8B4946CFA23481EE13FDD87710412696A2CC9BE07EF1B92FBAA2B86460BDBE | 271 | agents/openai.yaml
FA72B3ACD9AA4337E64D719A308EBBE502A369D53BC3409E26EC1F179C2AB68E | 3680 | evals/baseline-sem-skill.md
10D9BC2F8CE25522E4C9788A3BC9E92327202EB0AB620EBD03F8147EA7BC89FE | 9284 | evals/candidatos/a/SKILL.md
CE8217262B152CA95A878A5E6817FDDBDEBF7C63792BB163F06F60E19E44D1E2 | 12000 | evals/candidatos/b/SKILL.md
26F5463E15D0693D780B81C7CAB11F1626A0A0BD2A4CAA41081094F6C13C4AEE | 2481 | evals/comite-final.md
FFFC87901B3A8BC7A80BA1BF4CE63F596EA3D4FAC8303760A865E2E090CD3DE7 | 2526 | evals/criterio-comite.md
F8D8B56C039189464E1AA8D57BCB1DB39CC39F2A0A722ED6FA9BA732B5DA7C9E | 2136 | evals/criterio-painel.md
4EFD5A050F21B6FE68B8D6CC1BDFB413E10CFF6FEDCF2FE8CB8ECBE1C0F87FBB | 6802 | evals/evals.json
D82EB2445867854140D43732E61091CFEBFFC9E16D1A202E8AD078C851E6E35A | 2330 | evals/forward-test/outputs-1-2.md
996E51841352B3EF5C3AB58B668EBE5FFFB6681D86F25CD4CAEFE25E8A2075CA | 1643 | evals/forward-test/outputs-3-5.md
4D5EA6002F36588884B2D8F9B1BF696450139367BDCB7D76AAC96999F81335DF | 1176 | evals/forward-test/outputs-6-7.md
E49FF62251B17F6B2F32513AA9B728398ACE68D0B5463BB1563D69D0A7A72605 | 3003 | evals/forward-test/round-2-outputs-1-2.md
336C0FC8B54886C10A0B6DA107DFB9EFC1309A9E428D877817AEF7535749967E | 2490 | evals/forward-test/round-2-outputs-5-7.md
B2CAF1FE3097B2B3768F06EDCD87F530B5E17C3C81F9A2CB62E87F08D8BD847F | 1692 | evals/forward-test/round-5-output-5.md
57DA9CA6F4BB06585B4EF0D7B41C26E0187001ADFF76D2DEEA01FD50A1AB982B | 1992 | evals/manifest-sha256.txt
F81DB8673D5F78B93BD2640F1BC104F2379418FFF0537E118C7B1944FD3961E8 | 1680 | evals/painel-final.md
DD4BC3EB0B4BAA0E250203E4D332D02A70C73183AA2F80891A20069A7486E805 | 8149 | evals/placar.md
54D48CB6E5B80D0152EBFD12901FD17199DFC490661DC7E1172CCCE5C2BFF1BC | 7253 | references/contratos.md
92AA2879E03A4ADCFF5BB801E500F1A6B8C2DBB2F155B6FBF584D89C9D5D33DE | 5274 | references/fundamentos-do-dominio.md
EA76BABB72690E8D47AC62AB9A3B0D19C17B7B68CCC68B9A79E6C9871951F165 | 6964 | references/modelo-operacional-do-time.md
395C3B6B21553EF679DB3BADF3922123D1922FE6FB80EE3973643643D6C3D72E | 3933 | references/rubrica-inovacao-melhoria.md
9ED52040555A93779DD2E9EC18227BFE5FFF7A3C6436A685957213C32D023926 | 14263 | SKILL.md
```

## Manifesto histórico desatualizado

O `evals/manifest-sha256.txt` legado possui 21 entradas e diverge do estado
vivo em:

| Arquivo | Hash registrado | Hash vivo |
|---|---|---|
| `SKILL.md` | `29E64F71212D6A8328CA70D12090339C86E9219BEEBEB44B78EAFED7E43E1A4A` | `9ED52040555A93779DD2E9EC18227BFE5FFF7A3C6436A685957213C32D023926` |
| `references/contratos.md` | `80C8BA8983CBB001C66D0E284DDE35100493A59AB6395F479E513B83C7F83CE8` | `54D48CB6E5B80D0152EBFD12901FD17199DFC490661DC7E1172CCCE5C2BFF1BC` |

Por isso, placar/painel/Comitê e `FINAL_VALIDATION_OK` do legado provam uma
versão anterior, não o conteúdo vivo. Todos permanecem históricos e não foram
promovidos.

## Recorte aplicado

### Preservado com adaptação

Dor/JTBD/desperdício; baseline; hipótese/métrica/rollback/PDCA; tecnologia como
hipótese; estados do portfólio; lacunas; autoria/evidência; gerente não
executa.

### Reescrito

Identidade, cadeia, time, contratos, schema, evals e retorno. Comitê virou
Diretor; time futuro virou três agentes reais; exemplos YAML viraram artefatos
validados.

### Excluído

Modo `JULGAR`, rubrica, nota 9,5, `innovation_judgment_result`, candidatos A/B,
painéis e placares antigos como runtime. Julgamento pertence aos Juízes.

## Verificação posterior

Na promoção, recalcular os 22 hashes acima contra a fonte legada. Qualquer
divergência bloqueia a alegação “legado intacto” até ser explicada.

## Pacote promovido — 2026-07-26, rodada 3

O pacote canônico tem **23 arquivos versionados**: os 22 da migração mais
[`evals/corpus_adversarial.py`](../evals/corpus_adversarial.py), criado na
rodada 3 para reexecutar as 45 mutações do parecer independente. O
`evals/__pycache__/` que aparece depois de rodar os validadores é byproduto do
Python, coberto pelo `.gitignore` da raiz e fora da contagem.

| Bateria | Comando | Resultado |
|---|---|---|
| validador local | `PYTHONIOENCODING=utf-8 python evals/validate_workflow.py` | **122/122 PASS; 0 FAIL** |
| corpus adversarial | `PYTHONIOENCODING=utf-8 python evals/corpus_adversarial.py` | **45/45 rejeitadas; 0 escapes** |
| `skill-creator` | `PYTHONUTF8=1 python .../quick_validate.py <pasta>` | **4/4 `Skill is valid!`** |
| integridade do legado | dentro do validador local | **22/22 hashes, 101.022 bytes** |
| cadeia canônica completa | validador de cada pacote + `_compartilhado` | **1531/1531 PASS; 0 FAIL** |

Composição da cadeia medida em 2026-07-26 após esta frente: `_compartilhado`
61 · Segurança 184 · Negócios 170 · Registros 170 · **Inovação e Melhoria
122** · QA e Usabilidade 117 · Arquitetura de Dados 114 · Design UX/UI 109 ·
Desenvolvimento 105 · Arquitetura de Software 72 · Auditoria 65 · Juízes 62 ·
Evolução de Skills 57 · Diretor de Lentes 50 · Conteúdo e Marketing 39 · CEO
Maestro 33.

A cadeia era **1467/1467** com este Departamento em 59. O salto para
**1531/1531** é `122 − 59 = +63` verificações **deste pacote**: nenhum outro
validador mudou de número. Não é regressão de vizinho; é cobertura nova.

### Por que a rodada 3 existiu

A rodada 2 fechou com o validador em **59/59 PASS** e, no mesmo pacote, **39 de
45 mutações escapando** num corpus adversarial independente. O verde media
forma, não semântica: proveniência com formato correto mas sem contexto de
origem, gates autoassertivos, PDCA sem envelope autenticado, payload aberto e
julgamento livre em texto. A rodada 3 fechou as 45 e transformou cada
contraprova em fixture permanente — o teto do que isso prova está declarado em
[`../evals/ADVERSARIAL-AUDIT.md`](../evals/ADVERSARIAL-AUDIT.md) e em
[`../evals/PLACAR.md`](../evals/PLACAR.md).
