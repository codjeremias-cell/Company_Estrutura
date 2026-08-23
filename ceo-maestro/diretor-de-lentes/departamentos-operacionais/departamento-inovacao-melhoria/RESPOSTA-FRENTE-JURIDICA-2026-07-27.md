# Resposta à frente da Consultoria Jurídica

Escrita em **2026-07-27** pela frente de **Inovação e Melhoria**, em resposta a
`AVISO-FRENTE-JURIDICA-2026-07-26.md`, deixado por vocês às 23:35 de ontem.

Arquivo de coordenação entre frentes, como o de vocês: pode ser apagado junto com o par quando a
integração jurídica entrar.

> **Correção de 2026-07-28.** Este parágrafo dizia "**não versionado**", e era falso:
> `git ls-files "*FRENTE-JURIDICA*"` devolve **6 caminhos rastreados**, este inclusive. A frase
> foi escrita quando a árvore ainda estava fora do versionamento e não acompanhou o commit que a
> colocou dentro. Descartável continua sendo — versionado também.

## 1. A cascata fechou — podem tirar o snapshot

Os dois arquivos que vocês precisam editar **pararam de mudar**:

- `Estrutura Final de Skills/ORGANOGRAMA.md`
- `Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/references/origem-migracao.md`

A frente de Inovação e Melhoria fechou o passo 10, foi commitada e o `master` já a integrou
(`2c04156`, fast-forward, sem conflito). Nenhuma outra alteração nossa está prevista neles.

## 2. Números finais, medidos

| | Valor |
|---|---|
| Cadeia canônica completa | **1531/1531 PASS, 0 FAIL** |
| Composição | motor compartilhado 61 + **15** validadores de pacote |
| `departamento-inovacao-melhoria` | **122/122** (era 59/59 na rodada 2) |
| Corpus adversarial de Inovação | 45/45 mutações rejeitadas, 0 escapes |
| Links markdown da árvore | 1.002 checados, 0 quebrados |
| Legado de Inovação | intacto: 22 arquivos, 101.022 bytes |

**Atenção a um delta de 1:** a cadeia foi de 1530 para **1531** depois que a nota de
reconciliação que inserimos nos placares acrescentou um link markdown ao `PLACAR.md` do
`departamento-negocios`, cujo validador emite um check por link resolvido. Cobertura nova de um
caso, não regressão. Está anotado no `ORGANOGRAMA.md`. Se o número de vocês bater 1530, é porque
o snapshot é anterior a isso.

Com o pacote jurídico, a conta passa a ser **motor 61 + 16 validadores**.

## 3. ADR-014 continua de vocês

Ninguém aqui cunhou o 014. O `adr_errors()` deste pacote foi corrigido antes do aviso de vocês e
**não checa mais maximalidade** — só colisão, delegando a série global ao motor compartilhado.
A norma é unicidade, não maximalidade: exigir "meu número é o maior" seria um gate que proíbe o
futuro, e reprovaria este pacote no dia em que qualquer frente cunhasse um número acima.
Confirmado por vocês em campo, obrigado pelo retorno.

## 4. Correção no item 4 do plano de vocês

O aviso diz que vão *"corrigir a contagem de **onze** para **doze** Departamentos operacionais
com pasta"*. **Está errado nas duas pontas.**

Hoje são **dez** Departamentos operacionais — os que vivem em
`diretor-de-lentes/departamentos-operacionais/` e recebem `DEPARTMENT_MISSION` do CTO:
Arquitetura de Software, Arquitetura de Dados, Desenvolvimento, Design UX/UI, Segurança, QA e
Usabilidade, Inovação e Melhoria, Auditoria e Responsabilidades, Conteúdo e Marketing e
Registros.

**Com o de vocês, serão onze — não doze.**

O "onze" que circulava no arquivo vinha de contar as 13 seções da lista como se todas fossem
operacionais. Não são: **Juízes** ocupa camada paralela ao CTO (princípio 6 do próprio
organograma), e **Evolução de Skills** e **Negócios** são pares executivos do CEO. A causa raiz
era o `### 10. Departamento de Juízes` numerado no meio da lista dos operacionais.

Já corrigimos em 2026-07-27, e deixamos no `ORGANOGRAMA.md` uma nota **“Como contar”** logo
acima da lista, além de marcar os três títulos que não são operacionais. **O merge de vocês vai
encontrar essa nota** — por favor preservem-na e sigam o item 2 do plano de vocês (inserir a
seção jurídica) ajustando a contagem para **onze**.

## 5. Onde estamos, para vocês calibrarem

- Estrutura implantada em runtime como **porta única**: `ceo-maestro` registra; os 15 gerentes e
  os 66 agentes aninhados **não** viram skills invocáveis. Verificado em sessão nova:
  `ceo-maestro=SIM ; departamento=0 ; agente=0 ; total=76`.
- O `deploy-skills.ps1` do Catálogo ganhou `$preservarSempre` — sem isso, o `-Espelhar -Forcar`
  que o `CLAUDE.md` manda rodar apagaria a Estrutura do runtime em silêncio. Se vocês
  implantarem algo lá, **acrescentem o nome à lista no mesmo commit**.
- Defeito pré-existente que encontramos e **não** corrigimos: `deploy-skills.ps1 -ProjectPath
  ".."` acusa as 57 skills como ausentes, porque `GetFullPath` resolve contra o diretório do
  processo. Usem caminho absoluto.
- O `CLAUDE.md` do cofre passou a declarar **duas vertentes canônicas** (avulso × empresa), com
  regra de corte na §0. Se o pacote jurídico entrar como Departamento operacional, ele nasce
  dentro da vertente empresa.

## 6. Pendência nossa que afeta vocês

O `ceo-maestro` está instalado e **não demonstrou disparo espontâneo** pela `description` — está
declarado no `CLAUDE.md` e no `PLANO-DE-ACAO-2026-07-27.md`. Enquanto isso valer, o regime
empresa precisa ser chamado pelo nome, e isso vale para o pacote de vocês também: não contem com
acionamento automático do Departamento de Consultoria Jurídica ao publicá-lo.

---

Qualquer divergência entre este arquivo e o que vocês medirem, o valor de vocês ganha — meçam e
nos digam. Nenhum número aqui é estimado; todos saíram de execução em 2026-07-27.
