# Origem e recorte da migração

## Fonte congelada

- **Origem:** `SKILL - Nova formula/maestro/comite-de-lentes/lente-qa-usabilidade`
- **Captura:** 2026-07-26, antes de qualquer escrita no legado
- **Escala:** 87 arquivos, 823.887 bytes
- **Política:** legado intacto; rollback manual e evidência histórica; nunca
  fallback runtime.

## Recorte preservado

Preservado **conceitualmente**, com nova identidade e contrato:

- gerente orquestra e não executa;
- fail-closed, causalidade, versão e digest;
- `PASS/FAIL/SKIP/PENDING/UNVERIFIED` sem promoção;
- risco → critério → caso → resultado → evidência;
- autorização específica, dados sintéticos/minimizados e parada;
- revalidação de autorização, limpeza, rollback e recuperação;
- defeito reproduzível e evidência com alvo/ambiente/data/produtor;
- WCAG 2.2 AA, tarefas, personas, estados de interface e dimensões de borda;
- inventário de capacidade e lacuna explícita.

Nenhum arquivo foi copiado byte a byte: a cadeia, os agentes, a autoridade e os
envelopes mudaram.

## Recorte reescrito

| Legado | Novo | Por quê |
|---|---|---|
| `lente-qa-usabilidade` | `departamento-qa-usabilidade` | papel e superior novos |
| Comitê → lente | Diretor → Departamento | hierarquia vigente |
| capacidades futuras | três agentes materializados | organograma exige executores reais |
| `GERENCIAR | JULGAR` | somente gerência de QA | Juízes são independentes |
| nota/veredito local | estado/recomendação sem nota | corte e validação pertencem aos Juízes |
| função genérica de time | fronteiras funcional/não funcional/usabilidade | propriedade exclusiva |
| schema `qa-contracts/v3` | schema local do Departamento | novas identidades e envelopes |
| retorno ao Comitê | `DEPARTMENT_RETURN` ao Diretor | consumidor real já possui schema |
| fonte canônica pinada em runtime | síntese local com proveniência | remove dependência/fallback |
| proibição de agentes | `agentes/` obrigatório | pedido atual e guia de migração |

## Recorte não copiado

- Modo `JULGAR`, rubrica absoluta, autoindependência e saídas de julgamento.
- Candidatos A/B, rodadas antigas, placares, painel e respostas pós-skill.
- Validadores e fixtures do contrato/rota antigos.
- Afirmações de aprovação do legado. O último placar multidisciplinar
  registrado reprovou a arquitetura/design; passes técnicos posteriores não
  substituem esse gate.
- Qualquer path, enum, identidade ou digest fixado em `comite-de-lentes` /
  `lente-qa-usabilidade`.

Os casos de risco úteis foram **reescritos** em `evals/evals.json`; resultados
antigos não foram promovidos.

## Manifesto completo

Classificação por arquivo:

- `REESCRITO`: fonte operacional sintetizada no novo pacote;
- `NAO_COPIADO`: evidência/histórico do contrato antigo, mantida somente no
  legado.

```text
SHA-256                                                          BYTES   CLASSE        CAMINHO
805a9bfc329a9be4189a9bde4e61efc8bfc39a183f7841e8314c7ddd13f31af2     247 REESCRITO     agents/openai.yaml
68c333739154c2134a42dc832386085462130d7f5813ec6c4bdcf5682ab23a68   16545 NAO_COPIADO   evals/baseline-qa-canonica-r2.md
2d40824db09bc9b909f6ee23ca906d65330e9b3988524f208dc4e8539a2d5856     231 NAO_COPIADO   evals/candidatos/a/lente-qa-usabilidade/agents/openai.yaml
fbd2ce5785cf53a16aa1497e00065d4531915e142bbf40899f0d33a2bda01ee5    7664 NAO_COPIADO   evals/candidatos/a/lente-qa-usabilidade/references/contratos.md
9098757c781852a79df172a3763e03c8f65fca470f1b9c6f80d25bab0e00666f    5927 NAO_COPIADO   evals/candidatos/a/lente-qa-usabilidade/references/modelo-operacional-do-time.md
ed74e46323a13224ba29d73163e868867dd28fa817bb24c46739d15b34ce2f36    5633 NAO_COPIADO   evals/candidatos/a/lente-qa-usabilidade/references/rubrica-qa-usabilidade.md
98665304ece62df59d3d4870b2b69ebcd19c633f4b6f8d5f5f47ff94b6606bcc   15227 NAO_COPIADO   evals/candidatos/a/lente-qa-usabilidade/SKILL.md
b4d6a365b2b9e9ee8bba7087f9213bc1702a5d688793784fc71c5b11eda282e5     260 NAO_COPIADO   evals/candidatos/b/lente-qa-usabilidade/agents/openai.yaml
c96045a95669c817a37ef132bb3aca4798380615c11bff0dd0f1cff7a90c973a   10949 NAO_COPIADO   evals/candidatos/b/lente-qa-usabilidade/references/contratos.md
6c27863ba3dfdd822467b6e310467c72c0023913848a4c98499d86199905ebe0   10033 NAO_COPIADO   evals/candidatos/b/lente-qa-usabilidade/references/modelo-operacional-do-time.md
b0745a26e266a080114741574c46e8122ea0fc2753b233ab8a3ef0f8e52d018f    8947 NAO_COPIADO   evals/candidatos/b/lente-qa-usabilidade/references/rubrica-qa-usabilidade.md
4fd784a837663009469c0bdffce3ba76dc1f567e849eb73a6752a6bd87f5e8d0   15933 NAO_COPIADO   evals/candidatos/b/lente-qa-usabilidade/SKILL.md
457d3abb20e2b350c685b4050eebedb8c383a87e3641a7048f4397f4d88cf63d    6068 NAO_COPIADO   evals/comite/rodada-1/arquiteto-software.md
5782e8bba28a922e4b167dff2b568d5d33d14c4f2334820b47121c91fe72d161    4013 NAO_COPIADO   evals/comite/rodada-1/designer-ux-ui.md
48eb498adcfd691b8acf49b9142fd1cca586abffcb0eb64acd876bf5c7d1f9d1    5029 NAO_COPIADO   evals/comite/rodada-1/dev-senior.md
840e882d412a845c266f6cbc99a8db57a5cf113104e224b5eedef0030ff0133c    5845 NAO_COPIADO   evals/comite/rodada-1/especialista-seguranca.md
eb53a0412497b9c3c1e357125c8b0821c225ae3072fb6adfc57b0adcc52c0ef0    5839 NAO_COPIADO   evals/comite/rodada-1/inovacao-melhorias.md
75c1d185cc0206e3822ff19d3d23774e7ce101db34db950f612d34f49b43e2bc    6709 NAO_COPIADO   evals/comite/rodada-1/qa-usabilidade.md
2886341f64007a687f8a8e5027bad5c4407c03a1f3bc43e4e85e154697d25c67    5409 NAO_COPIADO   evals/comite/rodada-2/arquiteto-software.md
2f454a09502f5e878899887c2ed7e288372347433e4a651c1ce7cdf9ca82e64a    3941 NAO_COPIADO   evals/comite/rodada-2/designer-ux-ui.md
980b3b0c8bb401791c74e89e0b8fdef131336b3c0f56a2a2809ebce14989bfd2    4880 NAO_COPIADO   evals/comite/rodada-2/dev-senior.md
1ce4d48db59d21a714a7efc0d4d85862e2e580e82b343b656d67fd3a40dd1627    5972 NAO_COPIADO   evals/comite/rodada-2/especialista-seguranca.md
02e4c41246d205aae53a5c71846dae1172f637e9af16b9295b77f4a9935d76f5    3723 NAO_COPIADO   evals/comite/rodada-2/inovacao-melhorias.md
97de383559fa47a67edfe803df6e1451097394707d608cc76e4eb36746d9e016    7747 NAO_COPIADO   evals/comite/rodada-2/qa-usabilidade.md
45180bffb1e5c4c48c7619b8c123e3cc4b22b9bf72d9e30d5e87949c2b56789f    5338 NAO_COPIADO   evals/comite/rodada-3/arquiteto-software.md
c39daa6e6b3a3660489522cd09beb74267dbb541e1188c637c622a4527189119    9520 NAO_COPIADO   evals/comite/rodada-3/designer-ux-ui.md
9203fdb1316859cea94c3ee76dc4301bd1e3f18478ee1e80c28aad7b91066209    5282 NAO_COPIADO   evals/comite/rodada-4/arquiteto-software.md
187f84ea5edec3f3847ce22d12485c15136bb4f88b0911453f13f75da564ceaf    6222 NAO_COPIADO   evals/comite/rodada-4/designer-ux-ui.md
c037ddbe6e8a95c7bfb3adf463793156458f229436824620d381d83eaf751313    1136 NAO_COPIADO   evals/contratos/placar.md
68464d3bc94d6ca889d247fb7af3cf4b9bdc68d1455903c191dbec09f47e0610    3522 NAO_COPIADO   evals/contratos/placar-v3.md
0c558b7ee814f70db4cd293d3c796a229403503521b2dec5baa45b8fdbeb1fdb    1266 NAO_COPIADO   evals/contratos/seal-envelope.mjs
38e1ad6f097cb5ea3645276597194afaa1dcb336085738ae44959d8753a57517    4845 NAO_COPIADO   evals/contratos/validate-contracts.ps1
266a29fdcad72007764e086e66ea35d96bf276d8f7f283f75654d9948723599f   36466 NAO_COPIADO   evals/contratos/validate-contracts-v3.mjs
d826a8e0a5f0d94ab2aae9641bb9d424ef5198b7b25608739b7d753e2b44cc06    5858 NAO_COPIADO   evals/contratos/vectors.json
902b63739b5bc30e3b48c695ed449ad0b3232c117b8c97dbb32f6fbc8e089e67    1704 NAO_COPIADO   evals/criterio-comite.md
0a34dea86d486429b9af6edfcbf9fa8eddfcfbb8b0b3bea714bbc1c9e27d6fff    2891 NAO_COPIADO   evals/criterio-painel.md
e075d6d52cb791648003db28032cd6ca7aa36c3f50570cf4915dfd07aa2cba87    3270 NAO_COPIADO   evals/decisao-de-pegada.md
f63181b31ac700c361e0864a9b62cc7118c733a8d6ba352c91199ee09babcb48   12547 NAO_COPIADO   evals/evals.json
5570ebbbe1058702a1d8b62a6d3444f6923f40fdddc960f51ba56b2276043716    1950 NAO_COPIADO   evals/harness-r2.md
f13d2e7a5d262bf8c184cb1e4bddc417fed7b0eb3d2f625b89aa55bb78c92927    2638 NAO_COPIADO   evals/manifest-r2.md
a7ed6e4bbf1dd6afcbc47ab6604d8c81fc93379867dfe0816a960af146e2d6ba    3143 NAO_COPIADO   evals/manifest-r3b.md
2cc4b1aa9990b2de8215513b73b49ccdb0e6b61cf433ebed53c97f4c86a6e8cb    4846 NAO_COPIADO   evals/manifest-r4b.md
ec4f24ab178390bd178ab9aa1191744ee04cbdd8941ceccfebb5c9171e778bd3    7364 NAO_COPIADO   evals/painel/juiz-1.md
9c3a0726ab4c787a15310d5065c48111bb67bf533efa27c8846069bf589993ef    9822 NAO_COPIADO   evals/painel/juiz-2.md
4c2501696bb3c9471d84588a585795212653a22bb66cb743907a57c9cdd3b000    7246 NAO_COPIADO   evals/painel/juiz-3.md
200b14dd56e0c0e616f47baf578b20df52a8a39d9a15faee7a9a52935108c1b2   17716 NAO_COPIADO   evals/placar-baseline.md
75f8d1ca27907ef7a8f04ef8e4c6b2dd25744f5608013b83256954c5b53ce301    1465 NAO_COPIADO   evals/placar-comite-r1.md
ca1f7e2170c74f91e64fd0566e93a49f5bc81d8fd68bdc68bf2f2684ce28109c    1476 NAO_COPIADO   evals/placar-comite-r2.md
15aa4335d8a7bb7c10a094919b8a5794f2eeaccb5de060849852fb13c50bfd20    1048 NAO_COPIADO   evals/placar-comite-r3.md
2717e7d3756489f9cfbd34690739fcebdad851b2aae2caedc3b16665534a4538     889 NAO_COPIADO   evals/placar-comite-r4.md
60a2034d94c87cbf3d834d06a6d4b79ab963554fc1310c5ccdf6cc921edc43a6    1602 NAO_COPIADO   evals/placar-painel-r1.md
062aa67a8b88855214d66b6b9649142fdd463ff9c8ac3750dc7752ca52518c17    2668 NAO_COPIADO   evals/placar-pos-skill.md
ec2332120cab14d17a4f12fa2d862a9243517672fc41dcab5415d00f465e39ca   17175 NAO_COPIADO   evals/placar-pos-skill-r2.md
84457e9dba8aa7fd6d6fdf34f1b77664ec4030743c363cbf8bc97df9aace3748    6135 NAO_COPIADO   evals/pos-skill/outputs-1-3.md
c1c54c0103ab7f721ce9d35f5d8fe189f8d179cecd5c28cda343631414dfb9fd   13233 NAO_COPIADO   evals/pos-skill/outputs-4-7.md
fb50b969e162f963cb066702d8156eda6c6fc7d704d0e19a5c6ef63e99c2d9c2    3418 NAO_COPIADO   evals/pos-skill/outputs-8-10.md
d79aa1e66db2468d860726d2bd6e1cbbd9524f3bc65c54c5ff10616ca3f4153a   18717 NAO_COPIADO   evals/pos-skill-r2/output-case4-retest.md
e505377b11e2a06415e6c20083475aaa3d8370341b28b3116a8c9255f97623c8   13024 NAO_COPIADO   evals/pos-skill-r2/outputs-1-8.md
d9af94aacfc8928d0558e302463fa397b44a4479114e09154d5976421eb867b6   48685 NAO_COPIADO   evals/pos-skill-r2/outputs-1-8-fixtured.md
61c5b798ba2aa20ba3f5ee29dfc1e1c9664443724342177edce6c611431112bb    7305 NAO_COPIADO   evals/pos-skill-r2/outputs-9-15.md
4b2c8b648d53084f5e516213bb3ea85472118294ca7a1f10ee74e5254ede1a23   24119 NAO_COPIADO   evals/pos-skill-r2/outputs-9-15-fixtured.md
233b366c2ff937f882749846cf92ad661e47f30e081e3e52465244a9b043d845   12035 NAO_COPIADO   evals/pos-skill-r3/case4/artifact-capability-governance.json
3720e6681f00be31202232c6b0476f7ba86b053c0885ae58e00fced6348a7d6e   20960 NAO_COPIADO   evals/pos-skill-r3/case4/artifact-quality-risk.json
dfa29619f49fadf12500e4cf24fcd33b5620064917358250a56edc32bf7d3683    2343 NAO_COPIADO   evals/pos-skill-r3/case4/artifact-responsibility-ledger.json
725d8eda7269e988b00ca087c62204d63b76533220ae97224d339afc500f8027   36737 NAO_COPIADO   evals/pos-skill-r3/case4/artifact-test-cases-v3.json
733617a66fc85e6d709224b0aa02ffce5fa7180a20131c03b83fabefdd04f412   52425 NAO_COPIADO   evals/pos-skill-r3/case4/artifact-test-design.json
be881131906e9e93f418979334c6d65d9121439f65349d6759671eff5d76ba43    3761 NAO_COPIADO   evals/pos-skill-r3/case4/assignment.json
7488c2f9d5d45c466f2bdbda0b3d71751896eb9b8778d4c5cc0b3d396c0d60ea   10084 NAO_COPIADO   evals/pos-skill-r3/case4/management-result-case4.json
c40534fea2556dbd313e5b50faf8ba60d6f39c6807080fec3c26a18f199cf4ed    3665 NAO_COPIADO   evals/pos-skill-r3/case4/mission-quality-risk.json
7ca5ef85c53e4d08a575bc59990ab181d1e771c26adbdd1f15ccc8fe0b708217    4153 NAO_COPIADO   evals/pos-skill-r3/case4/mission-test-design.json
53eb99ae8ddf71b38bc14b4cc69a898d46156415623693e3ccaecc5e94694fd1    4359 NAO_COPIADO   evals/pos-skill-r3/case4/result-quality-risk.json
a72bf51c9770061b8a4f64fe1f525b59172751a0d9f40ce89510f9b82691294d    7320 NAO_COPIADO   evals/pos-skill-r3/case4/result-test-design.json
4c11ae4186baa024920f109b13d7facb5df7d3b70adc0d25702eebcee2d774ed   12689 NAO_COPIADO   evals/pos-skill-r3/outputs-cases-1-3-5-8.md
bb5e6a80dcd4f608c47d0afa9df845c15b8da2754665a3d3bcfca52ce246b082   11046 NAO_COPIADO   evals/pos-skill-r3/outputs-cases-9-15.md
0dcd00d1ba4370fa64d2c52494ad9eec618e4a2bbcf82bb72274bbf9751e3040    8570 NAO_COPIADO   evals/pos-skill-r3/outputs-retest-cases-1-5-7-11.md
2677d17b91640f9df9f86e0e8fe2e3d0a3d472eeefe4d32a01c7a0e65f3e9b77   13632 NAO_COPIADO   evals/pos-skill-r3/placar-forward-r3.md
5d59b49039663074e65e4a119256ca637ca3bc2a769b6d5edbc5015f26a1ebff   10518 NAO_COPIADO   evals/pos-skill-r3b/outputs-cases-1-8.md
5c47cdeb98fb115a17c3db8629fcbd1164d3ea8c9f2c268daebb44fe711accfc    6416 NAO_COPIADO   evals/pos-skill-r3b/outputs-cases-9-15.md
2716ef20e9d8b5919f1f7b5ff3eafc8ae8853255cde7b2eb6407ac998a9591be   11503 NAO_COPIADO   evals/pos-skill-r3b/placar-forward-r3b.md
83551a3ce10709e7390fb0124844008afdea15a12fb2ab24b94c451691306d10    8220 NAO_COPIADO   evals/pos-skill-r4/placar-case4-r4.md
a8a6a8e28c0392097a0c6f176f4f5be9ef0d52e3f14e9941fcd6e8793ad2e733    7329 NAO_COPIADO   evals/pos-skill-r4b/placar-case4-r4b.md
42f64b30f893d4b54e0c7f3cda5b66c219cda3d3575caabda5a14024a81c10f3    6515 NAO_COPIADO   evals/pos-skill-r5/outputs-cases-7-11.md
fe6432e1739d965d71708f4c53343209ee74e71599da81b443b2ff193011b7c5   24026 REESCRITO     references/contratos.md
0219de18732190dfc2a1d7dc371b44311e5f68d021545b74e126ee5364ad5822    6701 REESCRITO     references/modelo-operacional-do-time.md
85be39665dd3d43721e66d99aba3a79dc78f7e15615be54549f5ae70434a0954   35282 REESCRITO     references/qa-contracts-v3.schema.json
5b05772b2fd8850fca1821fa1d8e1f52bbe0031916ee0801be0525d292472359    8545 REESCRITO     references/rubrica-qa-usabilidade.md
d5f7ec5112a3de26df785890bb84edcb0aec1a59e3e9de4362f6dbc3c639569a   16731 REESCRITO     SKILL.md
```

## Integridade ao final

O validador recalcula este manifesto contra a origem. Qualquer arquivo ausente,
extra ou com hash divergente reprova a migração e impede a promoção.

## Concluído quando

Os 87 caminhos aparecem exatamente uma vez no manifesto, a origem continua
idêntica e nenhum artefato histórico é apresentado como prova da skill nova.

