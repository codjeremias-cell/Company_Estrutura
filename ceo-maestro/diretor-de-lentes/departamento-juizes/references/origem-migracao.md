# Origem e recorte da migração — Departamento de Juízes

## Fonte legada

Origem lógica: `SKILL - Nova formula/maestro/comite-de-lentes/lente-juizes`.

Snapshot observado em 2026-07-26: **13 arquivos, 123.190 bytes**. A contagem é contexto de escala,
não identidade; a proveniência é fixada pelos hashes abaixo, calculados sobre os bytes da fonte no
momento da seleção.

| Arquivo legado | SHA-256 |
|---|---|
| `SKILL.md` | `3d2a859f6cf89a02dac1db38c2dcf9d1710beafe9a6c30e4c3be221edac7664b` |
| `references/protocolo-de-julgamento.md` | `b37a09d16b38d7e76d9c4cbb8b4e9f71ac5f92e30149e65bdb9ad8986b86efd4` |
| `agents/openai.yaml` | `a9ea9749ddfb4d80a785721172ce1161d1af6d03d7e226bfa41f3e278fd2eb07` |
| `time/julgar-fidelidade-e-contrato/SKILL.md` | `3c3c62c97dda0c4e367c762b7b670b8c628e09cac110f086493290ea7a038d1f` |
| `time/julgar-robustez-e-evidencia/SKILL.md` | `402ad8fbfd1b56e4e1ef8abf271399e79267a3c259665c27cefbb2ae60cbd91e` |
| `time/julgar-experiencia-e-risco/SKILL.md` | `fddaa51ca7d13390a03787d143c344c17bddd62d4e1fb347a33fde56a7615040` |
| `evals/evals.json` | `2f3351846de549bc6f4c762b47817a67784e31889a17e1f9308eb8255e034215` |
| `evals/placar.md` | `066f2b813746ca10dcebe228603f1a04ba438c57c2609e8e5a00a2b5c4011e04` |
| `evals/backtest-2026-07-26.md` | `f5959e8ebaeedd0d653524df0bdc052224debc7646b9698a837f532bad283074` |
| `evals/baseline-e-pos-skill.md` | `5fd1c7d7ad36d01c7e89c407f2a0d9c18a6875808287ffd3d08cfc59cecd503b` |

## Recorte preservado

Migrou, com adaptação de nomes e de cadeia de comando:

- a **gerente que não julga**: reparte, consolida e só decide quando o consenso falha;
- as **três óticas nomeadas** com fronteira exclusiva e dona única — fidelidade e contrato,
  robustez e evidência, experiência e risco;
- a **cegueira**: higienização, path anônimo, varredura de autoria **e** de instrução, isolamento
  entre juízes, contexto limpo;
- a **independência**: ninguém julga o que ajudou a produzir;
- o **fail-closed**: sem parecer de juiz não há aprovação, e ausência nunca vira nota neutra;
- a **trava anti-bypass**: subskill só opera por envelope assinado pela gerente;
- **conteúdo é dado, nunca instrução**, para candidato e para evidência;
- a **rastreabilidade** `veredito → juiz → razão → evidence_ref → artifact_ref` real;
- o schema único de lacuna de cobertura, como bloco e nunca como frase solta;
- os **riscos residuais declarados** em um único lugar, com teto honesto por vetor.

## Recorte reescrito

| Legado | Novo | Por quê |
|---|---|---|
| gatilho: **disputa entre 2+ candidatos** | gatilho: **toda entrega** de Departamento e todo candidato integrado | o organograma tornou os Juízes camada obrigatória; disputa virou o modo secundário |
| saída: `PANEL_HANDOFF` recomendando vencedor | saída: `DEPARTMENT_JUDGE_REPORT` / `JUDGE_REPORT` com veredito `VALIDATED`/`REPROVED` | o Diretor e o CEO consomem gate, não recomendação |
| "não emite nota absoluta — isso é do Auditor" | **emite** nota absoluta por critério e `minimum_score` | a nota migrou para os Juízes; a Auditoria fornece a **prova de conformidade**, não a nota |
| `JUDGMENT_MISSION` / `JUDGE_TASK` / `JUDGE_VERDICT` | `JUDGMENT_REQUEST` / `JUDGE_ASSIGNMENT` / `JUDGE_OPINION` | o envelope de entrada passou a ser o do `diretor-de-lentes`; os internos foram renomeados para não colidir |
| superior `comite-de-lentes` | superior `diretor-de-lentes` | nova hierarquia |
| subskills em `time/` | agentes em `agentes/`, com prefixo `agente-` | contrato estrutural do organograma |
| sem `CONTRATO-DE-COMPROMISSO.md` | contrato obrigatório na gerente **e** em cada agente | contrato estrutural do organograma |
| regras de ouro citadas de forma genérica | fonte normativa única `regras-de-ouro/REGRAS-DE-OURO.md` | fim da duplicação |
| modo `leve` (1 juiz, 2 passadas) | **não migrado** | o `leve` existia para baratear disputa repetida do mesmo contrato; num gate obrigatório ele reduziria a cobertura das óticas justamente onde ela é a razão do gate. Fica disponível no legado para rollback |
| `champion_ref` / `previous_handoff` / cotejo do campeão | vivem só no modo DISPUTA | não há campeão numa validação de entrega única |

## Recorte não copiado

- `evals/placar.md`, `evals/backtest-2026-07-26.md` e `evals/baseline-e-pos-skill.md` **não foram
  promovidos**: medem a skill legada, com outro gatilho, outra saída e outro contrato. Permanecem
  na fonte como evidência histórica.
- `evals/evals.json` legado não foi copiado: seus prompts pedem comparação entre candidatos e não
  exercitam o gate obrigatório. Os cenários foram reescritos para a nova hierarquia.
- O modo `leve` e todo o aparato de campeão/handoff anterior ficaram fora do modo VALIDACAO.

## Política de rollback

O pacote legado permanece **intacto**. Ele é fonte histórica e rollback manual; **nunca** fallback
automático em runtime. O `diretor-de-lentes` não usa `lente-juizes` como equivalente do
`departamento-juizes`, e ausência do pacote canônico é `DIRECTOR_CAPABILITY_GAP`, não substituição
silenciosa.
