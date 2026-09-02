# deploy-estrutura.ps1
# Sincroniza a "Estrutura Final de Skills" com os runtimes do Claude e do Codex.
# Compativel com Windows PowerShell 5.1. Mantido em ASCII puro.
#
# Por que existe: ate 2026-07-27 esta arvore era implantada a mao. O resultado
# medido foi deriva de 125 arquivos entre a fonte e os DOIS runtimes -- os sete
# contratos de gerente e os 24 SKILL.md de agente fechados naquele dia nao
# estavam na porta que uma sessao nova carrega. Deriva silenciosa transforma
# qualquer teste de comportamento em teste de um pacote que ja nao existe.
#
# O que este script NAO faz: nao toca nas skills do Catalogo-Skills-Unificado.
# Ele espelha componente a componente, nunca a raiz do destino, porque o mesmo
# diretorio hospeda as skills do catalogo. Espelhar a raiz apagaria as 57.
#
# Exemplos:
#   Verificar paridade sem escrever (o modo honesto de conferir):
#     .\deploy-estrutura.ps1 -ProjectPath "C:\caminho\do\projeto" -Runtime Ambos -SomenteVerificar
#
#   Sincronizar Claude + Codex:
#     .\deploy-estrutura.ps1 -ProjectPath "C:\caminho\do\projeto" -Runtime Ambos
#
#   Pular a validacao pre-deploy (use apenas para diagnosticar o proprio deploy):
#     .\deploy-estrutura.ps1 -ProjectPath "..." -Runtime Claude -SemValidacao

[CmdletBinding()]
param(
  [string]$ProjectPath = "",

  [ValidateSet("Claude", "Codex", "Ambos")]
  [string]$Runtime = "Claude",

  [switch]$SomenteVerificar,
  [switch]$SemValidacao
)

$ErrorActionPreference = "Stop"
$source = $PSScriptRoot

# O contrato de implantacao. `ceo-maestro` e a porta unica DA CADEIA: nenhum
# gerente e nenhum agente aninhado vira skill invocavel, e e isso que "porta
# unica" quer dizer. As outras tres pastas e os tres arquivos existem no destino
# porque os caminhos relativos de dentro do pacote sobem ate a RAIZ da estrutura:
# sem eles, `../../../../regras-de-ouro/REGRAS-DE-OURO.md` e `_compartilhado/`
# nao resolvem no runtime como resolvem no cofre.
#
# CORRIGIDO EM 2026-09-02, e a frase anterior era falsa quando foi escrita. Ela
# dizia que `ceo-maestro` era "a unica pasta com SKILL.md na raiz da estrutura, e
# portanto a unica skill invocavel". A segunda metade era o contrato; a primeira
# era uma afirmacao sobre a arvore, e a arvore tinha DUAS -- um comentario 90
# linhas abaixo neste mesmo arquivo ja reconhecia o `especialista-planejador`
# como pacote antigo e fora do pre-deploy. Afirmacao sobre a arvore que ninguem
# executou contra a arvore.
#
# `planejador-estrutura` ENTRA como componente em 2026-09-02, por decisao de
# Jeremias. Ele nao e no de cadeia: e consultor direto, declaradamente FORA da
# cadeia de comando, sem `return_to` e sem envelope. Publica-lo nao abre porta
# nenhuma na cadeia -- a porta da cadeia continua sendo uma so.
#
# Ele chegou com esse nome, e nao com o antigo, por uma razao medida: sob
# `especialista-planejador` ele colidia com uma lente homonima do Catalogo, e o
# `deploy-skills.ps1` do catalogo NAO traz esse nome em $preservarSempre --
# entao publicar sob o nome antigo seria desfeito, em silencio, no proximo deploy
# de rotina do catalogo.
$componentesPasta = @("ceo-maestro", "planejador-estrutura", "regras-de-ouro", "_compartilhado", "registros")

# PLANO-DE-ACAO-*.md fica de fora por decisao: e plano de trabalho de uma
# frente, nao metodo. O runtime carrega metodo.
$componentesArquivo = @("AGENTS.md", "GUIA-DE-EXPANSAO-E-MIGRACAO.md", "ORGANOGRAMA.md")

# __pycache__ e artefato de execucao dos validadores. Nao vai ao runtime, e nao
# conta como divergencia na verificacao.
$excluirPastas = @("__pycache__")

function Assert-PathUnderRoot {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$Root
  )

  $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
  $pathFull = [System.IO.Path]::GetFullPath($Path)
  if (-not $pathFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Caminho fora da raiz autorizada: $pathFull"
  }
}

function Get-FileMap {
  param([Parameter(Mandatory = $true)][string]$Root)

  $map = @{}
  if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
    return $map
  }

  $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd('\', '/')
  foreach ($file in Get-ChildItem -LiteralPath $rootFull -Recurse -File -Force) {
    $relative = $file.FullName.Substring($rootFull.Length).TrimStart('\', '/').Replace('\', '/')
    $ignorar = $false
    foreach ($excluida in $excluirPastas) {
      if ($relative -like "$excluida/*" -or $relative -like "*/$excluida/*") { $ignorar = $true }
    }
    if ($ignorar) { continue }
    $map[$relative] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
  }
  return $map
}

function Get-Targets {
  $targets = [System.Collections.Generic.List[object]]::new()
  $runtimes = if ($Runtime -eq "Ambos") { @("Claude", "Codex") } else { @($Runtime) }

  if ($ProjectPath -ne "") {
    $base = [System.IO.Path]::GetFullPath($ProjectPath)
  } else {
    $base = [System.IO.Path]::GetFullPath($env:USERPROFILE)
  }

  foreach ($runtimeName in $runtimes) {
    if ($runtimeName -eq "Claude") {
      $relative = ".claude\skills"
    } elseif ($ProjectPath -ne "") {
      $relative = ".agents\skills"
    } else {
      $relative = ".codex\skills"
    }

    $targets.Add([pscustomobject]@{
      Runtime = $runtimeName
      Path = Join-Path $base $relative
    })
  }

  return $targets
}

function Invoke-ValidacaoPreDeploy {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($null -eq $python) {
    throw "python nao encontrado. Use -SemValidacao apenas se souber o que esta pulando."
  }

  # Pacote gerente e definido AQUI pelo mesmo criterio de
  # `_pacotes_gerentes` em _compartilhado/verificacoes_estrutura.py: todo
  # diretorio com SKILL.md fora de `agentes`, `evals` e
  # `fontes-legadas-pinadas`. Dossies, candidatos e snapshots tambem guardam
  # copias sob evals/, e por isso a exclusao continua.
  #
  # ALINHADO EM 2026-08-27, e a divergencia era real. Ate aqui o deploy exigia
  # tambem pasta `schemas/`, e a trava nao -- entao o deploy validava 15 pacotes
  # e a cadeia media 18. Tres ficavam FORA do pre-deploy: os dois da
  # diretoria-agentica, que chegaram naquele dia e SAIRAM da arvore em
  # 2026-09-01 por serem do projeto Empresa GradUP, e o planejador (entao
  # chamado `especialista-planejador`), que nao e novo. Nenhum dos tres publica envelope, e por isso nenhum tem
  # `schemas/` -- a exigencia media a natureza do pacote, nao a existencia dele.
  # O efeito era um relatorio que dizia "16 validadores, 0 com falha" sem
  # cobrir 3 dos 18. Criterio de identidade que diverge entre dois lugares vira
  # buraco silencioso: quem le o placar do deploy nao tem como saber o que ele
  # nao olhou.
  $gerentes = @(
    Get-ChildItem -LiteralPath $source -Recurse -File -Filter "SKILL.md" |
      Where-Object {
        $packageRelative = $_.Directory.FullName.Substring($source.Length).TrimStart('\', '/')
        $packageRelative -notmatch '(^|[\\/])(agentes|fontes-legadas-pinadas|evals)([\\/]|$)'
      } |
      ForEach-Object { $_.Directory.FullName } |
      Sort-Object -Unique
  )

  $validadores = [System.Collections.Generic.List[object]]::new()
  $semValidador = [System.Collections.Generic.List[string]]::new()
  foreach ($gerente in $gerentes) {
    $candidate = Join-Path $gerente "evals\validate_workflow.py"
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
      $validadores.Add((Get-Item -LiteralPath $candidate))
    } else {
      $semValidador.Add($gerente.Substring($source.Length).TrimStart('\', '/'))
    }
  }
  if ($semValidador.Count -gt 0) {
    throw ("Pacote(s) gerente(s) sem validador canonico: {0}" -f ($semValidador -join ", "))
  }

  $validadores = @($validadores | Sort-Object FullName)
  $motor = Join-Path $source "_compartilhado\teste_validador_schema.py"
  if (Test-Path -LiteralPath $motor -PathType Leaf) {
    $validadores = @($validadores) + @(Get-Item -LiteralPath $motor)
  }

  $falhas = 0
  foreach ($validador in $validadores) {
    $env:PYTHONIOENCODING = "utf-8"
    & $python.Source $validador.FullName | Out-Null
    if ($LASTEXITCODE -ne 0) {
      $falhas++
      $nome = Split-Path (Split-Path $validador.FullName -Parent) -Parent
      Write-Host ("  [ERRO ] validador reprovou ou quebrou: {0}" -f (Split-Path $nome -Leaf)) -ForegroundColor Red
    }
  }

  Write-Host ("  {0} validadores executados, {1} com falha" -f $validadores.Count, $falhas)
  if ($falhas -gt 0) {
    throw "Estrutura reprovada na validacao pre-deploy. Deploy bloqueado."
  }
}

function Compare-Target {
  param([Parameter(Mandatory = $true)][string]$TargetRoot)

  $errors = [System.Collections.Generic.List[string]]::new()

  foreach ($componente in $componentesPasta) {
    $origem = Join-Path $source $componente
    $destino = Join-Path $TargetRoot $componente

    if (-not (Test-Path -LiteralPath $destino -PathType Container)) {
      $errors.Add("componente ausente: $componente/")
      continue
    }

    $sourceMap = Get-FileMap -Root $origem
    $targetMap = Get-FileMap -Root $destino

    foreach ($relative in $sourceMap.Keys) {
      if (-not $targetMap.ContainsKey($relative)) {
        $errors.Add("arquivo ausente: $componente/$relative")
      } elseif ($sourceMap[$relative] -ne $targetMap[$relative]) {
        $errors.Add("hash divergente: $componente/$relative")
      }
    }
    foreach ($relative in $targetMap.Keys) {
      if (-not $sourceMap.ContainsKey($relative)) {
        $errors.Add("arquivo extra: $componente/$relative")
      }
    }
  }

  foreach ($arquivo in $componentesArquivo) {
    $origem = Join-Path $source $arquivo
    $destino = Join-Path $TargetRoot $arquivo
    if (-not (Test-Path -LiteralPath $destino -PathType Leaf)) {
      $errors.Add("arquivo de raiz ausente: $arquivo")
      continue
    }
    $h1 = (Get-FileHash -LiteralPath $origem -Algorithm SHA256).Hash
    $h2 = (Get-FileHash -LiteralPath $destino -Algorithm SHA256).Hash
    if ($h1 -ne $h2) { $errors.Add("hash divergente: $arquivo") }
  }

  return [pscustomobject]@{ Errors = @($errors) }
}

foreach ($componente in $componentesPasta) {
  if (-not (Test-Path -LiteralPath (Join-Path $source $componente) -PathType Container)) {
    throw "Componente de origem nao encontrado: $componente"
  }
}

Write-Host ""
if ($SemValidacao) {
  Write-Host "Validacao pre-deploy PULADA por -SemValidacao" -ForegroundColor Yellow
} else {
  Write-Host "Validacao pre-deploy da estrutura" -ForegroundColor Cyan
  Invoke-ValidacaoPreDeploy
}

$targets = @(Get-Targets)

if (-not $SomenteVerificar) {
  $robocopy = Get-Command robocopy -ErrorAction SilentlyContinue
  if ($null -eq $robocopy) {
    throw "robocopy nao encontrado. O deploy requer Windows; use -SomenteVerificar em outros sistemas."
  }

  foreach ($target in $targets) {
    Write-Host ""
    Write-Host ("Deploy {0}" -f $target.Runtime) -ForegroundColor Cyan
    Write-Host ("  Origem : {0}" -f $source)
    Write-Host ("  Destino: {0}" -f $target.Path)
    New-Item -ItemType Directory -Path $target.Path -Force | Out-Null

    foreach ($componente in $componentesPasta) {
      $origem = Join-Path $source $componente
      $destino = Join-Path $target.Path $componente
      Assert-PathUnderRoot -Path $destino -Root $target.Path
      # Robocopy defaults to one million retries with a 30-second wait. A
      # locked file would therefore make the deploy appear hung for months.
      # Keep retries bounded so the gate fails visibly and can be diagnosed.
      robocopy $origem $destino /MIR /XD $excluirPastas /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
      $code = $LASTEXITCODE
      if ($code -ge 8) {
        throw "Falha ao copiar '$componente' para '$($target.Path)' (robocopy $code)."
      }
      Write-Host ("  espelhado: {0}/" -f $componente)
    }

    foreach ($arquivo in $componentesArquivo) {
      $destino = Join-Path $target.Path $arquivo
      Assert-PathUnderRoot -Path $destino -Root $target.Path
      Copy-Item -LiteralPath (Join-Path $source $arquivo) -Destination $destino -Force
      Write-Host ("  copiado  : {0}" -f $arquivo)
    }
  }
}

Write-Host ""
Write-Host "Verificacao de paridade por SHA-256" -ForegroundColor Cyan
$totalErrors = 0
foreach ($target in $targets) {
  $comparison = Compare-Target -TargetRoot $target.Path
  foreach ($errorMessage in $comparison.Errors) {
    Write-Host ("  [ERRO ] {0}: {1}" -f $target.Runtime, $errorMessage) -ForegroundColor Red
  }
  if ($comparison.Errors.Count -eq 0) {
    Write-Host ("  [OK] {0}: estrutura identica em {1}" -f $target.Runtime, $target.Path) -ForegroundColor Green
  }
  $totalErrors += $comparison.Errors.Count
}

if ($totalErrors -gt 0) {
  Write-Host ""
  Write-Host ("REPROVADO: {0} divergencia(s) entre fonte e runtime." -f $totalErrors) -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "APROVADO: a Estrutura Final de Skills esta sincronizada nos runtimes selecionados." -ForegroundColor Green
if (-not $SomenteVerificar) {
  Write-Host "Reabra/reinicie as sessoes para recarregar as skills." -ForegroundColor Yellow
}
exit 0
