# Origem e recorte da migração — Departamento de Registros

Prestação de contas do recorte, na forma do passo 3 do
[GUIA-DE-EXPANSAO-E-MIGRACAO.md](../../../../../GUIA-DE-EXPANSAO-E-MIGRACAO.md). Governança aplicável
em [regras-de-ouro/REGRAS-DE-OURO.md](../../../../../regras-de-ouro/REGRAS-DE-OURO.md) — referenciada,
nunca copiada. Posição do pacote em [ORGANOGRAMA.md](../../../../../ORGANOGRAMA.md), item 10.

## Fonte legada

Origem lógica: `SKILL - Nova formula/maestro/comite-de-lentes/orquestrador-registros`.

Snapshot observado em **2026-07-26: 154 arquivos, 1.320.436 bytes**. A contagem e os bytes são
**contexto de escala, não identidade**: os filhos legados podem evoluir em paralelo. O que fixa a
proveniência são os hashes abaixo, calculados sobre os bytes da fonte **antes de qualquer escrita
deste pacote**.

### Receita do manifesto — chave e ordenação fixadas

O manifesto é a concatenação de **154 linhas** no formato `sha256␠␠caminho`, e a receita precisa
fixar, sem deixar nada ao ambiente:

| Elemento | Valor fixado |
|---|---|
| Chave de ordenação | o **caminho relativo**, nunca a linha inteira (a linha começa pelo hash e ordenaria por hash) |
| Comparador | **ordinal**, byte a byte — nunca `Sort-Object` nu, que é insensível a caixa e dependente de cultura |
| Separador entre hash e caminho | **dois espaços** |
| Separador de diretório no caminho | `/`, com o prefixo da raiz removido |
| Terminador de linha | `\n` (LF) em **todas** as linhas, inclusive a última |
| Codificação | UTF-8 **sem BOM** |

Reprodução em PowerShell, a partir da raiz do cofre — **executada em 2026-07-26**:

```powershell
$src = "SKILL - Nova formula\maestro\comite-de-lentes\orquestrador-registros"
$raiz = (Resolve-Path -LiteralPath $src).Path
$mapa = @{}
Get-ChildItem -LiteralPath $raiz -Recurse -File | ForEach-Object {
  $rel = $_.FullName.Substring($raiz.Length + 1).Replace('\','/')
  $mapa[$rel] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower()
}
$caminhos = [string[]]@($mapa.Keys)
[Array]::Sort($caminhos, [System.StringComparer]::Ordinal)   # chave = caminho, comparador ordinal
$sb = New-Object System.Text.StringBuilder
foreach ($c in $caminhos) { [void]$sb.Append($mapa[$c]).Append('  ').Append($c).Append("`n") }
$bytes = (New-Object System.Text.UTF8Encoding $false).GetBytes($sb.ToString())
$sha = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
([System.BitConverter]::ToString($sha).Replace('-','').ToLower())
```

Equivalente em Python, para conferência independente do runtime — **executado em 2026-07-26**, com
resultado idêntico ao do PowerShell:

```python
import hashlib, os
SRC = r"SKILL - Nova formula\maestro\comite-de-lentes\orquestrador-registros"
linhas = {}
for raiz, _, arquivos in os.walk(SRC):
    for nome in arquivos:
        p = os.path.join(raiz, nome)
        rel = os.path.relpath(p, SRC).replace("\\", "/")
        linhas[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
manifesto = "".join(f"{linhas[c]}  {c}\n" for c in sorted(linhas))
print(hashlib.sha256(manifesto.encode("utf-8")).hexdigest())
```

**Digest do manifesto:**
`2ddcc7f987bf539c17d44b75733770bd97ef1bffeef1d82a694de10c8f385df3`.
Uma única linha que mude, muda este digest; as tabelas abaixo dizem **qual**.

> **O valor publicado antes — `7a6809ac…` — foi retirado por não ser reproduzível.** A receita
> anterior mandava `Sort-Object` sobre a **linha inteira** já formatada (que começa pelo hash) e a
> prosa dizia "ordenadas por caminho": duas ordenações diferentes no mesmo parágrafo, a segunda sob um
> comparador insensível a caixa e dependente de cultura. Doze variantes foram testadas — ordem por
> caminho e por linha, sensível e insensível a caixa, `LF` e `CRLF`, com e sem quebra final — e
> **nenhuma** reproduziu `7a6809ac…`. Não é sinal de fonte alterada: os **154 hashes individuais das
> tabelas abaixo foram recalculados em 2026-07-26 e batem um a um**, com os mesmos 154 arquivos e
> 1.320.436 bytes. Era a receita que estava ambígua. Número que ninguém consegue conferir não é
> evidência — é decoração —, e por isso ele foi substituído por um valor com receita determinística e
> duas implementações que concordam.

### Hashes — pacote legado, fora de `evals/` (7 arquivos)

| Arquivo legado | SHA-256 |
|---|---|
| `agents/openai.yaml` | `e8422e93bd5a66ab467a3803707b5fba2d0409d22a75095ac071ab5d0884fdde` |
| `references/contratos.md` | `4633b2d36cd61c3fcd38fd22336b38d0e8ab2c8aece7b565858927b8297bf2bd` |
| `references/fundamentos-do-dominio.md` | `435182c7e8a0daa8ed86505546f6e54ecf85d0f1bdf0cb4f1edfd383fe1e6f07` |
| `references/modelo-operacional-do-time.md` | `f8e146a77a86c629f8f52ab3d269ab2ca9c12d502c98b4a27174925deae97eb1` |
| `references/perfil-cofre-jeremias.md` | `95789e47bad900746aae6bbbfbe4951efbd89fcc1c6c8d63433daa225d9b9e7c` |
| `references/rubrica-registros.md` | `93335ea67fffeec1bad587db298afde0478dd8fbf8df7a15d00050967b364cac` |
| `SKILL.md` | `2da51267e34261dfd3c70b421562bff99a622d832934a1181a4064b2b7e5537f` |

### Hashes — `evals/` (147 arquivos)

| Arquivo legado | SHA-256 |
|---|---|
| `evals/baseline-sem-skill.md` | `6e3a58cd79ae48d82dc0fad10c798594e3b493da50390ad0b123b269b4b15651` |
| `evals/baseline-sem-skill-r2.md` | `6b74dfa79aa59da80fa18f13d68179c60605ab0e67787e5a1308d0cb33bf641c` |
| `evals/candidatos/a/agents/openai.yaml` | `5bc5b9eeb91b648ff5cd7b0c6515c51a34e598f4dd0dd84acc3a204902653c9c` |
| `evals/candidatos/a/references/contratos.md` | `4ca79360d26523ba1aaa0e88c5f056f3e3fed7cb121beab43eefd71fa3d54922` |
| `evals/candidatos/a/references/fundamentos-do-dominio.md` | `dc93ecef894ab81926fb660c323a4b5854c51e107c144fab68dc83141d24b11a` |
| `evals/candidatos/a/references/modelo-operacional-do-time.md` | `1271cd0bf448604ae067ff4b3edb405a1d3a966e9a9939012ca50fc044d1a7f6` |
| `evals/candidatos/a/references/rubrica-registros.md` | `a750e91aa2968da3837c5fe357abba8eaba4aecdf33ba99cd0a66dae14983aba` |
| `evals/candidatos/a/SKILL.md` | `cf4a95120ea2283d26c6b6bb9dadb88583a218afef773a3fbcdf109b08d938ab` |
| `evals/candidatos/b/agents/openai.yaml` | `ba3e9873705916c333d0b2c050554b9d508f6842484c5f0428b8539551eb97a0` |
| `evals/candidatos/b/references/contratos.md` | `3d6edba65c3669c203991bb85dcaf9baeea12c8a0cffdb514a7c370544f1e10e` |
| `evals/candidatos/b/references/fundamentos-do-dominio.md` | `0683d658af32e7debcd249a8a899928c406b25b533a8f991b9200c33177062ea` |
| `evals/candidatos/b/references/modelo-operacional-do-time.md` | `5ab131e07111284bd23a94124a5063c37d865b98b7fd38680f70fc6edb0a2009` |
| `evals/candidatos/b/references/rubrica-registros.md` | `619b969d5a7716a6652bab094767b4e3c83b0d8cc4729237a70e001cc2873fe9` |
| `evals/candidatos/b/SKILL.md` | `b6beb0b07fc823be6d9c0bdff622ebe275653f3f046533de30cb01e77608661f` |
| `evals/comite/rodada-1/arquiteto-dados.md` | `8e7c68580f274265ce2a36c4fea77ded933d56b21ba42756d720a50f20c26eb7` |
| `evals/comite/rodada-1/arquiteto-software.md` | `54827f304a1dd33026565c1ad8a185a58db9d1a157895717b72aee2db0ded3fe` |
| `evals/comite/rodada-1/designer-ux-ui.md` | `0bb8a2fabed53a6291690dd610b383a846bd6f272a16ef67cfbac13465285d76` |
| `evals/comite/rodada-1/dev-senior.md` | `7dedb5bc47ed35ed56cb9cf2e862f78164e030e5178a94299720b6aff9cfc6d0` |
| `evals/comite/rodada-1/especialista-seguranca.md` | `a20ed63a5fcaa7abd9af877f11ed58064fc875e47d66aa2f099b7430d2ed79a4` |
| `evals/comite/rodada-1/qa-usabilidade.md` | `0bd4fd403df1a376efa38b5cd18dd2a5d82510bec402afcba784dabe9e99deb8` |
| `evals/comite/rodada-2/arquiteto-dados.md` | `30d984e8f2bbcd6d394e8f334478b366df1b6c209998653759842916392c9908` |
| `evals/comite/rodada-2/arquiteto-software.md` | `9347d1b33b561220bc9c7ab21e8b359f09b57bc2b99c5cf3e1c08097375239a7` |
| `evals/comite/rodada-2/designer-ux-ui.md` | `434c55f1390903c0557366a6425e8ba8b3b2698b2611f3231a6fbfc1639f05ca` |
| `evals/comite/rodada-2/dev-senior.md` | `57d67d1c9f76ae346ab10c81e9ffa82e96db494ab43ef29e979878ed48b686f3` |
| `evals/comite/rodada-2/especialista-seguranca.md` | `a4bcfc218a147b6a8d4e0de7069412cfff9a473dd65a4bac8e6b5f27fa93307e` |
| `evals/comite/rodada-2/inovacao-melhorias.md` | `9a060369f9783083154fdd585738f35138d53e343250702ecf4cd191d4711104` |
| `evals/comite/rodada-2/qa-usabilidade.md` | `4da2351d9c59dd62623de73151cbe0a3687849496c7c6a3bdd94e3dfb15fc762` |
| `evals/evals.json` | `b10d6e011bfeced1897ea05dfa9ae3bbd1fffdc6dad88c308129c424f62146fa` |
| `evals/fixtures/_tools/arvore-digest.py` | `e2f2cfb251407f62fa2520094fe0bd771566439744cd8dc22f0118fefd358d06` |
| `evals/fixtures/_tools/checar-fixtures.py` | `5bf1c2796a11fe38a22c449d6f27b302dc3ee3bfb9f8ed336fd01911dae7812d` |
| `evals/fixtures/c01/target/decisoes/ADR-0007-formato-do-relatorio-mensal.md` | `529d4178154f6159b88f4fafbdd725fdcd8cd4939ce4dbf06b6131f3519f17a2` |
| `evals/fixtures/c01/target/estado/estado.json` | `e6abc54b079f8d229dd3d77c8053c05f5c174a6465d721a90f47ea78e3d8ce8d` |
| `evals/fixtures/c01/target/estado/TAREFAS.md` | `8ba60515ac7e85643614e024ecab88c25fcbaf1ac2219dee9c8f1ebdd4ff4ef3` |
| `evals/fixtures/c01/target/indices/Indice-do-Projeto.md` | `ecdfadf70d150963642a6bdf36f72f6ce137dec02e91df05c26de7f67734d4a1` |
| `evals/fixtures/c01/target/memoria/MEMORIA-PROJETO.md` | `41b974602b9130b9544e9ef0de2e120e7fce776f8d6aaff41c59d013f8ae8e56` |
| `evals/fixtures/c02/target/decisoes/ADR-0003-padrao-de-logging.md` | `eea038e465a7cbd6bcb84cc200b03d94ab3e06554a967eba2d80e5a3bbbfbd36` |
| `evals/fixtures/c02/target/estado/estado.json` | `dd33b4bb01b10b78162a125143286ee947d940cc6f2b4aa5c1671f7e7b282c7c` |
| `evals/fixtures/c02/target/estado/TAREFAS.md` | `b618c8c6ab3ed393f8d67bfc4ac4e78aa42604dfd83107f29b8cd71c2ea6b469` |
| `evals/fixtures/c02/target/indices/Indice-do-Projeto.md` | `e70a67559cffa3942ce5c84e54b6b60fd175d5a05894f921bd79e88aa677b200` |
| `evals/fixtures/c02/target/memoria/MEMORIA-PROJETO.md` | `41b974602b9130b9544e9ef0de2e120e7fce776f8d6aaff41c59d013f8ae8e56` |
| `evals/fixtures/c03/target/decisoes/ADR-0002-limite-de-upload.md` | `db1791985f5bc00e777a9588d773775dce8edbef15894e7826f29bde6d25575d` |
| `evals/fixtures/c03/target/estado/estado.json` | `1fbbd16dc6c25022123f1ab9e52afb4efb51274b01e3c0dd1ec0eaea6183e358` |
| `evals/fixtures/c03/target/estado/TAREFAS.md` | `563ec8967ce7399ce473ea70fd15d5c274780ae7b890caf8da1faab042da7c06` |
| `evals/fixtures/c03/target/ideias/README.md` | `a19dc26059bbd9de4abd106f166b09bb40d55a92b7898798cde816044f7bc6ac` |
| `evals/fixtures/c03/target/memoria/MEMORIA-PROJETO.md` | `41b974602b9130b9544e9ef0de2e120e7fce776f8d6aaff41c59d013f8ae8e56` |
| `evals/fixtures/c03/target/src/upload/handler.js` | `3d81b040706aaeef43df044be2e86c08bb3b1f100a1c2c4c8349a23c034e4c50` |
| `evals/fixtures/c04/target/decisoes/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `evals/fixtures/c04/target/estado/estado.json` | `68932123573c9f2ff51761ed1155236503c71b8723d39218b886886c245b3d5f` |
| `evals/fixtures/c04/target/estado/TAREFAS.md` | `b0e037c6e15c6a2e4f9596d4b020b0a031c70543636caba9f28e6eed6ee1db8d` |
| `evals/fixtures/c04/target/memoria/MEMORIA-PROJETO.md` | `41b974602b9130b9544e9ef0de2e120e7fce776f8d6aaff41c59d013f8ae8e56` |
| `evals/fixtures/c04/target/src/api/rotas.js` | `723508d03ef14ed4eda64b92a871cf509711dfbf478d2b3d4f705389bb0ad406` |
| `evals/fixtures/c04/target/src/auth/login.js` | `cadd247ce3050e1ee367147d4b921f40cbc0598f0b73382cfd28578f715afe73` |
| `evals/fixtures/c05/target/estado/estado.json` | `68932123573c9f2ff51761ed1155236503c71b8723d39218b886886c245b3d5f` |
| `evals/fixtures/c05/target/estado/TAREFAS.md` | `b0e037c6e15c6a2e4f9596d4b020b0a031c70543636caba9f28e6eed6ee1db8d` |
| `evals/fixtures/c05/target/ideias/README.md` | `46fb4442416b3441af3c686073f0c2d4d367e2341eb741dca1e3a9a1a2ccf1c8` |
| `evals/fixtures/c05/target/memoria/MEMORIA-PROJETO.md` | `41b974602b9130b9544e9ef0de2e120e7fce776f8d6aaff41c59d013f8ae8e56` |
| `evals/fixtures/c06/assignment.json` | `c75c1136a44e3f9d445142742583768a2dc9399f1572ac06ce08316c8d7726d8` |
| `evals/fixtures/c06/target/projetos/vendarium/decisoes/ADR-0001-cache-em-memoria.md` | `8416231a6bf015eab72a29a823ddea252ff83d0d030538218eb491651b6309fa` |
| `evals/fixtures/c06/target/projetos/vendarium/estado/estado.json` | `68932123573c9f2ff51761ed1155236503c71b8723d39218b886886c245b3d5f` |
| `evals/fixtures/c06/target/projetos/vendarium/memoria/MEMORIA-PROJETO.md` | `41b974602b9130b9544e9ef0de2e120e7fce776f8d6aaff41c59d013f8ae8e56` |
| `evals/fixtures/c07/assignment.json` | `bdde09bcc686b54a6b8fcd4f4ca9eb240601ff2efe1d80802691e6f38b8101ed` |
| `evals/fixtures/c07/pacote/registros_management_result.json` | `7adf10bfeb113c9081fcc9d7ef3630fee3220010dcf4c4b7d5ef3ea369abee85` |
| `evals/fixtures/c07/target/decisoes/ADR-0011-particionamento-do-relatorio.md` | `5c69f3182d405ece507ef79a847befe2bc4366a61046210a1058866ebeeece79` |
| `evals/fixtures/c07/target/indices/Indice-de-Registros.md` | `666bc1dbc4abe98e06811f617869d9b349906399e5369339669dba5809d9de2e` |
| `evals/fixtures/c07/target/memoria/MEMORIA-PROJETO.md` | `3896f4345ad9c8c7b4e551daad436f9c2f4ae666fe660de08b5a365eee795a6b` |
| `evals/fixtures/c08/assignment.json` | `d552ef17cc1ff0b2a04e96ba6203571491cf622491df23fd6c2946f6769e4cef` |
| `evals/fixtures/c08/target/acervo/aprendizagem/Corvo.md` | `fc81866f29cb1706f65059b86acaafa2cf2a3e8b3933ce5e0b1fa046e953592b` |
| `evals/fixtures/c08/target/acervo/indice-publico.md` | `1d75d0e8ff0f345262a6bb91d8f7715e7add036c3fb64d0ba2c5766b673885e6` |
| `evals/fixtures/c08/target/estado/estado.json` | `68932123573c9f2ff51761ed1155236503c71b8723d39218b886886c245b3d5f` |
| `evals/fixtures/c08/target/estado/TAREFAS.md` | `b0e037c6e15c6a2e4f9596d4b020b0a031c70543636caba9f28e6eed6ee1db8d` |
| `evals/fixtures/c08/target/memoria/MEMORIA-PROJETO.md` | `41b974602b9130b9544e9ef0de2e120e7fce776f8d6aaff41c59d013f8ae8e56` |
| `evals/fixtures/c09/assignment.json` | `44dc4ce78384bde1a74f6f375e007e7e204927718e996690e0c813ba93e11729` |
| `evals/fixtures/c09/target/aprendizagem/Indice-de-Aprendizagem.md` | `44928af1b71ada3c42d158fa2d505699907240ed731992de0d0b4b87a9f26299` |
| `evals/fixtures/c09/target/indices/Base-de-Conhecimento.md` | `d8a905edba5722c46f4c47df8ee477eebd334f89608b7d7b335733acf4ea2633` |
| `evals/fixtures/c09/target/indices/Mapa-de-Projetos.md` | `d8ba0241c004a578872cceb47bcf477f2deb78ed32f908227f33163b531f9a80` |
| `evals/fixtures/c09/target/projetos/ferrolho/memoria/MEMORIA-PROJETO.md` | `b5edf5babf168ae35c25ef9aaa3c8e5efe37e822d995c39ec54bac6bf15b63ab` |
| `evals/fixtures/c09/target/projetos/pomar/memoria/MEMORIA-PROJETO.md` | `8ee11524f27ba500bb07ee1cd43bc8e8898c53be56694ff1d984de572b9b2ae7` |
| `evals/fixtures/c10/target/docs/Vendarium-Instalacao.md` | `c4519abc577aa075df010072b470792d3d06f0f541b7b95fcc6a45890e576d3e` |
| `evals/fixtures/c10/target/docs/Vendarium-Manual.md` | `de48988999dc81a101bc14d3002d6d1c8c111d417eb065959bca13a2c788942f` |
| `evals/fixtures/c10/target/estado/estado.json` | `68932123573c9f2ff51761ed1155236503c71b8723d39218b886886c245b3d5f` |
| `evals/fixtures/c10/target/estado/TAREFAS.md` | `b0e037c6e15c6a2e4f9596d4b020b0a031c70543636caba9f28e6eed6ee1db8d` |
| `evals/fixtures/c10/target/guias/Guia-de-Corte-Mensal.md` | `3f926314982c51a15cd420004acc361fe3002ca0f1023d6c95609dc08097eadc` |
| `evals/fixtures/c10/target/guias/Guia-de-Reprocessamento.md` | `c96b0c50531d87098aaed183e68b2be3f0a558126b2f1b44bed7b7db5105bc05` |
| `evals/fixtures/c10/target/guias/Indice-de-Guias.md` | `26692be70bae51d308374b51b073eb6152ef09ffc8b876bddd38522945920b57` |
| `evals/fixtures/c10/target/memoria/MEMORIA-PROJETO.md` | `41b974602b9130b9544e9ef0de2e120e7fce776f8d6aaff41c59d013f8ae8e56` |
| `evals/fixtures/c11/assignment.json` | `5f65de4d547085bf220ed7407ca33c4aea67b6fbad68897b8c8a7e3048eba06e` |
| `evals/fixtures/c11/target/decisoes/ADR-0001-motor-de-banco.md` | `4381b24f93b257a0a0979ea608870ebf71f60979584c098e93e06ff47ba08fbd` |
| `evals/fixtures/c11/target/estado/estado.json` | `68932123573c9f2ff51761ed1155236503c71b8723d39218b886886c245b3d5f` |
| `evals/fixtures/c11/target/estado/TAREFAS.md` | `b0e037c6e15c6a2e4f9596d4b020b0a031c70543636caba9f28e6eed6ee1db8d` |
| `evals/fixtures/c11/target/memoria/MEMORIA-PROJETO.md` | `41b974602b9130b9544e9ef0de2e120e7fce776f8d6aaff41c59d013f8ae8e56` |
| `evals/fixtures/c12/target/decisoes/ADR-0004-fila-de-envio.md` | `c67d90e4c746d196b1eea85c212a44f6d81e3c0e19b7641875d36fbe4b98c440` |
| `evals/fixtures/c12/target/estado/estado.json` | `68932123573c9f2ff51761ed1155236503c71b8723d39218b886886c245b3d5f` |
| `evals/fixtures/c12/target/estado/TAREFAS.md` | `b0e037c6e15c6a2e4f9596d4b020b0a031c70543636caba9f28e6eed6ee1db8d` |
| `evals/fixtures/c12/target/indices/Indice-do-Projeto.md` | `07e4b510f00a1909b1b72ba0d461bb07a6cc321520cc589209d0ef8b8030415d` |
| `evals/fixtures/c12/target/memoria/MEMORIA-PROJETO.md` | `41b974602b9130b9544e9ef0de2e120e7fce776f8d6aaff41c59d013f8ae8e56` |
| `evals/fixtures/c13/assignment.json` | `07c4a978dbcbf693afb14a7b0f3c638d6c7b849572d2e1c82838b568cc933503` |
| `evals/fixtures/c13/pacote/registros_management_result.json` | `6b587c061a861ea6556c57f817bbcfdceb56ab36d7eeb2fa5eb56573bcd76416` |
| `evals/fixtures/c14/assignment.json` | `7afa0d13853078befb0b828db863e75132cfb1cacd749adc15718b147abd95ce` |
| `evals/fixtures/c14/pacote/registros_management_result.json` | `d344d5eebb6fbff55df5c0d3ecabccd8c698b56abb62967f9007ed12c5216c0b` |
| `evals/fixtures/c14/target/decisoes/ADR-0002-particao-do-corte.md` | `429c402d0b30b7dac76f95c2ba9053770a1af8b8860b6937946bb69c03aaa69e` |
| `evals/fixtures/c14/target/estado/estado.json` | `53489470bd9222c4638489a56ed13a933fb52661b0aaebcfa94c3200b5ea9041` |
| `evals/fixtures/c14/target/estado/TAREFAS.md` | `d92122689da6bf18bb264259978c587e9ebbcd36ea9d7e696020161d3a353e48` |
| `evals/fixtures/c14/target/indices/Indice-do-Projeto.md` | `e5d85779d96c6d1b2feadab1eed6a6b48aa60945485b3d8c230f6ab4ddc1a20c` |
| `evals/fixtures/c15/assignment.json` | `61631dbe73f081c6943d79feeef760526191a0162d4d2128a8be6b5582b7ad20` |
| `evals/fixtures/c15/pacote/registros_management_result.json` | `8c24af9223f84b8a8a712c9f9b84fc21ef6ba4d9c888d896eb46099e0d17d1d7` |
| `evals/fixtures/c15/target/decisoes/ADR-0011-esquema-versionado-com-o-codigo.md` | `16b7035740808ccf579f87eb53c213b22dcefa75a9a86d1e6cea89a89eb171cb` |
| `evals/fixtures/c15/target/indices/Indice-do-Projeto.md` | `e6d4d61ac92cd89a314eae6f62b3a1473e95ada8117c37a0c480ca098f47b66b` |
| `evals/fixtures/c16/assignment.json` | `10d6eb809feded9226046b3930e517796d9fd5a4e444cf0c695a5e94578c8c97` |
| `evals/fixtures/c16/target/guias/Guia-de-Corte.md` | `09fbbdc8347e4ea9e0b7bdca8c9a3aeb9b3cbc1f713d6f42fdb20d9022d963cf` |
| `evals/fixtures/c16/target/guias/Indice-de-Guias.md` | `8e7afcd676dda7bb573d48cb2fc425f5ee714183a8a2336173ceaa1f5b5bc910` |
| `evals/fixtures/c16/target/indices/Indice-do-Projeto.md` | `996b6de05bc26bd6a9ad3cc51c60bcb1eaf4355f7b7e4bee20905e9a87f8e9aa` |
| `evals/fixtures/c17/assignment.json` | `ef03b1632c0b6367854f9c8cc89c27c13c0206555afa171901b26dcec02efe4f` |
| `evals/fixtures/c17/target/catalogo/README.md` | `7fe812ffd6e1eb7a5ae3112aa77de7041ae9f32ce4cc910022cce6f2a79d125e` |
| `evals/fixtures/c17/target/catalogo/skills/alfa/SKILL.md` | `17f1779322915eca4908b9491d2f068ab5180b1875d5b091eb0e1d122809873d` |
| `evals/fixtures/c17/target/catalogo/skills/beta/SKILL.md` | `bde865db59ddebc1dd2e8d9f0e2b47f140e13edc81b03313308be69e8130777f` |
| `evals/fixtures/c17/target/catalogo/skills/gama/SKILL.md` | `01f56bb366932c65f73a8d805c9c01d01984f8e30079f208e67e5a75f7069881` |
| `evals/fixtures/c17/target/publico/GUIA.md` | `056599e2c871dbb2b8b585606f4236e635010b5dcf245b1daa6b98a3ece78ea1` |
| `evals/fixtures/c17/target/publico/README.md` | `3181e65d59b668c4969d60ada8088be1ad2b3f9275f81928b47393f7878f8ae2` |
| `evals/fixtures/c18/assignment.json` | `d6ef631f584782dbb0d73b207a9571732d072d60ac9a424a89125764f3f215d7` |
| `evals/fixtures/c18/target/decisoes/ADR-0005-fila-do-coletor.md` | `c3f5349fad6d7a1c0aaa55d802075bd4bb0988cc973b532e5c74fb7e61517a80` |
| `evals/fixtures/c18/target/estado/estado.json` | `cedd6b11d0427b80cc9309c5186f15de714ec87419ed3aa0d4ec98563e8f60a1` |
| `evals/fixtures/c18/target/estado/TAREFAS.md` | `bfe9e3af4fc20cd21ce231c2597e393f33828aea7133544b85fa7b227033c439` |
| `evals/fixtures/MANIFESTO.json` | `a91373670071bb5bd234f8c7f1e2e147b4a5942c34239748dec72eaab824e16e` |
| `evals/forward-test/resultados.md` | `befdc374d20e8a4ec02667ec10886c2fc21411587c331df095361f68a20e4cba` |
| `evals/forward-test/resultados-r2.md` | `f0e48696092c3ad21572d621cc9702002bdf09424d21626eaed350d99624e499` |
| `evals/manifest-sha256.txt` | `bd5a1af040cdaefe2915923dc446f24ca872ed5c3b17259c24ec281ddf2eb135` |
| `evals/painel/juiz-1.md` | `c2d1e6e22759036da0c2be9a6f2c99a6fe046c635eeadcbcacf60841a8ff72ce` |
| `evals/painel/juiz-2.md` | `0a383857ac38467b0566ce538b63fccf07189169768b19d84e2cc24b39159ab3` |
| `evals/painel/juiz-3.md` | `3f7e103aeb041543d598f99181287e3c03a22f56414697b220d88b2b93a100f7` |
| `evals/piloto-r1/aderencia.md` | `557a986b4f821cd24685edc6dd3536b81372240c4f1479ee56ae6881a0905fbd` |
| `evals/piloto-r1/execucao.md` | `c0e76a3c5f901ae1c47ec8dd06bcf0ebbe57a10f6a4f3712ff3988a97facde07` |
| `evals/piloto-r1/git-diff.md` | `7c1e017635c80bcc501620cef2456769e70e0a9881840db2cefa015e8d43910d` |
| `evals/piloto-r1/ledger-e-recontagem.md` | `daaed6a29f6645a866cc6b345884a0bb1d3c3ec443f9148deab4b3eec7de6437` |
| `evals/piloto-r2/aderencia.md` | `81402fc867a2d6cb2bc90cf6571819360bef350f9a67f2ea3206bd26c0f33121` |
| `evals/piloto-r2/custo.md` | `b7af0c84c458fe0357fd37461c8029a202048062fd38f4ba46182da32b19dcd4` |
| `evals/piloto-r2/execucao.md` | `c1b9380d6aebb1ede3ada699db64c668bae564813ae13d53aec5c94ca3c13b79` |
| `evals/piloto-r2/git-diff.md` | `96ea25c2c5d22709c78992b11fad8003ac518952b2fdcce84cf45a37c107fa28` |
| `evals/piloto-r2/ledger-de-conservacao.md` | `67265b886053568cfe3c86f0ce67c136dd274e34c1524e8df89ace677db68075` |
| `evals/piloto-r2/recontagem-independente.md` | `3aaf936dc19213ec2c7fe65e1824adf4e142f38cfd37ea80f38d0c35fc111255` |
| `evals/piloto-r2/recorte-source-utterance.md` | `be4bf277e5e091a2954b532f1422bb915eda4472b7e7598fa93b89ef6c7a2853` |
| `evals/piloto-r2/relatorio-integridade.md` | `37ea893c31485542d93a7af0a6d375554100890bb3fb46292bce3f5584bc921b` |
| `evals/placar-comite-r1.md` | `a643be19c19bda1996db6a12b4b2d921cf181cbecccff7420ac14bb3a474a80b` |
| `evals/placar-comite-r2.md` | `3650fec50014b9c1fbd6a1e1bab1fb2d1b05cb95cebd9145dc92da69d0c35984` |
| `evals/placar-painel-r1.md` | `cfdacb833d6522ed2c377916148843fd6f6dd6bcdef1c2b52d9310517ddce478` |
| `evals/placar-pos-skill.md` | `29159ad93349f27ce8e1cb72ce2f9720e87e5c885f28d5956040e94afb21a505` |
| `evals/relatorio-testador-r1.md` | `fe945a371f0328aefda956493c916ed3f6b59850703c044f00b90efdf74ec583` |
| `evals/relatorio-testador-r2.md` | `f41debc330212ecd195f640a49994ecdaa8d7502de621a618e3b3963e6d50c11` |

## Partição por arquivo — a prova de cobertura

As três listas do passo 3 recortam **conteúdo**. A exigência de que *cada arquivo da fonte apareça em
exatamente uma delas* é provada por esta partição, onde cada um dos **154** arquivos recebe **um
único** rótulo, pelo destino dos seus bytes:

- **PRESERVADO** — o conteúdo migra e só muda nome e cadeia;
- **REESCRITO** — o arquivo migra, mas ao menos um contrato que ele carrega muda;
- **NAO-COPIADO** — nada dele entra no pacote canônico.

| Rótulo | Arquivos | Quais |
|---|---:|---|
| PRESERVADO | **3** | `references/fundamentos-do-dominio.md` · `references/modelo-operacional-do-time.md` · `references/perfil-cofre-jeremias.md` |
| REESCRITO | **3** | `SKILL.md` · `references/contratos.md` · `agents/openai.yaml` |
| NAO-COPIADO | **148** | `references/rubrica-registros.md` + os **147** de `evals/` |
| **Total** | **154** | fecha com o snapshot e com o digest do manifesto |

Aritmética: `3 + 3 + 148 = 154`. Nenhum arquivo em dois rótulos, nenhum sem rótulo.

Um arquivo **REESCRITO** ainda pode carregar mecanismo herdado — a lista 1 nomeia esse mecanismo e
diz de qual arquivo ele veio. A partição conta **arquivos**; as listas descrevem **conteúdo**. Onde as
duas coisas pareceriam colidir, esta seção manda.

## 1. Recorte preservado

O que justifica a migração existir. Todo item abaixo migra com adaptação de nome e de cadeia de
comando, sem mudança de mecanismo.

### De `references/fundamentos-do-dominio.md`

- O **teste de roteamento determinístico `R1..R8`**, aplicado em ordem, por registro atômico, sobre o
  texto original preservado, com a natureza e o destino de cada regra — é o coração do domínio e a
  razão de o Departamento existir.
- O **invariante de atomicidade** e a tabela de desempate "Parece / Mas / Decisão", inclusive a
  sub-decisão de **não** criar oitava natureza para relato de defeito.
- As **sete naturezas de registro** — `documento-produto`, `memoria-duravel`, `estado`,
  `aprendizagem`, `ideia-backlog`, `decisao-adr`, `guia-playbook` — cada uma com leitor, se
  envelhece e `DURABLE_KEY`; mais `nao-registro` como saída de fronteira.
- A **fronteira memória × estado**: memória guarda *como trabalhamos e por quê* e não envelhece;
  estado guarda *onde a tarefa está* e envelhece rápido. Memória durável é **somente leitura** para
  este Departamento, e a escrita é entregue ao dono como `HANDOFF_DECLARADO`.
- O **ciclo de vida** `CAPTURADO → ROTEADO → GRAVADO → INDEXADO → VERIFICADO`, com `VIGENTE`,
  `SUPERADO` e `ARQUIVADO` depois, e os **seis gates de transição** — `GATE_DECOMPOSICAO`,
  `GATE_DESTINO_UNICO`, `GATE_CUSTODIA`, `GATE_FONTE_UNICA`, `GATE_INDICE`, `GATE_INTEGRIDADE`.
- As **quatro transições emparelhadas** e a regra de que `PAIRED_WITH` não vazio impede fechamento
  isolado.
- A **custódia**: classificar antes de gravar com `internal` por omissão e a mais restritiva
  vencendo; varredura de segredo em **duas fases** (insumo e bytes finais); redação `[REDIGIDO:
  categoria]`; **confinamento de caminho fail-closed sem exceção**; hierarquia de canal, com destino,
  convenção e classificação decidíveis apenas por canal de nível ≤ 2.
- A **indexação** como parte do registro: `REGISTRO_ORFAO` e `INDICE_ADIANTADO`, e a distinção entre
  obrigação de índice `mecanica` e `convencao`.
- **Fonte, view, snapshot e destilação** como papéis derivados distintos: view se regenera, não se
  edita; snapshot é passado rotulado; destilação linka, não substitui.
- A disciplina de **convenção e série de ADR por escopo**: procurar a série antes de escrever,
  continuá-la exatamente, registrar a convenção quando não houver, e nunca misturar séries de
  escopos diferentes no mesmo diretório.
- A **fronteira do domínio** e as quatro obrigações da recusa, inclusive **provar** que nada foi
  escrito, em vez de apenas afirmar.
- A **citação por glosa + ponteiro + digest**, nunca cópia, para norma que mora fora do pacote — a
  regra que sustenta a proibição de copiar as Regras de Ouro para dentro destes arquivos.

### De `references/modelo-operacional-do-time.md`

- Os **atos que o gerente não delega**: a decomposição, a decisão de destino, a recusa de fronteira e
  o fechamento do ledger — porque "um destino sempre decide a fronteira a seu favor".
- Os **papéis por capacidade**, com `Responsabilidade` / `Entrega mínima` / `Não assume`, e a
  distinção entre **papel** (necessidade da missão) e **skill** (o que existe e foi verificado).
- As **três exceções fixas de acúmulo**: quem verifica integridade não é o autor do ato verificado;
  quem reconta não é quem decompôs; quem julga não produziu a linhagem.
- As **ondas de trabalho 0 a 6** e a regra de que a marcha reduzida comprime ondas sem trocar a ordem
  interna.
- As regras **anti-bypass de escrita concorrente**: uma fonte, um escritor por rodada; `baseline_sha256`
  conferido no instante da escrita, com divergência falhando fechado; índice compartilhado escrito uma
  única vez; view, snapshot e runtime gerado nunca como alvo de escrita direta.
- A **prioridade quando não há capacidade para tudo**, com o piso de que nenhuma priorização autoriza
  descartar um registro.
- O esquema de **perfil de destinos** com `existence`, `existence_evidence`, `within_trusted_root`,
  `write_scope` e `owner_capability_id` — caminho não conferido é alegação.

### De `references/perfil-cofre-jeremias.md`

- As **oito cicatrizes verificadas do cofre**, declaradas confirmadas por leitura, listagem ou
  contagem direta em 2026-07-26 — índice secundário órfão; decisão sem convenção de local e
  numeração; destino documentado e sem dono; memória contaminada por progresso; cópia local de norma
  que apodrece; espelho público desatualizado; **gate tautológico com evidência fabricada aceita como
  aprovação**; segunda cópia parada no tempo. São a base empírica dos controles, e cada uma nomeia o
  ato que a mediu.
- A regra de carga do arquivo: **binding de ambiente**, aberto somente quando o alvo for aquele
  cofre, e sempre como **hipótese a reconfirmar em runtime** — nada nele autoriza escrita.
- A separação **`method_root` × `target_root`**, que é o que sustenta a decisão 4 do
  [ADR-005](adr-005-quatro-agentes-e-relatorios-de-registros.md).
- As duas implementações herdadas por inteiro: varredura de segredo que registra categoria sem nunca
  materializar o valor casado, e confinamento de caminho por comparação de caminho absoluto com
  asserção de reparse point.

### Mecanismo herdado de arquivo que a lista 2 reescreve

- O **ledger de conservação** com seus **dois invariantes** e a tabela `STATE → contador`, e a
  **recontagem por um segundo ato** com prova declarada — mecanismo preservado de
  `references/contratos.md`; o envelope que o transporta é reescrito (lista 2).
- O **vocabulário de falha** — os **catorze** gates de integridade, sempre todos reportados, com
  `NAO_APLICAVEL` exigindo justificativa concreta — preservado de `references/contratos.md`, com a
  regra de **um único arquivo dono**: repetir a lista em outro lugar seria o `FATO_DUPLICADO` que o
  Departamento reprova em terceiros.
- A **escada de leitura por tier**, com os seis sinais de triagem cumulativos e o `tier` **medido, não
  escolhido**, caindo para o degrau completo diante de qualquer sinal falso, ausente ou não medido —
  mecanismo preservado de `SKILL.md`; os orçamentos em bytes de cada degrau são reescritos, porque
  citavam arquivos que este pacote não tem.

## 2. Recorte reescrito

Uma linha por mudança de contrato.

| Legado | Novo | Por quê |
|---|---|---|
| superior `comite-de-lentes`, com `relay_return_to: comite-de-lentes` e `return_to` canônico `maestro` | superior **`diretor-de-lentes`**, `returned_to: "diretor-de-lentes"` travado em `const` | nova hierarquia; o `departmentReturn` do [schema do Diretor](../../../schemas/diretor-de-lentes.schema.json) fixa o canal de retorno |
| modo interno `GERENCIAR \| JULGAR`, mais o eixo `ATUA \| CONSULTA` do Comitê, com tabela de tradução de seis linhas | **apenas** `mode: ATUA \| CONSULTA` da `DEPARTMENT_MISSION` do Diretor | o envelope de entrada pertence ao schema do superior; um segundo enum de modo dentro do Departamento reintroduz a tradução que o schema já eliminou |
| capacidade `JULGAR` própria: rubrica absoluta de dez dimensões ponderadas, nota 0–10 e corte 9,5 | **sem capacidade de julgar**: o Diretor emite `JUDGMENT_REQUEST` ao `departamento-juizes` | o [ADR-002](../../../departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md) deu a nota e o corte aos Juízes; dois cortes com o mesmo número e significados diferentes é ambiguidade — mesma razão do [ADR-003](../../departamento-auditoria-responsabilidades/references/adr-003-conformidade-sem-nota.md) |
| envelope de entrada `registros_assignment`, extensão de `lens_mission` | `DEPARTMENT_MISSION` do Diretor, com o dossiê do domínio em `inputs[]`, `scope_in[]` e `required_evidence[]` | consumir o envelope do superior, nunca redefini-lo |
| envelope de saída `registros_management_result`, extensão de `lens_management_result` | `DEPARTMENT_RETURN` com `returned_by: "departamento-registros"`, e o resultado de domínio referenciado em `artifact_refs[]` / `evidence_refs[]` | o schema do Diretor já define o que consome; o retorno do domínio vira artefato referenciado, não campo novo |
| envelope `registros_judgment_result`, com `verdict`, `BLOQUEADO_AUTOJULGAMENTO` e `MODO_DESCONHECIDO` | **não existe**; o veredito chega como `DEPARTMENT_JUDGE_REPORT` produzido pelos Juízes | quem julga é outro pacote; produzir veredito aqui seria emitir envelope de terceiro |
| `registros_capability_gap`, com `owner_of_decision` sobrescrito para `comite-de-lentes` | lacuna escalada ao Diretor, que materializa `DIRECTOR_CAPABILITY_GAP` com `owner: "diretor-de-lentes"` e `safe_state: "D_BLOCKED"` | o schema do Diretor já reserva o artefato de lacuna e trava o dono; a sobrescrita legada era desvio declarado do canônico |
| `causal.contract_version: 3`, com versionamento próprio do pacote | `causalHeader` do Diretor, com `contract_id`, `contract_version`, `contract_digest` e `producer` travado em **`departamento-registros`** | `producer` em `const` é o que rejeita envelope forjado por outro pacote — e o schema do Diretor **já** reserva `departamento-registros` no `operationalDepartment`, no `knownCapability`, na exigência de exatamente uma ocorrência no `department_matrix` (`minContains: 1`, `maxContains: 1`) e no par `returned_by` × `producer` do `departmentReturn` |
| estado `CANDIDATA_NAO_VINCULADA` / `integration_status: candidate_unlinked`, bloqueando missão até o catálogo do Comitê registrar identificador e digest | **não existe**: o pacote nasce no caminho canônico que o Diretor enumera em runtime | o bloqueio existia porque a skill era candidata fora de árvore; aqui a posição é o vínculo |
| `evals` de autoria contratados como **exceção** ao bloqueio de vínculo | sem exceção: evals do pacote são artefato do próprio pacote | exceção de vínculo some junto com o vínculo pendente |
| a triagem por seis sinais orçava os degraus em bytes de `contratos.md`, `fundamentos-do-dominio.md`, `modelo-operacional-do-time.md`, `perfil-cofre-jeremias.md` e `rubrica-registros.md` | mesmos seis sinais, mesmo `tier` medido e mesmo fail-closed; **orçamento em bytes refeito** sobre os arquivos deste pacote | manter os números antigos seria citar medição de arquivos que aqui não existem — e o degrau `JULGAR`, que só existia para abrir a rubrica, deixa de existir |
| `SKILL.md` legada com 521 linhas e `description` de gatilhos do Comitê | `SKILL.md` dentro dos limites mecânicos: frontmatter só com `name` e `description`, `description` ≤ 1024 caracteres, arquivo ≤ 500 linhas, `name` = nome da pasta | limites verificados pelo validador do pacote, passo 7 do guia |
| sem `CONTRATO-DE-COMPROMISSO.md` | contrato **obrigatório** na gerente **e** em cada agente | contrato estrutural do [ORGANOGRAMA.md](../../../../../ORGANOGRAMA.md) e princípio 8 |
| **zero** agentes reais: o "time" eram 15 papéis por capacidade descritos em prosa, sem pasta, sem `SKILL.md` e sem contrato | **quatro** agentes com pasta, `SKILL.md`, `CONTRATO-DE-COMPROMISSO.md` e `agents/openai.yaml`, com fronteira exclusiva | papel descrito não é capacidade descobrível em runtime; a decisão dos quatro e o corte das fronteiras estão no [ADR-005](adr-005-quatro-agentes-e-relatorios-de-registros.md) |
| `agents/openai.yaml` com identidade `orquestrador-registros` | identidade `departamento-registros` | nome da pasta, `name` do frontmatter e nome no organograma são o mesmo texto |
| escalonamento ao Comitê em sete situações nomeadas, incluindo "três tentativas sem fechar o ledger" | mesmas situações, escaladas ao Diretor pelo canal do `DEPARTMENT_RETURN` e, quando for lacuna de capacidade, ao artefato de lacuna dele | muda o destinatário e o envelope, não o gatilho |
| entrega final da rodada retornava ao Comitê e encerrava | entrega deste Departamento **também vai aos Juízes** antes do fechamento | contrato estrutural: toda entrega de departamento passa pelo `departamento-juizes` |

## 3. Recorte não copiado

**148 arquivos.** Nada aqui é promovido. Tudo aqui **continua válido como história**, no legado
intacto, e permanece citável como evidência do que a skill legada mediu — nunca como evidência do
que este pacote faz.

| Subárvore legada | Arquivos | Por que não migra |
|---|---:|---|
| `references/rubrica-registros.md` | 1 | é a rubrica do modo `JULGAR`: dez dimensões ponderadas, escala 0–10, corte 9,5, vetos e rótulos `APROVADA / REPROVADA / NÃO_JULGÁVEL`. Julgar não é mais capacidade deste Departamento — promovê-la criaria uma segunda nota sobre o mesmo candidato, exatamente o que o ADR-002 fechou |
| `evals/` — raiz (`evals.json`, `manifest-sha256.txt`, `baseline-sem-skill.md`, `baseline-sem-skill-r2.md`, `placar-comite-r1.md`, `placar-comite-r2.md`, `placar-painel-r1.md`, `placar-pos-skill.md`, `relatorio-testador-r1.md`, `relatorio-testador-r2.md`) | 10 | os prompts do `evals.json` acionam a skill legada pelo gatilho antigo e exercitam `GERENCIAR \| JULGAR`, o corte próprio e o retorno ao Comitê; os baselines e placares medem **aquele** gatilho e **aquela** saída. Promovê-los é fabricar evidência |
| `evals/candidatos/` (`a/` e `b/`, pacotes completos concorrentes) | 12 | são duas versões concorrentes da **própria skill legada**, insumo de julgamento comparativo. Não descrevem este pacote |
| `evals/comite/` (rodadas 1 e 2, pareceres por lente) | 13 | pareceres do **Comitê de Lentes** legado sobre a skill legada. Outro órgão, outro superior, outro objeto |
| `evals/painel/` (`juiz-1..3`) | 3 | pareceres do painel de juízes legado, na rubrica que não migra |
| `evals/piloto-r1/` | 4 | piloto executado contra a skill legada — aderência, execução, `git-diff`, ledger e recontagem |
| `evals/piloto-r2/` | 8 | segundo piloto executado, incluindo custo, recorte do `SOURCE_UTTERANCE` e relatório de integridade. É a origem medida de vários controles preservados; a **lição** entra pela lista 1, a **medição** fica no legado |
| `evals/forward-test/` (`resultados.md`, `resultados-r2.md`) | 2 | forward-tests comportamentais da skill legada. RI-04: relatório de teste só existe depois que alguém respondeu de verdade — reaproveitar respostas produzidas contra outro gatilho seria declarar prova que este pacote não tem |
| `evals/fixtures/` (18 casos, `_tools/`, `MANIFESTO.json`) | 95 | árvores-alvo sintéticas moldadas para os envelopes `registros_assignment` e `registros_management_result` e para o `assignment.json` legado. O envelope de entrada mudou; a fixture que o alimenta não sobrevive à mudança |
| **Total** | **148** | |

Os **hashes** de todos eles estão nas tabelas acima: o legado continua sendo a prova do que já foi
medido, e esta seção é o registro de que nada disso foi promovido a prova do pacote novo.

## Política de rollback

O pacote legado permanece **intacto**: nunca editado, nunca movido, nunca usado como fallback
automático em runtime. Ele é fonte histórica e rollback manual.

O `diretor-de-lentes` **não** trata `orquestrador-registros` como equivalente deste Departamento.
Ausência do pacote canônico no caminho enumerado é `DIRECTOR_CAPABILITY_GAP`, com
`safe_state: "D_BLOCKED"` — bloqueio declarado, nunca substituição silenciosa.

## Verificação de integridade do legado

Ao fechar a migração (passo 10 do guia), recalcular os hashes desta página e provar que a fonte não
mudou. O caminho curto é comparar o **digest do manifesto**; divergindo, as duas tabelas dizem em qual
arquivo.

**Executado no passo 10, em 2026-07-26.** Os 154 arquivos foram relidos do legado e os 154 hashes
recalculados: **nenhum arquivo a mais, nenhum a menos, nenhum hash divergente**; 1.320.436 bytes,
idênticos ao snapshot. O legado está **intacto**. O digest do manifesto foi recalculado pela receita
determinística acima, em PowerShell e em Python, com resultado idêntico — e substituiu o valor
anterior, que nenhuma variante reproduzia (ver a nota da seção *Receita do manifesto*).

**Concluído quando:** os 154 hashes recalculados batem com os desta página, o digest do manifesto é
`2ddcc7f987bf539c17d44b75733770bd97ef1bffeef1d82a694de10c8f385df3` pela receita fixada acima, e a
partição continua fechando em `3 + 3 + 148 = 154`.
